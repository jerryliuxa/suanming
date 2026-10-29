# -*- coding: utf-8 -*-
"""塔罗牌：78 张标准韦特体系。每日一抽（按日期+署名确定性）与三牌阵（过去/现在/未来）。

大牌正逆位牌义逐张撰写；小牌由数字原型 × 牌组领域构成通则牌义。
"""

import random
from datetime import date

# ---------- 大阿卡纳（韦特序：8 力量 / 11 正义） ----------
MAJOR = [
    ("愚者", "The Fool", "新的开始、纯真、带着信任的冒险", "鲁莽行事、缺乏计划、不设防"),
    ("魔术师", "The Magician", "显化之力、资源齐备、知行合一", "才未尽用、花言巧语、操弄"),
    ("女祭司", "The High Priestess", "直觉与内在智慧、静观其变", "忽视直觉、被秘密困扰、疏离"),
    ("女皇", "The Empress", "丰饶、滋养、感官与创造之爱", "停滞、过度保护、依赖"),
    ("皇帝", "The Emperor", "权威秩序、稳定结构、担当", "僵化固执、控制欲、父权压力"),
    ("教皇", "The Hierophant", "传统智慧、良师指引、承诺", "教条束缚、为叛逆而叛逆"),
    ("恋人", "The Lovers", "心之选择、价值观契合、深度结合", "失衡关系、价值观冲突、逃避抉择"),
    ("战车", "The Chariot", "意志致胜、驾驭对立、明确方向", "失控狂奔、方向不明、意气用事"),
    ("力量", "Strength", "以柔克刚、温柔驯服本能", "自我怀疑、被情绪牵着走"),
    ("隐士", "The Hermit", "内省求真、独处明心、引路之光", "孤僻封闭、拒绝指引、迷失"),
    ("命运之轮", "Wheel of Fortune", "转机降临、周期流转、顺势而起", "时运不济、抗拒变化、旧循环"),
    ("正义", "Justice", "因果分明、坦诚面对、公平裁决", "偏颇失衡、逃避责任"),
    ("倒吊人", "The Hanged Man", "换位思考、以退为进、心甘情愿的暂停", "无谓牺牲、原地打转"),
    ("死神", "Death", "终结与重生、彻底放手迎来新生", "抗拒改变、苟延残喘"),
    ("节制", "Temperance", "调和鼎鼐、中道平衡、耐心酿造", "极端失衡、火急火燎"),
    ("恶魔", "The Devil", "欲望枷锁、成瘾课题、看似不可离开的关系", "挣脱束缚、看见链条、觉醒"),
    ("塔", "The Tower", "骤变破局、旧结构瓦解、真相反转", "勉强维持摇摇欲坠、惊魂未定"),
    ("星星", "The Star", "希望疗愈、灵感涌动、静水深流", "信心受挫、期望落空"),
    ("月亮", "The Moon", "潜意识与幻象、暧昧不安、直觉敏锐", "迷雾渐散、真相浮现、情绪落地"),
    ("太阳", "The Sun", "喜悦成功、光明磊落、生命力旺盛", "暂时阴霾、过度乐观"),
    ("审判", "Judgement", "觉醒召唤、旧账清算、凤凰涅槃", "自责内耗、对召唤充耳不闻"),
    ("世界", "The World", "圆满达成、一个周期完成、世界在握", "差一步的圆满、未竟之业"),
]

# ---------- 小阿卡纳 ----------
SUIT = {
    "权杖": {"en": "Wands", "elem": "火", "domain": "行动与事业", "note": "热情、开创、竞争与远行"},
    "圣杯": {"en": "Cups", "elem": "水", "domain": "情感与心灵", "note": "爱、关系、直觉与内在感受"},
    "宝剑": {"en": "Swords", "elem": "风", "domain": "思维与沟通", "note": "理智、冲突、真相与决断"},
    "星币": {"en": "Pentacles", "elem": "土", "domain": "物质与现实", "note": "金钱、身体、工作与积累"},
}

RANKS = [
    ("Ace", "王牌", "一粒种子般的开端", "新机遇降临，值得郑重启动", "起点仓促、根基未稳、热情难续"),
    ("2", "二", "两端之间的权衡", "遇到需要协调的二者，平衡可期", "摇摆不定、两头落空、失衡"),
    ("3", "三", "初见成效的生长", "合作与扩展带来初步成果", "协作生隙、进展受阻"),
    ("4", "四", "暂时的稳定与守成", "稳住阵脚，巩固已有的城池", "停滞僵化、安全感成了牢笼"),
    ("5", "五", "波折与失序", "冲突或匮乏带来考验，走走停停", "走出低谷、结束消耗"),
    ("6", "六", "顺流与给予", "柳暗花明，助人与受助皆宜", "有施无受、面子工程、不平等"),
    ("7", "七", "考验与内省", "于坚持中评估策略，沉住气是关键词", "战略摇摆、半途而废"),
    ("8", "八", "加速与精进", "全力推进，势能与练习开始变现", "用力过猛、方向跑偏"),
    ("9", "九", "近成之前的沉淀", "收获在望，于独处中蓄力守心", "警惕过度、睡前焦虑、孤独感"),
    ("10", "十", "一个阶段的收成与终结", "功成圆满，负担亦是传承", "过载、家业生变、曲终人散"),
    ("Page", "侍从", "好奇的探索者", "消息与学习，从零开始尝试", "幼稚拖延、消息不实"),
    ("Knight", "骑士", "义无反顾的行动者", "带着冲劲追逐目标，行动即答案", "横冲直撞、虎头蛇尾"),
    ("Queen", "王后", "向内的滋养者", "以共情与涵养化解局面", "情绪淹没理性、过度付出"),
    ("King", "国王", "成熟的掌控者", "以经验与格局统筹全局", "刚愎自用、权威僵化"),
]

COURT_ZH = {"Page": "侍从", "Knight": "骑士", "Queen": "王后", "King": "国王"}


def _all_cards():
    cards = []
    for i, (zh, en, up, rev) in enumerate(MAJOR):
        cards.append({"id": "M%02d" % i, "num": i, "name": zh, "en": en,
                      "arcana": "大", "up": up, "rev": rev})
    for suit, sinfo in SUIT.items():
        for rank_en, rank_zh, theme, up, rev in RANKS:
            name = ("%s%s" % (suit, COURT_ZH[rank_en])) if rank_en in COURT_ZH else "%s%s" % (suit, rank_zh)
            cards.append({
                "id": "%s-%s" % (suit, rank_en),
                "num": None, "name": name,
                "en": "%s of %s" % (rank_en, sinfo["en"]),
                "arcana": "小", "suit": suit, "elem": sinfo["elem"],
                "up": "%s——%s；落在%s层面（%s）。" % (theme, up, sinfo["domain"], sinfo["note"]),
                "rev": "%s遇阻：%s，%s层面的节奏被打乱。" % (theme, rev, sinfo["domain"]),
            })
    return cards


ALL_CARDS = _all_cards()
BY_ID = {c["id"]: c for c in ALL_CARDS}


def _daily_seed(day, name):
    return "%s|%s" % (day.isoformat(), (name or "").strip().lower())


def daily_card(day=None, name=""):
    """每日一抽：按日期与署名确定（同一天同名同牌）。"""
    day = day or date.today()
    rng = random.Random(_daily_seed(day, name))
    card = rng.choice(ALL_CARDS)
    reversed_ = rng.random() < 0.5
    return {
        "mode": "daily", "date": day.isoformat(),
        "card": card, "reversed": reversed_,
        "meaning": card["rev"] if reversed_ else card["up"],
        "advice": "牌是镜子，照见的是你心里已有的答案；今日一抽仅供娱乐与自省参考。",
    }


def spread_three(question="", seed=None):
    """三牌阵：过去 / 现在 / 未来。"""
    rng = random.Random(seed) if seed is not None else random.SystemRandom()
    picks = rng.sample(ALL_CARDS, 3)
    positions = ["过去", "现在", "未来"]
    cards = []
    for pos, card in zip(positions, picks):
        reversed_ = rng.random() < 0.5
        cards.append({"position": pos, "card": card, "reversed": reversed_,
                      "meaning": card["rev"] if reversed_ else card["up"]})
    majors = sum(1 for c in cards if c["card"]["arcana"] == "大")
    revs = sum(1 for c in cards if c["reversed"])
    suits = [c["card"].get("suit") for c in cards if c["card"].get("suit")]
    dominant = max(set(suits), key=suits.count) if suits else None
    synth = []
    if question:
        synth.append("所问：「%s」。" % question[:60])
    if majors >= 2:
        synth.append("三张中大牌居多，此事关乎人生课题与命运节点，非一日之功。")
    elif majors == 0:
        synth.append("三张皆小牌，事在人为，日常选择决定走向。")
    if revs >= 2:
        synth.append("逆位偏多：内在阻力大于外部障碍，先理顺自己再理顺事情。")
    if dominant:
        synth.append("牌面以「%s」为主轴：留意%s层面的课题。" % (dominant, SUIT[dominant]["domain"]))
    return {
        "mode": "three", "question": question,
        "cards": cards,
        "synthesis": " ".join(synth) or "静心体会三张牌的流动。",
        "advice": "塔罗呈现的是当下的能量快照，未来仍在你手中；仅供娱乐与自省参考。",
    }
