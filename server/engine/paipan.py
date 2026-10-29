# -*- coding: utf-8 -*-
"""排盘引擎：四柱、十神、藏干、纳音、十二长生、空亡、神煞、五行、大运、胎元。"""

from datetime import datetime, timedelta
from . import astro, calendar_cn as cal
from .constants import (
    GAN, ZHI, GAN_WX, ZHI_WX, ZHI_SHENGXIAO, GZ60, CANGGAN, WUHU, WUSHU,
    nayin_of, di_shi, shi_shen, kong_wang, xingzuo_of,
    TIANYI, WENCHANG, LUSHEN, YANGREN, HONGLUAN, ZHI_HE6, ZHI_CHONG,
    zhi_xing, ZHI_HAI, ZHI_PO, _TAOHUA, _HUAGAI, _YIMA,
)

# 三合组查找：支 -> 组
_SANHE_GROUP = {}
for _name, _set, _wx in [(None, frozenset((8, 0, 4)), None), (None, frozenset((2, 6, 10)), None),
                         (None, frozenset((5, 9, 1)), None), (None, frozenset((11, 3, 7)), None)]:
    for _z in _set:
        _SANHE_GROUP[_z] = _set

ZHI_GROUP_LABEL = {(8, 0, 4): "申子辰", (2, 6, 10): "寅午戌", (5, 9, 1): "巳酉丑", (11, 3, 7): "亥卯未"}

PILLAR_KEYS = ["year", "month", "day", "hour"]
PILLAR_NAMES = {"year": "年柱", "month": "月柱", "day": "日柱", "hour": "时柱"}
PALACE_NAMES = {"year": "祖上/父母宫", "month": "父母/兄弟宫", "day": "自身/配偶宫", "hour": "子女/晚景宫"}


def _gz_parts(gz_index):
    return gz_index % 10, gz_index % 12


def _pillar(gz_index, day_gan_i):
    """构造单柱数据（十神相对日干）。"""
    g, z = _gz_parts(gz_index)
    canggan = []
    for gi, w in CANGGAN[z]:
        canggan.append({
            "c": GAN[gi], "wx": GAN_WX[gi], "shishen": shi_shen(day_gan_i, gi),
            "weight": w,
        })
    return {
        "ganzhi": GZ60[gz_index],
        "gan": {"c": GAN[g], "wx": GAN_WX[g], "yy": "阳" if g % 2 == 0 else "阴"},
        "zhi": {"c": ZHI[z], "wx": ZHI_WX[z], "sx": ZHI_SHENGXIAO[z], "yy": "阳" if z % 2 == 0 else "阴"},
        "shishen_gan": shi_shen(day_gan_i, g),
        "canggan": canggan,
        "nayin": nayin_of(gz_index),
        "dish": di_shi(day_gan_i, z),
        "gz_index": gz_index,
    }


def _effective_datetime(inp):
    """处理农历输入、真太阳时。返回 (北京 naive datetime, 说明 dict)。"""
    if inp.get("calendar") == "lunar":
        y, m, d = cal.solar_from_lunar(inp["y"], inp["m"], bool(inp.get("leap")), inp["d"])
    else:
        y, m, d = inp["y"], inp["m"], inp["d"]
    dt = datetime(y, m, d, inp.get("hour") or 0, inp.get("minute") or 0)
    note = {"true_solar": False, "offset_min": 0, "lon": None}
    if inp.get("true_solar") and inp.get("lon") is not None:
        minutes = astro.true_solar_time_minutes(dt, float(inp["lon"]))
        hour = int(minutes // 60)
        minute = int(round(minutes % 60))
        if minute == 60:
            hour, minute = hour + 1, 0
        day_shift = hour // 24
        dt2 = datetime(y, m, d, hour % 24, minute) + timedelta(days=day_shift)
        note = {"true_solar": True, "offset_min": round((dt2 - dt).total_seconds() / 60.0, 1),
                "lon": inp["lon"], "clock_text": dt.strftime("%H:%M"), "true_text": dt2.strftime("%H:%M")}
        dt = dt2
    return dt, note


def _hour_branch(hour):
    return ((hour + 1) // 2) % 12


def _all_jie(year):
    """year-1..year+1 的 12 节时刻列表 [(datetime, 节名, 月支)]，升序。"""
    out = []
    for y in (year - 1, year, year + 1):
        for t, name, branch in cal.jie_boundaries(y):
            if t not in [x[0] for x in out]:
                out.append((t, name, branch))
    out.sort(key=lambda x: x[0])
    return out


def _shensha(pillars, year_gz, day_gz):
    """神煞标注。返回 {pillar_key: [神煞名]} 与汇总列表。"""
    day_gan, year_gan = day_gz % 10, year_gz % 10
    day_zhi, year_zhi = day_gz % 12, year_gz % 12
    marks = {k: [] for k in PILLAR_KEYS}
    zhi_pillars = []  # (pillar_key, zhi_index)
    for key in PILLAR_KEYS:
        p = pillars[key]
        if p:
            zhi_pillars.append((key, p["gz_index"] % 12))

    def mark(branch, name):
        for key, z in zhi_pillars:
            if z == branch:
                marks[key].append(name)

    # 天乙贵人（日干、年干并查）
    for stem, label in ((day_gan, ""), (year_gan, "")):
        for b in TIANYI.get(stem, set()):
            mark(b, "天乙贵人")
    # 文昌
    mark(WENCHANG.get(day_gan, -1), "文昌贵人")
    # 禄神 / 羊刃
    mark(LUSHEN.get(day_gan, -1), "禄神")
    if day_gan in YANGREN:
        mark(YANGREN[day_gan], "羊刃")
    # 驿马/桃花/华盖（年支、日支并查，按三合组起）
    for anchor in (year_zhi, day_zhi):
        grp = _SANHE_GROUP.get(anchor)
        if not grp:
            continue
        if grp in _YIMA:
            mark(_YIMA[grp], "驿马")
        if grp in _TAOHUA:
            mark(_TAOHUA[grp], "桃花")
        if grp in _HUAGAI:
            mark(_HUAGAI[grp], "华盖")
    # 红鸾 / 天喜（年支起）
    hl = HONGLUAN[year_zhi]
    mark(hl, "红鸾")
    mark((hl + 6) % 12, "天喜")
    return marks


def _wuxing_scores(pillars):
    scores = {"木": 0.0, "火": 0.0, "土": 0.0, "金": 0.0, "水": 0.0}
    for key in PILLAR_KEYS:
        p = pillars[key]
        if not p:
            continue
        scores[p["gan"]["wx"]] += 1.0
        for item in p["canggan"]:
            scores[item["wx"]] += item["weight"]
    total = sum(scores.values()) or 1.0
    percent = {k: round(v * 100.0 / total, 1) for k, v in scores.items()}
    present = {k: v for k, v in scores.items() if v > 0}
    return {
        "scores": {k: round(v, 2) for k, v in scores.items()},
        "percent": percent,
        "strongest": max(present, key=present.get),
        "weakest": min(present, key=present.get),
        "missing": [k for k, v in scores.items() if v == 0],
    }


def _dayun(dt, month_gz, year_gz, gender):
    """大运：起运数与十步大运。"""
    yang_year = (year_gz % 10) % 2 == 0
    forward = (yang_year and gender == "male") or ((not yang_year) and gender == "female")
    jies = _all_jie(dt.year)
    if forward:
        target = next((j for j in jies if j[0] > dt), None)
    else:
        past = [j for j in jies if j[0] <= dt]
        target = past[-1] if past else None
    if target is None:
        return None
    delta_days = abs((target[0] - dt).total_seconds()) / 86400.0
    start_age = delta_days / 3.0                      # 3 天折 1 年
    jiaojie = dt + timedelta(days=delta_days / 3.0 * 365.2425)
    mg, mz = _gz_parts(month_gz)
    rows = []
    for i in range(1, 11):
        g = (mg + i) % 10 if forward else (mg - i) % 10
        z = (mz + i) % 12 if forward else (mz - i) % 12
        gz = cal.gz_index(g, z)
        age0 = start_age + 10 * (i - 1)
        age1 = age0 + 10
        y0 = jiaojie.year + 10 * (i - 1)
        y1 = y0 + 9
        rows.append({
            "index": i,
            "ganzhi": GZ60[gz],
            "shishen_gan": None,   # 稍后以日干补
            "start_age": round(age0, 1),
            "end_age": round(age1, 1),
            "start_year": y0,
            "end_year": y1,
            "jiaojie_text": "%d年%d月" % (int(age0), int(round((age0 - int(age0)) * 12))) if age0 >= 1 else "%.1f岁" % age0,
        })
    return {
        "forward": forward,
        "direction_text": "顺行" if forward else "逆行",
        "start_age": round(start_age, 1),
        "start_age_text": "%d年%d个月" % (int(start_age), int(round((start_age - int(start_age)) * 12))),
        "jiaojie_date": jiaojie.strftime("%Y-%m-%d"),
        "jiaojie_jieqi": target[1],
        "list": rows,
    }


def paipan(inp):
    """排盘主入口。inp 字段：
    name, gender(male/female), calendar(solar/lunar), y, m, d, hour(可空), minute,
    leap(农历闰月), zi_mode(late_swap/early_late), true_solar, lon
    """
    name = inp.get("name") or "未命名"
    gender = inp.get("gender", "male")
    dt, ts_note = _effective_datetime(inp)
    hour_known = inp.get("hour") is not None
    zi_mode = inp.get("zi_mode", "late_swap")

    warnings = []
    # 节气边界提示（2 小时内）
    for t, jname, _b in _all_jie(dt.year):
        if abs((t - dt).total_seconds()) <= 2 * 3600:
            warnings.append("出生时刻距「%s」交节（%s）不足 2 小时，月柱/年柱对边界敏感，结果可能受历法精度影响。"
                            % (jname, t.strftime("%m-%d %H:%M")))
            break

    # 年柱
    year_gz, year_num = cal.year_pillar_at(dt)
    # 月柱
    month_gz, month_branch, jie_name = cal.month_pillar_at(dt)
    # 日柱（考虑子时模式）
    day_date = dt.date()
    hour_for_zhi = dt.hour
    day_gz_today = cal.day_gz_index(day_date.year, day_date.month, day_date.day)
    late_zi = hour_known and dt.hour >= 23
    if late_zi and zi_mode == "late_swap":
        day_gz = (day_gz_today + 1) % 60
        warnings.append("采用「晚子时换日」流派：23:00 后日柱进位次日。")
    else:
        day_gz = day_gz_today
        if late_zi:
            warnings.append("采用「早晚子时」流派：23:00 后日柱仍用当日，时干按次日日干起遁。")
    day_gan_i, day_zhi_i = _gz_parts(day_gz)

    # 时柱：子时（23:00 后）属次日，时干均按次日日干起五鼠遁
    hour_gz = None
    if hour_known:
        hz = _hour_branch(hour_for_zhi)
        base_day = (day_gz_today + 1) % 60 if late_zi else day_gz_today
        hg = (WUSHU[base_day % 10] + hz) % 10
        hour_gz = cal.gz_index(hg, hz)

    pillars = {
        "year": _pillar(year_gz, day_gan_i),
        "month": _pillar(month_gz, day_gan_i),
        "day": _pillar(day_gz, day_gan_i),
        "hour": _pillar(hour_gz, day_gan_i) if hour_gz is not None else None,
    }
    for key in PILLAR_KEYS:
        if pillars[key]:
            pillars[key]["palace"] = PALACE_NAMES[key]

    # 大运
    dy = _dayun(dt, month_gz, year_gz, gender)
    if dy:
        for row in dy["list"]:
            g, z = _gz_parts(cal.gz_index(GAN.index(row["ganzhi"][0]), ZHI.index(row["ganzhi"][1])))
            row["shishen_gan"] = shi_shen(day_gan_i, g)
            row["wx_gan"], row["wx_zhi"] = GAN_WX[g], ZHI_WX[z]

    # 神煞
    marks = _shensha(pillars, year_gz, day_gz)
    for key in PILLAR_KEYS:
        if pillars[key]:
            pillars[key]["shensha"] = marks[key]

    # 空亡（日柱、年柱两套）
    kw_day = kong_wang(day_gz)
    kw_year = kong_wang(year_gz)
    for key in ("day", "year"):
        pillars[key]["kongwang"] = list(kw_day if key == "day" else kw_year)

    # 胎元：月干进一，月支进三
    mg, mz = _gz_parts(month_gz)
    taiyuan = GZ60[cal.gz_index((mg + 1) % 10, (mz + 3) % 12)]

    # 十神统计（天干四柱 + 地支本气）
    ss_stats = {}
    for key in PILLAR_KEYS:
        p = pillars[key]
        if not p:
            continue
        ss_stats[p["shishen_gan"]] = ss_stats.get(p["shishen_gan"], 0) + 1
        ss_stats[p["canggan"][0]["shishen"]] = ss_stats.get(p["canggan"][0]["shishen"], 0) + 1

    lunar = cal.lunar_date(dt.year, dt.month, dt.day)

    basic = {
        "name": name,
        "gender": "男" if gender == "male" else "女",
        "solar_text": "%d年%02d月%02d日 %s" % (
            dt.year, dt.month, dt.day,
            ("%02d:%02d" % (dt.hour, dt.minute)) if hour_known else "时辰未知"),
        "lunar_text": lunar["text"],
        "zodiac": ZHI_SHENGXIAO[year_gz % 12],
        "xingzuo": xingzuo_of(dt.month, dt.day),
        "true_solar": ts_note,
        "zi_mode": zi_mode,
    }

    return {
        "input": inp,
        "basic": basic,
        "day_gan": GAN[day_gan_i],
        "day_gan_wx": GAN_WX[day_gan_i],
        "pillars": pillars,
        "wuxing": _wuxing_scores(pillars),
        "dayun": dy,
        "taiyuan": taiyuan,
        "kongwang": {"day": list(kw_day), "year": list(kw_year)},
        "shishen_stats": ss_stats,
        "warnings": warnings,
        "_meta": {
            "birth_dt": dt.strftime("%Y-%m-%d %H:%M"),
            "year_gz": year_gz, "month_gz": month_gz, "day_gz": day_gz,
            "hour_gz": hour_gz, "hour_known": hour_known,
            "gender": gender, "name": name,
            "month_branch": month_branch, "jie_name": jie_name,
            "zi_mode": zi_mode,
        },
    }
