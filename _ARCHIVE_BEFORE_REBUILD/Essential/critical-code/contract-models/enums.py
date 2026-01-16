from enum import Enum


class TemplateType(Enum):
    """
    Contract template types supported by the system.

    WHY: Enums provide type-safe alternatives to string constants, preventing
         typos and invalid values at development time rather than runtime.
    WHAT: Represents the four types of contract templates available in the system:
         engineering, consulting, military, and governmental contracts.
    HOW: Used throughout the system for template selection, loading, and validation.
         The value is used for storage/serialization, the name for display.

    Example:
        >>> template_type = TemplateType.ENGINEERING
        >>> print(template_type.value)
        engineering
        >>> print(str(template_type))
        Engineering
    """
    ENGINEERING = "engineering"
    CONSULTING = "consulting"
    MILITARY = "military"
    GOVERNMENTAL = "governmental"

    def __str__(self) -> str:
        """
        Return human-readable template type name.

        Returns:
            Capitalized template type name (e.g., "Engineering")

        WHY: Provides user-friendly display text for UI and reports
        WHAT: Converts enum value to title case for readability
        HOW: Uses str.capitalize() on the enum value
        """
        return self.value.capitalize()


class SeverityLevel(Enum):
    """
    Severity levels for compliance issues.

    WHY: Provides type-safe severity classification for compliance issues,
         enabling consistent prioritization and sorting across the system.
    WHAT: Represents three levels of issue severity - HIGH (critical issues
         that must be addressed), MEDIUM (important but not blocking), and
         LOW (minor issues or suggestions).
    HOW: Used in ComplianceIssue model for categorization. The get_priority()
         method enables sorting issues by severity (HIGH first).

    Example:
        >>> severity = SeverityLevel.HIGH
        >>> print(severity.value)
        high
        >>> print(str(severity))
        High
        >>> print(severity.get_priority())
        1
    """
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    def __str__(self) -> str:
        """
        Return human-readable severity level.

        Returns:
            Capitalized severity level (e.g., "High")
        """
        return self.value.capitalize()

    def get_priority(self) -> int:
        """
        Get numeric priority for sorting (lower number = higher priority).

        Returns:
            Priority value (1=HIGH, 2=MEDIUM, 3=LOW)

        WHY: Enables sorting compliance issues by severity, ensuring critical
             issues appear first in reports and UI displays.
        WHAT: Maps each severity level to a numeric priority where lower
             numbers indicate higher priority (more urgent).
        HOW: Uses a dictionary lookup to map enum members to integers.
             Used with sorted() key parameter for issue ordering.

        Example:
            >>> issues = [issue1, issue2, issue3]
            >>> sorted_issues = sorted(issues, key=lambda i: i.severity.get_priority())
            >>> # Now issues are ordered: HIGH, MEDIUM, LOW
        """
        return {
            SeverityLevel.HIGH: 1,
            SeverityLevel.MEDIUM: 2,
            SeverityLevel.LOW: 3
        }[self]
