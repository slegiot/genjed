"""Content Generator Service.

Generates video/image content using AI models via Replicate.
"""

import logging
from typing import Dict, Optional
from dataclasses import dataclass

from ..models import Content, ContentStatus, Product, Template


@dataclass
class GenerationResult:
    """Result of content generation."""
    success: bool
    content: Content
    error_message: Optional[str] = None


class ContentGenerator:
    """Service for generating content using AI models."""
    
    def __init__(self, replicate_client, config: Optional[Dict] = None):
        """Initialize content generator.
        
        Args:
            replicate_client: ReplicateClient instance for API calls
            config: Optional configuration dictionary
        """
        self.replicate_client = replicate_client
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
    
    async def generate_for_product(
        self,
        product: Product,
        template: Template,
        aspect_ratio: str = "9:16",
        duration: int = 15
    ) -> GenerationResult:
        """Generate content for a product using the specified template.
        
        Args:
            product: Product to create content for
            template: Template defining the content format
            aspect_ratio: Video aspect ratio (e.g., "9:16", "16:9")
            duration: Duration in seconds
            
        Returns:
            GenerationResult with success status and content
        """
        self.logger.info(f"Generating content for product: {product.name}")
        
        # Create content object
        content = Content(
            batch_id="",  # Will be set by orchestrator
            product_id=product.product_id,
            template_id=template.template_id or template.name,
            aspect_ratio=aspect_ratio,
            duration_seconds=duration
        )
        content.update_status(ContentStatus.GENERATING)
        
        try:
            # Build prompt from template and product
            prompt = self._build_prompt(product, template)
            
            # Generate video using Replicate
            result = await self.replicate_client.generate_video(
                prompt=prompt,
                aspect_ratio=aspect_ratio,
                duration=duration
            )
            
            if result.status == "success" and result.output:
                content.video_url = result.output
                content.update_status(ContentStatus.GENERATED)
                content.metadata["processing_time"] = result.processing_time
                content.metadata["model_used"] = result.model_used
                content.metadata["resolution"] = "1080p"  # Default
                
                self.logger.info(f"Content generated successfully: {content.content_id}")
                
                return GenerationResult(
                    success=True,
                    content=content
                )
            else:
                error_msg = result.error or "Unknown generation error"
                content.update_status(ContentStatus.FAILED)
                content.error_message = error_msg
                
                self.logger.error(f"Content generation failed: {error_msg}")
                
                return GenerationResult(
                    success=False,
                    content=content,
                    error_message=error_msg
                )
                
        except Exception as e:
            error_msg = str(e)
            content.update_status(ContentStatus.FAILED)
            content.error_message = error_msg
            
            self.logger.error(f"Content generation exception: {error_msg}")
            
            return GenerationResult(
                success=False,
                content=content,
                error_message=error_msg
            )
    
    def _build_prompt(self, product: Product, template: Template) -> str:
        """Build generation prompt from product and template.
        
        Args:
            product: Product data
            template: Template configuration
            
        Returns:
            Prompt string for AI generation
        """
        # Get headline from template, replacing placeholders
        headline = template.text_overlay.headline_template.replace(
            "{{product_name}}", product.name
        )
        
        # Build descriptive prompt
        prompt_parts = [
            f"Professional video advertisement for {product.name}.",
            f"Product description: {product.description}.",
            f"Category: {product.category.value}.",
            f"Headline: {headline}.",
        ]
        
        if product.brand:
            prompt_parts.append(f"Brand: {product.brand}.")
        
        if template.text_overlay.cta_text:
            prompt_parts.append(f"Call to action: {template.text_overlay.cta_text}.")
        
        # Add template type context
        type_context = {
            "product_ad": "Clean, modern product showcase with dynamic camera movements.",
            "brand_story": "Emotional storytelling with brand values.",
            "testimonial": "Authentic customer testimonial style.",
            "tutorial": "Step-by-step demonstration.",
            "unboxing": "Exciting unboxing experience.",
            "comparison": "Side-by-side product comparison.",
            "lifestyle": "Lifestyle context showing product in use."
        }
        
        template_type = template.type.value if hasattr(template.type, 'value') else str(template.type)
        if template_type in type_context:
            prompt_parts.append(type_context[template_type])
        
        return " ".join(prompt_parts)
