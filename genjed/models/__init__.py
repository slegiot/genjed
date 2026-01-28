"""Genjed Data Models Package.

Contains all data models and schemas for the content creation workflow.
"""

from .batch import Batch, BatchStatus, GenerationConfig, SchedulingMode
from .product import Product, ProductCategory, AssetBundle, BrandGuidelines
from .template import Template, TemplateType, VisualConfig, AudioConfig, TextOverlay
from .content import Content, ContentStatus, QAReport, QAAction
from .distribution import (
    DistributionChannel, DistributionStatus, DistributionResult,
    DistributionReport, SchedulingConfig
)
from .analytics import (
    PerformanceMetrics, AnalyticsReport, TopPerformer,
    Underperformer, ROIAnalysis
)

__all__ = [
    # Batch models
    "Batch",
    "BatchStatus",
    "GenerationConfig",
    "SchedulingMode",
    # Product models
    "Product",
    "ProductCategory",
    "AssetBundle",
    "BrandGuidelines",
    # Template models
    "Template",
    "TemplateType",
    "VisualConfig",
    "AudioConfig",
    "TextOverlay",
    # Content models
    "Content",
    "ContentStatus",
    "QAReport",
    "QAAction",
    # Distribution models
    "DistributionChannel",
    "DistributionStatus",
    "DistributionResult",
    "DistributionReport",
    "SchedulingConfig",
    # Analytics models
    "PerformanceMetrics",
    "AnalyticsReport",
    "TopPerformer",
    "Underperformer",
    "ROIAnalysis",
]
