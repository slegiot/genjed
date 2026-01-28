"""Replicate API Client.

Handles communication with Replicate AI models for video, image, and audio generation.
"""

import os
import time
import asyncio
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

try:
    import replicate
    REPLICATE_AVAILABLE = True
except ImportError:
    REPLICATE_AVAILABLE = False


class ModelType(str, Enum):
    """Replicate model type enumeration."""
    VIDEO_GENERATION = "video_generation"
    IMAGE_TO_VIDEO = "image_to_video"
    TTS = "tts"
    IMAGE_UPSCALE = "image_upscale"
    BACKGROUND_REMOVAL = "background_removal"


@dataclass
class APIResult:
    """Result from Replicate API call."""
    status: str
    output: Optional[Any] = None
    error: Optional[str] = None
    processing_time: float = 0.0
    model_used: Optional[str] = None


class ReplicateClient:
    """Client for interacting with Replicate API."""
    
    def __init__(self, api_key: Optional[str] = None, max_retries: int = 3, retry_delay: float = 2.0):
        """Initialize Replicate client."""
        self.api_key = api_key or os.getenv("REPLICATE_API_KEY")
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._client = None
        
        if self.api_key and REPLICATE_AVAILABLE:
            self._client = replicate.Client(api_token=self.api_key)
    
    def _ensure_client(self) -> None:
        """Ensure client is initialized."""
        if not self._client:
            if not REPLICATE_AVAILABLE:
                raise RuntimeError("Replicate SDK not installed. Install with: pip install replicate")
            if not self.api_key:
                raise ValueError("Replicate API key not configured.")
            self._client = replicate.Client(api_token=self.api_key)
    
    def _get_model_id(self, model_type: ModelType) -> str:
        """Get model ID for a given model type."""
        model_map = {
            ModelType.VIDEO_GENERATION: "runwayml/gen-3-lite:b09e6e42b92a6dfe3f134e37341f93eafdd62e76",
            ModelType.IMAGE_TO_VIDEO: "stability-ai/stable-video-diffusion",
            ModelType.TTS: "coqui/xtts-v2:ff8b6f76baf30e0e0f51fd5d9d5b6bcbe63f4eca80fa97b4e68b0e4d7f0d3e5f",
            ModelType.IMAGE_UPSCALE: "stability-ai/real-esrgan",
            ModelType.BACKGROUND_REMOVAL: "zsxkzsx/transparent-background",
        }
        return model_map.get(model_type, "")
    
    async def generate_video(
        self,
        prompt: str,
        aspect_ratio: str = "9:16",
        duration: int = 15,
        **kwargs
    ) -> APIResult:
        """Generate video from text prompt."""
        self._ensure_client()
        
        aspect_ratio_map = {
            "9:16": {"width": 540, "height": 960},
            "16:9": {"width": 1280, "height": 720},
            "1:1": {"width": 1080, "height": 1080},
        }
        dimensions = aspect_ratio_map.get(aspect_ratio, {"width": 1280, "height": 720})
        
        input_params = {
            "prompt": prompt,
            "width": dimensions["width"],
            "height": dimensions["height"],
            "duration": duration,
            "num_inference_steps": kwargs.get("num_inference_steps", 20),
            "guidance_scale": kwargs.get("guidance_scale", 7.5),
            "seed": kwargs.get("seed"),
        }
        
        return await self._execute_with_retry(
            model_type=ModelType.VIDEO_GENERATION,
            input_params=input_params
        )
    
    async def generate_tts(
        self,
        text: str,
        language: str = "en",
        speaker_gender: str = "neutral",
        **kwargs
    ) -> APIResult:
        """Generate text-to-speech audio."""
        self._ensure_client()
        
        gender_map = {"male": "male", "female": "female", "neutral": "neutral"}
        
        input_params = {
            "text": text,
            "language": language,
            "speaker_name": gender_map.get(speaker_gender, "neutral"),
        }
        
        return await self._execute_with_retry(
            model_type=ModelType.TTS,
            input_params=input_params
        )
    
    async def _execute_with_retry(
        self,
        model_type: ModelType,
        input_params: Dict[str, Any]
    ) -> APIResult:
        """Execute Replicate API call with retry logic."""
        model_id = self._get_model_id(model_type)
        start_time = time.time()
        
        for attempt in range(self.max_retries):
            try:
                output = self._client.run(model_id, input=input_params)
                
                processing_time = time.time() - start_time
                
                if output and isinstance(output, list) and len(output) > 0:
                    return APIResult(
                        status="success",
                        output=output[0],
                        processing_time=processing_time,
                        model_used=model_id
                    )
                elif output:
                    return APIResult(
                        status="success",
                        output=output,
                        processing_time=processing_time,
                        model_used=model_id
                    )
                else:
                    raise Exception("No output from Replicate API")
                    
            except Exception as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    continue
                else:
                    return APIResult(
                        status="failed",
                        error=str(e),
                        processing_time=time.time() - start_time,
                        model_used=model_id
                    )
        
        return APIResult(status="failed", error="Max retries exceeded")
    
    def is_configured(self) -> bool:
        """Check if Replicate client is properly configured."""
        return self.api_key is not None and REPLICATE_AVAILABLE
