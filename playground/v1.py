# fetch all the sites in an event loop
# parse and extract text, media urls and the new webpage/site links from the fetched sites
# then save the site text according to the prescribed format
# then concurrently fetch the media urls and the new sites
# repeat the saving process once the data is obtained
# run this cycle for input level of depth only

config = {
    "sites_and_settings": [
        {
            "url": "https://news.google.com",
            "scrape_media_types": [
                "IMAGES",
                "TEXTS"
            ]
        },
        {
            "url": "https://arxiv.org",
            "scrape_media_types": [
                "IMAGES",
                "VIDEOS",
                "TEXTS",
                "PDFS"
            ]
        },
        {
            "url": "https://new.reddit.com",
            "scrape_media_types": [
                "TEXTS"
            ]
        }
    ]
}

def main():
    pass

if __name__ == "__main__":
    main()
