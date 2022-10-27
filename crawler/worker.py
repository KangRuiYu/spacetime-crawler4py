from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time
import custom_logger


class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests from scraper.py"
        super().__init__(daemon=True)
        
    def run(self):
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            scraped_urls = scraper.scraper(tbd_url, resp)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)

        # Log results
        results_logger = custom_logger.get_logger("results")

        # Log number of unique urls
        results_logger.info(f"{len(scraper.sites_seen)} unique urls")

        # Log number of unique page downloads
        results_logger.info(f"{len(scraper.site_hashes)} unique downloads")

        # Log longest page
        results_logger.info(f"{scraper.longest_page_url} is the longest page with {scraper.highest_word_count} words")

        # Log word freqs list
        for word, freq in sorted(scraper.word_freqs.items(), key=lambda x: x[1], reverse=True):
            results_logger.info(f"{word}:{freq}")
