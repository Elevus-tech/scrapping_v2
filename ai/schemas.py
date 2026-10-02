from dataclasses import dataclass
from typing import Optional


@dataclass
class SearchField:
    selector: str
    confidence: float
    reason: str = ""


@dataclass
class AIResponse:
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None