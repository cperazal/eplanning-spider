import scrapy
from scrapy import Request

class EplanningSpider(scrapy.Spider):
    name = 'eplanning_spider'
    allowed_domains = ['eplanning.ie']
    start_urls = ['https://www.eplanning.ie']

    def parse(self, response):
        urls = response.xpath('//a/@href').extract()
        for url in urls:
            if url == '#':
                pass
            else:
                yield Request(url, callback=self.parse_application)

    def parse_application(self, response):
        pass
