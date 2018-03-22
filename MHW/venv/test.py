from lib.mhwg_org import Site_MHWg_org
import re
from bs4 import BeautifulSoup
import requests
import time
import bs4
# import xlrd


def getHTMLText(url):
    try:
        r = requests.get(url)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except Exception as e:
        return "出现错误，请检查"


def fillUnivList(ulist, html):
    attributes = []
    armor = []

    soup = BeautifulSoup(html, 'html.parser')

    # 截取套装名字
    # setName = soup.h2.string
    # print(setName[:-8])

    # 查找防具数值
    soup = soup.find_all('table', class_='t1')

    # 第一个表
    tr0 = soup[0].find_all('tr')
    tr0 = tr0[1].find_all('td')
    for i in range(len(tr0)):
        if i == 1 or i == -1:
            pass
        else:
            attributes.append(tr0[0].string)
            attributes.append(tr0[1].string)

    # 第二个表
    tr1 = soup[1].find_all('tr')
    for i in range(len(tr1)):
        if i == 0 or i == 6:
            pass
        else:
            armorName = tr1[1].find_all('td')
            for i in range(len(armorName)):
                armor.append([armorName[0].string,armorName[1].string,armorName[2].string,armorName[3].string,armorName[4].string,armorName[5].string,armorName[6].string,armorName[7].string,])

    # 第三个表
    # tr2 = soup[2].find_all('tr')
    # for i in range(len(tr2)):
    #     if i == 1





    # ulist.append([soup[0].string])
    x =1






def printUnivList(ulist, num):
    pass




def main():
    html = Site_MHWg_org
    uinfo = []
    # url = "http://www.baidu.com"
    url = 'http://mhwg.org/ida/1191.html'
    html = getHTMLText(url)
    fillUnivList(uinfo, html)
    printUnivList(uinfo, 20)

main()

