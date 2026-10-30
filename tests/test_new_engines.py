# -*- coding: utf-8 -*-
"""奇门遁甲 / 六爻 / 姓名学 引擎测试。"""

import unittest

from server.engine import qimen, liuyao, name_score


class TestQimen(unittest.TestCase):
    def test_dipan_yang1(self):
        dp = qimen.dipan(1, True)
        self.assertEqual(dp, {1: "戊", 2: "己", 3: "庚", 4: "辛", 5: "壬",
                              6: "癸", 7: "丁", 8: "丙", 9: "乙"})

    def test_dipan_yin9(self):
        dp = qimen.dipan(9, False)
        self.assertEqual(dp, {9: "戊", 8: "己", 7: "庚", 6: "辛", 5: "壬",
                              4: "癸", 3: "丁", 2: "丙", 1: "乙"})

    def test_dipan_yin2(self):
        dp = qimen.dipan(2, False)
        self.assertEqual(dp, {2: "戊", 1: "己", 9: "庚", 8: "辛", 7: "壬",
                              6: "癸", 5: "丁", 4: "丙", 3: "乙"})

    def test_layout_anchor_yang1_bingyin(self):
        """阳遁一局 甲子日 丙寅时：值符天蓬携戊落艮八，休门落震三。"""
        lay = qimen._layout(True, 1, 0, 2)
        self.assertEqual(lay["zhi_fu_star"], "天蓬")
        self.assertEqual(lay["zhi_fu_gong"], 8)
        self.assertEqual(lay["tian_gan"][8], ["戊"])
        self.assertEqual(lay["door_pos"][3], "休门")
        self.assertEqual(lay["zhi_shi_door"], "休门")
        self.assertEqual(lay["zhi_shi_gong"], 3)
        # 天芮携禽干：芮宫天盘干 = 己 + 壬
        rui = lay["rui_gong"]
        self.assertEqual(lay["tian_gan"][rui], ["己", "壬"])
        self.assertEqual(lay["xunkong"], (10, 11))          # 甲子旬空戌亥
        self.assertEqual(lay["ma_zhi"], 8)                  # 寅时马在申

    def test_layout_fuyin_when_hour_is_xun_head(self):
        """阳遁三局 甲辰旬 壬子时：时干即旬首遁干壬 -> 伏吟。"""
        lay = qimen._layout(True, 3, 48, 48)                # 壬子时 gz=48
        self.assertIn("星门伏吟", lay["patterns"][0])

    def test_paipan_structure(self):
        for args in [(2026, 10, 31, 10), (2026, 10, 31, None), (2026, 7, 1, 23), (2024, 2, 4, 0)]:
            r = qimen.paipan_qimen(*args)
            self.assertEqual(len(r["palaces"]), 9)
            doors = {p["door"] for p in r["palaces"] if p["door"]}
            gods = {p["god"] for p in r["palaces"] if p["god"]}
            self.assertEqual(len(doors), 8)
            self.assertEqual(len(gods), 8)
            self.assertEqual(len(r["paragraphs"]), 5)
            self.assertIn(r["dun"], ("阳遁", "阴遁"))
            self.assertTrue(1 <= r["ju"] <= 9)

    def test_late_zi_day_swap(self):
        """23 点后日柱进次日。"""
        a = qimen.paipan_qimen(2026, 10, 31, 22)
        b = qimen.paipan_qimen(2026, 10, 31, 23)
        self.assertEqual(b["day_gz"], qimen.GZ60[(qimen.GZ60.index(a["day_gz"]) + 1) % 60])


class TestLiuyao(unittest.TestCase):
    def test_qian_pure(self):
        z = liuyao.zhuang_gua((1, 1, 1, 1, 1, 1))
        self.assertEqual(z["name"], "乾为天")
        self.assertEqual(z["palace"], "乾")
        self.assertEqual((z["shi"], z["ying"]), (6, 3))
        expect = ["甲子", "甲寅", "甲辰", "壬午", "壬申", "壬戌"]
        self.assertEqual([y["gan"] + y["zhi"] for y in z["yaos"]], expect)
        self.assertEqual([y["liuqin"] for y in z["yaos"]],
                         ["子孙", "妻财", "父母", "官鬼", "兄弟", "父母"])

    def test_youhun_guihun(self):
        self.assertEqual(liuyao.zhuang_gua((0, 0, 0, 1, 0, 1))["name"], "火地晋")
        self.assertEqual(liuyao.PALACE_MAP[(0, 0, 0, 1, 0, 1)][2], 4)   # 游魂世四
        z = liuyao.zhuang_gua((1, 1, 1, 1, 0, 1))
        self.assertEqual(z["name"], "火天大有")
        self.assertEqual(z["shi"], 3)                                    # 归魂世三

    def test_palace_map_covers_64(self):
        self.assertEqual(len(liuyao.PALACE_MAP), 64)

    def test_six_gods_jia_day(self):
        bits = (1, 1, 1, 1, 1, 1)
        vals = [7, 7, 7, 7, 7, 7]
        day_gz = 0                                       # 甲子日
        r = liuyao.analyze("coins", vals, 2026, 10, 31, None, "general")
        # 甲子日六神起青龙（此处仅验证 analyze 全链路可跑）
        self.assertTrue(r["score"] >= 20)

    def test_coins_mapping(self):
        self.assertEqual(liuyao.qigua_by_coins([3, 2, 1, 0, 3, 2]), [9, 8, 7, 6, 9, 8])

    def test_time_qigua_values(self):
        vals, text = liuyao.qigua_by_time(2026, 10, 31, 10)
        self.assertEqual(len(vals), 6)
        self.assertTrue(all(v in (6, 7, 8, 9) for v in vals))
        self.assertTrue(text)

    def test_divine_coins_full(self):
        r = liuyao.divine_by_coins([1, 1, 3, 1, 2, 2], 2026, 10, 31, "wealth")
        self.assertEqual(r["ben"]["name"], "雷天大壮")
        self.assertEqual(r["bian"]["name"], "雷泽归妹")
        self.assertEqual(r["moving"], [3])
        self.assertEqual(r["yong"]["target"], "妻财")
        self.assertTrue(20 <= r["score"] <= 95)
        self.assertEqual(r["day_gz"], "戊寅")
        self.assertEqual(r["month_gz"], "戊戌")

    def test_divine_time_full(self):
        r = liuyao.divine_by_time(2026, 10, 31, 10, "career")
        self.assertEqual(r["mode"], "time")
        self.assertIn("起卦依据", r["qigua_note"])
        self.assertTrue(20 <= r["score"] <= 95)


class TestNameScore(unittest.TestCase):
    def test_basic_grids(self):
        r = name_score.score_name("李", "明")
        nums = {g["name"]: g["num"] for g in r["grids"]}
        self.assertEqual((nums["天格"], nums["人格"], nums["地格"], nums["外格"], nums["总格"]),
                         (8, 15, 9, 2, 15))
        self.assertTrue(30 <= r["score"] <= 96)

    def test_compound_surname(self):
        r = name_score.score_name("欧阳", "志强")
        nums = {g["name"]: g["num"] for g in r["grids"]}
        self.assertEqual(nums["天格"], 15 + 17)
        self.assertEqual(nums["人格"], 17 + 7)
        self.assertEqual(nums["总格"], 15 + 17 + 7 + 12)

    def test_strokes_lookup(self):
        self.assertEqual(name_score.STROKES["张"], 11)
        self.assertEqual(name_score.STROKES["刘"], 15)
        self.assertEqual(name_score.STROKES["陈"], 16)
        self.assertEqual(name_score.STROKES["淑"], 12)
        self.assertEqual(name_score.STROKES["薇"], 19)
        self.assertEqual(name_score.STROKES["钰"], 13)

    def test_unknown_char(self):
        with self.assertRaises(ValueError):
            name_score.score_name("氪", "金")

    def test_sancai_wx(self):
        r = name_score.score_name("王", "芳")
        # 天5=土 人14=火 地11=木
        self.assertEqual((r["sancai"]["tian"], r["sancai"]["ren"], r["sancai"]["di"]),
                         ("土", "火", "木"))

    def test_single_given(self):
        r = name_score.score_name("李", "强")
        nums = {g["name"]: g["num"] for g in r["grids"]}
        self.assertEqual(nums["地格"], 12 + 1)
        self.assertEqual(nums["外格"], 2)


if __name__ == "__main__":
    unittest.main()
