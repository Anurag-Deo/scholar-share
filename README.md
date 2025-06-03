# 🎓 ScholarShare - AI-Powered Research Dissemination Platform

Transform complex research papers into accessible, multi-format content for broader audience engagement.

## ✨ Features

### 📄 Paper Analysis & Processing
- **Multi-format Input**: Upload PDFs, paste URLs (arXiv, etc.), or input text directly
- **Intelligent Analysis**: Extract key findings, methodology, results, and conclusions
- **Complexity Assessment**: Automatically determine paper complexity level
- **Technical Term Extraction**: Identify and explain technical terminology

### 📝 Content Generation
- **Blog Generation**: Create beginner-friendly blog posts with SEO optimization
- **Social Media Content**: Generate platform-specific posts for LinkedIn, Twitter, Facebook, and Instagram
- **🎨 NEW: AI-Generated Images**: Automatically create custom images for each social media platform
- **Academic Posters**: Generate LaTeX-based conference posters (IEEE, ACM, Nature styles)

### 🚀 Publishing & Sharing
- **Dev.to Integration**: Publish blog posts directly to Dev.to
- **Download Options**: Export content as Markdown files
- **Multi-Platform Optimization**: Content tailored for each platform's audience

## 🆕 Image Generation Feature

ScholarShare now automatically generates custom images for social media posts using AI:

### 🎨 Platform-Specific Images
- **LinkedIn**: Professional, clean, business-appropriate imagery
- **Twitter**: Eye-catching, modern, tech-focused visuals  
- **Facebook**: Engaging, accessible, community-friendly images
- **Instagram**: Vibrant, aesthetic, visual-first content

### 🤖 AI-Powered Visual Creation
1. **Smart Prompt Generation**: Uses GPT to create detailed visual prompts based on your research
2. **DALL-E Integration**: Generates high-quality images using OpenAI's DALL-E model
3. **Automatic Optimization**: Each image is tailored for its target platform's style and audience

### 📁 Image Management
- Images automatically saved to `outputs/images/`
- Download images directly from the interface
- Descriptive filenames for easy organization

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key (for text and image generation)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd scholarshare
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

5. **Open in browser**: Navigate to `http://localhost:7860`

## 🔧 Configuration

### Environment Variables
```bash
# Required: OpenAI API key for text generation
LIGHT_MODEL_API_KEY=your-openai-api-key

# Optional: Separate key for image generation
IMAGE_GEN_API_KEY=your-openai-api-key

# Optional: Image generation settings
IMAGE_GEN_MODEL=dall-e-3
IMAGE_GEN_IMAGE_SIZE=1024x1024
IMAGE_GEN_IMAGE_QUALITY=standard
IMAGE_GEN_IMAGE_STYLE=vivid
```

### Testing Image Generation
Run the included test script to verify image generation:
```bash
python test_image_generation.py
```

## 📖 Usage Guide

### 1. Process a Research Paper
- Upload a PDF file, paste an arXiv URL, or input text directly
- Click "🔍 Analyze Paper" to extract key information

### 2. Generate Blog Content
- Navigate to the "📝 Blog Generation" tab
- Click "✍️ Generate Blog Content" for SEO-optimized articles

### 3. Create Social Media Content with Images
- Go to the "📱 Social Media Content" tab
- Click "📱 Generate Social Content"
- Wait for both text and custom images to generate
- Each platform gets optimized content and matching visuals

### 4. Generate Academic Posters
- Use the "🎨 Poster Generation" tab
- Choose from IEEE, ACM, or Nature templates
- Download LaTeX code and compiled PDFs

### 5. Publish Content
- Use the "🚀 Publishing" tab to share to Dev.to
- Download all content as Markdown files

## 🏗️ Architecture

```
app/
├── agents/          # AI agents for different content types
├── services/        # External service integrations
│   ├── image_service.py    # 🆕 AI image generation
│   ├── llm_service.py      # LLM integration
│   └── devto_service.py    # Publishing service
├── models/          # Data schemas and models
├── config/          # Application configuration
└── utils/           # Helper utilities
```

## 🎯 Platform-Specific Features

### LinkedIn
- Professional tone and formatting
- Business-focused imagery with clean design
- Optimized for professional networking

### Twitter
- Thread format for longer content
- Character limit optimization
- Modern, tech-focused visuals

### Facebook
- Conversational tone with engagement hooks
- Community-friendly imagery
- Question prompts for comments

### Instagram
- Visual-first captions with emojis
- Vibrant, aesthetic imagery
- Hashtag optimization

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines for more information.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For questions, issues, or feature requests, please open an issue on GitHub or refer to our troubleshooting guide in `IMAGE_GENERATION_GUIDE.md`.
