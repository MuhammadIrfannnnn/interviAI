from pydantic import BaseModel, Field, field_validator
from typing import Literal

# Single-word professional titles that are accepted even when short (< 6 chars).
# This is NOT a whitelist — multi-word roles and long single words are also accepted.
_PROFESSIONAL_TITLES = frozenset({
    # Technology
    "developer", "engineer", "architect", "administrator",
    # Business
    "manager", "director", "consultant", "analyst", "executive",
    "coordinator", "strategist", "planner",
    # Finance
    "accountant", "auditor", "actuary", "bookkeeper",
    # Healthcare
    "doctor", "physician", "nurse", "pharmacist", "dentist",
    "surgeon", "therapist", "pathologist", "radiologist",
    "optometrist", "dietitian", "midwife",
    # Legal
    "lawyer", "attorney", "paralegal", "advocate", "counsel",
    "magistrate", "prosecutor",
    # Education
    "teacher", "lecturer", "professor", "tutor", "educator",
    "principal", "dean",
    # Design / Creative
    "designer", "illustrator", "animator", "photographer",
    "videographer", "copywriter", "journalist", "editor",
    "author", "curator", "producer", "director",
    # Trades
    "electrician", "plumber", "carpenter", "mechanic", "welder",
    "surveyor", "inspector", "technician",
    # Science
    "biologist", "chemist", "physicist", "geologist",
    "statistician", "researcher", "scientist",
    # Other
    "recruiter", "chef", "pilot", "navigator", "translator",
    "interpreter", "librarian", "phlebotomist",
})


class InterviewStart(BaseModel):
    role_applied: str = Field(..., min_length=2, max_length=100, description="Job role candidate is applying for")
    difficulty: Literal["Easy", "Medium", "Hard"]

    @field_validator("role_applied")
    @classmethod
    def validate_role(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Please enter a job role.")

        alpha_count = sum(1 for c in value if c.isalpha())
        if alpha_count < 2:
            raise ValueError("Please enter a valid professional job role.")

        # Reject runs of the same character (e.g. "aaaaaa")
        run = 1
        for i in range(1, len(value)):
            if value[i] == value[i - 1]:
                run += 1
                if run > 3:
                    raise ValueError("Please enter a valid professional job role.")
            else:
                run = 1

        # Reject common keyboard-smash sequences
        lower = value.lower()
        for smash in ("asdf", "qwer", "zxcv", "wasd"):
            if smash in lower:
                raise ValueError("Please enter a valid professional job role.")

        # ── Professional-role sanity check ──────────────────────────────────
        words = value.split()

        # Multi-word roles: accept if at least one word has 4+ alpha chars
        if len(words) >= 2:
            substantial = [
                w for w in words
                if sum(1 for c in w if c.isalpha()) >= 4
            ]
            if len(substantial) >= 1:
                return value
            raise ValueError("Please enter a valid professional job role.")

        # Single-word roles: must be a recognised title, end with a
        # professional suffix, or be long enough to be plausible.
        word = lower.strip()

        # Known short professional titles (nurse, chef, …)
        if word in _PROFESSIONAL_TITLES:
            return value

        # Common professional-role suffixes  (-er, -or, -ist, …)
        _PRO_SUFFIXES = (
            "er", "or", "ist", "ant",
            "ian", "ee", "man",
        )
        if any(word.endswith(s) and len(word) >= 5 for s in _PRO_SUFFIXES):
            return value

        # Long single words (8+ chars) are plausible custom roles
        if len(word) >= 8:
            return value

        raise ValueError("Please enter a valid professional job role.")