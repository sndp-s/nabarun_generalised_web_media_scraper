from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def parse_links(html_content, base_url):
    """
    Parse URLs from the given HTML content and return fully qualified URLs.
    
    Args:
        html_content (str): The HTML content as a string.
        base_url (str): The base URL to resolve relative URLs.
    
    Returns:
        List[str]: A list of fully qualified URLs.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    urls = set()  # Use a set to avoid duplicate URLs

    # Find all links in the HTML content
    for link in soup.find_all('a', href=True):
        url = link['href']
        # Resolve relative URLs to absolute URLs
        full_url = urljoin(base_url, url)
        parsed_url = urlparse(full_url)

        # Only include valid URLs with HTTP/HTTPS scheme
        if parsed_url.scheme in ['http', 'https']:
            urls.add(full_url)

    return list(urls)

# Example usage:
html = """
    <html>
    <body>
        <a href="/about">About Us</a>
        <a href="https://example.com/contact">Contact Us</a>
        <a href="https://google.com">Google</a>
        <a href="mailto:someone@example.com">Email Us</a>
    </body>
    </html>
"""
base_url = "https://example.com"
parsed_urls = parse_links(html, base_url)
for url in parsed_urls:
    print(url)
