from selenium import webdriver
import time
import requests

driver = webdriver.Chrome() # 需要一个谷歌驱动
time.sleep(3)
driver.get('https://mp.weixin.qq.com/')

driver.find_element_by_xpath('//*[@id="header"]/div[2]/div/div/form/div[1]/div[1]/div/span/input').clear() # 定位到元素  清楚文本信息
driver.find_element_by_xpath('//*[@id="header"]/div[2]/div/div/form/div[1]/div[1]/div/span/input').send_keys('1879468951@qq.com')
time.sleep(2)

driver.find_element_by_xpath('//*[@id="header"]/div[2]/div/div/form/div[1]/div[2]/div/span/input').clear()
driver.find_element_by_xpath('//*[@id="header"]/div[2]/div/div/form/div[1]/div[2]/div/span/input').send_keys('taoyuyuan1234')
time.sleep(2)

driver.find_element_by_xpath('//*[@id="header"]/div[2]/div/div/form/div[3]/label/i').click() # 点击 记住账号
time.sleep(2)

driver.find_element_by_xpath('//*[@id="header"]/div[2]/div/div/form/div[4]/a').click() # 登录
time.sleep(15) # 出现二维码需要自己扫一下

cookies = driver.get_cookies() # 获取登录之后的cookies

cookie = {}

for items in cookies():
	cookie[items.get('name')] = items.get('velue')

with open('cookies.txt', 'w') as file:
	file.write(json.dumps(cookie)) # 写入转成字符串的字典

driver.close()