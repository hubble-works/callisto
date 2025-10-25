import pytest
import time
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.github_app_auth import GitHubAppAuth


@pytest.fixture
def mock_private_key():
    """Mock RSA private key for testing."""
    return """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDKAmBFmojwu6IK
m+4XfVg5eg+Kv7TsSV3CWFgezEzKqMXpqyfuiO/56LGXpr9I+qwUoTnt62ksTJNl
ZbZ6UhsDEm0Ls3iSisl8hzTmzPF3VzYVRV8JbzX/ZJOBBQEc0YEOI0iXro7tWLVo
j2HisXCMxctrIPpi5rq9dJFJckmN+65iRv/kGqP6jD2I9wb9r2BBsXAtuRgMnbAe
jgjESIhhQsbCUsKaPQkUaILgQjLzDkfQQAa2AA69GVuV8Kwu7v5dbfEcFWfoaDUT
HSb1saSukC9lPAPZ2kk3Bg7epPt9Q56qxm4Ls3KGKEOTyJO+TQnewmEX+WB13312
x+A5LwObAgMBAAECggEAGoVvAURgJ9w30n+/+wUsUON7EzgcYeHh9YgmuD28npDD
kcGJomddEOjhbqu9ilsgE4H1T+IBHV1HrrTIsneBb15QbbcCz0PPCdKFz1VnJZ1l
ZCvcOyoGzgB03dKmij42h4DPYNv8jMxW3iLmSDO2jJd9Sj56plhsz5R0bKRHZDnu
ZF0luzLxrNhACmmdzkQ9L/bu/AvtG02+79zHnU9NdFFxX0WdVFZ6BtkMVIO1oBqk
WgoHHpdGgYm4TYMHIYOaGOwr3qfLCNZH9ZBArRuSYfX1mCBKQLIwm2pRmrJWUmrA
53SQzllIxk5vWSTTp8xXicHUvjKb25RlGJTfRY4juQKBgQD1yozz8v2Wj4aZH1GU
xuZbdCA+MTcVIJZlhuU4LNShPe0KVAMnrNS4VipMGKyUm7mNnFV67SEFI+iIHHFW
HGp7s85V1W/fD2TvO4Fe1XZr1zdhYV+6J2gY6Xk8whcVGVwPsIujf6BwfyTVFt6F
4AGtSQ8YpITgf9D6fUsVml1uYwKBgQDSZk0Di9BoS4fa1MHoiQ0PctJhdTk3UK/2
y3U9FpwXY44OzkFEI6NdQ7P0z3KvLpOEeS4LxMsSARTh/0HWYYopAEk5jWZBD0hn
s2mhfum4B4qk9plbaldfR6Lqr+SdVslBYqEDy2agCHmYmdvX2RZyIMKL2wopL5EV
H0PMiWJfaQKBgFZ6J1GFQreAU+j33eoseMvgdZ+sDSc/yep6pZc4Hq+EbCvgFyQU
aNtaZZNUcxPuHkC2qlSPrbhzQ9Lvvuh/Iu/W+Ve1uqCOeAK7uu60x+91TyTR7649
QyDQtDkuSJTB0WQrx1WFB9vMwBbA7xXHFI/1TnxrFd0u20XmY058ezblAoGBALIR
VtjLeeTrF93C9yIA7AbJHPjSp0wDhAmRhHXhLtY0scQiF+a9asPCSwnEkMFm3/7c
OHZJZbylIbFrwaLZBn9Q+Kg23fXuI09w7tN5gAD6kQKwmnZd9/hxvpZ1qzzmeIpY
GQIHIaILyi22+fMijfald0G6bk0RLu77ePwgwhsRAoGAVmx+pCMdPeREfl0vl4UQ
+MrTueCy7gEty+19lo4RN5SQw8wSGu447oTweyiysb9n+Ig1Q5DDQWMqAaY00S/F
nViVpbtR3Scila1w38fNeCW+taxb0CMbvCJaUbANLrjW9klMPGhIxCyxgXQvDAIL
ML4epSb9IvX5lG17pL4P3p4=
-----END PRIVATE KEY-----"""


@pytest.fixture
def github_app_auth(mock_private_key):
    """Create a GitHubAppAuth instance for testing."""
    return GitHubAppAuth(app_id="123456", private_key=mock_private_key)


def test_github_app_auth_initialization(mock_private_key):
    """Test GitHubAppAuth initialization."""
    auth = GitHubAppAuth(app_id="123456", private_key=mock_private_key)
    assert auth.app_id == "123456"
    assert auth.private_key == mock_private_key
    assert auth._installation_tokens == {}


def test_generate_jwt(github_app_auth):
    """Test JWT generation."""
    with patch("time.time", return_value=1000):
        jwt_token = github_app_auth.generate_jwt()
        assert jwt_token is not None
        assert isinstance(jwt_token, str)


@pytest.mark.asyncio
async def test_get_installation_id_success(github_app_auth):
    """Test successful retrieval of installation ID."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": 12345678}
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

        installation_id = await github_app_auth.get_installation_id("owner", "repo")
        assert installation_id == 12345678


@pytest.mark.asyncio
async def test_get_installation_id_failure(github_app_auth):
    """Test failed retrieval of installation ID."""
    from httpx import HTTPStatusError, Response, Request

    mock_request = Request("GET", "https://api.github.com/repos/owner/repo/installation")
    mock_response = Response(status_code=404, request=mock_request)

    async def mock_get(*args, **kwargs):
        raise HTTPStatusError("Not Found", request=mock_request, response=mock_response)

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = mock_get

        installation_id = await github_app_auth.get_installation_id("owner", "repo")
        assert installation_id is None


@pytest.mark.asyncio
async def test_get_installation_access_token_success(github_app_auth):
    """Test successful retrieval of installation access token."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "token": "ghs_test_token",
        "expires_at": "2025-10-25T18:00:00Z",
    }
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )

        token = await github_app_auth.get_installation_access_token(12345678)
        assert token == "ghs_test_token"
        # Verify token is cached
        assert 12345678 in github_app_auth._installation_tokens


@pytest.mark.asyncio
async def test_get_installation_access_token_cached(github_app_auth):
    """Test that cached tokens are reused."""
    # Pre-populate cache with a valid token
    future_expiry = time.time() + 3600  # 1 hour from now
    github_app_auth._installation_tokens[12345678] = {
        "token": "cached_token",
        "expires_at": future_expiry,
    }

    # Should return cached token without making HTTP request
    token = await github_app_auth.get_installation_access_token(12345678)
    assert token == "cached_token"


@pytest.mark.asyncio
async def test_get_token_for_repo_success(github_app_auth):
    """Test successful retrieval of token for a repository."""
    mock_installation_response = MagicMock()
    mock_installation_response.json.return_value = {"id": 12345678}
    mock_installation_response.raise_for_status = MagicMock()

    mock_token_response = MagicMock()
    mock_token_response.json.return_value = {
        "token": "ghs_test_token",
        "expires_at": "2025-10-25T18:00:00Z",
    }
    mock_token_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client:
        mock_async_client = mock_client.return_value.__aenter__.return_value
        mock_async_client.get = AsyncMock(return_value=mock_installation_response)
        mock_async_client.post = AsyncMock(return_value=mock_token_response)

        token = await github_app_auth.get_token_for_repo("owner", "repo")
        assert token == "ghs_test_token"


@pytest.mark.asyncio
async def test_get_token_for_repo_no_installation(github_app_auth):
    """Test token retrieval when installation is not found."""
    from httpx import HTTPStatusError, Response, Request

    mock_request = Request("GET", "https://api.github.com/repos/owner/repo/installation")
    mock_response = Response(status_code=404, request=mock_request)

    async def mock_get(*args, **kwargs):
        raise HTTPStatusError("Not Found", request=mock_request, response=mock_response)

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = mock_get

        token = await github_app_auth.get_token_for_repo("owner", "repo")
        assert token is None
