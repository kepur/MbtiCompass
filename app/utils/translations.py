import gettext
from fastapi import Request

# 定义支持的语言
SUPPORTED_LANGUAGES = ["en", "zh", "es"]
DEFAULT_LANGUAGE = "en"

def get_locale(request: Request):
    """ 获取用户的语言偏好 """
    accept_language = request.headers.get("Accept-Language", DEFAULT_LANGUAGE)
    lang = accept_language.split(",")[0].split("-")[0]  # 获取 "zh-CN" -> "zh"
    return lang if lang in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE

def get_translator(lang: str):
    """ 获取 gettext 翻译对象 """
    return gettext.translation(
        "messages",
        localedir="locales",
        languages=[lang],
        fallback=True
    )

def _(text: str, request: Request):
    """ 翻译文本 """
    lang = get_locale(request)
    translator = get_translator(lang)
    return translator.gettext(text)
