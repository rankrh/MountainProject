from MountainProject import MPRouteCrawler as crawler
import time

while True:
    try:
        crawler.MPScraper()
    except Exception as error:
        print(error)
        time.sleep(120)