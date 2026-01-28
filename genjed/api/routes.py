"""Genjed API Routes.

RESTful API endpoints for the Genjed.ai content creation workflow.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import asyncio

api = Blueprint('api', __name__, url_prefix='/api/v1')


def run_async(coro):
    """Run async function in sync context."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# In-memory storage (replace with database in production)
_batches = {}
_contents = {}
_campaigns = {}


# ============== Health Check ==============

@api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat()
    })


# ============== Campaign Endpoints ==============

@api.route('/campaigns', methods=['GET'])
def list_campaigns():
    """List all campaigns."""
    return jsonify({
        'campaigns': list(_campaigns.values()),
        'total': len(_campaigns)
    })


@api.route('/campaigns', methods=['POST'])
def create_campaign():
    """Create a new campaign."""
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    campaign_id = f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    campaign = {
        'campaign_id': campaign_id,
        'customer_id': data.get('customer_id', 'default'),
        'name': data.get('name', 'Untitled Campaign'),
        'description': data.get('description', ''),
        'status': 'created',
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }
    _campaigns[campaign_id] = campaign
    
    return jsonify({'campaign': campaign}), 201


@api.route('/campaigns/<campaign_id>', methods=['GET'])
def get_campaign(campaign_id):
    """Get campaign by ID."""
    campaign = _campaigns.get(campaign_id)
    if not campaign:
        return jsonify({'error': 'Campaign not found'}), 404
    return jsonify({'campaign': campaign})


@api.route('/campaigns/<campaign_id>', methods=['DELETE'])
def delete_campaign(campaign_id):
    """Delete a campaign."""
    if campaign_id not in _campaigns:
        return jsonify({'error': 'Campaign not found'}), 404
    del _campaigns[campaign_id]
    return jsonify({'message': 'Campaign deleted'})


# ============== Batch Endpoints ==============

@api.route('/batches', methods=['GET'])
def list_batches():
    """List all batches."""
    return jsonify({
        'batches': list(_batches.values()),
        'total': len(_batches)
    })


@api.route('/batches/<batch_id>', methods=['GET'])
def get_batch(batch_id):
    """Get batch by ID."""
    batch = _batches.get(batch_id)
    if not batch:
        return jsonify({'error': 'Batch not found'}), 404
    return jsonify({'batch': batch})


@api.route('/batches/<batch_id>/status', methods=['GET'])
def get_batch_status(batch_id):
    """Get batch processing status."""
    batch = _batches.get(batch_id)
    if not batch:
        return jsonify({'error': 'Batch not found'}), 404
    return jsonify({
        'batch_id': batch_id,
        'status': batch.get('status', 'unknown'),
        'progress': batch.get('progress', 0),
        'items_processed': batch.get('processed_items', 0),
        'items_total': batch.get('total_items', 0)
    })


# ============== Content Endpoints ==============

@api.route('/contents', methods=['GET'])
def list_contents():
    """List all generated content."""
    batch_id = request.args.get('batch_id')
    status = request.args.get('status')
    
    contents = list(_contents.values())
    
    if batch_id:
        contents = [c for c in contents if c.get('batch_id') == batch_id]
    if status:
        contents = [c for c in contents if c.get('status') == status]
    
    return jsonify({
        'contents': contents,
        'total': len(contents)
    })


@api.route('/contents/<content_id>', methods=['GET'])
def get_content(content_id):
    """Get content by ID."""
    content = _contents.get(content_id)
    if not content:
        return jsonify({'error': 'Content not found'}), 404
    return jsonify({'content': content})


@api.route('/contents/<content_id>/qa', methods=['GET'])
def get_content_qa(content_id):
    """Get QA report for content."""
    content = _contents.get(content_id)
    if not content:
        return jsonify({'error': 'Content not found'}), 404
    return jsonify({
        'content_id': content_id,
        'qa_report': content.get('qa_report', {})
    })


@api.route('/contents/<content_id>/approve', methods=['POST'])
def approve_content(content_id):
    """Manually approve content."""
    content = _contents.get(content_id)
    if not content:
        return jsonify({'error': 'Content not found'}), 404
    
    content['status'] = 'APPROVED'
    content['updated_at'] = datetime.utcnow().isoformat()
    
    return jsonify({'content': content})


@api.route('/contents/<content_id>/reject', methods=['POST'])
def reject_content(content_id):
    """Manually reject content."""
    content = _contents.get(content_id)
    if not content:
        return jsonify({'error': 'Content not found'}), 404
    
    data = request.json or {}
    content['status'] = 'REJECTED'
    content['rejection_reason'] = data.get('reason', '')
    content['updated_at'] = datetime.utcnow().isoformat()
    
    return jsonify({'content': content})


# ============== Product Endpoints ==============

_products = {}

@api.route('/products', methods=['GET'])
def list_products():
    """List all products."""
    return jsonify({
        'products': list(_products.values()),
        'total': len(_products)
    })


@api.route('/products', methods=['POST'])
def create_product():
    """Create a new product."""
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    from uuid import uuid4
    product_id = str(uuid4())
    product = {
        'product_id': product_id,
        'name': data.get('name', 'Untitled Product'),
        'description': data.get('description', ''),
        'image_urls': data.get('image_urls', []),
        'category': data.get('category', 'other'),
        'price': data.get('price', 0),
        'currency': data.get('currency', 'USD'),
        'brand': data.get('brand', ''),
        'created_at': datetime.utcnow().isoformat()
    }
    _products[product_id] = product
    
    return jsonify({'product': product}), 201


@api.route('/products/<product_id>', methods=['GET'])
def get_product(product_id):
    """Get product by ID."""
    product = _products.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    return jsonify({'product': product})


@api.route('/products/<product_id>', methods=['PUT'])
def update_product(product_id):
    """Update a product."""
    product = _products.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    data = request.json or {}
    for key in ['name', 'description', 'image_urls', 'category', 'price', 'currency', 'brand']:
        if key in data:
            product[key] = data[key]
    product['updated_at'] = datetime.utcnow().isoformat()
    
    return jsonify({'product': product})


@api.route('/products/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete a product."""
    if product_id not in _products:
        return jsonify({'error': 'Product not found'}), 404
    del _products[product_id]
    return jsonify({'message': 'Product deleted'})


# ============== Template Endpoints ==============

_templates = {}

@api.route('/templates', methods=['GET'])
def list_templates():
    """List all templates."""
    return jsonify({
        'templates': list(_templates.values()),
        'total': len(_templates)
    })


@api.route('/templates', methods=['POST'])
def create_template():
    """Create a new template."""
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    from uuid import uuid4
    template_id = str(uuid4())
    template = {
        'template_id': template_id,
        'name': data.get('name', 'Untitled Template'),
        'type': data.get('type', 'product_ad'),
        'visual_config': data.get('visual_config', {}),
        'audio_config': data.get('audio_config', {}),
        'text_overlay': data.get('text_overlay', {}),
        'created_at': datetime.utcnow().isoformat()
    }
    _templates[template_id] = template
    
    return jsonify({'template': template}), 201


@api.route('/templates/<template_id>', methods=['GET'])
def get_template(template_id):
    """Get template by ID."""
    template = _templates.get(template_id)
    if not template:
        return jsonify({'error': 'Template not found'}), 404
    return jsonify({'template': template})


# ============== Analytics Endpoints ==============

@api.route('/analytics/overview', methods=['GET'])
def analytics_overview():
    """Get analytics overview."""
    return jsonify({
        'total_campaigns': len(_campaigns),
        'total_batches': len(_batches),
        'total_contents': len(_contents),
        'total_products': len(_products),
        'total_templates': len(_templates)
    })


@api.route('/analytics/performance', methods=['GET'])
def analytics_performance():
    """Get performance analytics."""
    return jsonify({
        'message': 'Performance analytics endpoint',
        'data': {}
    })
