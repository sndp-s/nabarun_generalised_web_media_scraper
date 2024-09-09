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

import json
from logging_config import get_logger


logger = get_logger(__name__)


def get_app_config():
    """
    Parses app config json file and returns python dict
    """
    logger.info("Reading app config")
    with open("app_config.json", "r", encoding="utf-8") as config_file:
        config = json.load(config_file)
        return config


def fetch_site(url):
    pass


def main():
    """
    App entry point
    """
    app_config = get_app_config()
    sites_and_settings = app_config["sites_and_settings"]

    for details in sites_and_settings:
        url = details["url"]
        scrape_media_types = details["scrape_media_types"]

        # fetch site
        site = fetch_site(url)

        # parse the required media out of the fetched site data


if __name__ == "__main__":
    main()
