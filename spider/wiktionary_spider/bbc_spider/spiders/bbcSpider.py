# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import Spider, Rule
from ..items import BbcSpiderItem
from scrapy.linkextractors import LinkExtractor
import re

vocab = "/Users/lizhen/KikaCode/mix_engine/vocab/en_US_unigram_2w"
f = open(vocab, "r")
raw_words = list()
for line in f:
    word, count = line.strip().split()
    raw_words.append(word)
print("vocab size =", len(raw_words))


class bbcSpider(Spider):
    name = "wiktionary_es_verb"
    allowed_domains = ["en.wiktionary.org"]

    # rules = (
    #     # Rule(LinkExtractor(allow=('https://en.wiktionary.org/w/index.php\\?title=Category:Spanish_verbs_ending_in_')), callback='parse_verb_list'),
    #     Rule(LinkExtractor(allow=('https://en.wiktionary.org/wiki/[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]+')), callback='parse_verb_page'),
    # )
    words = raw_words
    url = "https://en.wiktionary.org/wiki/"

    id = 0
    start_urls = [url + str(words[id])]

    def parse(self, response):
        ps1 = response.xpath("//div[@class='mw-parser-output']//div[@class='toc']//"
                            "li[contains(@class,'toclevel-1')]/a/span[@class='toctext']//text()").extract()
        ps1_word = response.xpath("//h1[@class='firstHeading']//text()").extract()

        ps2 = response.xpath("//div[@class='mw-parser-output']//"
                            "h2/span[@class='mw-headline']//text()").extract()
        ps2_word = response.xpath("//h1[@id='section_0']//text()").extract()

        print("num of words in ps1: %d ; ps2: %d" % (len(ps1), len(ps2)))
        item = BbcSpiderItem()
        if len(ps1) > 0:
            item['languages'] = '\t'.join(ps1).encode('utf-8')

        elif len(ps2) > 0:
            item['languages'] = '\t'.join(ps2).encode('utf-8')

        else:
            item['languages'] = "Language Not Found".encode('utf-8')

        if len(ps1_word) > 0:
            item['word'] = ps1_word[0].encode('utf-8')
        elif len(ps2_word) > 0:
            item['word'] = ps2_word[0].encode('utf-8')
        else:
            item['word'] = "Word Not Found".encode('utf-8')

        yield item

        for word in self.words[1:]:
            yield scrapy.Request("https://en.wiktionary.org/wiki/" + str(word), callback=self.parse)

    # def parse_verb_list(self, response):
    #     # print("parse_verb_list----------------------------------------------------")
    #     # ps = response.xpath("//div[@class='mw-pages']//div[@class='mw-content-ltr']")
    #     ps = response.xpath("//div[@id='mw-pages']//div[@class='mw-content-ltr']//li//a/@href").extract()
    #     for p in ps:
    #         yield scrapy.Request('https://en.wiktionary.org' + p, callback=self.parse_verb_page)
    #     ps = response.xpath("//div[@id='mw-pages']/a/@href").extract()
    #     for p in ps:
    #         # page_url = p.xpath("./@href").extract()
    #         yield scrapy.Request('https://en.wiktionary.org' + p, callback=self.parse_verb_list)















