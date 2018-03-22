import requests
from lxml import etree
from Queue import Queue
import threading
'''
Queue.qsize() #返回队列大小
Queue.empty() #如果队列为空 返回TURE 反之返回False

Queue.put()
Queue.get()
'''

class Crawl_thread(threading):
	"""抓取线程"""
	def __init__(self, thread_id, queue):#在市里这个类的时候会调用init方法
		threading.Thread,__init__(self)
		self.thread_id = thread_id
		self.queue = queue
		print ('调用了init方法')

	def run(self):
		print('启动线程').format(self.thread_id)
		self.Crawl_spider()
		print('退出了线程').format(self.thread_id)

	def Crawl_spider(self):
		while Ture:
			if self.queue.empty():
				break
			else:
				page = self.queue.get()
				print u'正在工作的线程是，{}，正在采集第{}个页面'.format(self.thread_id)
				url = 'https://www.qiushibaike.com/8hr/page/{}/'.format(str(page))
				headers = {Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Mobile Safari/537.36}

				try:
					content = requests.get(url, headers = headers)
					date_queue.put(content.text)

				except Exception as e:
					print('采集线程错误')，e

class Parser_thread(threading.Thread):
	'''解析网页的类'''
	def __init__(self， thread_id, queue):
		thread.Thread.__init__(self)
		self.thread_id = thread_id
		self.queue = queue

	def run(self):
		print('启动线程').format(self.thread_id)
		self.Crawl_spider()
		print('退出了线程').format(self.thread_id)


data_queue = Queue() #创建一个队列

kl_thread = Crawl_thread() #实例一个类
		