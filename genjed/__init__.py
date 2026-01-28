"""Genjed.ai Content Creation Engine.

A comprehensive workflow engine for generating AI-powered video content.
"""

__version__ = "1.0.0"
__author__ = "Genjed.ai"

from .config import get_config
from .core import WorkflowOrchestrator

__all__ = ["get_config", "WorkflowOrchestrator"]
