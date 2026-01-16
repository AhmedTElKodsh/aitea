"""
Contract data models using Pydantic.

WHY: Pydantic provides automatic validation and JSON serialization
WHAT: Core data models for contracts, sections, and clauses
HOW: Inherit from BaseModel, use Field() for constraints
"""

import re
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
from shared.models.enums import TemplateType


class Clause(BaseModel):
    """
    A single clause within a contract section.

    Attributes:
        text: The clause content (required, non-empty)
        required: Whether this clause is mandatory

    Example:
        >>> clause = Clause(text="The contractor shall...", required=True)
        >>> print(clause.text)
        The contractor shall...
    """
    text: str = Field(..., min_length=1)
    required: bool = True


class Section(BaseModel):
    """
    A section containing multiple clauses.

    Attributes:
        title: Section heading (required, non-empty)
        description: Optional section description
        clauses: List of Clause objects

    Example:
        >>> section = Section(title="Scope of Work")
        >>> section.clauses.append(Clause(text="..."))
    """
    title: str = Field(..., min_length=1)
    description: Optional[str] = None 
    clauses: List[Clause] = Field(default_factory=list)


class Contract(BaseModel):
    """
    A complete contract document.

    Attributes:
        project_code: Unique identifier (PROJ-XXXX-YYYY format)
        template_type: Type of contract template
        sections: List of Section objects
        created_at: Timestamp of creation

    Example:
        >>> contract = Contract(
        ...     project_code="PROJ-2024-0001",
        ...     template_type=TemplateType.ENGINEERING
        ... )
    """
    project_code: str = Field(..., pattern=r"^PROJ-\d{4}-\d{4}$")
    template_type: TemplateType
    sections: List[Section] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)