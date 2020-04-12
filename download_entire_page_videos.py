import argparse
import os
from typing import List

from scraper import EMAIL, PASSWORD, extract


def orchestrate_youtube_dl(path: str, links: List[str]):
    for link in links:
        os.system(
            f'{path} --verbose --ignore-errors --id --username {EMAIL} --password {PASSWORD} {link}'
        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Download All Videos From Facebook Page")
    required_parser = parser.add_argument_group("required arguments")
    required_parser.add_argument('--youtube_dl', '-y', help="The path to the local youtube-dl binary", required=True)
    required_parser.add_argument('--fbpage', '-f', help="The complete URL of Facebook page", required=True)
    required_parser.add_argument('--numofposts', '-n', help="The posts to fetch from the page", required=True)

    args = parser.parse_args()

    page_data = extract(args.fbpage, int(args.numofposts))
    post_ids_links = [page_datum.get('PostId') for page_datum in page_data]
    post_ids_links = list(filter(None, post_ids_links))
    orchestrate_youtube_dl(args.youtube_dl, post_ids_links)
