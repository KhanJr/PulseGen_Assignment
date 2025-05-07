import streamlit as st
import json
from documentation_crawler import DocumentationCrawler
from content_processor import ContentProcessor
from module_extractor import ModuleExtractor


def main():
    st.title("Documentation Module Extractor")

    # Input for URLs
    st.header("Input URLs")
    urls_input = st.text_area(
        "Enter one or more documentation URLs (one per line):",
        help="Example: https://help.instagram.com",
    )

    max_depth = st.slider(
        "Maximum crawl depth",
        min_value=1,
        max_value=5,
        value=1,
        help="How many links deep to crawl from the initial URL",
    )

    # Ollama model selection
    model_options = [
        "llama3.1",
        "llama3",
        "codellama",
        "mistral",
        "phi3",
        "qwen3:1.7b",
        "phi3:mini",
    ]
    selected_model = st.selectbox(
        "Select Ollama model",
        model_options,
        help="Make sure you've pulled this model using 'ollama pull [model]'",
    )

    if st.button("Extract Modules"):
        if not urls_input.strip():
            st.error("Please enter at least one URL")
            return

        urls = [url.strip() for url in urls_input.split("\n") if url.strip()]

        with st.spinner("Crawling documentation pages..."):
            # Step 1: Crawl the documentation
            crawler = DocumentationCrawler(urls, max_depth=max_depth)
            pages_content = crawler.crawl()

            st.success(f"Crawled {len(pages_content)} pages")

        with st.spinner("Processing content..."):
            # Step 2: Process the content
            processor = ContentProcessor(pages_content)
            processed_content = processor.process()

            st.success("Content processed successfully")

        with st.spinner(f"Extracting modules using {selected_model}..."):
            # Step 3: Extract modules and submodules using Ollama
            extractor = ModuleExtractor(processed_content, model_name=selected_model)
            output = extractor.extract_modules()

            st.success("Modules extracted successfully")

        # Display results
        st.header("Extracted Modules")
        st.json(output)

        # Option to download as JSON file
        json_str = json.dumps(output, indent=2)
        st.download_button(
            label="Download JSON",
            data=json_str,
            file_name="extracted_modules.json",
            mime="application/json",
        )


if __name__ == "__main__":
    main()
