from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from furl import furl

from luxafor.remote.webhook import FlagColor, RemoteWebhookFlag, main


@pytest.fixture
def webhook_flag():
    return RemoteWebhookFlag()


@pytest.fixture
def mock_httpx_client():
    mock_response = MagicMock()
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)

    mock_class = MagicMock()
    mock_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
    mock_class.return_value.__aexit__ = AsyncMock(return_value=False)

    with patch("luxafor.remote.webhook.httpx.AsyncClient", mock_class):
        yield mock_client


@pytest.mark.parametrize(
    ("member", "expected"),
    [
        (FlagColor.RED, "red"),
        (FlagColor.GREEN, "green"),
        (FlagColor.YELLOW, "yellow"),
        (FlagColor.BLUE, "blue"),
        (FlagColor.WHITE, "white"),
        (FlagColor.CYAN, "cyan"),
        (FlagColor.MAGENTA, "magenta"),
    ],
)
def test_flag_color_values(member, expected):
    assert member.value == expected


def test_flag_color_member_count():
    assert len(FlagColor) == 7


def test_flag_color_lookup_by_value():
    assert FlagColor("red") is FlagColor.RED


def test_flag_color_invalid_value():
    with pytest.raises(ValueError, match="invalid"):
        FlagColor("invalid")


def test_init_defaults(webhook_flag):
    assert webhook_flag.token == "CaUt1RwoiqSzeD9PuT-_tyUfR-9ZeTq31bF3kKAqbtY"
    assert webhook_flag.user_id == "b72bbd0b799a"
    assert str(webhook_flag.url) == "http://localhost:5383"


def test_init_custom_parameters():
    flag = RemoteWebhookFlag(
        token="custom-token",
        user_id="custom-user",
        host="example.com",
        port=8080,
    )
    assert flag.token == "custom-token"
    assert flag.user_id == "custom-user"
    assert str(flag.url) == "http://example.com:8080"


def test_init_url_is_furl(webhook_flag):
    assert isinstance(webhook_flag.url, furl)


@pytest.mark.anyio
async def test_solid_color_posts_correct_url(webhook_flag, mock_httpx_client):
    await webhook_flag.solid_color(FlagColor.RED)

    mock_httpx_client.post.assert_called_once()
    call_args = mock_httpx_client.post.call_args
    assert call_args.args[0] == "http://localhost:5383/webhook/v1/actions/solid_color"


@pytest.mark.anyio
async def test_solid_color_sends_correct_payload(webhook_flag, mock_httpx_client):
    await webhook_flag.solid_color(FlagColor.GREEN)

    call_kwargs = mock_httpx_client.post.call_args.kwargs
    assert call_kwargs["json"] == {
        "userId": "b72bbd0b799a",
        "actionFields": {"color": "green"},
    }


@pytest.mark.anyio
async def test_solid_color_uses_timeout(webhook_flag, mock_httpx_client):
    await webhook_flag.solid_color(FlagColor.BLUE)

    call_kwargs = mock_httpx_client.post.call_args.kwargs
    assert call_kwargs["timeout"] == 10


@pytest.mark.anyio
async def test_solid_color_with_custom_flag(mock_httpx_client):
    flag = RemoteWebhookFlag(
        token="t",
        user_id="custom-user",
        host="api.example.com",
        port=9000,
    )
    await flag.solid_color(FlagColor.CYAN)

    call_args = mock_httpx_client.post.call_args
    assert call_args.args[0] == "http://api.example.com:9000/webhook/v1/actions/solid_color"
    assert call_args.kwargs["json"]["userId"] == "custom-user"
    assert call_args.kwargs["json"]["actionFields"]["color"] == "cyan"


@pytest.mark.parametrize("color", list(FlagColor))
@pytest.mark.anyio
async def test_solid_color_all_colors(webhook_flag, mock_httpx_client, color):
    await webhook_flag.solid_color(color)

    payload = mock_httpx_client.post.call_args.kwargs["json"]
    assert payload["actionFields"]["color"] == color.value


def test_set_color_raises_attribute_error(webhook_flag):
    with pytest.raises(AttributeError, match="device"):
        webhook_flag.set_color(FlagColor.RED)


@pytest.mark.anyio
async def test_main_calls_solid_color_red(mock_httpx_client):
    await main()

    mock_httpx_client.post.assert_called_once()
    call_args = mock_httpx_client.post.call_args
    assert call_args.args[0] == "http://localhost:5383/webhook/v1/actions/solid_color"
    assert call_args.kwargs["json"]["actionFields"]["color"] == "red"
