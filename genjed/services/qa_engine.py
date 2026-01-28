"""Quality Assurance Engine.

Validates generated content against brand, technical, and content requirements.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

from ..models import Content, QAReport, QAAction, ContentStatus


@dataclass
class QACheckResult:
    """Result of a single QA check."""
    check_name: str
    passed: bool
    severity: str = "MEDIUM"
    issues: List[str] = field(default_factory=list)
    score_contribution: float = 0.0


class QAEngine:
    """Quality assurance engine for validating generated content."""
    
    def __init__(
        self,
        auto_approve_threshold: float = 95.0,
        human_review_threshold: float = 80.0,
        config: Optional[Dict] = None
    ):
        """Initialize QA engine."""
        self.auto_approve_threshold = auto_approve_threshold
        self.human_review_threshold = human_review_threshold
        self.config = config or self._default_config()
    
    def _default_config(self) -> Dict:
        """Get default QA configuration."""
        return {
            "brand_compliance": {
                "color_match_threshold": 0.85,
                "logo_visibility_required": True,
                "font_consistency_required": True
            },
            "technical": {
                "min_resolution": "1080p",
                "valid_codecs": ["h264", "h265"],
                "duration_tolerance": 1
            },
            "content": {
                "typo_check": True,
                "product_info_check": True,
                "cta_visibility_check": True
            },
            "platform_specific": {
                "instagram_reels": {"max_duration": 90, "aspect_ratio": "9:16"},
                "tiktok": {"max_duration": 60, "aspect_ratio": "9:16"},
                "youtube_shorts": {"max_duration": 60, "aspect_ratio": "9:16"},
                "ctv": {"aspect_ratio": "16:9", "quality": "4k"},
                "dooh": {"aspect_ratio": "16:9|1:1", "brightness": "high"}
            }
        }
    
    async def run_qa_checks(
        self,
        content: Content,
        target_platform: str
    ) -> QAReport:
        """Run all QA checks on content for a target platform."""
        report = QAReport(content_id=content.content_id)
        
        checks = [
            await self._validate_technical_specs(content, target_platform),
            await self._validate_brand_compliance(content),
            await self._validate_content_accuracy(content),
            await self._validate_platform_requirements(content, target_platform),
        ]
        
        for check in checks:
            if check.passed:
                report.checks_passed.append(check.check_name)
                report.qa_score += check.score_contribution
            else:
                report.checks_flagged.append({
                    "check": check.check_name,
                    "severity": check.severity,
                    "issues": check.issues
                })
        
        report.requires_human_review = (
            len(report.checks_flagged) > 0 or
            report.qa_score < self.auto_approve_threshold
        )
        
        if report.qa_score >= self.auto_approve_threshold and not report.checks_flagged:
            report.recommended_action = QAAction.APPROVE
        elif report.qa_score >= self.human_review_threshold:
            report.recommended_action = QAAction.APPROVE
        else:
            report.recommended_action = QAAction.REVISE
        
        if report.recommended_action == QAAction.APPROVE:
            content.update_status(ContentStatus.QA_PASSED)
        else:
            content.update_status(ContentStatus.QA_FAILED)
        
        content.qa_report = report
        return report
    
    async def _validate_technical_specs(
        self,
        content: Content,
        target_platform: str
    ) -> QACheckResult:
        """Validate technical specifications."""
        issues = []
        passed = True
        
        min_res = self.config["technical"]["min_resolution"]
        if "1080" not in content.metadata.get("resolution", ""):
            issues.append(f"Resolution below {min_res} threshold")
            passed = False
        
        max_duration = self.config["platform_specific"].get(target_platform, {}).get("max_duration", 90)
        if content.duration_seconds > max_duration:
            issues.append(f"Duration {content.duration_seconds}s exceeds {max_duration}s limit")
            passed = False
        
        return QACheckResult(
            check_name="TECHNICAL_SPECS",
            passed=passed,
            severity="HIGH" if not passed else "LOW",
            issues=issues,
            score_contribution=25.0 if passed else 0.0
        )
    
    async def _validate_brand_compliance(self, content: Content) -> QACheckResult:
        """Validate brand compliance."""
        issues = []
        passed = True
        
        color_match = content.metadata.get("color_match_score", 1.0)
        if color_match < self.config["brand_compliance"]["color_match_threshold"]:
            issues.append(f"Color match score {color_match:.2f} below threshold")
            passed = False
        
        if self.config["brand_compliance"]["logo_visibility_required"]:
            if not content.metadata.get("logo_visible", True):
                issues.append("Logo not visible in content")
                passed = False
        
        return QACheckResult(
            check_name="BRAND_COMPLIANCE",
            passed=passed,
            severity="MEDIUM" if not passed else "LOW",
            issues=issues,
            score_contribution=25.0 if passed else 0.0
        )
    
    async def _validate_content_accuracy(self, content: Content) -> QACheckResult:
        """Validate content accuracy."""
        issues = []
        passed = True
        
        if self.config["content"]["typo_check"]:
            if content.metadata.get("typos_detected", 0) > 0:
                issues.append(f"Typos detected: {content.metadata['typos_detected']}")
                passed = False
        
        if self.config["content"]["product_info_check"]:
            if not content.metadata.get("product_info_verified", True):
                issues.append("Product information not verified")
                passed = False
        
        if self.config["content"]["cta_visibility_check"]:
            if not content.metadata.get("cta_visible", True):
                issues.append("Call-to-action not visible")
                passed = False
        
        return QACheckResult(
            check_name="CONTENT_ACCURACY",
            passed=passed,
            severity="HIGH" if not passed else "LOW",
            issues=issues,
            score_contribution=25.0 if passed else 0.0
        )
    
    async def _validate_platform_requirements(
        self,
        content: Content,
        target_platform: str
    ) -> QACheckResult:
        """Validate platform-specific requirements."""
        issues = []
        passed = True
        
        platform_config = self.config["platform_specific"].get(target_platform, {})
        
        if platform_config:
            required_ratio = platform_config.get("aspect_ratio", "")
            if required_ratio and content.aspect_ratio not in required_ratio:
                issues.append(f"Aspect ratio {content.aspect_ratio} doesn't match {required_ratio}")
                passed = False
        
        return QACheckResult(
            check_name="PLATFORM_REQUIREMENTS",
            passed=passed,
            severity="MEDIUM" if not passed else "LOW",
            issues=issues,
            score_contribution=25.0 if passed else 0.0
        )
    
    async def process_batch(
        self,
        contents: List[Content],
        target_platform: str
    ) -> List[QAReport]:
        """Process QA for a batch of content."""
        reports = []
        for content in contents:
            report = await self.run_qa_checks(content, target_platform)
            reports.append(report)
        return reports
