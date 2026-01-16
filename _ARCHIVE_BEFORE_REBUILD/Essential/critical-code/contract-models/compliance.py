"""
Compliance report data models using Pydantic.

WHY: Compliance checking produces structured results
WHAT: Models for issues, suggestions, and reports
HOW: Inherit from BaseModel, use validators for score constraints
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
from shared.models.enums import SeverityLevel


class RewriteSuggestion(BaseModel):
    """
    Suggested rewrite for a compliance issue.

    Attributes:
        original_text: The problematic text
        suggested_text: The recommended replacement
        confidence: Confidence score (0.0 to 1.0)
    """
    # TODO: Define fields
    # Hint: confidence should be between 0.0 and 1.0
    original_text: str
    suggested_text: str
    confidence: float = Field(gt=0.0, le=1.0)


class ComplianceIssue(BaseModel):
    """
    A single compliance issue found during review.

    Attributes:
        severity: Issue severity level (HIGH, MEDIUM, LOW)
        description: Detailed description of the issue
        clause_index: Optional index of the affected clause
        suggestions: List of rewrite suggestions
    """
    severity: SeverityLevel
    description: str = Field(min_length=1)
    clause_index: Optional[int] = None
    suggestions: List[RewriteSuggestion] = Field(default_factory=list)
    

class ComplianceReport(BaseModel):
    """
    Complete compliance report for a contract.

    Attributes:
        contract_id: ID of the reviewed contract
        score: Overall compliance score (0.0 to 1.0)
        issues: List of compliance issues found
        checked_at: Timestamp of the review
    """
    contract_id: str
    score: float = Field(ge=0.0, le=1.0)
    issues: List[ComplianceIssue] = Field(default_factory=list)
    checked_at: datetime = Field(default_factory=datetime.now)

    @field_validator('score')
    @classmethod
    def validate_score_precision(cls, v: float) -> float:
        """Round score to 2 decimal places for consistency."""
        return round(v, 2)
    
