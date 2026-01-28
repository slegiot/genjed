"""Distribution Engine.

Handles publishing content to multiple channels.
"""

import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

from ..models import (
    Content, DistributionResult, DistributionReport,
    DistributionStatus, SchedulingConfig
)


@dataclass
class ChannelConfig:
    """Configuration for a distribution channel."""
    platform: str
    enabled: bool = True
    credentials: Dict = field(default_factory=dict)
    config: Dict = field(default_factory=dict)


class DistributionEngine:
    """Multi-channel distribution engine."""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize distribution engine."""
        self.config = config or {}
        self.channels: Dict[str, ChannelConfig] = self._initialize_channels()
    
    def _initialize_channels(self) -> Dict[str, ChannelConfig]:
        """Initialize channel configurations."""
        return {
            "instagram_reels": ChannelConfig(
                platform="instagram",
                enabled=True,
                config={"max_duration": 90, "aspect_ratio": "9:16"}
            ),
            "tiktok": ChannelConfig(
                platform="tiktok",
                enabled=True,
                config={"max_duration": 60, "aspect_ratio": "9:16"}
            ),
            "youtube_shorts": ChannelConfig(
                platform="youtube",
                enabled=True,
                config={"max_duration": 60, "aspect_ratio": "9:16"}
            ),
            "ctv": ChannelConfig(
                platform="ctv",
                enabled=True,
                config={"aspect_ratio": "16:9", "quality": "4k"}
            ),
            "dooh": ChannelConfig(
                platform="dooh",
                enabled=True,
                config={"aspect_ratio": "16:9|1:1", "brightness": "high"}
            ),
        }
    
    async def publish_content(
        self,
        content: Content,
        target_channels: List[str],
        scheduling: Optional[SchedulingConfig] = None
    ) -> DistributionReport:
        """Publish content to multiple channels."""
        report = DistributionReport(
            batch_id=content.batch_id,
            content_id=content.content_id
        )
        
        scheduling = scheduling or SchedulingConfig()
        
        for channel in target_channels:
            if channel not in self.channels:
                result = DistributionResult(
                    content_id=content.content_id,
                    channel=channel,
                    status=DistributionStatus.FAILED,
                    error_message=f"Channel {channel} not configured"
                )
            elif not self.channels[channel].enabled:
                result = DistributionResult(
                    content_id=content.content_id,
                    channel=channel,
                    status=DistributionStatus.FAILED,
                    error_message=f"Channel {channel} is disabled"
                )
            else:
                result = await self._publish_to_channel(content, channel, scheduling)
            
            report.add_result(result)
        
        return report
    
    async def _publish_to_channel(
        self,
        content: Content,
        channel: str,
        scheduling: SchedulingConfig
    ) -> DistributionResult:
        """Publish content to a specific channel."""
        try:
            prepared = await self._prepare_for_channel(content, channel)
            
            if scheduling.mode == "scheduled" and scheduling.scheduled_time:
                return DistributionResult(
                    content_id=content.content_id,
                    channel=channel,
                    status=DistributionStatus.SCHEDULED,
                    scheduled_publish_time=scheduling.scheduled_time
                )
            else:
                return DistributionResult(
                    content_id=content.content_id,
                    channel=channel,
                    status=DistributionStatus.SUCCESS,
                    published_url=f"https://{channel}.com/post/test",
                    published_id=f"test_{int(time.time())}"
                )
        except Exception as e:
            return DistributionResult(
                content_id=content.content_id,
                channel=channel,
                status=DistributionStatus.FAILED,
                error_message=str(e)
            )
    
    async def _prepare_for_channel(self, content: Content, channel: str) -> Dict:
        """Prepare content for specific channel requirements."""
        return {
            "video_url": content.video_url,
            "aspect_ratio": content.aspect_ratio,
            "duration": content.duration_seconds
        }
    
    def list_available_channels(self) -> List[str]:
        """List all configured channels."""
        return [ch for ch, config in self.channels.items() if config.enabled]
