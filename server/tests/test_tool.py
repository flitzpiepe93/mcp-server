import fastmcp.server.dependencies as deps
import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError
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
def under_scoped(monkeypatch):
    """Inject an identity admitted to the server but missing the tool scope.

    Carries the base ``titanic:access`` scope (so it authenticates) but not
    ``titanic:survival:read``, exercising the per-tool authorization boundary.
    """
    token = AccessToken(
        token="test-token",
        client_id="example-agent",
        scopes=["titanic:access"],
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


async def test_missing_tool_scope_is_rejected(under_scoped, client):
    """A token without titanic:survival:read must not reach the tool, even
    though it is admitted to the server via the base scope."""
    with pytest.raises(ToolError):
        async with client:
            await client.call_tool("get_survival_rate", {"group_by": "sex"})


async def test_missing_tool_scope_hides_tool_from_listing(under_scoped, client):
    """The tool is filtered out of the listing for an under-scoped token, so it
    is never advertised to an agent that may not call it."""
    async with client:
        tools = await client.list_tools()

    assert "get_survival_rate" not in {t.name for t in tools}


async def test_audit_log_records_agent_identity(authenticated, client, caplog):
    """The audit trail must attribute the call to the authenticated agent,
    not fall back to ``anonymous`` — guards the dependencies import in audit.py.
    """
    with caplog.at_level("INFO", logger="fastmcp.audit"):
        async with client:
            await client.call_tool("get_survival_rate", {"group_by": "sex"})

    assert "agent=example-agent" in caplog.text
