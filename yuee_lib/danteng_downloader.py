import requests
import os
import threading_danteng


class Downloader(threading_danteng.ObjectDanteng):
    # 复制此段作为初始化函数
    def __init__(self):
        super().__init__()
        self._log_title = 'DOWNLOADER'

    # 开始执行事务
    # 复制此函数修改
    def download(self, url, path, filename):
        args = {
            'url': url,
            'path': path,
            'filename': filename,
        }
        self._que_in.put(args)
        self._start_thread()
        return True

    # 调用不同的类来解决问题
    # 复制此函数修改
    def _thread_do(self):
        return DownloaderThread(self._que_in, self._que_out)


class DownloaderThread(threading_danteng.ThreadDanteng):
    def __init__(self, que_in, que_out):
        super().__init__(que_in, que_out)

    # 覆盖此函数
    def _exec(self, args):
        self._download(args)
        pass

    def _download(self, args):
        count = 0
        while True:
            count += 1
            try:
                response = requests.get(args['url'], timeout=10)
                break
            except Exception as e:  # 超时重新下载
                self._log('<%s>下载时，连接超时%d次，正在重试！' % (args['filename'], count))

        self.check_folder('', args['path'])
        with open(os.path.join(args['path'], args['filename']), 'wb') as file:
            file.write(response.content)

        self._log('文件<%s>下载成功！' % args['filename'])

    # 检查目录是否存在，不存在则创建
    @staticmethod
    def check_folder(base_path, name):
        path = base_path
        if base_path != '' and not os.path.exists(path):
            os.mkdir(path)

        for sep_mark in ['/', '\\']:
            if name.find(sep_mark) >= 0:
                name_split = name.split(sep_mark)
                for i in range(len(name_split)):
                    path = os.path.join(path, name_split[i])
                    if not os.path.exists(path):
                        os.mkdir(path)

        path = os.path.join(base_path, name)
        if not os.path.exists(path):
            os.mkdir(path)
