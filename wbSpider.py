#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author : Dong-Qing
# Time : 2019/7/16

import requests
import rsa
import time
import re, json
import random
import urllib3
import base64
import pymongo
from urllib.parse import quote
from binascii import b2a_hex
from bs4 import BeautifulSoup
from urllib.parse import urlencode


urllib3.disable_warnings()  # 取消警告

# 配置数据库信息
MONGO_URl = 'localhost'
MONGO_DB = 'weibo' # 数据库名
MONGO_TABLE = 'renminwang'  # 表名

# 连接数据库
client = pymongo.MongoClient(host=MONGO_URl, port=27017)
db = client[MONGO_DB]  # 指定要使用的数据库

# ---------------------


def get_timestamp():
    return int(time.time() * 1000)  # 获取13位时间戳


class WeiBo():
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.session()  # 登录用session
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
        }
        self.session.verify = False  # 取消证书验证


        self.base_https = "https:"
        self.base_url = "https://weibo.com"
        self.domain = 100206

    def prelogin(self):
        '''预登录，获取一些必须的参数'''
        self.su = base64.b64encode(self.username.encode())  # 阅读js得知用户名进行base64转码
        url = 'https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su={}&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.19)&_={}'.format(
            quote(self.su), get_timestamp())  # 注意su要进行quote转码
        response = self.session.get(url).content.decode()

        self.nonce = re.findall(r'"nonce":"(.*?)"', response)[0]
        self.pubkey = re.findall(r'"pubkey":"(.*?)"', response)[0]
        self.rsakv = re.findall(r'"rsakv":"(.*?)"', response)[0]
        self.servertime = re.findall(r'"servertime":(.*?),', response)[0]
        return self.nonce, self.pubkey, self.rsakv, self.servertime

    def get_sp(self):
        '''用rsa对明文密码进行加密，加密规则通过阅读js代码得知'''
        publickey = rsa.PublicKey(int(self.pubkey, 16), int('10001', 16))
        message = str(self.servertime) + '\t' + str(self.nonce) + '\n' + str(self.password)
        self.sp = rsa.encrypt(message.encode(), publickey)
        return b2a_hex(self.sp)

    def login(self):
        url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
        data = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'qrcode_flag': 'false',
            'useticket': '1',
            'pagerefer': 'https://login.sina.com.cn/crossdomain2.php?action=logout&r=https%3A%2F%2Fweibo.com%2Flogout.php%3Fbackurl%3D%252F',
            'vsnf': '1',
            'su': self.su,
            'service': 'miniblog',
            'servertime': str(int(self.servertime) + random.randint(1, 20)),
            'nonce': self.nonce,
            'pwencode': 'rsa2',
            'rsakv': self.rsakv,
            'sp': self.get_sp(),
            'sr': '1536 * 864',
            'encoding': 'UTF - 8',
            'prelt': '35',
            'url': 'https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'META',
        }
        response = self.session.post(url, data=data, allow_redirects=False).text  # 提交账号密码等参数
        redirect_url = re.findall(r'location.replace\("(.*?)"\);', response)[0]  # 微博在提交数据后会跳转，此处获取跳转的url
        result = self.session.get(redirect_url, allow_redirects=False).text  # 请求跳转页面
        ticket, ssosavestate = re.findall(r'ticket=(.*?)&ssosavestate=(.*?)"', result)[0]  # 获取ticket和ssosavestate参数
        uid_url = 'https://passport.weibo.com/wbsso/login?ticket={}&ssosavestate={}&callback=sinaSSOController.doCrossDomainCallBack&scriptId=ssoscript0&client=ssologin.js(v1.4.19)&_={}'.format(
            ticket, ssosavestate, get_timestamp())
        data = self.session.get(uid_url).text  # 更新session信息

        # 请求获取uid
        # uid = re.findall(r'"uniqueid":"(.*?)"', data)[0]
        # home_url = 'https://weibo.com/u/{}/home?wvr=5&lf=reg'.format(uid)  # 请求首页

        # html_url = 'https://weibo.com/renminwang'
        # html = self.session.get(html_url)
        # html.encoding = 'utf-8'

        print("登录成功")
        return self.session


    ''' 爬取微博正文 '''
    def wbContent(self, html_url, name, page):

        name = name
        page = page

        html = self.session.get(html_url).text
        soup = BeautifulSoup(html, 'lxml')
        scripts = soup.find_all('script')
        print("正在解析html")


        weibo_title = {} # 创建保存数据

        ''' 解析提取html '''
        for script in scripts:
            s = re.findall(r'\<div(.*)', script.text)
            # '''解析script'''
            if s:
                content_html = '<html><div'+s[0][0:-2].replace("\\", "")+'</html>'
                content_soup = BeautifulSoup(content_html, 'lxml')

                side_contents = content_soup.find_all("div",class_="WB_cardwrap S_bg2")
                if side_contents:
                    # 解析左边栏目
                    for side in side_contents:
                        weibo_title = self.side_content(side, weibo_title)


                contents = content_soup.find_all("div",attrs={"action-type": "feed_list_item"})
                # 判断是否有微博内容
                if contents:
                    pagebar = 0

                    self.content(content_soup, pagebar, name, page, weibo_title)


    def side_content(self, side_contents, weibo_title):
        '''解析微博关注，粉丝，微博总数'''

        soup = side_contents
        weibo_title = weibo_title

        # 关注数，粉丝数，微博总数

        td = soup.find_all("td")
        if td :
            attention_num = td[0].find("strong", class_="W_f12").text  # 关注数
            fans_num = td[1].find("strong", class_="W_f12").text  # 粉丝数
            total_num = td[2].find("strong", class_="W_f12").text  #微博总数

            weibo_title["关注数"] = attention_num
            weibo_title["粉丝数"] = fans_num
            weibo_title["微博总数"] = total_num

        # 认证，行业类别，简介，友情链接
        person_info = soup.find("div",class_="PCD_person_info")
        # print(person_info)
        if person_info:
            approve = person_info.find("div",class_="verify_area W_tog_hover S_line2")
            approve_types = approve.find("span",class_="icon_bed W_fl").find("a")["href"]  # 认证类型
            # 区别认证信息
            # 首先定义认证
            approve_type = "无认证"

            if approve_types:
                if approve_types == "//verified.weibo.com/verify?from=profile":
                    approve_type = "个人认证"
                if approve_types == "//fuwu.biz.weibo.com":
                    approve_type = "机构认证"


            approve_info = approve.find("p",class_="info").text  # 认证信息

            weibo_title["认证类型"] = approve_type
            weibo_title["认证信息"] = approve_info

            approve_li = person_info.find("div",class_="detail").find_all("li")

            if approve_li:
                for li in approve_li:
                        ico = li.find("span",class_="item_ico W_fl")
                        span = li.find("span", class_="item_text W_fl")
                        if ico == 2:
                            weibo_title["作者地域"] = span.text.replace(" ", "").replace(r'(\\n|\r\n|\n|\r)', "")

                        if ico == 4:
                            weibo_title["毕业院校"] = span.find("a").text.replace(" ", "").replace(r'(\\n|\r\n|\n|\r)', "")

                        if ico == "ö":
                            weibo_title["生日"] = span.text.replace(" ", "").replace(r'(\\n|\r\n|\n|\r)', "")

                        if ico == 3:  # 行业类别
                            industry = span.find("span",class_="S_txt2").text
                            if span.find("a"):
                                weibo_title[industry] = span.find("a").text.replace(" ", "").replace(
                                    r'(\\n|\r\n|\n|\r)', "")
                            else:

                                for s in span('span'):
                                    s.extract()
                                    weibo_title[industry] = span.text.replace(" ", "").replace(
                                        r'(\\n|\r\n|\n|\r)', "")
                        if ico == "Ü":
                            introductions = span.text
                            introduction = re.findall(r'简介:(.*?)', introductions)[0]
                            weibo_title["简介"] = introduction.text.replace(" ", "").replace(
                                r'(\\n|\r\n|\n|\r)', "")

                        if ico == "T":
                            weibo_title["友情链接"] = span.find("a").text.replace(" ", "").replace(
                                r'(\\n|\r\n|\n|\r)', "")+span.find("a")["href"]


        return weibo_title



    def content(self, soup, pagebar, name, page, weibo_title):
        '''解析微博，以及判断是否有下一页，未加载页面'''
        soup = soup
        pagebar = pagebar
        name = name
        page = page
        weibo_title = weibo_title

        content = soup.find_all("div", attrs={"action-type": "feed_list_item"})

        WB_tbinfo = content[0]["tbinfo"]
        # num = re.findall(r'ouid=(.*)',WB_tbinfo)[0].split("&")[0]
        mid = str(self.domain) + re.findall(r'ouid=(.*)', WB_tbinfo)[0].split("&")[0]

        ''' 提取每条微博 '''
        print("正在提取每条微博")
        if content:
            for item in content:
                self.weibo_item(item, weibo_title)

        # 检测是否有下一页
        if pagebar == 2:
            try:
                list_page = soup.find('a', text="下一页")
                list_url = self.base_url+ "/" + list_page["href"]
                print(list_url)
                page = page + 1  # 下一页加 1
                pagebar = 0
                # print(pagebar)
                print("{name}正在抓取第{num}页，请稍后".format(name=name,num=page))
                time.sleep(1)  # 每解析一页，休息1秒，防止被封。
                # 请求下一页
                self.wbContent(list_url, name, page)

            except:
                pagebar = 0
                print("{name}微博已经全部抓取完毕！共{num}页，或爬虫出现问题，请检查".format(name=name,num = page))

        ''' 检测加载内容 '''
        load_weibo = soup.find('div',class_='WB_cardwrap S_bg2')

        if load_weibo:
            load_url = self.base_url + "/p/aj/v6/mblog/mbloglist?"
            print("{name}正在抓取未加载{num}，请稍后".format(name=name, num=pagebar))
            time.sleep(1)
            self.load_weibo(load_url, mid, pagebar, name, page, weibo_title)

    def load_weibo(self, load_url, mid, pagebar, name, page, weibo_title):
        load_url = load_url
        mid = mid
        pagebar = pagebar
        name = name
        page = page
        weibo_title = weibo_title

        '''加载页面'''
        par = {
            "ajwvr": 6,
            "domain": 100206,
            "profile_ftype": 1,
            "is_all": 1,
            "pagebar": pagebar,
            "pl_name": "Pl_Official_MyProfileFeed__28",
            "id": mid,
            "script_uri": name,
            "feed_type": 0,
            "page": page,
            "pre_page": page,
            "domain_op": self.domain,
        }

        # 解析返回json,bs4解析传给weibo_item解析
        url = load_url + urlencode(par)  # 构建请求url
        print(url)
        load_html = self.session.get(url)  # 请求url
        load_json = json.loads(load_html.text)["data"]  # 转换json

        soup = BeautifulSoup(load_json,"lxml")  # 解析成bs4格式
        pagebar = pagebar + 1
        self.content(soup, pagebar, name, page, weibo_title)

    def weibo_item(self,item,weibo_title):
        '''解析具体微博 '''
        # print("正在解析微博")

        zhuanzai_item = item.find_all(attrs={'minfo':True})
        weibo_title = weibo_title
        weibo = {}

        # 判断转载还是原创
        if zhuanzai_item:
            weibo_type = "转载"
        else:
            weibo_type = "原创"
            WB_detail = item.find_all('div',class_='WB_detail')[0]  # 整条微博soup
            WB_time_div = WB_detail.find('div',class_='WB_from S_txt2') # 微博时间soup

            # 解析微博id，用作微博唯一标识
            WB_id = WB_time_div.find_all('a')[0]['name']  # 微博id

            # 判断数据库中是否存在
            condition = {"WB_id": WB_id}
            find_WB = db[MONGO_TABLE].find_one(condition)
            if find_WB:

                WB_bottom = item.find('div', class_='WB_feed_handle')  # 微博点赞，转发，评论
                print("数据库已存在这条微博，id编号为{value}".format(value=WB_id))

                # ''' 点赞，转发，评论数量 '''
                bottmo_li = WB_bottom.find_all('li')
                forward_num = bottmo_li[1].find('span', class_='pos').find_all('em')[1].text
                comment_num = bottmo_li[2].find('span', class_='pos').find_all('em')[1].text
                like_num = bottmo_li[3].find('span', class_='pos').find_all('em')[1].text

                # 对比转发数有没有增加
                if forward_num != find_WB["forward_num"]:
                    find_WB["转发数量"] = forward_num  # 转发数量
                    db[MONGO_TABLE].update(condition, find_WB)
                    print("更新转发数量，id编号为{value}".format(value=WB_id))

                else:
                    print("转发数量无更新，id编号为{value}".format(value=WB_id))

                # 对比评论数有没有增加
                if comment_num != find_WB["comment_num"]:
                    find_WB["评论数量"] = comment_num  # 评论数量
                    db[MONGO_TABLE].update(condition, find_WB)
                    print("更新评论数量，id编号为{value}".format(value=WB_id))

                else:
                    print("评论数量无更新，id编号为{value}".format(value=WB_id))

                # 对比点赞数有没有增加
                if like_num != find_WB["like_num"]:
                    find_WB["点赞数量"] = like_num  # 点赞数量
                    db[MONGO_TABLE].update(condition, find_WB)
                    print("更新点赞数量，id编号为{value}".format(value=WB_id))

                else:
                    print("点赞数量无更新，id编号为{value}".format(value=WB_id))

            else:

                # 如果不存在解析微博，并保存
                WB_text = WB_detail.find('div',class_='WB_text W_f14')  # 微博文字soup
                WB_media = WB_detail.find('div',class_='media_box')  # 微博媒体，图片，动图，视频，微博故事
                WB_bottom = item.find('div',class_='WB_feed_handle')  # 微博点赞，转发，评论

                # 微博url
                WB_url = self.base_url + WB_time_div.find_all('a')[0]['href']  # 微博url

                # 解析微博时间
                WB_time = WB_time_div.find_all('a')[0]['title'] # 微博时间

                # 来自
                if len(WB_time_div.find_all('a')) > 1:
                    weibo_come = WB_time_div.find_all('a')[1].text
                    weibo["来自"] = weibo_come  # 来自

                # 判断是否是视频
                WB_video = WB_media.has_attr('video')
                img_ulr = []
                WB_video_url = ''
                if WB_video:
                    WB_video_url = self.base_https + WB_video[0]["src"]  # 视频链接
                else:

                    WB_img_li = WB_media.find_all('li')
                    for li in WB_img_li:
                        img_ulr.append(self.base_https + li.find('img')["src"])  # 图片链接

                # ''' 点赞，转发，评论数量 '''
                bottmo_li = WB_bottom.find_all('li')
                forward_num = bottmo_li[1].find('span',class_='pos').find_all('em')[1].text
                comment_num = bottmo_li[2].find('span',class_='pos').find_all('em')[1].text
                like_num = bottmo_li[3].find('span',class_='pos').find_all('em')[1].text


                # ''' 检测有没有展开全文 '''

                all_content_link = WB_text.find('a', attrs={'action-type':"fl_unfold"})
                if all_content_link:
                    # all_content_url = self.base_https + all_content_link["href"]  # 展开全文链接
                    content_text = self.parse_all_content(WB_url)
                else:
                    content_text = WB_text.text


                weibo["关注数"] = weibo_title["关注数"]
                weibo["粉丝数"] = weibo_title["粉丝数"]
                weibo["微博总数"] = weibo_title["微博总数"]
                weibo["认证类型"] = weibo_title["认证类型"]
                if weibo_title["认证信息"]:
                    weibo["认证信息"] = weibo_title["认证信息"]
                else:
                    weibo["认证信息"] = ""

                try:
                    weibo["作者地域"] = weibo_title["作者地域"]
                except:
                    weibo["作者地域"] = ""

                try:
                    weibo["毕业院校"] = weibo_title["毕业院校"]
                except:
                    weibo["毕业院校"] = ""

                try:
                    weibo["生日"] = weibo_title["生日"]
                except:
                    weibo["生日"] = ""

                try:
                    weibo["行业类别"] = weibo_title["行业类别"]
                except:
                    weibo["行业类别"] = ""

                try:
                    weibo["公司"] = weibo_title["公司"]
                except:
                    weibo["公司"] = ""

                try:
                    weibo["简介"] = weibo_title["简介"]
                except:
                    weibo["简介"] = ""

                try:
                    weibo["友情链接"] = weibo_title["友情链接"]
                except:
                    weibo["友情链接"] = ""

                weibo["微博id"] = WB_id  # 微博id
                weibo["微博url"] = WB_url  # 微博url
                weibo["时间"] = WB_time  # 时间
                weibo["类型"] = weibo_type  # 微博类型
                weibo["正文"] = content_text.replace(" ", "").replace(r'(\\n|\r\n|\n|\r)', "")  # 正文
                weibo["视频url"] = WB_video_url  # 视频链接
                weibo["图片ulr"] = img_ulr  # 图片链接
                weibo["转发数量"] = forward_num  # 转发数量
                weibo["评论数量"] = comment_num  # 评论数量
                weibo["点赞数量"] = like_num  # 点赞数量


                # TODO 微博转发, 去掉秒拍视频
                self.save_to_Mongo(weibo, WB_id)


    # ---------------------
    # 判断数据库中是否存在

    def find_Mongo(self, condition):

        if db[MONGO_TABLE].find_one(condition):
            return True
        else:
            return False

    # 存入数据库
    def save_to_Mongo(self, result, WB_id):

        # try:
        #     if db[MONGO_TABLE].insert_one(result):
        #         print('存储微博{WB_id}到MongoDB成功'.format(WB_id=WB_id))
        # except Exception:
        #     print('存储到MongoDb失败')
        db[MONGO_TABLE].insert_one(result)

        print('存储微博{WB_id}到MongoDB成功'.format(WB_id=WB_id))

    # ---------------------

    def parse_all_content(self, all_content_url):
        ''' 有展开全文的情况，获取全文 '''
        content_html = self.session.get(all_content_url).text
        print(all_content_url)
        soup = BeautifulSoup(content_html,'lxml')
        # 解析script
        scripts = soup.find_all('script')
        print("正在解析html")


        ''' 解析提取html '''
        content_text = ""
        for script in scripts:
            s = re.findall(r'\<div(.*)', script.text)
            # '''解析script'''
            if s:
                content_html = '<html><div' + s[0][0:-2].replace("\\", "") + '</html>'
                content_soup = BeautifulSoup(content_html, 'lxml')
                content = content_soup.find('div',class_='WB_text W_f14')
                if content:
                    content_text = content.text

        return content_text

    def main(self):
        self.prelogin()
        self.get_sp()
        self.login()
        name = 'renminwang'
        html_url = 'https://weibo.com/' + name + "?profile_ftype=1&is_all=1"
        page = 1  # 下一页计数
        self.wbContent(html_url, name, page)


if __name__ == '__main__':
    username = '15311089821'  # 微博账号
    password = 'm123456789'  # 微博密码
    weibos = WeiBo(username, password)
    weibos.main()
    # TODO 在登陆之后获取tbinfo，用框架改写，定时爬取，搜索页面爬取，热搜爬取， 账号池的搭建， 分布式的搭建， ip池的搭建（不重要）

