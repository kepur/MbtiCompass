from lunar_python import Lunar, Solar
from typing import Dict, Tuple

# 天干和对应的五行
TIAN_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
TIAN_GAN_WUXING = ["木", "木", "火", "火", "土", "土", "金", "金", "水", "水"]

# 地支和对应的五行
DI_ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
DI_ZHI_WUXING = ["水", "土", "木", "木", "土", "火", "火", "土", "金", "金", "土", "水"]

# 纳音五行表（完整六十甲子）
NAYIN_WUXING = {
    "甲子": "海中金", "乙丑": "海中金", "丙寅": "炉中火", "丁卯": "炉中火",
    "戊辰": "大林木", "己巳": "大林木", "庚午": "路旁土", "辛未": "路旁土",
    "壬申": "剑锋金", "癸酉": "剑锋金", "甲戌": "山头火", "乙亥": "山头火",
    "丙子": "涧下水", "丁丑": "涧下水", "戊寅": "城头土", "己卯": "城头土",
    "庚辰": "白蜡金", "辛巳": "白蜡金", "壬午": "杨柳木", "癸未": "杨柳木",
    "甲申": "泉中水", "乙酉": "泉中水", "丙戌": "屋上土", "丁亥": "屋上土",
    "戊子": "霹雳火", "己丑": "霹雳火", "庚寅": "松柏木", "辛卯": "松柏木",
    "壬辰": "长流水", "癸巳": "长流水", "甲午": "砂石金", "乙未": "砂石金",
    "丙申": "山下火", "丁酉": "山下火", "戊戌": "平地木", "己亥": "平地木",
    "庚子": "壁上土", "辛丑": "壁上土", "壬寅": "金箔金", "癸卯": "金箔金",
    "甲辰": "佛灯火", "乙巳": "佛灯火", "丙午": "天河水", "丁未": "天河水",
    "戊申": "大驿土", "己酉": "大驿土", "庚戌": "钗钏金", "辛亥": "钗钏金",
    "壬子": "桑柘木", "癸丑": "桑柘木", "甲寅": "大溪水", "乙卯": "大溪水",
    "丙辰": "沙中土", "丁巳": "沙中土", "戊午": "天上火", "己未": "天上火",
    "庚申": "石榴木", "辛酉": "石榴木", "壬戌": "大海水", "癸亥": "大海水",
}

def get_lunar_from_solar(year: int, month: int, day: int) -> Dict[str, str]:
    """
    根据公历日期计算农历日期。

    参数:
        year (int): 公历年份，例如 1995
        month (int): 公历月份，例如 8
        day (int): 公历日，例如 15

    返回:
        dict: 包含农历年、月、日的信息
    """
    solar = Solar.fromYmd(year, month, day)
    lunar = solar.getLunar()
    return {
        "lunar_year": lunar.getYearInChinese(),
        "lunar_month": lunar.getMonthInChinese(),
        "lunar_day": lunar.getDayInChinese(),
    }

def get_bazi_and_wuxing_from_solar(year: int, month: int, day: int, birth_time: str) -> Dict:
    """
    根据公历日期和时间计算八字及五行。

    参数:
        year (int): 公历年份，例如 1995
        month (int): 公历月份，例如 8
        day (int): 公历日，例如 15
        birth_time (str): 出生时间，格式 "HH:MM"，例如 "14:30"

    返回:
        dict: 包含八字、五行统计和日主的信息
    """
    if not birth_time:
        raise ValueError("缺少出生时间")
    try:
        hour, minute = map(int, birth_time.split(":"))
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError("时间超出有效范围")
    except ValueError:
        raise ValueError("出生时间格式错误，应为 HH:MM，例如 14:30")

    # 创建公历日期对象，直接传入小时和分钟
    solar = Solar(year, month, day, hour, minute, 0)  # 秒默认为 0
    lunar = solar.getLunar()

    # 获取八字
    bazi = {
        "year": lunar.getYearInGanZhi(),
        "month": lunar.getMonthInGanZhi(),
        "day": lunar.getDayInGanZhi(),
        "hour": lunar.getTimeInGanZhi()
    }

    # 计算五行
    def get_wuxing(ganzhi: str) -> Tuple[str, str, str]:
        tian_gan = ganzhi[0]
        di_zhi = ganzhi[1]
        tg_wuxing = TIAN_GAN_WUXING[TIAN_GAN.index(tian_gan)]
        dz_wuxing = DI_ZHI_WUXING[DI_ZHI.index(di_zhi)]
        nayin = NAYIN_WUXING.get(ganzhi, "未知")
        return (tg_wuxing, dz_wuxing, nayin)

    wuxing = {
        "year": get_wuxing(bazi["year"]),
        "month": get_wuxing(bazi["month"]),
        "day": get_wuxing(bazi["day"]),
        "hour": get_wuxing(bazi["hour"])
    }

    # 五行统计
    wuxing_count = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
    for pillar in wuxing.values():
        wuxing_count[pillar[0]] += 1  # 天干五行
        wuxing_count[pillar[1]] += 1  # 地支五行

    return {
        "bazi": bazi,
        "wuxing": wuxing,
        "wuxing_count": wuxing_count,
        "day_master": wuxing["day"][0]  # 日主
    }

# 测试
if __name__ == "__main__":
    lunar_date = get_lunar_from_solar(1995, 8, 15)
    print("农历日期:", lunar_date)

    result = get_bazi_and_wuxing_from_solar(1995, 8, 15, "14:30")
    print("\n八字:", result["bazi"])
    print("五行 (天干, 地支, 纳音):", result["wuxing"])
    print("五行统计:", result["wuxing_count"])
    print("日主:", result["day_master"])