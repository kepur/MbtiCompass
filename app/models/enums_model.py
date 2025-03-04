import enum

from enum import Enum as PyEnum

from enum import Enum as PyEnum

class EventType(PyEnum):
    PRIVATE = "私人"
    PUBLIC = "公众"

class PaymentType(PyEnum):
    AA = "AA"  # 各自支付
    ORGANIZER_PAY = "主办方付费"
    FREE = "免费"
    CROWDFUNDING_ONLINE = "众筹（线上）"  # 线上支付到平台
    CROWDFUNDING_OFFLINE = "众筹（线下）"  # 线下支付

# 🔹 星座枚举
class ZodiacEnum(str, PyEnum):
    Aries = "Aries"
    Taurus = "Taurus"
    Gemini = "Gemini"
    Cancer = "Cancer"
    Leo = "Leo"
    Virgo = "Virgo"
    Libra = "Libra"
    Scorpio = "Scorpio"
    Sagittarius = "Sagittarius"
    Capricorn = "Capricorn"
    Aquarius = "Aquarius"
    Pisces = "Pisces"

# 🔹 MBTI 枚举
class MBTIEnum(str, PyEnum):
    INTJ = "INTJ"
    INTP = "INTP"
    ENTJ = "ENTJ"
    ENTP = "ENTP"
    INFJ = "INFJ"
    INFP = "INFP"
    ENFJ = "ENFJ"
    ENFP = "ENFP"
    ISTJ = "ISTJ"
    ISFJ = "ISFJ"
    ESTJ = "ESTJ"
    ESFJ = "ESFJ"
    ISTP = "ISTP"
    ISFP = "ISFP"
    ESTP = "ESTP"
    ESFP = "ESFP"

# 🔹 生辰八字（六十甲子）
class BaziEnum(str, PyEnum):
    JiaZi = "甲子"
    YiChou = "乙丑"
    BingYin = "丙寅"
    DingMao = "丁卯"
    WuChen = "戊辰"
    JiSi = "己巳"
    GengWu = "庚午"
    XinWei = "辛未"
    RenShen = "壬申"
    GuiYou = "癸酉"
    # 继续扩展六十甲子...

# 🔹 教育程度
class EducationEnum(str, PyEnum):
    HighSchool = "High School"
    Bachelors = "Bachelors"
    Masters = "Masters"
    PhD = "PhD"

# 🔹 兴趣爱好（用户可以选择多个）
class HobbyEnum(str,PyEnum):
    Music = "Music"
    Sports = "Sports"
    Gaming = "Gaming"
    Reading = "Reading"
    Travel = "Travel"
    Photography = "Photography"


# 定义性别枚举
class GenderEnum(str, PyEnum):
    MALE = "male"         # 男
    FEMALE = "female"     # 女
    NON_BINARY = "non-binary"  # 非二元性别
    TRANSGENDER = "transgender"  # 跨性别
    OTHER = "other"       # 其他

