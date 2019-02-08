# -*- coding: utf-8 -*-
import scrapy
import re
from copy import deepcopy 


class SuningSpider(scrapy.Spider):
    name = 'suning'
    allowed_domains = ['suning.com']
    start_urls = ['https://book.suning.com/']

    def parse(self, response):
          #大分类
        li_lists=response.xpath("//div[@class='menu-list']//div[@class='menu-item']")

        for li in li_lists:
            item={}
            #大分类
            item['b_type']=li.xpath("./dl/dt/h3/a/text()").extract_first()
            #小分类
            s_lists=li.xpath("./dl/dd/a")
            for s_list in s_lists:
                item['s_type']=s_list.xpath("./text()").extract_first()
                item['s_href']=s_list.xpath("./@href").extract_first()
                if item['s_href']!=None:
                    yield scrapy.Request(
                        item['s_href'],
                        callback=self.parse_book_list,
                        meta={"item":deepcopy(item)}
                        )
    
    #图书列表详情
    def parse_book_list(self,response):
        item=response.meta["item"]
        #图书列表
        #print(response.xpath("//div[@id='filter-results']//ul/li//div[@class='img-block']/a/img/@src"))
        book_list=response.xpath("//div[@id='filter-results']//ul/li")
        for book in book_list:
            item['book_title']=book.xpath("//div[@class='res-info']/p[2]/a/text()").extract_first().replace("\n","")
            item['book_href']='https:'+book.xpath("//div[@class='res-img']/div[@class='img-block']/a/@href").extract_first()
            yield scrapy.Request(
                item['book_href'],
                callback=self.parse_book_detail,
                meta={"item":deepcopy(item)}
                )

            #下一页地址
        if len(re.findall("param.currentPage = \"(.*?)\";",response.body.decode())) and len(re.findall("param.pageNumbers = \"(.*?)\";",response.body.decode())):
            currentPage=int(re.findall("param.currentPage = \"(.*?)\";",response.body.decode())[0])
            pageNumbers=int((re.findall("param.pageNumbers = \"(.*?)\";",response.body.decode())[0]))
            if currentPage<pageNumbers:
                next_href="https://list.suning.com/1-502320-{}-0-0-0-0-14-0-4.html".format(currentPage+1)
                yield scrapy.Request(
                    next_href,
                    callback=self.parse_book_list,
                    meta={'item':response.meta['item']}
                    )
                
    #每本图书的详细情况
    def parse_book_detail(self,response):
        item=response.meta['item']
        item['book_img']='https:'+response.xpath("//a[@id='bigImg']/img/@src").extract_first()
        item['book_writer']=response.xpath("//div[@class='proinfo-main']/ul/li[1]/text()").extract_first()
        if item['book_writer']:
            item['book_writer']=re.sub("\r*\t*\n*",'',item['book_writer']).replace(" ",'')
        with open("t.txt",'a') as f:
            f.write(str(item))
            f.write("\n")