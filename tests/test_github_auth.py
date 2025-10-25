import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock
from app.services.github_auth import GitHubAuthService
from app.services.github_app_auth import GitHubAppCredentials, GitHubAppAuthService


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
def mock_http_client():
    """Create a mock HTTP client."""
    return MagicMock(spec=httpx.AsyncClient)


@pytest.fixture
def mock_credentials(mock_private_key):
    """Create GitHubAppCredentials for testing."""
    return GitHubAppCredentials(app_id="123456", private_key=mock_private_key)


def test_github_auth_service_initialization_with_personal_token(mock_http_client):
    """Test GitHubAuthService initialization with personal token."""
    auth_service = GitHubAuthService(
        http_client=mock_http_client,
        personal_token="ghp_test_token",
    )
    assert auth_service.personal_token == "ghp_test_token"
    assert auth_service.app_auth_service is None


def test_github_auth_service_initialization_with_app_credentials(mock_http_client, mock_credentials):
    """Test GitHubAuthService initialization with GitHub App credentials."""
    auth_service = GitHubAuthService(
        http_client=mock_http_client,
        app_credentials=mock_credentials,
    )
    assert auth_service.personal_token is None
    assert auth_service.app_auth_service is not None
    assert isinstance(auth_service.app_auth_service, GitHubAppAuthService)


def test_github_auth_service_initialization_with_both(mock_http_client, mock_credentials):
    """Test GitHubAuthService initialization fails with both personal token and app credentials."""
    with pytest.raises(ValueError, match="Provide either personal_token or app_credentials, not both"):
        GitHubAuthService(
            http_client=mock_http_client,
            personal_token="ghp_test_token",
            app_credentials=mock_credentials,
        )


def test_github_auth_service_initialization_without_credentials(mock_http_client):
    """Test GitHubAuthService initialization fails without any credentials."""
    with pytest.raises(ValueError, match="Either personal_token or app_credentials must be provided"):
        GitHubAuthService(http_client=mock_http_client)


@pytest.mark.asyncio
async def test_get_auth_header_with_personal_token(mock_http_client):
    """Test get_auth_header returns personal token when available."""
    auth_service = GitHubAuthService(
        http_client=mock_http_client,
        personal_token="ghp_test_token",
    )
    
    header = await auth_service.get_auth_header()
    assert header == "Bearer ghp_test_token"


@pytest.mark.asyncio
async def test_get_auth_header_with_personal_token_with_repo(mock_http_client):
    """Test get_auth_header with personal token when owner/repo provided (ignores them)."""
    auth_service = GitHubAuthService(
        http_client=mock_http_client,
        personal_token="ghp_test_token",
    )
    
    header = await auth_service.get_auth_header(owner="owner", repo="repo")
    assert header == "Bearer ghp_test_token"


@pytest.mark.asyncio
async def test_get_auth_header_with_app_auth_success(mock_http_client, mock_credentials):
    """Test get_auth_header with GitHub App authentication success."""
    auth_service = GitHubAuthService(
        http_client=mock_http_client,
        app_credentials=mock_credentials,
    )
    
    # Mock the app auth service get_token_for_repo method
    auth_service.app_auth_service.get_token_for_repo = AsyncMock(return_value="ghs_app_token")
    
    header = await auth_service.get_auth_header(owner="test-owner", repo="test-repo")
    assert header == "Bearer ghs_app_token"
    auth_service.app_auth_service.get_token_for_repo.assert_called_once_with("test-owner", "test-repo")


@pytest.mark.asyncio
async def test_get_auth_header_with_app_auth_failure(mock_http_client, mock_credentials):
    """Test get_auth_header with GitHub App authentication failure."""
    auth_service = GitHubAuthService(
        http_client=mock_http_client,
        app_credentials=mock_credentials,
    )
    
    # Mock the app auth service get_token_for_repo method to return None
    auth_service.app_auth_service.get_token_for_repo = AsyncMock(return_value=None)
    
    with pytest.raises(ValueError, match="GitHub App authentication failed"):
        await auth_service.get_auth_header(owner="test-owner", repo="test-repo")


@pytest.mark.asyncio
async def test_get_auth_header_with_app_auth_requires_owner_repo(mock_http_client, mock_credentials):
    """Test get_auth_header requires owner/repo when using GitHub App auth."""
    auth_service = GitHubAuthService(
        http_client=mock_http_client,
        app_credentials=mock_credentials,
    )
    
    with pytest.raises(ValueError, match="owner and repo are required for GitHub App authentication"):
        await auth_service.get_auth_header()


@pytest.mark.asyncio
async def test_get_auth_header_with_app_auth_without_repo(mock_http_client, mock_credentials):
    """Test get_auth_header fails when only owner is provided with GitHub App auth."""
    auth_service = GitHubAuthService(
        http_client=mock_http_client,
        app_credentials=mock_credentials,
    )
    
    with pytest.raises(ValueError, match="owner and repo are required for GitHub App authentication"):
        await auth_service.get_auth_header(owner="test-owner")


@pytest.mark.asyncio
async def test_get_auth_header_app_only_without_owner_repo(mock_http_client, mock_credentials):
    """Test get_auth_header fails when only app credentials available and owner/repo not provided."""
    auth_service = GitHubAuthService(
        http_client=mock_http_client,
        app_credentials=mock_credentials,
    )
    
    with pytest.raises(ValueError, match="owner and repo are required for GitHub App authentication"):
        await auth_service.get_auth_header()

