"""Analytics Data Models.

Defines performance metrics and analytics reporting.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
import uuid
import time


class MetricType(str, Enum):
    """Performance metric type enumeration."""
    VIEWS = "views"
    IMPRESSIONS = "impressions"
    CLICKS = "clicks"
    CTR = "ctr"
    WATCH_TIME = "watch_time"
    ENGAGEMENT_RATE = "engagement_rate"
    SHARES = "shares"
    CONVERSIONS = "conversions"
    REVENUE = "revenue"


@dataclass
class PerformanceMetrics:
    """Performance metrics for content."""
    content_id: str
    channel: str
    views: int = 0
    impressions: int = 0
    clicks: int = 0
    ctr: float = 0.0
    watch_time_seconds: int = 0
    engagement_rate: float = 0.0
    shares: int = 0
    conversions: int = 0
    revenue: float = 0.0
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict:
        return {
            "content_id": self.content_id,
            "channel": self.channel,
            "views": self.views,
            "impressions": self.impressions,
            "clicks": self.clicks,
            "ctr": self.ctr,
            "watch_time_seconds": self.watch_time_seconds,
            "engagement_rate": self.engagement_rate,
            "shares": self.shares,
            "conversions": self.conversions,
            "revenue": self.revenue,
            "timestamp": self.timestamp
        }
    
    def calculate_ctr(self) -> float:
        """Calculate click-through rate."""
        if self.impressions == 0:
            return 0.0
        return (self.clicks / self.impressions) * 100
    
    def calculate_roas(self, spend: float = 0.0) -> float:
        """Calculate return on ad spend."""
        if spend == 0:
            return 0.0
        return self.revenue / spend


@dataclass
class TopPerformer:
    """Top performing item for analytics."""
    item_id: str
    name: str
    metric_value: float
    metric_type: str
    percentage: float


@dataclass
class Underperformer:
    """Underperforming item for analytics."""
    item_id: str
    name: str
    metric_value: float
    metric_type: str
    issues: List[str]


@dataclass
class ROIAnalysis:
    """Return on investment analysis."""
    total_spend: float = 0.0
    total_revenue: float = 0.0
    roas: float = 0.0
    average_order_value: float = 0.0
    cost_per_conversion: float = 0.0


@dataclass
class AnalyticsReport:
    """Analytics report for a batch."""
    batch_id: str
    period_days: int = 7
    top_performers_by_product: List[TopPerformer] = field(default_factory=list)
    top_performers_by_format: List[TopPerformer] = field(default_factory=list)
    top_performers_by_channel: List[TopPerformer] = field(default_factory=list)
    underperformers: List[Underperformer] = field(default_factory=list)
    roi_analysis: ROIAnalysis = field(default_factory=ROIAnalysis)
    recommendations: List[str] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    generated_at: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict:
        return {
            "batch_id": self.batch_id,
            "period_days": self.period_days,
            "top_performers_by_product": [
                {"item_id": p.item_id, "name": p.name, "metric_value": p.metric_value,
                 "metric_type": p.metric_type, "percentage": p.percentage}
                for p in self.top_performers_by_product
            ],
            "top_performers_by_format": [
                {"item_id": p.item_id, "name": p.name, "metric_value": p.metric_value,
                 "metric_type": p.metric_type, "percentage": p.percentage}
                for p in self.top_performers_by_format
            ],
            "top_performers_by_channel": [
                {"item_id": p.item_id, "name": p.name, "metric_value": p.metric_value,
                 "metric_type": p.metric_type, "percentage": p.percentage}
                for p in self.top_performers_by_channel
            ],
            "underperformers": [
                {"item_id": u.item_id, "name": u.name, "metric_value": u.metric_value,
                 "metric_type": u.metric_type, "issues": u.issues}
                for u in self.underperformers
            ],
            "roi_analysis": {
                "total_spend": self.roi_analysis.total_spend,
                "total_revenue": self.roi_analysis.total_revenue,
                "roas": self.roi_analysis.roas,
                "average_order_value": self.roi_analysis.average_order_value,
                "cost_per_conversion": self.roi_analysis.cost_per_conversion
            },
            "recommendations": self.recommendations,
            "insights": self.insights,
            "generated_at": self.generated_at
        }
