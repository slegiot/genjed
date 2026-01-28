#!/usr/bin/env python3
"""Genjed Application Entry Point.

Run the web application from the project root directory.
"""

import os
import sys

# Add the genjed package to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set working directory to project root
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Import and run the Flask app
from genjed.web.app import app

if __name__ == '__main__':
    # Check if API key is configured
    if not os.getenv('REPLICATE_API_KEY'):
        print("⚠️  WARNING: REPLICATE_API_KEY not set")
        print("   Set with: export REPLICATE_API_KEY='your-key'")
        print()
    
    print("🚀 Starting Genjed.ai Web Application...")
    print("📍 Open http://localhost:5001 in your browser")
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5001)
