from danteng_lib import log, check_folder
import requests
from pyquery import PyQuery as pq
import os


MAIN_PAGE_NAME = 'mainpage.html'


class Site_MHWg_org(object):
    _temp_save_path = 'mhwg_org'
    _main_page_url = 'http://mhwg.org'
    _main_page_name = 'mainpage.html'

    def __init__(self):
        pass

    def _log(self, text):
        log(text)

    # 获取首页代码
    def mainpage(self):
        html_file_path = os.path.join(self._temp_save_path, self._main_page_name)
        if os.path.exists(html_file_path):
            with open(html_file_path, 'r', encoding='UTF-8') as f:
                return pq(f.read())
        else:
            check_folder(html_file_path, 1)
            response = self._get(self._main_page_url)
            if response.status_code == 200:
                with open(html_file_path, 'w', encoding='UTF-8') as f:
                    f.write(response.text)
                return pq(response.text)

    def get_page(self, page_url):
        url = '%s/%s' % (self._main_page_url, page_url)
        html_file_path = os.path.join(self._temp_save_path, page_url[1:] if page_url[0:1] == '/' else page_url)
        if os.path.exists(html_file_path):
            with open(html_file_path, 'r', encoding='UTF-8') as f:
                return pq(f.read())
        else:
            # return False
            check_folder(html_file_path, 1)
            response = self._get(url)
            if response.status_code == 200:
                with open(html_file_path, 'w', encoding='UTF-8') as f:
                    f.write(response.text)
                self._log('地址 %s 保存完毕。' % page_url)
                return pq(response.text)

    def _get(self, url):
        response = None
        for i in range(5):
            try:
                response = requests.get(url, timeout=10)
            except:  # 超时重新下载
                if i == 5:
                    self._log('连续操作超时%d次，操作失败！' % (i + 1))
                    return False
                else:
                    self._log('操作超时，正在重试（第%d次）...' % (i + 1))
        return response
