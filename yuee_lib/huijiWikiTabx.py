# 处理和维护HuijiWiki中Tabx类数据的模块
import json
from collections import OrderedDict
from danteng_lib import log


# wiki：用于操作的huijiWiki对象
# title：存储Tabx的数据所在页面名称
# key：默认为''，如果不为空字符串的话，将使用header中的这个项目当作key来生成数据
class HuijiWikiTabx(object):
    def __init__(self, wiki, title, main_key):
        self._wiki = wiki
        self._title = title
        self._key = main_key
        self._original_data = OrderedDict()
        self._header = []  # 数据的表头
        self._key_list = []
        self._data = OrderedDict()  # 数据内容
        # 初始化各个数据
        # 如果需要新建，就初始化一个表格
        self._ready = self.load() and self.generate_header() and self.generate_data()

    # 创建一个新的表
    def create_new_tabx(self):
        self._original_data = OrderedDict([
            ('license', 'CC0-1.0'),
            ('description', OrderedDict([
                ('en', 'table description'),
            ])),
            ('sources', 'Create by huijiWikiTabx'),
            ('schema', OrderedDict([
                ('fields', [])
            ])),
            ('data', [])
        ])
        self.generate_header(True)
        self.generate_data(True)
        self._ready = True
        return True

    # 读取线上数据到本地
    def load(self):
        self._wiki.raw(self._title, notice=False)
        self._wiki.wait_threads()
        result = self._wiki.get_result()
        if len(result) == 1:
            self._original_data = json.loads(result[0]['rawtext'], object_pairs_hook=OrderedDict)
            return True
        else:
            return False

    # 判断是否准备就绪
    def ready(self):
        return self._ready

    # 生成表头
    def generate_header(self, is_new=False):
        # 获取header
        self._header = []
        if is_new:
            return True
        if 'schema' not in self._original_data:
            log('[[%s]]数据有误：未找到表头字段，请检查。' % self._title)
            return False
        if 'fields' not in self._original_data['schema']:
            log('[[%s]]数据有误：未找到表头字段，请检查。' % self._title)
            return False
        for field in self._original_data['schema']['fields']:
            self._header.append(field['name'])
        if self._key != '' and self._key not in self._header:
            log('[[%s]]数据有误：表头字段中未找到当作KEY的“%s”，请检查。' % (self._title, self._key))
            return False
        return True

    # 获取表头
    def get_header(self):
        return self._header

    # 获取原始表头
    def get_original_header(self):
        return self._original_data['schema']['fields']

    # 设置原始表头
    def set_original_header(self, header):
        self._original_data['schema']['fields'] = header
        self.generate_header()

    # 生成数据
    def generate_data(self, is_new=False):
        self._data = OrderedDict()
        if is_new:
            return True
        if 'data' not in self._original_data:
            log('[[%s]]数据有误：未找到内容数据，请检查。' % self._title)
            return False
        for index in range(0, len(self._original_data['data'])):
            row_data = OrderedDict()
            for key_index in range(0, len(self._header)):
                row_data[self._header[key_index]] = self._original_data['data'][index][key_index]

            key = index if self._key == '' else row_data[self._key]
            if self._key != '' and not key:
                log('[[%s]]数据有误：第 %d 行当作KEY的“%s”值是None，请检查。' % (self._title, index+1, self._key))
                return False
            self._data[key] = row_data
        return True

    # 获取全部数据
    def get_all_data(self):
        return self._data

    # 获取数据长度
    def length(self):
        return len(self._data)

    # 查询数据中是否有某个key
    def has_key(self, key):
        return key in self._data

    # 查询数据中是否有某个key
    def has_row(self, key):
        return key in self._data

    # 获取指定key的row_data
    def get_row(self, key):
        if key in self._data:
            return self._data[key]
        else:
            return False

    # 添加/修改新的行
    def mod_row(self, key, data):
        temp_data = OrderedDict()
        for key_index in range(0, len(self._header)):
            header_name = self._header[key_index]
            if header_name == self._key:
                temp_data[header_name] = key
            elif header_name in data:
                temp_data[header_name] = data[header_name]
            else:
                temp_data[header_name] = None
        self._data[key] = temp_data

    # 添加新的行
    # 保存回服务器
    def save(self):
        if len(self._header) == 0:
            return False
        new_data = []
        for row_data in self._data.values():
            temp_row = []
            for key_name in self._header:
                temp_row.append(row_data[key_name])
            new_data.append(temp_row)
        self._original_data['data'] = new_data

        self._wiki.edit(self._title, json.dumps(self._original_data, ensure_ascii=False))
        return True


