#!/usr/bin/env python3
"""
Entry point for Hugging Face Spaces deployment.
This file is required by HF Spaces and should be named 'app.py' in the root directory.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import and run the main application
from main import create_interface

if __name__ == "__main__":
    # Create output directories
    Path("outputs/posters").mkdir(parents=True, exist_ok=True)
    Path("outputs/blogs").mkdir(parents=True, exist_ok=True)
    Path("outputs/presentations").mkdir(parents=True, exist_ok=True)
    Path("data").mkdir(parents=True, exist_ok=True)
    
    # Create the Gradio interface
    app = create_interface()
    
    # Launch with Hugging Face Spaces compatible settings
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,  # HF Spaces uses port 7860
        share=False,
        debug=False
    )
