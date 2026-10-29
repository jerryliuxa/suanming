# -*- coding: utf-8 -*-
"""排盘 / 批八字 / 运程引擎测试。"""

import sys
import os
import unittest
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from server.engine.paipan import paipan  # noqa: E402
from server.engine.analysis import analyze  # noqa: E402
from server.engine import fortune  # noqa: E402
from server import api  # noqa: E402


def chart_of(**kw):
    inp = {"name": "测试", "gender": "male", "calendar": "solar",
           "y": 2000, "m": 1, "d": 1, "hour": 12, "minute": 0}
    inp.update(kw)
    return paipan(inp)


def pillars(chart):
    return [chart["pillars"][k]["ganzhi"] if chart["pillars"][k] else None
            for k in ("year", "month", "day", "hour")]


class TestPaipan(unittest.TestCase):
    def test_2000_01_01_noon(self):
        c = chart_of()
        self.assertEqual(pillars(c), ["己卯", "丙子", "戊午", "戊午"])
        ss = [c["pillars"][k]["shishen_gan"] for k in ("year", "month", "day", "hour")]
        self.assertEqual(ss, ["劫财", "偏印", "比肩", "比肩"])
        self.assertEqual([c["pillars"][k]["nayin"] for k in ("year", "month", "day")],
                         ["城头土", "涧下水", "天上火"])
        self.assertEqual(c["kongwang"]["day"], ["子", "丑"])
        self.assertEqual(c["taiyuan"], "丁卯")
        self.assertEqual(c["basic"]["zodiac"], "兔")

    def test_1990_08_16_sishi(self):
        c = chart_of(y=1990, m=8, d=16, hour=9, minute=30)
        self.assertEqual(pillars(c), ["庚午", "甲申", "癸丑", "丁巳"])
        self.assertTrue(c["dayun"]["forward"], "阳年男应顺行")
        marks = c["pillars"]["year"]["shensha"]
        self.assertIn("桃花", marks)

    def test_female_yin_year_backward(self):
        # 己卯年（阴年）女命应顺行
        c = chart_of(gender="female")
        self.assertTrue(c["dayun"]["forward"])
        # 阴年男命逆行
        c2 = chart_of(gender="male")
        self.assertFalse(c2["dayun"]["forward"])

    def test_late_zi_modes(self):
        a = chart_of(hour=23, minute=30, zi_mode="late_swap")
        b = chart_of(hour=23, minute=30, zi_mode="early_late")
        self.assertEqual([a["pillars"]["day"]["ganzhi"], a["pillars"]["hour"]["ganzhi"]],
                         ["己未", "甲子"])
        self.assertEqual([b["pillars"]["day"]["ganzhi"], b["pillars"]["hour"]["ganzhi"]],
                         ["戊午", "甲子"])

    def test_early_zi_same(self):
        a = chart_of(hour=0, minute=30, zi_mode="late_swap")
        b = chart_of(hour=0, minute=30, zi_mode="early_late")
        self.assertEqual(pillars(a), pillars(b))
        self.assertEqual(pillars(a), ["己卯", "丙子", "戊午", "壬子"])

    def test_hour_unknown(self):
        c = chart_of(hour=None)
        self.assertIsNone(c["pillars"]["hour"])
        self.assertTrue(c["basic"]["solar_text"].endswith("时辰未知"))

    def test_true_solar(self):
        c = chart_of(y=1990, m=8, d=16, hour=11, minute=0, true_solar=True, lon=87.62)
        self.assertEqual(c["pillars"]["hour"]["ganzhi"], "丙辰")
        self.assertTrue(c["basic"]["true_solar"]["true_solar"])

    def test_dayun_10_steps(self):
        c = chart_of()
        self.assertEqual(len(c["dayun"]["list"]), 10)
        ages = [r["start_age"] for r in c["dayun"]["list"]]
        self.assertEqual(ages[1] - ages[0], 10)


class TestAnalysis(unittest.TestCase):
    def setUp(self):
        self.chart = chart_of(y=1990, m=8, d=16, hour=9, minute=30)
        self.result = analyze(self.chart)

    def test_sections_complete(self):
        titles = [s["title"] for s in self.result["sections"]]
        for t in ["命盘总览", "性格特质", "事业方向", "财运分析", "感情婚姻",
                  "六亲缘分", "健康提示", "开运建议", "大运走势"]:
            self.assertIn(t, titles)

    def test_grade_in_range(self):
        self.assertIn(self.result["ctx"]["grade"],
                      ["从强", "强", "偏强", "中和", "偏弱", "弱", "从弱"])
        self.assertTrue(self.result["ctx"]["xiyong"])

    def test_deterministic(self):
        again = analyze(chart_of(y=1990, m=8, d=16, hour=9, minute=30))
        self.assertEqual(self.result["summary"], again["summary"])


class TestFortune(unittest.TestCase):
    def setUp(self):
        self.chart = chart_of(y=1990, m=8, d=16, hour=9, minute=30)
        self.ctx = analyze(self.chart)["ctx"]

    def test_year_fortune_structure(self):
        yf = fortune.year_fortune(self.chart, 2026, self.ctx)
        self.assertEqual(yf["ganzhi"], "丙午")
        self.assertEqual(len(yf["months"]), 12)
        self.assertTrue(12 <= yf["score"] <= 95)
        for m in yf["months"]:
            self.assertTrue(12 <= m["score"] <= 95)
            self.assertIn(m["grade"], ["上吉", "吉", "平顺", "起伏", "低伏"])

    def test_month_pillars(self):
        """2026 丙午年：寅月应庚寅、卯月辛卯（五虎遁丙辛寻庚起）。"""
        yf = fortune.year_fortune(self.chart, 2026, self.ctx)
        self.assertEqual(yf["months"][0]["ganzhi"], "庚寅")
        self.assertEqual(yf["months"][1]["ganzhi"], "辛卯")
        self.assertEqual(yf["months"][11]["ganzhi"], "辛丑")

    def test_day_fortune(self):
        d = fortune.day_fortune(self.chart, date(2026, 10, 7), self.ctx)
        self.assertEqual(d["ganzhi"], "甲寅")
        self.assertTrue(12 <= d["score"] <= 95)

    def test_deterministic(self):
        a = fortune.year_fortune(self.chart, 2026, self.ctx)
        b = fortune.year_fortune(self.chart, 2026, self.ctx)
        self.assertEqual(a["score"], b["score"])
        self.assertEqual([m["score"] for m in a["months"]], [m["score"] for m in b["months"]])


class TestApi(unittest.TestCase):
    def test_paipan_ok(self):
        r = api.api_paipan({"gender": "male", "y": 2000, "m": 1, "d": 1, "hour": 12})
        self.assertEqual(r["pillars"]["day"]["ganzhi"], "戊午")

    def test_bad_date(self):
        with self.assertRaises(api.ApiError):
            api.api_paipan({"gender": "male", "y": 1899, "m": 1, "d": 1, "hour": 12})
        with self.assertRaises(api.ApiError):
            api.api_paipan({"gender": "male", "y": 2000, "m": 13, "d": 1, "hour": 12})

    def test_lunar_input(self):
        r = api.api_paipan({"gender": "male", "calendar": "lunar", "y": 2024,
                            "m": 1, "d": 1, "hour": 12})
        self.assertEqual(r["basic"]["solar_text"].startswith("2024年02月10"), True)

    def test_bad_lunar(self):
        with self.assertRaises(api.ApiError):
            api.api_paipan({"gender": "male", "calendar": "lunar", "y": 2024,
                            "m": 2, "d": 31, "hour": 12})


if __name__ == "__main__":
    unittest.main(verbosity=2)
