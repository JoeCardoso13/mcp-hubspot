"""
Shared fixtures and configuration for integration tests.

These tests require a valid HUBSPOT_ACCESS_TOKEN environment variable.
They make real API calls and should not be run in CI without proper setup.
"""

import os

import pytest
import pytest_asyncio

from mcp_hubspot.api_client import HubspotClient


def pytest_configure(config):
    """Check for required environment variables before running tests."""
    if not os.environ.get("HUBSPOT_ACCESS_TOKEN"):
        pytest.exit(
            "ERROR: HUBSPOT_ACCESS_TOKEN environment variable is required.\n"
            "Set it before running integration tests:\n"
            "  export HUBSPOT_ACCESS_TOKEN=your_token_here\n"
            "  make test-integration"
        )


@pytest.fixture
def access_token() -> str:
    """Get the access token from environment."""
    token = os.environ.get("HUBSPOT_ACCESS_TOKEN")
    if not token:
        pytest.skip("HUBSPOT_ACCESS_TOKEN not set")
    return token


@pytest_asyncio.fixture
async def client(access_token: str) -> HubspotClient:
    """Create a client for testing."""
    client = HubspotClient(access_token=access_token)
    yield client
    await client.close()


# TODO: Add well-known test data constants
# class TestData:
#     """Well-known test data for integration tests."""
#     KNOWN_ID = "abc123"
