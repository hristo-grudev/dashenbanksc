import scrapy

from scrapy.loader import ItemLoader

from ..items import DashenbankscItem
from itemloaders.processors import TakeFirst


class DashenbankscSpider(scrapy.Spider):
	name = 'dashenbanksc'
	start_urls = ['https://dashenbanksc.com/press-releases/']

	def parse(self, response):
		post_links = response.xpath('//article//article')
		for post in post_links:
			url = post.xpath('.//div[@class="post-content"]/a/@href').get()
			date = post.xpath('.//span[@class="published"]/text()').get()
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date})

		next_page = response.xpath('/@href').getall()
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response, date):
		title = response.xpath('//h1/text()').get()
		description = response.xpath('(//div[@class="et_pb_text_inner"])[1]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()

		item = ItemLoader(item=DashenbankscItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
