import json
import os
import html
import random
from datetime import datetime, timedelta

import streamlit as st
import streamlit.components.v1 as components


# =========================
# 기본 설정
# =========================
st.set_page_config(page_title="2026 Fortune", layout="centered")

APP_URL = "https://my-fortune.streamlit.app"  # 본인 배포 URL로 유지/변경
DB_PATH = "data/fortune_db.json"

LANGS = [
    ("ko", "한국어"),
    ("en", "English"),
    ("ja", "日本語"),
    ("zh", "中文"),
    ("ru", "Русский"),
    ("hi", "हिन्दी"),
]

# =========================
# I18N (UI 라벨)
# =========================
I18N = {
    "ko": {
        "lang_label": "언어 / Language",
        "title": "2026 띠 + MBTI + 사주 + 오늘/내일/주/월 운세",
        "caption": "완전 무료",
        "name_placeholder": "이름 입력 (결과에 표시돼요)",
        "birth_title": "생년월일 입력",
        "mbti_mode": "MBTI 어떻게 할까?",
        "direct": "직접 선택",
        "simple12": "간단 테스트 (12문항)",
        "test16": "상세 테스트 (16문항)",
        "test_start_12": "간단 테스트 시작! 12문항만 답하면 MBTI가 나와요",
        "test_start_16": "상세 테스트 시작! 하나씩 답해주세요",
        "energy": "에너지 방향",
        "info": "정보 수집",
        "decision": "결정 방식",
        "life": "생활 방식",
        "result_btn": "결과 보기!",
        "fortune_btn": "운세 보기!",
        "reset": "처음부터 다시하기",
        "share_btn": "친구에게 결과 공유하기",
        "share_hint": "모바일은 공유창(카톡/문자 등)이 뜹니다. PC는 복사로 동작할 수 있어요.",
        "tarot_btn": "오늘의 타로 카드 보기",
        "tarot_title": "오늘의 타로 카드",
        "zodiac_title": "띠 운세",
        "mbti_title": "MBTI 특징",
        "saju_title": "사주 한 마디",
        "combo": "최고 조합!",
        "overall_title": "핵심 총평",
        "combo_title": "조합 한 마디",
        "lucky_color_title": "럭키 컬러",
        "lucky_item_title": "럭키 아이템",
        "luck_scores": "운세 지수",
        "work": "일/학업",
        "money": "재물",
        "love": "연애",
        "health": "건강",
        "people": "인간관계",
        "keyword": "키워드",
        "mood": "기분/에너지",
        "caution": "주의할 점",
        "best_time": "행운 시간",
        "lucky_number": "행운 숫자",
        "do_this": "오늘의 미션",
        "one_line": "한 줄 조언",
        "weekly_strategy": "이번 주 전략",
        "tabs_today": "오늘",
        "tabs_tomorrow": "내일",
        "tabs_week": "이번 주",
        "tabs_month": "이번 달",
        "today_focus": "포인트",
        "copy_fallback": "공유가 안 되면 아래 텍스트를 복사해서 보내세요.",
        "share_text_title": "공유 텍스트",

        "ad_badge": "광고",
        "dananum_title": "정수기 렌탈 대박!",
        "dananum_line1": "제휴카드면 월 0원부터!",
        "dananum_line2": "설치 당일 최대 50만원 지원 + 사은품 듬뿍",
        "dananum_btn": "다나눔렌탈.com 바로가기",
        "ad_slot_label": "AD",
        "ad_slot_sub": "(승인 후 이 위치에 광고가 표시됩니다)",

        "year": "년", "month": "월", "day": "일",
        "invalid_year": "생년은 1900~2030년 사이로 입력해주세요!",
        "mbti_select": "MBTI 선택",
    },
    "en": {
        "lang_label": "Language",
        "title": "2026 Zodiac + MBTI + Fortune (Day/Week/Month)",
        "caption": "Completely Free",
        "name_placeholder": "Enter name (shown in result)",
        "birth_title": "Birth date",
        "mbti_mode": "How to do MBTI?",
        "direct": "Direct pick",
        "simple12": "Quick test (12)",
        "test16": "Detailed test (16)",
        "test_start_12": "Quick test! Answer 12 questions to get MBTI",
        "test_start_16": "Detailed test start! Answer one by one",
        "energy": "Energy",
        "info": "Information",
        "decision": "Decision",
        "life": "Lifestyle",
        "result_btn": "Show result!",
        "fortune_btn": "Show fortune!",
        "reset": "Start over",
        "share_btn": "Share with friends",
        "share_hint": "On mobile it opens share sheet. On PC it may copy.",
        "tarot_btn": "Today's Tarot",
        "tarot_title": "Today's Tarot",
        "zodiac_title": "Zodiac",
        "mbti_title": "MBTI",
        "saju_title": "Saju",
        "combo": "Best combo!",
        "overall_title": "Main summary",
        "combo_title": "Combo line",
        "lucky_color_title": "Lucky color",
        "lucky_item_title": "Lucky item",
        "luck_scores": "Luck scores",
        "work": "Work/Study",
        "money": "Money",
        "love": "Love",
        "health": "Health",
        "people": "People",
        "keyword": "Keyword",
        "mood": "Mood/Energy",
        "caution": "Caution",
        "best_time": "Lucky time",
        "lucky_number": "Lucky number",
        "do_this": "Mission",
        "one_line": "One-line advice",
        "weekly_strategy": "Weekly strategy",
        "tabs_today": "Today",
        "tabs_tomorrow": "Tomorrow",
        "tabs_week": "This week",
        "tabs_month": "This month",
        "today_focus": "Focus",
        "copy_fallback": "If share doesn't work, copy the text below.",
        "share_text_title": "Share text",

        "ad_slot_label": "AD",
        "ad_slot_sub": "(Ads appear here after approval)",

        "year": "Year", "month": "Month", "day": "Day",
        "invalid_year": "Please enter a birth year between 1900 and 2030!",
        "mbti_select": "Select MBTI",
    },
    "ja": {
        "lang_label": "言語 / Language",
        "title": "2026 干支 + MBTI + 運勢（今日/明日/週/月）",
        "caption": "完全無料",
        "name_placeholder": "名前（結果に表示）",
        "birth_title": "生年月日",
        "mbti_mode": "MBTI は？",
        "direct": "直接選択",
        "simple12": "簡単テスト（12）",
        "test16": "詳細テスト（16）",
        "test_start_12": "簡単テスト開始！12問でMBTIが出ます",
        "test_start_16": "詳細テスト開始！順番に答えてください",
        "energy": "エネルギー",
        "info": "情報収集",
        "decision": "意思決定",
        "life": "生活スタイル",
        "result_btn": "結果を見る！",
        "fortune_btn": "運勢を見る！",
        "reset": "最初から",
        "share_btn": "友達に共有",
        "share_hint": "スマホは共有画面が開きます。PCはコピーの場合があります。",
        "tarot_btn": "今日のタロット",
        "tarot_title": "今日のタロット",
        "zodiac_title": "干支",
        "mbti_title": "MBTI",
        "saju_title": "サジュ",
        "combo": "最高の組み合わせ！",
        "overall_title": "総評",
        "combo_title": "一言",
        "lucky_color_title": "ラッキーカラー",
        "lucky_item_title": "ラッキーアイテム",
        "luck_scores": "運勢スコア",
        "work": "仕事/学業",
        "money": "金運",
        "love": "恋愛",
        "health": "健康",
        "people": "人間関係",
        "keyword": "キーワード",
        "mood": "気分/エネルギー",
        "caution": "注意点",
        "best_time": "ラッキータイム",
        "lucky_number": "ラッキーナンバー",
        "do_this": "今日のミッション",
        "one_line": "一言アドバイス",
        "weekly_strategy": "今週の戦略",
        "tabs_today": "今日",
        "tabs_tomorrow": "明日",
        "tabs_week": "今週",
        "tabs_month": "今月",
        "today_focus": "ポイント",
        "copy_fallback": "共有できない場合は下のテキストをコピーしてください。",
        "share_text_title": "Share text",

        "ad_slot_label": "AD",
        "ad_slot_sub": "（承認後ここに広告が表示されます）",

        "year": "年", "month": "月", "day": "日",
        "invalid_year": "1900〜2030の間で入力してください。",
        "mbti_select": "MBTI を選択",
    },
    "zh": {
        "lang_label": "语言 / Language",
        "title": "2026 生肖 + MBTI + 运势（今日/明日/周/月）",
        "caption": "完全免费",
        "name_placeholder": "输入姓名（显示在结果中）",
        "birth_title": "生日",
        "mbti_mode": "MBTI 怎么做？",
        "direct": "直接选择",
        "simple12": "简测（12题）",
        "test16": "详测（16题）",
        "test_start_12": "简测开始！回答12题即可得到MBTI",
        "test_start_16": "详测开始！请依次回答",
        "energy": "精力方向",
        "info": "信息获取",
        "decision": "决策方式",
        "life": "生活方式",
        "result_btn": "查看结果！",
        "fortune_btn": "查看运势！",
        "reset": "重新开始",
        "share_btn": "分享给朋友",
        "share_hint": "手机会弹出分享面板；电脑可能变成复制。",
        "tarot_btn": "今日塔罗",
        "tarot_title": "今日塔罗",
        "zodiac_title": "生肖",
        "mbti_title": "MBTI",
        "saju_title": "四柱一句",
        "combo": "最佳组合！",
        "overall_title": "总评",
        "combo_title": "组合一句",
        "lucky_color_title": "幸运色",
        "lucky_item_title": "幸运物",
        "luck_scores": "运势指数",
        "work": "工作/学习",
        "money": "财运",
        "love": "感情",
        "health": "健康",
        "people": "人际",
        "keyword": "关键词",
        "mood": "情绪/能量",
        "caution": "注意事项",
        "best_time": "幸运时间",
        "lucky_number": "幸运数字",
        "do_this": "今日任务",
        "one_line": "一句建议",
        "weekly_strategy": "本周策略",
        "tabs_today": "今天",
        "tabs_tomorrow": "明天",
        "tabs_week": "本周",
        "tabs_month": "本月",
        "today_focus": "重点",
        "copy_fallback": "若分享无反应，请复制下方文本发送。",
        "share_text_title": "Share text",

        "ad_slot_label": "AD",
        "ad_slot_sub": "（审核通过后此处显示广告）",

        "year": "年", "month": "月", "day": "日",
        "invalid_year": "请输入1900到2030之间的年份。",
        "mbti_select": "选择 MBTI",
    },
    "ru": {
        "lang_label": "Язык / Language",
        "title": "2026 Зодиак + MBTI + Удача（день/неделя/месяц）",
        "caption": "Бесплатно",
        "name_placeholder": "Имя (в результате)",
        "birth_title": "Дата рождения",
        "mbti_mode": "Как MBTI?",
        "direct": "Выбрать вручную",
        "simple12": "Быстрый тест (12)",
        "test16": "Тест (16)",
        "test_start_12": "Быстрый тест! 12 вопросов — и MBTI готов",
        "test_start_16": "Тест! Ответьте по порядку",
        "energy": "Энергия",
        "info": "Информация",
        "decision": "Решения",
        "life": "Стиль жизни",
        "result_btn": "Показать!",
        "fortune_btn": "Узнать удачу!",
        "reset": "Сначала",
        "share_btn": "Поделиться",
        "share_hint": "На телефоне откроется «Поделиться». На ПК может копировать.",
        "tarot_btn": "Таро на сегодня",
        "tarot_title": "Таро",
        "zodiac_title": "Зодиак",
        "mbti_title": "MBTI",
        "saju_title": "Саджу",
        "combo": "Лучшее сочетание!",
        "overall_title": "Итог",
        "combo_title": "Фраза",
        "lucky_color_title": "Цвет удачи",
        "lucky_item_title": "Предмет удачи",
        "luck_scores": "Индексы удачи",
        "work": "Работа/учёба",
        "money": "Деньги",
        "love": "Любовь",
        "health": "Здоровье",
        "people": "Люди",
        "keyword": "Ключ",
        "mood": "Настроение",
        "caution": "Осторожно",
        "best_time": "Счастливое время",
        "lucky_number": "Счастливое число",
        "do_this": "Задание",
        "one_line": "Совет",
        "weekly_strategy": "Стратегия недели",
        "tabs_today": "Сегодня",
        "tabs_tomorrow": "Завтра",
        "tabs_week": "Неделя",
        "tabs_month": "Месяц",
        "today_focus": "Фокус",
        "copy_fallback": "Если не работает — скопируйте текст ниже.",
        "share_text_title": "Share text",

        "ad_slot_label": "AD",
        "ad_slot_sub": "(Реклама появится после одобрения)",

        "year": "Год", "month": "Месяц", "day": "День",
        "invalid_year": "Введите год рождения от 1900 до 2030.",
        "mbti_select": "Выберите MBTI",
    },
    "hi": {
        "lang_label": "भाषा / Language",
        "title": "2026 राशि + MBTI + भाग्य (दिन/सप्ताह/महीना)",
        "caption": "पूरी तरह मुफ्त",
        "name_placeholder": "नाम (परिणाम में दिखेगा)",
        "birth_title": "जन्म तिथि",
        "mbti_mode": "MBTI कैसे?",
        "direct": "सीधे चुनें",
        "simple12": "क्विक टेस्ट (12)",
        "test16": "टेस्ट (16)",
        "test_start_12": "क्विक टेस्ट! 12 सवालों में MBTI",
        "test_start_16": "टेस्ट शुरू! एक-एक करके जवाब दें",
        "energy": "ऊर्जा",
        "info": "जानकारी",
        "decision": "निर्णय",
        "life": "जीवन शैली",
        "result_btn": "देखें!",
        "fortune_btn": "भाग्य देखें!",
        "reset": "रीसेट",
        "share_btn": "साझा करें",
        "share_hint": "मोबाइल पर शेयर स्क्रीन खुलेगी; PC पर कॉपी हो सकता है।",
        "tarot_btn": "आज का टैरो",
        "tarot_title": "टैरो",
        "zodiac_title": "राशि",
        "mbti_title": "MBTI",
        "saju_title": "Saju",
        "combo": "बेस्ट कॉम्बो!",
        "overall_title": "सार",
        "combo_title": "कॉम्बो लाइन",
        "lucky_color_title": "लकी रंग",
        "lucky_item_title": "लकी आइटम",
        "luck_scores": "लuck स्कोर",
        "work": "काम/पढ़ाई",
        "money": "पैसा",
        "love": "प्यार",
        "health": "स्वास्थ्य",
        "people": "लोग",
        "keyword": "कीवर्ड",
        "mood": "मूड/ऊर्जा",
        "caution": "सावधानी",
        "best_time": "लकी समय",
        "lucky_number": "लकी नंबर",
        "do_this": "मिशन",
        "one_line": "सलाह",
        "weekly_strategy": "इस हफ्ते की रणनीति",
        "tabs_today": "आज",
        "tabs_tomorrow": "कल",
        "tabs_week": "इस हफ्ते",
        "tabs_month": "इस महीने",
        "today_focus": "फोकस",
        "copy_fallback": "यदि शेयर न चले, नीचे का टेक्स्ट कॉपी करें।",
        "share_text_title": "Share text",

        "ad_slot_label": "AD",
        "ad_slot_sub": "(अनुमोदन के बाद विज्ञापन)",

        "year": "वर्ष", "month": "महीना", "day": "दिन",
        "invalid_year": "कृपया 1900 से 2030 के बीच वर्ष दर्ज करें।",
        "mbti_select": "MBTI चुनें",
    },
}


def T(lang: str, key: str) -> str:
    return I18N.get(lang, {}).get(key) or I18N["en"].get(key) or key


# =========================
# CSS (모바일/가림 방지)
# =========================
st.markdown(
    """
<style>
.block-container{
  padding-top: 1.1rem !important;
  padding-bottom: 2.0rem !important;
}
div[data-baseweb="radio"] label{
  white-space: normal !important;
  line-height: 1.25 !important;
}
html, body, [class*="css"]{
  font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Noto Sans KR","Apple SD Gothic Neo","Malgun Gothic",sans-serif;
}
.stButton > button{
  border-radius: 18px !important;
  padding: 0.85rem 1rem !important;
  font-weight: 900 !important;
}
</style>
""",
    unsafe_allow_html=True,
)


# =========================
# DB 로드 (없으면 에러 안내)
# =========================
@st.cache_data(show_spinner=False)
def load_db(path: str):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


DB = load_db(DB_PATH)


def db(lang: str, key: str, fallback_lang="en"):
    """DB에서 lang 우선, 없으면 en fallback"""
    if not DB:
        return None
    if lang in DB and key in DB[lang]:
        return DB[lang][key]
    if fallback_lang in DB and key in DB[fallback_lang]:
        return DB[fallback_lang][key]
    return None


# =========================
# 유틸
# =========================
def seeded_pick(items, seed: int):
    r = random.Random(seed)
    return items[r.randrange(len(items))]


def get_zodiac_index(year: int) -> int:
    return (year - 4) % 12


def get_period_seed(base_date: datetime, period: str) -> int:
    """
    period: 'today'/'tomorrow'/'week'/'month'
    """
    if period == "today":
        d = base_date
        return int(d.strftime("%Y%m%d"))
    if period == "tomorrow":
        d = base_date + timedelta(days=1)
        return int(d.strftime("%Y%m%d"))
    if period == "week":
        # ISO week 기준
        y, w, _ = base_date.isocalendar()
        return y * 100 + w
    if period == "month":
        return base_date.year * 100 + base_date.month
    return int(base_date.strftime("%Y%m%d"))


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def make_scores(seed: int, zodiac_idx: int, mbti: str):
    r = random.Random(seed + zodiac_idx * 97 + sum(ord(c) for c in mbti))
    def score():
        return r.randint(55, 95)
    return {
        "work": score(),
        "money": score(),
        "love": score(),
        "health": score(),
        "people": score(),
    }


def score_grade(lang: str, s: int):
    # 문구 뽑을 때 grade로도 활용 가능
    s = int(s)
    if s >= 86:
        return ("S", {"ko": "최고", "en": "Excellent", "ja": "最高", "zh": "极佳", "ru": "Отлично", "hi": "बहुत अच्छा"}).get(lang, "Excellent")
    if s >= 75:
        return ("A", {"ko": "좋음", "en": "Good", "ja": "良い", "zh": "不错", "ru": "Хорошо", "hi": "अच्छा"}).get(lang, "Good")
    if s >= 65:
        return ("B", {"ko": "보통", "en": "Okay", "ja": "普通", "zh": "一般", "ru": "Норм", "hi": "ठीक"}).get(lang, "Okay")
    return ("C", {"ko": "주의", "en": "Caution", "ja": "注意", "zh": "注意", "ru": "Осторожно", "hi": "सावधानी"}).get(lang, "Caution")


def bar_html(pct: int):
    pct = clamp(int(pct), 0, 100)
    return f"""
    <div style="background:rgba(0,0,0,0.07); border-radius:999px; height:10px; overflow:hidden; margin-top:6px;">
      <div style="width:{pct}%; height:10px; background:linear-gradient(90deg, rgba(111,66,193,0.85), rgba(231,76,60,0.75));"></div>
    </div>
    """


def render_ad_placeholder(lang: str):
    components.html(
        f"""
    <div style="
        margin: 14px 6px 8px 6px;
        padding: 14px 14px;
        border: 1.6px dashed rgba(142,68,173,0.45);
        border-radius: 18px;
        background: rgba(255,255,255,0.55);
        text-align: center;
        font-family: -apple-system,Segoe UI,Roboto,'Noto Sans KR',sans-serif;
    ">
        <div style="font-size:0.82em; color:#6f42c1; font-weight:900; letter-spacing:1px; margin-bottom:4px;">
            {html.escape(T(lang, "ad_slot_label"))}
        </div>
        <div style="font-size:0.9em; color:#888;">
            {html.escape(T(lang, "ad_slot_sub"))}
        </div>
    </div>
    """,
        height=90,
    )


def render_dananum_ad_ko_only(lang: str):
    if lang != "ko":
        return
    components.html(
        f"""
    <div style="
        margin: 14px 6px 8px 6px;
        padding: 16px 14px;
        border: 2px solid rgba(231,76,60,0.35);
        border-radius: 18px;
        background: rgba(255,255,255,0.78);
        text-align: center;
        box-shadow: 0 8px 24px rgba(0,0,0,0.10);
        font-family: -apple-system,Segoe UI,Roboto,'Noto Sans KR',sans-serif;
    ">
        <div style="display:flex; justify-content:center; align-items:center; gap:8px; margin-bottom:8px;">
            <span style="
                font-size:0.78em; padding:4px 10px; border-radius:999px;
                background: rgba(231,76,60,0.10);
                border: 1px solid rgba(231,76,60,0.25);
                color:#e74c3c; font-weight:900;">
                {html.escape(T(lang, "ad_badge"))}
            </span>
            <span style="font-weight:900; color:#d35400;">{html.escape(T(lang, "dananum_title"))}</span>
        </div>
        <div style="font-size:1.0em; color:#333; line-height:1.6; margin:6px 0 4px 0;">
            {html.escape(T(lang, "dananum_line1"))}
        </div>
        <div style="font-size:1.0em; color:#333; line-height:1.6; margin:0 0 14px 0;">
            {html.escape(T(lang, "dananum_line2"))}
        </div>
        <a href="https://www.다나눔렌탈.com" target="_blank" style="text-decoration:none;">
            <button style="
                background: #ffffff;
                color: #e67e22;
                padding: 12px 18px;
                border: 1.6px solid rgba(230,126,34,0.55);
                border-radius: 14px;
                font-weight:900;
                font-size: 1.0em;
                cursor: pointer;
                box-shadow: 0 6px 18px rgba(230,126,34,0.18);
            ">{html.escape(T(lang, "dananum_btn"))}</button>
        </a>
    </div>
    """,
        height=180,
    )


def share_button_component(lang: str, button_label: str, share_text: str, share_url: str):
    safe_text = share_text.replace("\\", "\\\\").replace("`", "\\`")
    safe_url = share_url.replace("\\", "\\\\").replace("`", "\\`")
    hint = T(lang, "share_hint").replace("\\", "\\\\").replace("`", "\\`")

    components.html(
        f"""
        <div style="text-align:center; margin: 8px 0 14px 0; font-family:-apple-system,Segoe UI,Roboto,'Noto Sans KR',sans-serif;">
            <button id="shareBtn" style="
                background:#6f42c1; color:white; padding:16px 22px;
                border:none; border-radius:999px; font-size:1.05em; font-weight:900;
                box-shadow: 0 10px 24px rgba(111,66,193,0.25); cursor:pointer;
                width: min(520px, 92%);
            ">{html.escape(button_label)}</button>
            <div style="margin-top:10px; font-size:0.92em; color:#666;">{html.escape(hint)}</div>
        </div>

        <script>
        (function() {{
            const btn = document.getElementById("shareBtn");
            const text = `{safe_text}`;
            const url  = `{safe_url}`;

            btn.addEventListener("click", async () => {{
                try {{
                    if (navigator.share) {{
                        await navigator.share({{
                            text: text,
                            url: url
                        }});
                        return;
                    }}
                }} catch (e) {{}}

                try {{
                    if (navigator.clipboard && navigator.clipboard.writeText) {{
                        await navigator.clipboard.writeText(text + "\\n" + url);
                        alert("Copied! Paste it to share.");
                    }} else {{
                        alert("Share not supported. Copy text below.");
                    }}
                }} catch (e) {{
                    alert("Share not supported. Copy text below.");
                }}
            }});
        }})();
        </script>
        """,
        height=120,
    )


def render_fortune_card(
    lang: str,
    name_line: str,
    zodiac_name: str,
    zodiac_desc: str,
    mbti: str,
    mbti_desc: str,
    saju: str,
    keyword: str,
    mood: str,
    overall: str,
    combo_line: str,
    lucky_color: str,
    lucky_item: str,
    best_time: str,
    lucky_number: int,
    caution: str,
    mission: str,
    one_line: str,
    weekly_strategy: str,
    scores: dict,
    detail_sentences: dict,
    focus_line: str,
):
    def e(x): return html.escape(str(x))

    # 디테일 문장 (각 카테고리 1개씩)
    work_line = detail_sentences["work"]
    money_line = detail_sentences["money"]
    love_line = detail_sentences["love"]
    health_line = detail_sentences["health"]
    people_line = detail_sentences["people"]

    html_block = f"""
    <div style="
        margin: 10px 6px 10px 6px;
        padding: 16px 14px;
        border-radius: 18px;
        background: linear-gradient(135deg, rgba(161,140,209,0.30), rgba(251,194,235,0.28), rgba(142,197,252,0.28));
        border: 1px solid rgba(142,68,173,0.18);
        text-align: center;
        font-family: -apple-system,Segoe UI,Roboto,'Noto Sans KR',sans-serif;
    ">
        <div style="font-size:1.45em; font-weight:900; color:#5e2b97;">
            {e(name_line)}2026
        </div>
        <div style="font-size:1.12em; font-weight:900; color:#222; margin-top:6px;">
            {e(zodiac_name)} · {e(mbti)}
        </div>
        <div style="font-size:1.0em; font-weight:900; color:#6f42c1; margin-top:8px;">
            {e(T(lang, "combo"))}
        </div>
    </div>

    <div style="
        margin: 12px 6px 12px 6px;
        padding: 18px 16px;
        border-radius: 18px;
        background: rgba(255,255,255,0.94);
        border: 1.6px solid rgba(142,68,173,0.22);
        box-shadow: 0 10px 26px rgba(0,0,0,0.10);
        font-family: -apple-system,Segoe UI,Roboto,'Noto Sans KR',sans-serif;
    ">
        <div style="display:flex; gap:10px; flex-wrap:wrap; margin-bottom:10px;">
            <div style="padding:8px 12px; border-radius:999px; background:rgba(111,66,193,0.08); border:1px solid rgba(111,66,193,0.18); font-weight:900; color:#6f42c1;">
                {e(T(lang,'keyword'))}: {e(keyword)}
            </div>
            <div style="padding:8px 12px; border-radius:999px; background:rgba(231,76,60,0.06); border:1px solid rgba(231,76,60,0.14); font-weight:900; color:#d35400;">
                {e(T(lang,'mood'))}: {e(mood)}
            </div>
        </div>

        <div style="font-size:1.02em; line-height:1.95; color:#111; text-align:left;">
            <b>{e(T(lang,'today_focus'))}</b>: {e(focus_line)}<br><br>

            <b>{e(T(lang,'zodiac_title'))}</b>: {e(zodiac_desc)}<br>
            <b>{e(T(lang,'mbti_title'))}</b>: {e(mbti_desc)}<br>
            <b>{e(T(lang,'saju_title'))}</b>: {e(saju)}<br><br>

            <b>{e(T(lang,'overall_title'))}</b>: {e(overall)}<br>
            <b>{e(T(lang,'combo_title'))}</b>: {e(combo_line)}<br><br>

            <b>{e(T(lang,'luck_scores'))}</b><br>

            <div style="margin-top:10px;">
                <div style="font-weight:900;">{e(T(lang,'work'))}: {scores['work']}/100</div>
                {bar_html(scores['work'])}
                <div style="margin-top:6px; color:#222;">• {e(work_line)}</div>

                <div style="font-weight:900; margin-top:14px;">{e(T(lang,'money'))}: {scores['money']}/100</div>
                {bar_html(scores['money'])}
                <div style="margin-top:6px; color:#222;">• {e(money_line)}</div>

                <div style="font-weight:900; margin-top:14px;">{e(T(lang,'love'))}: {scores['love']}/100</div>
                {bar_html(scores['love'])}
                <div style="margin-top:6px; color:#222;">• {e(love_line)}</div>

                <div style="font-weight:900; margin-top:14px;">{e(T(lang,'health'))}: {scores['health']}/100</div>
                {bar_html(scores['health'])}
                <div style="margin-top:6px; color:#222;">• {e(health_line)}</div>

                <div style="font-weight:900; margin-top:14px;">{e(T(lang,'people'))}: {scores['people']}/100</div>
                {bar_html(scores['people'])}
                <div style="margin-top:6px; color:#222;">• {e(people_line)}</div>
            </div>

            <br>
            <b>{e(T(lang,'lucky_color_title'))}</b>: {e(lucky_color)} &nbsp; | &nbsp;
            <b>{e(T(lang,'lucky_item_title'))}</b>: {e(lucky_item)}<br>
            <b>{e(T(lang,'best_time'))}</b>: {e(best_time)} &nbsp; | &nbsp;
            <b>{e(T(lang,'lucky_number'))}</b>: {lucky_number}<br><br>

            <b>{e(T(lang,'caution'))}</b>: {e(caution)}<br>
            <b>{e(T(lang,'do_this'))}</b>: {e(mission)}<br>
            <b>{e(T(lang,'one_line'))}</b>: {e(one_line)}<br><br>

            <div style="
                padding:12px 12px;
                border-radius:14px;
                background:rgba(142,197,252,0.18);
                border:1px solid rgba(142,197,252,0.35);
            ">
                <b>{e(T(lang,'weekly_strategy'))}</b><br>
                {e(weekly_strategy)}
            </div>
        </div>
    </div>
    """
    components.html(html_block, height=980)


# =========================
# MBTI 질문(12/16) - DB에서 가져옴
# =========================
def get_mbti_pack(lang: str, pack_key: str):
    packs = db(lang, "mbti_questions") or db("en", "mbti_questions")
    if not packs:
        return None
    return packs.get(pack_key) or (db("en", "mbti_questions") or {}).get(pack_key)


def compute_mbti_from_answers(answers):
    """
    answers: list of tuples like [('E','I',choice), ...]
    """
    counts = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}
    for a, b, picked in answers:
        if picked == a:
            counts[a] += 1
        else:
            counts[b] += 1
    ei = "E" if counts["E"] >= counts["I"] else "I"
    sn = "S" if counts["S"] >= counts["N"] else "N"
    tf = "T" if counts["T"] >= counts["F"] else "F"
    jp = "J" if counts["J"] >= counts["P"] else "P"
    return ei + sn + tf + jp


# =========================
# 세션 초기화
# =========================
if "lang" not in st.session_state:
    st.session_state.lang = "ko"
if "result_shown" not in st.session_state:
    st.session_state.result_shown = False
if "mbti" not in st.session_state:
    st.session_state.mbti = None
if "name" not in st.session_state:
    st.session_state.name = ""
if "year" not in st.session_state:
    st.session_state.year = 2005
if "month" not in st.session_state:
    st.session_state.month = 1
if "day" not in st.session_state:
    st.session_state.day = 1


# =========================
# 언어 선택
# =========================
lang_codes = [c for c, _ in LANGS]
lang_labels = [f"{name} ({code})" for code, name in LANGS]
default_idx = lang_codes.index(st.session_state.lang) if st.session_state.lang in lang_codes else 0
selected = st.radio(T(st.session_state.lang, "lang_label"), lang_labels, index=default_idx, horizontal=True)
st.session_state.lang = lang_codes[lang_labels.index(selected)]
lang = st.session_state.lang


# =========================
# DB 없으면 안내
# =========================
if DB is None:
    st.error("data/fortune_db.json 파일이 필요합니다. 아래 제공한 JSON을 그대로 추가하세요.")
    st.stop()


# =========================
# 입력 화면
# =========================
if not st.session_state.result_shown:
    st.markdown(
        f"<h1 style='text-align:center; color:#6f42c1; margin:10px 0 6px 0;'>{html.escape(T(lang,'title'))}</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='text-align:center; color:#777; margin:0 0 14px 0;'>{html.escape(T(lang,'caption'))}</p>",
        unsafe_allow_html=True,
    )

    # 광고 (한국어만 다나눔렌탈)
    render_dananum_ad_ko_only(lang)
    render_ad_placeholder(lang)

    st.session_state.name = st.text_input(T(lang, "name_placeholder"), value=st.session_state.name)

    st.markdown(f"### {T(lang,'birth_title')}")
    c1, c2, c3 = st.columns(3)
    st.session_state.year = c1.number_input(T(lang, "year"), min_value=1900, max_value=2030, value=st.session_state.year, step=1)
    st.session_state.month = c2.number_input(T(lang, "month"), min_value=1, max_value=12, value=st.session_state.month, step=1)
    st.session_state.day = c3.number_input(T(lang, "day"), min_value=1, max_value=31, value=st.session_state.day, step=1)

    mbti_mode = st.radio(T(lang, "mbti_mode"), [T(lang, "direct"), T(lang, "simple12"), T(lang, "test16")])

    # 직접 선택
    if mbti_mode == T(lang, "direct"):
        mbti_keys = db(lang, "mbti_desc_keys") or db("en", "mbti_desc_keys") or []
        if not mbti_keys:
            mbti_keys = [
                "INTJ","INTP","ENTJ","ENTP","INFJ","INFP","ENFJ","ENFP",
                "ISTJ","ISFJ","ESTJ","ESFJ","ISTP","ISFP","ESTP","ESFP"
            ]
        mbti_input = st.selectbox(T(lang, "mbti_select"), sorted(mbti_keys))
        if st.button(T(lang, "fortune_btn"), use_container_width=True):
            st.session_state.mbti = mbti_input
            st.session_state.result_shown = True
            st.rerun()

    # 12문항
    elif mbti_mode == T(lang, "simple12"):
        pack = get_mbti_pack(lang, "simple12")
        st.markdown(f"#### {T(lang,'test_start_12')}")
        if not pack:
            st.error("MBTI 질문 DB가 없습니다. fortune_db.json을 확인하세요.")
            st.stop()

        answers = []
        for i, q in enumerate(pack["questions"]):
            label = q["q"]
            opt_a = q["a"]["text"]
            opt_b = q["b"]["text"]
            picked = st.radio(label, [opt_a, opt_b], key=f"q12_{i}")
            # 어떤 축인지
            a_dim = q["a"]["dim"]
            b_dim = q["b"]["dim"]
            answers.append((a_dim, b_dim, a_dim if picked == opt_a else b_dim))

        if st.button(T(lang, "result_btn"), use_container_width=True):
            st.session_state.mbti = compute_mbti_from_answers(answers)
            st.session_state.result_shown = True
            st.rerun()

    # 16문항
    else:
        pack = get_mbti_pack(lang, "detail16")
        st.markdown(f"#### {T(lang,'test_start_16')}")
        if not pack:
            st.error("MBTI 질문 DB가 없습니다. fortune_db.json을 확인하세요.")
            st.stop()

        answers = []
        # 4개씩 섹션
        sections = [
            ("EI", T(lang, "energy")),
            ("SN", T(lang, "info")),
            ("TF", T(lang, "decision")),
            ("JP", T(lang, "life")),
        ]

        for sec_key, sec_title in sections:
            st.subheader(sec_title)
            for i, q in enumerate([x for x in pack["questions"] if x["axis"] == sec_key]):
                label = q["q"]
                opt_a = q["a"]["text"]
                opt_b = q["b"]["text"]
                picked = st.radio(label, [opt_a, opt_b], key=f"q16_{sec_key}_{i}")
                a_dim = q["a"]["dim"]
                b_dim = q["b"]["dim"]
                answers.append((a_dim, b_dim, a_dim if picked == opt_a else b_dim))

        if st.button(T(lang, "result_btn"), use_container_width=True):
            st.session_state.mbti = compute_mbti_from_answers(answers)
            st.session_state.result_shown = True
            st.rerun()


# =========================
# 결과 화면
# =========================
if st.session_state.result_shown:
    if not (1900 <= st.session_state.year <= 2030):
        st.error(T(lang, "invalid_year"))
        if st.button(T(lang, "reset"), use_container_width=True):
            st.session_state.clear()
            st.rerun()
        st.stop()

    base_date = datetime.now()
    zodiac_idx = get_zodiac_index(st.session_state.year)
    mbti = st.session_state.mbti or "ENFP"
    name_line = (st.session_state.name.strip() + " ") if st.session_state.name.strip() else ""

    # DB 데이터
    zlist = db(lang, "zodiacs") or db("en", "zodiacs")
    zodiac_name = zlist[zodiac_idx]["name"]
    zodiac_desc = zlist[zodiac_idx]["desc"]

    mbti_desc_map = db(lang, "mbti_desc") or db("en", "mbti_desc")
    mbti_desc = mbti_desc_map.get(mbti, mbti)

    saju_msgs = db(lang, "saju_msgs") or db("en", "saju_msgs")
    saju = saju_msgs[(st.session_state.year + st.session_state.month + st.session_state.day) % len(saju_msgs)]

    # 공통 뽑기 함수들
    def pick(key, seed):
        arr = db(lang, key) or db("en", key)
        return seeded_pick(arr, seed)

    def pick_from_dict(key, subkey, seed):
        d = db(lang, key) or db("en", key)
        arr = d[subkey]
        return seeded_pick(arr, seed)

    def build_detail_sentences(period_seed, scores):
        # 카테고리별 "구체 문장"을 DB에서 뽑음
        cat_db = db(lang, "category_msgs") or db("en", "category_msgs")

        out = {}
        for cat in ["work", "money", "love", "health", "people"]:
            grade_code, grade_text = score_grade(lang, scores[cat])
            # grade별 문장 풀에서 뽑되, zodiac/mbti/period에 따라 seed 흔들기
            arr = cat_db[cat].get(grade_code) or cat_db[cat]["B"]
            out[cat] = seeded_pick(arr, period_seed + zodiac_idx * 19 + sum(ord(c) for c in mbti) + len(cat) * 7)

        return out

    # 탭별 렌더 함수
    def render_period(period: str):
        pseed = get_period_seed(base_date, period)

        keyword = pick("keywords", pseed + zodiac_idx * 3)
        mood = pick("moods", pseed + zodiac_idx * 5)
        overall = pick("overall_fortunes", pseed + zodiac_idx * 7)
        combo_line = seeded_pick(db(lang, "combo_comments") or db("en", "combo_comments"), pseed + zodiac_idx * 11).format(zodiac_name, mbti_desc)

        lucky_color = pick("lucky_colors", pseed + zodiac_idx * 13)
        lucky_item = pick("lucky_items", pseed + zodiac_idx * 17)

        caution = pick("cautions", pseed + zodiac_idx * 19)
        mission = pick("missions", pseed + zodiac_idx * 23)
        one_line = pick("one_lines", pseed + zodiac_idx * 29)
        weekly_strategy = pick("weekly_strategies", pseed + zodiac_idx * 31)

        # 포인트 문장: 기간별로 다른 풀 사용
        focus_key = {
            "today": "focus_today",
            "tomorrow": "focus_tomorrow",
            "week": "focus_week",
            "month": "focus_month",
        }[period]
        focus_line = pick(focus_key, pseed + zodiac_idx * 37)

        # 시간/숫자
        times = db(lang, "best_times") or db("en", "best_times")
        best_time = seeded_pick(times, pseed + zodiac_idx * 41)
        lucky_number = random.Random(pseed + zodiac_idx * 43).randint(1, 9)

        # 점수 + 디테일 문장
        scores = make_scores(pseed, zodiac_idx, mbti)
        detail_sentences = build_detail_sentences(pseed, scores)

        render_fortune_card(
            lang=lang,
            name_line=name_line,
            zodiac_name=zodiac_name,
            zodiac_desc=zodiac_desc,
            mbti=mbti,
            mbti_desc=mbti_desc,
            saju=saju,
            keyword=keyword,
            mood=mood,
            overall=overall,
            combo_line=combo_line,
            lucky_color=lucky_color,
            lucky_item=lucky_item,
            best_time=best_time,
            lucky_number=lucky_number,
            caution=caution,
            mission=mission,
            one_line=one_line,
            weekly_strategy=weekly_strategy,
            scores=scores,
            detail_sentences=detail_sentences,
            focus_line=focus_line,
        )

        # 공유 텍스트(탭별)
        share_text = (
            f"{name_line}2026\n"
            f"{zodiac_name} · {mbti}\n"
            f"{T(lang,'combo')}\n\n"
            f"{T(lang,'keyword')}: {keyword}\n"
            f"{T(lang,'mood')}: {mood}\n\n"
            f"{T(lang,'overall_title')}: {overall}\n"
            f"{T(lang,'combo_title')}: {combo_line}\n\n"
            f"{T(lang,'luck_scores')} - "
            f"{T(lang,'work')} {scores['work']}/100: {detail_sentences['work']}\n"
            f"{T(lang,'money')} {scores['money']}/100: {detail_sentences['money']}\n"
            f"{T(lang,'love')} {scores['love']}/100: {detail_sentences['love']}\n"
            f"{T(lang,'health')} {scores['health']}/100: {detail_sentences['health']}\n"
            f"{T(lang,'people')} {scores['people']}/100: {detail_sentences['people']}\n\n"
            f"{T(lang,'lucky_color_title')}: {lucky_color}\n"
            f"{T(lang,'lucky_item_title')}: {lucky_item}\n"
            f"{T(lang,'best_time')}: {best_time} / {T(lang,'lucky_number')}: {lucky_number}\n\n"
            f"{T(lang,'caution')}: {caution}\n"
            f"{T(lang,'do_this')}: {mission}\n"
            f"{T(lang,'one_line')}: {one_line}\n"
        )

        # 광고 자리 + 한국어 광고
        render_ad_placeholder(lang)
        render_dananum_ad_ko_only(lang)

        # 타로
        with st.expander(T(lang, "tarot_btn"), expanded=False):
            tarot = db(lang, "tarot_cards") or db("en", "tarot_cards")
            card = random.choice(list(tarot.keys()))
            st.success(f"{T(lang,'tarot_title')}: {card} - {tarot[card]}")

        # 공유 버튼(모바일 공유시트 / PC 복사 fallback)
        share_button_component(lang, T(lang, "share_btn"), share_text, APP_URL)

        st.caption(T(lang, "copy_fallback"))
        st.text_area(T(lang, "share_text_title"), share_text + "\n" + APP_URL, height=220)
        st.caption(APP_URL)

    # 탭 UI
    tab1, tab2, tab3, tab4 = st.tabs([T(lang, "tabs_today"), T(lang, "tabs_tomorrow"), T(lang, "tabs_week"), T(lang, "tabs_month")])
    with tab1:
        render_period("today")
    with tab2:
        render_period("tomorrow")
    with tab3:
        render_period("week")
    with tab4:
        render_period("month")

    if st.button(T(lang, "reset"), use_container_width=True):
        st.session_state.clear()
        st.rerun()
