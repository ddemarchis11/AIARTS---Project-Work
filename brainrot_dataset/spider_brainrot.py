import scrapy
from pathlib import Path

class ItalianBrainrotAllSpider(scrapy.Spider):
    name = "italian_brainrot_all"
    allowed_domains = ["brainrot.fandom.com"]
    start_urls = ["https://brainrot.fandom.com/wiki/Category:Italian_Brainrot"]

    def parse(self, response):
        # 1. prendo solo gli <a> con la classe del link al titolo
        for href in response.css(
                "li.category-page__member a.category-page__member-link::attr(href)"
            ).getall():
            yield {"link": response.urljoin(href)}

        # 2. gestisco la paginazione
        next_page = response.css("a.category-page__pagination-next::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)