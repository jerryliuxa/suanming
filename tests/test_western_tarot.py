# -*- coding: utf-8 -*-
"""西方占星与塔罗测试。"""

import sys
import os
import math
import unittest
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from server.engine import western, tarot, astro  # noqa: E402


class TestPlanetMachinery(unittest.TestCase):
    def test_sun_cross_check(self):
        """JPL 地球根数推出的太阳地心黄经 与 已验证的 Meeus 太阳黄经一致（<0.5°）。"""
        for jd in (2451545.0, 2459000.0, 2461000.0):
            ex, ey, _ = western._helio("地球", jd)
            sun_jpl = math.degrees(math.atan2(-ey, -ex)) % 360.0
            sun_meeus = astro.sun_apparent_longitude(jd)
            diff = abs((sun_jpl - sun_meeus + 180) % 360 - 180)
            self.assertLess(diff, 0.5, "jd=%s 差异 %.3f°" % (jd, diff))

    def test_planets_deterministic_and_ranged(self):
        p1 = western.planet_longitude("木星", 2461000.0)
        p2 = western.planet_longitude("木星", 2461000.0)
        self.assertEqual(p1, p2)
        for name in ("水星", "金星", "火星", "木星", "土星"):
            lon = western.planet_longitude(name, 2461000.0)
            self.assertTrue(0 <= lon < 360, name)

    def test_new_moon_moon_near_sun(self):
        """2024-02-10 春节（朔，北京 06:53 ≈ UT 22:53 前日）：此刻日月角距应≈0（<1°）。"""
        jd = astro.to_jd(2024, 2, 9, 22.88)   # UT
        self.assertLess(western._ang_diff(western.moon_longitude(jd),
                                          western.sun_longitude(jd)), 1.0)


class TestSigns(unittest.TestCase):
    def test_sun_sign_anchors(self):
        _, _, idx = western.sign_of(western.sun_longitude(astro.to_jd(2000, 1, 1, 12)))
        self.assertEqual(western.SIGNS[idx], "摩羯")
        _, _, idx = western.sign_of(western.sun_longitude(astro.to_jd(2026, 3, 23, 12)))
        self.assertEqual(western.SIGNS[idx], "白羊")

    def test_moon_sign_new_moon_aquarius(self):
        """2024-02-10 朔日在水瓶（太阳约水瓶 21°），月亮应同在水瓶。"""
        jd = astro.to_jd(2024, 2, 10, 12.0)
        sign, _, _ = western.sign_of(western.moon_longitude(jd))
        self.assertEqual(sign, "水瓶")


class TestAscendant(unittest.TestCase):
    def test_ramc_zero_case(self):
        """构造 GMST+经度=0：赤道上 0°白羊中天时，上升应为 0°巨蟹（90°），中天 0°白羊。"""
        jd = 2451545.0  # 2000-01-01 12:00 UT，GMST≈280.46°
        gmst = western.gmst_deg(jd)
        lon = (-gmst) % 360.0
        asc, mc, ramc = western.ascendant_mc(jd, lon, 0.0)
        self.assertAlmostEqual(ramc, 0.0, places=3)
        self.assertAlmostEqual(mc, 0.0, places=3)
        self.assertAlmostEqual(asc, 90.0, places=3)

    def test_asc_mc_separation(self):
        asc, mc, _ = western.ascendant_mc(astro.to_jd(1990, 8, 16, 9.5), 116.41, 39.9)
        self.assertTrue(0 <= asc < 360 and 0 <= mc < 360)
        sep = abs((asc - mc) % 360)
        if sep > 180:
            sep = 360 - sep
        self.assertTrue(40 <= sep <= 150, "上升与中天夹角异常：%s" % sep)


class TestNatalChart(unittest.TestCase):
    def test_beijing_time_sun_altitude(self):
        """时制回归：8 月中旬上午 9:30（北京）太阳地平高度应约 40~50°（曾因误当 UT 得 18°）。"""
        import math
        from datetime import datetime
        jd = astro.beijing_to_jd(datetime(1990, 8, 16, 9, 30))
        asc, mc, ramc = western.ascendant_mc(jd, 116.41, 39.9)
        lam = western.sun_longitude(jd) * math.pi / 180
        eps = 23.4393 * math.pi / 180
        ra = math.atan2(math.sin(lam) * math.cos(eps), math.cos(lam))
        dec = math.asin(math.sin(lam) * math.sin(eps))
        H = ramc * math.pi / 180 - ra
        alt = math.degrees(math.asin(math.sin(dec) * math.sin(math.radians(39.9))
                                     + math.cos(dec) * math.cos(math.radians(39.9)) * math.cos(H)))
        self.assertGreater(alt, 38.0, "太阳高度异常：%.1f°" % alt)
        self.assertLess(alt, 52.0)

    def test_structure(self):
        r = western.natal_chart(1990, 8, 16, 9, 30, 116.41, 39.90, "测试")
        bodies = [p["body"] for p in r["placements"]]
        self.assertEqual(len(bodies), 9)
        for body in ("太阳", "月亮", "水星", "金星", "火星", "木星", "土星", "上升", "中天"):
            self.assertIn(body, bodies)
        self.assertEqual(sum(r["elements"].values()), 5)
        for p in r["placements"]:
            if p.get("house"):
                self.assertTrue(1 <= p["house"] <= 12)

    def test_no_time_no_asc(self):
        r = western.natal_chart(1990, 8, 16, None, None, 116.41, 39.90)
        self.assertFalse(r["has_time"])
        self.assertIsNone(r["basic"]["asc_sign"])

    def test_deterministic(self):
        a = western.natal_chart(1990, 8, 16, 9, 30, 116.41, 39.90)
        b = western.natal_chart(1990, 8, 16, 9, 30, 116.41, 39.90)
        self.assertEqual(a["placements"], b["placements"])


class TestTransitsAndPair(unittest.TestCase):
    def test_daily_transits(self):
        natal = western.natal_chart(1990, 8, 16, 9, 30, 116.41, 39.90)
        t = western.daily_transits(natal)
        self.assertTrue(20 <= t["score"] <= 95)
        self.assertEqual(set(t["transits"]), set(("太阳", "月亮", "水星", "金星", "火星", "木星", "土星")))

    def test_pair(self):
        r = western.compatibility("白羊", "狮子")
        self.assertGreaterEqual(r["score"], 75)   # 同为火象
        r2 = western.compatibility("白羊", "处女")
        self.assertLessEqual(r2["score"], 60)     # 火土磨合组合


class TestTarot(unittest.TestCase):
    def test_deck(self):
        self.assertEqual(len(tarot.ALL_CARDS), 78)
        self.assertEqual(len({c["id"] for c in tarot.ALL_CARDS}), 78)
        self.assertEqual(len(tarot.MAJOR), 22)
        self.assertEqual(tarot.MAJOR[0][0], "愚者")
        self.assertEqual(tarot.MAJOR[21][0], "世界")

    def test_daily_deterministic(self):
        a = tarot.daily_card(date(2026, 10, 7), "张三")
        b = tarot.daily_card(date(2026, 10, 7), "张三")
        self.assertEqual(a["card"]["id"], b["card"]["id"])
        self.assertEqual(a["reversed"], b["reversed"])

    def test_spread_three(self):
        r = tarot.spread_three("近期事业如何")
        self.assertEqual(len(r["cards"]), 3)
        ids = [c["card"]["id"] for c in r["cards"]]
        self.assertEqual(len(set(ids)), 3)
        self.assertEqual([c["position"] for c in r["cards"]], ["过去", "现在", "未来"])
        for c in r["cards"]:
            self.assertTrue(c["meaning"])
        self.assertTrue(r["synthesis"])

    def test_meanings_complete(self):
        for c in tarot.ALL_CARDS:
            self.assertTrue(c["up"] and c["rev"], c["name"] + " 缺牌义")


if __name__ == "__main__":
    unittest.main(verbosity=2)
