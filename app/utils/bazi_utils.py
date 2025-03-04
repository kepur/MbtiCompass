import datetime
import lunarcalendar
from lunarcalendar import Converter, Solar, Lunar

# 天干（10个）
TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

# 地支（12个）
DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 生肖对应地支
SHENGXIAO = {
    "子": "鼠", "丑": "牛", "寅": "虎", "卯": "兔", "辰": "龙", "巳": "蛇",
    "午": "马", "未": "羊", "申": "猴", "酉": "鸡", "戌": "狗", "亥": "猪"
}

# 五行对应天干地支
WUXING = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土", "己": "土",
    "庚": "金", "辛": "金", "壬": "水", "癸": "水",
    "子": "水", "丑": "土", "寅": "木", "卯": "木",
    "辰": "土", "巳": "火", "午": "火", "未": "土",
    "申": "金", "酉": "金", "戌": "土", "亥": "水"
}

# 合婚匹配关系
HEHUN_RELATIONSHIPS = {
    "六合": [("子", "丑"), ("寅", "亥"), ("卯", "戌"), ("辰", "酉"), ("巳", "申"), ("午", "未")],
    "三合": [("申", "子", "辰"), ("亥", "卯", "未"), ("寅", "午", "戌"),
             ("巳", "酉", "丑"), ("午", "戌", "寅"), ("酉", "丑", "巳")],
    "相冲": [("子", "午"), ("丑", "未"), ("寅", "申"), ("卯", "酉"),
             ("辰", "戌"), ("巳", "亥")]
}


def solar_to_lunar(year, month, day):
    """
    将阳历（公历）日期转换为阴历（农历）
    """
    solar_date = Solar(year, month, day)
    lunar_date = Converter.Solar2Lunar(solar_date)
    return lunar_date.year, lunar_date.month, lunar_date.day


def get_bazi(year, month, day, hour):
    """
    计算四柱八字
    """
    lunar_year, lunar_month, lunar_day = solar_to_lunar(year, month, day)

    year_gan_zhi = TIANGAN[(lunar_year - 4) % 10] + DIZHI[(lunar_year - 4) % 12]
    month_gan_zhi = TIANGAN[(lunar_year * 12 + lunar_month) % 10] + DIZHI[lunar_month % 12]
    day_gan_zhi = TIANGAN[(year * 365 + month * 30 + day) % 10] + DIZHI[(year * 365 + month * 30 + day) % 12]
    hour_gan_zhi = TIANGAN[(day * 12 + hour) % 10] + DIZHI[(hour // 2) % 12]

    bazi_wuxing = [WUXING[year_gan_zhi[0]], WUXING[year_gan_zhi[1]],
                   WUXING[month_gan_zhi[0]], WUXING[month_gan_zhi[1]],
                   WUXING[day_gan_zhi[0]], WUXING[day_gan_zhi[1]],
                   WUXING[hour_gan_zhi[0]], WUXING[hour_gan_zhi[1]]]

    return {
        "八字": [year_gan_zhi, month_gan_zhi, day_gan_zhi, hour_gan_zhi],
        "五行": bazi_wuxing,
        "生肖": SHENGXIAO[year_gan_zhi[1]]
    }


def calculate_wuxing_balance(bazi_wuxing):
    """
    计算五行强弱
    """
    wuxing_count = {w: bazi_wuxing.count(w) for w in set(WUXING.values())}
    return wuxing_count


def check_compatibility(person1_bazi, person2_bazi):
    """
    合婚匹配，检查生肖是否六合、三合、相冲
    """
    person1_shengxiao = person1_bazi["生肖"]
    person2_shengxiao = person2_bazi["生肖"]

    # 检查六合
    for pair in HEHUN_RELATIONSHIPS["六合"]:
        if (person1_shengxiao, person2_shengxiao) in pair or (person2_shengxiao, person1_shengxiao) in pair:
            return "六合（非常适合）"

    # 检查三合
    for trio in HEHUN_RELATIONSHIPS["三合"]:
        if person1_shengxiao in trio and person2_shengxiao in trio:
            return "三合（适合）"

    # 检查相冲
    for pair in HEHUN_RELATIONSHIPS["相冲"]:
        if (person1_shengxiao, person2_shengxiao) in pair or (person2_shengxiao, person1_shengxiao) in pair:
            return "相冲（不适合）"

    return "普通匹配"


# 测试案例
if __name__ == "__main__":
    person1_bazi = get_bazi(1998, 10, 20, 14)
    person2_bazi = get_bazi(1997, 3, 15, 10)

    print("Person 1 八字:", person1_bazi["八字"])
    print("Person 1 五行:", person1_bazi["五行"])
    print("Person 1 五行分析:", calculate_wuxing_balance(person1_bazi["五行"]))

    print("\nPerson 2 八字:", person2_bazi["八字"])
    print("Person 2 五行:", person2_bazi["五行"])
    print("Person 2 五行分析:", calculate_wuxing_balance(person2_bazi["五行"]))

    print("\n合婚匹配:", check_compatibility(person1_bazi, person2_bazi))
