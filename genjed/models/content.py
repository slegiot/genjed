"""Content Data Models.

Defines generated content and QA states.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
import uuid
import time


class ContentStatus(str, Enum):
    """Content generation status enumeration."""
    PENDING = "PENDING"
    GENERATING = "GENERATING"
    GENERATED = "GENERATED"
    GENERATED_RETRY = "GENERATED_RETRY"
    QA_IN_PROGRESS = "QA_IN_PROGRESS"
    QA_PASSED = "QA_PASSED"
    QA_FAILED = "QA_FAILED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DISTRIBUTED = "DISTRIBUTED"
    FAILED = "FAILED"


class QAAction(str, Enum):
    """QA action enumeration."""
    APPROVE = "APPROVE"
    REVISE = "REVISE"
    REJECT = "REJECT"


@dataclass
class QACheck:
    """Individual QA check result."""
    check_name: str
    passed: bool
    severity: str = "MEDIUM"
    issues: List[str] = field(default_factory=list)
    score_contribution: float = 0.0


@dataclass
class QAReport:
    """Quality assurance report for content."""
    content_id: str
    checks_passed: List[str] = field(default_factory=list)
    checks_flagged: List[Dict] = field(default_factory=list)
    qa_score: float = 0.0
    requires_human_review: bool = False
    recommended_action: QAAction = QAAction.REVISE
    reviewer_notes: Optional[str] = None
    reviewed_at: Optional[float] = None
    reviewed_by: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "content_id": self.content_id,
            "checks_passed": self.checks_passed,
            "checks_flagged": self.checks_flagged,
            "qa_score": self.qa_score,
            "requires_human_review": self.requires_human_review,
            "recommended_action": self.recommended_action.value if isinstance(self.recommended_action, QAAction) else self.recommended_action,
            "reviewer_notes": self.reviewer_notes,
            "reviewed_at": self.reviewed_at,
            "reviewed_by": self.reviewed_by
        }


@dataclass
class Content:
    """Generated content model."""
    batch_id: str
    product_id: str
    template_id: str
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    aspect_ratio: str = "9:16"
    duration_seconds: int = 15
    content_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: ContentStatus = ContentStatus.PENDING
    qa_report: Optional[QAReport] = None
    metadata: Dict = field(default_factory=dict)
    error_message: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict:
        return {
            "content_id": self.content_id,
            "batch_id": self.batch_id,
            "product_id": self.product_id,
            "template_id": self.template_id,
            "status": self.status.value if isinstance(self.status, ContentStatus) else self.status,
            "video_url": self.video_url,
            "thumbnail_url": self.thumbnail_url,
            "aspect_ratio": self.aspect_ratio,
            "duration_seconds": self.duration_seconds,
            "qa_report": self.qa_report.to_dict() if self.qa_report else None,
            "metadata": self.metadata,
            "error_message": self.error_message,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def update_status(self, status: ContentStatus) -> None:
        """Update content status and timestamp."""
        self.status = status
        self.updated_at = time.time()
    
    def add_qa_flag(self, flag: str, severity: str = "MEDIUM") -> None:
        """Add a QA flag to the content."""
        if self.qa_report is None:
            self.qa_report = QAReport(content_id=self.content_id)
        if 'qa_flags' not in self.metadata:
            self.metadata['qa_flags'] = []
        self.metadata['qa_flags'].append({"flag": flag, "severity": severity})
