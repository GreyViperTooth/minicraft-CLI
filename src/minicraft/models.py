"""Pydantic models for minicraft project validation."""

from pydantic import BaseModel, ConfigDict, Field


class CraftBaseModel(BaseModel):
    """Base model for all minicraft models.

    Rejects unknown fields to catch typos in YAML specs early.
    """

    model_config = ConfigDict(extra="forbid")


class PartSpec(CraftBaseModel):
    """Specification for a single part in the project."""

    plugin: str = Field(description="The plugin to use for building this part.")
    source: str = Field(default=".", description="The source directory for this part.")
    after: list[str] = Field(
        default_factory=list,
        description="Parts that must be staged before this part can build.",
    )


class Project(CraftBaseModel):
    """Top-level project model validated from a YAML spec file."""

    name: str = Field(description="The identifying name of the project.")
    parts: dict[str, PartSpec] = Field(
        description="A mapping of part names to their specifications.",
    )
