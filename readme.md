# Module Extraction AI Agent

A powerful AI-powered Streamlit application that extracts structured information from documentation websites, identifying modules and submodules with detailed descriptions.

## 📋 Overview

This application automatically crawls documentation websites, processes the content, and uses local Large Language Models (LLMs) through Ollama to identify key components of products or services. It transforms unstructured documentation into structured, hierarchical JSON data that clearly delineates modules, submodules, and their descriptions.

## ✨ Features

- **Multi-URL Processing**: Handles one or more documentation URLs simultaneously
- **Recursive Crawling**: Automatically explores and extracts content from linked pages
- **Intelligent Structure Extraction**: Identifies hierarchical relationships between content sections
- **Local LLM Integration**: Uses Ollama to run inference without sending data to external APIs
- **Structured JSON Output**: Generates well-formatted output ready for integration with other systems
- **User-Friendly Interface**: Simple Streamlit UI for easy interaction

## 🏗️ Technical Architecture

**Web Crawler Component**

```python
from playwright.sync_api import sync_playwright
import os
import json
from urllib.parse import urljoin, urlparse

class DocumentationCrawler:
    def __init__(self, base_urls, max_depth=3, cache_dir="cache"):
        self.base_urls = base_urls if isinstance(base_urls, list) else [base_urls]
        self.visited_urls = set()
        self.pages_content = {}
        self.max_depth = max_depth
        self.cache_dir = cache_dir

        # Create cache directory if it doesn't exist
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
```

**Content Processor Component**

```python
from bs4 import BeautifulSoup
import html2text
import json
import re

class ContentProcessor:
    def __init__(self, pages_content):
        self.pages_content = pages_content
        self.processed_content = {}

    def process(self):
        """Process all HTML content and convert to structured format."""
        for url, page_data in self.pages_content.items():
            try:
                # Ensure we have content to process
                if not page_data.get("content"):
                    print(f"Warning: No content found for {url}")
                    continue
```

**Module Extractor Component**

```python
from langchain_ollama.chat_models import ChatOllama
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema

class ModuleExtractor:
    def __init__(self, processed_content, model_name="llama3.1"):
        self.processed_content = processed_content
        self.model_name = model_name
```

## 🚀 Installation

### Prerequisites

- Python 3.8+
- [Ollama](https://ollama.com/download) installed and running locally

### Setup Steps

```bash
# Clone the repository
git clone https://github.com/yourusername/module-extraction-agent.git
cd module-extraction-agent

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install

# Pull required Ollama model
ollama pull llama3.1
```

### Required Dependencies

```
streamlit==1.27.0
playwright==1.39.0
beautifulsoup4==4.12.2
html2text==2020.1.16
langchain==0.1.0
langchain-core==0.1.0
langchain-ollama==0.0.1
fix-busted-json==0.1.0
```

## 💻 Usage

### Starting the Application

```bash
streamlit run app.py
```

### Using the Interface

1. Enter one or more documentation URLs (one per line)
2. Adjust crawl depth using the slider (recommended: 2-3 for most sites)
3. Select your preferred Ollama model (llama3.1 recommended)
4. Click "Extract Modules" to begin processing
5. View and download the resulting JSON

### Command Line Interface

For headless operation or automation:

```bash
python module_extractor.py --urls https://www.pulsegen.io/about-us --depth 3 --model llama3.1
```

## 📊 Example Output

```json
{
  "Account Management": {
    "Description": "Tools and settings for controlling your profile, authentication, and account preferences.",
    "Submodules": {
      "Profile Settings": "Configure personal information, username, and profile visibility options.",
      "Security Controls": "Manage passwords, two-factor authentication, and account recovery options.",
      "Privacy Settings": "Control who can view your content, send messages, or find your account."
    }
  },
  "Content Creation": {
    "Description": "Features for creating, editing, and publishing different types of content.",
    "Submodules": {
      "Post Creation": "Upload photos and videos with captions, locations, and tags.",
      "Story Creation": "Share temporary content with interactive stickers and effects.",
      "Reels": "Create and edit short-form vertical videos with audio and effects."
    }
  }
}
```

## 🧪 Testing

This application has been tested on multiple documentation websites:

- **Consumer Platforms**: Instagram Help Center, Twitter Help Center
- **B2B Documentation**: PulseGen Documentation
- **Open Source Projects**: React Documentation, FastAPI Documentation

The tool effectively handles various documentation structures, from simple FAQ pages to complex technical documentation.

## 🔧 Advanced Configuration

### Customizing the LLM

The application supports multiple Ollama models. For optimal results:

- Use `llama3.1` for best general-purpose extraction
- Use `mistral` for faster extraction with slightly lower accuracy

### JSON Parsing Optimization

To handle JSON parsing errors:

```python
def repair_json(broken_json):
    """Repair common JSON formatting issues."""
    # Convert single quotes to double quotes
    step1 = re.sub(r"(?<!\\)'", '"', broken_json)

    # Add missing commas between objects in arrays
    step2 = re.sub(r'}(\s*){', '}, {', step1)

    # Try to add missing closing brackets if needed
    if step2.count('{') > step2.count('}'):
        step2 += '}' * (step2.count('{') - step2.count('}'))

    return step2
```

## 📝 Known Limitations

- Processing time scales with documentation size and complexity
- Very large sites may exceed memory limitations
- JSON parsing errors can occur with extremely complex or poorly structured content
- Local LLM quality depends on available computational resources

## 🔮 Future Enhancements

- Docker containerization for easy deployment
- Support for additional document formats (PDF, Markdown)
- Semantic chunking for more intelligent content processing
- Answer caching mechanism for faster repeat queries
- Confidence scores for extracted modules and submodules
- API endpoints for headless operation

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m 'Add YourFeature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

_Created for the Pulse AI Assignment challenge_

Sources
