"""Pydantic models for HubSpot CRM API responses."""

from typing import Any

from pydantic import BaseModel, Field


class Paging(BaseModel):
    """HubSpot pagination cursor."""

    model_config = {"populate_by_name": True}

    after: str | None = Field(default=None, alias="after")


class PagingResponse(BaseModel):
    """HubSpot paging wrapper."""

    next: Paging | None = Field(default=None)


class CrmProperties(BaseModel):
    """Common CRM object properties returned by HubSpot."""

    model_config = {"populate_by_name": True, "extra": "allow"}


class CrmObject(BaseModel):
    """A single HubSpot CRM object (contact, company, or deal)."""

    id: str = Field(..., description="HubSpot object ID")
    properties: dict[str, Any] = Field(default_factory=dict, description="Object properties")
    created_at: str | None = Field(default=None, alias="createdAt")
    updated_at: str | None = Field(default=None, alias="updatedAt")
    archived: bool = Field(default=False)


class CrmListResponse(BaseModel):
    """Response from a CRM list endpoint."""

    model_config = {"populate_by_name": True}

    results: list[CrmObject] = Field(default_factory=list)
    paging: PagingResponse | None = Field(default=None)
