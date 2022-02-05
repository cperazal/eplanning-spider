import scrapy
from scrapy import Request, FormRequest

class EplanningSpider(scrapy.Spider):
    name = 'eplanning_spider'
    allowed_domains = ['eplanning.ie']
    start_urls = ['https://www.eplanning.ie']

    def parse(self, response):
        urls = response.xpath('//a/@href').extract()
        for url in urls[0:10]:
            if url == '#':
                pass
            else:
                yield Request(url, callback=self.parse_application)

    def parse_application(self, response):
        app_url = response.xpath('//*[@class="glyphicon glyphicon-inbox btn-lg"]/following::a/@href').extract_first()
        yield Request(response.urljoin(app_url), callback=self.parse_form)

    def parse_form(self, response):
        yield FormRequest.from_response(
                                      response,
                                      formdata={'RdoTimeLimit': '28'},
                                      dont_filter=True,
                                      formxpath='(//form)[2]',
                                      callback=self.parse_pages)

    def parse_pages(self, response):
        application_urls = response.xpath('//table//tr//td/a/@href').extract()
        for url in application_urls:
            url = response.urljoin(url)
            yield Request(url, callback=self.parse_items)

        next_page_url = response.xpath("//*[@rel='next']//@href").extract_first()
        next_page_abosolute_url = response.urljoin(next_page_url)
        yield Request(next_page_abosolute_url, callback=self.parse_pages)

    def parse_items(self, response):
        btn_agents = response.xpath("//input[@value='Agents']/@style").extract_first()
        if 'display: inline;  visibility: visible;' in btn_agents:
            name = response.xpath('//tr[th = "Name :"]/td/text()').extract_first()
            address_first = response.xpath('//tr[th = "Address :"]/td/text()').extract()
            address_second = response.xpath('//tr[th = "Address :"]/following-sibling::tr/text()').extract()[0:3]
            address_full = address_first + address_second
            phone = response.xpath('//tr[th = "Phone :"]/td/text()').extract_first()
            fax = response.xpath('//tr[th = "Fax :"]/td/text()').extract_first()
            email = response.xpath('//tr[th = "e-mail :"]/td/a/text()').extract_first()
            url = response.url

            yield {
                'name': name,
                'address': address_full,
                'phone': phone,
                'fax': fax,
                'email': email,
                'url': url
            }

        else:
            self.logger.info('Agent button not found on page')