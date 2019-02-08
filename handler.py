from MountainProject import MPRouteCrawler as crawler

while True:
    try:
        crawler.MPScraper()
    except Exception as e:
        print(e)