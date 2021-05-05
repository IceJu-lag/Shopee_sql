import requests
import pymysql
import time
import threading
import sys
sys.setrecursionlimit(10000)

'''
    模块：requests
    功能：爬取首页CatID及子类目ID 并获取商品信息
'''


class Cat:
    def __init__(self, url):
        self.cat_list = []
        self.cat_id = []
        self.url = url
        self.cat_url_list = []
        self.find_sql = []
        self.item = []
        self.items = []
        self.update = []

    def get_res(self, url):  # get requests res
            user_agent = r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'
            headers = {
                'User-Agent': user_agent
            }
            res = requests.get(url, headers=headers)
            return res

    def index_id(self):  # Get Cat_ID List
        self.cat_list = []
        url = self.url + '/api/v2/category_list/get'
        cat_list = self.get_res(url).json()['data']['category_list']
        for cat_id in cat_list:
            cat_id = cat_id['catid']
            self.cat_list.append(cat_id)
        self.cat_id_list()

    def cat_id_list(self):  # Get Cat ID Log List
        self.cat_id = []
        for cat_id in self.cat_list:
            url = self.url + '/api/v4/search/search_facet?match_id=%s&page_type=search'%cat_id
            cat_id_list = self.get_res(url).json()['colorful_block']
            for cat_id_res in cat_id_list:
                #print(cat_id_res)
                name = cat_id_res['category']['display_name']
                res = cat_id_res
                res_id = res['catid']
                product_count = res['count']
                #print(name,res_id, product_count)
                cat = [res_id,name,product_count]
                #ConnMysql().cat_sql(cat)
                self.cat_id.append(res_id)
        self.run_thread()

    def run_thread(self):  # Create thread
        thread_1 = threading.Thread(target=self.url_list)
        thread_2 = threading.Thread(target=self.url_list_50)
        thread_1.start()
        thread_2.start()
        thread_1.join()
        thread_2.join()

    def url_list(self):  # Get url list

        for cat_id in self.cat_id:
            self.cat_url_list = []
            for i in range(50):
                page = i*50
                url = self.url +'/api/v4/search/search_items?by=relevancy&limit=50&locations=-2&match_id=%s&newest=%s&order=desc&page_type=search&scenario=PAGE_OTHERS&version=2'%(cat_id,page)
                self.cat_url_list.append(url)
            #print(len(self.cat_url_list))
            self.url_res()

    def url_list_50(self):  # Get url list

        for cat_id in self.cat_id:
            self.cat_url_list = []
            for i in range(50,100):
                page = i*50
                url = self.url +'/api/v4/search/search_items?by=relevancy&limit=50&locations=-2&match_id=%s&newest=%s&order=desc&page_type=search&scenario=PAGE_OTHERS&version=2'%(cat_id,page)
                self.cat_url_list.append(url)
            #print(len(self.cat_url_list))
            self.url_res()


    def url_res(self):  # Get cat_id items
        #print(self.cat_url_list)
        for url in self.cat_url_list:
            #print(url)
            #print('Successful')

            res = self.get_res(url).json()['items']
            for item in res:
                    item = item['item_basic']
                    itemid = item['itemid']
                    shopid = item['shopid']
                    imag = item['image']
                    currency = item['currency']
                    ctime = item['ctime']
                    ctime = time.strftime("%Y-%m-%d", time.localtime(ctime))
                    sold = item['sold']
                    history_sold = item['historical_sold']
                    liked_count = item['liked_count']
                    view_count = item['view_count']
                    catid = item['catid']
                    cmt_count = item['cmt_count']
                    price = item['price']
                    price_min = item['price_min']
                    price_max = item['price_max']
                    shop_location = item['shop_location']
                    can_use_cod = item['can_use_cod']
                    items = [itemid, shopid, ctime, sold, view_count, imag, currency, history_sold, liked_count, catid,
                             cmt_count, price, price_min, price_max, shop_location, can_use_cod]
                    # print(self.item)
                    # self.item.append()
                    # sql = "insert into items VALUES(%s,%s,'%s',%s,%s,'%s','%s',%s,%s,%s,%s,'%s','%s','%s','%s','%s')" % tuple(items)
                    # self.insert_sql.append([find_sql,sql])
                    # print(self.items)
                    # print(self.item)
                    find_sql = ConnMysql().save_sql(itemid)
                    #print(self.items)
                    if find_sql == 0:
                            self.items.append(tuple(items))
                            if len(self.items) >= 50:
                                ConnMysql().insert_sql(self.items)
                                self.items = []
                    else:
                            self.update.append((sold, view_count, itemid))
                            print(len(self.update))
                            if len(self.update) >= 50:
                                ConnMysql().update_sql(self.update, )
                                self.update = []





'''
    模块：Pymysql
    功能：链接mysql服务器，并写入数据    
'''


class ConnMysql:
    def __init__(self):  # conner mysql
        self.host = '127.0.0.1'
        self.user = 'root'
        self.pwd = '112345566'
        self.db = 'shopee'
        self.sql = pymysql.connect(host=self.host, user=self.user, password=self.pwd, database=self.db)
        self.sql_s = self.sql.cursor()

    def save_sql(self, item):  # insert sql for items or update items sold and view
        find_sql = f"select*from items where find_in_set('{item}',itemid);"
        find_sql = self.sql_s.execute(find_sql)
        return find_sql

    def insert_sql(self, items):
        if len(items) >= 50:
            sql = "insert into items VALUES(%s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
            #print('items'+str(len(list(items))))
            self.sql_s.executemany(sql, list(items))

    def update_sql(self, update):
        if len(update) >= 50:
            sql = "UPDATE items set sold = %s,view_count = %s WHERE itemid =%s;"
            self.sql_s.executemany(sql, tuple(update))
            #print('update'+str(len(update)))




'''
    def cat_sql(self,cat):  # insert mysql for cat_id or update cat_id
        find_sql = f"select*from catid where find_in_set('%s',id);"%cat[0]
        find_sql = self.sql_s.execute(find_sql)
        if find_sql == 0:
            sql = "insert into catid value('%s','%s','%s')"%tuple(cat)
            self.sql_s.execute(sql)
        else:
            sql = "UPDATE catid set count = '%s' where id = %s"%(cat[2],cat[0])
            self.sql_s.execute(sql)
        self.sql.commit()
'''

'''
    模块：threading
    功能：设置定时启动，开启多线程运行
'''


def thread1():  # Create thread  And Run Thread
    tw_thread = threading.Thread(target=Cat('https://xiapi.xiapibuy.com').index_id)
    ph_thread = threading.Thread(target=Cat('https://ph.xiapibuy.com').index_id)

    ph_thread.start()
    tw_thread.start()
    ph_thread.join()
    tw_thread.join()


def thread2():
    my_thread = threading.Thread(target=Cat('https://my.xiapibuy.com').index_id)
    id_thread = threading.Thread(target=Cat('https://id.xiapibuy.com').index_id)

    my_thread.start()
    id_thread.start()
    my_thread.join()
    id_thread.join()


def thread3():
    th_thread = threading.Thread(target=Cat('https://th.xiapibuy.com').index_id)
    sg_thread = threading.Thread(target=Cat('https://sg.xiapibuy.com').index_id)

    th_thread.start()
    sg_thread.start()
    th_thread.join()
    sg_thread.join()


def thread4():
    vn_thread = threading.Thread(target=Cat('https://vn.xiapibuy.com').index_id)
    br_thread = threading.Thread(target=Cat('https://vn.xiapibuy.com').index_id)

    br_thread.start()
    vn_thread.start()
    vn_thread.join()
    br_thread.join()


def time_start():  # Set Time Start
    start = threading.Timer(604800, time_start)
    thread1()
    time.sleep(1200)
    thread2()
    time.sleep(1200)
    thread3()
    time.sleep(1200)
    thread4()
    start.start()
    start.join()


if __name__ == '__main__':
    time_start()
