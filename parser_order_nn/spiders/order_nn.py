import scrapy
from scrapy.http import HtmlResponse

from parser_order_nn.items import ParserOrderNnItem
from parser_order_nn.settings import FILE_NAME


class OrderNnSpider(scrapy.Spider):
    name = "order_nn"
    allowed_domains = ["order_nn.ru"]
    start_urls = ["https://order-nn.ru/kmo/catalog/"]
    custom_settings = {'FEED_URI': f"./{FILE_NAME}.json",
                       'FEED_FORMAT': 'json'}

    def parse(self, response):
        temp_main_cat = dict(zip(
            response.xpath("//div[@class='sections-block-level-2-item']/a/text()").getall(),
            response.xpath("//div[@class='sections-block-level-2-item']/a/@href").getall()
        ))
        for key, value in temp_main_cat.items():
            match key:
                case 'Краски и материалы специального назначения':
                    yield response.follow(url=self.req_url(value),
                                          callback=self.parse_get_products,
                                          dont_filter=True
                                          )
                case 'Краски для наружных работ':
                    yield response.follow(url=self.req_url(value),
                                          callback=self.parse_get_products,
                                          dont_filter=True
                                          )
                case 'Лаки':
                    yield response.follow(url=self.req_url(value),
                                          callback=self.parse_get_products,
                                          dont_filter=True
                                          )

    def parse_get_products(self, response: HtmlResponse):
        next_page = response.xpath("//li[@class='active']/following::li/a/text()").get()


        if int(next_page) > self.old_page(response):
            yield response.follow(f"{response.url.split('?')[0]}?PAGEN_1={next_page}",
                                  callback=self.parse_get_products,
                                  dont_filter=True,
                                  )

        links = response.xpath("//div[@class='horizontal-product-item-block_3_2']/a/@href").getall()
        for link in links:
            yield response.follow(url=self.req_url(link),
                                  callback=self.parse_data_product,
                                  dont_filter=True,
                                  )

    def parse_data_product(self, response: HtmlResponse):

        product_name = response.xpath("//h1[@itemprop='name']/text()").get(),
        product_price = response.xpath("//span[@class='element-current-price-number']/text()").get(),
        product_description = response.xpath("//div[@class='tab-pane active']//p/text()").getall(),

        yield scrapy.FormRequest(url='https://order-nn.ru/local/ajax/kmo/getCharacterItems.php',
                                 method='POST',
                                 dont_filter=True,
                                 formdata={'type': 'character',
                                           'style': 'element',
                                           'items': response.url.split('/')[-1]},
                                 callback=self.parse_product_characteristic,
                                 cb_kwargs={'product_name': product_name,
                                            'product_price': product_price,
                                            'product_description': product_description}
                                 )

    def parse_product_characteristic(self, response: HtmlResponse, **kwargs):

        yield ParserOrderNnItem(
            product_name=kwargs.get('product_name'),
            product_price=kwargs.get('product_price'),
            product_description=kwargs.get('product_description'),
            product_characteristic_key=response.selector.xpath("//td[@class='table-character-text']/text()").getall(),
            product_characteristic_value=response.selector.xpath("//td[@class='table-character-value']/text()").getall()
        )

    @staticmethod
    def req_url(url):
        return f"https://order-nn.ru{url}"

    @staticmethod
    def old_page(response):
        """
        Вычисление текущей страницы
        :param response:
        :return: int
        """
        number = response.url.split('=')[-1]
        if number.isdigit():
            return int(number)
        else:
            return 1
