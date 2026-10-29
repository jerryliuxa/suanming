# -*- coding: utf-8 -*-
"""历法层：干支纪日、年柱月柱（节气定界）、二十四节气表、农历（定朔+定气置闰）。

所有时刻均为北京时间（东八区）naive datetime；"日数"指北京时间的公历日序（JDN）。
"""

from datetime import datetime
from . import astro
from .constants import (GAN, ZHI, TERMS, JIE_NAMES, JIE_BRANCH, WUHU, GZ60,
                        LUNAR_MONTHS, LUNAR_DAYS)

# 节名 -> 太阳黄经
_JIE_LON = {"立春": 315, "惊蛰": 345, "清明": 15, "立夏": 45, "芒种": 75, "小暑": 105,
            "立秋": 135, "白露": 165, "寒露": 195, "立冬": 225, "大雪": 255, "小寒": 285}

# 干支纪日锚点：1949-10-01 为甲子日
_DAY_ANCHOR_JDN = astro.jdn(1949, 10, 1)

# 中气黄经（用于农历置闰）：雨水330 春分0 谷雨30 小满60 夏至90 大暑120
# 处暑150 秋分180 霜降210 小雪240 冬至270 大寒300
_ZHONGQI_LON = [330, 0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300]


def gz_index(gan_i, zhi_i):
    """天干索引+地支索引 -> 六十甲子索引。"""
    return (6 * gan_i - 5 * zhi_i) % 60


def day_gz_index(y, m, d):
    """公历日期的日柱干支索引（甲子=0）。"""
    return (astro.jdn(y, m, d) - _DAY_ANCHOR_JDN) % 60


def year_gz_index(year):
    """公历年份的年柱干支索引（以立春切换）。"""
    return (year - 1984) % 60


def year_pillar_at(dt):
    """北京时间 dt 的年柱（立春为界）。返回 (干支索引, 生肖年公历年)。"""
    lichun = astro.solar_term_beijing(dt.year, 315)
    y = dt.year if dt >= lichun else dt.year - 1
    return year_gz_index(y), y


def _day_num(jd):
    """儒略日(UT) -> 北京时间当日的日数（JDN）。"""
    dt = astro.jd_to_beijing(jd)
    return astro.jdn(dt.year, dt.month, dt.day)


def jie_boundaries(year):
    """定位公历年任意时刻月支所需的节界（含上一年大雪）。

    返回按时间升序的 [(datetime, 节名, 所开启的月支索引)]。
    """
    bs = [(astro.solar_term_beijing(year - 1, 255), "大雪", 0)]
    for name in ["小寒", "立春", "惊蛰", "清明", "立夏", "芒种",
                 "小暑", "立秋", "白露", "寒露", "立冬", "大雪"]:
        bs.append((astro.solar_term_beijing(year, _JIE_LON[name]), name, JIE_BRANCH[name]))
    bs.sort(key=lambda x: x[0])
    return bs


def month_pillar_at(dt):
    """北京时间 dt 的月柱（以节为界）。返回 (干支索引, 月支索引, 所在节名)。"""
    for t, name, branch in jie_boundaries(dt.year):
        if t > dt:
            break
        cur = (t, name, branch)
    ygz, _ = year_pillar_at(dt)
    ygan = ygz % 10
    steps = (cur[2] - 2) % 12
    mgan = (WUHU[ygan] + steps) % 10
    return gz_index(mgan, cur[2]), cur[2], cur[1]


def jieqi_table(year):
    """公历年的二十四节气 [(名称, 北京时间 datetime)]，按时间升序（小寒在前）。"""
    out = []
    for name, lon in TERMS:
        out.append((name, astro.solar_term_beijing(year, lon)))
    out.sort(key=lambda x: x[1])
    return out


# ---------------- 农历 ----------------

def _ws_day(year):
    """冬至所在公历年的冬至日数（JDN）。"""
    return _day_num(astro.solar_term_jd(year, 270))


def lunar_month_table(year):
    """构建覆盖 [公历 year-1 年冬至所在月, 公历 year+2 年初] 的农历月表。

    每月一项 dict(start, end, num, leap, ly)：
      start/end 为本月首末日数（JDN，end 为下月首，不含）；
      num 为月序 1..12（正月=1）；leap 为闰月标记；ly 为农历年标签（=该年春节所在公历年）。
    """
    anchors = [_ws_day(year - 1), _ws_day(year), _ws_day(year + 1)]
    jd_start = astro.to_jd(year - 1, 11, 1)
    jd_end = astro.to_jd(year + 2, 3, 1)
    nm_days = [_day_num(j) for j in astro.new_moons_between(jd_start, jd_end)]
    # 去重（同一日内重复不太可能，但保险）
    nm_days = sorted(set(nm_days))

    # 每个月的中气日集合
    zq_days = set()
    for y in (year - 1, year, year + 1):
        for lon in _ZHONGQI_LON:
            zq_days.add(_day_num(astro.solar_term_jd(y, lon)))

    # 月首列表
    starts = [s for s in nm_days]
    n = len(starts)

    def month_idx_of(day):
        """day 所在月的索引。"""
        for i in range(n - 1):
            if starts[i] <= day < starts[i + 1]:
                return i
        raise ValueError("day out of range")

    # 各冬至锚点所在月索引
    a_idx = [month_idx_of(a) for a in anchors]

    months = [None] * n
    # 逐段处理：段 [a_idx[k], a_idx[k+1]) 为一个农历年段，段首为十一月
    for k in range(len(a_idx) - 1):
        lo, hi = a_idx[k], a_idx[k + 1]
        gap = hi - lo
        leap_at = None
        if gap == 13:
            # 置闰：两冬至之间 13 个月，取第一个无中气者为闰月
            for i in range(lo + 1, hi):
                has_zq = any(starts[i] <= d < starts[i + 1] for d in zq_days)
                if not has_zq:
                    leap_at = i
                    break
            if leap_at is None:
                leap_at = hi  # 理论不会发生
        ly = (year - 1) + k
        num = 11
        for i in range(lo, min(hi + 3, n - 1)):
            is_leap = (i == leap_at)
            if is_leap:
                # 闰月沿用上一个月的月序：闰六月位于六月之后、七月之前
                months[i] = {"start": starts[i], "end": starts[i + 1],
                             "num": num - 1, "leap": True, "ly": ly}
                continue
            months[i] = {"start": starts[i], "end": starts[i + 1],
                         "num": num, "leap": False, "ly": ly}
            if num == 12:
                num = 1
                ly += 1
            else:
                num += 1
    return [m for m in months if m is not None]


def lunar_date(y, m, d):
    """公历日期 -> 农历。返回 dict(ly, year_gz, num, leap, day, text)。

    农历年干支以春节所在公历年计（民俗口径）。
    """
    target = astro.jdn(y, m, d)
    table = lunar_month_table(y)
    for mo in table:
        if mo["start"] <= target < mo["end"]:
            gz = GZ60[(mo["ly"] - 1984) % 60]
            leap_pre = "闰" if mo["leap"] else ""
            text = "%s年%s%s月%s" % (gz, leap_pre, LUNAR_MONTHS[mo["num"] - 1],
                                     LUNAR_DAYS[target - mo["start"]])
            return {"ly": mo["ly"], "year_gz": gz, "num": mo["num"],
                    "leap": mo["leap"], "day": target - mo["start"] + 1, "text": text}
    raise ValueError("lunar date not found for %s-%s-%s" % (y, m, d))


def solar_from_lunar(ly, num, leap, day):
    """农历 -> 公历。ly 为农历年标签（春节所在公历年）。"""
    table = lunar_month_table(ly)
    for mo in table:
        if mo["ly"] == ly and mo["num"] == num and mo["leap"] == leap:
            if day < 1 or day > mo["end"] - mo["start"]:
                raise ValueError("农历日超出当月天数")
            return _jdn_to_ymd(mo["start"] + day - 1)
    raise ValueError("农历月不存在")


def _jdn_to_ymd(jdn_val):
    """日数(JDN) -> (y, m, d)。"""
    jd = jdn_val - 0.5
    z = int(jd + 0.5)
    f = jd + 0.5 - z
    if z < 2299161:
        a = z
    else:
        alpha = int((z - 1867216.25) / 36524.25)
        a = z + 1 + alpha - alpha // 4
    b = a + 1524
    c = int((b - 122.1) / 365.25)
    dd = int(365.25 * c)
    e = int((b - dd) / 30.6001)
    day = b - dd - int(30.6001 * e) + f
    month = e - 1 if e < 14 else e - 13
    year = c - 4716 if month > 2 else c - 4715
    return (year, month, int(day))


def month_days_count(num, leap, ly):
    """农历某月天数（供输入校验）。"""
    table = lunar_month_table(ly)
    for mo in table:
        if mo["ly"] == ly and mo["num"] == num and mo["leap"] == leap:
            return mo["end"] - mo["start"]
    raise ValueError("month not found")
