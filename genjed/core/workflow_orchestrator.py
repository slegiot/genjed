"""Workflow Orchestrator.

Main orchestrator for the Genjed.ai content creation workflow.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from ..models import (
    Batch, BatchStatus, AssetBundle, Template,
    Content, GenerationConfig, SchedulingConfig
)
from ..services import (
    ReplicateClient, ContentGenerator, QAEngine,
    DistributionEngine, AnalyticsEngine
)


@dataclass
class WorkflowResult:
    """Result of workflow execution."""
    batch_id: str
    success: bool
    contents_generated: int
    contents_qa_passed: int
    contents_distributed: int
    errors: List[str]


class WorkflowOrchestrator:
    """Main workflow orchestrator for Genjed.ai."""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize workflow orchestrator."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize services
        self.replicate_client = ReplicateClient()
        self.content_generator = ContentGenerator(self.replicate_client)
        self.qa_engine = QAEngine()
        self.distribution_engine = DistributionEngine()
        self.analytics_engine = AnalyticsEngine()
    
    async def execute_workflow(
        self,
        asset_bundle: AssetBundle,
        template: Template,
        generation_config: Optional[GenerationConfig] = None
    ) -> WorkflowResult:
        """Execute the complete content creation workflow."""
        self.logger.info(f"Starting workflow for campaign: {asset_bundle.campaign_id}")
        
        generation_config = generation_config or GenerationConfig()
        batch = Batch(
            customer_id=asset_bundle.customer_id,
            campaign_id=asset_bundle.campaign_id,
            asset_bundle=asset_bundle,
            template=template,
            generation_config=generation_config
        )
        
        errors = []
        contents_generated = 0
        contents_qa_passed = 0
        contents_distributed = 0
        
        try:
            self.logger.info("Step 1: Generating content...")
            batch.update_status(BatchStatus.GENERATION_IN_PROGRESS)
            
            generated_contents = await self._generate_content(batch)
            contents_generated = len(generated_contents)
            
            self.logger.info("Step 2: Running QA checks...")
            batch.update_status(BatchStatus.QA_IN_PROGRESS)
            
            qa_passed_contents = await self._run_qa_checks(generated_contents, batch)
            contents_qa_passed = len(qa_passed_contents)
            
            self.logger.info("Step 3: Distributing content...")
            batch.update_status(BatchStatus.DISTRIBUTION_IN_PROGRESS)
            
            distributed_contents = await self._distribute_content(qa_passed_contents, batch)
            contents_distributed = len(distributed_contents)
            
            batch.update_status(BatchStatus.COMPLETED)
            self.logger.info(f"Workflow completed successfully")
            
        except Exception as e:
            self.logger.error(f"Workflow failed: {str(e)}")
            batch.update_status(BatchStatus.FAILED)
            batch.error_message = str(e)
            errors.append(str(e))
        
        return WorkflowResult(
            batch_id=batch.batch_id,
            success=batch.status == BatchStatus.COMPLETED,
            contents_generated=contents_generated,
            contents_qa_passed=contents_qa_passed,
            contents_distributed=contents_distributed,
            errors=errors
        )
    
    async def _generate_content(self, batch: Batch) -> List[Content]:
        """Generate content for all products in batch."""
        contents = []
        
        num_products = len(batch.asset_bundle.products)
        num_aspect_ratios = len(batch.template.visual_config.aspect_ratios)
        num_durations = len(batch.template.visual_config.duration_seconds)
        batch.total_items = num_products * num_aspect_ratios * num_durations
        
        for product in batch.asset_bundle.products:
            for aspect_ratio in batch.template.visual_config.aspect_ratios:
                for duration in batch.template.visual_config.duration_seconds:
                    result = await self.content_generator.generate_for_product(
                        product=product,
                        template=batch.template,
                        aspect_ratio=aspect_ratio,
                        duration=duration
                    )
                    result.content.batch_id = batch.batch_id
                    contents.append(result.content)
                    batch.increment_processed(success=result.success)
        
        return contents
    
    async def _run_qa_checks(self, contents: List[Content], batch: Batch) -> List[Content]:
        """Run QA checks on generated content."""
        passed_contents = []
        target_channels = batch.generation_config.target_channels
        
        for content in contents:
            target_platform = target_channels[0] if target_channels else "instagram_reels"
            report = await self.qa_engine.run_qa_checks(content, target_platform)
            
            if report.recommended_action.value == "APPROVE":
                passed_contents.append(content)
        
        batch.processed_items = len(contents)
        return passed_contents
    
    async def _distribute_content(self, contents: List[Content], batch: Batch) -> List[Content]:
        """Distribute approved content to target channels."""
        distributed_contents = []
        scheduling = SchedulingConfig(mode=batch.generation_config.scheduling_mode.value)
        target_channels = batch.generation_config.target_channels
        
        for content in contents:
            report = await self.distribution_engine.publish_content(
                content=content,
                target_channels=target_channels,
                scheduling=scheduling
            )
            
            if report.channels_succeeded > 0:
                distributed_contents.append(content)
        
        return distributed_contents
