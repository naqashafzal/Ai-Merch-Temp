# src/website_analyzer.py

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import colorgram

class WebsiteAnalyzer:
    """Handles all website scraping and asset extraction."""
    def __init__(self, url):
        if not url.startswith('http://') and not url.startswith('https://'):
            self.url = 'https://' + url
        else:
            self.url = url
        self.soup = None
        self.domain = urlparse(self.url).netloc
        self.assets_dir = os.path.join('assets', self.domain)
        os.makedirs(self.assets_dir, exist_ok=True)

    def fetch_and_parse_html(self):
        # ... (This method remains the same) ...
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(self.url, headers=headers, timeout=20)
            response.raise_for_status()
            self.soup = BeautifulSoup(response.text, 'html.parser')
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL {self.url}: {e}")
            return False

    def get_logo(self):
        """
        Finds and downloads the most likely logo from the website.
        ENHANCED: Includes more selectors and a fallback to find favicons.
        """
        if not self.soup: return None

        # --- 1. Attempt to find the main logo ---
        
        # More comprehensive list of selectors
        logo_selectors = [
            'a[href="/"] img[src*="logo"]', 'img[class*="logo"]', 'img[id*="logo"]',
            'img[alt*="logo" i]', 'img[src*="logo"]', 'a[aria-label*="logo" i] img',
            'a[class*="logo"] img', 'header img',
        ]

        for selector in logo_selectors:
            logo_img = self.soup.select_one(selector)
            if logo_img and logo_img.get('src'):
                logo_path = self._download_image(logo_img['src'], "logo")
                if logo_path: return logo_path # Return the first one we successfully download
        
        # --- 2. Fallback: Attempt to find a high-quality favicon ---
        
        favicon_selectors = [
            'link[rel="apple-touch-icon"]', 'link[rel="icon"]',
            'link[rel="shortcut icon"]'
        ]

        for selector in favicon_selectors:
            favicon_link = self.soup.select_one(selector)
            if favicon_link and favicon_link.get('href'):
                # Prioritize larger icons if size is specified
                sizes = favicon_link.get('sizes')
                if sizes and '180x180' not in sizes and '32x32' not in sizes:
                    continue # Skip low-res favicons if better ones might exist
                
                logo_path = self._download_image(favicon_link['href'], "favicon_logo")
                if logo_path: return logo_path

        return None # Return None if nothing is found

    def _download_image(self, src, filename_prefix):
        """Helper function to download an image from a source URL."""
        try:
            # Construct absolute URL and handle URL decoding
            image_url = urljoin(self.url, unquote(src))
            
            logo_response = requests.get(image_url, stream=True, timeout=10)
            logo_response.raise_for_status()

            # Determine a valid file extension
            file_extension = os.path.splitext(urlparse(image_url).path)[1].lower() or '.png'
            if file_extension not in ['.png', '.jpg', '.jpeg', '.svg', '.gif', '.ico']: file_extension = '.png'
            
            image_path = os.path.join(self.assets_dir, f"{filename_prefix}{file_extension}")
            
            with open(image_path, 'wb') as f:
                for chunk in logo_response.iter_content(1024): f.write(chunk)
            
            # Verify the image is valid (but skip for SVGs)
            if file_extension != '.svg': Image.open(image_path).verify()
            
            print(f"Successfully downloaded asset: {image_url}")
            return image_path
        except Exception as e:
            print(f"Could not download image from {src}: {e}")
            return None

    def capture_screenshot(self):
        # ... (This method remains the same) ...
        screenshot_path = os.path.join(self.assets_dir, "screenshot.png")
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--hide-scrollbars")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        try:
            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
            driver.get(self.url)
            driver.save_screenshot(screenshot_path)
            driver.quit()
            return screenshot_path
        except Exception as e:
            print(f"Error capturing screenshot: {e}")
            return None

    def get_brand_colors(self, image_path, num_colors=6):
        # ... (This method remains the same) ...
        if not os.path.exists(image_path) or image_path.endswith('.svg'): return []
        try:
            colors = colorgram.extract(image_path, num_colors)
            return [f'#{c.rgb.r:02x}{c.rgb.g:02x}{c.rgb.b:02x}' for c in colors if c.proportion > 0.02]
        except Exception as e:
            print(f"Could not extract colors from image {image_path}: {e}")
            return []