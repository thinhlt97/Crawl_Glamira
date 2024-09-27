import scrapy
import pandas as pd
from urllib.parse import urljoin
import os
class EngagementScrapy(scrapy.Spider):
    name = 'engagement_ring'
    start_urls = [
        'https://www.glamira.com/engagement-rings/']
    image_counter = 0
    
    def parse(self,response):
        for prod in response.css('li.item'):
            prod_id = prod.css('div.product-price-handle div.price-box::attr(data-product-id)').get()
            if prod_id is None:
                pass
            else:
                title = prod.css('a.product-link h2.product-item-details::text').get()
                price = prod.css('span.price-wrapper span.price::text').get()
                img_url = prod.css('img.product-image-photo::attr(src)').get()
                image_name = title.replace(' ','_')
                yield {
                'prod_id': prod_id,
                'title':title,
                'price': price,
                'img_url': img_url,
                'image_name': image_name
                }
                yield scrapy.Request(img_url, callback=self.save_image,errback=self.handle_failure,meta={'image_name':image_name})
        for i in range(2,51):
            next_page = f'https://www.glamira.com/engagement-rings/?p={i}/'
            yield response.follow(next_page, callback = self.parse)
    def save_image(self,response):
        folder = 'image_engagement_ring'
        if not os.path.exists(folder):
            os.makedirs(folder)
        self.image_counter +=1
        image_name = response.meta['image_name']
        image_name = f'{self.image_counter}_{image_name}.jpg'
        image_path = os.path.join(folder,image_name)
        with open (image_path,'wb') as f:
            f.write(response.body)
        self.log(f"Image saved as {image_name}")
    
    def handle_failure(self, failure):
        # Lấy URL bị lỗi từ request
        failed_url = failure.request.url
    
        # Ghi URL lỗi vào file
        with open('failed_urls.txt', 'a') as f:
            f.write(failed_url + '\n')
        # Log lỗi và tiếp tục
        self.log(f"Failed to download {failure.request.url}: {failure.value}", level=scrapy.log.ERROR)