# -*- coding: utf-8 -*-
"""奇门遁甲：时家奇门 · 转盘拆补法排盘。

排盘口径：
- 定阴阳遁与局数：以日所在节气定阴阳（冬至后阳遁、夏至后阴遁），
  以最近一个甲/己「符头」日的地支定三元（子午卯酉上元、寅申巳亥中元、辰戌丑未下元），
  按拆补法取该节气的三元局数。
- 地盘：三奇六仪（戊己庚辛壬癸丁丙乙）按局数落宫，阳遁顺布、阴遁逆布。
- 天盘九星、八门转盘顺时针轮转（环形次序不变），八神阳遁顺布、阴遁逆布。
- 甲遁于六仪：时干为甲时按旬首遁干寻宫。
- 中五宫寄坤二宫（天禽寄天芮）。
"""

from datetime import datetime
from . import calendar_cn as cal
from .constants import GAN, ZHI, GZ60, WUSHU

# 九宫：洛书数 -> (卦名, 卦符)
PALACE_GUA = {1: ("坎", "☵"), 2: ("坤", "☷"), 3: ("震", "☳"), 4: ("巽", "☴"),
              5: ("中", "☯"), 6: ("乾", "☰"), 7: ("兑", "☱"), 8: ("艮", "☶"), 9: ("离", "☲")}

# 转盘顺时针宫序（不含中五宫）：坎艮震巽离坤兑乾
CIRCLE = [1, 8, 3, 4, 9, 2, 7, 6]

# 九星本位（按洛书宫）
STARS = {1: "天蓬", 2: "天芮", 3: "天冲", 4: "天辅", 5: "天禽",
         6: "天心", 7: "天柱", 8: "天任", 9: "天英"}
STAR_TRAIT = {
    "天蓬": "水贼之星，胆大智高，利北上投资亦主冒险", "天芮": "病星师道，利结友求学，不利治病求财",
    "天冲": "慈心造化，利征伐竞技，不利嫁娶", "天辅": "文书教化，利考学修文，大吉之星",
    "天禽": "中宫寄芮，端厚忠贞，百事皆宜", "天心": "天医之首，利求医、谋事、隐遁，大吉",
    "天柱": "破坏之星，利固守诉讼，不利远行", "天任": "富屋贵人，利见贵立业，忌 听谗言",
    "天英": "火明之宿，利文书宴乐，不利求财嫁娶",
}

# 八门本位（中五宫无门）
DOORS = {1: "休门", 2: "死门", 3: "伤门", 4: "杜门", 6: "开门", 7: "惊门", 8: "生门", 9: "景门"}
DOOR_TRAIT = {
    "休门": "吉门·水，利见贵求官、婚姻修造，宜静养休息",
    "生门": "吉门·土，最利求财、营造、看病，生意人之门",
    "开门": "吉门·金，利开业求职、上官赴任，一帆风顺之门",
    "伤门": "凶门·木，主伤害搏猎，宜讨债捕猎，余事不利",
    "杜门": "小凶·木，主闭塞，宜躲灾避难、修筑堤防",
    "景门": "小吉·火，利文书考试、献策饮酒，防口舌血光",
    "死门": "大凶·土，主丧亡刑狱，只宜吊丧送葬",
    "惊门": "凶门·金，主惊恐官司，宜捕盗诉讼",
}

# 八神顺序（值符居首，阳遁顺布 / 阴遁逆布）
GODS = ["值符", "腾蛇", "太阴", "六合", "白虎", "玄武", "九地", "九天"]
GOD_TRAIT = {
    "值符": "贵神之首，所到之处百恶消散", "腾蛇": "虚诈惊恐，主怪异缠绕之事",
    "太阴": "荫佑秘密，利暗中谋划、女子之事", "六合": "婚姻和合，利合作中介、交易成婚",
    "白虎": "凶猛刚强，主刀兵疾病道路之凶", "玄武": "盗贼暗昧，主欺诈失窃暧昧",
    "九地": "柔顺安静，利屯兵固守、埋葬", "九天": "志高气扬，利远行出征、扬名上进",
}

# 三奇六仪（甲遁于戊）；阳遁顺布、阴遁逆布
YI_GAN = "戊己庚辛壬癸丁丙乙"
XUN_QIYI = ["戊", "己", "庚", "辛", "壬", "癸"]  # 甲子/甲戌/甲申/甲午/甲辰/甲寅旬遁干

# 节气 -> (上元局, 中元局, 下元局)
JU_TABLE = {
    "冬至": (1, 7, 4), "惊蛰": (1, 7, 4), "小寒": (2, 8, 5),
    "大寒": (3, 9, 6), "春分": (3, 9, 6), "立春": (8, 5, 2),
    "雨水": (9, 6, 3), "清明": (4, 1, 7), "立夏": (4, 1, 7),
    "谷雨": (5, 2, 8), "小满": (5, 2, 8), "芒种": (6, 3, 9),
    "夏至": (9, 3, 6), "白露": (9, 3, 6), "小暑": (8, 2, 5),
    "大暑": (7, 1, 4), "秋分": (7, 1, 4), "立秋": (2, 5, 8),
    "处暑": (1, 4, 7), "寒露": (6, 9, 3), "立冬": (6, 9, 3),
    "霜降": (5, 8, 2), "小雪": (5, 8, 2), "大雪": (4, 7, 1),
}

# 阳遁节气集合（冬至…芒种）
YANG_TERMS = ["冬至", "小寒", "大寒", "立春", "雨水", "惊蛰", "春分", "清明", "谷雨",
              "立夏", "小满", "芒种"]

# 对冲宫（反吟）
OPPOSITE = {1: 9, 9: 1, 2: 8, 8: 2, 3: 7, 7: 3, 4: 6, 6: 4, 5: 5}

# 驿马：时支 -> 马星支
YIMA = {2: 8, 8: 2, 6: 0, 0: 6, 9: 3, 3: 9, 5: 11, 11: 5, 1: 7, 7: 1, 4: 10, 10: 4}


def dipan(ju, yang):
    """地盘：{宫: 仪干}。戊起局宫，阳遁顺布、阴遁逆布。"""
    order = list(range(1, 10)) if yang else list(range(9, 0, -1))
    idx = order.index(ju)
    return {order[(idx + k) % 9]: g for k, g in enumerate(YI_GAN)}


def _xun_of(gz):
    """干支索引 -> (旬首索引, 旬名)。"""
    x = gz - gz % 10
    return x, GZ60[x] + "旬"


def _xunkong(gz):
    """时辰旬空（两支索引）。"""
    x = gz - gz % 10
    first_zhi = x % 12
    return ((first_zhi + 10) % 12, (first_zhi + 11) % 12)


def _rotate(circle_items, target_palace, mover_item):
    """转盘：把 mover_item 转到 target_palace，环形次序不变。

    circle_items: 与 CIRCLE 对齐的物品列表；返回 {宫: 物品}（8 宫）。
    """
    i = circle_items.index(mover_item)
    t = CIRCLE.index(target_palace)
    out = {}
    for j, item in enumerate(circle_items):
        out[CIRCLE[(j - i + t) % 8]] = item
    return out


def _layout(yang, ju, day_gz, hour_gz):
    """给定阴阳遁、局数、日柱/时柱干支索引，排出完整盘（内部纯函数，便于测试）。"""
    dp = dipan(ju, yang)
    pal_of_gan = {v: k for k, v in dp.items()}

    xun_i, xun_name = _xun_of(hour_gz)
    qiyi = XUN_QIYI[xun_i // 10]                 # 旬首遁干
    yuan_gong = pal_of_gan[qiyi]                 # 旬首干所在宫（原始宫）
    zhi_fu_star = STARS[yuan_gong]               # 值符星（五宫为天禽）
    zhi_shi_door = DOORS.get(yuan_gong, "死门")  # 值使门（五宫寄坤二，死门）
    yuan_door_gong = 2 if yuan_gong == 5 else yuan_gong

    hgan_i = hour_gz % 10
    hour_gan = GAN[hgan_i]
    # 时干寻宫：甲遁于旬首仪；落中五宫寄坤二
    seek_gan = qiyi if hour_gan == "甲" else hour_gan
    raw_target = pal_of_gan[seek_gan]
    target = 2 if raw_target == 5 else raw_target

    # ---- 天盘九星（转盘，天禽寄天芮）----
    circle_stars = [STARS[p] for p in CIRCLE]          # 禽不入环，寄芮
    mover = "天芮" if zhi_fu_star == "天禽" else zhi_fu_star
    star_pos = _rotate(circle_stars, target, mover)
    # 天盘干：星携带其本宫地盘干；天禽的干（五宫）随芮而行
    star_dipan_gan = {s: [dp[p]] for p, s in STARS.items()}
    star_dipan_gan["天芮"].append(dp[5])               # 禽干寄芮
    tian_gan = {g: list(star_dipan_gan[s]) for g, s in star_pos.items()}
    rui_gong = next(g for g, s in star_pos.items() if s == "天芮")

    # ---- 八门（值使随时辰行宫，其余随环转动）----
    delta = hour_gz - xun_i                            # 旬首时辰至此经过的时辰数
    step = delta if yang else -delta
    door_gong = ((yuan_door_gong - 1 + step) % 9 + 9) % 9 + 1
    door_note = ""
    if door_gong == 5:
        door_gong, door_note = 2, "（值使落中五宫，寄坤二）"
    circle_doors = [DOORS[p] for p in CIRCLE]
    door_pos = _rotate(circle_doors, door_gong, zhi_shi_door)

    # ---- 八神（天盘值符所临宫起布，阳顺阴逆）----
    god_pos = {}
    start = CIRCLE.index(target)
    order = range(8) if yang else range(7, -1, -1)
    for k, idx in enumerate(order):
        god_pos[CIRCLE[(start + k) % 8]] = GODS[idx]

    # ---- 格局 ----
    patterns = []
    if raw_target == yuan_gong:
        patterns.append("星门伏吟：天盘与地盘重叠，主事情停滞、宜静不宜动，守旧待时。")
    elif OPPOSITE.get(raw_target) == yuan_gong:
        patterns.append("星门反吟：天地盘对冲，主反复不定、事多颠倒，速成速败。")
    fuyin_gan = [g for g in range(1, 10)
                 if g != 5 and tian_gan[g][0] == dp[g]]
    if len(fuyin_gan) >= 4 and not patterns:
        patterns.append("多宫干伏吟：天地盘干相同者众，诸事迟滞，宜守常。")

    xunkong = _xunkong(hour_gz)
    ma_zhi = YIMA[hour_gz % 12]

    return {
        "yang": yang, "ju": ju, "dp": dp, "tian_gan": tian_gan,
        "star_pos": star_pos, "door_pos": door_pos, "god_pos": god_pos,
        "rui_gong": rui_gong, "xun_name": xun_name, "qiyi": qiyi,
        "zhi_fu_star": zhi_fu_star, "zhi_shi_door": zhi_shi_door,
        "zhi_fu_gong": target, "zhi_shi_gong": door_gong,
        "xunkong": xunkong, "ma_zhi": ma_zhi, "patterns": patterns,
        "door_note": door_note, "hour_gan": hour_gan,
    }


def _find_day_context(y, m, d, hour):
    """定日柱、时柱、节气、阴阳遁、三元、局数（拆补法）。"""
    from datetime import timedelta
    if hour is None:
        hour = 12                                       # 缺省按午时
    day_jdn_shift = 1 if hour == 23 else 0          # 23 点后日柱进次日（换日派）
    base = datetime(y, m, d) + timedelta(days=day_jdn_shift)
    day_gz = cal.day_gz_index(base.year, base.month, base.day)

    now = datetime(y, m, d, hour)
    # 当前节气（含上年大雪起）
    bounds = []
    for yy in (y - 1, y):
        for name, t in cal.jieqi_table(yy):
            bounds.append((t, name))
    bounds.sort()
    term = bounds[0][1]
    for t, name in bounds:
        if t <= now:
            term = name
        else:
            break
    yang = term in YANG_TERMS

    # 符头：最近一个甲/己日
    back = 0
    while True:
        gi = (day_gz - back) % 60
        if gi % 10 in (0, 5):
            break
        back += 1
    futou_gz = (day_gz - back) % 60
    futou_zhi = futou_gz % 12
    # 符头支定三元：子午卯酉上元、寅申巳亥中元、辰戌丑未下元
    if futou_zhi in (0, 6, 3, 9):       # 子 午 卯 酉
        yuan_i = 0
    elif futou_zhi in (2, 8, 5, 11):    # 寅 申 巳 亥
        yuan_i = 1
    else:                               # 辰 戌 丑 未
        yuan_i = 2
    ju = JU_TABLE[term][yuan_i]
    yuan_name = ("上元", "中元", "下元")[yuan_i]
    futou_name = GZ60[futou_gz]

    # 时柱
    hz = ((hour + 1) // 2) % 12
    hg = (WUSHU[day_gz % 10] + hz) % 10
    hour_gz = cal.gz_index(hg, hz)
    return day_gz, hour_gz, term, yang, ju, yuan_name, futou_name, base


def paipan_qimen(y, m, d, hour):
    """时家奇门排盘主入口。y/m/d 公历，hour 0-23（可为 None，默认午时）。"""
    day_gz, hour_gz, term, yang, ju, yuan_name, futou_name, base = _find_day_context(y, m, d, hour)
    lay = _layout(yang, ju, day_gz, hour_gz)

    hz = hour_gz % 12
    xk = lay["xunkong"]
    ma = lay["ma_zhi"]

    # 逐宫信息
    palaces = []
    for g in range(1, 10):
        gua, sym = PALACE_GUA[g]
        star = lay["star_pos"].get(g)
        if g == 5:
            star = "天禽（寄坤二）"
        elif g == lay["rui_gong"]:
            star = "天芮禽"
        palaces.append({
            "gong": g, "gua": gua, "sym": sym,
            "star": star,
            "door": lay["door_pos"].get(g),
            "god": lay["god_pos"].get(g) if g != 5 else None,
            "tian_gan": "".join(lay["tian_gan"].get(g, [])),
            "di_gan": lay["dp"][g],
        })

    # ---- 分析段落 ----
    zg, zs = lay["zhi_fu_gong"], lay["zhi_shi_gong"]
    paragraphs = []
    paragraphs.append(
        "本盘为【%s遁%s局】（%s%s），起课时间 %s 年 %s 月 %s 日 %s，日柱【%s】、时柱【%s】。"
        "时辰%s，旬首遁【%s】，值符【%s】落%s宫，值使【%s】落%s宫%s。空亡在%s与%s，驿马星在%s。" % (
            "阳" if yang else "阴", ju, term, yuan_name,
            base.year, base.month, base.day, ZHI[hz] + "时",
            GZ60[day_gz], GZ60[hour_gz], lay["xun_name"], lay["qiyi"],
            lay["zhi_fu_star"], PALACE_GUA[zg][0], lay["zhi_shi_door"],
            PALACE_GUA[zs][0], lay["door_note"],
            ZHI[xk[0]], ZHI[xk[1]], ZHI[ma]))
    jdoors = ("开门", "休门", "生门")
    good_doors = [(g, d) for g, d in lay["door_pos"].items() if d in jdoors]
    good_txt = "、".join("%s（%s宫）" % (d, PALACE_GUA[g][0]) for g, d in sorted(good_doors, key=lambda x: x[0]))
    paragraphs.append(
        "三门落宫：%s。择方而动：出行、谈判、开业可优先朝吉门所在方位行事；"
        "凶门（死、惊、伤）所临方位宜静不宜动。" % (good_txt or "暂无三吉门落于八宫"))
    fu = lay["zhi_fu_star"]
    paragraphs.append(
        "值符星【%s】：%s。值使门【%s】：%s。"
        "值符为全盘之主，看其落宫与时干的关系断大事走向；值使主事之进程，看其落宫旺衰断成败快慢。" % (
            fu, STAR_TRAIT[fu], lay["zhi_shi_door"], DOOR_TRAIT[lay["zhi_shi_door"]]))
    if lay["patterns"]:
        paragraphs.append("格局提示：" + "".join(lay["patterns"]))
    else:
        paragraphs.append("本盘无伏吟反吟，天地盘动静相宜，事情按部就班推进。")
    paragraphs.append(
        "用法提示：问事以「用神」落宫为核心——问自身看日干落宫，问他人看时干落宫，"
        "问财看生门与戊土落宫，问事业官运看开门与值符落宫，问疾病看天芮落宫。"
        "用神宫得吉门吉神旺相则事顺，临凶门凶神或落空亡则事阻。空亡之宫（%s、%s）主事虚难成，"
        "马星之宫（%s）主动变出行。" % (ZHI[xk[0]], ZHI[xk[1]], ZHI[ma]))

    return {
        "mode": "qimen",
        "date_text": "%d-%02d-%02d" % (y, m, d),
        "hour_zhi": ZHI[hz],
        "day_gz": GZ60[day_gz],
        "hour_gz": GZ60[hour_gz],
        "dun": "阳遁" if yang else "阴遁",
        "ju": ju,
        "ju_name": "%s%s局" % ("阳遁" if yang else "阴遁", ju),
        "term": term, "yuan": yuan_name, "futou": futou_name,
        "xun": lay["xun_name"], "qiyi": lay["qiyi"],
        "zhi_fu": {"star": lay["zhi_fu_star"], "gong": zg, "gua": PALACE_GUA[zg][0]},
        "zhi_shi": {"door": lay["zhi_shi_door"], "gong": zs, "gua": PALACE_GUA[zs][0],
                    "note": lay["door_note"]},
        "xunkong": [ZHI[xk[0]], ZHI[xk[1]]],
        "yima": ZHI[ma],
        "patterns": lay["patterns"],
        "palaces": palaces,
        "paragraphs": paragraphs,
        "note": "时家奇门采用转盘拆补法，中五宫寄坤二；流派之间在置闰与寄宫上略有差异，"
                "结果供传统文化研究娱乐参考，不构成任何决策依据。",
    }
