from unittest.mock import MagicMock, patch

import pytest

from luxafor.local import FlagColor, HIDBuffer, LuxaforFlag

# -- FlagColor enum --


@pytest.mark.parametrize(
    ("member", "expected"),
    [
        (FlagColor.OFF, 0x4F),
        (FlagColor.BLUE, 0x42),
        (FlagColor.CYAN, 0x43),
        (FlagColor.GREEN, 0x47),
        (FlagColor.MAGENTA, 0x4D),
        (FlagColor.RED, 0x52),
        (FlagColor.WHITE, 0x57),
        (FlagColor.YELLOW, 0x59),
    ],
)
def test_flag_color_values(member, expected):
    assert member.value == expected


def test_flag_color_member_count():
    assert len(FlagColor) == 8


def test_flag_color_values_are_ascii():
    assert FlagColor.OFF.value == ord("O")
    assert FlagColor.RED.value == ord("R")
    assert FlagColor.BLUE.value == ord("B")


def test_flag_color_lookup_by_value():
    assert FlagColor(0x52) is FlagColor.RED


def test_flag_color_invalid_value():
    with pytest.raises(ValueError, match="0"):
        FlagColor(0x00)


# -- HIDBuffer --


class TestHIDBufferInit:
    def test_defaults(self):
        buf = HIDBuffer()
        assert buf[0] == 0x00
        assert buf[2] == FlagColor.OFF.value
        assert len(buf) == 8

    def test_custom_report_id_and_color(self):
        buf = HIDBuffer(report_id=0x01, color=FlagColor.RED)
        assert buf[0] == 0x01
        assert buf[2] == FlagColor.RED.value

    def test_unused_slots_are_zero(self):
        buf = HIDBuffer(report_id=0x01, color=FlagColor.GREEN)
        assert buf[1] == 0x00
        assert buf[3] == 0x00
        assert buf[4] == 0x00
        assert buf[5] == 0x00
        assert buf[6] == 0x00
        assert buf[7] == 0x00


class TestHIDBufferProtocol:
    def test_len(self):
        assert len(HIDBuffer()) == 8

    def test_bytes(self):
        buf = HIDBuffer(report_id=0x01, color=FlagColor.RED)
        raw = bytes(buf)
        assert isinstance(raw, bytes)
        assert len(raw) == 8
        assert raw[0] == 0x01
        assert raw[2] == FlagColor.RED.value

    def test_getitem(self):
        buf = HIDBuffer(color=FlagColor.CYAN)
        assert buf[2] == FlagColor.CYAN.value

    def test_setitem(self):
        buf = HIDBuffer()
        buf[3] = 0xFF
        assert buf[3] == 0xFF

    def test_iter(self):
        buf = HIDBuffer(report_id=0x01, color=FlagColor.BLUE)
        values = list(buf)
        assert len(values) == 8
        assert values[0] == 0x01
        assert values[2] == FlagColor.BLUE.value

    def test_contains_present(self):
        buf = HIDBuffer(color=FlagColor.RED)
        assert FlagColor.RED.value in buf

    def test_contains_absent(self):
        buf = HIDBuffer(color=FlagColor.OFF)
        assert FlagColor.RED.value not in buf

    def test_repr(self):
        buf = HIDBuffer()
        r = repr(buf)
        assert r.startswith("HIDBuffer")
        assert "b'" in r


# -- LuxaforFlag --


@pytest.fixture
def mock_hid_device():
    with patch("luxafor.local._hid.hid.Device") as mock_cls:
        mock_device = MagicMock()
        mock_cls.return_value = mock_device
        yield mock_cls, mock_device


@pytest.fixture
def flag(mock_hid_device):
    _, _ = mock_hid_device
    return LuxaforFlag()


class TestLuxaforFlagInit:
    def test_class_constants(self):
        assert LuxaforFlag.VENDOR_ID == 0x04D8
        assert LuxaforFlag.PRODUCT_ID == 0xF372

    def test_connects_on_init(self, mock_hid_device):
        mock_cls, _ = mock_hid_device
        LuxaforFlag()
        mock_cls.assert_called_once_with(0x04D8, 0xF372)

    def test_device_set_on_success(self, mock_hid_device):
        _, mock_device = mock_hid_device
        flag = LuxaforFlag()
        assert flag.device is mock_device

    def test_device_none_on_failure(self):
        with patch("luxafor.local._hid.hid.Device", side_effect=OSError("no device")):
            flag = LuxaforFlag()
        assert flag.device is None


class TestLuxaforFlagConnect:
    def test_reconnect_sets_device(self, flag, mock_hid_device):
        mock_cls, mock_device = mock_hid_device
        flag.device = None
        mock_cls.reset_mock()

        flag.connect()

        mock_cls.assert_called_once_with(0x04D8, 0xF372)
        assert flag.device is mock_device

    def test_reconnect_failure_keeps_none(self, flag):
        flag.device = None
        with patch("luxafor.local._hid.hid.Device", side_effect=OSError("gone")):
            flag.connect()
        assert flag.device is None


class TestLuxaforFlagSetColor:
    def test_writes_correct_bytes(self, flag, mock_hid_device):
        _, mock_device = mock_hid_device
        flag.set_color(FlagColor.RED)

        mock_device.write.assert_called_once()
        written = mock_device.write.call_args.args[0]
        assert isinstance(written, bytes)
        assert len(written) == 8
        assert written[0] == 0x00
        assert written[2] == FlagColor.RED.value

    def test_reconnects_when_device_none(self, mock_hid_device):
        mock_cls, mock_device = mock_hid_device
        flag = LuxaforFlag()
        flag.device = None
        mock_cls.reset_mock()

        flag.set_color(FlagColor.GREEN)

        mock_cls.assert_called_once_with(0x04D8, 0xF372)
        mock_device.write.assert_called_once()

    def test_no_write_when_reconnect_fails(self, flag):
        flag.device = None
        with patch("luxafor.local._hid.hid.Device", side_effect=OSError("gone")):
            flag.set_color(FlagColor.BLUE)
        assert flag.device is None

    def test_write_failure_clears_device(self, flag, mock_hid_device):
        _, mock_device = mock_hid_device
        mock_device.write.side_effect = OSError("write failed")

        flag.set_color(FlagColor.RED)

        assert flag.device is None

    def test_write_failure_does_not_raise(self, flag, mock_hid_device):
        _, mock_device = mock_hid_device
        mock_device.write.side_effect = OSError("write failed")
        flag.set_color(FlagColor.RED)

    @pytest.mark.parametrize("color", list(FlagColor))
    def test_all_colors(self, flag, mock_hid_device, color):
        _, mock_device = mock_hid_device
        flag.set_color(color)

        written = mock_device.write.call_args.args[0]
        assert written[2] == color.value
