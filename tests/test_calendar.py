# -*- coding: utf-8 -*-
"""历法层锚点测试：干支纪日、节气时刻、农历（春节/闰月/反查）。"""

import sys
import os
import unittest
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from server.engine import astro, calendar_cn as cal  # noqa: E402
from server.engine.constants import GZ60  # noqa: E402


class TestDayGZ(unittest.TestCase):
    def test_anchor_1949(self):
        self.assertEqual(GZ60[cal.day_gz_index(1949, 10, 1)], "甲子")

    def test_anchor_2000(self):
        self.assertEqual(GZ60[cal.day_gz_index(2000, 1, 1)], "戊午")

    def test_anchor_1990(self):
        self.assertEqual(GZ60[cal.day_gz_index(1990, 8, 16)], "癸丑")

    def test_cycle_60(self):
        i = cal.day_gz_index(2000, 1, 1)
        self.assertEqual(GZ60[(i + 60) % 60], "戊午")
        # 相邻日期干支进一位
        self.assertEqual((cal.day_gz_index(2000, 1, 2) - i) % 60, 1)


class TestSolarTerms(unittest.TestCase):
    def assert_near(self, got, y, mo, d, h, mi, minutes=20):
        expect = datetime(y, mo, d, h, mi)
        diff = abs((got - expect).total_seconds()) / 60.0
        self.assertLess(diff, minutes, "%s vs %s 相差 %.1f 分钟" % (got, expect, diff))

    def test_lichun_2024(self):
        self.assert_near(astro.solar_term_beijing(2024, 315), 2024, 2, 4, 16, 27)

    def test_lichun_2025(self):
        self.assert_near(astro.solar_term_beijing(2025, 315), 2025, 2, 3, 22, 10)

    def test_dongzhi_2024(self):
        self.assert_near(astro.solar_term_beijing(2024, 270), 2024, 12, 21, 17, 20)

    def test_dongzhi_range(self):
        """2000~2030 每年冬至都应落在 12 月 21~23 日。"""
        for y in range(2000, 2031):
            dt = astro.solar_term_beijing(y, 270)
            self.assertEqual(dt.month, 12, y)
            self.assertIn(dt.day, (21, 22, 23), y)

    def test_xiazhi_range(self):
        for y in range(2000, 2031):
            dt = astro.solar_term_beijing(y, 90)
            self.assertEqual(dt.month, 6, y)
            self.assertIn(dt.day, (20, 21, 22), y)


class TestYearMonthPillar(unittest.TestCase):
    def test_year_2000_before_lichun(self):
        gz, y = cal.year_pillar_at(datetime(2000, 1, 1, 12))
        self.assertEqual(GZ60[gz], "己卯")
        self.assertEqual(y, 1999)

    def test_lichun_boundary(self):
        before, _ = cal.year_pillar_at(datetime(2024, 2, 4, 15))
        after, _ = cal.year_pillar_at(datetime(2024, 2, 4, 17))
        self.assertEqual(GZ60[before], "癸卯")
        self.assertEqual(GZ60[after], "甲辰")

    def test_month_2000_01(self):
        gz, branch, name = cal.month_pillar_at(datetime(2000, 1, 1, 12))
        self.assertEqual(GZ60[gz], "丙子")
        self.assertEqual(branch, 0)
        self.assertEqual(name, "大雪")

    def test_month_lichun_boundary(self):
        gz_before, _, _ = cal.month_pillar_at(datetime(2024, 2, 4, 15))
        gz_after, _, _ = cal.month_pillar_at(datetime(2024, 2, 4, 17))
        self.assertEqual(GZ60[gz_before], "乙丑")
        self.assertEqual(GZ60[gz_after], "丙寅")

    def test_wuhu_geng_year(self):
        # 庚午年（1990）寅月起戊寅，申月为甲申
        gz, _, _ = cal.month_pillar_at(datetime(1990, 8, 16, 12))
        self.assertEqual(GZ60[gz], "甲申")


class TestLunar(unittest.TestCase):
    CHUNJIE = [(1980, 2, 16), (1984, 2, 2), (1990, 1, 27), (1997, 2, 7),
               (2000, 2, 5), (2008, 2, 7), (2016, 2, 8), (2020, 1, 25),
               (2023, 1, 22), (2024, 2, 10), (2025, 1, 29), (2026, 2, 17)]

    def test_chunjie_is_first_day(self):
        for y, m, d in self.CHUNJIE:
            ld = cal.lunar_date(y, m, d)
            self.assertEqual((ld["num"], ld["leap"], ld["day"]), (1, False, 1),
                             "%d 春节应为正月初一，得到 %s" % (y, ld["text"]))

    def test_leap_months(self):
        def has_leap(ly, num):
            return any(x["ly"] == ly and x["num"] == num and x["leap"]
                       for x in cal.lunar_month_table(ly))
        self.assertTrue(has_leap(2020, 4))
        self.assertTrue(has_leap(2023, 2))
        self.assertTrue(has_leap(2025, 6))
        self.assertFalse(has_leap(2021, 5))

    def test_solar_from_lunar(self):
        self.assertEqual(cal.solar_from_lunar(2024, 1, False, 1), (2024, 2, 10))
        self.assertEqual(cal.solar_from_lunar(2025, 6, True, 1), (2025, 7, 25))
        self.assertEqual(cal.solar_from_lunar(2020, 5, False, 5), (2020, 6, 25))  # 端午

    def test_roundtrip(self):
        for y, m, d in [(2024, 6, 15), (2023, 9, 1), (2026, 10, 6), (1990, 8, 16)]:
            ld = cal.lunar_date(y, m, d)
            back = cal.solar_from_lunar(ld["ly"], ld["num"], ld["leap"], ld["day"])
            self.assertEqual(back, (y, m, d), "农历往返不一致：%s" % ld["text"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
