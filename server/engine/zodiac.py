# -*- coding: utf-8 -*-
"""生肖流年：十二生肖与流年太岁的值/合/冲/刑/害/破关系与批语。"""

from .constants import ZHI, ZHI_HE6, ZHI_CHONG, zhi_xing, ZHI_HAI, ZHI_PO, ZHI_SHENGXIAO
from . import calendar_cn as cal

REL_TEXT = {
    "值太岁": "本命逢太岁，俗称本命年：运势起伏较大，宜守不宜攻，红绳拜太岁民俗可安神定志。",
    "合太岁": "与太岁相合，人缘顺遂，贵人暗助，惟合中藏绊，防因情面误事。",
    "冲太岁": "岁破之象，变动剧烈：搬迁、跳槽、出行皆多，主动求变可解被动之冲。",
    "刑太岁": "与太岁相刑，是非口舌、规则纠纷偏多，凡事依规而行，远离争执。",
    "害太岁": "与太岁相害，防小人暗损、亲友反目，合伙借贷须格外谨慎。",
    "破太岁": "与太岁相破，旧物易损、计划易散，宜小步慢行、及时止损。",
    "平": "与太岁无刑冲破害，运势如常，稳中有进，照常经营即可。",
}

GRADE = {"值太岁": 52, "合太岁": 72, "冲太岁": 40, "刑太岁": 45, "害太岁": 48, "破太岁": 50, "平": 62}


def relation_to_taisui(zhi, flow_zhi):
    """生肖地支 zhi 与流年支 flow_zhi 的太岁关系。"""
    if zhi == flow_zhi:
        return "值太岁"
    if ZHI_HE6.get(zhi, (None,))[0] == flow_zhi:
        return "合太岁"
    if ZHI_CHONG.get(zhi) == flow_zhi:
        return "冲太岁"
    if zhi_xing(zhi, flow_zhi):
        return "刑太岁"
    if ZHI_HAI.get(zhi) == flow_zhi:
        return "害太岁"
    if ZHI_PO.get(zhi) == flow_zhi:
        return "破太岁"
    return "平"


def zodiac_year(year):
    """某流年十二生肖运程总览。"""
    flow_gz, _ = cal.year_pillar_at(__import__("datetime").datetime(year, 7, 1))
    flow_zhi = flow_gz % 12
    out = []
    for z in range(12):
        rel = relation_to_taisui(z, flow_zhi)
        score = GRADE[rel]
        out.append({
            "zhi": ZHI[z],
            "shengxiao": ZHI_SHENGXIAO[z],
            "relation": rel,
            "score": score,
            "grade": ("吉" if score >= 70 else "平" if score >= 55 else "起伏"),
            "text": REL_TEXT[rel],
        })
    return {"year": year, "taisui_gz": __import__("server.engine.constants", fromlist=["GZ60"]).GZ60[flow_gz],
            "taisui_zhi": ZHI[flow_zhi], "list": out}
