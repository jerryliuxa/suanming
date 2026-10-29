# -*- coding: utf-8 -*-
"""紫微斗数排盘：命宫身宫、五行局、安紫微诸星、四化、十二宫、大限。

流派说明：
- 以农历（含闰月）生日与生时排盘；闰月默认整月归本月（各派对闰月处理略有差异）；
- 火星铃星按「年支组起宫顺数生时」之常法；未含诸星庙旺亮度与博士十二神，后续版本扩展。
"""

from .constants import GAN, ZHI, nayin_of, LUSHEN, WUHU
from . import texts as T

# 十四主星特质
STAR_TRAIT = {
    "紫微": "帝座之星，气度雍容，天生带领导气场，喜发号施令亦能担当。",
    "天机": "智多星，心思灵敏，善于谋略策划，宜幕僚、企划、技术之路。",
    "太阳": "博爱之光，热情外放，乐于付出，名利心重且闲不住。",
    "武曲": "财星刚毅，执行果决，重实际讲效率，财官双美但略显孤刚。",
    "天同": "福星温和，乐天知命，享受生活，感情丰富，安逸中自有福气。",
    "廉贞": "囚星敢作敢为，EQ 高、交际手腕强，能文能武，桃花色彩浓。",
    "天府": "库星稳重，保守务实，善于积累与统筹，是天生的管理者。",
    "太阴": "月华之星，温柔细腻，重情感爱干净，宜文教、财务、艺文。",
    "贪狼": "欲望之星，多才多艺应酬一流，人生课题在于专注与节制。",
    "巨门": "暗星口才佳，好探究质疑，靠口吃饭，慎防是非口舌。",
    "天相": "印星辅佐，端正稳重，乐于助人善协调，是最佳执行伙伴。",
    "天梁": "荫星老成，有长者风范，喜照顾人、讲道理，逢凶有解。",
    "七杀": "将星冲劲十足，人生大起大落，开创力强，宜拼搏不宜守成。",
    "破军": "耗星先破后立，不安现状、破旧开新，变动中求富贵。",
}

SIXI_HUA = {
    0: ("廉贞", "破军", "武曲", "太阳"),
    1: ("天机", "天梁", "紫微", "太阴"),
    2: ("天同", "天机", "文昌", "廉贞"),
    3: ("太阴", "天同", "天机", "巨门"),
    4: ("贪狼", "太阴", "右弼", "天机"),
    5: ("武曲", "贪狼", "天梁", "文曲"),
    6: ("太阳", "武曲", "太阴", "天同"),
    7: ("巨门", "太阳", "文曲", "文昌"),
    8: ("天梁", "紫微", "左辅", "武曲"),
    9: ("破军", "巨门", "太阴", "贪狼"),
}
HUA_NAMES = ["化禄", "化权", "化科", "化忌"]

MAJOR_ORDER = ["紫微", "天机", "太阳", "武曲", "天同", "廉贞",
               "天府", "太阴", "贪狼", "巨门", "天相", "天梁", "七杀", "破军"]

PALACES = ["命宫", "兄弟", "夫妻", "子女", "财帛", "疾厄",
           "迁移", "交友", "官禄", "田宅", "福德", "父母"]

NAYIN_JU = {"水": ("水二局", 2), "木": ("木三局", 3), "金": ("金四局", 4),
            "土": ("土五局", 5), "火": ("火六局", 6)}


def _mirror(pos):
    """紫微-天府 关于寅申轴对称。"""
    return (4 - pos) % 12


def find_ziwei(day, ju_num):
    """由生日与局数定紫微落宫（寅=2 起数，返回地支索引）。"""
    b = (ju_num - day % ju_num) % ju_num   # 借数
    shang = (day + b) // ju_num
    pos = (2 + shang - 1) % 12
    if b % 2 == 1:                          # 借数奇退偶进
        pos = (pos - b) % 12
    elif b > 0:
        pos = (pos + b) % 12
    return pos, b, shang


def paipan_ziwei(ly, month, leap, day, hour_zhi, gender="male"):
    """紫微排盘。ly: 农历年标签（春节所在公历年）；hour_zhi: 0=子时。"""
    leap = bool(leap)
    y_gz = (ly - 1984) % 60
    y_gan = y_gz % 10
    yang_year = y_gan % 2 == 0

    # 命宫 / 身宫
    ming = (2 + (month - 1) - hour_zhi) % 12
    shen = (2 + (month - 1) + hour_zhi) % 12

    # 命宫干支 → 五行局（纳音）
    m_gan = (WUHU[y_gan] + (ming - 2) % 12) % 10
    from .constants import GZ60
    m_gz = GZ60.index(GAN[m_gan] + ZHI[ming])
    na = nayin_of(m_gz)
    na_wx = na[-1]
    ju_name, ju = NAYIN_JU[na_wx]

    # 安紫微
    zw, jie_shu, shang = find_ziwei(day, ju)

    stars = {s: None for s in MAJOR_ORDER}
    stars["紫微"] = zw
    stars["天机"] = (zw - 1) % 12
    stars["太阳"] = (zw - 3) % 12
    stars["武曲"] = (zw - 4) % 12
    stars["天同"] = (zw - 5) % 12
    stars["廉贞"] = (zw - 8) % 12
    tf = _mirror(zw)
    stars["天府"] = tf
    stars["太阴"] = (tf + 1) % 12
    stars["贪狼"] = (tf + 2) % 12
    stars["巨门"] = (tf + 3) % 12
    stars["天相"] = (tf + 4) % 12
    stars["天梁"] = (tf + 5) % 12
    stars["七杀"] = (tf + 6) % 12
    stars["破军"] = (tf + 10) % 12

    # 时系 / 月系 / 年干系 / 年支系
    helpers = {
        "文昌": (10 - hour_zhi) % 12,
        "文曲": (4 + hour_zhi) % 12,
        "左辅": (4 + (month - 1)) % 12,
        "右弼": (10 - (month - 1)) % 12,
        "禄存": LUSHEN[y_gan],
        "擎羊": (LUSHEN[y_gan] + 1) % 12,
        "陀罗": (LUSHEN[y_gan] - 1) % 12,
    }
    from .constants import _YIMA
    grp = None
    for g_set in _YIMA:
        if (y_gz % 12) in g_set:
            helpers["天马"] = _YIMA[g_set]
            break
    qing = {(8, 0, 4): (2, 10), (2, 6, 10): (1, 3), (5, 9, 1): (3, 10), (11, 3, 7): (9, 10)}
    for g_set, (huo, ling) in qing.items():
        if (y_gz % 12) in g_set:
            helpers["火星"] = (huo + hour_zhi) % 12
            helpers["铃星"] = (ling + hour_zhi) % 12
            break
    helpers["地空"] = (11 - hour_zhi) % 12
    helpers["地劫"] = (11 + hour_zhi) % 12
    qk = {0: (1, 7), 4: (1, 7), 1: (0, 8), 5: (0, 8), 2: (11, 9), 3: (11, 9),
          8: (3, 5), 9: (3, 5), 7: (6, 2)}
    kui, yue = qk[y_gan] if y_gan in qk else (6, 2)   # 辛年: 午寅
    if y_gan == 7:
        kui, yue = 6, 2
    helpers["天魁"] = kui
    helpers["天钺"] = yue

    # 四化
    hua_stars = SIXI_HUA[y_gan]
    hua_map = dict(zip(hua_stars, HUA_NAMES))

    # 十二宫（命宫逆布）
    palaces = []
    for i, name in enumerate(PALACES):
        pos = (ming - i) % 12
        major = [s for s in MAJOR_ORDER if stars[s] == pos]
        minor = [s for s, p in helpers.items() if p == pos]
        palaces.append({
            "name": name,
            "pos": pos,
            "branch": ZHI[pos],
            "gan": GAN[(WUHU[y_gan] + (pos - 2) % 12) % 10],
            "major": major,
            "minor": minor,
            "is_shen": pos == shen,
            "limit": None,
        })

    # 大限：命宫起，阳男阴女顺行（父母宫方向），阴男阳女逆行（兄弟宫方向）
    forward = (yang_year and gender == "male") or ((not yang_year) and gender == "female")
    for i in range(12):
        idx = (-i) % 12 if forward else i
        age0 = ju + 10 * i
        palaces[idx]["limit"] = "%d-%d" % (age0, age0 + 9)

    # 借星（无主星之宫借对宫）
    for p in palaces:
        if not p["major"]:
            opp = (p["pos"] + 6) % 12
            for q in palaces:
                if q["pos"] == opp and q["major"]:
                    p["borrowed"] = q["major"]
                    break

    # 命宫批语
    ming_p = palaces[0]
    trait_txt = []
    for s in ming_p["major"]:
        trait_txt.append("%s：%s" % (s, STAR_TRAIT[s]))
    body = "命宫坐%s（%s%s），身宫落%s。" % (
        ZHI[ming], ming_p["gan"], ZHI[ming],
        [p["name"] for p in palaces if p["is_shen"]][0])
    if trait_txt:
        body += "命宫主星：" + "；".join(t.rstrip("。") for t in trait_txt) + "。"
    else:
        body += "命宫无主星，借对宫（%s）之星论性，性情较受迁移宫影响。" % (
            ming_p.get("borrowed") and "、".join(ming_p["borrowed"]) or "－")
    hua_desc = "、".join("%s%s" % (s, h) for s, h in zip(hua_stars, HUA_NAMES))

    return {
        "basic": {
            "lunar": "%d年%s%d月%d日" % (ly, "闰" if leap else "", month, day),
            "hour": "%s时" % ZHI[hour_zhi],
            "gender": "男" if gender == "male" else "女",
            "wuxing_ju": ju_name,
            "ming_gong": ZHI[ming], "shen_gong": ZHI[shen],
            "year_gz": GAN[y_gan] + ZHI[y_gz % 12],
            "direction": "顺行" if forward else "逆行",
        },
        "ziwei_pos": ZHI[zw],
        "palaces": palaces,
        "hua": hua_desc,
        "hua_map": dict(zip(hua_stars, HUA_NAMES)),
        "major_positions": {s: ZHI[p] for s, p in stars.items()},
        "helpers_positions": {s: ZHI[p] for s, p in helpers.items()},
        "brief": body,
        "note": "紫微盘未含诸星亮度、博士十二神与流曜；闰月归属各派略有差异，结果供传统文化研究娱乐参考。",
    }
