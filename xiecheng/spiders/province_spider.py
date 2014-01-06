#coding:utf-8
import MySQLdb
from scrapy.http import Request
from scrapy.selector import Selector
from scrapy.spider import BaseSpider
import re
conn=MySQLdb.connect(host='54.201.192.244',user='qyer',passwd='qyer',db='mafengwo',port=3306,charset='utf8')
cur=conn.cursor()
class province_spider(BaseSpider):
    name = "province"
    start_urls = ['http://you.ctrip.com/place/',]
    allowed_domains = ['you.ctrip.com']

    def parse(self, response):
        hxs = Selector(response)
        sites = hxs.xpath('//div[@id="Main_countrylist"]/div[@class="item"]/ul[@class="cf"]/li')
        #crawl province urls and names ,
        #then post prov_url、prov_name to parse_city() method to get city_urls、city_names
        page = 1
        poi_page = 1
        for site in sites[:20]:
            prov_url = site.xpath('a/@href').extract()[0].replace('/place/','').replace('.html','')
            prov_name = site.xpath('a/text()').extract()[0]
            ####print prov_name
            if prov_url not in ('/place/beijing1.html','/place/shanghai2.html'):
#                省级需要获取城市urls
                ####print prov_url,prov_name
                yield Request(url='http://you.ctrip.com/countrysightlist/%s/p%s.html'%(prov_url,page),\
                    callback = self.parse_city,meta={'prov_url':prov_url,'prov_name':prov_name,'page':page})
            else:
                #直辖市直接获取poi_urls
                for func in ([self.parse_sightlist_poi_urls,'sightlist'],[self.parse_restaurantlist_poi_urls,'restaurantlist'],\
                             [self.parse_shoppinglist_poi_urls,'shoppinglist'],[self.parse_resortlist_poi_urls,'resortlist']):
                    yield Request(url = 'http://you.ctrip.com/%s/%s/s0-p%s.html'%(func[1],prov_url,poi_page),callback = func[0],\
                        meta={'prov_url':prov_url,'prov_name':prov_name,'poi_page':poi_page,'is_province':0,'city_url':prov_url})
#        页面中抓不到，手动添加的一些省份
        hand_add_province = (('heilongjiang100055',u'黑龙江'),('jilin100031',u'吉林'),('liaoning100061',u'辽宁'),('hebei100059',u'河北'),('shandong100039',u'山东'),('qinghai100032',u'青海'),\
         ('guizhou100064',u'贵州'),('hubei100067',u'湖北'),('anhui100068',u'安徽'),('henan100058',u'河南'),('ningxia100063',u'宁夏'),('jiangxi100054',u'江西'))
        for prov in hand_add_province:
            yield Request(url='http://you.ctrip.com/countrysightlist/%s/p%s.html'%(prov[0],page),\
                callback = self.parse_city,meta={'prov_url':prov[0],'prov_name':prov[1],'page':page})
#        处理页面中抓不到的两个直辖市，然后crawl poi_urls
        for func in ([self.parse_sightlist_poi_urls,'sightlist'],[self.parse_restaurantlist_poi_urls,'restaurantlist'],\
                 [self.parse_shoppinglist_poi_urls,'shoppinglist'],[self.parse_resortlist_poi_urls,'resortlist']):
            yield Request(url = 'http://you.ctrip.com/%s/chongqing158/s0-p%s.html'%(func[1],poi_page),callback = func[0],\
                meta={'prov_url':'chongqing158','prov_name':u'重庆','poi_page':poi_page,'is_province':0,'city_url':'chongqing158'})
            yield Request(url='http://you.ctrip.com/%s/tianjin154/s0-p%s.html'%(func[1],poi_page), callback = func[0],\
                meta={'prov_url':'tianjin154','prov_name':u'天津','poi_page':poi_page,'is_province':0,'city_url':'tianjin154'})
        #调试用
#        yield Request(url='http://you.ctrip.com/resortlist/beijing1/s0-p1.html',\
#            callback = self.parse_resortlist_poi_urls, meta={'prov_url':'shaanxi100057',\
#                    'prov_name':u'北京','page':page,'city_url':'beijing01','poi_page':poi_page,'is_province':0})
    def parse_city(self,response):
        #crawl city urls and names to get poi_urls and poi_names
        hxs = Selector(response)
        prov_url = response.meta['prov_url']
        prov_name = response.meta['prov_name']
        page = response.meta['page']
        sites = hxs.xpath('//div[@class="citysight_list"]/div[@class="csingle_sight"]')
        max_page = 1
        #如果有城市列表才continue crawling
        if sites:
            #获取最大分页数
            if hxs.xpath('//div[@class="pager cf"]/div[@class="nav"]/a[last()-1]/text()').extract():
                max_page = hxs.xpath('//div[@class="pager cf"]/div[@class="nav"]/a[last()-1]/text()').extract()[0]
            rank =(page-1)*10+1
            for site in sites:
                city_name = site.xpath('div/span/text()').extract()[0]
                city_url = site.xpath('div/a/@href').extract()[0].replace('/place/','').replace('.html','')
                city_rank = rank
                ####print city_name,city_url,city_rank
                #get poi_urls
                poi_page = 1
                for func in ([self.parse_sightlist_poi_urls,'sightlist'],[self.parse_restaurantlist_poi_urls,'restaurantlist'],\
                             [self.parse_shoppinglist_poi_urls,'shoppinglist'],[self.parse_resortlist_poi_urls,'resortlist']):
                    yield Request(url = 'http://you.ctrip.com/%s/%s/s0-p%s.html'%(func[1],city_url,poi_page),callback = func[0],meta={'prov_url':\
                        prov_url,'prov_name':prov_name,'city_url':city_url,'city_name':city_name,'city_rank':city_rank,'poi_page':poi_page,'is_province':1})
                rank = rank +1
        page = page + 1
        #callback selfmethod  to crawl next page
        if page <= int(max_page):
            yield Request(url='http://you.ctrip.com/countrysightlist/%s/p%s.html'%(prov_url,page), \
                callback = self.parse_city,meta={'prov_url':prov_url,'prov_name':prov_name,'page':page})

    #获取所有该城市下景点poi urls
    def parse_sightlist_poi_urls(self,response):
        hxs = Selector(response)
        prov_url = response.meta['prov_url']
        prov_name = response.meta['prov_name']
        is_province = response.meta['is_province']
        city_name = city_rank = city_url = ''
        city_url = response.meta['city_url']
        if is_province:
            city_name = response.meta['city_name']
            city_rank = response.meta['city_rank']
        poi_page = response.meta['poi_page']
        sites = hxs.xpath('//div[@class="city_picsight_list"]/div[@class="cpic_sight"]')
        max_page = 1
        #如果有城市列表才continue crawling
        if sites:
            #获取最大分页数
            if hxs.xpath('//div[@class="pager cf"]/div[@class="nav"]/a[last()-1]/text()').extract():
                max_page = hxs.xpath('//div[@class="pager cf"]/div[@class="nav"]/a[last()-1]/text()').extract()[0]
                #####print max_page,response.url
            rank =(poi_page-1)*10+1
            for site in sites:
                star_rank = ''
                poi_name = site.xpath('dl/dt/a/text()').extract()[0]
                poi_url = site.xpath('dl/dt/a/@href').extract()[0]
                star_rank_tmp = site.xpath('dl/dt/text()').extract()
                if star_rank_tmp:
                    star_rank = star_rank_tmp[0]
                poi_rank = rank
                ####print poi_name,poi_url,poi_rank
                #get poi_content
                yield Request(url='http://you.ctrip.com%s' %poi_url,callback = self.parse_sightlist_poi_content,meta = \
                {'prov_url':prov_url,'prov_name':prov_name,'city_url':city_url,'city_name':city_name,'city_rank':city_rank,\
                 'poi_name':poi_name,'poi_url':poi_url,'poi_rank':poi_rank,'star_rank':star_rank,'is_province':is_province})
#                for func in ([self.parse_sightlist_poi_urls,'sightlist'],[self.parse_restaurantlist_poi_urls,'restaurantlist'],\
#                             [self.parse_shoppinglist_poi_urls,'shoppinglist'],[self.parse_resortlist_poi_urls,'resortlist']):
#                    yield Request(url = 'http://you.ctrip.com/%s/%s/s0-p%s.html'%(func[1],city_url,poi_page),callback = func[0],meta={'prov_url':\
#                        prov_url,'prov_name':prov_name,'city_url':city_url,'city_name':city_name,'city_rank':city_rank,'poi_page':poi_page})
                rank = rank +1
        poi_page = poi_page + 1
        #callback selfmethod  to crawl next page
        if poi_page <= int(max_page):
            yield Request(url='http://you.ctrip.com/sightlist/%s/s0-p%s.html'%(city_url,poi_page),\
                callback = self.parse_sightlist_poi_urls,meta={'prov_url':prov_url,'prov_name':prov_name,'city_url':city_url,'city_name':city_name,'city_rank':city_rank,'poi_page':poi_page,'is_province':is_province})

    #获取所有城市下美食poi urls
    def parse_restaurantlist_poi_urls(self,response):
        hxs = Selector(response)
        prov_url = response.meta['prov_url']
        prov_name = response.meta['prov_name']
        is_province = response.meta['is_province']
        city_name = city_rank = city_url = ''
        city_url = response.meta['city_url']
        if is_province:
            city_name = response.meta['city_name']
            city_rank = response.meta['city_rank']
        poi_page = response.meta['poi_page']
        sites = hxs.xpath('//div[@class="city_picsight_list "]/div[@class="cpic_sight"]')
        max_page = 1
        #如果有城市列表才continue crawling
        if sites:
            #获取最大分页数
            if hxs.xpath('//div[@class="pager cf"]/div[@class="nav"]/a[last()-1]/text()').extract():
                max_page = hxs.xpath('//div[@class="pager cf"]/div[@class="nav"]/a[last()-1]/text()').extract()[0]
                ###print max_page,response.url
            rank =(poi_page-1)*10+1
            for site in sites:
                poi_name = site.xpath('dl/dt/a/text()').extract()[0]
                poi_url = site.xpath('dl/dt/a/@href').extract()[0]
                poi_rank = rank
                ###print poi_name,poi_url,poi_rank
                #get poi_content
                yield Request(url='http://you.ctrip.com%s' %poi_url,callback = self.parse_restaurantlist_poi_content ,meta =\
                    {'prov_url':prov_url,'prov_name':prov_name,'city_url':city_url,'city_name':city_name,'city_rank':city_rank,\
                     'poi_name':poi_name,'poi_url':poi_url,'poi_rank':poi_rank,'is_province':is_province})
                rank = rank +1
        poi_page = poi_page + 1
        #callback selfmethod  to crawl next page
        if poi_page <= int(max_page):
            yield Request(url='http://you.ctrip.com/restaurantlist/%s/s0-p%s.html'%(city_url,poi_page),\
                callback = self.parse_restaurantlist_poi_urls,meta={'prov_url':prov_url,'prov_name':prov_name,'city_url':city_url,'city_name':city_name,'city_rank':city_rank,'poi_page':poi_page,'is_province':is_province})
    #获取所有城市下购物poi urls
    def parse_shoppinglist_poi_urls(self,response):
        hxs = Selector(response)
        prov_url = response.meta['prov_url']
        prov_name = response.meta['prov_name']
        is_province = response.meta['is_province']
        city_name = city_rank = city_url = ''
        city_url = response.meta['city_url']
        if is_province:
            city_name = response.meta['city_name']
            city_rank = response.meta['city_rank']
        poi_page = response.meta['poi_page']
        sites = hxs.xpath('//div[@class="city_picsight_list"]/div[@class="cpic_sight"]')
        max_page = 1
        #如果有城市列表才continue crawling
        ##print sites
        if sites:
            #获取最大分页数
            if hxs.xpath('//div[@class="pager cf"]/div[@class="nav"]/a[last()-1]/text()').extract():
                max_page = hxs.xpath('//div[@class="pager cf"]/div[@class="nav"]/a[last()-1]/text()').extract()[0]
                ####print max_page,response.url
            rank =(poi_page-1)*10+1
            for site in sites:
                poi_name = site.xpath('dl/dt/a/text()').extract()[0]
                poi_url = site.xpath('dl/dt/a/@href').extract()[0]
                poi_rank = rank
                ####print poi_name,poi_url,poi_rank
                #get poi_content
                yield Request(url='http://you.ctrip.com%s' %poi_url,callback = self.parse_shoppinglist_poi_content,meta =\
                {'prov_url':prov_url,'prov_name':prov_name,'city_url':city_url,'city_name':city_name,'city_rank':city_rank,\
                 'poi_name':poi_name,'poi_url':poi_url,'poi_rank':poi_rank,'is_province':is_province})
                #                for func in ([self.parse_sightlist_poi_urls,'sightlist'],[self.parse_restaurantlist_poi_urls,'restaurantlist'],\
                #                             [self.parse_shoppinglist_poi_urls,'shoppinglist'],[self.parse_resortlist_poi_urls,'resortlist']):
                #                    yield Request(url = 'http://you.ctrip.com/%s/%s/s0-p%s.html'%(func[1],city_url,poi_page),callback = func[0],meta={'prov_url':\
                #                        prov_url,'prov_name':prov_name,'city_url':city_url,'city_name':city_name,'city_rank':city_rank,'poi_page':poi_page})
                rank = rank +1
        poi_page = poi_page + 1
        #callback selfmethod  to crawl next page
        if poi_page <= int(max_page):
            yield Request(url='http://you.ctrip.com/shoppinglist/%s/s0-p%s.html'%(city_url,poi_page),\
                callback = self.parse_shoppinglist_poi_urls,meta={'prov_url':prov_url,'prov_name':prov_name,'city_url':city_url,'city_name':city_name,'city_rank':city_rank,'poi_page':poi_page,'is_province':is_province})
    #获取所有城市下娱乐poi urls
    def parse_resortlist_poi_urls(self,response):
        hxs = Selector(response)
        prov_url = response.meta['prov_url']
        prov_name = response.meta['prov_name']
        is_province = response.meta['is_province']
        city_name = city_rank = city_url = ''
        city_url = response.meta['city_url']
        if is_province:
            city_name = response.meta['city_name']
            city_rank = response.meta['city_rank']
        poi_page = response.meta['poi_page']
        sites = hxs.xpath('//div[@class="city_picsight_list"]/div[@class="cpic_sight"]')
        max_page = 1
        #如果有城市列表才continue crawling
        #print sites
        if sites:
            #获取最大分页数
            if hxs.xpath('//div[@class="pager cf"]/div[@class="nav"]/a[last()-1]/text()').extract():
                max_page = hxs.xpath('//div[@class="pager cf"]/div[@class="nav"]/a[last()-1]/text()').extract()[0]
                ####print max_page,response.url
            rank =(poi_page-1)*10+1
            
            for site in sites:
                start_rank = ''
                poi_name = site.xpath('dl/dt/a/text()').extract()[0]
                poi_url = site.xpath('dl/dt/a/@href').extract()[0]
                star_rank_tmp = site.xpath('dl/dt/text()').extract()
                if star_rank_tmp:
                    star_rank = star_rank_tmp[0]
                poi_rank = rank
                ####print poi_name,poi_url,poi_rank
                #get poi_content
                yield Request(url='http://you.ctrip.com%s' %poi_url,callback = self.parse_resortlist_poi_content ,meta =\
                {'prov_url':prov_url,'prov_name':prov_name,'city_url':city_url,'city_name':city_name,'city_rank':city_rank,\
                 'poi_name':poi_name,'poi_url':poi_url,'poi_rank':poi_rank,'is_province':is_province,'star_rank':star_rank})
                #                for func in ([self.parse_sightlist_poi_urls,'sightlist'],[self.parse_restaurantlist_poi_urls,'restaurantlist'],\
                #                             [self.parse_shoppinglist_poi_urls,'shoppinglist'],[self.parse_resortlist_poi_urls,'resortlist']):
                #                    yield Request(url = 'http://you.ctrip.com/%s/%s/s0-p%s.html'%(func[1],city_url,poi_page),callback = func[0],meta={'prov_url':\
                #                        prov_url,'prov_name':prov_name,'city_url':city_url,'city_name':city_name,'city_rank':city_rank,'poi_page':poi_page})
                rank = rank +1
        poi_page = poi_page + 1
        #callback selfmethod  to crawl next page
        if poi_page <= int(max_page):
            yield Request(url='http://you.ctrip.com/resortlist/%s/s0-p%s.html'%(city_url,poi_page),\
                callback = self.parse_resortlist_poi_urls,meta={'prov_url':prov_url,'prov_name':prov_name,'city_url':city_url,'city_name':city_name,'city_rank':city_rank,'poi_page':poi_page,'is_province':is_province})

    def parse_sightlist_poi_content(self,response):
        hxs = Selector(response)
        prov_url = response.meta['prov_url']
        prov_name = response.meta['prov_name']
        is_province = response.meta['is_province']
        city_url = response.meta['city_url']
        city_name = response.meta['city_name']
        city_rank = response.meta['city_rank']
        poi_name = response.meta['poi_name']
        poi_url = response.meta['poi_url']
        poi_rank = response.meta['poi_rank']
        star_rank = response.meta['star_rank']
        sites = hxs.xpath('//div[@class="detailinfo"]/ul/li')
        if sites:
            poi_tags = poi_play_time = poi_tel = poi_open_time = poi_ticket = poi_addr = ''
            for site in sites:
                #标  签
                poi_tmp_field = site.xpath('dl/dt/text()').extract()
                if poi_tmp_field and poi_tmp_field[0].find(u'标') == 0 and poi_tmp_field[0].find(u'签'):
                    for tag in site.xpath('dl/dd/a'):
                        tag = tag.xpath('text()').extract()
                        if tag:
                            poi_tags += tag[0]+' '
                if poi_tmp_field:
                    tmp = site.xpath('dl/dd/div/text()').extract()
#                    ###print poi_tmp_field[0]
#                    if tmp:
#                        ###print tmp[0]
                    if poi_tmp_field[0].find(u'游玩时间') == 0:
                        if tmp:
                            poi_play_time = tmp[0]

                    elif poi_tmp_field[0].find(u'电  话') == 0 or poi_tmp_field[0].find(u'联系电话') == 0:
                        if tmp:
                            poi_tel = tmp[0]
                    elif poi_tmp_field[0].find(u'开放时间') == 0:
                        if tmp:
                            poi_open_time = tmp[0]
                    elif poi_tmp_field[0].find(u'门票信息') == 0:
                        if tmp:
                            poi_ticket = tmp[0]
                    elif poi_tmp_field[0].find(u'地  址') == 0:
                        if tmp:
                            poi_addr = tmp[0]
#                ###print poi_tags+'\n'+poi_play_time+'\n'+poi_tel +'\n'+ poi_open_time +'\n'+ poi_ticket +'\n'+ poi_addr
            #经纬度
            lat = re.compile(r'var lat = (\d{0,10}.{0,1}\d+);',re.S).search(response.body).groups()[0]
            lng = re.compile(r'var lng = (\d{0,10}.{0,1}\d+);',re.S).search(response.body).groups()[0]
#            ###print lat.groups()[0]
#            ###print lng.groups()[0]

            poi_desc = poi_traffic = poi_percentage = ''
            poi_desc_tmp = hxs.xpath('//div[@class="detailcon"]/div[@class="text_style"]/text()').extract()
            #景点简介，交通
            if poi_desc_tmp:
                poi_desc = poi_desc_tmp[0]
                if len(poi_desc_tmp) > 1:
                    poi_traffic = poi_desc_tmp[1]
#                ###print poi_desc,poi_traffic
            #游友点评
            poi_percentage_tmp = hxs.xpath('//div[@class="percentage"]/strong/text()').extract()
            if poi_percentage_tmp:
                poi_percentage = poi_percentage_tmp[0]
#                ###print poi_percentage
#            conn=MySQLdb.connect(host='54.201.192.244',user='qyer',passwd='qyer',db='mafengwo',port=3306,charset='utf8')
#            cur=conn.cursor()
            sql = 'insert into xiecheng_poi(prov_url,prov_name,is_province,city_url,city_name,city_rank,poi_name,poi_url,\
            poi_tags,poi_tel,poi_addr,poi_lat,poi_lng,poi_desc,poi_percentage,poi_open_time,poi_play_time,poi_ticket,poi_rank,poi_type)\
             values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'

            params = (prov_url,prov_name,is_province,city_url,city_name,city_rank,poi_name,poi_url,\
                      poi_tags,poi_tel,poi_addr,lat,lng,poi_desc,poi_percentage,poi_open_time,poi_play_time,poi_ticket,poi_rank,u'景点')
            cur.execute(sql,params)
            print sql % params
            print 'parse_sightlist_poi_content: success'
#            cur.close()
#            conn.close()


    def parse_restaurantlist_poi_content(self,response):
        hxs = Selector(response)
        prov_url = response.meta['prov_url']
        prov_name = response.meta['prov_name']
        is_province = response.meta['is_province']
        city_url = response.meta['city_url']
        city_name = response.meta['city_name']
        city_rank = response.meta['city_rank']
        poi_name = response.meta['poi_name']
        poi_url = response.meta['poi_url']
        poi_rank = response.meta['poi_rank']
        sites = hxs.xpath('//div[@class="detailinfo"]/ul/li')
        if sites:
            poi_cat = poi_tel = poi_open_time  = poi_addr = ''
            for site in sites:
                #标  签
                poi_tmp_field = site.xpath('dl/dt/text()').extract()
                if poi_tmp_field and poi_tmp_field[0].find(u'菜') == 0 and poi_tmp_field[0].find(u'系'):
                    for cat in site.xpath('dl/dd/a'):
                        cat = cat.xpath('text()').extract()
                        if cat:
                            poi_cat += cat[0]+' '
                if poi_tmp_field:
                    tmp = site.xpath('dl/dd/div/text()').extract()
#                    ###print poi_tmp_field[0]
#                    if tmp:
#                        ###print tmp[0]
                    if poi_tmp_field[0].find(u'营业时间') == 0:
                        if tmp:
                            poi_open_time = tmp[0]

                    elif poi_tmp_field[0].find(u'电        话') == 0:
                        if tmp:
                            poi_tel = tmp[0]
                    elif poi_tmp_field[0].find(u'地        址') == 0:
                        if tmp:
                            poi_addr = tmp[0]
                    ###print poi_cat
                    ###print poi_open_time
                    ###print poi_tel
                    ###print poi_addr
                #经纬度
            lat = re.compile(r'var lat = (\d{0,10}.{0,1}\d+);',re.S).search(response.body).groups()[0]
            lng = re.compile(r'var lng = (\d{0,10}.{0,1}\d+);',re.S).search(response.body).groups()[0]
            ###print lat.groups()[0]
            ###print lng.groups()[0]

            poi_desc  = poi_percentage = ''
            poi_desc_tmp = hxs.xpath('//div[@class="detailcon"]/div[@class="text_style"]/text()').extract()
            #简介，交通
            if poi_desc_tmp:
                poi_desc = poi_desc_tmp[0]
                ###print poi_desc
                #游友点评
            poi_percentage_tmp = hxs.xpath('//div[@class="percentage"]/strong/text()').extract()
            if poi_percentage_tmp:
                poi_percentage = poi_percentage_tmp[0]
                ###print poi_percentage
#            conn=MySQLdb.connect(host='54.201.192.244',user='qyer',passwd='qyer',db='mafengwo',port=3306,charset='utf8')
#            cur=conn.cursor()
            sql = 'insert into xiecheng_poi(prov_url,prov_name,is_province,city_url,city_name,city_rank,poi_name,poi_url,\
            poi_tags,poi_tel,poi_addr,poi_lat,poi_lng,poi_desc,poi_percentage,poi_open_time,poi_rank,poi_type)\
             values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'

            params = (prov_url,prov_name,is_province,city_url,city_name,city_rank,poi_name,poi_url,\
                      poi_cat,poi_tel,poi_addr,lat,lng,poi_desc,poi_percentage,poi_open_time,poi_rank,u'美食')
            cur.execute(sql,params)
            print sql % params
            print 'parse_restaurantlist_poi_content: success'
#            cur.close()
#            conn.close()
    def parse_shoppinglist_poi_content(self,response):
        hxs = Selector(response)
        prov_url = response.meta['prov_url']
        prov_name = response.meta['prov_name']
        is_province = response.meta['is_province']
        city_url = response.meta['city_url']
        city_name = response.meta['city_name']
        city_rank = response.meta['city_rank']
        poi_name = response.meta['poi_name']
        poi_url = response.meta['poi_url']
        poi_rank = response.meta['poi_rank']
        sites = hxs.xpath('//div[@class="detailinfo"]/ul/li')
        if sites:
            poi_tags =  poi_tel  = poi_addr = ''
            for site in sites:
                #标  签
                poi_tmp_field = site.xpath('dl/dt/text()').extract()
                if poi_tmp_field and poi_tmp_field[0].find(u'标') == 0 and poi_tmp_field[0].find(u'签'):
                    for tag in site.xpath('dl/dd/a'):
                        tag = tag.xpath('text()').extract()
                        if tag:
                            poi_tags += tag[0]+' '
                if poi_tmp_field:
                    tmp = site.xpath('dl/dd/div/text()').extract()
#                    ##print poi_tmp_field[0]
#                    if tmp:
#                        ##print tmp[0]
                    if poi_tmp_field[0].find(u'地  址') == 0:
                        if tmp:
                            poi_addr = tmp[0]

                    elif poi_tmp_field[0].find(u'电  话') == 0:
                        if tmp:
                            poi_tel = tmp[0]
                    ##print poi_tags
                    ##print poi_tel
                    ##print poi_addr
                    #经纬度
            lat = re.compile(r'var lat = (\d{0,10}.{0,1}\d+);',re.S).search(response.body).groups()[0]
            lng = re.compile(r'var lng = (\d{0,10}.{0,1}\d+);',re.S).search(response.body).groups()[0]
            ##print lat.groups()[0]
            ##print lng.groups()[0]

            poi_desc  = poi_percentage = ''
            poi_desc_tmp = hxs.xpath('//div[@class="detailcon"]/div[@class="text_style"]/text()').extract()
            #景点简介，交通
            if poi_desc_tmp:
                poi_desc = poi_desc_tmp[0]
                ##print poi_desc
                #游友点评
            poi_percentage_tmp = hxs.xpath('//div[@class="percentage"]/strong/text()').extract()
            if poi_percentage_tmp:
                poi_percentage = poi_percentage_tmp[0]
                ##print poi_percentage
#            conn=MySQLdb.connect(host='54.201.192.244',user='qyer',passwd='qyer',db='mafengwo',port=3306,charset='utf8')
#            cur=conn.cursor()
            sql = 'insert into xiecheng_poi(prov_url,prov_name,is_province,city_url,city_name,city_rank,poi_name,poi_url,\
            poi_tags,poi_tel,poi_addr,poi_lat,poi_lng,poi_desc,poi_percentage,poi_rank,poi_type)\
             values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'

            params = (prov_url,prov_name,is_province,city_url,city_name,city_rank,poi_name,poi_url,\
                      poi_tags,poi_tel,poi_addr,lat,lng,poi_desc,poi_percentage,poi_rank,u'购物')
            cur.execute(sql,params)
            print sql % params
            print 'parse_shoppinglist_poi_content: success'
#            cur.close()
#            conn.close()
    def parse_resortlist_poi_content(self,response):
        hxs = Selector(response)
        prov_url = response.meta['prov_url']
        prov_name = response.meta['prov_name']
        is_province = response.meta['is_province']
        city_url = response.meta['city_url']
        city_name = response.meta['city_name']
        city_rank = response.meta['city_rank']
        poi_name = response.meta['poi_name']
        poi_url = response.meta['poi_url']
        star_rank = response.meta['star_rank']
        poi_rank = response.meta['poi_rank']
        sites = hxs.xpath('//div[@class="detailinfo"]/ul/li')
        if sites:
            poi_tags = poi_play_time = poi_tel = poi_open_time = poi_ticket = poi_addr = ''
            for site in sites:
                #标  签
                poi_tags = ''
                poi_tmp_field = site.xpath('dl/dt/text()').extract()
                if poi_tmp_field and poi_tmp_field[0].find(u'标') == 0 and poi_tmp_field[0].find(u'签'):
                    for tag in site.xpath('dl/dd/a'):
                        tag = tag.xpath('text()').extract()
                        if tag:
                            poi_tags += tag[0]+' '
                if poi_tmp_field:
                    tmp = site.xpath('dl/dd/div/text()').extract()
#                    #print poi_tmp_field[0]
#                    if tmp:
#                        #print tmp[0]
                    if poi_tmp_field[0].find(u'游玩时间') == 0:
                        if tmp:
                            poi_play_time = tmp[0]

                    elif poi_tmp_field[0].find(u'电  话') == 0 or poi_tmp_field[0].find(u'联系电话') == 0:
                        if tmp:
                            poi_tel = tmp[0]
                    elif poi_tmp_field[0].find(u'开放时间') == 0:
                        if tmp:
                            poi_open_time = tmp[0]
                    elif poi_tmp_field[0].find(u'门票信息') == 0:
                        if tmp:
                            poi_ticket = tmp[0]
                    elif poi_tmp_field[0].find(u'地  址') == 0:
                        if tmp:
                            poi_addr = tmp[0]
                #print poi_tags+'\n'+poi_play_time+'\n'+poi_tel +'\n'+ poi_open_time +'\n'+ poi_ticket +'\n'+ poi_addr
                #经纬度
            lat = re.compile(r'var lat = (\d{0,10}.{0,1}\d+);',re.S).search(response.body).groups()[0]
            lng = re.compile(r'var lng = (\d{0,10}.{0,1}\d+);',re.S).search(response.body).groups()[0]
            #print lat.groups()[0]
            #print lng.groups()[0]

            poi_desc = poi_traffic = poi_percentage = ''
            poi_desc_tmp = hxs.xpath('//div[@class="detailcon"]/div[@class="text_style"]/text()').extract()
            #景点简介，交通
            if poi_desc_tmp:
                poi_desc = poi_desc_tmp[0]
                if len(poi_desc_tmp) > 1:
                    poi_traffic = poi_desc_tmp[1]
                    #print poi_desc,poi_traffic
                #游友点评
            poi_percentage_tmp = hxs.xpath('//div[@class="percentage"]/strong/text()').extract()
            if poi_percentage_tmp:
                poi_percentage = poi_percentage_tmp[0]
                #print poi_percentage
            sql = 'insert into xiecheng_poi(prov_url,prov_name,is_province,city_url,city_name,city_rank,poi_name,poi_url,\
            star_rank,poi_tags,poi_play_time,poi_tel,poi_open_time,poi_ticket,poi_addr,poi_lat,poi_lng,poi_desc,poi_traffic,poi_percentage,poi_rank,poi_type)\
             values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            params = (prov_url,prov_name,is_province,city_url,city_name,city_rank,poi_name,poi_url,\
                      star_rank,poi_tags,poi_play_time,poi_tel,poi_open_time,poi_ticket,poi_addr,lat,lng,poi_desc,poi_traffic,poi_percentage,poi_rank,u'娱乐')
            cur.execute(sql,params)
            print sql % params
            print 'parse_resortlist_poi_content: success'
