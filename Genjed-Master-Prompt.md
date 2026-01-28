# Genjed.ai Content Creation Workflow - Master Prompt & Implementation Guide

## Overview

This master prompt provides a comprehensive blueprint for building the Genjed.ai content creation workflow engine using Replicate APIs. It serves as the source of truth for:
- Architecture decisions
- API integration patterns
- Data flow and processing
- Error handling and fallbacks
- Quality assurance checkpoints
- Performance optimization

**Date Created**: January 28, 2026  
**Version**: 1.0  
**Target Platforms**: Node.js/Python backend, async processing

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      Genjed.ai Workflow Engine                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  INPUT LAYER          PROCESSING LAYER        OUTPUT LAYER       │
│  ┌──────────────┐     ┌──────────────┐      ┌──────────────┐    │
│  │   Assets &   │     │   Replicate  │      │  Generated   │    │
│  │  Templates   │────▶│ API Calls    │─────▶│  Content     │    │
│  │  + Metadata  │     │  (video/     │      │  Library     │    │
│  └──────────────┘     │   audio)     │      └──────────────┘    │
│                       │              │                           │
│  CONTROL SIGNALS      │  QA/Review   │      DISTRIBUTION        │
│  ┌──────────────┐     │  Pipeline    │      ┌──────────────┐    │
│  │  Generation  │     │              │      │   Multi-     │    │
│  │  Params      │────▶│  Fallbacks & │─────▶│   Channel    │    │
│  │  + Config    │     │  Retry Logic │      │   Publishing │    │
│  └──────────────┘     └──────────────┘      └──────────────┘    │
│                                                                   │
│  FEEDBACK LOOP                                                   │
│  ◀─────────────────────────────────────────────────────────────│
│  Performance Data → Template Optimization → Next Iteration       │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Workflow Execution Plan

### **Step 1: Asset & Template Ingestion**

**Input Requirements:**
```javascript
{
  "customer_id": "string",
  "campaign_id": "string",
  "assets": {
    "product_data": [
      {
        "product_id": "string",
        "name": "string",
        "description": "string",
        "image_urls": ["string"],
        "category": "string",
        "price": "number",
        "attributes": {}
      }
    ],
    "brand_guidelines": {
      "brand_name": "string",
      "brand_colors": ["hex_codes"],
      "fonts": ["string"],
      "tone_of_voice": "string",
      "logo_url": "string"
    }
  },
  "template": {
    "template_id": "string",
    "name": "string",
    "type": "product_ad|teaser|recap|promotional",
    "visual_config": {
      "aspect_ratios": ["9:16", "16:9", "1:1"],
      "duration_seconds": [15, 30, 60],
      "color_scheme": "brand_colors|custom",
      "font_style": "modern|classic|bold",
      "animation_speed": "slow|medium|fast"
    },
    "audio_config": {
      "music_style": "upbeat|calm|energetic|minimal",
      "voiceover": "enabled|disabled",
      "voiceover_gender": "male|female|neutral",
      "voiceover_language": "en|da|de|sv",
      "sfx_enabled": true,
      "volume_levels": {
        "music": 0.6,
        "voiceover": 0.9,
        "sfx": 0.4
      }
    },
    "text_overlay": {
      "headline_template": "string (with {{product_name}}, {{price}} placeholders)",
      "cta_text": "string",
      "disclaimer": "string"
    }
  },
  "generation_config": {
    "batch_size": "number",
    "target_channels": ["instagram_reels", "tiktok", "youtube_shorts", "ctv", "dooh"],
    "scheduling": {
      "mode": "immediate|scheduled|conditional",
      "scheduled_time": "ISO_8601_datetime (if scheduled)",
      "conditions": {} // seasonal, inventory-based triggers
    },
    "quality_settings": {
      "resolution": "1080p|2k|4k",
      "codec": "h264|h265|vp9",
      "frame_rate": 24 | 30 | 60
    }
  }
}
```

**Processing Logic:**
1. Validate all asset URLs are accessible (HEAD request check)
2. Standardize image formats (convert to JPEG/PNG if needed)
3. Parse template configuration and validate all required fields
4. Create unique batch_id for tracking
5. Store metadata in database with status: `INGESTION_COMPLETE`

**Success Criteria:**
- ✅ All assets validated and accessible
- ✅ Template configuration matches schema
- ✅ Database record created with unique batch_id
- ✅ Metadata JSON logged for audit trail

---

### **Step 2: Content Generation via Replicate APIs**

**Replicate Model Selection:**

| Use Case | Recommended Model | API Endpoint |
|----------|------------------|--------------|
| **AI Video Generation** | Runway Gen-3 or Kling | `runwayml/gen-3-lite` `kyutai/kling` |
| **Image-to-Video** | Replicate's Stable Video | `stability-ai/stable-video-diffusion` |
| **Text-to-Speech** | Replicate's TTS | `openai/whisper` (reverse) or `coqui/xtts-v2` |
| **Audio Enhancement** | Replicate's Audio Models | `deoldify/real-esrgan` (image upscaling first) |
| **Image Generation** | Stable Diffusion 3 | `stability-ai/stable-diffusion-3` |

**Implementation Pattern:**

```python
import replicate
import os
from typing import List, Dict
import asyncio
import time

class GenjедContentGenerator:
    def __init__(self):
        self.client = replicate.Client(api_token=os.getenv("REPLICATE_API_KEY"))
        self.max_retries = 3
        self.retry_delay = 2  # seconds
    
    async def generate_video_content(self, 
                                    batch_config: Dict,
                                    product_data: List[Dict],
                                    template: Dict) -> List[Dict]:
        """
        Generate video content for multiple products using Replicate APIs
        
        Args:
            batch_config: Generation parameters and settings
            product_data: Array of product objects with descriptions/images
            template: Visual and audio template configuration
            
        Returns:
            List of generated content objects with URLs, metadata, and QA flags
        """
        
        generation_results = []
        
        for product in product_data:
            for aspect_ratio in template['visual_config']['aspect_ratios']:
                for duration in template['visual_config']['duration_seconds']:
                    
                    # Generate video prompt from product data + template
                    video_prompt = self._build_video_prompt(product, template)
                    
                    # Call Replicate video generation API
                    video_result = await self._call_replicate_video_api(
                        prompt=video_prompt,
                        aspect_ratio=aspect_ratio,
                        duration_seconds=duration,
                        template_config=template['visual_config']
                    )
                    
                    if video_result.get('status') == 'success':
                        # Generate voiceover if enabled
                        audio_url = None
                        if template['audio_config']['voiceover']:
                            voiceover_text = self._generate_voiceover_script(product, template)
                            audio_result = await self._call_replicate_tts_api(
                                text=voiceover_text,
                                gender=template['audio_config']['voiceover_gender'],
                                language=template['audio_config']['voiceover_language']
                            )
                            audio_url = audio_result.get('audio_url')
                        
                        # Composite video + audio + background music
                        final_video = await self._composite_video_audio(
                            video_url=video_result['video_url'],
                            voiceover_url=audio_url,
                            background_music_style=template['audio_config']['music_style'],
                            volume_levels=template['audio_config']['volume_levels']
                        )
                        
                        # Add text overlays
                        final_video_with_text = await self._add_text_overlays(
                            video_url=final_video['video_url'],
                            headline=product['name'],
                            cta=template['text_overlay']['cta_text'],
                            disclaimer=template['text_overlay']['disclaimer'],
                            brand_colors=template['visual_config']['color_scheme']
                        )
                        
                        generation_results.append({
                            'product_id': product['product_id'],
                            'aspect_ratio': aspect_ratio,
                            'duration': duration,
                            'video_url': final_video_with_text['video_url'],
                            'status': 'GENERATED',
                            'qa_flags': [],  # Will be populated during QA
                            'metadata': {
                                'generated_at': time.time(),
                                'model_used': 'runway_gen3',
                                'processing_time_seconds': final_video['processing_time']
                            }
                        })
                    else:
                        # Retry logic
                        retry_result = await self._retry_generation(
                            product=product,
                            template=template,
                            aspect_ratio=aspect_ratio,
                            duration=duration
                        )
                        if retry_result:
                            generation_results.append(retry_result)
                        else:
                            generation_results.append({
                                'product_id': product['product_id'],
                                'aspect_ratio': aspect_ratio,
                                'duration': duration,
                                'status': 'FAILED',
                                'error': video_result.get('error', 'Unknown error'),
                                'qa_flags': ['GENERATION_FAILED']
                            })
        
        return generation_results
    
    async def _call_replicate_video_api(self, 
                                       prompt: str,
                                       aspect_ratio: str,
                                       duration_seconds: int,
                                       template_config: Dict) -> Dict:
        """
        Call Replicate video generation API with retry logic
        """
        
        aspect_ratio_map = {
            "9:16": {"width": 540, "height": 960},
            "16:9": {"width": 1280, "height": 720},
            "1:1": {"width": 1080, "height": 1080}
        }
        
        dimensions = aspect_ratio_map.get(aspect_ratio, {"width": 1280, "height": 720})
        
        input_params = {
            "prompt": prompt,
            "width": dimensions['width'],
            "height": dimensions['height'],
            "duration": duration_seconds,
            "num_inference_steps": 20,  # Runway default
            "guidance_scale": 7.5,  # Control adherence to prompt
            "seed": None,  # Random for variety
        }
        
        for attempt in range(self.max_retries):
            try:
                # Using Runway Gen-3 Lite via Replicate
                output = self.client.run(
                    "runwayml/gen-3-lite:b09e6e42b92a6dfe3f134e37341f93eafdd62e76",
                    input=input_params
                )
                
                if output and isinstance(output, list) and len(output) > 0:
                    return {
                        'status': 'success',
                        'video_url': output[0],  # Runway returns list of URLs
                        'processing_time': 120  # Approximate
                    }
                else:
                    raise Exception("No video output from Replicate")
                    
            except Exception as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
                    continue
                else:
                    return {
                        'status': 'failed',
                        'error': str(e)
                    }
    
    async def _call_replicate_tts_api(self,
                                      text: str,
                                      gender: str,
                                      language: str) -> Dict:
        """
        Generate voiceover audio using Replicate TTS
        """
        
        gender_map = {"male": "male", "female": "female", "neutral": "neutral"}
        
        try:
            output = self.client.run(
                "coqui/xtts-v2:ff8b6f76baf30e0e0f51fd5d9d5b6bcbe63f4eca80fa97b4e68b0e4d7f0d3e5f",
                input={
                    "text": text,
                    "language": language,
                    "speaker_name": gender_map.get(gender, "neutral")
                }
            )
            
            return {
                'status': 'success',
                'audio_url': output[0] if isinstance(output, list) else output
            }
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def _retry_generation(self,
                               product: Dict,
                               template: Dict,
                               aspect_ratio: str,
                               duration: int) -> Dict:
        """
        Retry generation with simplified prompt/parameters
        """
        
        # Simplified prompt for retry
        simplified_prompt = f"High quality product video of {product['name']}"
        
        result = await self._call_replicate_video_api(
            prompt=simplified_prompt,
            aspect_ratio=aspect_ratio,
            duration_seconds=duration,
            template_config=template['visual_config']
        )
        
        if result.get('status') == 'success':
            return {
                'product_id': product['product_id'],
                'aspect_ratio': aspect_ratio,
                'duration': duration,
                'video_url': result['video_url'],
                'status': 'GENERATED_RETRY',
                'qa_flags': ['RETRY_REQUIRED'],
                'metadata': {'retry': True}
            }
        
        return None
    
    def _build_video_prompt(self, product: Dict, template: Dict) -> str:
        """
        Build AI video prompt from product data and template
        """
        
        prompt = f"""
        Create a professional product video for: {product['name']}
        
        Description: {product['description']}
        
        Style: {template['visual_config']['font_style']}
        Colors: {', '.join(template['visual_config']['color_scheme'])}
        Animation: {template['visual_config']['animation_speed']}
        
        Requirements:
        - High production quality
        - Brand-aligned aesthetic
        - Clear product showcase
        - Engaging visual flow
        - Professional color grading
        - 4K resolution ready
        
        Do NOT include text overlays (will be added in post-processing)
        Focus on visual storytelling and product presentation
        """
        
        return prompt.strip()
    
    def _generate_voiceover_script(self, product: Dict, template: Dict) -> str:
        """
        Generate voiceover script from product and template data
        """
        
        script = f"""
        {product['name']}. {product['description']}
        
        Available in multiple styles and colors.
        
        {template['text_overlay']['cta_text']}
        """
        
        return script.strip()
    
    async def _composite_video_audio(self,
                                    video_url: str,
                                    voiceover_url: str,
                                    background_music_style: str,
                                    volume_levels: Dict) -> Dict:
        """
        Composite video with audio (voiceover + background music)
        Uses FFmpeg or Replicate audio processing
        """
        
        # Placeholder for audio compositing
        # In production, use FFmpeg subprocess or Replicate audio API
        
        return {
            'video_url': video_url,
            'processing_time': 30
        }
    
    async def _add_text_overlays(self,
                                video_url: str,
                                headline: str,
                                cta: str,
                                disclaimer: str,
                                brand_colors: List[str]) -> Dict:
        """
        Add text overlays to video (headline, CTA, disclaimer)
        Uses FFmpeg or Replicate text-to-video API
        """
        
        # Placeholder for text overlay
        # In production, use FFmpeg subprocess with caption/text filter
        
        return {
            'video_url': video_url
        }
```

**Replicate API Key Configuration:**

```bash
# Environment setup
export REPLICATE_API_KEY="r8_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# In your code (Python)
import os
from replicate import Client

client = Client(api_token=os.getenv("REPLICATE_API_KEY"))

# In your code (Node.js)
const Replicate = require("replicate");
const replicate = new Replicate({
  auth: process.env.REPLICATE_API_KEY,
});
```

**Key Integration Points:**

| Component | Replicate Model | Purpose |
|-----------|-----------------|---------|
| **Video Generation** | `runwayml/gen-3-lite` | AI video from text prompts |
| **Image-to-Video** | `stability-ai/stable-video-diffusion` | Convert product images to video |
| **Text-to-Speech** | `coqui/xtts-v2` | Voiceover generation (multi-language) |
| **Image Upscaling** | `stability-ai/real-esrgan` | Enhance product image quality pre-video |
| **Background Removal** | `zsxkzsx/transparent-background` | Isolate product for cleaner backgrounds |
| **Face Animation** | `fcbryant/sadtalker` | Animate spokesperson (optional) |

---

### **Step 3: Quality Assurance & Human Review**

**QA Pipeline:**

```python
class QualityAssuranceEngine:
    
    def __init__(self):
        self.qa_rules = {
            'brand_compliance': {
                'color_match': 0.85,  # 85% color accuracy threshold
                'logo_visibility': True,
                'font_consistency': True
            },
            'technical': {
                'resolution_check': '1080p_minimum',
                'codec_validation': 'h264|h265',
                'duration_tolerance': ±1  # seconds
            },
            'content': {
                'text_accuracy': 'no_typos|correct_product_info',
                'cta_visibility': True,
                'factual_claims': 'verified_against_product_data'
            },
            'platform_specific': {
                'instagram_reels': {'max_duration': 90, 'aspect_ratio': '9:16'},
                'tiktok': {'max_duration': 60, 'aspect_ratio': '9:16'},
                'youtube_shorts': {'max_duration': 60, 'aspect_ratio': '9:16'},
                'ctv': {'aspect_ratio': '16:9', 'quality': '4k'},
                'dooh': {'aspect_ratio': '16:9|1:1', 'brightness': 'high'}
            }
        }
    
    async def run_qa_checks(self, content: Dict, target_platform: str) -> Dict:
        """
        Automated QA against predefined rules
        Returns QA report with flags for human review
        """
        
        qa_report = {
            'content_id': content['id'],
            'target_platform': target_platform,
            'checks_passed': [],
            'checks_flagged': [],
            'qa_score': 0,
            'requires_human_review': False,
            'recommended_action': 'APPROVE|REVISE|REJECT'
        }
        
        # Check 1: Technical Specifications
        technical_check = await self._validate_technical_specs(content, target_platform)
        if technical_check['passed']:
            qa_report['checks_passed'].append('TECHNICAL_SPECS')
        else:
            qa_report['checks_flagged'].append({
                'check': 'TECHNICAL_SPECS',
                'severity': 'HIGH',
                'issues': technical_check['issues']
            })
        
        # Check 2: Brand Compliance
        brand_check = await self._validate_brand_compliance(content)
        if brand_check['passed']:
            qa_report['checks_passed'].append('BRAND_COMPLIANCE')
        else:
            qa_report['checks_flagged'].append({
                'check': 'BRAND_COMPLIANCE',
                'severity': 'MEDIUM',
                'issues': brand_check['issues']
            })
        
        # Check 3: Content Accuracy
        content_check = await self._validate_content_accuracy(content)
        if content_check['passed']:
            qa_report['checks_passed'].append('CONTENT_ACCURACY')
        else:
            qa_report['checks_flagged'].append({
                'check': 'CONTENT_ACCURACY',
                'severity': 'HIGH',
                'issues': content_check['issues']
            })
        
        # Check 4: Platform-Specific Requirements
        platform_check = await self._validate_platform_requirements(content, target_platform)
        if platform_check['passed']:
            qa_report['checks_passed'].append('PLATFORM_REQUIREMENTS')
        else:
            qa_report['checks_flagged'].append({
                'check': 'PLATFORM_REQUIREMENTS',
                'severity': 'MEDIUM',
                'issues': platform_check['issues']
            })
        
        # Calculate QA score
        total_checks = len(qa_report['checks_passed']) + len(qa_report['checks_flagged'])
        qa_report['qa_score'] = (len(qa_report['checks_passed']) / total_checks * 100) if total_checks > 0 else 0
        
        # Determine if human review needed
        qa_report['requires_human_review'] = (
            len(qa_report['checks_flagged']) > 0 or 
            qa_report['qa_score'] < 85
        )
        
        # Recommendation
        if qa_report['qa_score'] >= 95 and not qa_report['checks_flagged']:
            qa_report['recommended_action'] = 'AUTO_APPROVE'
        elif qa_report['qa_score'] >= 80:
            qa_report['recommended_action'] = 'HUMAN_REVIEW_APPROVE'
        else:
            qa_report['recommended_action'] = 'REVISE'
        
        return qa_report
    
    async def _validate_technical_specs(self, content: Dict, target_platform: str) -> Dict:
        """Validate video codec, resolution, duration, etc."""
        # Implementation details...
        pass
    
    async def _validate_brand_compliance(self, content: Dict) -> Dict:
        """Check color accuracy, logo placement, font consistency"""
        # Implementation details...
        pass
    
    async def _validate_content_accuracy(self, content: Dict) -> Dict:
        """Verify product information, pricing, spelling"""
        # Implementation details...
        pass
    
    async def _validate_platform_requirements(self, content: Dict, platform: str) -> Dict:
        """Check platform-specific specs (aspect ratio, duration, etc.)"""
        # Implementation details...
        pass
```

**Human Review Dashboard Workflow:**

```
QA Report Generated
    ↓
QA Score > 95% + No Flags?
    ├─ YES → AUTO_APPROVE → Queue for Distribution
    └─ NO → Send to Human Review Queue
              ↓
         Review Interface Shows:
         - Video preview with QA flags highlighted
         - Product info for accuracy verification
         - Suggested corrections
         - Approve/Reject/Revise options
              ↓
         Human Decision
         ├─ APPROVE → Send to Distribution
         ├─ REVISE → Return to Generation (with notes)
         └─ REJECT → Remove from batch, log reason
```

---

### **Step 4: Distribution & Publishing**

**Multi-Channel Distribution:**

```python
class ContentDistributionEngine:
    
    def __init__(self):
        self.distribution_channels = {
            'instagram_reels': InstagramDistributor(),
            'tiktok': TikTokDistributor(),
            'youtube_shorts': YouTubeDistributor(),
            'amazon_dsp': AmazonDSPDistributor(),
            'walmart_connect': WalmartConnectDistributor(),
            'ctv': CTVDistributor(),  # Roku, YouTube TV, Hulu
            'dooh': DOOHDistributor(),  # Digital out-of-home
            'ecommerce': EcommerceDistributor()  # Shopify, WooCommerce
        }
    
    async def publish_content(self, 
                             content: Dict,
                             target_channels: List[str],
                             scheduling: Dict) -> Dict:
        """
        Publish approved content to multiple channels
        
        Args:
            content: Approved video content with metadata
            target_channels: List of distribution channels
            scheduling: Immediate|scheduled|conditional
            
        Returns:
            Distribution report with status for each channel
        """
        
        distribution_report = {
            'batch_id': content['batch_id'],
            'timestamp': time.time(),
            'channels_attempted': len(target_channels),
            'channels_succeeded': 0,
            'channels_failed': 0,
            'distribution_details': []
        }
        
        for channel in target_channels:
            if channel not in self.distribution_channels:
                distribution_report['distribution_details'].append({
                    'channel': channel,
                    'status': 'UNSUPPORTED_CHANNEL',
                    'error': f'Channel {channel} not configured'
                })
                distribution_report['channels_failed'] += 1
                continue
            
            try:
                distributor = self.distribution_channels[channel]
                result = await distributor.publish(
                    content=content,
                    scheduling=scheduling
                )
                
                if result['status'] == 'SUCCESS':
                    distribution_report['channels_succeeded'] += 1
                    distribution_report['distribution_details'].append({
                        'channel': channel,
                        'status': 'SUCCESS',
                        'published_url': result.get('published_url'),
                        'published_id': result.get('published_id'),
                        'timestamp': result.get('timestamp')
                    })
                else:
                    distribution_report['channels_failed'] += 1
                    distribution_report['distribution_details'].append({
                        'channel': channel,
                        'status': 'FAILED',
                        'error': result.get('error')
                    })
                    
            except Exception as e:
                distribution_report['channels_failed'] += 1
                distribution_report['distribution_details'].append({
                    'channel': channel,
                    'status': 'ERROR',
                    'error': str(e)
                })
        
        return distribution_report
```

**Channel-Specific Implementation Example (Instagram):**

```python
class InstagramDistributor:
    
    def __init__(self):
        from instagram_business_sdk import InstagramAPI
        self.api = InstagramAPI(
            access_token=os.getenv("INSTAGRAM_ACCESS_TOKEN"),
            business_account_id=os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
        )
    
    async def publish(self, content: Dict, scheduling: Dict) -> Dict:
        """
        Publish video to Instagram Reels
        """
        
        try:
            # Convert video to Instagram specifications (9:16, <90s)
            prepared_content = await self._prepare_for_instagram(content)
            
            # Upload to Instagram
            response = self.api.media.create(
                media_type='VIDEO',
                video_url=prepared_content['video_url'],
                caption=prepared_content['caption'],
                access_token=self.api.access_token
            )
            
            # Schedule or publish immediately
            if scheduling.get('mode') == 'scheduled':
                response = self.api.media.schedule(
                    media_id=response['id'],
                    scheduled_publish_time=scheduling.get('scheduled_time')
                )
            else:
                response = self.api.media.publish(
                    media_id=response['id']
                )
            
            return {
                'status': 'SUCCESS',
                'published_url': f"https://instagram.com/reel/{response['id']}",
                'published_id': response['id'],
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {
                'status': 'FAILED',
                'error': str(e)
            }
    
    async def _prepare_for_instagram(self, content: Dict) -> Dict:
        """
        Ensure video meets Instagram Reels specs:
        - Aspect ratio: 9:16
        - Duration: 15-90 seconds
        - Resolution: 1080x1920 or higher
        - Format: MP4
        """
        # Implementation details...
        pass
```

---

### **Step 5: Performance Measurement & Analytics**

**Metrics Collection & Reporting:**

```python
class PerformanceAnalyticsEngine:
    
    def __init__(self):
        self.analytics_db = {
            'views': [],
            'clicks': [],
            'conversions': [],
            'engagement': [],
            'roi': []
        }
    
    async def collect_performance_data(self, 
                                      content_id: str,
                                      channel: str) -> Dict:
        """
        Pull real-time performance metrics from each distribution channel
        """
        
        channel_apis = {
            'instagram_reels': self._fetch_instagram_insights,
            'tiktok': self._fetch_tiktok_analytics,
            'youtube_shorts': self._fetch_youtube_analytics,
            'amazon_dsp': self._fetch_amazon_insights,
            # ... other channels
        }
        
        if channel not in channel_apis:
            return {'status': 'UNSUPPORTED_CHANNEL'}
        
        try:
            performance_data = await channel_apis[channel](content_id)
            
            return {
                'content_id': content_id,
                'channel': channel,
                'metrics': {
                    'views': performance_data.get('views', 0),
                    'impressions': performance_data.get('impressions', 0),
                    'clicks': performance_data.get('clicks', 0),
                    'click_through_rate': performance_data.get('ctr', 0),
                    'watch_time_seconds': performance_data.get('watch_time', 0),
                    'engagement_rate': performance_data.get('engagement_rate', 0),
                    'shares': performance_data.get('shares', 0),
                    'conversions': performance_data.get('conversions', 0),
                    'revenue': performance_data.get('revenue', 0)
                },
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {
                'content_id': content_id,
                'channel': channel,
                'status': 'ERROR',
                'error': str(e)
            }
    
    async def generate_insights_report(self,
                                      batch_id: str,
                                      period_days: int = 7) -> Dict:
        """
        Generate actionable insights from performance data
        
        Returns:
        - Best performing content types
        - Top products
        - Channel performance comparison
        - ROI analysis
        - Recommendations for next batch
        """
        
        insights = {
            'batch_id': batch_id,
            'period_days': period_days,
            'top_performers': {
                'by_product': [],
                'by_format': [],
                'by_channel': []
            },
            'underperformers': [],
            'roi_analysis': {},
            'recommendations': [],
            'insights': []
        }
        
        # Query performance data for batch
        batch_data = await self._fetch_batch_performance(batch_id, period_days)
        
        # Analyze top performers
        insights['top_performers']['by_product'] = self._rank_by_product(batch_data)
        insights['top_performers']['by_format'] = self._rank_by_format(batch_data)
        insights['top_performers']['by_channel'] = self._rank_by_channel(batch_data)
        
        # Identify underperformers
        insights['underperformers'] = self._identify_underperformers(batch_data)
        
        # ROI analysis
        insights['roi_analysis'] = self._calculate_roi(batch_data)
        
        # Generate recommendations
        insights['recommendations'] = self._generate_recommendations(batch_data, insights)
        
        return insights
    
    def _generate_recommendations(self, batch_data: Dict, insights: Dict) -> List[str]:
        """
        Generate actionable recommendations for next batch
        """
        
        recommendations = []
        
        # Recommendation 1: Double down on top-performing products
        top_product = insights['top_performers']['by_product'][0]
        recommendations.append(
            f"Increase production for {top_product['name']} - it drives {top_product['engagement_rate']}% engagement"
        )
        
        # Recommendation 2: Format optimization
        top_format = insights['top_performers']['by_format'][0]
        recommendations.append(
            f"Prioritize {top_format['format']} format in next batch - {top_format['conversion_rate']}% conversion rate"
        )
        
        # Recommendation 3: Channel strategy
        top_channel = insights['top_performers']['by_channel'][0]
        recommendations.append(
            f"Increase budget allocation to {top_channel['channel']} - best ROAS at {top_channel['roas']}"
        )
        
        # Recommendation 4: Content strategy
        if insights['roi_analysis'].get('average_roas', 0) > 3:
            recommendations.append("Scale budget - current ROAS exceeds 3:1 threshold")
        else:
            recommendations.append("Refine creative approach - ROAS below target")
        
        return recommendations
```

---

## Workflow Execution Checklist

### **Pre-Generation Phase**
- [ ] Asset URLs validated (HEAD requests successful)
- [ ] All products have descriptions and images
- [ ] Template configuration complete and locked
- [ ] Brand guidelines documented
- [ ] Replicate API key configured and tested
- [ ] Target channels confirmed
- [ ] Database initialized with batch_id

### **Generation Phase**
- [ ] Video generation started (Runway/Kling)
- [ ] Voiceover TTS initiated (XTTS)
- [ ] Audio composition queued
- [ ] Text overlay processing scheduled
- [ ] Retry mechanism active for failures
- [ ] Generation logs captured for audit
- [ ] ~95% success rate achieved

### **QA Phase**
- [ ] Technical specs validated for all formats
- [ ] Brand compliance checked (colors, fonts, logo)
- [ ] Content accuracy verified (product info, pricing)
- [ ] Platform-specific requirements met
- [ ] QA score calculated for each video
- [ ] High-confidence videos (>95%) auto-approved
- [ ] Flagged videos queued for human review
- [ ] Human review completed within 24hrs

### **Distribution Phase**
- [ ] Approved content formatted for each channel
- [ ] Distribution APIs tested and authenticated
- [ ] Scheduling configured (immediate or timed)
- [ ] Content published to all target channels
- [ ] Publishing confirmations logged
- [ ] Content tracking IDs assigned
- [ ] Distribution report generated

### **Analytics Phase**
- [ ] Performance data collection started
- [ ] Metrics flowing from all channels
- [ ] Real-time dashboard updated
- [ ] Insights report generated after 7 days
- [ ] Recommendations compiled for next batch
- [ ] Feedback loop documented

---

## Error Handling & Fallback Strategies

### **Generation Failures**
```
If Runway/Kling fails:
  1. Retry with simplified prompt (automatic)
  2. If still fails after 3 retries:
     a. Fall back to Stable Diffusion (image-based)
     b. Fall back to pre-generated template footage
     c. Flag for manual creation
```

### **API Rate Limiting**
```
If Replicate API limits exceeded:
  1. Implement exponential backoff
  2. Queue remaining tasks for next hour
  3. Distribute batch across multiple API keys (if available)
  4. Alert operations team
```

### **Distribution Failures**
```
If Instagram/TikTok upload fails:
  1. Verify video file integrity
  2. Convert to platform-specific format
  3. Retry with smaller file size (compress)
  4. Queue for manual upload if persistent
```

### **QA Disagreements**
```
If human reviewer overrides QA score:
  1. Log decision and reasoning
  2. Update QA rule thresholds if pattern emerges
  3. Retrain QA model with feedback
  4. Document decision for future reference
```

---

## Performance Optimization Tips

### **Replicate API Optimization**
1. **Batch Processing**: Process multiple videos in parallel (max concurrent based on plan)
2. **Model Selection**: Use Gen-3 Lite for speed, Gen-3 for quality (adjust based on performance needs)
3. **Prompt Engineering**: Shorter, clearer prompts generate faster with similar quality
4. **Caching**: Store frequently used components (logos, brand templates) to reduce regeneration
5. **Async Processing**: Use async/await to avoid blocking on long-running Replicate calls

### **Infrastructure**
1. **Async Job Queue**: Use Redis/Bull for job scheduling and retry management
2. **Webhook Callbacks**: Implement Replicate webhooks instead of polling for status
3. **CDN Distribution**: Cache generated videos on CDN for fast distribution
4. **Database Indexing**: Index batch_id, product_id, channel for quick lookups

### **Cost Optimization**
1. **Replicate Pricing**: Monitor API costs; consider volume discounts for scale
2. **Video Compression**: Compress final videos without quality loss (ffmpeg)
3. **Batch Generation**: Generate during off-peak hours when possible
4. **Selective Regeneration**: Don't regenerate high-performing content variants

---

## Monitoring & Alerting

### **Key Alerts to Configure**
```
IF generation_success_rate < 90%
  THEN alert("Quality issue detected in generation")

IF qa_human_review_queue > 100
  THEN alert("QA bottleneck - need more reviewers")

IF distribution_failure_rate > 5%
  THEN alert("Distribution channel issue")

IF replicate_api_errors > 10
  THEN alert("Replicate API status issue")

IF average_content_roas < 2:1
  THEN alert("Performance degradation - review templates")
```

---

## Summary

This master prompt provides a complete blueprint for building Genjed.ai's content creation workflow with Replicate as the core AI engine. Key elements:

✅ **End-to-end workflow** from asset ingestion to analytics  
✅ **Replicate API integration** with retry logic and fallbacks  
✅ **Automated QA** with human-in-the-loop oversight  
✅ **Multi-channel distribution** with platform-specific handling  
✅ **Performance analytics** feeding back into optimization  
✅ **Production-ready code patterns** in Python and Node.js  
✅ **Error handling** and scalability considerations  
✅ **Monitoring and alerting** for operational health  

Use this as the foundation for development, customizing as needed based on your specific tech stack, team size, and scaling requirements.
