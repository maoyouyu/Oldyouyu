from lib.mhwg_org import Site_MHWg_org
from collections import OrderedDict
from danteng_lib import log, save_obj, load_obj
from SaveToExcel import save_to_excel
from huijiWiki import HuijiWiki
from huijiWikiTabx import HuijiWikiTabx
import re
import os


WEAPON_NAME_MAP = {
    '大剣': '大剑',
    '太刀': '太刀',
    '片手剣': '单手剑',
    '双剣': '双剑',
    'ハンマー': '锤',
    '狩猟笛': '狩猎笛',
    'ランス': '长枪',
    'ガンランス': '铳枪',
    'スラッシュアックス': '剑斧',
    'チャージアックス': '盾斧',
    '操虫棍': '操虫棍',
    'ライトボウガン': '轻弩',
    'ヘビィボウガン': '重弩',
    '弓': '弓',
}

WEAPON_OBJ_FILEPATH = 'weapon_data.obj'


def run_job():
    if not os.path.exists(WEAPON_OBJ_FILEPATH):
        weapon_all_data = get_weapon_data()
    else:
        weapon_all_data = load_obj(WEAPON_OBJ_FILEPATH)
    wiki = HuijiWiki('mhw')
    if not wiki.login('Yuee bot', '123654abC'):
        log('登录失败，请检查。')
        return False
    if not wiki.get_edit_token():
        log('获取令牌失败，请检查。')
        return False
    # update_weapon_data(wiki, weapon_all_data)

    generate_weapon_excel(weapon_all_data)
    # output_weapon_name_excel(weapon_all_data)


def update_weapon_data(wiki, weapon_all_data):
    for weapon_type_name, weapon_type_data in weapon_all_data.items():
        weapon_tabx = HuijiWikiTabx(wiki, 'Data:武器/%s.tabx' % weapon_type_name, 'name_jp')
        if not weapon_tabx.ready():
            weapon_tabx.create_new_tabx()

        # 补充表头
        headers_list = weapon_tabx.get_header()
        original_headers = weapon_tabx.get_original_header()
        for _, weapon_data in weapon_type_data.items():
            for weapon_data_header, weapon_data_value in weapon_data.items():
                use_header = weapon_data_header
                if type(weapon_data_value) in [int, float]:
                    header_type = 'number'
                elif type(weapon_data_value) == bool:
                    header_type = 'boolean'
                elif type(weapon_data_value) == list:
                    header_type = 'string'
                    use_header = '%s[]' % weapon_data_header
                    weapon_data[weapon_data_header] = ';'.join([str(value) for value in weapon_data_value])
                else:
                    header_type = 'string'
                    weapon_data[weapon_data_header] = str(weapon_data_value)
                if weapon_data_header not in headers_list:
                    original_headers.append(OrderedDict([
                        ('name', weapon_data_header),
                        ('type', header_type),
                        ('title', OrderedDict([
                            ('en', use_header),
                        ]))
                    ]))
                    headers_list.append(weapon_data_header)
        weapon_tabx.set_original_header(original_headers)

        # 填写内容
        for _, weapon_data in weapon_type_data.items():
            weapon_tabx.mod_row(weapon_data['name_jp'], weapon_data)

        weapon_tabx.save()
        break

    pass


def get_weapon_data():
    mhwg_org = Site_MHWg_org()
    # 获取首页对象
    mainpage = mhwg_org.mainpage()

    # 从首页获取武器列表
    weapon_data = OrderedDict()

    pq_weapon_a_groups = mainpage('#sc_2 a')
    for weapon_type_index in range(len(pq_weapon_a_groups)):
        pq_weapon_type = pq_weapon_a_groups.eq(weapon_type_index)
        type_page_url = pq_weapon_type.attr('href')

        weapon_type_name = WEAPON_NAME_MAP[pq_weapon_type.text()]

        if weapon_type_name not in ['双剑']:
            continue

        weapon_data[weapon_type_name] = OrderedDict()

        # 从武器列表页，获取所有武器派生页面的数据
        pq_weapon_type_page = mhwg_org.get_page(type_page_url)
        pq_weapon_type_a_groups = pq_weapon_type_page('.t1 a')
        for weapon_index in range(len(pq_weapon_type_a_groups)):
            pq_weapon = pq_weapon_type_a_groups.eq(weapon_index)
            weapon_page_url = pq_weapon.attr('href')
            if weapon_page_url.find('#') >= 0:
                continue

            pq_weapon_page = mhwg_org.get_page(weapon_page_url)

            if not pq_weapon_page:
                log('武器页未找到 %s' % weapon_page_url)
                continue

            # if weapon_page_url not in ['/ida/220824.html']:
            #     continue
            log('开始解析 %s' % weapon_page_url)
            result = analyze_weapon_page(pq_weapon_page, weapon_type_name)
            if not result:
                continue
            weapon_data[weapon_type_name].update(result)

    # save_obj(weapon_data, 'weapon_data.obj')
    return weapon_data


# 解析一个武器页
def analyze_weapon_page(pq_obj, weapon_type_name):
    # 先抓出所有table.ti，数据都在这3个表格里
    table_t1_group = pq_obj('table.t1')

    if weapon_type_name == '狩猎笛':
        if len(table_t1_group) != 4:
            log('table.ti长度不为4，请检查')
            return False

        temp_weapon_data = OrderedDict()
        # 第一个 table.t1 是该派生各级别数据（攻击，槽，斩味）
        analyze_weapon_page_base_info(table_t1_group.eq(0), temp_weapon_data, weapon_type_name)
        # 第二个 table.t1 是强化素材表查询
        analyze_weapon_page_upgrade_info(table_t1_group.eq(2), temp_weapon_data)
        # 第三个 table.t1 是入手方法查询
        analyze_weapon_page_craft_info(table_t1_group.eq(3), temp_weapon_data)
    else:
        if len(table_t1_group) != 3:
            log('table.ti长度不为3，请检查')
            return False

        temp_weapon_data = OrderedDict()
        # 第一个 table.t1 是该派生各级别数据（攻击，槽，斩味）
        analyze_weapon_page_base_info(table_t1_group.eq(0), temp_weapon_data, weapon_type_name)
        # 第二个 table.t1 是强化素材表查询
        analyze_weapon_page_upgrade_info(table_t1_group.eq(1), temp_weapon_data)
        # 第三个 table.t1 是入手方法查询
        analyze_weapon_page_craft_info(table_t1_group.eq(2), temp_weapon_data)

    return temp_weapon_data


def analyze_weapon_page_base_info(info_obj, temp_weapon_data, weapon_type_name):
    # 第一行是目录，从第二行开始取数据
    info_obj_tr_group = info_obj('tr')
    for i in range(1, len(info_obj_tr_group)):
        info_obj_tr = info_obj_tr_group.eq(i)
        info_obj_td_group = info_obj_tr.children('td')
        # 名称
        temp_weapon_info = OrderedDict([
            ('name_jp', info_obj_td_group.eq(0).text()),
            ('rare', 0),
            ('atk', 0),
            ('def', 0),
            ('cri', 0),
            ('elem', ''),
            ('elem_v', 0),
            ('elem_release', False),
            ('socket', []),
            ('seal_dragon', ''),
        ])
        # 攻击力
        temp_weapon_info.update(get_weapon_stat(info_obj_td_group.eq(1)))

        # 瓶
        if weapon_type_name == '弓':
            temp_weapon_info.update(get_weapon_bow_stat(info_obj_td_group.eq(3)))
        # 弹药
        elif weapon_type_name in ['轻弩', '重弩']:
            temp_weapon_info.update(get_weapon_gun_stat(info_obj_td_group.eq(2)))
            temp_weapon_info['b_special'] = info_obj_td_group.eq(3).text()
        # 斩味
        else:
            temp_weapon_info.update(get_weapon_kire(info_obj_td_group.eq(3)))
        # 斩味处理完成↑

        if temp_weapon_info['atk'] > 0:
            temp_weapon_data[temp_weapon_info['name_jp']] = temp_weapon_info
    return True


def analyze_weapon_page_upgrade_info(info_obj, temp_weapon_data):
    info_obj_tr_group = info_obj('tr')
    for i in range(1, len(info_obj_tr_group)):
        info_obj_tr = info_obj_tr_group.eq(i)
        info_obj_td_group = info_obj_tr('td')
        # 名称
        weapon_name = info_obj_td_group.eq(1).text()
        # 攻击力
        find = re.findall(r'(.*?)\n\[巻き戻し不可\]', weapon_name)
        can_not_back = False
        if find:
            weapon_name = find[0]
            can_not_back = True

        if weapon_name not in temp_weapon_data:
            # log('强化部分出现了基础数据部分没有的武器名称：%s' % weapon_name)
            continue

        temp_weapon_info = temp_weapon_data[weapon_name]
        if temp_weapon_info['atk'] == 0:
            log('武器没有攻击力，可能是未完成的数据，已跳过。武器名称：%s' % weapon_name)
            return False

        temp_weapon_info['rare'] = int(info_obj_td_group.eq(0).text())
        temp_weapon_info['can_not_back'] = can_not_back

        # 可强化路线
        temp_weapon_info['upgrade_target'] = []
        upgrade_target_item_text = info_obj_td_group.eq(3).text()
        if upgrade_target_item_text != '':
            temp_weapon_info['upgrade_target'] = upgrade_target_item_text.split('\n')

        # 强化素材
        # temp_weapon_info['获得类型'] = '强化'
        # temp_weapon_info['价格'] = 0
        # temp_weapon_info['素材'] = []
        temp_weapon_info.update(get_material_info(info_obj_td_group.eq(2).text(), 'upgrade'))

        # 强化表完成
    return True


def analyze_weapon_page_craft_info(info_obj, temp_weapon_data):
    info_obj_tr_group = info_obj('tr')
    for i in range(1, len(info_obj_tr_group)):
        info_obj_tr = info_obj_tr_group.eq(i)
        info_obj_td_group = info_obj_tr('td')
        # 名称
        weapon_name = info_obj_td_group.eq(0).text()
        weapon_name = weapon_name.replace('\n↓', '').replace('\n[巻き戻し不可]', '')
        # 只统计当前有的项目
        if weapon_name in temp_weapon_data:
            temp_weapon_info = temp_weapon_data[weapon_name]

            material_div_groups = info_obj_td_group.eq(1).find('div')
            for div_index in range(len(material_div_groups)):
                material_div_text = material_div_groups.eq(div_index).text()
                if material_div_text[0:4] == '[生産]':
                    temp_weapon_info.update(get_material_info(material_div_text, 'craft'))
    return True


ELEMENT_MAP = {
    '火': '火',
    '水': '水',
    '雷': '雷',
    '龍': '龙',
    '氷': '冰',
    '毒': '毒',
    '麻痺': '麻痹',
    '睡眠': '睡眠',
    '爆破': '爆破',
    '強撃': '强击',
    '強属性': '强属性',
    '減気': '减气',
    '滅龍': '灭龙',
    '榴弾': '榴弹'
}

GUNLANCE_MAP = {
    '通常': '通常',
    '拡散': '扩散',
    '放射': '放射',
}

SOUND_COLOR_MAP = {
    '#f3f3f3': '白',
    '#e0002a': '红',
    'blue': '蓝',
    '#00cc00': '绿',
    '#00eeee': '青',
    '#eeee00': '黄',
    '#ff00ff': '紫',
    '#C778C7': '紫',
    '#ef810f': '橙',
    '#99F8F8': '青',
}

CLUB_EFFECT = {
    '攻撃強化【切断】': '攻击强化【切断】',
    'スピード強化': '速度强化',
    '攻撃強化【属性】': '攻击强化【属性】',
    '回復強化【体力】': '回复强化【体力】',
    '攻撃強化【打撃】': '攻击强化【打击】',
    '回復強化【スタミナ】': '回复强化【耐力】',
}

BURE_MAP = {
    'なし': 0,
    '小': 1,
    '中': 2,
    '大': 3,
}


def get_weapon_stat(td_obj):
    stat_text = td_obj.text()
    result_info = OrderedDict([
        ('other_effect', [])
    ])

    for stat_text_one_line in stat_text.split('\n'):
        stat_text_one_line = stat_text_one_line.strip()
        # 攻击力
        find = re.findall(r'攻撃：(\d+)', stat_text_one_line)
        if find:
            result_info['atk'] = int(find[0])
            continue
        # 孔数
        find = re.findall(r'スロット：(.*)', stat_text_one_line)
        if find:
            if find[0] == '':
                continue
            result_info['socket'] = []
            for socket_info in find[0].split(' '):
                if socket_info == '-':
                    result_info['socket'].append(0)
                elif socket_info == '①':
                    result_info['socket'].append(1)
                elif socket_info == '②':
                    result_info['socket'].append(2)
                elif socket_info == '③':
                    result_info['socket'].append(3)
            continue
        # 防御
        find = re.findall(r'防御(.+)', stat_text_one_line)
        if find:
            result_info['def'] = int(find[0].replace('+', ''))
            continue
        # 会心
        find = re.findall(r'会心(.+)%', stat_text_one_line)
        if find:
            result_info['cri'] = int(find[0].replace('+', ''))
            continue

        # 找属性攻击力
        find = re.findall(r'(:?属性解放：)?(\D+)(\d+)', stat_text_one_line)
        if find:
            elem_type = find[0][1]
            if elem_type in ELEMENT_MAP:
                if find[0][0] == '属性解放：':
                    result_info['elem_release'] = True

                result_info['elem'] = ELEMENT_MAP[elem_type]
                result_info['elem_v'] = int(find[0][2])
                continue
            # 铳枪
            elif elem_type in GUNLANCE_MAP:
                result_info['gun_type'] = '%s%s' % (GUNLANCE_MAP[elem_type], find[0][2])
                continue

        # 盾斧，剑斧的瓶
        find = re.findall(r'ビン：(\D+)(\d*)', stat_text_one_line)
        if find:
            elem_type = find[0][0]
            if elem_type in ELEMENT_MAP:
                result_info['bottle'] = ELEMENT_MAP[elem_type]
                result_info['bottle_v'] = 0
                if find[0][1] != '':
                    result_info['bottle_v'] = int(find[0][1])
                continue
        # 龙封
        find = re.findall(r'龍封力\[(.+)]', stat_text_one_line)
        if find:
            result_info['seal_dragon'] = find[0]
            continue

        # 狩猎笛
        if stat_text_one_line == '■■■':
            result_info['sound'] = []
            all_span_obj_groups = td_obj.children('span')
            for sound_span_index in range(len(all_span_obj_groups)):
                sound_span_obj = all_span_obj_groups.eq(sound_span_index)
                if sound_span_obj.text() != '■■■':
                    # log('音色提取出错，请检查')
                    continue

                sound_color_obj_groups = sound_span_obj.eq(0).find('span')

                for sound_index in range(len(sound_color_obj_groups)):
                    sound_color_obj = sound_color_obj_groups.eq(sound_index)
                    find_color = re.findall(r'color:(.*?);', sound_color_obj.attr('style'))
                    if find_color:
                        if find_color[0] not in SOUND_COLOR_MAP:
                            log('音色颜色未匹配到：%s' % find_color[0])
                        result_info['sound'].append(SOUND_COLOR_MAP[find_color[0]])
            continue

        # 操虫棍
        if stat_text_one_line in CLUB_EFFECT:
            result_info['effect'] = CLUB_EFFECT[stat_text_one_line]
            continue

        # 轻弩重弩期待值，删掉
        find = re.findall(r'\(期待値：(\d+)\)', stat_text_one_line)
        if find:
            continue

        # 轻弩重弩抖动
        find = re.findall(r'ブレ：(.+)', stat_text_one_line)
        if find:
            result_info['bure'] = BURE_MAP[find[0]]
            continue

        # 强化部件
        find = re.findall(r'強化パーツ：(\d+)', stat_text_one_line)
        if find:
            result_info['upgrade_slot'] = int(find[0])
            continue

        # 其他
        result_info['other_effect'].append(stat_text_one_line)

    return result_info


def get_weapon_kire(td_obj):
    result_info = OrderedDict()
    for k_num in range(0, 6):
        result_info['kire_%d' % k_num] = []

    kcon_obj = td_obj.find('.kcon')
    # 循环几个斩味
    kbox_obj_group = kcon_obj('.kbox')
    for kbox_index in range(len(kbox_obj_group)):
        kbox_obj = kbox_obj_group.eq(kbox_index)

        kbox_span_title_num = int(kbox_obj.text())
        temp_kbox_data = {}
        # 先获取都有哪些斩味级别，分别多少斩味
        # 最后然后再整理成一个list
        kbox_span_group = kbox_obj('span')
        for span_index in range(len(kbox_span_group)):
            kbox_span_obj = kbox_span_group.eq(span_index)
            class_text = kbox_span_obj.attr('class')
            style_text = kbox_span_obj.attr('style')

            kr_rank = int(class_text.replace('kr', ''))
            kr_width = int(int(style_text.replace('width:', '').replace('px;', '')) / 0.4)

            temp_kbox_data[kr_rank] = kr_width
        # 整理成list
        kr_list = []
        for rank_num in range(0, 8):
            if rank_num in temp_kbox_data:
                kr_list.append(temp_kbox_data[rank_num])
            else:
                kr_list.append(0)
        result_info['kire_%d' % kbox_span_title_num] = kr_list
    return result_info


# 获取弓的瓶子信息
BOTTLE_POS_MAP = {
    '接': 0,
    '強': 1,
    '麻': 2,
    '毒': 3,
    '睡': 4,
    '爆': 5,
}


def get_weapon_bow_stat(td_obj):
    # 依次是接、强、麻、毒、睡、爆
    result_info = OrderedDict([
        ('bottle', [0, 0, 0, 0, 0, 0])
    ])
    colored_span_groups = td_obj('div>p>span').find('span')

    for span_index in range(len(colored_span_groups)):
        span_obj = colored_span_groups.eq(span_index)
        if span_obj.hasClass('c_g'):
            result_info['bottle'][BOTTLE_POS_MAP[span_obj.text()]] = 1
        elif span_obj.hasClass('c_r'):
            result_info['bottle'][BOTTLE_POS_MAP[span_obj.text()]] = 2

    return result_info


# 获取轻弩重弩的子弹情况
def get_weapon_gun_stat(td_obj):
    result_info = OrderedDict([
        ('b_rapid', []),  # 速射的子弹类型
        ('b_auto_fill', []),  # 自动装填的子弹类型
        ('b_normal', [0, 0, 0]),  # 通常
        ('b_through', [0, 0, 0]),  # 贯通
        ('b_scatter', [0, 0, 0]),  # 散弹
        ('b_pierce', [0, 0, 0]),  # 徹甲
        ('b_cluster', [0, 0, 0]),  # 扩散
        ('b_recover', [0, 0]),  # 回复
        ('b_poison', [0, 0]),  # 毒
        ('b_para', [0, 0]),  # 麻痹
        ('b_sleep', [0, 0]),  # 睡眠
        ('b_stun', [0, 0]),  # 减气
        ('b_flame', 0),  # 火
        ('b_water', 0),  # 水
        ('b_thunder', 0),  # 雷
        ('b_freeze', 0),  # 冰
        ('b_dragon', 0),  # 龙
        ('b_cut', 0),  # 斩裂弹
        ('b_ryu', 0),  # 龙击弹
        ('b_atk', 0),  # 鬼人
        ('b_def', 0),  # 硬化
        ('b_catch', 0),  # 捕捉
    ])

    mhwg_b_order_list = ['b_normal', 'b_recover', 'b_flame', 'b_cut',
                         'b_through', 'b_poison', 'b_water', 'b_ryu',
                         'b_scatter', 'b_para', 'b_freeze', 'b_atk',
                         'b_pierce', 'b_sleep', 'b_thunder', 'b_def',
                         'b_cluster', 'b_stun', 'b_dragon', 'b_catch']

    index = -1
    b_td_groups = td_obj.find('td')
    for b_type in mhwg_b_order_list:
        if type(result_info[b_type]) == list:
            for b_index in range(0, len(result_info[b_type])):
                index += 1
                if b_td_groups.eq(index).text() not in ['', '-']:
                    result_info[b_type][b_index] = int(b_td_groups.eq(index).text())
                    if b_td_groups.eq(index).has_class('bt3'):
                        result_info['b_rapid'].append('%s#%d' % (b_type, b_index+1))
                    if b_td_groups.eq(index).has_class('bt4'):
                        result_info['b_auto_fill'].append('%s#%d' % (b_type, b_index+1))
        else:
            index += 1
            if b_td_groups.eq(index).text() not in ['',  '-']:
                result_info[b_type] = int(b_td_groups.eq(index).text())
                if b_td_groups.eq(index).has_class('bt3'):
                    result_info['b_rapid'].append(b_type)
                if b_td_groups.eq(index).has_class('bt4'):
                    result_info['b_auto_fill'].append(b_type)

    return result_info


# craft_type 为“强化”或是“生产”
def get_material_info(material_text, craft_type):
    result_info = OrderedDict([
        (craft_type + '_cost', 0),
        (craft_type + '_m1', ''),
        (craft_type + '_n1', 0),
        (craft_type + '_m2', ''),
        (craft_type + '_n2', 0),
        (craft_type + '_m3', ''),
        (craft_type + '_n3', 0),
        (craft_type + '_m4', ''),
        (craft_type + '_n4', 0),
    ])

    material_index = 0

    if material_text != '':
        for upgrade_one_item_text in material_text.split('\n'):
            upgrade_one_item_text = upgrade_one_item_text.strip()
            if upgrade_one_item_text[-1:] == 'z':
                result_info[craft_type + '_cost'] = int(upgrade_one_item_text[:-1])
            else:
                find = re.findall(r'(.+?)\s?x(\d+)', upgrade_one_item_text)
                if find:
                    material_index += 1
                    result_info['%s_m%d' % (craft_type, material_index)] = find[0][0]
                    result_info['%s_n%d' % (craft_type, material_index)] = int(find[0][1])
    return result_info


def generate_weapon_excel(weapon_all_data):
    k_max = 6
    m_num_max = 6

    # 生成excel数据
    for weapon_type, weapon_type_data in weapon_all_data.items():
        headers = OrderedDict()
        contents = OrderedDict()

        # headers[weapon_type] = ['_index']
        headers[weapon_type] = ['name_jp', 'name_chs', 'derive', 'derive_index', 'pos']
        contents[weapon_type] = OrderedDict()

        total_index = 0
        for weapon_name, weapon_data in weapon_type_data.items():
            # 整理数据
            total_index += 1
            # weapon_data['_index'] = total_index

            # # 拆分斩味数据
            # for i in range(k_max):
            #     weapon_data['斩味+%d' % i] = weapon_data['斩味'][i] if i < len(weapon_data['斩味']) else []
            # del weapon_data['斩味']
            #
            # # 拆分素材数据
            # for m_type in ['强化', '生产']:
            #     if '%s素材' % m_type in weapon_data:
            #         for i in range(m_num_max):
            #             weapon_data['%s素材%d' % (m_type, i + 1)] = weapon_data['%s素材' % m_type][i]['素材名'] if i < len(
            #                 weapon_data['%s素材' % m_type]) else ''
            #             weapon_data['%s素材数量%d' % (m_type, i + 1)] = weapon_data['%s素材' % m_type][i]['数量'] if i < len(
            #                 weapon_data['%s素材' % m_type]) else ''
            #         del weapon_data['%s素材' % m_type]

            # 调整数据
            # 重新生成数据表
            temp_weapon_data = OrderedDict()
            for data_key, data_value in weapon_data.items():
                use_header = data_key
                if type(data_value) == list:
                    use_header = '%s[]' % data_key
                    data_value = ';'.join([str(value) for value in data_value])
                elif type(data_value) not in [int, float, bool, str]:
                    data_value = str(data_value)
                temp_weapon_data[use_header] = data_value

                if use_header not in headers[weapon_type]:
                    headers[weapon_type].append(use_header)

            contents[weapon_type][weapon_name] = temp_weapon_data

        save_filepath = os.path.join('武器_%s.xlsx' % weapon_type)
        save_to_excel(headers, contents, save_filepath)
        log('武器 %s 数据保存完毕' % weapon_type)


def output_weapon_name_excel(weapon_all_data):
    sheet_name = '译名对照'

    # 武器excel
    headers = OrderedDict()
    contents = OrderedDict()
    headers[sheet_name] = ['_index', '类型', '日文名', '中文名']
    contents[sheet_name] = OrderedDict()

    # 素材excel
    headers_item = OrderedDict()
    contents_item = OrderedDict()
    headers_item[sheet_name] = ['_index', '日文名', '中文名']
    contents_item[sheet_name] = OrderedDict()

    item_name_list = []

    total_index = 0
    total_item_index = 0
    for weapon_type, weapon_type_data in weapon_all_data.items():
        for weapon_name, weapon_data in weapon_type_data.items():
            # 整理数据
            total_index += 1
            contents[sheet_name][weapon_name] = {
                '_index': total_index,
                '类型': weapon_type,
                '日文名': weapon_name,
                '中文名': '',
            }
            for craft_type in ['upgrade', 'craft']:
                for i in range(1, 5):
                    craft_key = '%s_m%d' % (craft_type, i)
                    if craft_key in weapon_data:
                        item_name = weapon_data[craft_key]
                        if item_name not in item_name_list:
                            item_name_list.append(item_name)
                            total_item_index += 1
                            contents_item[sheet_name][total_item_index] = {
                                '_index': total_item_index,
                                '日文名': item_name,
                                '中文名': '',
                            }

    save_filepath = os.path.join('weapon_name.xlsx')
    save_to_excel(headers, contents, save_filepath)
    save_filepath = os.path.join('item_name.xlsx')
    save_to_excel(headers_item, contents_item, save_filepath)
    log('译名表保存完毕。')


if __name__ == '__main__':
    run_job()
