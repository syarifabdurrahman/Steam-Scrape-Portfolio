# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from w3lib.html import remove_tags  # for cleaning html

# make the list result to one sentence string "Take first"
from scrapy.loader.processors import TakeFirst, MapCompose, Join

from scrapy.selector import Selector


# Cleaning using remove tags
def clean_html(reviews_summary):
    clened_review_summary = ''
    try:
        clened_review_summary = remove_tags(reviews_summary)
    except TypeError:
        clened_review_summary = 'No reviews'

    return clened_review_summary


def get_platform(one_class):
    platforms = []
    platform = one_class.split(' ')[-1]
    if platform == 'win':
        platforms.append('Windows')
    if platform == 'mac':
        platforms.append('Mac os')
    if platform == 'linux':
        platforms.append('Linux')
    if platform == 'vr_supported':
        platforms.append('VR Supported')

    return platforms

 # pricing check when its discount or not


def get_original_price(html_markup):
    original_price = ''
    selector_obj = Selector(text=html_markup)
    div_with_discount = selector_obj.xpath(
        ".//div[contains(@class,'search_price discounted')]")
    if len(div_with_discount) > 0:  # there is discount
        original_price = div_with_discount.xpath(
            ".//span/strike/text()").get()
    else:
        # using normalize-space() to remove \r\n
        original_price = selector_obj.xpath(
            ".//div[contains(@class,'search_price')]/text()").getall()

    return original_price

 # Cleaning discount rate that have '-' before percentage
def clean_discount(discount_rate_percentage):
    if discount_rate_percentage:
        return discount_rate_percentage.lstrip('-')
    return discount_rate_percentage


def clean_discount_price(discounted_price):
    if discounted_price:
        return discounted_price.strip()

    list = discounted_price or "Don\'t have discount price"
    return list


class SteamItem(scrapy.Item):
    item_url = scrapy.Field(
        output_processor=TakeFirst()
    )
    item_image_url = scrapy.Field(
        output_processor=TakeFirst()
    )
    item_name = scrapy.Field(
        output_processor=TakeFirst()
    )
    item_date = scrapy.Field(
        output_processor=TakeFirst()
    )
    item_supported_platforms = scrapy.Field(
        input_processor=MapCompose(get_platform),
    )
    item_reviews = scrapy.Field(
        input_processor=MapCompose(clean_html),
        output_processor=TakeFirst()
    )
    item_regular_price = scrapy.Field(
        input_processor=MapCompose(get_original_price, str.strip),
        output_processor=Join('')

    )
    item_discounted_percentage = scrapy.Field(
        input_processor=MapCompose(clean_discount),
        output_processor=TakeFirst()
    )
    item_discounted_price = scrapy.Field(
        input_processor=MapCompose(clean_discount_price),
        output_processor=TakeFirst()
    )
