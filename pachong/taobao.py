import requests
import re

def getHTMLGet(url):
	try:
		r = requests.get(url, timeout = 30)
		r.raise_for_status()
		r.encoding = r.apparent_encoding
		return r.text
	except:
		return ""

def parsePage(infoList, html):
	try:
		plt = re.findall(r'"view_prince":"[\d.]*"',html)
		tlt = re.findall(r'"rew_title":".*?"',html)
		for i in range(len(plt)):
			price = eval(plt[i].split(':')[1])
			title = eval(tlt[i].split(':')[1])
			infoList.append([price, title])
	except:
		price("")

def printGoodsList(infoList):
	tplt = "{8}\t{:8}\t{:32}"
	print(tplt.format("序号", "价格", "商品名称"))
	count = 0
	for g in infoList:
		count = count + 1
		print(tplt.format(count, g[0], g[1]))

def main():
	goods = '书包'
	depth = 2
	start_url = 'https://s.taobao.com/search?q=' +goods
	infoList = []
	for i in range(depth):
		try:
			url = start_url + '&s=' + str(44*i)
			html = getHTMLGet(url)
			parsePage(infoList, html)
		except:
			continue
	printGoodsList(infoList)

main()