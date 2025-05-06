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

    def crawl(self):
        """Crawl all provided URLs and extract content."""
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            for base_url in self.base_urls:
                self._crawl_page(page, base_url, 0)

            browser.close()

        return self.pages_content

    def _crawl_page(self, page, url, depth):
        """Recursively crawl pages up to max_depth."""
        if url in self.visited_urls or depth > self.max_depth:
            return

        try:
            print(f"Crawling: {url}")
            page.goto(url, wait_until="networkidle")

            # Extract main content, excluding headers, footers, navigation
            content = page.evaluate(
                """() => {
                // Remove unwanted elements
                const elementsToRemove = document.querySelectorAll('header, footer, nav, .navigation, .sidebar, .menu, .ads');
                elementsToRemove.forEach(el => el.remove());
                
                // Get main content
                const mainContent = document.querySelector('main, .main, #main, .content, #content, article, .article, .documentation');
                
                if (mainContent) {
                    return mainContent.innerHTML;
                } else {
                    return document.body.innerHTML;
                }
            }"""
            )

            title = page.title()

            # Store the content
            self.pages_content[url] = {"title": title, "content": content, "url": url}

            self.visited_urls.add(url)

            # Find all documentation links on the page
            links = page.evaluate(
                """() => {
                const links = Array.from(document.querySelectorAll('a[href]'));
                return links.map(link => ({
                    href: link.href,
                    text: link.textContent.trim()
                }));
            }"""
            )

            # Follow documentation links
            base_domain = urlparse(url).netloc
            for link in links:
                link_url = link["href"]
                parsed_link = urlparse(link_url)

                # Only follow links to the same domain and likely documentation pages
                if parsed_link.netloc == base_domain or not parsed_link.netloc:
                    # Convert relative URLs to absolute
                    if not parsed_link.netloc:
                        link_url = urljoin(url, link_url)

                    self._crawl_page(page, link_url, depth + 1)

        except Exception as e:
            print(f"Error crawling {url}: {e}")
