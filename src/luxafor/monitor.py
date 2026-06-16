"""Internet health monitor for the Luxafor Flag."""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum, auto

import anyio

from luxafor.local import FlagColor, LuxaforFlag
from luxafor.util import setup_logger

logger = setup_logger()

PROBE_TARGETS: list[tuple[str, int]] = [
    ("8.8.8.8", 53),
    ("1.1.1.1", 53),
    ("9.9.9.9", 53),
]
PROBE_INTERVAL: float = 1.5
PROBE_TIMEOUT: float = 2.0
WINDOW_SIZE: int = 20
HYSTERESIS_SECONDS: float = 3.0
BLINK_INTERVAL: float = 0.5
DISPLAY_TICK: float = 0.2
ANOMALY_FLASH_DURATION: float = 0.6


class Status(Enum):
    """Monitor health states."""

    HEALTHY = auto()
    DEGRADED = auto()
    DOWN = auto()
    CRITICAL = auto()


STATUS_COLORS: dict[Status, FlagColor] = {
    Status.HEALTHY: FlagColor.GREEN,
    Status.DEGRADED: FlagColor.YELLOW,
    Status.DOWN: FlagColor.RED,
    Status.CRITICAL: FlagColor.RED,
}


@dataclass
class ProbeSample:
    """Result of a single probe round."""

    timestamp: float
    successes: int
    total: int


@dataclass
class InternetMonitor:
    """Monitors internet health and drives a Luxafor Flag."""

    flag: LuxaforFlag
    critical_after: float = 300.0
    samples: deque[ProbeSample] = field(default_factory=lambda: deque(maxlen=WINDOW_SIZE))
    current_status: Status = Status.HEALTHY
    _suggested_status: Status = Status.HEALTHY
    _suggested_since: float = field(default_factory=time.monotonic)
    _down_since: float | None = None
    _anomaly_flash_until: float = 0.0
    _last_color: FlagColor | None = None

    async def _probe_one(self, host: str, port: int) -> bool:
        """TCP connect probe to a single target."""
        try:
            async with await anyio.connect_tcp(host, port):
                return True
        except OSError:
            return False

    async def _probe_round(self) -> ProbeSample:
        """Probe all targets concurrently with a timeout."""
        results: list[bool] = []

        async def probe_with_timeout(host: str, port: int) -> None:
            with anyio.move_on_after(PROBE_TIMEOUT):
                results.append(await self._probe_one(host, port))
                return
            results.append(False)

        async with anyio.create_task_group() as tg:
            for host, port in PROBE_TARGETS:
                tg.start_soon(probe_with_timeout, host, port)

        return ProbeSample(
            timestamp=time.monotonic(),
            successes=sum(results),
            total=len(PROBE_TARGETS),
        )

    def _compute_health(self) -> float:
        """Weighted health score (0.0–1.0), biased toward recent samples."""
        if not self.samples:
            return 1.0

        total_weight = 0.0
        weighted_score = 0.0

        for i, sample in enumerate(self.samples):
            weight = 1.0 + i
            total_weight += weight
            weighted_score += weight * (sample.successes / sample.total)

        return weighted_score / total_weight

    def _detect_anomaly(self, sample: ProbeSample) -> bool:
        """Detect anomalous packet loss: a drop amid otherwise healthy traffic."""
        if sample.successes == sample.total:
            return False
        if self.current_status != Status.HEALTHY:
            return False
        if len(self.samples) < 3:
            return False
        recent = list(self.samples)[-4:-1]
        return all(s.successes == s.total for s in recent)

    def _health_to_status(self, health: float) -> Status:
        if health > 0.8:
            return Status.HEALTHY
        if health > 0.4:
            return Status.DEGRADED
        return Status.DOWN

    def _update_status(self, health: float) -> Status:
        """Update status with hysteresis and critical escalation."""
        now = time.monotonic()
        target = self._health_to_status(health)

        if (
            self.current_status in {Status.DOWN, Status.CRITICAL}
            and self._down_since is not None
            and now - self._down_since >= self.critical_after
        ):
            self.current_status = Status.CRITICAL
            return Status.CRITICAL

        if target != self._suggested_status:
            self._suggested_status = target
            self._suggested_since = now

        if self._suggested_status != self.current_status:
            if now - self._suggested_since >= HYSTERESIS_SECONDS:
                self.current_status = self._suggested_status

                if self.current_status == Status.DOWN:
                    self._down_since = now
                elif self.current_status not in {Status.DOWN, Status.CRITICAL}:
                    self._down_since = None

        return self.current_status

    def _set_color(self, color: FlagColor) -> None:
        """Set flag color, skipping redundant writes."""
        if color != self._last_color:
            self.flag.set_color(color)
            self._last_color = color

    async def _probe_loop(self) -> None:
        """Continuously probe and update health state."""
        while True:
            sample = await self._probe_round()
            self.samples.append(sample)

            if self._detect_anomaly(sample):
                self._anomaly_flash_until = time.monotonic() + ANOMALY_FLASH_DURATION
                logger.info(
                    "Anomalous packet loss detected",
                    successes=sample.successes,
                    total=sample.total,
                )

            health = self._compute_health()
            status = self._update_status(health)

            logger.debug(
                "Probe complete",
                successes=sample.successes,
                total=sample.total,
                health=round(health, 3),
                status=status.name,
            )

            await anyio.sleep(PROBE_INTERVAL)

    async def _display_loop(self) -> None:
        """Drive the flag LED based on current state."""
        blink_on = True

        while True:
            now = time.monotonic()

            if now < self._anomaly_flash_until:
                self._set_color(FlagColor.CYAN)
            elif self.current_status == Status.CRITICAL:
                self._set_color(FlagColor.RED if blink_on else FlagColor.OFF)
                blink_on = not blink_on
                await anyio.sleep(BLINK_INTERVAL)
                continue
            else:
                blink_on = True
                self._set_color(STATUS_COLORS[self.current_status])

            await anyio.sleep(DISPLAY_TICK)

    async def run(self) -> None:
        """Start the monitor."""
        logger.info(
            "Starting internet monitor",
            targets=[f"{h}:{p}" for h, p in PROBE_TARGETS],
            critical_after=self.critical_after,
        )
        self._set_color(FlagColor.GREEN)

        async with anyio.create_task_group() as tg:
            tg.start_soon(self._probe_loop)
            tg.start_soon(self._display_loop)


async def start_monitor(critical_after: float = 300.0) -> None:
    """Entry point for the monitor."""
    flag = LuxaforFlag()
    monitor = InternetMonitor(flag=flag, critical_after=critical_after)
    await monitor.run()
