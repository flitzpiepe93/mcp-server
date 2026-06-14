import fastmcp.server.dependencies as deps
import pytest
from fastmcp import Client
from fastmcp.server.auth import AccessToken
from server.app import build_server
from server.repository import MemoryTitanicRepository, SurvivalGroupBy, SurvivalRate

EXPECTED = [
    SurvivalRate(sex="female", count=314, survival_rate=0.742),
    SurvivalRate(sex="male", count=577, survival_rate=0.189),
]


@pytest.fixture
def authenticated(monkeypatch):
    """Inject a fake identity with the required scopes.

    The in-memory transport carries no token, so the scope-protected tool
    would otherwise be filtered out. Patching FastMCP's public
    ``get_access_token`` lets us exercise the tool path without a real Keycloak.
    """
    token = AccessToken(
        token="test-token",
        client_id="example-agent",
        scopes=["titanic:access", "titanic:survival:read"],
        expires_at=None,
    )
    monkeypatch.setattr(deps, "get_access_token", lambda: token)


@pytest.fixture
def client():
    repo = MemoryTitanicRepository({SurvivalGroupBy.SEX: EXPECTED})
    return Client(build_server(lambda: repo))


async def test_get_survival_rate_returns_repository_data(authenticated, client):
    async with client:
        result = await client.call_tool("get_survival_rate", {"group_by": "sex"})

    returned = [(r.sex, r.count, r.survival_rate) for r in result.data]
    assert returned == [(e.sex, e.count, e.survival_rate) for e in EXPECTED]


async def test_get_survival_rate_is_listed(authenticated, client):
    async with client:
        tools = await client.list_tools()

    assert "get_survival_rate" in {t.name for t in tools}
