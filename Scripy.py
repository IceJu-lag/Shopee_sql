import requests
import matplotlib.pyplot as plt
import pandas as pd

import numpy as np
import PIL.Image as Image
from wordcloud import WordCloud
import collections

'''
    模块：网络爬虫
    功能：爬取文章ID，爬取文章详细信息。保存excel
    数据传输至可视化模块，及写入并保存excel文件
'''

class Res:
    def __init__(self): # 初始化數據
        self.urls = []
        self.recruitment_id = []
        self.company_urls = []
        self.job_info = []
        self.job_major = []
        self.city = []
        self.slayer = []

    # 模拟游览器进行网站爬取
    def get_res(self,url): # 爬取網站信息
        user_agent = r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'

        headers = {
            'User-Agent': user_agent
        }
        res = requests.get(url,headers=headers)
        return res


    # 生成10-29页所有网站
    def get_urls(self):  # 獲取10-29頁所有網站
        for i in range(9,28):
            i*=15
            url = 'http://sxufe.bysjy.com.cn/module/getonlines?start=%s&count=16&k=&professionals=&recruit_type='%i
            self.urls.append(url)
        self.get_url_res()


    #爬取10-29页网站
    #获取10-29页网站内所有文章id
    def get_url_res(self): # 獲取10-29也所有文章id
        for url in self.urls:
            res = self.get_res(url).json()['data']
            for res_1 in res:
                res_1 = res_1['recruitment_id']
                self.recruitment_id.append(res_1)
        self.get_company_url()


    #生成所有文章页面网址
    def get_company_url(self): # 獲取所有公司招聘詳情頁網站
        for res_id in self.recruitment_id:
            url = 'http://student.bibibi.net/index.php?r=online_recruitment/ajaxgetrecruitment&token=yxqqnn2400000015&openid=&recruitment_id=%s&type=0&_=1618570223556'%res_id
            self.company_urls.append(url)
        self.get_company_res()

    #对文章页面网址进行爬取
    def get_company_res(self): # 獲取頁面內的信息
        for company_url in self.company_urls:
            #print(company_url)
            res = self.get_res(company_url).json()['data']
            res_title = res['title']
            if len(res['job_list']):
                res_job = res['job_list'][0]
                res_job_major = res_job['about_major']
                company_name = res['company_name']
                res_slayer = res_job['salary']
                res_city_name =  res_job['city_name']
                res_city = res_city_name.split(' ')
                #print(res_city_name)
                info_company = [res_title, company_name, res_job_major, res_slayer, res_city_name]
                self.job_info.append(info_company)
                self.write_excel()
                self.city.append(res_city)
                self.slayer.append(res_slayer)
                self.job_major.append(res_job_major)
        MatLip(self.job_major, self.slayer, self.city )

    #写入并保存excel文件
    def write_excel(self):
        save = pd.DataFrame(self.job_info, columns=['標題', '公司名稱', '專業', '薪資', '城市'])
        save.to_excel('Save.xlsx', index=False, header=True, encoding='utf-8')
        print('写入数据成功')
        #exit()


'''
        模块：数据可视化
        功能：城市词云图，薪资柱状图显示，专业饼状图显示
'''


class MatLip:
    # 数据初始化，并获取返回数据
    def __init__(self,job_major,slayer,city): # 初始化數據
        self.job_major = job_major
        self.slayer = slayer
        self.city = city
        self.city_count = []
        self.slayer_mat()
        self.city_mat()
        self.job_Mar()
        #self.show_mat()
        #self.ax2 = fig.add_subplot(122)
    #对城市进行词云图
    def city_mat(self): # 城市數據詞雲圖化
        for city in self.city:
            for city_name in city:
                self.city_count.append(city_name)
        #print(self.city_count)
        word_counts = collections.Counter(self.city_count)
        #print(word_counts)
        # 调用包PIL中的open方法，读取图片文件，通过numpy中的array方法生成数组
        mask_pic = np.array(Image.open("1.jpg"))
        word = WordCloud(
            font_path='C:/Windows/Fonts/方正粗黑宋简体.ttf',  # 设置字体，本机的字体
            mask=mask_pic,  # 设置背景图片
            background_color='white',  # 设置背景颜色
            max_font_size=150,  # 设置字体最大值
            max_words=2000,  # 设置最大显示字数
            # 设置停用词，停用词则不在词云途中表示
        ).generate_from_frequencies(word_counts)
        image = word.to_image()
        word.to_file('2.png')  # 保存图片
        image.show()

    #对薪资进行区间进行重新划分统计
    def slayer_mat(self):
        creat_slayer = {'3K-5K': 0,
                        '5k-7K': 0,
                        '7K-9K': 0,
                        '9K-11K': 0,
                        '11K-14K': 0,
                        '14K-20K': 0,
                        '面议':0}
        for slayers in self.slayer:
            slayers = slayers.split('-')
            for slayer in slayers:
                if 'K/月' in slayer:
                    slayer_1 = float(slayer.replace('K/月', ''))
                elif 'K' in slayer:
                    slayer_2 = float(slayer.replace('K', ''))
                elif '面议' in slayer:
                    creat_slayer['面议'] += 1
                    break
            #print(slayer_1,slayer_2)
            avg_slayer = (slayer_1 + slayer_2) / 2

            if avg_slayer >= 3.0 and avg_slayer < 5.0:
                creat_slayer['3K-5K'] += 1
            elif avg_slayer >= 5.0 and avg_slayer < 7.0:
                creat_slayer['5k-7K'] += 1
            elif avg_slayer >= 7.0 and avg_slayer < 9.0:
                creat_slayer['7K-9K'] += 1
            elif avg_slayer >= 9.0 and avg_slayer < 11.0:
                creat_slayer['9K-11K'] += 1
            elif avg_slayer >= 11.0 and avg_slayer < 14.0:
                creat_slayer['11K-14K'] += 1
            elif avg_slayer >= 14.0 and avg_slayer < 20.0:
                creat_slayer['14K-20K'] += 1
        self.creat_slayer = creat_slayer
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        plt.bar(range(len(creat_slayer.values())), creat_slayer.values(),
                tick_label=list(creat_slayer.keys()),color = 'rbg')
        plt.show()

    #对需求专业进行统计划分
    def job_Mar(self):
        self.all_job_mar = []
        for job_mars in self.job_major:
            job_mars = job_mars.split('，')
            for job_mar in job_mars:
                self.all_job_mar.append(job_mar)
        self.all_job_mar = dict(collections.Counter(self.all_job_mar).most_common(10))
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        plt.pie(self.all_job_mar.values(), labels= self.all_job_mar.keys(),autopct='%3.2f%%')
        plt.show()


    '''
    def show_mat(self):
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        plt.subplot(1, 2, 1)
        plt.bar(range(len(self.creat_slayer.values())), self.creat_slayer.values(), color='rgb',tick_label=list(self.creat_slayer.keys()))
        plt.subplot(1, 2, 2)
        plt.pie(self.all_job_mar.values(), labels= self.all_job_mar.keys())
        plt.show()
    '''


if __name__ == '__main__':
    #MatLip().job_mat()
    Res().get_urls()
