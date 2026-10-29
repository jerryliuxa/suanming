# -*- coding: utf-8 -*-
"""八字合婚：双方命例对照评分（年支/日支关系、日干关系、纳音、五行互补）。"""

from .constants import (
    GAN, ZHI, GAN_HE, ZHI_HE6, ZHI_CHONG, zhi_xing, ZHI_HAI, ZHI_PO,
    SHENG, KE, nayin_of,
)

from . import texts as T


def _rel_score(a, b):
    """地支两两关系打分，返回 (分, 关系名列表)。"""
    s, rels = 0, []
    if a == b:
        rels.append("同支")
    if ZHI_HE6.get(a, (None,))[0] == b:
        s += 15; rels.append("六合")
    for name, members, _wx in [("申子辰", frozenset((8, 0, 4)), None), ("寅午戌", frozenset((2, 6, 10)), None),
                               ("巳酉丑", frozenset((5, 9, 1)), None), ("亥卯未", frozenset((11, 3, 7)), None)]:
        if a in members and b in members and a != b:
            s += 12; rels.append("三合局（%s）" % name)
            break
    if ZHI_CHONG.get(a) == b:
        s -= 12; rels.append("相冲")
    xing = zhi_xing(a, b)
    if xing:
        s -= 9; rels.append("相刑（%s）" % xing)
    if ZHI_HAI.get(a) == b:
        s -= 7; rels.append("相害")
    if ZHI_PO.get(a) == b:
        s -= 4; rels.append("相破")
    if not rels:
        rels.append("无特殊作用")
        s += 3
    return s, rels


def _gan_rel(a, b):
    """日干关系。"""
    wa, wb = GAN[a], GAN[b]
    from .constants import GAN_WX
    wxa, wxb = GAN_WX[a], GAN_WX[b]
    if GAN_HE[a][0] == b:
        return 14, "天干五合（%s%s合）" % (GAN[a], GAN[b])
    if wxa == wxb:
        return 4, "日干比和（同为%s）" % wxa
    if SHENG[wxb] == wxa:
        return 8, "彼生我（%s生%s）" % (wb, wa)
    if SHENG[wxa] == wxb:
        return 5, "我生彼（%s生%s）" % (wa, wb)
    if KE[wxa] == wxb:
        return -4, "我克彼（%s克%s）" % (wa, wb)
    if KE[wxb] == wxa:
        return -7, "彼克我（%s克%s）" % (wb, wa)
    return 0, ""


def hehun(chart_a, chart_b):
    """合婚评分。chart 为 paipan 结果。"""
    ya = chart_a["pillars"]["year"]["gz_index"]
    yb = chart_b["pillars"]["year"]["gz_index"]
    da = chart_a["pillars"]["day"]["gz_index"]
    db = chart_b["pillars"]["day"]["gz_index"]
    day_gan_a = chart_a["_meta"]["day_gz"] % 10
    day_gan_b = chart_b["_meta"]["day_gz"] % 10

    parts = []
    total = 55

    s, rels = _rel_score(ya % 12, yb % 12)
    total += s
    parts.append(("生肖年支", s, "%s vs %s：%s" % (ZHI[ya % 12], ZHI[yb % 12], "、".join(rels))))

    s, rels = _rel_score(da % 12, db % 12)
    applied = round(s * 1.3)
    total += applied
    parts.append(("日支配偶宫", applied, "%s vs %s：%s" % (ZHI[da % 12], ZHI[db % 12], "、".join(rels))))

    s, text = _gan_rel(day_gan_a, day_gan_b)
    total += s
    parts.append(("日主关系", s, text))

    na_a = nayin_of(ya)
    na_b = nayin_of(yb)
    wxa, wxb = na_a[-1], na_b[-1]
    if wxa == wxb:
        s = 5; t = "年命纳音比和（%s / %s）" % (na_a, na_b)
    elif SHENG[wxb] == wxa:
        s = 8; t = "彼方纳音生我（%s 生 %s）" % (na_b, na_a)
    elif SHENG[wxa] == wxb:
        s = 6; t = "我方纳音生彼（%s 生 %s）" % (na_a, na_b)
    elif KE[wxa] == wxb or KE[wxb] == wxa:
        s = -5; t = "纳音相克（%s / %s）" % (na_a, na_b)
    else:
        s = 0; t = "年命纳音无生克（%s / %s）" % (na_a, na_b)
    total += s
    parts.append(("年命纳音", s, t))

    # 五行互补
    wxa_dist = chart_a["wuxing"]["scores"]
    wxb_dist = chart_b["wuxing"]["scores"]
    notes = []
    bonus = 0
    for wx in ("木", "火", "土", "金", "水"):
        if wxa_dist[wx] == 0 and wxb_dist[wx] >= 2:
            bonus += 5
            notes.append("彼方补我之%s" % wx)
        if wxb_dist[wx] == 0 and wxa_dist[wx] >= 2:
            bonus += 5
            notes.append("我方补彼之%s" % wx)
    total += min(bonus, 12)
    parts.append(("五行互补", min(bonus, 12), "；".join(notes) if notes else "两人五行结构相似，无特别互补"))

    total = int(round(max(20, min(96, total))))
    if total >= 85:
        grade, verdict = "天作之合", "两人干支呼应极佳，互为助力，是难得的良缘格局。"
    elif total >= 72:
        grade, verdict = "上等婚配", "整体契合度高，虽有小小磨合，不碍大局，宜相互珍惜。"
    elif total >= 58:
        grade, verdict = "中吉之配", "缘分平顺，性情有互补亦有差异，经营得当可稳中有升。"
    elif total >= 45:
        grade, verdict = "缘分平平", "两人节奏不同，须多沟通包容，避免各执己见。"
    else:
        grade, verdict = "多磨之象", "干支作用偏冲克，聚散磨合较多，宜晚婚缓嫁、以时间换空间。"

    key_points = []
    for name, s, text in parts:
        tag = "吉" if s >= 8 else ("忌" if s <= -4 else "平")
        key_points.append("【%s · %s %+d】%s" % (name, tag, s, text))

    return {
        "score": total,
        "grade": grade,
        "verdict": verdict,
        "parts": [{"name": n, "score": int(s), "text": t} for n, s, t in parts],
        "key_points": key_points,
        "advice": "合婚以年支、日支配偶宫与日主关系为纲，重在相处之道；评分仅供文化娱乐参考，感情成败终在人为。",
    }
