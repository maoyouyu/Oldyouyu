##################################################
# 将解析后的模板内容，保存到excel文件中
# headers：OrderDict，模板表头数据，key是sheet名称，value是sheet的表头list
# contents：OrderDict，模板内容数据，key是sheet名称，value是一个OrderDict，里面的key只做索引，内容会按照表头更新
# save_path：保存excel的地址
##################################################

import xlsxwriter
import re
import datetime


def save_to_excel(headers, contents, save_path):
    sheet_name_list = []
    workbook = xlsxwriter.Workbook(save_path)
    for sheet_raw_name in headers:
        sheet_name = sheet_name_fix(sheet_raw_name)
        if sheet_name not in sheet_name_list:
            worksheet = workbook.add_worksheet(sheet_name)
            sheet_name_list.append(sheet_name)
        # 表头行数据准备
        headers_list = headers[sheet_raw_name]

        # 写内容
        row = 1
        special_date_header = []  # 已经判明是需要加#的date类型的列
        if sheet_raw_name not in contents:
            print('【%s】名称没有出现在contents参数中，请检查' % sheet_raw_name)
            continue
        for content_index in contents[sheet_raw_name]:
            col = 0
            for header_index in range(len(headers[sheet_raw_name])):
                header = headers[sheet_raw_name][header_index]
                if header in contents[sheet_raw_name][content_index]:
                    value = contents[sheet_raw_name][content_index][header]
                    value_type = 'normal'

                    # 如果是数字
                    try:
                        if type(value) == str and value != '':
                            value = float(value)
                        if type(value) == float and value % 1 == 0.0:
                            value = int(value)
                    except ValueError:
                        pass
                    # 如果是日期
                    if type(value) == str:
                        find_date = re.findall(r'^\d+?-\d+?-\d+$', value)
                        if find_date:
                            try:
                                date_time = datetime.datetime.strptime(value, '%Y-%m-%d')
                                date_format = workbook.add_format({'num_format': 'yyyy/m/d'})
                                value_type = 'date'
                            except ValueError:
                                pass
                        # 特殊日期格式（生日）
                        find_date = re.findall(r'^\d+?月\d+日$', value)
                        if find_date:
                            try:
                                date_time = datetime.datetime.strptime(value, '%m月%d日')
                                date_format = workbook.add_format({'num_format': 'm"月"d"日";@'})
                                value_type = 'date'
                                if header not in special_date_header:
                                    special_date_header.append(header)
                                    headers_list[header_index + 2] = '#' + header
                            except ValueError:
                                pass
                    elif type(value) not in [str, int, float, bool]:
                        value = str(value)

                    # 根据不同类型
                    if value_type == 'date':
                        worksheet.write_datetime(row, col, date_time, date_format)
                    else:
                        worksheet.write(row, col, value)
                else:
                    worksheet.write(row, col, '')
                col += 1
            row += 1

        # 写入表头行
        worksheet.write_row(0, 0, headers_list)

        # 加自动过滤
        worksheet.autofilter(0, 0, worksheet.dim_rowmax, worksheet.dim_colmax)
    try:
        workbook.close()
    except PermissionError as e:
        return {'result': False, 'msg': '保存失败，文件可能正在被打开。错误信息：' + str(e)}

    return {'result': True}


def sheet_name_fix(sheet_name):
    char_list = ['\\', '/', ':', '*', '?', '[', ']']
    for i in range(0, len(char_list)):
        char = char_list[i]
        sheet_name = sheet_name.replace(char, '_%d_' % i)
    return sheet_name[0:31]

# 范例代码
#
#     # 生成excel数据
#     headers = OrderedDict([
#         (data_basename, ['_index'])
#     ])
#     contents = OrderedDict([
#         (data_basename, OrderedDict())
#     ])
#
#     for one_data_index in range(0, len(data_content)):
#         one_data = data_content[one_data_index]
#         if type(one_data) == OrderedDict:
#             for key in one_data.keys():
#                 if key not in headers[data_basename]:
#                     headers[data_basename].append(key)
#             contents[data_basename][one_data_index] = one_data.copy()
#             contents[data_basename][one_data_index]['_index'] = one_data_index
#         else:
#             key = 'value'
#             if key not in headers[data_basename]:
#                 headers[data_basename].append(key)
#             contents[data_basename][one_data_index] = OrderedDict([
#                 ('_index', one_data_index),
#                 ('value', one_data)
#             ])
#
#     save_filepath = os.path.join(cfg['OUTPUT']['xlsx_output_path'], data_basename + '.xlsx')
#     save_to_excel(headers, contents, save_filepath)
