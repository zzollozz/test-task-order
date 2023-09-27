# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import csv
import pandas as pd

from parser_order_nn.settings import FILE_NAME


class ParserOrderNnPipeline:
    def process_item(self, item, spider):
        item['product_name'] = self.process_product_name(item)
        item['product_price'] = self.process_product_price(item)
        item['product_description'] = self.process_product_description(item)
        item['product_characteristic'] = self.process_product_characteristic(item)

        del item['product_characteristic_key']
        del item['product_characteristic_value']

        # self.save_item(item)  # <-- эта хрень не работает как надо
        print(f"==> Обработка продукта: {item['product_name']}")
        return item

    def process_product_name(self, item):
        return item['product_name'][0]

    def process_product_price(self, item):
        return item['product_price'][0].replace(' ', '') if item['product_price'][0] != None else '0'

    def process_product_description(self, item):
        return ','.join(list(map(lambda x: x.replace(u'\xa0', u' '), item['product_description'][0])))

    def process_product_characteristic(self, item):
        for index, value in enumerate(item['product_characteristic_value']):
            item['product_characteristic_value'][index] = value.replace(u'\xa0', u' ')
        return dict(zip(item['product_characteristic_key'], item['product_characteristic_value']))



    def save_item(self, item):
        """
        *** в разработке ***
        Запись item в CSV файл с использованием pandas
        :param item:
        :return:
        """
        data_frame = pd.DataFrame(columns=[item])
        data_frame.to_csv('data.csv')


class CSVPipeline(object):
    """
    Запись item в CSV файл
    """
    def __init__(self):
        self.file = f'{FILE_NAME}.csv'

        with open(self.file, 'r', newline='') as csv_file:
            self.tmp_data = csv.DictReader(csv_file).fieldnames

        self.csv_file = open(self.file, 'a', newline='', encoding='UTF-8')

    def process_item(self, item, spider):
        colums = item.fields.keys()

        data = csv.DictWriter(self.csv_file, colums)
        if not self.tmp_data:
            data.writeheader()
            self.tmp_data = True
        data.writerow(item)
        return item

    def __del__(self):
        self.csv_file.close()

