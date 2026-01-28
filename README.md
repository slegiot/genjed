# Genjed.ai

AI-Powered Content Creation Engine for generating professional video content.

## Features

- **AI Video Generation** - Generate videos using Runway Gen-3, Kling AI, Stable Video Diffusion
- **Text-to-Speech** - Multilingual voiceovers with XTTS-v2 (20+ languages)
- **Quality Assurance** - Automated QA for brand compliance, technical specs, content accuracy
- **Multi-Channel Distribution** - Publish to Instagram Reels, TikTok, YouTube Shorts, CTV, DOOH
- **Performance Analytics** - Track views, engagement, conversions, and ROI

## Quick Start

### Prerequisites

- Python 3.9+
- Replicate API key

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/genjed.git
cd genjed

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export REPLICATE_API_KEY='your-api-key'
export FLASK_SECRET_KEY='your-secret-key'
```

### Running the Application

```bash
cd genjed/web
python3 app.py
```

Open http://localhost:5000 in your browser.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/health` | GET | Health check |
| `/api/v1/campaigns` | GET/POST | List/create campaigns |
| `/api/v1/campaigns/<id>` | GET/DELETE | Get/delete campaign |
| `/api/v1/batches` | GET | List batches |
| `/api/v1/batches/<id>` | GET | Get batch details |
| `/api/v1/contents` | GET | List generated content |
| `/api/v1/contents/<id>` | GET | Get content details |
| `/api/v1/contents/<id>/approve` | POST | Approve content |
| `/api/v1/contents/<id>/reject` | POST | Reject content |
| `/api/v1/products` | GET/POST | List/create products |
| `/api/v1/templates` | GET/POST | List/create templates |
| `/api/v1/analytics/overview` | GET | Analytics overview |

## Project Structure

```
genjed/
├── genjed/
│   ├── api/           # REST API endpoints
│   ├── config/        # Configuration management
│   ├── core/          # Workflow orchestration
│   ├── models/        # Data models
│   ├── services/      # Business logic services
│   ├── utils/         # Utility functions
│   └── web/           # Flask web app & templates
├── requirements.txt
└── README.md
```

## License

MIT License - see LICENSE file for details.

## Author

Genjed.ai Team
