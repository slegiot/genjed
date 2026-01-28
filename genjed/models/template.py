"""Template Data Models.

Defines template structures for content generation.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class TemplateType(str, Enum):
    """Template type enumeration."""
    PRODUCT_AD = "product_ad"
    BRAND_STORY = "brand_story"
    TESTIMONIAL = "testimonial"
    TUTORIAL = "tutorial"
    UNBOXING = "unboxing"
    COMPARISON = "comparison"
    LIFESTYLE = "lifestyle"


@dataclass
class VisualConfig:
    """Visual configuration for templates."""
    aspect_ratios: List[str] = field(default_factory=lambda: ["9:16"])
    duration_seconds: List[int] = field(default_factory=lambda: [15])
    resolution: str = "1080p"
    frame_rate: int = 30
    transitions: List[str] = field(default_factory=list)
    effects: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "aspect_ratios": self.aspect_ratios,
            "duration_seconds": self.duration_seconds,
            "resolution": self.resolution,
            "frame_rate": self.frame_rate,
            "transitions": self.transitions,
            "effects": self.effects
        }


@dataclass
class AudioConfig:
    """Audio configuration for templates."""
    voiceover_enabled: bool = False
    music_enabled: bool = True
    music_genre: Optional[str] = None
    voiceover_gender: str = "neutral"
    volume_levels: Dict[str, float] = field(default_factory=lambda: {
        "music": 0.6,
        "voiceover": 0.9,
        "sfx": 0.4
    })
    
    def to_dict(self) -> Dict:
        return {
            "voiceover_enabled": self.voiceover_enabled,
            "music_enabled": self.music_enabled,
            "music_genre": self.music_genre,
            "voiceover_gender": self.voiceover_gender,
            "volume_levels": self.volume_levels
        }


@dataclass
class TextOverlay:
    """Text overlay configuration for templates."""
    headline_template: str = "{{product_name}}"
    subheadline_template: Optional[str] = None
    cta_text: str = "Shop Now!"
    text_position: str = "bottom"
    font_family: Optional[str] = None
    font_size: int = 24
    text_color: str = "#FFFFFF"
    background_color: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "headline_template": self.headline_template,
            "subheadline_template": self.subheadline_template,
            "cta_text": self.cta_text,
            "text_position": self.text_position,
            "font_family": self.font_family,
            "font_size": self.font_size,
            "text_color": self.text_color,
            "background_color": self.background_color
        }


@dataclass
class Template:
    """Template model for content generation."""
    name: str
    type: TemplateType
    visual_config: VisualConfig = field(default_factory=VisualConfig)
    audio_config: AudioConfig = field(default_factory=AudioConfig)
    text_overlay: TextOverlay = field(default_factory=TextOverlay)
    template_id: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "template_id": self.template_id,
            "name": self.name,
            "type": self.type.value if isinstance(self.type, TemplateType) else self.type,
            "visual_config": self.visual_config.to_dict(),
            "audio_config": self.audio_config.to_dict(),
            "text_overlay": self.text_overlay.to_dict(),
            "description": self.description,
            "tags": self.tags
        }
