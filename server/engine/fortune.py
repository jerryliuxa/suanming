# -*- coding: utf-8 -*-
"""运程引擎：流年/流月/流日与原局的刑冲合害作用评分。

评分模型（可解释、确定性）：
  基础分（年58/月55/日62）
  + 喜忌：流柱干支五行入喜用加分、入忌神减分
  + 作用：六合/三合/半合加分，六冲/刑/害/破减分（日支、月支权重更高）
  + 特殊：冲提纲（冲月支）、天克地冲额外减分；岁运之间轻微修正
  结果钳制在 12~95，映射 上吉/吉/平顺/起伏/低伏 五档。
"""

from datetime import datetime, timedelta
from . import astro, calendar_cn as cal
from .constants import (
    GAN, ZHI, GAN_WX, ZHI_WX, GZ60, GAN_HE, ZHI_HE6, ZHI_CHONG,
    zhi_xing, ZHI_HAI, ZHI_PO, SANHE, WUHU, SS_GROUP, CANGGAN, KE, shi_shen,
)
from . import texts as T

PILLAR_KEYS = ["year", "month", "day", "hour"]
PAL_W = {"year": 1.0, "month": 1.2, "day": 1.3, "hour": 1.0}
PAL_CN = {"year": "年", "month": "月", "day": "日", "hour": "时"}

_JIE_CACHE = {}


def _jie_list(year):
    """公历年相关的 12 节（含上年大雪），带缓存。"""
    if year in _JIE_CACHE:
        return _JIE_CACHE[year]
    out = cal.jie_boundaries(year)
    _JIE_CACHE[year] = out
    return out


def _flow_year_pillar(year):
    """流年干支（以立春为界）。"""
    return cal.year_gz_index(year)


def _xi_ji_mod(wuxing, xiyong, ji):
    if wuxing in xiyong:
        return 1
    if wuxing in ji:
        return -1
    return 0


def _interactions(flow_gz, chart, xiyong, ji, scale=1.0, extra_gz=None, extra_scale=0.0):
    """流柱与原局（及另一流柱）的作用关系。

    返回 (delta, chips, themes)。chips 用于前端展示，如「冲日支(子午)」。
    """
    fg, fz = flow_gz % 10, flow_gz % 12
    delta = 0.0
    chips = []
    themes = []

    for key in PILLAR_KEYS:
        p = chart["pillars"][key]
        if not p:
            continue
        ng, nz = p["gz_index"] % 10, p["gz_index"] % 12
        w = PAL_W[key] * scale

        # 天干五合
        if GAN_HE[fg][0] == ng:
            delta += 3.0 * w
            chips.append("%s合%s（%s柱）" % (GAN[fg], GAN[ng], PAL_CN[key]))
        # 地支六合
        if ZHI_HE6[fz][0] == nz:
            delta += 4.0 * w
            chips.append("%s合%s（%s支）" % (ZHI[fz], ZHI[nz], PAL_CN[key]))
            if key == "day":
                themes.append(T.REL_THEMES["合日支"])
        # 六冲
        if ZHI_CHONG[fz] == nz:
            delta -= 6.0 * w
            chips.append("%s冲%s（%s支）" % (ZHI[fz], ZHI[nz], PAL_CN[key]))
            if key == "day":
                themes.append(T.REL_THEMES["冲日支"])
            elif key == "month":
                themes.append(T.REL_THEMES["冲提纲"])
                delta -= 2.0 * w
            elif key in REL_THEME_MAP:
                themes.append(REL_THEME_MAP[key])
        # 相刑
        if zhi_xing(fz, nz):
            delta -= 5.0 * w
            chips.append("%s刑%s（%s支）" % (ZHI[fz], ZHI[nz], PAL_CN[key]))
        # 六害
        if ZHI_HAI.get(fz) == nz:
            delta -= 3.0 * w
            chips.append("%s害%s（%s支）" % (ZHI[fz], ZHI[nz], PAL_CN[key]))
        # 相破
        if ZHI_PO.get(fz) == nz:
            delta -= 2.0 * w
            chips.append("%s破%s（%s支）" % (ZHI[fz], ZHI[nz], PAL_CN[key]))

    # 三合局 / 半合
    natal_branches = [p["gz_index"] % 12 for key in PILLAR_KEYS
                      if (p := chart["pillars"][key])]
    for name, members, wx in SANHE:
        if fz not in members:
            continue
        hits = [b for b in natal_branches if b in members and b != fz]
        if len(hits) >= 2:
            delta += 8.0 * scale
            chips.append("%s三合局（%s）" % (ZHI[fz], name))
            if wx in xiyong:
                delta += 3.0 * scale
        elif len(hits) == 1:
            delta += 3.0 * scale
            chips.append("%s半合%s" % (ZHI[fz], ZHI[hits[0]]))

    # 天克地冲（对额外流柱，如大运）
    if extra_gz is not None and extra_scale > 0:
        eg, ez = extra_gz % 10, extra_gz % 12
        gan_conflict = KE[GAN_WX[fg]] == GAN_WX[eg] or KE[GAN_WX[eg]] == GAN_WX[fg]
        zhi_conflict = ZHI_CHONG[fz] == ez
        if gan_conflict and zhi_conflict:
            delta -= 8.0 * extra_scale
            chips.append("天克地冲（%s%s vs %s%s）" % (GAN[fg], ZHI[fz], GAN[eg], ZHI[ez]))
            themes.append(T.REL_THEMES["天克地冲"])
        elif zhi_conflict:
            delta -= 3.0 * extra_scale
            chips.append("%s冲%s（岁运）" % (ZHI[fz], ZHI[ez]))
        elif GAN_HE[fg][0] == eg:
            delta += 2.0 * extra_scale
            chips.append("%s合%s（岁运）" % (GAN[fg], GAN[eg]))

    return delta, chips, _dedupe(themes)


REL_THEME_MAP = {"year": "根基祖辈", "hour": "子女下属"}


def _dedupe(seq):
    out = []
    for x in seq:
        if x not in out:
            out.append(x)
    return out


def _score_band(score):
    if score >= 70:
        return "吉"
    if score >= 45:
        return "平"
    return "凶"


def _pick(lst, seed):
    """确定性挑选，让不同干支的宜忌有所变化。"""
    if not lst:
        return None
    return lst[seed % len(lst)]


def _yi_ji(score, seed, themes):
    if score >= 72:
        yi = [_pick(T.YI_HIGH, seed + i) for i in range(3)]
        ji = [_pick(T.JI_LOW, seed) ]
    elif score >= 58:
        yi = [_pick(T.YI_MID, seed + i) for i in range(3)]
        ji = [_pick(T.JI_LOW, seed)]
    else:
        yi = [_pick(T.YI_MID, seed + i) for i in range(2)]
        ji = [_pick(T.JI_LOW, seed + i) for i in range(3)]
    yi = [y for y in yi if y]
    ji = [j for j in ji if j]
    return _dedupe(yi), _dedupe(ji)


def _flow_interpret(flow_gz, chart, ctx, base, scale, seed, extra_gz=None, extra_scale=0.0):
    """通用流柱解读。"""
    xiyong, ji = ctx["xiyong"], ctx["ji"]
    fg, fz = flow_gz % 10, flow_gz % 12
    delta, chips, themes = _interactions(flow_gz, chart, xiyong, ji,
                                         scale=scale, extra_gz=extra_gz, extra_scale=extra_scale)
    # 喜忌
    gan_mod = 12.0 * scale if _xi_ji_mod(GAN_WX[fg], xiyong, ji) == 1 else (
        -10.0 * scale if _xi_ji_mod(GAN_WX[fg], xiyong, ji) == -1 else 0)
    zhi_main = CANGGAN[fz][0][0]
    zhi_wx = GAN_WX[zhi_main]
    zhi_mod = 8.0 * scale if zhi_wx in xiyong else (
        -7.0 * scale if zhi_wx in ji else 0)
    score = base + delta + gan_mod + zhi_mod
    score = int(round(max(12, min(95, score))))

    day_gan_i = GAN.index(chart["day_gan"])
    ss = shi_shen(day_gan_i, fg)
    band = _score_band(score)
    brief = T.YUN_COMMENTS[ss][band]
    if chips:
        brief += "要点：" + "、".join(chips[:3]) + "。"
    themes = _dedupe(themes + T.YUN_THEMES[ss])[:4]
    yi, ji_list = _yi_ji(score, seed, themes)
    return {
        "score": score,
        "grade": T.grade_of(score),
        "band": band,
        "shishen": ss,
        "chips": chips,
        "themes": themes,
        "brief": brief,
        "yi": yi,
        "ji": ji_list,
    }


def year_fortune(chart, year, ctx):
    """流年 + 12 流月。"""
    ygz = _flow_year_pillar(year)
    # 当前大运
    extra_gz, extra_scale = None, 0.0
    dy = chart.get("dayun")
    if dy and dy.get("list"):
        for row in dy["list"]:
            if row["start_year"] <= year <= row["end_year"]:
                extra_gz = cal.gz_index(GAN.index(row["ganzhi"][0]), ZHI.index(row["ganzhi"][1]))
                extra_scale = 0.6
                break
    out = _flow_interpret(ygz, chart, ctx, base=58.0, scale=1.0, seed=ygz, extra_gz=extra_gz, extra_scale=extra_scale)
    out["year"] = year
    out["ganzhi"] = GZ60[ygz]
    out["wx"] = GAN_WX[ygz % 10] + ZHI_WX[ygz % 12]

    # 12 流月：立春(year) -> 立春(year+1)
    months = []
    starts = []
    for t, name, branch in _jie_list(year):
        if name == "立春" and t >= datetime(year, 1, 1):
            starts.append((t, name, branch))
    # 补下一年立春作为终点
    next_lc = None
    for t, name, branch in _jie_list(year + 1):
        if name == "立春":
            next_lc = (t, name, branch)
            break
    # 节序列：从立春(year) 到 小寒(year+1)
    seq = []
    grab = False
    for t, name, branch in _jie_list(year):
        if name == "立春":
            grab = True
        if grab:
            seq.append((t, name, branch))
    for t, name, branch in _jie_list(year + 1):
        if name == "小寒":
            seq.append((t, name, branch))
            break
    ygan = ygz % 10
    for i, (t, name, branch) in enumerate(seq):
        end_t = seq[i + 1][0] if i + 1 < len(seq) else (next_lc[0] if next_lc else t)
        mgz = cal.gz_index((WUHU[ygan] + (branch - 2) % 12) % 10, branch)
        mf = _flow_interpret(mgz, chart, ctx, base=55.0, scale=0.75, seed=mgz * 7 + year)
        mf["month_branch"] = branch
        mf["ganzhi"] = GZ60[mgz]
        mf["label"] = "%s月（%s起）" % (ZHI[branch], name)
        mf["jie_name"] = name
        mf["start"] = t.strftime("%Y-%m-%d")
        mf["end"] = end_t.strftime("%Y-%m-%d")
        months.append(mf)
    out["months"] = months
    return out


def day_fortune(chart, date, ctx):
    """流日运程。date 为 date 对象。"""
    dgz = cal.day_gz_index(date.year, date.month, date.day)
    out = _flow_interpret(dgz, chart, ctx, base=62.0, scale=0.6, seed=dgz * 13 + date.day)
    out["date"] = date.strftime("%Y-%m-%d")
    out["ganzhi"] = GZ60[dgz]
    out["weekday"] = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][date.weekday()]
    return out


def month_days_fortune(chart, year, month, ctx):
    """整月逐日运程（日历热力图用）。"""
    out = []
    d = datetime(year, month, 1).date()
    while d.month == month:
        out.append(day_fortune(chart, d, ctx))
        d += timedelta(days=1)
    return out


def today_all(chart, ctx, now=None):
    """当年/当月/今日运程。now 为北京时间 datetime（服务端本地时间）。"""
    now = now or datetime.now()
    year = year_fortune(chart, now.year, ctx)
    # 当月（按公历月）
    days = month_days_fortune(chart, now.year, now.month, ctx)
    today = day_fortune(chart, now.date(), ctx)
    # 当月干支
    mgz, mbranch, jname = cal.month_pillar_at(now)
    month_view = _flow_interpret(mgz, chart, ctx, base=55.0, scale=0.75, seed=mgz * 7 + now.year)
    month_view["ganzhi"] = GZ60[mgz]
    month_view["label"] = "%s月（%s起）" % (ZHI[mbranch], jname)
    return {"today_date": now.strftime("%Y-%m-%d"),
            "year": year, "month": month_view, "day": today,
            "calendar": days}


def serialize_year(yf):
    """流年结果序列化（剥离内部字段）。"""
    return yf


def serialize_today(tf):
    return tf
