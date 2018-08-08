# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from ..items import BbcSpiderItem
from scrapy.linkextractors import LinkExtractor
import re


class bbcSpider(CrawlSpider):
    name = "cnn"
    allowed_domains = ["cnnespanol.cnn.com"]

    rules = (
        Rule(LinkExtractor(allow=('http://cnnespanol.cnn.com')), callback='parse'),
    )

    start_urls = ["https://cnnespanol.cnn.com/2016/08/30/asesora-de-clinton-se-separa-por-un-nuevo-escandalo-sexual-de-su-marido/"]

    def parse(self, response):
        ps = response.xpath("//div[contains(@class, 'content-body-text')]//p")
        for p in ps:
            texts = p.xpath(".//text()").extract()
            texts = [t.strip() for t in texts]
            sentence = ' '.join(texts)
            item = BbcSpiderItem()
            item['text'] = sentence
            yield item

