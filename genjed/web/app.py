"""Genjed Web Application.

Flask-based web interface for the Genjed.ai content creation workflow.
"""

import os
import sys
import asyncio
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import models
from models.product import Product, ProductCategory, BrandGuidelines, AssetBundle
from models.template import Template, TemplateType, VisualConfig, AudioConfig, TextOverlay
from models.batch import GenerationConfig, SchedulingMode
from core.workflow_orchestrator import WorkflowOrchestrator

# Import API routes
from api.routes import api as api_blueprint

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'genjed-dev-key-change-in-production')

# Register API blueprint
app.register_blueprint(api_blueprint)

# Store workflow results in memory (in production, use a database)
workflow_results = {}
batches = {}


def run_async(coro):
    """Run async function in sync context."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@app.route('/')
def index():
    """Home page with dashboard."""
    return render_template('index.html', 
                         batches=list(batches.values()),
                         results=list(workflow_results.values()))


@app.route('/create-campaign', methods=['GET', 'POST'])
def create_campaign():
    """Create a new content generation campaign."""
    if request.method == 'POST':
        try:
            # Get form data
            customer_id = request.form.get('customer_id', 'customer_001')
            campaign_id = request.form.get('campaign_id', f'campaign_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
            
            # Product data
            product_name = request.form.get('product_name', 'Sample Product')
            product_description = request.form.get('product_description', 'A great product')
            product_price = float(request.form.get('product_price', 99.99))
            product_category = request.form.get('product_category', 'electronics')
            product_image_url = request.form.get('product_image_url', 'https://example.com/product.jpg')
            
            # Brand data
            brand_name = request.form.get('brand_name', 'MyBrand')
            brand_colors = request.form.get('brand_colors', '#FF0000,#00FF00').split(',')
            brand_tone = request.form.get('brand_tone', 'Professional')
            
            # Template data
            template_name = request.form.get('template_name', 'Product Ad')
            headline_template = request.form.get('headline_template', 'Amazing {{product_name}}')
            cta_text = request.form.get('cta_text', 'Shop Now!')
            
            # Generation config
            target_channels = request.form.getlist('target_channels') or ['instagram_reels', 'tiktok']
            aspect_ratios = request.form.getlist('aspect_ratios') or ['9:16']
            durations = [int(d) for d in request.form.getlist('durations')] or [15]
            
            # Create product
            product = Product(
                name=product_name,
                description=product_description,
                image_urls=[product_image_url],
                category=ProductCategory(product_category),
                price=product_price,
                brand=brand_name
            )
            
            # Create brand guidelines
            brand_guidelines = BrandGuidelines(
                brand_name=brand_name,
                brand_colors=brand_colors,
                fonts=['Inter', 'Roboto'],
                tone_of_voice=brand_tone
            )
            
            # Create asset bundle
            asset_bundle = AssetBundle(
                customer_id=customer_id,
                campaign_id=campaign_id,
                products=[product],
                brand_guidelines=brand_guidelines
            )
            
            # Create template
            template = Template(
                name=template_name,
                type=TemplateType.PRODUCT_AD,
                visual_config=VisualConfig(
                    aspect_ratios=aspect_ratios,
                    duration_seconds=durations,
                    resolution='1080p',
                    frame_rate=30
                ),
                audio_config=AudioConfig(
                    voiceover_enabled=request.form.get('voiceover_enabled') == 'on'
                ),
                text_overlay=TextOverlay(
                    headline_template=headline_template,
                    cta_text=cta_text
                )
            )
            
            # Create generation config
            generation_config = GenerationConfig(
                batch_size=10,
                target_channels=target_channels,
                scheduling_mode=SchedulingMode.IMMEDIATE,
                resolution='1080p',
                codec='h264'
            )
            
            # Run workflow
            orchestrator = WorkflowOrchestrator()
            result = run_async(orchestrator.execute_workflow(
                asset_bundle=asset_bundle,
                template=template,
                generation_config=generation_config
            ))
            
            # Store result
            workflow_results[result.batch_id] = {
                'batch_id': result.batch_id,
                'campaign_id': campaign_id,
                'success': result.success,
                'contents_generated': result.contents_generated,
                'contents_qa_passed': result.contents_qa_passed,
                'contents_distributed': result.contents_distributed,
                'errors': result.errors,
                'created_at': datetime.now().isoformat()
            }
            
            return redirect(url_for('view_batch', batch_id=result.batch_id))
            
        except Exception as e:
            return render_template('create_campaign.html', error=str(e))
    
    return render_template('create_campaign.html')


@app.route('/batch/<batch_id>')
def view_batch(batch_id):
    """View batch details and results."""
    result = workflow_results.get(batch_id)
    if not result:
        return render_template('error.html', message='Batch not found'), 404
    return render_template('batch_details.html', result=result)


@app.route('/api/batches')
def api_batches():
    """API endpoint to list all batches."""
    return jsonify(list(workflow_results.values()))


@app.route('/api/batch/<batch_id>')
def api_batch(batch_id):
    """API endpoint to get batch details."""
    result = workflow_results.get(batch_id)
    if not result:
        return jsonify({'error': 'Batch not found'}), 404
    return jsonify(result)


@app.route('/api/generate', methods=['POST'])
def api_generate():
    """API endpoint to trigger content generation."""
    try:
        data = request.json
        
        # Create product from API data
        product = Product(
            name=data.get('product_name', 'Sample Product'),
            description=data.get('product_description', 'A great product'),
            image_urls=data.get('image_urls', ['https://example.com/product.jpg']),
            category=ProductCategory(data.get('category', 'electronics')),
            price=float(data.get('price', 99.99))
        )
        
        # Create brand guidelines
        brand_guidelines = BrandGuidelines(
            brand_name=data.get('brand_name', 'MyBrand'),
            brand_colors=data.get('brand_colors', ['#FF0000']),
            fonts=['Inter'],
            tone_of_voice=data.get('tone', 'Professional')
        )
        
        # Create asset bundle
        asset_bundle = AssetBundle(
            customer_id=data.get('customer_id', 'api_customer'),
            campaign_id=data.get('campaign_id', f'api_campaign_{datetime.now().strftime("%Y%m%d_%H%M%S")}'),
            products=[product],
            brand_guidelines=brand_guidelines
        )
        
        # Create template
        template = Template(
            name='API Template',
            type=TemplateType.PRODUCT_AD,
            visual_config=VisualConfig(
                aspect_ratios=data.get('aspect_ratios', ['9:16']),
                duration_seconds=data.get('durations', [15])
            ),
            text_overlay=TextOverlay(
                headline_template=data.get('headline', '{{product_name}}'),
                cta_text=data.get('cta', 'Shop Now!')
            )
        )
        
        # Create generation config
        generation_config = GenerationConfig(
            target_channels=data.get('channels', ['instagram_reels'])
        )
        
        # Run workflow
        orchestrator = WorkflowOrchestrator()
        result = run_async(orchestrator.execute_workflow(
            asset_bundle=asset_bundle,
            template=template,
            generation_config=generation_config
        ))
        
        # Store result
        workflow_results[result.batch_id] = {
            'batch_id': result.batch_id,
            'success': result.success,
            'contents_generated': result.contents_generated,
            'contents_qa_passed': result.contents_qa_passed,
            'contents_distributed': result.contents_distributed,
            'errors': result.errors,
            'created_at': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'batch_id': result.batch_id,
            'result': workflow_results[result.batch_id]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    # Check if API key is set via environment variable
    if not os.getenv('REPLICATE_API_KEY'):
        print("WARNING: REPLICATE_API_KEY environment variable not set.")
        print("Set it with: export REPLICATE_API_KEY='your-api-key'")
    
    print("Starting Genjed.ai Web Application...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)
