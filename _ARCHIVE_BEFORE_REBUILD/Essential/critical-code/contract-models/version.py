"""
Version management data models using Pydantic.

WHY: Track contract changes over time for audit trails and rollback capability
WHAT: Models for versioned contract snapshots and change tracking
HOW: Uses Pydantic BaseModel with references to Contract model
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from shared.models.contract import Contract


class VersionDiff(BaseModel):
    """
    Represents differences between two contract versions.

    WHY: Enables users to see what changed between versions without
         comparing full documents manually.
    WHAT: Tracks which sections were added, removed, or modified
         between consecutive versions.
    HOW: Populated by comparing section titles between versions.
         Used in version history UI to show change summaries.

    Attributes:
        added_sections: Titles of newly added sections
        removed_sections: Titles of removed sections
        modified_sections: Titles of modified sections

    Example:
        >>> diff = VersionDiff(
        ...     added_sections=["Warranties"],
        ...     modified_sections=["Payment Terms"]
        ... )
        >>> print(diff.added_sections)
        ['Warranties']
    """
    added_sections: List[str] = Field(default_factory=list)
    removed_sections: List[str] = Field(default_factory=list)
    modified_sections: List[str] = Field(default_factory=list)


class Version(BaseModel):
    """
    A versioned snapshot of a contract.

    WHY: Track contract changes over time for audit and rollback
    WHAT: Stores a complete contract snapshot with metadata
    HOW: References Contract model and optional diff from previous version

    Attributes:
        version_id: Unique version identifier (e.g., "v1", "v2")
        contract: The contract snapshot at this version
        created_at: Timestamp of version creation
        diff_from_previous: Changes from previous version (None for first version)

    Example:
        >>> version = Version(
        ...     version_id="v1",
        ...     contract=contract,
        ... )
        >>> print(version.version_id)
        v1
    """
    version_id: str = Field(..., min_length=1)
    contract: Contract
    created_at: datetime = Field(default_factory=datetime.now)
    diff_from_previous: Optional[VersionDiff] = None