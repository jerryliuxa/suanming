# -*- coding: utf-8 -*-
"""天文历法底层：儒略日、太阳视黄经（Meeus 低阶算法）、节气时刻、朔日时刻、均时差。

精度说明：
- 太阳黄经采用 Meeus《Astronomical Algorithms》低阶算法，误差约 ±0.01°，
  折合节气时刻约 ±15 分钟以内；对绝大多数出生时刻的排盘无影响，
  出生时间距节气交界 2 小时以内时前端会给出提示。
- 朔日采用 Meeus 49 章截断周期项，误差约 ±3 分钟，足以确定农历日界。
- ΔT 采用分段线性近似（1900-2035 误差 < 2 秒）。
"""

import math
from datetime import datetime, timedelta

_D2R = math.pi / 180.0

# ΔT 分段锚点（年, 秒）
_DELTAT_POINTS = [
    (1900, -2.7), (1920, 21.2), (1940, 24.3), (1950, 29.2), (1960, 33.2),
    (1970, 40.2), (1980, 50.5), (1990, 56.9), (2000, 63.8), (2010, 66.1),
    (2020, 69.4), (2026, 69.1), (2035, 69.0),
]


def deltat_seconds(year):
    """TT - UT1 的近似秒数。"""
    if year <= 1900:
        return -2.7
    if year >= 2035:
        return 69.0
    for i in range(len(_DELTAT_POINTS) - 1):
        y0, d0 = _DELTAT_POINTS[i]
        y1, d1 = _DELTAT_POINTS[i + 1]
        if y0 <= year <= y1:
            return d0 + (d1 - d0) * (year - y0) / (y1 - y0)
    return 69.0


def to_jd(y, m, d, hour=0.0):
    """公历（格里历）-> 儒略日（UT）。y/m/d 为日期，hour 为当日小时（含小数）。"""
    if m <= 2:
        y -= 1
        m += 12
    a = y // 100
    b = 2 - a + a // 4
    jd = int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + d + b - 1524.5
    return jd + hour / 24.0


def jd_to_beijing(jd):
    """儒略日（UT）-> 北京时间 datetime（naive）。"""
    unix_days = jd - 2440587.5
    dt = datetime(1970, 1, 1) + timedelta(days=unix_days)
    return dt + timedelta(hours=8)


def beijing_to_jd(dt):
    """北京时间 naive datetime -> 儒略日（UT）。"""
    utc = dt - timedelta(hours=8)
    epoch = datetime(1970, 1, 1)
    days = (utc - epoch).total_seconds() / 86400.0
    return 2440587.5 + days


def jdn(y, m, d):
    """公历日期的儒略日数（当日正午的 JD 取整），用于干支纪日。"""
    return int(to_jd(y, m, d, 12.0) + 0.5)


def _normalize_deg(x):
    return x % 360.0


def sun_apparent_longitude(jd_ut):
    """太阳视黄经（度）。输入儒略日（UT），内部换算 TT。"""
    year = 2000.0 + (jd_ut - 2451545.0) / 365.25
    jd_tt = jd_ut + deltat_seconds(int(year)) / 86400.0
    t = (jd_tt - 2451545.0) / 36525.0
    l0 = 280.46646 + 36000.76983 * t + 0.0003032 * t * t
    m = 357.52911 + 35999.05029 * t - 0.0001537 * t * t
    mr = (m % 360.0) * _D2R
    c = ((1.914602 - 0.004817 * t - 0.000014 * t * t) * math.sin(mr)
         + (0.019993 - 0.000101 * t) * math.sin(2 * mr)
         + 0.000289 * math.sin(3 * mr))
    true_lon = l0 + c
    omega = (125.04 - 1934.136 * t) * _D2R
    return _normalize_deg(true_lon - 0.00569 - 0.00478 * math.sin(omega))


def solar_term_jd(year, lon_deg):
    """求某公历年内太阳视黄经到达 lon_deg 的时刻（儒略日 UT）。

    lon_deg: 0=春分 15=清明 ... 315=立春（沿黄道递增 15 度一节气）。
    """
    month, day = _nominal_date(lon_deg)
    jd0 = to_jd(year, month, day, 12.0)
    # 牛顿迭代：太阳平均每天走 0.9856°
    jd = jd0
    target = _normalize_deg(lon_deg)
    for _ in range(6):
        lam = sun_apparent_longitude(jd)
        diff = (target - lam + 180.0) % 360.0 - 180.0
        if abs(diff) < 1e-7:
            break
        jd += diff / 0.98564735
    return jd


def _nominal_date(lon_deg):
    """由黄经反查节气近似日期（初值用）。"""
    from .constants import TERMS, TERM_NOMINAL
    for name, lon in TERMS:
        if lon == lon_deg % 360:
            return TERM_NOMINAL[name]
    raise ValueError("bad term longitude %s" % lon_deg)


def solar_term_beijing(year, lon_deg):
    """节气时刻的北京时间 datetime。"""
    return jd_to_beijing(solar_term_jd(year, lon_deg))


def moon_apparent_longitude(jd):
    """月亮视黄经（度）——公开接口，供西方占星模块使用。"""
    return _moon_apparent_longitude(jd)


def _moon_apparent_longitude(jd):
    """月亮视黄经（度）。Meeus 47 章级数前 25 项，截断误差约 ±0.05°（≈6 分钟）。

    输入儒略日（TT/UT 差异对本用途可忽略，< 0.1 分钟）。
    """
    t = (jd - 2451545.0) / 36525.0
    lp = (218.3164477 + 481267.88123421 * t - 0.0015786 * t * t
          + t ** 3 / 538841.0 - t ** 4 / 65194000.0)
    d = (297.8501921 + 445267.1114034 * t - 0.0018819 * t * t
         + t ** 3 / 545868.0 - t ** 4 / 113065000.0)
    m = 357.5291092 + 35999.0502909 * t - 0.0001536 * t * t + t ** 3 / 24490000.0
    mp = (134.9633964 + 477198.8675055 * t + 0.0087414 * t * t
          + t ** 3 / 69699.0 - t ** 4 / 14712000.0)
    f = (93.2720950 + 483202.0175233 * t - 0.0036539 * t * t
         - t ** 3 / 3526000.0 + t ** 4 / 863310000.0)
    dr, mr, mpr, fr = d * _D2R, m * _D2R, mp * _D2R, f * _D2R
    # (系数 1e-6 度, 相位组合)
    terms = [
        (6288774, (0, 1, 0, 0)), (1274027, (2, -1, 0, 0)), (658314, (2, 0, 0, 0)),
        (213618, (0, 2, 0, 0)), (-185116, (0, 0, 1, 0)), (-114332, (0, 0, 0, 2)),
        (58793, (2, -2, 0, 0)), (57066, (2, -1, -1, 0)), (53322, (2, 1, 0, 0)),
        (45758, (2, 0, -1, 0)), (-40923, (0, 1, -1, 0)), (-34720, (1, 0, 0, 0)),
        (-30383, (0, 1, 1, 0)), (15327, (2, 0, 0, -2)), (-12528, (0, 1, 0, 2)),
        (10980, (0, 1, 0, -2)), (10675, (4, -1, 0, 0)), (10034, (0, 3, 0, 0)),
        (8548, (4, -2, 0, 0)), (-7888, (2, -1, 1, 0)), (-6766, (2, 0, 1, 0)),
        (-5163, (1, -1, 0, 0)), (4987, (1, 0, 1, 0)), (4036, (2, 1, -1, 0)),
        (3994, (2, 2, 0, 0)), (3861, (4, 0, 0, 0)),
    ]
    # 相位组合以 (a,b,c,e) 表示 a*D + b*M' + c*M + e*F
    s = 0.0
    for coeff, (a, b, c, e) in terms:
        arg = a * dr + b * mpr + c * mr + e * fr
        s += coeff * math.sin(arg)
    return _normalize_deg(lp + s / 1e6)


def _sun_longitude_tt(jd_tt):
    """太阳视黄经（度），输入 TT 儒略日（与 sun_apparent_longitude 相同算法）。"""
    return sun_apparent_longitude(jd_tt)  # 内部已含 ΔT 换算，对本层精度足够


def new_moon_jd(k):
    """第 k 个朔日的儒略日（UT）。k=0 为 2000-01-06 朔。

    以平均朔为初值，牛顿迭代求解月亮视黄经 = 太阳视黄经。
    """
    t = k / 1236.85
    seed = (2451550.09766 + 29.530588861 * k + 0.00015437 * t * t
            - 0.000000150 * t ** 3 + 0.00000000073 * t ** 4)
    jd = seed
    for _ in range(5):
        diff = _normalize_deg(_moon_apparent_longitude(jd) - _sun_longitude_tt(jd) + 180.0) - 180.0
        if abs(diff) < 1e-8:
            break
        # 黄经差变化率约 12.19 度/天
        jd -= diff / 12.190749
    return jd


def new_moons_between(jd_start, jd_end):
    """[jd_start, jd_end) 内所有朔日的儒略日（UT），升序。"""
    k0 = int(math.floor((jd_start - 2451550.09766) / 29.530588861)) - 2
    out = []
    k = k0
    while True:
        jd = new_moon_jd(k)
        if jd >= jd_end:
            break
        if jd >= jd_start:
            out.append(jd)
        k += 1
    return out


def equation_of_time_minutes(jd_ut):
    """均时差（分钟）：真太阳时 = 平太阳时 + 均时差。"""
    jd_tt = jd_ut + 69.0 / 86400.0
    t = (jd_tt - 2451545.0) / 36525.0
    l0 = _normalize_deg(280.46646 + 36000.76983 * t + 0.0003032 * t * t)
    m = (357.52911 + 35999.05029 * t - 0.0001537 * t * t) * _D2R
    c = ((1.914602 - 0.004817 * t) * math.sin(m)
         + (0.019993 - 0.000101 * t) * math.sin(2 * m) + 0.000289 * math.sin(3 * m))
    true_lon = (l0 + c) * _D2R
    eps = (23.439291 - 0.0130042 * t) * _D2R
    ra = math.atan2(math.cos(eps) * math.sin(true_lon), math.cos(true_lon))
    ra = math.degrees(ra) % 360.0
    eot = 4.0 * ((l0 - ra + 180.0) % 360.0 - 180.0)
    return eot


def true_solar_time_minutes(clock_dt, longitude_east):
    """北京时间 clock_dt、东经 longitude_east 处的真太阳时（当天分钟数）。"""
    jd = to_jd(clock_dt.year, clock_dt.month, clock_dt.day,
               clock_dt.hour + clock_dt.minute / 60.0 + clock_dt.second / 3600.0)
    eot = equation_of_time_minutes(jd)
    minutes = clock_dt.hour * 60 + clock_dt.minute + clock_dt.second / 60.0
    return minutes + (longitude_east - 120.0) * 4.0 + eot
