# -*- coding: utf-8 -*-
"""西方占星：行星黄经（JPL 近似轨道根数）、上升/中天、本命盘、行运相位、星座配对。

精度说明：
- 太阳复用 Meeus 算法；月亮用 Meeus 47 章级数（±0.1°）；
- 水星~土星采用 JPL 近似开普勒根数（误差数角分级），对 30° 宽的星座区间足够；
  行星贴近星座交界 1° 以内时前端提示；
- 宫位采用整宫制（上升星座即第一宫），时区按东八区处理。
"""

import math
from datetime import datetime
from . import astro

_D2R = math.pi / 180.0

# 星座
SIGNS = ["白羊", "金牛", "双子", "巨蟹", "狮子", "处女", "天秤", "天蝎", "射手", "摩羯", "水瓶", "双鱼"]
SIGN_SYMS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]
SIGN_ELEMENT = ["火", "土", "风", "水", "火", "土", "风", "水", "火", "土", "风", "水"]
SIGN_MODE = ["基本", "固定", "变动", "基本", "固定", "变动", "基本", "固定", "变动", "基本", "固定", "变动"]
SIGN_RULER = ["火星", "金星", "水星", "月亮", "太阳", "水星", "金星", "冥王星", "木星", "土星", "天王星", "海王星"]

# 太阳过界近似日期（3 月 21 日前后 0° 白羊），用于参考
SUN_SIGN_TRAIT = {
    "白羊": "行动派先锋，直来直往、敢为人先，胜负欲强但来去都快。",
    "金牛": "稳定务实，感官敏锐，重视安全感与积累，认定了便不动摇。",
    "双子": "好奇心旺盛，信息灵通，能言善道，兴趣广但易分心。",
    "巨蟹": "情感细腻，重家庭与归属，护内念旧，情绪如潮有涨落。",
    "狮子": "自信大方，天生舞台感，慷慨重面子，渴望被看见与认可。",
    "处女": "细致挑剔，逻辑与秩序感强，擅长优化完善，对自己要求苛刻。",
    "天秤": "优雅权衡，重视关系与公平，审美出众，怕冲突易纠结。",
    "天蝎": "深刻专注，洞察力强，爱恨分明，意志力与掌控欲并存。",
    "射手": "乐观爱自由，眼界开阔爱哲思，直率奔放，难被束缚。",
    "摩羯": "目标导向，自律耐压，事业心重，慢热而长情。",
    "水瓶": "独立前瞻，重理念与群体，思维跳脱，保持距离感。",
    "双鱼": "浪漫共情，想象力丰富，界限感弱，慈悲而多梦。",
}

MOON_TRAIT = "月亮星座是情绪与安全感的模式：你如何应对压力、如何表达需要、什么环境让你安心。"

ASC_TRAIT = "上升星座是人格面具与第一印象：他人眼中你的气质，也是应对世界的默认姿态。"

PLANET_ROLE = {
    "太阳": "核心自我与人生主旨",
    "月亮": "情绪与内在需要",
    "水星": "思维与表达",
    "金星": "爱与审美",
    "火星": "行动与欲望",
    "木星": "机遇与信念",
    "土星": "责任与课题",
    "上升": "人格面具",
    "中天": "事业方向",
}

# JPL 近似开普勒根数（J2000，世纪变率）：a, e, I, L, ϖ, Ω
_PLANETS = {
    "水星": (0.38709927, 0.20563593, 7.00497902, 252.25032350, 77.45779628, 48.33076593,
             0.00000037, 0.00001906, -0.00594749, 149472.67411175, 0.16047689, -0.12534081),
    "金星": (0.72333566, 0.00677672, 3.39467605, 181.97909950, 131.60246718, 76.67984255,
             0.00000390, -0.00004107, -0.00078890, 58517.81538729, 0.00268329, -0.27769418),
    "地球": (1.00000261, 0.01671123, -0.00001531, 100.46457166, 102.93768193, 0.0,
             0.00000562, -0.00004392, -0.01294668, 35999.37244981, 0.32327364, 0.0),
    "火星": (1.52371034, 0.09339410, 1.84969142, -4.55343205, -23.94362959, 49.55953891,
             0.00001847, 0.00007882, -0.00813131, 19140.30268499, 0.44441088, -0.29257343),
    "木星": (5.20288700, 0.04838624, 1.30439695, 34.39644051, 14.72847983, 100.47390909,
             -0.00011607, -0.00013253, -0.00183714, 3034.74612775, 0.21252668, 0.20469106),
    "土星": (9.53667594, 0.05386179, 2.48599187, 49.95424423, 92.59887831, 113.66242448,
             -0.00125060, -0.00050991, 0.00193609, 1222.49362201, -0.41897216, -0.28867794),
}


def _helio(name, jd_tt):
    """行星日心黄道坐标 (x, y, z)（AU）。"""
    row = _PLANETS[name]
    a0, e0, i0, l0, w0, o0, da, de, di, dl, dw, do_ = row
    t = (jd_tt - 2451545.0) / 36525.0
    a = a0 + da * t
    e = e0 + de * t
    inc = (i0 + di * t) * _D2R
    L = l0 + dl * t
    peri = w0 + dw * t
    node = o0 + do_ * t
    arg_peri = (peri - node) * _D2R
    M = ((L - peri) % 360.0) * _D2R
    if M > math.pi:
        M -= 2 * math.pi
    E = M
    for _ in range(8):
        E -= (E - e * math.sin(E) - M) / (1 - e * math.cos(E))
    xp = a * (math.cos(E) - e)
    yp = a * math.sqrt(1 - e * e) * math.sin(E)
    w, om, i_ = arg_peri, node * _D2R, inc
    x = (math.cos(w) * math.cos(om) - math.sin(w) * math.sin(om) * math.cos(i_)) * xp \
        + (-math.sin(w) * math.cos(om) - math.cos(w) * math.sin(om) * math.cos(i_)) * yp
    y = (math.cos(w) * math.sin(om) + math.sin(w) * math.cos(om) * math.cos(i_)) * xp \
        + (-math.sin(w) * math.sin(om) + math.cos(w) * math.cos(om) * math.cos(i_)) * yp
    z = (math.sin(w) * math.sin(i_)) * xp + (math.cos(w) * math.sin(i_)) * yp
    return x, y, z


def planet_longitude(name, jd_ut):
    """地心视黄经（度）。name ∈ 水星/金星/火星/木星/土星。"""
    year = 2000.0 + (jd_ut - 2451545.0) / 365.25
    jd_tt = jd_ut + astro.deltat_seconds(int(year)) / 86400.0
    px, py, _ = _helio(name, jd_tt)
    ex, ey, _ = _helio("地球", jd_tt)
    gx, gy = px - ex, py - ey
    return math.degrees(math.atan2(gy, gx)) % 360.0


def sun_longitude(jd_ut):
    return astro.sun_apparent_longitude(jd_ut)


def moon_longitude(jd_ut):
    return astro.moon_apparent_longitude(jd_ut)


def all_planets(jd_ut):
    """七曜地心黄经 dict。"""
    return {
        "太阳": sun_longitude(jd_ut),
        "月亮": moon_longitude(jd_ut),
        "水星": planet_longitude("水星", jd_ut),
        "金星": planet_longitude("金星", jd_ut),
        "火星": planet_longitude("火星", jd_ut),
        "木星": planet_longitude("木星", jd_ut),
        "土星": planet_longitude("土星", jd_ut),
    }


def gmst_deg(jd_ut):
    d = jd_ut - 2451545.0
    t = d / 36525.0
    g = 280.46061837 + 360.98564736629 * d + 0.000387933 * t * t
    return g % 360.0


def ascendant_mc(jd_ut, lon_east, lat):
    """上升与中天黄经（度）。"""
    ramc = (gmst_deg(jd_ut) + lon_east) % 360.0
    eps = (23.4392911 - 0.0130042 * ((jd_ut - 2451545.0) / 36525.0)) * _D2R
    r = ramc * _D2R
    mc = math.degrees(math.atan2(math.sin(r), math.cos(r) * math.cos(eps))) % 360.0
    asc = math.degrees(math.atan2(
        math.cos(r),
        -(math.sin(r) * math.cos(eps) + math.tan(lat * _D2R) * math.sin(eps)))) % 360.0
    return asc, mc, ramc


def sign_of(lon):
    """黄经 -> (星座名, 宫内度数, 索引)。"""
    idx = int(lon // 30) % 12
    return SIGNS[idx], round(lon % 30.0, 2), idx


def natal_chart(y, m, d, hour, minute, lon_east, lat, name=""):
    """本命星盘。hour/minute 为东八区钟表时间，可为 None（无时辰则不算上升与宫位）。"""
    if hour is None:
        jd = astro.to_jd(y, m, d, 12.0)
        has_time = False
    else:
        jd = astro.beijing_to_jd(datetime(y, m, d, hour, minute or 0))
        has_time = True
    planets = all_planets(jd)
    asc = mc = None
    if has_time:
        asc, mc, _ = ascendant_mc(jd, lon_east, lat)
    placements = []
    for body, lon in planets.items():
        sign, deg, idx = sign_of(lon)
        placements.append({
            "body": body, "lon": round(lon, 2), "sign": sign, "deg": deg,
            "sym": SIGN_SYMS[idx], "element": SIGN_ELEMENT[idx], "role": PLANET_ROLE[body],
            "house": (int(((lon - asc) % 360) // 30) + 1) if asc is not None else None,
        })
    if asc is not None:
        for label, lon in (("上升", asc), ("中天", mc)):
            sign, deg, idx = sign_of(lon)
            placements.append({"body": label, "lon": round(lon, 2), "sign": sign, "deg": deg,
                               "sym": SIGN_SYMS[idx], "element": SIGN_ELEMENT[idx],
                               "role": PLANET_ROLE[label], "house": 1 if label == "上升" else 10})
    # 四元素分布
    elem_count = {"火": 0, "土": 0, "风": 0, "水": 0}
    for p in placements:
        if p["body"] in ("太阳", "月亮", "水星", "金星", "火星"):
            elem_count[p["element"]] += 1
    sun_sign = placements[0]["sign"]
    moon_sign = placements[1]["sign"]
    result = {
        "basic": {
            "name": name or "未命名",
            "birth": "%d年%02d月%02d日 %s" % (y, m, d, ("%02d:%02d" % (hour, minute)) if has_time else "时间未知"),
            "sun_sign": sun_sign, "moon_sign": moon_sign,
            "asc_sign": sign_of(asc)[0] if asc else None,
        },
        "placements": placements,
        "elements": elem_count,
        "sun_trait": SUN_SIGN_TRAIT[sun_sign],
        "has_time": has_time,
        "note": "宫位采用整宫制；时区按东八区；行星采用 JPL 近似轨道根数（数角分级精度）。",
    }
    if asc is not None:
        result["asc_trait"] = ASC_TRAIT + "你的上升在%s。" % result["basic"]["asc_sign"]
    return result


ASPECTS = [("合相", 0), ("六合", 60), ("刑相", 90), ("拱相", 120), ("冲相", 180)]
ASPECT_ORB = {"合相": 8, "六合": 6, "刑相": 8, "拱相": 8, "冲相": 8}
ASPECT_GOOD = {"合相": 0, "六合": 1, "刑相": -1, "拱相": 1, "冲相": -1}
ASPECT_MEAN = {
    "六合": "机会与助力悄然出现，需要主动伸手去接。",
    "刑相": "张力与摩擦，逼你升级能力，过程不顺却是成长的杠杆。",
    "拱相": "天赋般顺畅的流动，事半功倍，别浪费在舒适区。",
    "冲相": "两面拉扯、非此即彼，课题在于找到平衡点。",
    "合相": "能量叠加聚焦，特质被放大强化。",
}


def _ang_diff(a, b):
    d = abs(a - b) % 360.0
    return d if d <= 180 else 360 - d


def find_aspects(points_a, points_b, orb_scale=1.0):
    """两组黄经点之间的相位。返回 [(a名, b名, 相位, 角距, 吉凶)]。"""
    out = []
    for an, alon in points_a.items():
        for bn, blon in points_b.items():
            diff = _ang_diff(alon, blon)
            for name, angle in ASPECTS:
                if abs(diff - angle) <= ASPECT_ORB[name] * orb_scale:
                    out.append((an, bn, name, round(diff, 1), ASPECT_GOOD[name]))
                    break
    return out


def daily_transits(natal):
    """今日行运（北京当天中午的七曜）与本命点的相位。"""
    now = datetime.now()
    jd = astro.to_jd(now.year, now.month, now.day, 4.0)   # 北京时间正午 = 04:00 UT
    transits = all_planets(jd)
    natal_points = {p["body"]: p["lon"] for p in natal["placements"] if p["body"] != "中天"}
    found = find_aspects(transits, natal_points, orb_scale=0.8)
    items = []
    score = 60
    for tn, nn, asp, diff, good in found:
        if nn == tn:
            continue
        items.append({
            "text": "行运%s 与本命%s 成%s（角距 %s°）——%s" % (tn, nn, asp, diff, ASPECT_MEAN[asp]),
            "good": good, "transit": tn, "natal": nn, "aspect": asp,
        })
        score += 5 * good if asp != "合相" else (2 if tn in ("木星", "金星", "太阳") else -2 if tn in ("土星", "火星") else 0)
    score = max(20, min(95, score))
    items.sort(key=lambda x: (-x["good"], x["aspect"]))
    return {"date": now.strftime("%Y-%m-%d"),
            "transits": {k: sign_of(v)[0] for k, v in transits.items()},
            "aspects": items[:8], "score": score,
            "grade": "吉" if score >= 68 else "平" if score >= 52 else "起伏"}


def compatibility(sign_a, sign_b):
    """星座配对：元素与模式亲和。"""
    ia, ib = SIGNS.index(sign_a), SIGNS.index(sign_b)
    ea, eb = SIGN_ELEMENT[ia], SIGN_ELEMENT[ib]
    ma, mb = SIGN_MODE[ia], SIGN_MODE[ib]
    if ia == ib:
        score, verdict = 78, "同星座：镜像般懂得彼此，优缺点同频共振。"
    elif ea == eb:
        score, verdict = 82, "同元素（%s象）：价值观与节奏天然同频，相处顺畅。" % ea
    elif (ea, eb) in (("火", "风"), ("风", "火"), ("土", "水"), ("水", "土")):
        score, verdict = 76, "相生组合（%s×%s）：一方给燃料一方给空间，互相点亮。" % (ea, eb)
    elif (ea, eb) in (("火", "土"), ("土", "火"), ("风", "水"), ("水", "风")):
        score, verdict = 55, "磨合组合（%s×%s）：节奏与表达方式差异大，需翻译彼此的语言。" % (ea, eb)
    else:
        score, verdict = 62, "对宫或跨象组合（%s×%s）：互补吸引，张力与成长并存。" % (ea, eb)
    if ma == mb and ia != ib:
        score += 3
        verdict += "同为%s宫，生活步调接近。" % ma
    score = min(95, score)
    return {
        "pair": "%s × %s" % (sign_a, sign_b),
        "elements": "%s象 × %s象" % (ea, eb),
        "score": score,
        "grade": "很配" if score >= 75 else "有缘" if score >= 60 else "需经营",
        "verdict": verdict,
        "advice": "占星配对只看太阳星座是远远不够的，月亮与上升往往才是日常相处的真相；仅供娱乐参考。",
    }
