from scrapy.crawler import CrawlerProcess

from scrapy.settings import Settings
from parser_order_nn import settings
from parser_order_nn.spiders.order_nn import OrderNnSpider


if __name__ == '__main__':

    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(OrderNnSpider)
    process.start()
