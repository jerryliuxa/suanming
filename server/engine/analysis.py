# -*- coding: utf-8 -*-
"""批八字规则引擎：日主旺衰、从格判定、喜用神、特殊格局、结构化批文。

打分模型（可解释）：
  得令（月令旺相休囚死，满分40）+ 得地（通根，满分45）+ 得势（印比数量，满分35）
  总分 0~120 映射七档：从强/强/偏强/中和/偏弱/弱/从弱。
喜用神以扶抑为主、调候为辅，全部结论附命盘事实依据。
"""

from .constants import (
    GAN, ZHI, GAN_WX, ZHI_WX, SHENG, KE, SHENG_WO, WO_KE, KE_WO, CANGGAN,
    LING_WX, WANG_XIANG_SCORE, wang_xiang, SS_GROUP,
)
from . import texts as T

PILLAR_KEYS = ["year", "month", "day", "hour"]

_GROUP_TEXT_KEY = {"比": "比肩", "印": "印星", "食": "食伤", "财": "财星", "官": "官杀"}
_GROUP_ELEMENTS = {
    "比": None,  # 依日主而定
    "印": None,
}


def _pillar_shishen(chart, key):
    p = chart["pillars"][key]
    return p["shishen_gan"] if p else None


def _stems_shishen(chart):
    """四天干十神列表。"""
    out = []
    for key in PILLAR_KEYS:
        ss = _pillar_shishen(chart, key)
        if ss:
            out.append(ss)
    return out


def _branch_elements(chart):
    """四地支本气五行 [(pillar_key, element)]。"""
    out = []
    for key in PILLAR_KEYS:
        p = chart["pillars"][key]
        if p:
            out.append((key, p["zhi"]["wx"]))
    return out


def _meta(chart):
    return chart["_meta"]


def score_strength(chart):
    """日主强弱打分，返回 (总分, 明细 dict)。"""
    meta = _meta(chart)
    day_gan_i = GAN.index(chart["day_gan"])
    day_wx = GAN_WX[day_gan_i]
    month_branch = meta["month_branch"]
    ling = LING_WX[month_branch]
    status = wang_xiang(day_wx, ling)
    detail = {"得令": WANG_XIANG_SCORE[status], "令的状态": status}

    # 得地：通根（同五行藏干），月支×1.2 日支×1.3
    loc_w = {"year": 1.0, "month": 1.2, "day": 1.3, "hour": 1.0}
    got_root = 0.0
    for key in PILLAR_KEYS:
        p = chart["pillars"][key]
        if not p:
            continue
        for item in p["canggan"]:
            if item["wx"] == day_wx:
                got_root += (18 if item["weight"] >= 0.6 else
                             10 if item["weight"] >= 0.3 else 5) * loc_w[key]
    detail["得地"] = min(got_root, 45.0)

    # 得势：天干地支中印比数量
    help_score = 0.0
    for key in PILLAR_KEYS:
        p = chart["pillars"][key]
        if not p:
            continue
        ss = p["shishen_gan"]
        grp = SS_GROUP[ss]
        if grp == "比":
            help_score += 10 if key in ("year", "month") else 8
        elif grp == "印":
            help_score += 9 if ss == "正印" else 6
        # 地支本气
        bz = p["canggan"][0]
        g2 = SS_GROUP[bz["shishen"]]
        if key != "month" and g2 in ("比", "印"):
            help_score += 6 if g2 == "比" else 5
    detail["得势"] = min(help_score, 35.0)

    total = detail["得令"] + detail["得地"] + detail["得势"]
    return total, detail


def strength_grade(total):
    if total >= 92:
        return "从强"
    if total >= 76:
        return "强"
    if total >= 62:
        return "偏强"
    if total >= 46:
        return "中和"
    if total >= 30:
        return "偏弱"
    if total >= 14:
        return "弱"
    return "从弱"


def pick_xiyong(chart, grade, month_branch):
    """喜用神与忌神（五行列表）。"""
    day_gan_i = GAN.index(chart["day_gan"])
    day_wx = GAN_WX[day_gan_i]
    wo = day_wx                 # 比劫
    yin = SHENG_WO[day_wx]      # 印（生我）
    shang = SHENG[day_wx]       # 食伤（我生）
    cai = WO_KE[day_wx]         # 财（我克）
    guan = KE_WO[day_wx]        # 官杀（克我）

    if grade in ("从强",):
        return [wo, yin], [guan, cai, shang]
    if grade in ("强", "偏强"):
        # 身强宜克泄耗：按月令与透干选两用
        prefs = [guan, shang, cai]
        return prefs[:2], [wo, yin]
    if grade in ("从弱",):
        return [cai, guan, shang], [wo, yin]
    if grade in ("弱", "偏弱"):
        return [yin, wo], [guan, shang, cai]
    # 中和：调候为主
    if month_branch in (10, 11, 0, 1):     # 亥子丑冬生，喜火暖局
        return ["火", "木"], ["水"]
    if month_branch in (5, 6, 7):          # 巳午未夏生，喜水润局
        return ["水", "金"], ["火"]
    return [cai, guan], [shang]


def detect_patterns(chart):
    """特殊格局（以透干为准）。"""
    stems = set(_stems_shishen(chart))
    pats = []
    if "伤官" in stems and "正官" in stems:
        pats.append(("shangguan_jian_guan", T.SPECIAL_PATTERNS["shangguan_jian_guan"]))
    if "偏印" in stems and "食神" in stems:
        pats.append(("xiaoshen_duoshi", T.SPECIAL_PATTERNS["xiaoshen_duoshi"]))
    if ("正财" in stems or "偏财" in stems) and ("正官" in stems or "七杀" in stems):
        pats.append(("caiguan_shuangmei", T.SPECIAL_PATTERNS["caiguan_shuangmei"]))
    if "七杀" in stems and ("正印" in stems or "偏印" in stems):
        pats.append(("shayin_xiangsheng", T.SPECIAL_PATTERNS["shayin_xiangsheng"]))
    if "食神" in stems and "七杀" in stems:
        pats.append(("shishen_zhisha", T.SPECIAL_PATTERNS["shishen_zhisha"]))
    if "伤官" in stems and ("正财" in stems or "偏财" in stems):
        pats.append(("shangguan_peicai", T.SPECIAL_PATTERNS["shangguan_peicai"]))
    if "正官" in stems and "七杀" in stems:
        pats.append(("guansha_hunza", T.SPECIAL_PATTERNS["guansha_hunza"]))
    # 羊刃驾杀
    day_gan = chart["day_gan"]
    from .constants import YANGREN
    if day_gan in YANGREN:
        blade = ZHI[YANGREN[day_gan]]
        for key in PILLAR_KEYS:
            p = chart["pillars"][key]
            if p and p["zhi"]["c"] == blade and "七杀" in stems:
                pats.append(("yangren_jiasha", T.SPECIAL_PATTERNS["yangren_jiasha"]))
                break
    return pats


def dominant_and_lacking(chart):
    """最旺十神组与最缺十神组。"""
    stats = chart.get("shishen_stats", {})
    groups = {}
    for ss, n in stats.items():
        g = SS_GROUP[ss]
        groups[g] = groups.get(g, 0) + n
    for g in ("比", "印", "食", "财", "官"):
        groups.setdefault(g, 0)
    dom = max(groups, key=lambda g: groups[g])
    zero = [g for g, n in groups.items() if n == 0]
    return dom, groups, zero


def build_context(chart):
    meta = _meta(chart)
    total, detail = score_strength(chart)
    grade = strength_grade(total)
    xiyong, ji = pick_xiyong(chart, grade, meta["month_branch"])
    dom, groups, zero = dominant_and_lacking(chart)
    patterns = detect_patterns(chart)
    return {
        "total": round(total, 1),
        "detail": detail,
        "grade": grade,
        "xiyong": xiyong,
        "ji": ji,
        "dominant": dom,
        "groups": groups,
        "zero_groups": zero,
        "patterns": patterns,
    }


def _dedupe(seq):
    out = []
    for x in seq:
        if x not in out:
            out.append(x)
    return out


def analyze(chart):
    """批八字主入口：返回 sections = [{"title", "paragraphs": [...]}] 与 ctx。"""
    meta = _meta(chart)
    ctx = build_context(chart)
    day_gan = chart["day_gan"]
    day_wx = chart["day_gan_wx"]
    gender = "男" if meta["gender"] == "male" else "女"
    month_branch = meta["month_branch"]
    ling = LING_WX[month_branch]
    sections = []

    # ---- 命盘总览 ----
    p1 = "%s命主，日主%s（%s），生于%s月（%s当令），日主处「%s」之地。" % (
        gender, day_gan, day_wx, ZHI[month_branch], ling, ctx["detail"]["令的状态"])
    p1 += "得令%d分、得地%d分、得势%d分，合计%s分，判为「%s」。" % (
        ctx["detail"]["得令"], ctx["detail"]["得地"], ctx["detail"]["得势"],
        ctx["total"], ctx["grade"])
    sections.append({
        "title": "命盘总览",
        "paragraphs": [p1, T.STRENGTH_DESC[ctx["grade"]],
                       "喜用之神为「%s」，忌避「%s」。" % ("、".join(ctx["xiyong"]), "、".join(ctx["ji"]))],
    })

    # ---- 性格特质 ----
    paras = [T.DAY_MASTER_TRAIT[day_gan]]
    paras.append("命局中%s" % T.GROUP_TRAIT[ctx["dominant"]])
    for g in ctx["zero_groups"]:
        key = _GROUP_TEXT_KEY[g]
        if key in T.SHISHEN_LACK:
            paras.append(T.SHISHEN_LACK[key])
            break
    sections.append({"title": "性格特质", "paragraphs": paras})

    # ---- 格局特长 ----
    if ctx["patterns"]:
        sections.append({"title": "格局与特长",
                         "paragraphs": [text for _, text in ctx["patterns"]]})

    # ---- 事业方向 ----
    xi_txt = "；".join(T.XIYONG_DESC[w].rstrip("。") for w in ctx["xiyong"][:2])
    guan_grp = ctx["groups"].get("官", 0)
    shi_grp = ctx["groups"].get("食", 0)
    career = "事业方向宜顺喜用而行：%s。" % xi_txt
    if guan_grp >= 2:
        career += "局中官杀有力，能扛责任、服众管人，管理、公职、大平台发展为宜。"
    elif shi_grp >= 2:
        career += "局中食伤吐秀，宜以专业、创意、技术立身，自由度高的平台更能发挥。"
    else:
        career += "官星印星平平，宜稳中求进，靠专业积累与人脉口碑逐步上台阶。"
    if ctx["grade"] in ("强", "偏强", "从强"):
        career += "身强能任事，敢闯敢拼，创业自营亦可一试。"
    elif ctx["grade"] in ("弱", "偏弱", "从弱"):
        career += "身弱任重则损，宜借力平台、依附强援，不宜过早独立扛局。"
    sections.append({"title": "事业方向", "paragraphs": [career]})

    # ---- 财运分析 ----
    cai_grp = ctx["groups"].get("财", 0)
    bi_grp = ctx["groups"].get("比", 0)
    wealth = ""
    if cai_grp == 0:
        wealth += T.SHISHEN_LACK["财星"]
    elif cai_grp >= 2:
        wealth += "命局财星多现，财缘丰厚、机会常伴，%s。" % (
            "身强能任财，可放手经营" if ctx["grade"] in ("强", "偏强", "从强")
            else "惟身弱不胜财，机会多而承接难，须先强身（补喜用）再求大财")
    else:
        wealth += "命局财星明透，财路清晰，勤而有获。"
    if bi_grp >= 2:
        wealth += "惟比劫并见，劫财夺财之象明显：合伙需立字据、借贷需谨慎，钱财宜置产转化。"
    wealth += "求财宜取「%s」之气：%s。" % ("、".join(ctx["xiyong"]), xi_txt)
    sections.append({"title": "财运分析", "paragraphs": [wealth]})

    # ---- 感情婚姻 ----
    day_p = chart["pillars"]["day"]
    spouse_ss = day_p["canggan"][0]["shishen"]
    love = "日支配偶宫坐%s，%s。" % (day_p["zhi"]["c"], T.SPOUSE_DESC[spouse_ss])
    if meta["gender"] == "male":
        if ctx["groups"].get("财", 0) == 0:
            love += "男命以财为妻星，局中财星不透，姻缘宜迟不宜急，晚婚反稳。"
        elif ctx["groups"].get("比", 0) >= 2:
            love += "男命以财为妻星，妻星透而比劫争之，感情中须防竞争者与口舌，宜坦诚经营。"
        else:
            love += "男命以财为妻星，妻星有力，得贤内助之象。"
    else:
        if ctx["groups"].get("官", 0) == 0:
            love += "女命以官为夫星，局中官星不显，姻缘宜随缘不强求，事业自立为先。"
        elif "七杀" in _stems_shishen(chart) and "正官" in _stems_shishen(chart):
            love += "女命官杀混杂，感情选择多、易生纷扰，宜早定心思、择良人而嫁。"
        else:
            love += "女命以官为夫星，夫星清透，得端正可靠之伴侣。"
    sections.append({"title": "感情婚姻", "paragraphs": [love]})

    # ---- 六亲缘分 ----
    fam = []
    for key, label in (("year", "年柱（祖上父母）"), ("month", "月柱（父母兄弟）"), ("hour", "时柱（子女）")):
        p = chart["pillars"][key]
        if not p:
            continue
        ss = p["canggan"][0]["shishen"]
        if key == "hour":
            fam.append("%s坐%s，%s。" % (label, p["zhi"]["c"], T.CHILD_DESC[ss]))
        else:
            fam.append("%s：%s坐%s，%s。" % (label, p["gan"]["c"], p["zhi"]["c"], T.SIX_REL[ss]))
    sections.append({"title": "六亲缘分", "paragraphs": fam})

    # ---- 健康提示 ----
    wx = chart["wuxing"]["scores"]
    strong = [k for k, v in wx.items() if v >= max(wx.values()) * 0.8 and v > 0]
    weak = [k for k, v in wx.items() if v <= 1.0]
    tips = []
    for w in _dedupe(strong)[:2]:
        if w in ctx["ji"]:
            tips.append("%s气过旺，须防%s方面的问题。" % (w, T.HEALTH_WX[w]))
    for w in _dedupe(weak)[:2]:
        tips.append("%s气偏弱，%s先天偏娇，宜早养护。" % (w, T.HEALTH_WX[w]))
    if not tips:
        tips.append("五行未见明显偏枯，日常规律作息即可。")
    tips_txt = "；".join(x.rstrip("。") for x in tips) + "。"
    sections.append({"title": "健康提示", "paragraphs": [tips_txt]})

    # ---- 开运建议 ----
    luck = []
    for w in ctx["xiyong"][:2]:
        luck.append(T.XIYONG_DESC[w])
    luck.append("数字颜色、方位行业皆可参喜用：趋吉之道，在于顺势补偏。")
    sections.append({"title": "开运建议", "paragraphs": luck})

    # ---- 大运走势 ----
    dy = chart.get("dayun")
    if dy and dy.get("list"):
        rows = []
        for row in dy["list"][:8]:
            g_wx = row["wx_gan"]
            if g_wx in ctx["xiyong"]:
                grade_txt = "吉"
            elif g_wx in ctx["ji"]:
                grade_txt = "凶"
            else:
                grade_txt = "平"
            comment = T.YUN_COMMENTS[row["shishen_gan"]][grade_txt]
            rows.append("%s岁起%s大运（%s～%s年）：%s" % (
                row["start_age"], row["ganzhi"], row["start_year"], row["end_year"],
                comment))
        sections.append({"title": "大运走势", "paragraphs": rows})

    summary = "%s，%s命，日主%s%s，「%s」格局，喜%s而忌%s。" % (
        meta["name"], gender, day_gan, day_wx, ctx["grade"],
        "、".join(ctx["xiyong"]), "、".join(ctx["ji"]))

    return {"summary": summary, "sections": sections, "ctx": ctx}


# ---------------- 序列化辅助（API 输出用） ----------------

def serialize(chart, result):
    return {
        "summary": result["summary"],
        "strength": {
            "score": result["ctx"]["total"],
            "grade": result["ctx"]["grade"],
            "detail": {k: v for k, v in result["ctx"]["detail"].items() if k != "令的状态"},
            "ling_status": result["ctx"]["detail"]["令的状态"],
        },
        "xiyong": result["ctx"]["xiyong"],
        "ji": result["ctx"]["ji"],
        "patterns": [{"key": k, "text": t} for k, t in result["ctx"]["patterns"]],
        "sections": result["sections"],
        "disclaimer": "本批文由传统命理规则引擎自动生成，仅供文化娱乐参考，不构成任何现实决策依据。",
    }
