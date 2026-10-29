# -*- coding: utf-8 -*-
"""梅花易数：时间起卦 / 数字起卦，本卦互卦变卦、体用生克解卦。"""

from . import calendar_cn as cal

# 八卦：名 -> (符号, 二进制[初爻..上爻], 自然象, 五行, 亲人)
TRIGRAMS = {
    "乾": ("☰", (1, 1, 1), "天", "金", "父"),
    "兑": ("☱", (1, 1, 0), "泽", "金", "少女"),
    "离": ("☲", (1, 0, 1), "火", "火", "中女"),
    "震": ("☳", (1, 0, 0), "雷", "木", "长男"),
    "巽": ("☴", (0, 1, 1), "风", "木", "长女"),
    "坎": ("☵", (0, 1, 0), "水", "水", "中男"),
    "艮": ("☶", (0, 0, 1), "山", "土", "少男"),
    "坤": ("☷", (0, 0, 0), "地", "土", "母"),
}
ORDER = ["乾", "兑", "离", "震", "巽", "坎", "艮", "坤"]
SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

# 六十四卦名矩阵 [上卦][下卦]
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

# 六十四卦白话断语（现代释义，按名索引）
HEX_MEANING = {
    "乾为天": "刚健进取，自强不息。创始之力正盛，宜主动开拓，戒骄戒躁。",
    "天泽履": "如履虎尾，谨慎前行。礼让守分，虽险无咎。",
    "天火同人": "同志相聚，和衷共济。宜开诚布公，广结善缘。",
    "天雷无妄": "守正则吉，妄动则灾。顺其自然，不存侥幸。",
    "天风姤": "不期而遇，机会暗藏。慎防表象，明辨真伪。",
    "天水讼": "争讼之象，宜和不宜斗。退一步海阔天空。",
    "天山遁": "退避保身，韬光养晦。暂敛锋芒，以待时来。",
    "天地否": "闭塞不通，诸事多阻。宜守静待变，否极泰来。",
    "泽天夬": "决断时刻，当机立断。光明正大，去旧图新。",
    "兑为泽": "喜悦和乐，口舌生财。以诚相待，共享成果。",
    "泽火革": "变革之时，旧去新来。谋定后动，顺天应人。",
    "泽雷随": "顺随而行，柔顺得吉。择善而从，不可盲随。",
    "泽风大过": "非常之时行非常之事，刚毅担当，量力而行。",
    "泽水困": "身处困境，志不可屈。守正蓄力，困而不失其所。",
    "泽山咸": "两情相感，心心相印。宜真诚感应，姻缘事业皆旺。",
    "泽地萃": "聚人聚财，群英荟萃。善用众力，防人满为患。",
    "火天大有": "大有收获，如日中天。富而好礼，盛极知谦。",
    "火泽睽": "背离分歧，同床异梦。小事化无，求同存异。",
    "离为火": "光明附丽，文明兴旺。宜借势而行，过刚易折。",
    "火雷噬嗑": "咬合除障，恩威并施。遇到梗阻，果断处理。",
    "火风鼎": "鼎新调和，稳定成器。培养贤才，事业更新。",
    "火水未济": "事未竟成，尚在途中。审慎推进，勿急功近利。",
    "火山旅": "旅途奔波，寄身在外。谨慎低调，随遇而安。",
    "火地晋": "晋升之象，旭日东升。进取有名，稳步向上。",
    "雷天大壮": "声势壮大，阳刚正盛。力虽足，仍守规矩。",
    "雷泽归妹": "名分已定而序有失，进退有度方得始终。",
    "雷火丰": "丰大光明，如日中天。盛时多忧，早作安排。",
    "震为雷": "惊雷震动，变动突来。临危不乱，闻雷自省。",
    "雷风恒": "恒久之道，贵在坚持。立身有常，万事可成。",
    "雷水解": "冰雪消融，困境得解。宜速不宜迟，向西南去。",
    "雷山小过": "小事可为，大事勿举。稍越常度无妨，切忌高飞。",
    "雷地豫": "喜悦豫备，顺动而乐。居安思危，乐不忘忧。",
    "风天小畜": "力量初聚，以柔畜刚。小有积蓄，静待时机。",
    "风泽中孚": "诚信立身，中心不欺。以信感人，无往不利。",
    "风火家人": "家和万事兴，内外有别。正人先正己，齐家成业。",
    "风雷益": "损上益下，施比受福。助人即助己，进取有利。",
    "巽为风": "随风入微，以顺为进。申命行事，柔而不弱。",
    "风水涣": "涣散之局，凝聚为要。重整旗鼓，聚拢人心。",
    "风山渐": "循序渐进，如雁成行。不急不躁，功到自成。",
    "风地观": "观人观己，登高望远。多看多学，静观其变。",
    "水天需": "等待时机，饮食宴乐。需而有恒，时机自至。",
    "水泽节": "节而有度，量入为出。恰如其分，过节则苦。",
    "水火既济": "功德圆满，既济功成。盛时思危，谨防初吉终乱。",
    "水雷屯": "万物初生，创始维艰。蓄势待发，贵人可倚。",
    "水风井": "井养不穷，守常济人。修身养德，源源不绝。",
    "坎为水": "重重险陷，履险如夷。诚信守正，行险而不失其信。",
    "水山蹇": "前路蹇难，进退两难。反身修德，借力贵人。",
    "水地比": "亲比相依，择主而从。以诚相交，则众辅助。",
    "山天大畜": "大有蓄积，厚积薄发。养贤蓄德，可成大器。",
    "山泽损": "损己益人，先失后得。减负去奢，愈损愈得。",
    "山火贲": "文饰之美，质胜于文。修饰得体，返璞归真。",
    "山雷颐": "颐养之道，慎言节食。自求口实，观其自养。",
    "山风蛊": "整饬积弊，拨乱反正。对症下药，治蛊有道。",
    "山水蒙": "启蒙求知，虚心请教。童蒙求我，学则不困。",
    "艮为山": "适可而止，当止则止。守位安分，动静得宜。",
    "山地剥": "剥落衰微，硕果仅存。敛藏守正，静待复元。",
    "地天泰": "天地交泰，通达安顺。上下同心，万事亨通。",
    "地泽临": "君临其事，大势将至。以宽临下，进取有望。",
    "地火明夷": "光明受损，韬晦避害。内明外柔，守志待旦。",
    "地雷复": "一阳来复，否去泰来。迷途知返，七日可期。",
    "地风升": "积小成大，步步高升。柔以时升，进德修业。",
    "地水师": "出师有名，纪律为先。行险而顺，任贤则胜。",
    "地山谦": "谦谦君子，卑以自牧。满招损，谦受益。",
    "坤为地": "厚德载物，柔顺包容。以静制动，先迷后得。",
}

YAO_NAMES = ["初", "二", "三", "四", "五", "上"]


def _to_name(bits):
    """三爻二进制(初..上) -> 卦名。"""
    for name, (_, b, *_ ) in TRIGRAMS.items():
        if tuple(bits) == tuple(b):
            return name
    raise ValueError("bad bits")


def _lines_of(tri_name):
    return list(TRIGRAMS[tri_name][1])


def _compose(lines6):
    """六爻线 -> (上卦名, 下卦名, 卦名)。lines6[0] 为初爻。"""
    lower = _to_name(lines6[0:3])
    upper = _to_name(lines6[3:6])
    return upper, lower, HEX_NAMES[upper][lower]


def _hu_gua(lines6):
    """互卦：二三四爻为下卦，三四五爻为上卦。"""
    lower = _to_name([lines6[1], lines6[2], lines6[3]])
    upper = _to_name([lines6[2], lines6[3], lines6[4]])
    return upper, lower, HEX_NAMES[upper][lower]


def _bian_gua(lines6, dong_yao):
    """变卦：动爻（1~6，初爻为1）阴阳互变。"""
    b = list(lines6)
    b[dong_yao - 1] = 1 - b[dong_yao - 1]
    upper, lower, name = _compose(b)
    return b, upper, lower, name


def _zhi_num(i):
    """地支序（起卦用）：子1..亥12。"""
    return i + 1


def qigua_by_time(year, month, day, hour):
    """梅花时间起卦。年月日按农历计。返回六爻线与动爻。"""
    lunar = cal.lunar_date(year, month, day)
    lm = lunar["num"]
    ld = lunar["day"]
    # 时辰支序（23:00 后按次日?? 梅花按当日时辰）：hour -> 支序
    hz = ((hour + 1) // 2) % 12
    h_num = _zhi_num(hz)
    ly_zhi = (lunar["ly"] - 1984) % 12        # 农历年支序（子0）
    n1 = (_zhi_num(ly_zhi) + lm + ld) % 8 or 8      # 上卦数
    n2 = (n1 + h_num) % 8 or 8                      # 下卦数（年月日时总和）
    dong = (n1 + h_num) % 6 or 6                    # 动爻
    upper = ORDER[n1 - 1]
    lower = ORDER[n2 - 1]
    lines = _lines_of(lower) + _lines_of(upper)
    return {"lines": lines, "dong": dong, "upper": upper, "lower": lower,
            "lunar_text": lunar["text"], "n1": n1, "n2": n2, "hour_zhi_num": h_num}


def qigua_by_numbers(n1, n2):
    """数字起卦：n1 定上卦，n2 定下卦，(n1+n2+时数?) 简化以 n1+n2 定动爻。"""
    u = n1 % 8 or 8
    lo = n2 % 8 or 8
    dong = (n1 + n2) % 6 or 6
    upper, lower = ORDER[u - 1], ORDER[lo - 1]
    lines = _lines_of(lower) + _lines_of(upper)
    return {"lines": lines, "dong": dong, "upper": upper, "lower": lower,
            "n1": u, "n2": lo}


def _rel(a_wx, b_wx):
    """b 相对 a 的作用：a=体, b=用。返回 (码, 描述)。"""
    if a_wx == b_wx:
        return "比和", "体用比和，同气相求"
    if SHENG[b_wx] == a_wx:
        return "用生体", "用生体，外来助力，大吉之象"
    if KE[a_wx] == b_wx:
        return "体克用", "体克用，我可制彼，小吉而费力"
    if SHENG[a_wx] == b_wx:
        return "体生用", "体生用，我力外泄，有耗损之虞"
    if KE[b_wx] == a_wx:
        return "用克体", "用克体，外力相迫，凶象须防"
    return "neutral", ""


def interpret(gua, extra_note=""):
    """解卦：本卦互卦变卦 + 体用生克评分。"""
    lines = gua["lines"]
    dong = gua["dong"]
    upper, lower, name = _compose(lines)
    ti_name = lower if dong >= 4 else upper      # 动爻所在卦为用，另一卦为体
    yong_name = upper if dong >= 4 else lower
    ti_wx = TRIGRAMS[ti_name][3]
    yong_wx = TRIGRAMS[yong_name][3]
    rel, rel_text = _rel(ti_wx, yong_wx)
    base = {"用生体": 88, "比和": 82, "体克用": 72, "体生用": 50, "用克体": 30}[rel]

    hu_upper, hu_lower, hu_name = _hu_gua(lines)
    b_lines, b_up, b_low, b_name = _bian_gua(lines, dong)
    hu_wx = TRIGRAMS[hu_lower][3]     # 互卦下卦近体
    bian_wx = TRIGRAMS[b_up if dong >= 4 else b_low][3]
    # 互卦/变卦修正
    mods = []
    if hu_wx == ti_wx:
        base += 4; mods.append("互卦比和体卦，事有同助")
    elif SHENG[hu_wx] == ti_wx:
        base += 6; mods.append("互卦生体，过程有贵人")
    elif KE[hu_wx] == ti_wx:
        base -= 8; mods.append("互卦克体，中途多阻")
    if bian_wx == ti_wx:
        base += 4; mods.append("变卦比和，结局平稳")
    elif SHENG[bian_wx] == ti_wx:
        base += 8; mods.append("变卦生体，结果向吉")
    elif KE[bian_wx] == ti_wx:
        base -= 10; mods.append("变卦克体，结局堪忧")
    base = max(5, min(98, base))

    yao_label = YAO_NAMES[dong - 1] + "爻"
    paragraphs = [
        "本卦【%s】（上%s%s、下%s%s），动爻在第%s。以动爻所在为用卦（%s·%s），另一卦为体卦（%s·%s）——%s。" % (
            name, TRIGRAMS[upper][0], upper, TRIGRAMS[lower][0], lower,
            yao_label, TRIGRAMS[yong_name][0] + yong_name, yong_wx,
            TRIGRAMS[ti_name][0] + ti_name, ti_wx, rel_text),
        "互卦【%s】示事情经过；变卦【%s】示最终趋势。%s" % (
            hu_name, b_name, ("；".join(mods) + "。") if mods else ""),
        "卦义：%s" % HEX_MEANING[name],
    ]
    if extra_note:
        paragraphs.append(extra_note)
    grade = ("上吉" if base >= 80 else "吉" if base >= 68 else
             "平" if base >= 55 else "起伏" if base >= 42 else "凶")
    return {
        "name": name, "hu": hu_name, "bian": b_name,
        "ti": {"name": ti_name, "wx": ti_wx, "sym": TRIGRAMS[ti_name][0]},
        "yong": {"name": yong_name, "wx": yong_wx, "sym": TRIGRAMS[yong_name][0]},
        "rel": rel, "dong": dong, "score": base, "grade": grade,
        "paragraphs": paragraphs, "lines": lines,
    }


def divine_by_time(year, month, day, hour):
    gua = qigua_by_time(year, month, day, hour)
    out = interpret(gua, extra_note="起卦依据：农历%s，以年月日之数起上卦，加时辰数起下卦，总数取动爻。" % gua["lunar_text"])
    out["mode"] = "time"
    out["qigua"] = {k: gua[k] for k in ("n1", "n2", "hour_zhi_num", "lunar_text")}
    return out


def divine_by_numbers(n1, n2):
    gua = qigua_by_numbers(int(n1), int(n2))
    out = interpret(gua, extra_note="起卦依据：以数 %d 起上卦、数 %d 起下卦，两数之和取动爻。" % (gua["n1"], gua["n2"]))
    out["mode"] = "numbers"
    return out
