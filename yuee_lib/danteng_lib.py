import os
import pickle
from time import strftime, localtime


# 带时间的log
def log(string, error_string=''):
    _str = '%s %s' % (strftime("[%H:%M:%S]", localtime()), string)
    try:
        print('%s %s' % (strftime("[%H:%M:%S]", localtime()), string))
    except:
        print('%s %s' % (strftime("[%H:%M:%S]", localtime())
                         , error_string if error_string == '' else '字符串中有无法显示的字符。'))
    return _str


# dump数据到文件
def save_obj(obj, path):
    with open(path, 'wb') as f:
        pickle.dump(obj, f)
    return True


# 从文件读取dump出来的数据
def load_obj(path):
    if os.path.exists(path):
        with open(path, 'rb') as f:
            return pickle.load(f)
    else:
        return None


# 检查所有层级目录是否存在，不存在则创建
# mode:
# 0:检查最右的一层（会将最右边的那层创建目录）
# 1:不检查最后一层（最右边的那层被视为一个文件名）
def check_folder(filepath, mode=0):
    filepath = filepath.replace('\\', '/')

    path_split = filepath.split('/')

    path = ''
    if len(path_split) > mode:
        for i in range(len(path_split) - mode):
            path = os.path.join(path, path_split[i])
            if path == '':
                continue
            if not os.path.exists(path):
                os.mkdir(path)


# 自动识别编码读取
# 说明：UTF兼容ISO8859-1和ASCII，GB18030兼容GBK，GBK兼容GB2312，GB2312兼容ASCII
CODES = ['UTF-8', 'UTF-16', 'GB18030', 'BIG5']
# UTF-8 BOM前缀字节
UTF_8_BOM = b'\xef\xbb\xbf'


def read_file(file_path):
    result = False
    file_text = ''
    coding = ''
    with open(file_path, 'rb') as f:
        b = f.read()
        # 遍历编码类型
        for code in CODES:
            try:
                b.decode(encoding=code)
                if code == 'UTF-8' and b.startswith(UTF_8_BOM):
                    coding = 'UTF-8-SIG'
                else:
                    coding = code
                break
            except Exception:
                continue
        if coding != '':
            file_text = b.decode(encoding=coding)
            result = True
    return file_text, result
