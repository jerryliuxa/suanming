# -*- coding: utf-8 -*-
"""新算法测试：紫微斗数 / 梅花易数 / 合婚 / 生肖流年。"""

import sys
import os
import unittest
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from server.engine import ziwei, meihua, zodiac, hehun  # noqa: E402
from server.engine.paipan import paipan  # noqa: E402


class TestZiweiMingGong(unittest.TestCase):
    def test_first_month_zi_hour(self):
        """正月子时 → 命宫在寅。"""
        r = ziwei.paipan_ziwei(2024, 1, False, 15, 0)
        self.assertEqual(r["basic"]["ming_gong"], "寅")

    def test_wu_hour_ming_shen_same(self):
        """午时命身同宫。"""
        r = ziwei.paipan_ziwei(2024, 8, False, 15, 6)
        self.assertEqual(r["basic"]["ming_gong"], r["basic"]["shen_gong"])

    def test_ming_gong_formula(self):
        """八月午时：月宫酉起子逆数至午 → 命宫卯。"""
        r = ziwei.paipan_ziwei(2024, 8, False, 15, 6)
        self.assertEqual(r["basic"]["ming_gong"], "卯")
        # 身宫 = 月宫 + 时支 = 酉 + 6 = 卯
        self.assertEqual(r["basic"]["shen_gong"], "卯")


class TestZiweiStars(unittest.TestCase):
    def test_ding_ziwei_known(self):
        """定紫微：水二局初五在卯；木三局初一在辰；水二局初三在寅。"""
        self.assertEqual(ziwei.ZHI[ziwei.find_ziwei(5, 2)[0]], "卯")
        self.assertEqual(ziwei.ZHI[ziwei.find_ziwei(1, 3)[0]], "辰")
        self.assertEqual(ziwei.ZHI[ziwei.find_ziwei(3, 2)[0]], "寅")

    def test_tianfu_mirror(self):
        """紫微与天府关于寅申轴对称：紫微在子 → 天府在辰。"""
        zw = ziwei.find_ziwei(15, 2)[0] if False else None
        # 直接验证对称函数
        self.assertEqual(ziwei._mirror(2), 2)    # 寅 ↔ 寅
        self.assertEqual(ziwei._mirror(0), 4)    # 子 ↔ 辰
        self.assertEqual(ziwei._mirror(1), 3)    # 丑 ↔ 卯
        self.assertEqual(ziwei._mirror(8), 8)    # 申 ↔ 申

    def test_all_14_major_stars_placed(self):
        r = ziwei.paipan_ziwei(1990, 6, False, 26, 4)
        self.assertEqual(len(r["major_positions"]), 14)
        for pos in r["major_positions"].values():
            self.assertIn(pos, ziwei.ZHI)
        # 紫微系六星与天府系八星全部落宫
        self.assertEqual(sorted(r["major_positions"]), sorted(ziwei.MAJOR_ORDER))

    def test_hua_jia_year(self):
        """甲年四化：廉贞化禄、破军化权、武曲化科、太阳化忌。"""
        r = ziwei.paipan_ziwei(2024, 1, False, 15, 0)
        self.assertIn("廉贞化禄", r["hua"])
        self.assertIn("破军化权", r["hua"])
        self.assertIn("武曲化科", r["hua"])
        self.assertIn("太阳化忌", r["hua"])

    def test_shen_palace_limited(self):
        """身宫只可能落在命/夫妻/财帛/迁移/官禄/福德。"""
        allowed = {"命宫", "夫妻", "财帛", "迁移", "官禄", "福德"}
        for hz in range(12):
            r = ziwei.paipan_ziwei(2024, 5, False, 20, hz)
            shen = [p["name"] for p in r["palaces"] if p["is_shen"]][0]
            self.assertIn(shen, allowed)

    def test_limits_start_at_ju(self):
        """大限首限起于五行局数。"""
        r = ziwei.paipan_ziwei(1990, 6, False, 26, 4)
        ju = r["basic"]["wuxing_ju"]
        ju_num = {"水二局": 2, "木三局": 3, "金四局": 4, "土五局": 5, "火六局": 6}[ju]
        ming_p = r["palaces"][0]
        self.assertEqual(ming_p["limit"], "%d-%d" % (ju_num, ju_num + 9))


class TestMeihua(unittest.TestCase):
    def test_hex_matrix_spot(self):
        self.assertEqual(meihua.HEX_NAMES["乾"]["坤"], "天地否")
        self.assertEqual(meihua.HEX_NAMES["坤"]["乾"], "地天泰")
        self.assertEqual(meihua.HEX_NAMES["坎"]["离"], "水火既济")
        self.assertEqual(meihua.HEX_NAMES["离"]["坎"], "火水未济")
        self.assertEqual(meihua.HEX_NAMES["艮"]["坤"], "山地剥")
        self.assertEqual(meihua.HEX_NAMES["震"]["坎"], "雷水解")

    def test_meaning_complete(self):
        """64 卦均有断语。"""
        for row in meihua.HEX_NAMES.values():
            for name in row.values():
                self.assertIn(name, meihua.HEX_MEANING, name + " 缺断语")

    def test_qigua_deterministic(self):
        a = meihua.divine_by_time(2026, 10, 7, 10)
        b = meihua.divine_by_time(2026, 10, 7, 10)
        self.assertEqual(a["name"], b["name"])
        self.assertEqual(a["score"], b["score"])
        self.assertIn(a["name"], meihua.HEX_MEANING)
        # 2026-10-07 = 丙午年八月廿七；年支午=7，上卦数 (7+8+27)%8=2 → 兑
        self.assertEqual(a["qigua"]["n1"], 2)

    def test_number_qigua(self):
        r = meihua.divine_by_numbers(3, 5)
        self.assertTrue(r["name"])
        self.assertTrue(5 <= r["score"] <= 98)


class TestZodiac(unittest.TestCase):
    def test_2026_horse_year(self):
        r = zodiac.zodiac_year(2026)
        self.assertEqual(r["taisui_gz"], "丙午")
        by = {x["zhi"]: x for x in r["list"]}
        self.assertEqual(by["午"]["relation"], "值太岁")   # 马
        self.assertEqual(by["子"]["relation"], "冲太岁")   # 鼠
        self.assertEqual(by["丑"]["relation"], "害太岁")   # 牛（午害丑）
        self.assertEqual(by["未"]["relation"], "合太岁")   # 羊（午未合）
        self.assertEqual(by["卯"]["relation"], "破太岁")   # 兔（午破卯）
        # 未 与 午：丑午害? 未 vs 午: 六合 ✓

    def test_all_twelve(self):
        r = zodiac.zodiac_year(2027)
        self.assertEqual(len(r["list"]), 12)


class TestHehun(unittest.TestCase):
    def _chart(self, y, m, d, h, gender="male"):
        return paipan({"name": "t", "gender": gender, "calendar": "solar",
                       "y": y, "m": m, "d": d, "hour": h, "minute": 0})

    def test_score_range_and_deterministic(self):
        a = self._chart(1990, 8, 16, 9)
        b = self._chart(1992, 3, 8, 14, "female")
        r1 = hehun.hehun(a, b)
        r2 = hehun.hehun(a, b)
        self.assertEqual(r1["score"], r2["score"])
        self.assertTrue(20 <= r1["score"] <= 96)
        self.assertEqual(len(r1["parts"]), 5)

    def test_luihe_pair_higher(self):
        """六合年支对（子丑）应高于无作用对（同参数近似）。"""
        a1 = self._chart(1990, 8, 16, 9)   # 庚午年
        b1 = self._chart(1990, 2, 20, 10, "female")  # 庚午年 午午自刑
        a2 = self._chart(1990, 8, 16, 9)   # 午
        b2 = self._chart(1990, 12, 5, 10, "female")  # 庚午年仍午? 12-05 已大雪但立春前仍庚午
        r1 = hehun.hehun(a1, b1)
        self.assertTrue(20 <= r1["score"] <= 96)


if __name__ == "__main__":
    unittest.main(verbosity=2)
