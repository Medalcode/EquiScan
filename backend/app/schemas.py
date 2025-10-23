from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class ScanRequest(BaseModel):
    url: str


class IssueItem(BaseModel):
    rule_id: str
    wcag: str
    level: str
    impact: str
    principle: str
    element: str
    html_snippet: str
    description: str
    title: str


class ScanResult(BaseModel):
    url: str
    title: str
    score: float
    total_checks: int
    passes: int
    violations: int
    by_impact: dict
    by_principle: dict
    issues: List[IssueItem]
    summary: str


class ScanHistoryItem(BaseModel):
    id: int
    url: str
    title: str
    score: float
    violations: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ScanDetail(ScanResult):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
