from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import HtmlResponse
from bs4 import BeautifulSoup

class DesktopBgSpider(CrawlSpider):
    name = 'desktop_crawler'
    allowed_domains = ['desktop.bg']
    start_urls = ['https://desktop.bg/computers-all']

    rules = (
        Rule(LinkExtractor(allow=r'https://desktop.bg/computers-[a-zA-Z0-9_-]+$'), callback='parse_computer', follow=True),
        Rule(LinkExtractor(restrict_css='div.pagination > a[rel="next"]'), follow=True)
    )

    def parse_computer(self, response: HtmlResponse):
        product_parser = BeautifulSoup(response.body, "html.parser")

        ram_option = "-"
        ram_tr = product_parser.find("tr", class_="DesktopRam attached", id="DesktopRam")

        if ram_tr:
            span_val = ram_tr.find("div", class_="default-option options").find("label").find("span")
            if span_val:
                ram_option = span_val.text.strip()

        parse_table = product_parser.find("table", class_="product-characteristics")

        if parse_table:
            rows = parse_table.find_all("tr")
            tds = [td for row in rows for td in row.find_all("td")]

            def extract_first(td):
                div_option = td.find("div", class_="default-option options")
                if div_option:
                    label_option = div_option.find("label", class_="with-thumb")
                    if label_option:
                        span_val = label_option.find("span")
                        if span_val:
                            return span_val.text.strip()
                return td.text.strip()

            if len(tds) >= 8:
                yield {
                    'URL': response.url,
                    'Motherboard': extract_first(tds[5]),
                    'CPU': extract_first(tds[6]),
                    'GPU': extract_first(tds[7]),
                    'RAM': ram_option
                }