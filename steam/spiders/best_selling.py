# data processing dont do in this script

import scrapy
import json
from scrapy.loader import ItemLoader
from scrapy.selector import Selector
from ..items import SteamItem

class BestSellingSpider(scrapy.Spider):
    name = 'best_selling'
    allowed_domains = ['store.steampowered.com']

    records_number = 0

    handle_httpstatus_list = [555]

    def start_requests(self):
        yield scrapy.Request(
            url=f'https://store.steampowered.com/search/results/?query&start={self.records_number}&count=50&dynamic_data=&sort_by=_ASC&snr=1_7_7_7000_7&filter=topsellers&infinite=1',
            headers={
                'X-Prototype-Version': '1.7',
                'X-Requested-With': 'XMLHttpRequest',
            },
            method='GET',
            cookies={
                'browserid':'3001119256047957485', 
                'sessionid':'91338ada627670a380fee9f5',
                'steamCountry':'ID%7C1ec3e2eaca6a5c04b9eb1f1a181c20c9'
            },
            callback=self.parse,
        )

    def parse(self, response):
        json_load = json.loads(response.body)
        html_data = json_load['results_html']
        all_game = Selector(text=html_data)

        # with open('index.html',mode='w') as file:
        #     file.write(html_data)

        games = all_game.xpath("//a[@data-gpnav='item']")

        # steam_item = SteamItem()

        for game in games:
            loader = ItemLoader(item=SteamItem(),selector = game,response=response)
            loader.add_xpath('item_url',".//@href")
            loader.add_xpath('item_image_url',".//div[@class='col search_capsule']/img/@src")
            loader.add_xpath('item_name',".//span[@class='title']/text()")
            loader.add_xpath('item_date',".//div[@class='col search_released responsive_secondrow']/text()")
            loader.add_xpath('item_supported_platforms',".//span[contains(@class,'platform_img') or @class='vr_supported']/@class")
            loader.add_xpath('item_reviews',".//span[contains(@class,'search_review_summary')]/@data-tooltip-html")
            loader.add_xpath('item_discounted_percentage',".//div[contains(@class,'search_discount')]/span/text()")
            loader.add_xpath('item_regular_price',".//div[contains(@class,'search_price_discount_combined')]")
            loader.add_xpath('item_discounted_price',"(.//div[contains(@class,'search_price discounted')]/text())[2]")

            yield loader.load_item()

            # steam_item['item_url'] = game.xpath(".//@href").get()
            # steam_item['item_image_url'] = game.xpath(".//div[@class='col search_capsule']/img/@src").get()
            # steam_item['item_name'] = game.xpath(".//span[@class='title']/text()").get()
            # steam_item['item_date'] = game.xpath(".//div[@class='col search_released responsive_secondrow']/text()").get()
            # steam_item['item_supported_platforms'] = self.get_platform(game.xpath(".//span[contains(@class,'platform_img') or @class='vr_supported']/@class").getall())
            # steam_item['item_reviews'] = self.clean_html(game.xpath(".//span[contains(@class,'search_review_summary')]/@data-tooltip-html").get())
            # steam_item['item_discounted_percentage'] = self.clean_discount(game.xpath(".//div[contains(@class,'search_discount')]/span/text()").get())
            # steam_item['item_regular_price'] = self.get_original_price(game.xpath(".//div[contains(@class,'search_price_discount_combined')]"))
            # steam_item['item_discounted_price'] = self.clean_discount_price(game.xpath(".//div[contains(@class,'search_price discounted')]/text()").getall())

            # steam_item['item_discounted_price'] = 
            # yield steam_item

        #Pagination
        total_page = json_load['total_count']
        increment_by = 50

        if self.records_number <= total_page:
            print(self.records_number)
            self.records_number+=increment_by
            new_url = f'https://store.steampowered.com/search/results/?query&start={self.records_number}&count=50&dynamic_data=&sort_by=_ASC&snr=1_7_7_7000_7&filter=topsellers&infinite=1'

            yield scrapy.Request(
                url=new_url,
                headers={
                        'X-Prototype-Version': '1.7',
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                method='GET',
                callback=self.parse
                )