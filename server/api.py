# -*- coding: utf-8 -*-
"""API 处理器：排盘 / 批八字 / 运程 / 命例库。"""

from .engine import paipan as pp
from .engine import analysis, fortune, calendar_cn as cal
from . import store
from .engine.constants import GZ60


class ApiError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


def _validate_input(body):
    inp = {
        "name": str(body.get("name") or "").strip()[:20],
        "gender": "female" if body.get("gender") == "female" else "male",
        "calendar": "lunar" if body.get("calendar") == "lunar" else "solar",
        "zi_mode": "early_late" if body.get("zi_mode") == "early_late" else "late_swap",
    }
    for key in ("y", "m", "d"):
        try:
            inp[key] = int(body.get(key))
        except (TypeError, ValueError):
            raise ApiError("缺少或非法的日期字段：%s" % key)
    if inp["calendar"] == "lunar":
        inp["leap"] = 1 if body.get("leap") else 0
        if not (1 <= inp["m"] <= 12 and 1 <= inp["d"] <= 30):
            raise ApiError("农历月份日期超出范围")
        try:
            solar = cal.solar_from_lunar(inp["y"], inp["m"], bool(inp["leap"]), inp["d"])
        except Exception:
            raise ApiError("农历日期不存在，请检查（如闰月、大小月）")
        if not (1901 <= solar[0] <= 2050):
            raise ApiError("仅支持 1901～2050 年")
    else:
        if not (1901 <= inp["y"] <= 2050 and 1 <= inp["m"] <= 12 and 1 <= inp["d"] <= 31):
            raise ApiError("日期超出支持范围（1901～2050）")
    if body.get("hour") is None or body.get("hour") == "":
        inp["hour"] = None
        inp["minute"] = 0
    else:
        try:
            inp["hour"] = int(body.get("hour"))
            inp["minute"] = int(body.get("minute") or 0)
        except (TypeError, ValueError):
            raise ApiError("时辰格式非法")
        if not (0 <= inp["hour"] <= 23 and 0 <= inp["minute"] <= 59):
            raise ApiError("时辰超出范围")
    if body.get("true_solar"):
        try:
            lon = float(body.get("lon"))
        except (TypeError, ValueError):
            raise ApiError("经度格式非法")
        if not (73 <= lon <= 136):
            raise ApiError("经度超出中国范围（73～136）")
        inp["true_solar"] = True
        inp["lon"] = lon
    else:
        inp["true_solar"] = False
        inp["lon"] = None
    return inp


def _chart_of(body):
    inp = _validate_input(body.get("input", body))
    try:
        return pp.paipan(inp)
    except ApiError:
        raise
    except Exception as e:
        raise ApiError("排盘失败：%s" % e, 500)


def api_meta(body):
    from datetime import datetime
    now = datetime.now()
    dgz = cal.day_gz_index(now.year, now.month, now.day)
    ygz, _ = cal.year_pillar_at(now)
    mgz, mbranch, jname = cal.month_pillar_at(now)
    return {
        "app": "玄机阁 · 八字排盘命理平台",
        "version": "1.0.0",
        "engine": "自研天文历法引擎（Meeus 算法，节气±15分钟内）",
        "today": now.strftime("%Y-%m-%d"),
        "today_ganzhi": {"year": GZ60[ygz], "month": GZ60[mgz], "day": GZ60[dgz]},
    }


def api_paipan(body):
    chart = _chart_of(body)
    out = {k: v for k, v in chart.items() if k != "_meta"}
    return out


def api_analysis(body):
    chart = _chart_of(body)
    result = analysis.analyze(chart)
    return analysis.serialize(chart, result)


def api_fortune_year(body):
    chart = _chart_of(body)
    try:
        year = int(body.get("year"))
    except (TypeError, ValueError):
        raise ApiError("年份非法")
    if not (1901 <= year <= 2059):
        raise ApiError("年份超出支持范围（1901～2059）")
    result = analysis.analyze(chart)
    ctx = result["ctx"]
    yf = fortune.year_fortune(chart, year, ctx)
    dy = chart.get("dayun")
    decade = None
    if dy and dy.get("list"):
        for row in dy["list"]:
            if row["start_year"] <= year <= row["end_year"]:
                decade = {"ganzhi": row["ganzhi"], "start_year": row["start_year"],
                          "end_year": row["end_year"], "start_age": row["start_age"],
                          "shishen_gan": row["shishen_gan"]}
                break
    yf["decade"] = decade
    return yf


def api_fortune_today(body):
    chart = _chart_of(body)
    result = analysis.analyze(chart)
    ctx = result["ctx"]
    return fortune.today_all(chart, ctx)


def api_charts_list(body):
    return {"charts": store.list_charts()}


def api_charts_add(body):
    inp = _validate_input(body.get("input", body))
    chart = pp.paipan(inp)
    name = chart["basic"]["name"]
    cid = store.add_chart(name, inp["gender"], inp, chart["basic"]["solar_text"])
    return {"id": cid}


def api_charts_delete(body, chart_id):
    if not store.delete_chart(chart_id):
        raise ApiError("命例不存在", 404)
    return {"deleted": chart_id}


# ---------------- 新增算法 ----------------

def _hour_zhi_of(body):
    try:
        hour = int(body.get("hour"))
    except (TypeError, ValueError):
        raise ApiError("请选择时辰")
    if not (0 <= hour <= 23):
        raise ApiError("时辰超出范围")
    return ((hour + 1) // 2) % 12


def api_ziwei(body):
    from .engine import ziwei
    try:
        ly = int(body.get("y"))
    except (TypeError, ValueError):
        raise ApiError("请填写农历年份")
    if not (1901 <= ly <= 2050):
        raise ApiError("农历年份超出范围")
    try:
        month = int(body.get("m"))
        day = int(body.get("d"))
    except (TypeError, ValueError):
        raise ApiError("农历月日非法")
    if not (1 <= month <= 12 and 1 <= day <= 30):
        raise ApiError("农历月/日超出范围（日 1～30）")
    leap = 1 if body.get("leap") else 0
    gender = "female" if body.get("gender") == "female" else "male"
    hour_zhi = _hour_zhi_of(body)
    try:
        return ziwei.paipan_ziwei(ly, month, leap, day, hour_zhi, gender)
    except Exception as e:
        raise ApiError("紫微排盘失败：%s" % e, 500)


def api_meihua(body):
    from .engine import meihua
    mode = body.get("mode", "time")
    if mode == "numbers":
        try:
            n1 = int(body.get("n1"))
            n2 = int(body.get("n2"))
        except (TypeError, ValueError):
            raise ApiError("请输入起卦数字")
        if not (1 <= n1 <= 99999 and 1 <= n2 <= 99999):
            raise ApiError("数字超出范围（1～99999）")
        return meihua.divine_by_numbers(n1, n2)
    inp = _validate_input(body)
    if inp["hour"] is None:
        raise ApiError("时间起卦需要选择时辰")
    try:
        return meihua.divine_by_time(inp["y"], inp["m"], inp["d"], inp["hour"])
    except Exception as e:
        raise ApiError("起卦失败：%s" % e, 500)


def api_hehun(body):
    from .engine import hehun
    a, b = body.get("a"), body.get("b")
    if not a or not b:
        raise ApiError("请填写双方出生信息")
    ca = _chart_of({"input": a})
    cb = _chart_of({"input": b})
    result = hehun.hehun(ca, cb)
    result["a"] = {"name": ca["basic"]["name"], "gender": ca["basic"]["gender"],
                   "solar": ca["basic"]["solar_text"], "year_gz": ca["pillars"]["year"]["ganzhi"],
                   "day_gz": ca["pillars"]["day"]["ganzhi"]}
    result["b"] = {"name": cb["basic"]["name"], "gender": cb["basic"]["gender"],
                   "solar": cb["basic"]["solar_text"], "year_gz": cb["pillars"]["year"]["ganzhi"],
                   "day_gz": cb["pillars"]["day"]["ganzhi"]}
    return result


def api_zodiac(body):
    from .engine import zodiac
    from datetime import datetime
    year = body.get("year")
    if year is None:
        year = datetime.now().year
    try:
        year = int(year)
    except (TypeError, ValueError):
        raise ApiError("年份非法")
    if not (1901 <= year <= 2059):
        raise ApiError("年份超出支持范围")
    return zodiac.zodiac_year(year)


# ---------------- 西方占星 / 塔罗 ----------------

def _astro_input(body):
    try:
        y, m, d = int(body.get("y")), int(body.get("m")), int(body.get("d"))
    except (TypeError, ValueError):
        raise ApiError("请填写公历出生日期")
    if not (1900 <= y <= 2050 and 1 <= m <= 12 and 1 <= d <= 31):
        raise ApiError("日期超出支持范围")
    hv = body.get("hour")
    if hv is None or hv == "":
        hour = minute = None
    else:
        try:
            hour = int(hv)
            minute = int(body.get("minute") or 0)
        except (TypeError, ValueError):
            raise ApiError("时间格式非法")
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ApiError("时间超出范围")
    try:
        lon = float(body.get("lon")) if body.get("lon") is not None else 116.41
        lat = float(body.get("lat")) if body.get("lat") is not None else 39.90
    except (TypeError, ValueError):
        raise ApiError("经纬度格式非法")
    if not (-180 <= lon <= 180 and -90 <= lat <= 90):
        raise ApiError("经纬度超出范围")
    return y, m, d, hour, minute, lon, lat


def api_astro(body):
    from .engine import western
    y, m, d, hour, minute, lon, lat = _astro_input(body)
    name = str(body.get("name") or "").strip()[:20]
    natal = western.natal_chart(y, m, d, hour, minute, lon, lat, name)
    natal["input"] = {"y": y, "m": m, "d": d, "hour": hour, "minute": minute,
                      "lon": lon, "lat": lat, "name": name}
    if body.get("with_today"):
        natal["today"] = western.daily_transits(natal)
    return natal


def api_astro_pair(body):
    from .engine import western
    sa, sb = body.get("a"), body.get("b")
    if sa not in western.SIGNS or sb not in western.SIGNS:
        raise ApiError("请选择两个星座")
    return western.compatibility(sa, sb)


def api_tarot(body):
    from .engine import tarot
    from datetime import date as _date
    mode = body.get("mode", "daily")
    if mode == "three":
        question = str(body.get("question") or "").strip()[:60]
        return tarot.spread_three(question)
    name = str(body.get("name") or "").strip()[:20]
    day = _date.today()
    if body.get("date"):
        try:
            yy, mm, dd = str(body.get("date")).split("-")
            day = _date(int(yy), int(mm), int(dd))
        except Exception:
            raise ApiError("日期格式非法")
    return tarot.daily_card(day, name)
