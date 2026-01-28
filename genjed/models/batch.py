"""Batch Processing Data Models.

Defines batch processing states and configurations.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
import uuid
import time


class BatchStatus(str, Enum):
    """Batch processing status enumeration."""
    PENDING = "PENDING"
    INGESTION_COMPLETE = "INGESTION_COMPLETE"
    GENERATION_IN_PROGRESS = "GENERATION_IN_PROGRESS"
    GENERATION_COMPLETE = "GENERATION_COMPLETE"
    QA_IN_PROGRESS = "QA_IN_PROGRESS"
    QA_COMPLETE = "QA_COMPLETE"
    DISTRIBUTION_IN_PROGRESS = "DISTRIBUTION_IN_PROGRESS"
    DISTRIBUTION_COMPLETE = "DISTRIBUTION_COMPLETE"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class SchedulingMode(str, Enum):
    """Scheduling mode enumeration."""
    IMMEDIATE = "immediate"
    SCHEDULED = "scheduled"
    CONDITIONAL = "conditional"


@dataclass
class GenerationConfig:
    """Generation configuration for batch processing."""
    batch_size: int = 10
    target_channels: List[str] = field(default_factory=lambda: [
        "instagram_reels", "tiktok", "youtube_shorts"
    ])
    scheduling_mode: SchedulingMode = SchedulingMode.IMMEDIATE
    scheduled_time: Optional[str] = None
    resolution: str = "1080p"
    codec: str = "h264"
    frame_rate: int = 30
    
    def to_dict(self) -> Dict:
        return {
            "batch_size": self.batch_size,
            "target_channels": self.target_channels,
            "scheduling_mode": self.scheduling_mode.value if isinstance(self.scheduling_mode, SchedulingMode) else self.scheduling_mode,
            "scheduled_time": self.scheduled_time,
            "resolution": self.resolution,
            "codec": self.codec,
            "frame_rate": self.frame_rate
        }


@dataclass
class Batch:
    """Batch processing model.
    
    Represents a batch of content to be generated and distributed.
    
    Attributes:
        batch_id: Unique batch identifier
        customer_id: Customer identifier
        campaign_id: Campaign identifier
        status: Current batch status
        asset_bundle: Input assets and products
        template: Template to use for generation
        generation_config: Generation configuration
        created_at: Batch creation timestamp
        updated_at: Last update timestamp
        completed_at: Completion timestamp
        total_items: Total items to process
        processed_items: Number of items processed
        failed_items: Number of items that failed
    """
    customer_id: str
    campaign_id: str
    asset_bundle: 'AssetBundle'
    template: 'Template'
    generation_config: GenerationConfig = field(default_factory=GenerationConfig)
    batch_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: BatchStatus = BatchStatus.PENDING
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    total_items: int = 0
    processed_items: int = 0
    failed_items: int = 0
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "batch_id": self.batch_id,
            "customer_id": self.customer_id,
            "campaign_id": self.campaign_id,
            "status": self.status.value if isinstance(self.status, BatchStatus) else self.status,
            "asset_bundle": self.asset_bundle.to_dict(),
            "template": self.template.to_dict(),
            "generation_config": self.generation_config.to_dict(),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at,
            "total_items": self.total_items,
            "processed_items": self.processed_items,
            "failed_items": self.failed_items,
            "error_message": self.error_message
        }
    
    def update_status(self, status: BatchStatus) -> None:
        """Update batch status and timestamp."""
        self.status = status
        self.updated_at = time.time()
        if status == BatchStatus.COMPLETED:
            self.completed_at = time.time()
    
    def calculate_progress(self) -> float:
        """Calculate processing progress as percentage."""
        if self.total_items == 0:
            return 0.0
        return (self.processed_items / self.total_items) * 100
    
    def increment_processed(self, success: bool = True) -> None:
        """Increment processed items counter."""
        self.processed_items += 1
        if not success:
            self.failed_items += 1
        self.updated_at = time.time()
