import scrapy
import pandas as pd
from urllib.parse import urljoin
import os
class DiamondRingScrapy(scrapy.Spider):
    name = 'diamond_ring'
    start_urls = [
        'https://www.glamira.com/diamond-rings/']
    image_counter = 0 # Tạo hàm đếm để xếp số thứ tự cho ảnh
    
    def parse(self,response):
        for prod in response.css('li.item'):
            prod_id = prod.css('div.product-price-handle div.price-box::attr(data-product-id)').get()
            if prod_id is None: # Nếu ảnh đó không có product id thì không lấy
                pass
            else:
                title = prod.css('a.product-link h2.product-item-details::text').get() # Lấy tên sản phầm
                price = prod.css('span.price-wrapper span.price::text').get() # Giá sản phẩm
                img_url = prod.css('img.product-image-photo::attr(src)').get() #link ảnh sản phẩm
                image_name = title.replace(' ','_') # thay dấu khoảng trắng bằng dấu _ để đặt tên ảnh
                # in nội dung ra màn hình và lưu vào file csv
                yield {
                'prod_id': prod_id,
                'title':title,
                'price': price,
                'img_url': img_url,
                'image_name': image_name
                }
                #Gọi hàm save_image để lưu ảnh
                yield scrapy.Request(img_url, callback=self.save_image,errback=self.handle_failure,meta={'image_name':image_name})
        #Sản phẩm diamond ring có 120 nên cho chạy vòng lặp 120 lần
        for i in range(2,121):
            next_page = f'https://www.glamira.com/diamond-rings/?p={i}/'
            yield response.follow(next_page, callback = self.parse)
    #Hàm lưu ảnh
    def save_image(self,response):
        folder = 'image_diamond_ring'
        if not os.path.exists(folder):
            os.makedirs(folder)
        self.image_counter +=1
        image_name = response.meta['image_name']
        #image_name = response.url.split('/')[-1]
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