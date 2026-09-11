from typing import Literal

from pydantic import BaseModel, Field


class EmailAnalysis(BaseModel):
    category: Literal[
        "Customer Support",
        "Sales",
        "Complaint",
        "Job Inquiry",
        "Invoice",
        "General",
        "Spam",
    ]

    priority: Literal[
        "LOW",
        "MEDIUM",
        "HIGH",
        "URGENT",
    ]

    intent: str = Field(
        min_length=1,
        max_length=500,
    )

    summary: str = Field(
        min_length=1,
        max_length=1000,
    )

    requires_reply: bool