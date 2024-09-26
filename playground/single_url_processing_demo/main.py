"""
Lets try to fetch and process only a single url
"""
import logging
from datetime import datetime
import requests

# setup logger
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('single_url_processing_script.log', mode='w')
    ]
)

logger = logging.getLogger("single_url_processing_script")


def get_formatted_timestamp():
    """
    Returns the current date and time as a formatted string suitable for file names.
    
    :return: Formatted date and time string without spaces.
    """
    now = datetime.now()
    # Format: YYYYMMDD_HHMMSS
    formatted_timestamp = now.strftime("%Y%m%d_%H%M%S")
    return formatted_timestamp


# main code
def main():
    """
    Demonstrate the operations (fetching, parse, extracing and saving the contents of the site) on a single url
    """
    url = "https://news.google.com"

    # fetch the site data
    try:
        response = requests.get(url)
        response.raise_for_status()
        logger.debug("url fetched")
    # except requests.exceptions.ConnectTimeout:
    #     # NOTE :: retry
    #     pass
    except Exception as exc:
        msg = f"Failed to fetch the site {url}"
        logger.error(msg, exc_info=True)
        raise Exception(msg) from exc

    # check content type inorder to process the site accordingly
    content_type = response.headers.get("Content-Type", "").lower()

    # parse and prepare response
    if 'application/json' in content_type:
        try:
            json_data = response.json()

            return json_data
        except ValueError as exc:
            msg = f"Failed to parse json response for url {url}"
            logger.error(msg, exc_info=True)
            raise Exception(msg) from exc
    elif 'text/html' in content_type or 'text/plain' in content_type:
        html_content = response.text
        # NOTE :: parse the html content and obtain other text, other urls
        # NOTE :: out of other urls, identify the html pages and other media urls (audio, video, document)
        # NOTE :: download the medias in the current scope, create a new scope/context and process the other page urls

        return html_content
    elif 'application/xml' in content_type or 'text/xml' in content_type:
        xml_content = response.content

        return xml_content
    else:
        logger.warning(f"Unknown content type: {content_type}")
        print(f"Unknown content type: {content_type}")

    # parse the content and extract the text and urls from it
    # parse content based on the response type,

    # text can be directly stored at this point

    # urls need to be fetch agains, depending on mime type, either they are media urls or website/webpage urls again
    # if media urls then download them and save them along side the text and if website/webpage urls then we will have to call fetch them again and repeat the above cycle until we do this in some input n level depths


if __name__ == "__main__":
    main()
