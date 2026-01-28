"""Distribution Data Models.

Defines distribution channels and publishing states.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
import uuid
import time


class DistributionStatus(str, Enum):
    """Distribution status enumeration."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SCHEDULED = "SCHEDULED"


class PlatformType(str, Enum):
    """Platform type enumeration."""
    INSTAGRAM_REELS = "instagram_reels"
    TIKTOK = "tiktok"
    YOUTUBE_SHORTS = "youtube_shorts"
    CTV = "ctv"
    DOOH = "dooh"
    ECOMMERCE = "ecommerce"


@dataclass
class DistributionChannel:
    """Distribution channel configuration."""
    platform: PlatformType
    enabled: bool = True
    credentials: Dict = field(default_factory=dict)
    config: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "platform": self.platform.value if isinstance(self.platform, PlatformType) else self.platform,
            "enabled": self.enabled,
            "credentials": self.credentials,
            "config": self.config
        }


@dataclass
class DistributionResult:
    """Result of content distribution to a channel."""
    content_id: str
    channel: str
    status: DistributionStatus
    published_url: Optional[str] = None
    published_id: Optional[str] = None
    error_message: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    scheduled_publish_time: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "content_id": self.content_id,
            "channel": self.channel,
            "status": self.status.value if isinstance(self.status, DistributionStatus) else self.status,
            "published_url": self.published_url,
            "published_id": self.published_id,
            "error_message": self.error_message,
            "timestamp": self.timestamp,
            "scheduled_publish_time": self.scheduled_publish_time
        }


@dataclass
class DistributionReport:
    """Overall distribution report for a batch."""
    batch_id: str
    content_id: str
    channels_attempted: int = 0
    channels_succeeded: int = 0
    channels_failed: int = 0
    distribution_details: List[DistributionResult] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict:
        return {
            "batch_id": self.batch_id,
            "content_id": self.content_id,
            "channels_attempted": self.channels_attempted,
            "channels_succeeded": self.channels_succeeded,
            "channels_failed": self.channels_failed,
            "distribution_details": [d.to_dict() for d in self.distribution_details],
            "timestamp": self.timestamp
        }
    
    def add_result(self, result: DistributionResult) -> None:
        """Add a distribution result and update counters."""
        self.distribution_details.append(result)
        self.channels_attempted += 1
        if result.status == DistributionStatus.SUCCESS:
            self.channels_succeeded += 1
        else:
            self.channels_failed += 1


@dataclass
class SchedulingConfig:
    """Content scheduling configuration."""
    mode: str = "immediate"
    scheduled_time: Optional[str] = None
    conditions: Dict = field(default_factory=dict)
    timezone: str = "UTC"
    
    def to_dict(self) -> Dict:
        return {
            "mode": self.mode,
            "scheduled_time": self.scheduled_time,
            "conditions": self.conditions,
            "timezone": self.timezone
        }
