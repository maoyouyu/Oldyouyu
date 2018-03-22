import requests
from bs4 import BeautifulSoup
from zhuafangju import analysis
from yuee_lib.SaveToExcel import save_to_excel
from collections import OrderedDict
import os


# 获取网页源代码
def getHTMLText(url):

    # 判断网页文件是否存在
    root_html = 'html' + "\\" + url.split('/')[-2] + "\\" + url.split('/')[-1]
    if os.path.exists(root_html):
        with open(root_html, 'r', encoding="utf-8") as f:
            html = f.read()
        return html

    else:
        html = saveWeb(url)
        print("文件保存成功！")
        # r = requests.get(url)
        # root_html = root_html + '.html'
        # with open(root_html, 'w') as f:
        #     f.write(r.text)
        return html


# 首页爬虫
def homeSpider(html):
    url_list = []
    soup = BeautifulSoup(html, 'html.parser')
    soup = soup.find('table', id='sc_3')
    urlSpider = soup('tr')
    for k in range(len(urlSpider)):
        if k >= 2:
            a_list = urlSpider[k].find_all('a')
            for attrs_list in a_list:
                a_url = attrs_list.attrs
                html = 'http://mhwg.org' + a_url['href']
                url_list.append(html)
    print('首页解析完成')
    return url_list

# 第二页标签
def secondSpider(url_list):
    armor_url_list = []
    for secondurl in url_list:
        # 解析网页地址
        second = getHTMLText(secondurl)

        secondSoup = BeautifulSoup(second, 'html.parser')
        secondSoup = secondSoup.find_all('div', class_="card-header")
        for v in secondSoup:
            secondSoup_url = v.find('a')['href']
            html = 'http://mhwg.org' + secondSoup_url
            armor_url_list.append(html)
    print('子页解析完成')
    return armor_url_list

# 最终页爬虫
def finallySpider(armor_url_list,armor_list):


    for secondurl in armor_url_list:
        # 解析最终页网页地址
        finallyHtml = getHTMLText(secondurl)
        third_list = analysis(finallyHtml)
        armor_list.update(third_list)

        # 合并表格
        for k, v in third_list.items():
            armor_list[k] = v
        print('表格和并成功' + secondurl)


    return armor_list


# 生成excel数据
def saveExcel(armor_list):

    data_basename = '防具'
    headers = OrderedDict([
        (data_basename, [])
        # (data_basename, ['套装名字', 'レア', '性别','装备名字','防御力','强化后','火', '水', '雷','氷', '龍'
        #                  '防御力', '强化后', '火', '水', '雷', '氷', '龍', '技能1', '技能值1', '技能2', '技能值2'
        #                  '技能3', '技能值3', '技能4', '技能值4', '套装技能名称', 'スキル名1', '必要数1', 'スキル名2',
        #                  '必要数2', 'スキル名3', '必要数3', 'スキル名4', '必要数4', 'スキル名5', '必要数5', '各防具生産費用',
        #                  '必要素材1', '必要数量1', '必要素材2', '必要数量2', '必要素材3', '必要数量3', '必要素材4', '必要数量4',
        #                  '必要素材5', '必要数量5',
        #                  ])
    ])
    contents = OrderedDict([
        (data_basename, OrderedDict())
    ])

    for armor_name, armor_info in armor_list.items():
        for header in armor_info.keys():
            if header not in headers[data_basename]:
                headers[data_basename].append(header)

    contents[data_basename] = armor_list

    save_filepath = os.path.join(data_basename + '.xlsx')

    save_to_excel(headers, contents, save_filepath)

    print('表格处理我完成')

    x=1

# 创建更改本地路径
def changeRoot(url,root):

    # 根据不同的路径，更改文件路径
    if url.split('/')[-2] == 'data':
        root = root +"\\" + 'data\\'
    elif url.split('/')[-2] == 'ida':
        root = root +"\\" + 'ida\\'

    return root

# 设置超时
def get(url):
    response = None
    for i in range(10):
        try:
            response = requests.get(url, timeout=10)
        except:  # 超时重新下载
            if i == 10:
                print('连续操作超时%d次，操作失败！' % (i + 1))
                return False
            else:
                print('操作超时，正在重试（第%d次）...' % (i + 1))
    return response

# 保存网页
def saveWeb(url):
    root = "html"
    root = changeRoot(url, root)
    path = root + url.split('/')[-1]
    try:

        if not os.path.exists(root):
            os.mkdir(root)
        if not os.path.exists(path):
            response = get(url)
            if response.status_code == 200:
                with open(path, 'w', encoding="UTF-8") as f:
                    f.write(response.text)

                return response.text
        else:
            print('文件已存在')

    except Exception as e:
        return "出现网页出现错误，请检查"

def main():
    armor_list = OrderedDict()
    uinfo = []
    f = open('html\【MHW】モンハンワールド攻略レシピ.html', 'r', encoding="utf-8")
    html = f.read()
    f.close()

    url_list = homeSpider(html)
    armor_url_list = secondSpider(url_list)
    # finally_url = getHTMLText(armor_url_list)
    finallySpider(armor_url_list,armor_list)
    saveExcel(armor_list)

if __name__ == '__main__':
    main()