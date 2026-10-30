# -*- coding: utf-8 -*-
"""六爻预测（火珠林法）：摇卦/时间起卦 → 纳甲装卦 → 六亲六兽世应 → 规则断语。

起卦口径：
- 摇卦：用户输入六次铜钱结果（自初爻向上），每爻取值 6/7/8/9
  （6 老阴×、7 少阳—、8 少阴--、9 老阳○），6/9 为动爻。
- 时间起卦：按梅花体例以农历年月日+时辰数取上下卦与动爻。
装卦：京房纳甲（乾金甲子外壬午、坎水戊寅外戊申……），
以本宫五行为我定六亲，以日干起六兽，八宫卦序定世应。
"""

from datetime import datetime

from . import calendar_cn as cal
from .constants import GAN, ZHI, GZ60, ZHI_WX, WUSHU

# 八卦三爻（自初爻起，1=阳 0=阴）
TRI_BITS = {"乾": (1, 1, 1), "兑": (1, 1, 0), "离": (1, 0, 1), "震": (1, 0, 0),
            "巽": (0, 1, 1), "坎": (0, 1, 0), "艮": (0, 0, 1), "坤": (0, 0, 0)}
TRI_SYM = {"乾": "☰", "兑": "☱", "离": "☲", "震": "☳",
           "巽": "☴", "坎": "☵", "艮": "☶", "坤": "☷"}

HEX_NAMES = {
    "乾": {"乾": "乾为天", "兑": "天泽履", "离": "天火同人", "震": "天雷无妄", "巽": "天风姤", "坎": "天水讼", "艮": "天山遁", "坤": "天地否"},
    "兑": {"乾": "泽天夬", "兑": "兑为泽", "离": "泽火革", "震": "泽雷随", "巽": "泽风大过", "坎": "泽水困", "艮": "泽山咸", "坤": "泽地萃"},
    "离": {"乾": "火天大有", "兑": "火泽睽", "离": "离为火", "震": "火雷噬嗑", "巽": "火风鼎", "坎": "火水未济", "艮": "火山旅", "坤": "火地晋"},
    "震": {"乾": "雷天大壮", "兑": "雷泽归妹", "离": "雷火丰", "震": "震为雷", "巽": "雷风恒", "坎": "雷水解", "艮": "雷山小过", "坤": "雷地豫"},
    "巽": {"乾": "风天小畜", "兑": "风泽中孚", "离": "风火家人", "震": "风雷益", "巽": "巽为风", "坎": "风水涣", "艮": "风山渐", "坤": "风地观"},
    "坎": {"乾": "水天需", "兑": "水泽节", "离": "水火既济", "震": "水雷屯", "巽": "水风井", "坎": "坎为水", "艮": "水山蹇", "坤": "水地比"},
    "艮": {"乾": "山天大畜", "兑": "山泽损", "离": "山火贲", "震": "山雷颐", "巽": "山风蛊", "坎": "山水蒙", "艮": "艮为山", "坤": "山地剥"},
    "坤": {"乾": "地天泰", "兑": "地泽临", "离": "地火明夷", "震": "地雷复", "巽": "地风升", "坎": "地水师", "艮": "地山谦", "坤": "坤为地"},
}

# 京房纳甲：内卦/外卦各三爻（初→三 / 四→上），(天干, 地支)
NAJIA_IN = {
    "乾": [("甲", "子"), ("甲", "寅"), ("甲", "辰")],
    "坎": [("戊", "寅"), ("戊", "辰"), ("戊", "午")],
    "艮": [("丙", "辰"), ("丙", "午"), ("丙", "申")],
    "震": [("庚", "子"), ("庚", "寅"), ("庚", "辰")],
    "巽": [("辛", "丑"), ("辛", "亥"), ("辛", "酉")],
    "离": [("己", "卯"), ("己", "丑"), ("己", "亥")],
    "坤": [("乙", "未"), ("乙", "巳"), ("乙", "卯")],
    "兑": [("丁", "巳"), ("丁", "卯"), ("丁", "丑")],
}
NAJIA_OUT = {
    "乾": [("壬", "午"), ("壬", "申"), ("壬", "戌")],
    "坎": [("戊", "申"), ("戊", "戌"), ("戊", "子")],
    "艮": [("丙", "戌"), ("丙", "子"), ("丙", "寅")],
    "震": [("庚", "午"), ("庚", "申"), ("庚", "戌")],
    "巽": [("辛", "未"), ("辛", "巳"), ("辛", "卯")],
    "离": [("己", "酉"), ("己", "未"), ("己", "巳")],
    "坤": [("癸", "丑"), ("癸", "亥"), ("癸", "酉")],
    "兑": [("丁", "亥"), ("丁", "酉"), ("丁", "未")],
}

# 八宫五行
PALACE_WX = {"乾": "金", "兑": "金", "离": "火", "震": "木",
             "巽": "木", "坎": "水", "艮": "土", "坤": "土"}

SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

# 六神起法：日干 -> 初爻六神，自初爻向上依 青龙朱雀勾陈腾蛇白虎玄武 轮转
SIX_GODS = ["青龙", "朱雀", "勾陈", "腾蛇", "白虎", "玄武"]
GOD_START = {"甲": 0, "乙": 0, "丙": 1, "丁": 1, "戊": 2, "己": 3, "庚": 4, "辛": 4, "壬": 5, "癸": 5}

# 用神取法：事项 -> 用神六亲（婚姻另分男女）
CATEGORY_YONGSHEN = {
    "general": ("世爻", "问事无专类，以世爻为自占之主"),
    "wealth": ("妻财", "求财以妻财为用神，兼看子孙（财之源）"),
    "career": ("官鬼", "事业功名以官鬼为用神，兼看父母（文书）"),
    "marriage_m": ("妻财", "男占婚姻以妻财为用神（妻之象）"),
    "marriage_f": ("官鬼", "女占婚姻以官鬼为用神（夫之象）"),
    "study": ("父母", "考试学业以父母爻为用神（文书成绩）"),
    "health": ("官鬼", "自占疾病以官鬼为病、子孙为医药，先看官鬼兴衰"),
    "lost": ("妻财", "寻物寻人以财或应爻为用，兼看世应生克"),
    "travel": ("父母", "出行以父母为行李文书，世爻为行人，宜世动或应生世"),
    "lawsuit": ("官鬼", "官司诉讼以官鬼为用，世为我方、应为对方"),
}

YAO_WX_CACHE = {}


def _bits_to_name(bits6):
    lower = next(t for t, b in TRI_BITS.items() if tuple(bits6[0:3]) == b)
    upper = next(t for t, b in TRI_BITS.items() if tuple(bits6[3:6]) == b)
    return upper, lower, HEX_NAMES[upper][lower]


def _build_palace_map():
    """八宫六十四卦：卦(六爻bits元组) -> (宫名, 卦序, 世爻, 应爻)。

    八宫变卦次序：本宫(上爻世)、一世(初爻变)、二世、三世、四世、五世、
    游魂（五世四爻复归）、归魂（游魂内卦还原）。
    """
    changes = [(), (1,), (1, 2), (1, 2, 3), (1, 2, 3, 4), (1, 2, 3, 4, 5), (1, 2, 3, 5), (5,)]
    shi = (6, 1, 2, 3, 4, 5, 4, 3)
    out = {}
    for palace_tri in TRI_BITS:
        base = list(TRI_BITS[palace_tri]) * 2      # 纯卦上下同卦
        for i, ch in enumerate(changes):
            bits = list(base)
            for ln in ch:
                bits[ln - 1] = 1 - bits[ln - 1]
            out[tuple(bits)] = (palace_tri, i, shi[i], ((shi[i] - 1 + 3) % 6) + 1)
    return out


PALACE_MAP = _build_palace_map()


def liu_qin(palace_wx, yao_wx):
    """以卦宫为我定六亲。"""
    if yao_wx == palace_wx:
        return "兄弟"
    if SHENG[yao_wx] == palace_wx:
        return "父母"
    if SHENG[palace_wx] == yao_wx:
        return "子孙"
    if KE[yao_wx] == palace_wx:
        return "官鬼"
    return "妻财"


def zhuang_gua(bits6):
    """纳甲装卦：返回六爻信息（自初爻起）。"""
    upper, lower, name = _bits_to_name(list(bits6))
    palace, pidx, shi, ying = PALACE_MAP[tuple(bits6)]
    pwx = PALACE_WX[palace]
    yaos = []
    for i in range(6):
        if i < 3:
            gan, zhi = NAJIA_IN[lower][i]
        else:
            gan, zhi = NAJIA_OUT[upper][i - 3]
        zhi_i = ZHI.index(zhi)
        wx = ZHI_WX[zhi_i]
        yaos.append({
            "pos": i + 1, "yang": bits6[i] == 1,
            "gan": gan, "zhi": zhi, "wx": wx,
            "liuqin": liu_qin(pwx, wx),
            "is_shi": i + 1 == shi, "is_ying": i + 1 == ying,
        })
    return {"name": name, "upper": upper, "lower": lower, "palace": palace,
            "palace_wx": pwx, "idx": pidx, "shi": shi, "ying": ying, "yaos": yaos}


def qigua_by_time(year, month, day, hour):
    """时间起卦（梅花体例）：农历年月日数起上卦、加时辰数起下卦，总数取动爻。"""
    lunar = cal.lunar_date(year, month, day)
    lm, ld = lunar["num"], lunar["day"]
    ly_zhi = (lunar["ly"] - 1984) % 12
    hz = ((hour + 1) // 2) % 12
    n1 = ((ly_zhi + 1) + lm + ld) % 8 or 8
    n2 = (n1 + hz + 1) % 8 or 8
    dong = (n1 + hz + 1) % 6 or 6
    order = ["乾", "兑", "离", "震", "巽", "坎", "艮", "坤"]
    lines = list(TRI_BITS[order[n2 - 1]]) + list(TRI_BITS[order[n1 - 1]])
    vals = []
    for i in range(6):
        if i + 1 == dong:
            vals.append(9 if lines[i] else 6)
        else:
            vals.append(7 if lines[i] else 8)
    return vals, lunar["text"]


def qigua_by_coins(coin_counts):
    """摇卦：coin_counts 为六次掷币的「背面数」（0-3，自初爻起）。
    3背=老阳9，2背=少阴8，1背=少阳7，0背=老阴6。"""
    table = {3: 9, 2: 8, 1: 7, 0: 6}
    return [table[int(c)] for c in coin_counts]


def _liushen(day_gz, yaos):
    start = GOD_START[GAN[day_gz % 10]]
    for i, y in enumerate(yaos):
        y["god"] = SIX_GODS[(start + i) % 6]


def _yongshen_lines(ben, target):
    """找用神爻：返回本卦中六亲匹配的爻位列表。"""
    return [y["pos"] for y in ben["yaos"] if y["liuqin"] == target]


def _relation(a, b):
    """b 对 a 的作用（a=用神五行, b=日月/动爻五行）。"""
    if a == b:
        return "比扶"
    if SHENG[b] == a:
        return "生"
    if KE[b] == a:
        return "克"
    if SHENG[a] == b:
        return "泄"
    return "耗"


def analyze(mode, vals, y, m, d, hour, category):
    day_gz = cal.day_gz_index(y, m, d)
    mgz, mbranch, jname = cal.month_pillar_at(datetime(y, m, d, 12))
    day_zhi = day_gz % 12
    day_wx = ZHI_WX[day_zhi]
    month_wx = ZHI_WX[mbranch]

    bits = tuple(1 if v in (7, 9) else 0 for v in vals)
    ben = zhuang_gua(bits)
    moving = [i + 1 for i, v in enumerate(vals) if v in (6, 9)]
    bian_bits = tuple(bits[i] ^ 1 if i + 1 in moving else bits[i] for i in range(6))
    bian = zhuang_gua(bian_bits) if moving else None
    _liushen(day_gz, ben["yaos"])

    cat_key = category if category in CATEGORY_YONGSHEN else "general"
    yong_target, yong_note = CATEGORY_YONGSHEN[cat_key]
    yong_pos_list = _yongshen_lines(ben, yong_target) if yong_target not in ("世爻",) else [ben["shi"]]

    # ---- 评分 ----
    score = 60
    notes = []

    if yong_target == "世爻" or not yong_pos_list:
        yong_pos = ben["shi"]
        yong = ben["yaos"][yong_pos - 1]
        if yong_target != "世爻":
            score -= 12
            notes.append("用神%s不上卦，主事情暗昧不明、目标难觅，宜缓图。" % yong_target)
    else:
        yong_pos = yong_pos_list[0]
        yong = ben["yaos"][yong_pos - 1]
        if len(yong_pos_list) > 1:
            notes.append("卦中%s两现，以动者/临世应者为主，多现主事有反复。" % yong_target)
    yong_wx = yong["wx"]

    # 日月作用
    rel_day = _relation(yong_wx, day_wx)
    rel_month = _relation(yong_wx, month_wx)
    for who, rel, up, down in (("日辰", rel_day, 15, 15), ("月建", rel_month, 12, 12)):
        if rel in ("生", "比扶"):
            score += up
            notes.append("用神得%s%s，旺相有力。" % (who, "比扶" if rel == "比扶" else "生"))
        elif rel == "克":
            score -= down
            notes.append("用神被%s克伤，衰弱受制，其事难成或宜退守。" % who)
        elif rel == "泄":
            score -= 6
            notes.append("用神%s泄气，力有外耗。" % who)

    # 世应
    shi_yao = ben["yaos"][ben["shi"] - 1]
    ying_yao = ben["yaos"][ben["ying"] - 1]
    if yong_pos == ben["shi"]:
        score += 10
        notes.append("用神持世，事在己身，得失皆由自己掌握。")
    rel_shi_day = _relation(shi_yao["wx"], day_wx)
    if rel_shi_day in ("生", "比扶"):
        score += 5
        notes.append("世爻得日辰生扶，自身状态尚可。")
    shi_ying_rel = _relation(shi_yao["wx"], ying_yao["wx"])
    if shi_ying_rel in ("生", "比扶"):
        score += 4
        notes.append("应爻生扶世爻（或比和），他人环境对我有情，谋事多助力。")
    elif shi_ying_rel == "克":
        score -= 8
        notes.append("应爻克世，外部环境有压力或对方不情愿。")

    # 动爻
    for p in moving:
        ya = ben["yaos"][p - 1]
        if ya["liuqin"] == yong_target:
            score += 8
            notes.append("第%s爻用神发动（%s爻动），事情主动有变，成败将应于此。" % (p, "老阳" if vals[p - 1] == 9 else "老阴"))
        elif ya["wx"] != yong_wx and SHENG[ya["wx"]] == yong_wx:
            score += 6
            notes.append("第%s爻%s原神（%s）发动生用神，事有生机，贵人暗助。" % (p, ya["god"], ya["liuqin"]))
        elif KE[ya["wx"]] == yong_wx:
            if ya["liuqin"] == "官鬼" and cat_key not in ("career", "lawsuit"):
                notes.append("第%s爻%s官鬼发动克用神，防阻挠、病伤、口舌。" % (p, ya["god"]))
            else:
                notes.append("第%s爻%s%s发动克用神，忌神猖獗，所谋多阻。" % (p, ya["god"], ya["liuqin"]))
            score -= 10

    # 空亡
    xun = day_gz - day_gz % 10
    fz = ZHI[(xun % 12 + 10) % 12], ZHI[(xun % 12 + 11) % 12]
    if yong["zhi"] in fz:
        score -= 12
        notes.append("用神临旬空（%s%s），主心虚无定、事多虚约，待出空或冲空之日方见分晓。" % fz)

    score = max(20, min(95, score))
    grade = ("上吉" if score >= 80 else "吉" if score >= 68 else
             "平" if score >= 55 else "阻" if score >= 42 else "凶")

    # ---- 段落 ----
    paragraphs = []
    paragraphs.append(
        "得【%s】（%s），%s，世爻在%s爻（%s%s，临%s），应爻在%s爻。%s" % (
            ben["name"], ben["palace"] + "宫",
            "静卦" if not moving else "动爻在第" + "、".join(str(x) for x in moving) + "爻",
            ben["shi"], shi_yao["gan"] + shi_yao["zhi"], shi_yao["liuqin"],
            shi_yao["god"], ben["ying"],
            "变出【%s】。" % bian["name"] if bian else "卦无动爻，事态平稳少变。"))
    paragraphs.append("取用：%s。" % yong_note)
    if notes:
        paragraphs.append("断曰：" + "；".join(n.rstrip("。") for n in notes) + "。")
    if bian and moving:
        changed = ["%s爻（%s%s→%s%s）" % (p, ben["yaos"][p - 1]["gan"] + ben["yaos"][p - 1]["zhi"],
                                          ben["yaos"][p - 1]["liuqin"],
                                          bian["yaos"][p - 1]["gan"] + bian["yaos"][p - 1]["zhi"],
                                          bian["yaos"][p - 1]["liuqin"]) for p in moving]
        paragraphs.append("动爻化出：%s。动爻所化示事情的去向，化进化吉、化退化凶、化回头克则事有反复。" %
                          "、".join(changed))
    advice = ("上吉之占，乘势而行，勿疑。" if score >= 80 else
              "吉占，可行，惟留意日月冲动之处。" if score >= 68 else
              "平占，成败参半，谋定而后动，广结助力。" if score >= 55 else
              "所占多阻，宜守不宜攻，待时再举。" if score >= 42 else
              "凶占，所谋难遂，退一步保身为上。")
    paragraphs.append(advice)

    return {
        "mode": mode,
        "category": cat_key,
        "date_text": "%d-%02d-%02d" % (y, m, d),
        "day_gz": GZ60[day_gz],
        "month_gz": GZ60[mgz],
        "vals": vals,
        "ben": ben, "bian": bian,
        "moving": moving,
        "xunkong": list(fz),
        "yong": {"target": yong_target, "pos": yong_pos, "wx": yong_wx,
                 "liuqin": yong["liuqin"], "zhi": yong["zhi"]},
        "score": score, "grade": grade,
        "paragraphs": paragraphs,
        "note": "六爻装卦采用京房纳甲与八宫世应，断语为规则化简断；"
                "同一卦不同流派取用与旺衰口诀或有出入，结果供传统文化研究娱乐参考。",
    }


def divine_by_coins(coin_counts, y, m, d, category):
    vals = qigua_by_coins(coin_counts)
    return analyze("coins", vals, y, m, d, None, category)


def divine_by_time(y, m, d, hour, category):
    vals, lunar_text = qigua_by_time(y, m, d, hour)
    out = analyze("time", vals, y, m, d, hour, category)
    out["qigua_note"] = "起卦依据：农历%s，年月日数起上卦、加时辰数起下卦，总数取动爻。" % lunar_text
    return out
