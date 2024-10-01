"""
Generalized Media Scraper
Imagine media ( audio, video, images, pdf,..) are being stored in some websites. We need to create a program such that we can scrape out the entire website targetting ( read more below ) specific set of media, and downloading all of them in the form of ( original_url , actual_stored_file, metadata_text )

Targetting can be done via starting with a single URL or can be done with url pattern matching.

The program should be such that:
one should be able to add websites into it with ease - i.e. almost no code required to scrape through different websites

Automated retries on failure - on full failure, put the failure into error logs

In case of too many failures - abort. Too many failure is an absolute or relative number which are to come from configuration.

Should be able to do it very fast, fastest possible.

There would be server throttling, code against it.

As a test website the following are good examples:
News Sites : https://news.google.com

Celebrity Image Site: https://theplace-2.com

Research Sites: https://arxiv.org

Cross Polinated Social Network : https://new.reddit.com
"""


import os
import re
import json
import asyncio
from datetime import datetime
from urllib.parse import urljoin, urlparse, urlunparse
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import aiohttp
from logging_config import get_logger


class VisitedSites:
    def __init__(self):
        self.visited = set()
        self.lock = asyncio.Lock()

    async def add(self, url):
        async with self.lock:
            self.visited.add(url)

    async def contains(self, url):
        async with self.lock:
            return url in self.visited


class MediaScraper:
    def __init__(self):
        """
        Initialize MediaScraper class, setting up logger and configuration.
        """
        self.logger = get_logger(__name__)
        self.app_config = self.get_app_config()
        self.max_workers = self.app_config["max_workers"]
        self.max_depth = self.app_config["max_depth"]
        self.shared_executor = ThreadPoolExecutor(
            max_workers=self.app_config["max_workers"])
        self.crawl_id = self.get_formatted_timestamp()
        self.visited_sites = VisitedSites()

    def prepare_filename_for_url(self, url):
        # Normalize the URL by removing unsafe characters
        # Replace non-alphanumeric characters with an underscore
        normalized_name = re.sub(r'[^a-zA-Z0-9]', '_', url)

        # Add a timestamp to ensure the filename is unique
        timestamp = self.get_formatted_timestamp()

        # Combine normalized URL and timestamp
        filename = f"{normalized_name}_{timestamp}.txt"

        return filename

    def sanitize_url(self, url):
        # Parse the URL
        parsed_url = urlparse(url)

        # Normalize the scheme and netloc (domain) to be lowercase
        scheme = parsed_url.scheme.lower()
        netloc = parsed_url.netloc.lower()

        # Remove default ports (port 80 for http and port 443 for https)
        if (scheme == 'http' and netloc.endswith(':80')):
            netloc = netloc[:-3]  # Remove ":80"
        elif (scheme == 'https' and netloc.endswith(':443')):
            netloc = netloc[:-4]  # Remove ":443"

        # Normalize the path by removing redundant slashes and trailing slashes
        path = parsed_url.path
        if path != '/':
            path = path.rstrip('/')

        # Rebuild the URL without query string or fragment
        sanitized_url = urlunparse((scheme, netloc, path, '', '', ''))

        return sanitized_url

    def get_app_config(self):
        """
        Parses app config json file and returns python dict
        """
        self.logger.info("Reading app config")
        with open("app_config.json", "r", encoding="utf-8") as config_file:
            config = json.load(config_file)
            return config

    def get_formatted_timestamp(self):
        """
        Returns the current date and time as a formatted string suitable for file names.

        :return: Formatted date and time string without spaces.
        """
        now = datetime.now()
        # Format: YYYYMMDD_HHMMSS
        formatted_timestamp = now.strftime("%Y%m%d_%H%M%S")
        return formatted_timestamp

    async def bulk_add_items_to_queue(self, queue, items):
        for item in items:
            await queue.put(item)

    async def fetch_site_content(self, session, url):
        # Fetch the site
        # TODO :: Implement error handling
        # TODO :: Raise exception for status
        # TODO :: Implement retrial on failure logic
        # TODO :: Implement workaround for server throttling
        # response code 429 - Too many requests, response code 503 - service temporarily unavailable
        # TODO :: Abort operation on too many failures
        # NOTE :: Should we maintain a status on each site_and_settings object? visited_sites is storing urls only not the whole thing... Lets see when the need arrives
        self.logger.info("Fetching %s", url)
        async with session.get(url) as response:
            content_type = response.headers.get("Content-Type", "").lower()
            if 'text/html' in content_type or 'text/plain' in content_type:
                self.logger.info("%s fetched", url)
                return await response.text()
            else:
                self.logger.warning(
                    "NOT SUPPORTED :: Content-Type %s :: URL %s", content_type, url)
                return None

    async def _parse_html(self, html_content, base_url, scrape_media_types, depth):
        self.logger.info("Parsing html")
        soup = BeautifulSoup(html_content, 'html.parser')
        urls_and_settings = set()  # Use a set to avoid duplicate URLs

        # Find all links in the HTML content
        for link in soup.find_all('a', href=True):
            url = self.sanitize_url(link['href'])
            full_url = urljoin(base_url, url)
            parsed_url = urlparse(full_url)
            url_type = "PAGE"

            if await self.visited_sites.contains(full_url):
                continue

            if parsed_url.scheme in ['http', 'https']:
                # Identify downloadable documents
                if url.endswith(('.pdf', '.doc', '.docx', '.ppt', '.pptx')):
                    url_type = "DOCUMENT"
                    self.logger.info("New document url %s found", full_url)
                    urls_and_settings.add((full_url, url_type, depth))

                # Break when we are already at the required max depth level
                elif depth+1 > self.max_depth:
                    continue

                else:
                    self.logger.info("New page url %s found", full_url)
                    urls_and_settings.add((full_url, url_type, depth+1))

        # Find all image sources
        if "IMAGE" in scrape_media_types:
            for img in soup.find_all('img', src=True):
                img_url = img['src']
                full_img_url = urljoin(base_url, img_url)
                self.logger.info("New image url %s  found", full_img_url)
                urls_and_settings.add((full_img_url, "IMAGE", depth))

        # Find all video sources
        if "VIDEO" in scrape_media_types:
            for video in soup.find_all('video', src=True):
                video_url = video['src']
                full_video_url = urljoin(base_url, video_url)
                self.logger.info("New video url %s  found", full_video_url)
                urls_and_settings.add((full_video_url, "VIDEO", depth))

        # Find all audio sources
        if "AUDIO" in scrape_media_types:
            for audio in soup.find_all('audio', src=True):
                audio_url = audio['src']
                full_audio_url = urljoin(base_url, audio_url)
                self.logger.info("New audio url %s  found", full_audio_url)
                urls_and_settings.add((full_audio_url, "AUDIO", depth))

        # Extract text content from the HTML
        parsed_text = soup.get_text(separator='\n', strip=True)

        self.logger.info("HTML parsed")

        return [
            {
                "url": url,
                "type": type,
                "depth": depth,
                **({"scrape_media_types": scrape_media_types} if type == "PAGE" else {})
            }
            for (url, type, depth) in urls_and_settings
        ], parsed_text

    async def parse_html(self, html_content, base_url, scrape_media_types, depth):
        result = await asyncio.get_running_loop().run_in_executor(
            self.shared_executor, self._parse_html, html_content, base_url, scrape_media_types, depth)
        return result

    def _save_file(self, content, filename, is_text):
        self.logger.info("Saving file %s", filename)
        base_directory = os.path.join("downloads", self.crawl_id)
        os.makedirs(base_directory, exist_ok=True)
        file_path = os.path.join(base_directory, filename)

        # Set the file open mode and encoding based on whether it's text or binary
        mode = 'w' if is_text else 'wb'
        encoding = 'utf-8' if is_text else None

        # Open and write the content based on the type
        with open(file_path, mode, encoding=encoding) as file:
            file.write(content)

        self.logger.debug("File %s saved", file_path)
        return file_path

    async def save_file(self, content, filename, is_text=True):
        file_path = await asyncio.get_running_loop().run_in_executor(self.shared_executor, self._save_file, content, filename, is_text)
        return file_path

    async def worker(self, worker_id, queue, session):
        self.logger.info("Worker %s spawned", worker_id)
        while True:
            # Obtain a new task
            site_and_settings = await queue.get()

            self.logger.info("Worker %s picked task %s",
                             worker_id, site_and_settings)

            try:
                url = site_and_settings["url"]
                url_type = site_and_settings["type"]
                depth = site_and_settings["depth"]

                # Ensure that the url is not already visited
                # NOTE :: We can do this check at the time of adding the url to the task queue itself
                if not await self.visited_sites.contains(url):
                    await self.visited_sites.add(url)

                    # NOTE :: This the url type can be inferred from the response content type
                    if url_type == "PAGE":
                        scrape_media_types = site_and_settings["scrape_media_types"]

                        # Fetch the page
                        html_content = await self.fetch_site_content(session, url)
                        if html_content:
                            # parse and extract the new urls contained in the site
                            urls_and_settings, text = await self.parse_html(
                                html_content, url, scrape_media_types, depth)

                            # Add newly obtained links to the queue
                            await self.bulk_add_items_to_queue(queue, urls_and_settings)

                            # Dump the text content to a file
                            await self.save_file(text, self.prepare_filename_for_url(url))

                    elif url_type == "IMAGE":
                        self.logger.debug(
                            "%s download not supported yet", url_type)

                    elif url_type == "VIDEO":
                        self.logger.debug(
                            "%s download not supported yet", url_type)

                    elif url_type == "AUDIO":
                        self.logger.debug(
                            "%s download not supported yet", url_type)

                    elif url_type == "DOCUMENT":
                        self.logger.debug(
                            "%s download not supported yet", url_type)

            except Exception as exc:
                self.logger.exception("Worker exception")

            finally:
                queue.task_done()

            self.logger.info("Task %s completed", site_and_settings)

    async def run(self):
        """
        App entry point
        """
        # Obtain raw seed sites and settings and prep for task queue
        sites_and_settings = [{"depth": 1, **site_and_settings, "url": self.sanitize_url(
            site_and_settings["url"])} for site_and_settings in self.app_config["sites_and_settings"]]

        # Init a task queue
        queue = asyncio.Queue()
        await self.bulk_add_items_to_queue(queue, sites_and_settings)

        # Create the workers
        async with aiohttp.ClientSession() as session:
            workers = [asyncio.create_task(self.worker(i, queue, session))
                       for i in range(self.max_workers)]

            # Wait for all the tasks in the queue to be processed
            await queue.join()

            # Cancel the workers
            for worker in workers:
                worker.cancel()

            # Await clean cancellation
            await asyncio.gather(*workers)


if __name__ == "__main__":
    scraper = MediaScraper()
    asyncio.run(scraper.run())
