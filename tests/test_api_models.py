"""Tests for HubSpot API models."""

from mcp_hubspot.api_models import CrmListResponse, CrmObject, Paging, PagingResponse


def test_crm_object_full() -> None:
    """Test CrmObject with all fields."""
    data = {
        "id": "123",
        "properties": {"email": "test@example.com", "firstname": "Jane"},
        "createdAt": "2026-01-01T00:00:00Z",
        "updatedAt": "2026-01-02T00:00:00Z",
        "archived": False,
    }
    obj = CrmObject(**data)
    assert obj.id == "123"
    assert obj.properties["email"] == "test@example.com"
    assert obj.created_at == "2026-01-01T00:00:00Z"
    assert obj.archived is False


def test_crm_object_minimal() -> None:
    """Test CrmObject with only required fields."""
    obj = CrmObject(id="456")
    assert obj.id == "456"
    assert obj.properties == {}
    assert obj.created_at is None
    assert obj.archived is False


def test_paging() -> None:
    """Test Paging model."""
    paging = Paging(after="abc123")
    assert paging.after == "abc123"


def test_paging_response() -> None:
    """Test PagingResponse model."""
    resp = PagingResponse(next=Paging(after="next_cursor"))
    assert resp.next is not None
    assert resp.next.after == "next_cursor"


def test_paging_response_none() -> None:
    """Test PagingResponse with no next page."""
    resp = PagingResponse()
    assert resp.next is None


def test_crm_list_response() -> None:
    """Test CrmListResponse with results and paging."""
    data = {
        "results": [
            {"id": "1", "properties": {"name": "First"}},
            {"id": "2", "properties": {"name": "Second"}},
        ],
        "paging": {"next": {"after": "3"}},
    }
    response = CrmListResponse(**data)
    assert len(response.results) == 2
    assert response.results[0].id == "1"
    assert response.paging is not None
    assert response.paging.next is not None
    assert response.paging.next.after == "3"


def test_crm_list_response_empty() -> None:
    """Test CrmListResponse with no results."""
    response = CrmListResponse()
    assert response.results == []
    assert response.paging is None
