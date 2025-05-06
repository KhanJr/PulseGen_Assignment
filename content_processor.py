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
                soup = BeautifulSoup(page_data["content"], "html.parser")

                # Remove scripts, styles, and comments
                for element in soup(["script", "style"]):
                    element.decompose()

                # Extract hierarchical structure (headers and content)
                structure = self._extract_structure(soup)

                # Validate the structure
                validated_structure = self._validate_structure(structure)

                self.processed_content[url] = {
                    "title": self._sanitize_text(page_data["title"]),
                    "structure": validated_structure,
                    "url": url,
                }
            except Exception as e:
                print(f"Error processing URL {url}: {e}")
                self.processed_content[url] = {
                    "title": "Error processing page",
                    "structure": [],
                    "url": url,
                }

        # Final validation check
        self._ensure_json_compatibility()
        return self.processed_content

    def _extract_structure(self, soup):
        """Extract hierarchical structure from HTML."""
        structure = []
        converter = html2text.HTML2Text()
        converter.ignore_links = False

        # Find all headers
        headers = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])

        for header in headers:
            header_level = int(header.name[1])
            header_text = header.get_text().strip()

            # Find content between this header and the next header
            content = []
            current = header.next_sibling

            while current and not (
                current.name and current.name in ["h1", "h2", "h3", "h4", "h5", "h6"]
            ):
                if current.name in ["p", "ul", "ol", "div", "table"]:
                    content.append(str(current))
                current = current.next_sibling

            # Convert content to markdown for better readability
            content_text = "\n".join(content)
            md_content = converter.handle(content_text)

            structure.append(
                {
                    "level": header_level,
                    "title": header_text,
                    "content": md_content.strip(),
                }
            )

        return structure

    def _validate_structure(self, structure):
        """Validate and sanitize the extracted structure for JSON compatibility."""
        validated = []

        if not isinstance(structure, list):
            print("Warning: Structure is not a list. Creating empty structure.")
            return validated

        for item in structure:
            try:
                # Check if item has required fields
                if not isinstance(item, dict):
                    continue

                if not all(key in item for key in ["level", "title", "content"]):
                    continue

                # Sanitize values
                validated_item = {
                    "level": int(item["level"]),
                    "title": self._sanitize_text(item["title"]),
                    "content": self._sanitize_text(item["content"]),
                }
                validated.append(validated_item)
            except Exception as e:
                print(f"Error validating structure item: {e}")

        return validated

    def _sanitize_text(self, text):
        """Clean up text to prevent JSON parsing issues."""
        if not text:
            return ""

        # Ensure text is a string
        text = str(text)

        # Replace problematic quotes
        text = text.replace("'", "'").replace('"', '"')

        # Remove control characters
        text = re.sub(r"[\x00-\x1F\x7F]", "", text)

        # Handle newlines and tabs for better JSON compatibility
        text = text.replace("\n", " ").replace("\r", " ").replace("\t", " ")

        # Replace any other problematic characters for JSON
        text = re.sub(r"[^\x20-\x7E]", "", text)

        return text

    def _ensure_json_compatibility(self):
        """Verify the processed content can be serialized to valid JSON."""
        try:
            # Test serialization
            json.dumps(self.processed_content)
            return True
        except (TypeError, ValueError) as e:
            print(f"JSON serialization error: {e}. Attempting to fix...")

            # Try to repair the content
            for url in self.processed_content:
                if "structure" in self.processed_content[url]:
                    # Keep only validated structure items
                    self.processed_content[url]["structure"] = [
                        item
                        for item in self.processed_content[url]["structure"]
                        if isinstance(item, dict)
                        and "level" in item
                        and "title" in item
                        and "content" in item
                    ]

            # Verify again
            try:
                json.dumps(self.processed_content)
                print("JSON compatibility issue resolved.")
                return True
            except (TypeError, ValueError) as e:
                print(f"Could not fix JSON compatibility: {e}")
                # Last resort - create minimal valid output
                self.processed_content = {
                    "error": "Content could not be processed into valid JSON",
                    "urls": list(self.pages_content.keys()),
                }
                return False
