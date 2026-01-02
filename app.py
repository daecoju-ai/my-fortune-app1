import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, date
import random
import hashlib

# =========================================================
# Page Config
# =========================================================
st.set_page_config(page_title="2026 Fortune × MBTI", layout="centered")

# =========================================================
# CSS (모바일 최적화 + 상단 가림 방지)
# =========================================================
st.markdown(
    """
<style>
header, footer {visibility:hidden;}
.block-container {padding-top: 0.7rem; padding-bottom: 2rem; max-width: 880px;}
html, body, [class*="css"] {font-family: system-ui, -apple-system, "Noto Sans KR", "Segoe UI", Arial, sans-serif;}

.hero {
  background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 50%, #8ec5fc 100%);
  border-radius: 22px;
  padding: 14px 14px 12px 14px;
  margin: 6px 0 12px 0;
  color: white;
  text-align: center;
  text-shadow: 0 2px 10px rgba(0,0,0,0.25);
}
.hero-title {font-size: 1.85rem; font-weight: 900; margin: 0;}
.hero-sub {opacity: 0.88; font-size: 0.98rem; margin-top: 6px;}

.card {
  background: rgba(255,255,255,0.96);
  border-radius: 20px;
  padding: 16px;
  box-shadow: 0 10px 28px rgba(0,0,0,0.12);
  border: 1px solid rgba(140,120,180,0.18);
  margin: 10px 0;
}
.card-title {font-weight: 900; margin-bottom: 8px;}
.mini {font-size: 0.92rem; opacity: 0.78;}

.ad-reserved {
  border: 2px dashed rgba(160,120,220,0.55);
  border-radius: 18px;
  padding: 12px;
  text-align: center;
  margin: 10px 0 14px 0;
}

.ad-ko {
  background: #fffbe6;
  border: 2px solid rgba(230,126,34,0.35);
  border-radius: 20px;
  padding: 16px;
  text-align: center;
  margin: 10px 0 14px 0;
}
.badge {
  display:inline-block;
  padding:4px 10px;
  border-radius:999px;
  background:rgba(231,76,60,0.10);
  color:#e74c3c;
  font-weight:900;
  font-size:12px;
  border:1px solid rgba(231,76,60,0.25);
}
.ad-btn {
  margin-top: 12px;
  background:#e67e22;
  color:white;
  padding:12px 22px;
  border:none;
  border-radius:999px;
  font-weight:900;
  cursor:pointer;
}
</style>
""",
    unsafe_allow_html=True
)

# =========================================================
# Session State
# =========================================================
def ss_init():
    if "lang" not in st.session_state:
        st.session_state.lang = "ko"
    if "step" not in st.session_state:
        st.session_state.step = "input"  # input / test12 / test16 / result
    if "name" not in st.session_state:
        st.session_state.name = ""
    if "y" not in st.session_state:
        st.session_state.y = 2005
    if "m" not in st.session_state:
        st.session_state.m = 1
    if "d" not in st.session_state:
        st.session_state.d = 1
    if "mbti_mode" not in st.session_state:
        st.session_state.mbti_mode = "direct"  # direct / test12 / test16
    if "mbti" not in st.session_state:
        st.session_state.mbti = "ENFJ"

ss_init()

# =========================================================
# Language Packs (6)
# =========================================================
LANGS = [
    ("한국어", "ko"),
    ("English", "en"),
    ("中文", "zh"),
    ("日本語", "ja"),
    ("Русский", "ru"),
    ("हिन्दी", "hi"),
]

T = {
    "ko": {
        "lang_label": "언어 / Language",
        "title": "2026년 운세",
        "caption": "띠 + MBTI + 사주 + 오늘/내일 운세 (무료)",
        "input_title": "정보 입력",
        "name_ph": "이름 입력 (결과에 표시돼요)",
        "birth": "생년월일 입력",
        "year": "년", "month": "월", "day": "일",
        "mbti_mode": "MBTI 어떻게 할까?",
        "direct": "직접 입력",
        "test12": "간단 테스트 (12문항)",
        "test16": "상세 테스트 (16문항)",
        "choose_mbti": "MBTI 선택",
        "start_test": "테스트 시작",
        "view_result": "운세 보기!",
        "reset": "처음부터 다시 하기",
        "share_btn": "친구에게 결과 공유하기",
        "share_help": "모바일: 시스템 공유창 / PC: 복사",
        "share_title": "내 운세 결과",
        "share_fail": "공유가 지원되지 않아 텍스트를 복사했어요.",
        "copied": "복사 완료! 카톡/메시지에 붙여넣기 해주세요.",
        "tarot_btn": "오늘의 타로 카드 보기",
        "tarot_title": "오늘의 타로 카드",
        "top_combo": "최고 조합!",
        "zodiac_title": "띠 운세",
        "mbti_title": "MBTI 특징",
        "saju_title": "사주 한 마디",
        "today": "오늘 운세",
        "tomorrow": "내일 운세",
        "annual": "2026 전체 운세",
        "love": "연애운",
        "money": "재물운",
        "work": "일/학업운",
        "health": "건강운",
        "tip": "팁",
        "caution": "주의",
        "luck": "행운 포인트",
        "lucky_color": "럭키 컬러",
        "lucky_item": "럭키 아이템",
        "lucky_num": "럭키 넘버",
        "mbti_influence": "MBTI가 운세에 미치는 영향",
        "combo_advice": "띠 + MBTI 조합 조언",
        "influence_love": "연애에 미치는 영향",
        "influence_money": "재물에 미치는 영향",
        "influence_work": "일/학업에 미치는 영향",
        "influence_health": "건강에 미치는 영향",
        "test12_title": "MBTI – 12",
        "test12_desc": "제출하면 바로 결과로 넘어갑니다.",
        "test16_title": "MBTI – 16",
        "test16_desc": "각 축 4문항씩(총 16). 제출하면 결과로 넘어갑니다.",
        "err_year": "생년은 1900~2030년 사이로 입력해주세요!",
        "err_birth": "생년월일이 올바르지 않아요. 날짜를 다시 확인해 주세요!",
        "ad_badge": "광고",
        "ad_title": "정수기렌탈 궁금할 때?",
        "ad_desc": "다나눔렌탈 제휴카드 시 월 0원부터 + 설치당일 최대 현금50만원 페이백!",
        "ad_btn": "다나눔렌탈.com 바로가기",
        "ad_url": "https://www.다나눔렌탈.com",
        "ad_reserved": "AD (승인 후 이 위치에 광고가 표시됩니다)",
        "axis_e": "에너지 방식(E/I)",
        "axis_s": "정보 처리(S/N)",
        "axis_t": "판단 기준(T/F)",
        "axis_j": "생활 스타일(J/P)",
    },
    "en": {
        "lang_label": "Language",
        "title": "2026 Fortune",
        "caption": "Zodiac + MBTI + Today/Tomorrow (Free)",
        "input_title": "Input",
        "name_ph": "Name (optional)",
        "birth": "Birth date",
        "year": "Year", "month": "Month", "day": "Day",
        "mbti_mode": "MBTI method",
        "direct": "Direct input",
        "test12": "Quick test (12)",
        "test16": "Detailed test (16)",
        "choose_mbti": "Choose MBTI",
        "start_test": "Start test",
        "view_result": "View Fortune!",
        "reset": "Start over",
        "share_btn": "Share with friends",
        "share_help": "Mobile: share sheet / Desktop: copy",
        "share_title": "My fortune result",
        "share_fail": "Share not supported. Copied text instead.",
        "copied": "Copied! Paste in chat.",
        "tarot_btn": "Draw today's tarot",
        "tarot_title": "Today's Tarot",
        "top_combo": "Best Combo!",
        "zodiac_title": "Zodiac fortune",
        "mbti_title": "MBTI traits",
        "saju_title": "Fortune line",
        "today": "Today",
        "tomorrow": "Tomorrow",
        "annual": "2026 Overall",
        "love": "Love",
        "money": "Money",
        "work": "Work/Study",
        "health": "Health",
        "tip": "Tip",
        "caution": "Caution",
        "luck": "Lucky points",
        "lucky_color": "Lucky color",
        "lucky_item": "Lucky item",
        "lucky_num": "Lucky number",
        "mbti_influence": "How MBTI affects your fortune",
        "combo_advice": "Zodiac + MBTI combo advice",
        "influence_love": "Impact on love",
        "influence_money": "Impact on money",
        "influence_work": "Impact on work/study",
        "influence_health": "Impact on health",
        "test12_title": "MBTI – 12",
        "test12_desc": "Submit and you’ll jump to results.",
        "test16_title": "MBTI – 16",
        "test16_desc": "4 questions per axis (16 total). Submit to see results.",
        "err_year": "Birth year must be 1900–2030!",
        "err_birth": "Invalid birth date. Please check again!",
        "ad_reserved": "AD (Ads will appear here after approval)",
        "axis_e": "Energy (E/I)",
        "axis_s": "Perception (S/N)",
        "axis_t": "Decision (T/F)",
        "axis_j": "Lifestyle (J/P)",
    },
    "zh": {
        "lang_label": "语言",
        "title": "2026 运势",
        "caption": "生肖 + MBTI + 今日/明日（免费）",
        "input_title": "输入",
        "name_ph": "姓名（可选）",
        "birth": "生日",
        "year": "年", "month": "月", "day": "日",
        "mbti_mode": "MBTI 方式",
        "direct": "直接输入",
        "test12": "简易测试（12题）",
        "test16": "详细测试（16题）",
        "choose_mbti": "选择 MBTI",
        "start_test": "开始测试",
        "view_result": "查看运势！",
        "reset": "重新开始",
        "share_btn": "分享给朋友",
        "share_help": "手机：系统分享 / 电脑：复制",
        "share_title": "我的运势结果",
        "share_fail": "无法分享，已复制文本。",
        "copied": "已复制！可粘贴到聊天应用。",
        "tarot_btn": "抽取今日塔罗",
        "tarot_title": "今日塔罗",
        "top_combo": "最佳组合！",
        "zodiac_title": "生肖运势",
        "mbti_title": "MBTI 特点",
        "saju_title": "一句话",
        "today": "今日",
        "tomorrow": "明日",
        "annual": "2026 总运",
        "love": "恋爱运",
        "money": "财运",
        "work": "事业/学业",
        "health": "健康运",
        "tip": "建议",
        "caution": "注意",
        "luck": "幸运点",
        "lucky_color": "幸运色",
        "lucky_item": "幸运物",
        "lucky_num": "幸运数字",
        "mbti_influence": "MBTI 对运势的影响",
        "combo_advice": "生肖 + MBTI 组合建议",
        "influence_love": "对恋爱运的影响",
        "influence_money": "对财运的影响",
        "influence_work": "对事业/学业的影响",
        "influence_health": "对健康运的影响",
        "test12_title": "MBTI – 12",
        "test12_desc": "提交后将直接进入结果。",
        "test16_title": "MBTI – 16",
        "test16_desc": "每个维度4题（共16题）。提交后进入结果。",
        "err_year": "出生年份需在 1900–2030！",
        "err_birth": "生日不正确，请重新检查！",
        "ad_reserved": "AD（审核通过后此处显示广告）",
        "axis_e": "能量来源(E/I)",
        "axis_s": "信息处理(S/N)",
        "axis_t": "判断方式(T/F)",
        "axis_j": "生活风格(J/P)",
    },
    "ja": {
        "lang_label": "言語",
        "title": "2026 運勢",
        "caption": "干支 + MBTI + 今日/明日（無料）",
        "input_title": "入力",
        "name_ph": "名前（任意）",
        "birth": "生年月日",
        "year": "年", "month": "月", "day": "日",
        "mbti_mode": "MBTI の方法",
        "direct": "直接入力",
        "test12": "簡単テスト（12問）",
        "test16": "詳細テスト（16問）",
        "choose_mbti": "MBTI を選択",
        "start_test": "テスト開始",
        "view_result": "運勢を見る！",
        "reset": "最初から",
        "share_btn": "友だちに共有",
        "share_help": "スマホ：共有 / PC：コピー",
        "share_title": "運勢結果",
        "share_fail": "共有できないため、テキストをコピーしました。",
        "copied": "コピー完了！貼り付けてください。",
        "tarot_btn": "今日のタロット",
        "tarot_title": "今日のタロット",
        "top_combo": "最高の組み合わせ！",
        "zodiac_title": "干支運勢",
        "mbti_title": "MBTI 特徴",
        "saju_title": "一言",
        "today": "今日",
        "tomorrow": "明日",
        "annual": "2026 総合運",
        "love": "恋愛運",
        "money": "金運",
        "work": "仕事/学業",
        "health": "健康運",
        "tip": "ヒント",
        "caution": "注意",
        "luck": "ラッキーポイント",
        "lucky_color": "ラッキーカラー",
        "lucky_item": "ラッキーアイテム",
        "lucky_num": "ラッキーナンバー",
        "mbti_influence": "MBTI が運勢に与える影響",
        "combo_advice": "干支 + MBTI 組み合わせアドバイス",
        "influence_love": "恋愛への影響",
        "influence_money": "金運への影響",
        "influence_work": "仕事/学業への影響",
        "influence_health": "健康への影響",
        "test12_title": "MBTI – 12",
        "test12_desc": "送信すると結果へ移動します。",
        "test16_title": "MBTI – 16",
        "test16_desc": "各軸4問（合計16）。送信すると結果へ移動します。",
        "err_year": "1900〜2030年の範囲で入力してください！",
        "err_birth": "生年月日が正しくありません。確認してください！",
        "ad_reserved": "AD（承認後ここに広告が表示されます）",
        "axis_e": "エネルギー(E/I)",
        "axis_s": "認知(S/N)",
        "axis_t": "判断(T/F)",
        "axis_j": "スタイル(J/P)",
    },
    "ru": {
        "lang_label": "Язык",
        "title": "Удача 2026",
        "caption": "Зодиак + MBTI + Сегодня/Завтра (бесплатно)",
        "input_title": "Ввод",
        "name_ph": "Имя (необязательно)",
        "birth": "Дата рождения",
        "year": "Год", "month": "Месяц", "day": "День",
        "mbti_mode": "Способ MBTI",
        "direct": "Ввести вручную",
        "test12": "Быстрый тест (12)",
        "test16": "Подробный тест (16)",
        "choose_mbti": "Выберите MBTI",
        "start_test": "Начать тест",
        "view_result": "Показать результат!",
        "reset": "Сначала",
        "share_btn": "Поделиться",
        "share_help": "Телефон: поделиться / ПК: копировать",
        "share_title": "Мой результат",
        "share_fail": "Поделиться нельзя — скопировали текст.",
        "copied": "Скопировано! Вставьте в чат.",
        "tarot_btn": "Таро дня",
        "tarot_title": "Таро дня",
        "top_combo": "Лучшее сочетание!",
        "zodiac_title": "Зодиак",
        "mbti_title": "MBTI",
        "saju_title": "Фраза",
        "today": "Сегодня",
        "tomorrow": "Завтра",
        "annual": "Итог 2026",
        "love": "Любовь",
        "money": "Деньги",
        "work": "Работа/Учёба",
        "health": "Здоровье",
        "tip": "Совет",
        "caution": "Осторожно",
        "luck": "Счастливые пункты",
        "lucky_color": "Цвет",
        "lucky_item": "Талисман",
        "lucky_num": "Число",
        "mbti_influence": "Как MBTI влияет на удачу",
        "combo_advice": "Совет по сочетанию",
        "influence_love": "Влияние на любовь",
        "influence_money": "Влияние на деньги",
        "influence_work": "Влияние на работу/учёбу",
        "influence_health": "Влияние на здоровье",
        "test12_title": "MBTI – 12",
        "test12_desc": "Отправьте — и перейдёте к результату.",
        "test16_title": "MBTI – 16",
        "test16_desc": "4 вопроса на ось (всего 16). Отправьте для результата.",
        "err_year": "Год рождения должен быть 1900–2030!",
        "err_birth": "Неверная дата рождения. Проверьте!",
        "ad_reserved": "AD (после одобрения здесь будет реклама)",
        "axis_e": "Энергия(E/I)",
        "axis_s": "Восприятие(S/N)",
        "axis_t": "Решения(T/F)",
        "axis_j": "Стиль(J/P)",
    },
    "hi": {
        "lang_label": "भाषा",
        "title": "2026 भाग्य",
        "caption": "राशि + MBTI + आज/कल (मुफ़्त)",
        "input_title": "इनपुट",
        "name_ph": "नाम (वैकल्पिक)",
        "birth": "जन्मतिथि",
        "year": "वर्ष", "month": "महीना", "day": "दिन",
        "mbti_mode": "MBTI तरीका",
        "direct": "सीधा इनपुट",
        "test12": "त्वरित टेस्ट (12)",
        "test16": "विस्तृत टेस्ट (16)",
        "choose_mbti": "MBTI चुनें",
        "start_test": "टेस्ट शुरू",
        "view_result": "परिणाम देखें!",
        "reset": "फिर से शुरू",
        "share_btn": "दोस्तों को शेयर करें",
        "share_help": "मोबाइल: शेयर / PC: कॉपी",
        "share_title": "मेरा परिणाम",
        "share_fail": "यहाँ शेयर सपोर्ट नहीं है, टेक्स्ट कॉपी किया।",
        "copied": "कॉपी हो गया! चैट में पेस्ट करें।",
        "tarot_btn": "आज का टैरो",
        "tarot_title": "आज का टैरो",
        "top_combo": "सबसे अच्छा कॉम्बो!",
        "zodiac_title": "राशि",
        "mbti_title": "MBTI",
        "saju_title": "एक लाइन",
        "today": "आज",
        "tomorrow": "कल",
        "annual": "2026 कुल",
        "love": "प्रेम",
        "money": "धन",
        "work": "कार्य/पढ़ाई",
        "health": "स्वास्थ्य",
        "tip": "टिप",
        "caution": "सावधानी",
        "luck": "लकी पॉइंट्स",
        "lucky_color": "रंग",
        "lucky_item": "आइटम",
        "lucky_num": "नंबर",
        "mbti_influence": "MBTI का असर",
        "combo_advice": "कॉम्बो सलाह",
        "influence_love": "प्रेम पर असर",
        "influence_money": "धन पर असर",
        "influence_work": "काम/पढ़ाई पर असर",
        "influence_health": "स्वास्थ्य पर असर",
        "test12_title": "MBTI – 12",
        "test12_desc": "सबमिट करते ही परिणाम दिखेगा।",
        "test16_title": "MBTI – 16",
        "test16_desc": "प्रति आयाम 4 प्रश्न (कुल 16)। सबमिट पर परिणाम।",
        "err_year": "वर्ष 1900–2030 के बीच होना चाहिए!",
        "err_birth": "जन्मतिथि गलत है। कृपया जाँचें!",
        "ad_reserved": "AD (स्वीकृति के बाद यहाँ विज्ञापन दिखेगा)",
        "axis_e": "ऊर्जा(E/I)",
        "axis_s": "जानकारी(S/N)",
        "axis_t": "निर्णय(T/F)",
        "axis_j": "स्टाइल(J/P)",
    },
}

# =========================================================
# Data
# =========================================================
MBTI_TYPES = [
    "INTJ","INTP","ENTJ","ENTP",
    "INFJ","INFP","ENFJ","ENFP",
    "ISTJ","ISFJ","ESTJ","ESFJ",
    "ISTP","ISFP","ESTP","ESFP"
]

ZODIAC_KO = ["쥐띠","소띠","호랑이띠","토끼띠","용띠","뱀띠","말띠","양띠","원숭이띠","닭띠","개띠","돼지띠"]
ZODIAC_EN = ["Rat","Ox","Tiger","Rabbit","Dragon","Snake","Horse","Goat","Monkey","Rooster","Dog","Pig"]

ZODIAC_DESC = {
    "ko": {
        "쥐띠":"민첩한 판단이 빛나요. 작은 기회를 크게 키우는 해!",
        "소띠":"꾸준함이 성과로 돌아옵니다. 안정 속에서 강해져요.",
        "호랑이띠":"승부수 타이밍! 리더십과 추진력이 폭발합니다.",
        "토끼띠":"균형이 핵심! 과감함보단 신중함이 유리합니다.",
        "용띠":"운기 상승! 자신감이 기회를 끌어당겨요.",
        "뱀띠":"직감이 돈이 됩니다. 정보/타이밍에 강해요.",
        "말띠":"속도감이 장점! 다만 과열/과로는 주의.",
        "양띠":"관계운이 강합니다. 협업이 수익으로 이어져요.",
        "원숭이띠":"아이디어가 돈이 되는 해! 기획/콘텐츠에 강점.",
        "닭띠":"노력 결실! 평가/승진/인정운이 좋아요.",
        "개띠":"귀인운! 사람을 통해 길이 열립니다.",
        "돼지띠":"여유 속에 복이 들어옵니다. 꾸준히 쌓으면 대박!",
    },
    "en": {
        "Rat":"Quick judgment shines. Small chances become big wins.",
        "Ox":"Consistency pays off with stable growth.",
        "Tiger":"Bold timing! Leadership and momentum surge.",
        "Rabbit":"Balance is key. Careful moves win.",
        "Dragon":"Fortune rises. Confidence attracts opportunities.",
        "Snake":"Intuition turns into profit. Timing matters.",
        "Horse":"Speed is power—avoid burnout.",
        "Goat":"Relationships bring gains. Collaboration wins.",
        "Monkey":"Ideas become money. Great for planning/content.",
        "Rooster":"Effort rewarded—recognition and promotion.",
        "Dog":"Helpful people appear—network opens doors.",
        "Pig":"Luck grows in calm—accumulate steadily.",
    },
    "zh": {
        "Rat":"判断敏捷，小机会能放大成大收获。",
        "Ox":"稳扎稳打，长期坚持会带来成果。",
        "Tiger":"敢冲敢拼，领导力与行动力增强。",
        "Rabbit":"关键在平衡，谨慎更有利。",
        "Dragon":"运势上升，自信会吸引机会。",
        "Snake":"直觉变现，信息与时机很重要。",
        "Horse":"速度是优势，但要避免过劳。",
        "Goat":"人际运强，合作带来收益。",
        "Monkey":"点子变钱，策划/内容运佳。",
        "Rooster":"努力见回报，认可与晋升机会多。",
        "Dog":"贵人运旺，人脉带来突破。",
        "Pig":"越放松越顺，稳稳累积更大吉。",
    },
    "ja": {
        "Rat":"判断が冴える年。小さなチャンスが大きく育つ。",
        "Ox":"コツコツ型が勝つ。安定の中で強くなる。",
        "Tiger":"勝負のタイミング！推進力とリーダー運。",
        "Rabbit":"バランス重視。慎重さが有利。",
        "Dragon":"運気上昇。自信がチャンスを呼ぶ。",
        "Snake":"直感が利益に。情報とタイミングが鍵。",
        "Horse":"スピードが武器。過労だけ注意。",
        "Goat":"人間関係運◎。協力が収益に。",
        "Monkey":"アイデアが武器。企画/コンテンツ運◎。",
        "Rooster":"努力が実る。評価・昇進の流れ。",
        "Dog":"味方が増える年。人から道が開く。",
        "Pig":"ゆとりが福を呼ぶ。積み上げで大吉。",
    },
    "ru": {
        "Rat":"Быстрое мышление приносит шанс — малое станет большим.",
        "Ox":"Постоянство даёт результат. Стабильный рост.",
        "Tiger":"Время решительных шагов — лидерство и импульс.",
        "Rabbit":"Баланс важнее риска. Осторожность выигрышнее.",
        "Dragon":"Удача растёт — уверенность притягивает возможности.",
        "Snake":"Интуиция приносит прибыль — важны информация и тайминг.",
        "Horse":"Скорость — плюс, но берегите силы.",
        "Goat":"Сильна удача в отношениях — сотрудничество выгодно.",
        "Monkey":"Идеи монетизируются — планирование/контент в плюс.",
        "Rooster":"Награда за труд — признание и рост.",
        "Dog":"Люди помогают — связи открывают двери.",
        "Pig":"Спокойствие усиливает удачу — копите постепенно.",
    },
    "hi": {
        "Rat":"तेज़ निर्णय से लाभ—छोटे मौके बड़े बनेंगे।",
        "Ox":"लगातार मेहनत का फल—स्थिर प्रगति।",
        "Tiger":"साहसी समय—लीडरशिप और गति बढ़ेगी।",
        "Rabbit":"संतुलन ज़रूरी—सावधानी फायदेमंद।",
        "Dragon":"भाग्य बढ़ेगा—आत्मविश्वास अवसर खींचेगा।",
        "Snake":"अंतर्ज्ञान से लाभ—जानकारी/टाइमिंग अहम।",
        "Horse":"स्पीड आपकी ताकत—ओवरवर्क से बचें।",
        "Goat":"रिश्तों से फायदा—सहयोग से कमाई।",
        "Monkey":"आइडिया से पैसा—प्लानिंग/कंटेंट मजबूत।",
        "Rooster":"मेहनत का फल—पहचान/प्रमोशन के संकेत।",
        "Dog":"सहयोगी मिलेंगे—नेटवर्क से रास्ता खुलेगा।",
        "Pig":"शांत रहो तो भाग्य बढ़े—धीरे-धीरे बड़ा लाभ।",
    }
}

MBTI_DESC = {
    "ko": {
        "INTJ":"전략가 · 큰그림/계획","INTP":"분석가 · 논리/아이디어","ENTJ":"리더 · 추진/결단","ENTP":"기획자 · 전환/토론",
        "INFJ":"통찰가 · 의미/사람","INFP":"이상가 · 가치/감성","ENFJ":"조율가 · 공감/리딩","ENFP":"촉진자 · 에너지/영감",
        "ISTJ":"관리자 · 원칙/정리","ISFJ":"수호자 · 배려/책임","ESTJ":"운영자 · 현실/성과","ESFJ":"친화형 · 관계/분위기",
        "ISTP":"장인 · 문제해결","ISFP":"감성형 · 미감/균형","ESTP":"승부사 · 실행/순간판단","ESFP":"무드메이커 · 표현/즐거움",
    },
    "en": {
        "INTJ":"Strategist · planning & big picture","INTP":"Analyst · logic & ideas","ENTJ":"Commander · decisive leadership","ENTP":"Innovator · pivot & debate",
        "INFJ":"Insightful · meaning & people","INFP":"Idealist · values & empathy","ENFJ":"Coordinator · guidance & care","ENFP":"Spark · energy & inspiration",
        "ISTJ":"Organizer · rules & structure","ISFJ":"Defender · responsibility & warmth","ESTJ":"Operator · execution & results","ESFJ":"Connector · harmony & people",
        "ISTP":"Craft · fixes & tools","ISFP":"Artist · aesthetics & balance","ESTP":"Doer · action & quick calls","ESFP":"Entertainer · vibe & expression",
    },
    "zh": {
        "INTJ":"战略家 · 大局/规划","INTP":"分析者 · 逻辑/点子","ENTJ":"指挥者 · 推进/决断","ENTP":"创意者 · 转向/辩论",
        "INFJ":"洞察者 · 意义/人心","INFP":"理想者 · 价值/共情","ENFJ":"协调者 · 共感/带领","ENFP":"激发者 · 能量/灵感",
        "ISTJ":"管理者 · 规则/整理","ISFJ":"守护者 · 体贴/责任","ESTJ":"执行者 · 现实/成果","ESFJ":"亲和者 · 关系/氛围",
        "ISTP":"匠人 · 解决问题","ISFP":"感性者 · 审美/平衡","ESTP":"行动派 · 执行/快决","ESFP":"气氛组 · 表达/快乐",
    },
    "ja": {
        "INTJ":"戦略家 · 計画/大局","INTP":"分析家 · 論理/アイデア","ENTJ":"指揮官 · 推進/決断","ENTP":"発明家 · 転換/議論",
        "INFJ":"洞察家 · 意味/人","INFP":"理想家 · 価値/共感","ENFJ":"調整役 · 共感/リード","ENFP":"促進役 · エネルギー/発想",
        "ISTJ":"管理者 · ルール/整理","ISFJ":"守護者 · 思いやり/責任","ESTJ":"運営者 · 現実/成果","ESFJ":"協調型 · 関係/雰囲気",
        "ISTP":"職人 · 問題解決","ISFP":"感性型 · 美意識/バランス","ESTP":"勝負師 · 実行/即断","ESFP":"ムードメーカー · 表現/楽しさ",
    },
    "ru": {
        "INTJ":"Стратег · план и масштаб","INTP":"Аналитик · логика и идеи","ENTJ":"Командир · решительность","ENTP":"Новатор · поворот и дебаты",
        "INFJ":"Инсайт · смысл и люди","INFP":"Идеалист · ценности и эмпатия","ENFJ":"Координатор · забота и лидерство","ENFP":"Искра · энергия и вдохновение",
        "ISTJ":"Организатор · порядок и правила","ISFJ":"Защитник · ответственность","ESTJ":"Оператор · результат","ESFJ":"Связующий · гармония и люди",
        "ISTP":"Мастер · починка/решения","ISFP":"Художник · эстетика/баланс","ESTP":"Деятель · действие/быстро","ESFP":"Шоумен · эмоции/веселье",
    },
    "hi": {
        "INTJ":"रणनीतिकार · योजना/बड़ा चित्र","INTP":"विश्लेषक · लॉजिक/आइडिया","ENTJ":"नेता · निर्णायक/प्रगति","ENTP":"नवोन्मेषक · बदलाव/बहस",
        "INFJ":"अंतर्दृष्टि · अर्थ/लोग","INFP":"आदर्शवादी · मूल्य/सहानुभूति","ENFJ":"समन्वयक · मार्गदर्शन/देखभाल","ENFP":"ऊर्जा · प्रेरणा/उत्साह",
        "ISTJ":"व्यवस्थापक · नियम/संरचना","ISFJ":"रक्षक · जिम्मेदारी/देखभाल","ESTJ":"ऑपरेटर · परिणाम/यथार्थ","ESFJ":"कनेक्टर · रिश्ते/सद्भाव",
        "ISTP":"कारीगर · समस्या-समाधान","ISFP":"कलाकार · सौंदर्य/संतुलन","ESTP":"एक्शन · जल्दी निर्णय","ESFP":"मूड · अभिव्यक्ति/मज़ा",
    }
}

FORTUNE = {
    "ko": {
        "saju_line": "오행 균형 → 무리하지 않으면 전반적으로 대길!",
        "today": [
            "정리하면 운이 열립니다. 미뤄둔 것 1개만 끝내도 흐름이 바뀌어요.",
            "말 한마디가 기회를 부릅니다. 먼저 연락하면 관계운이 상승해요.",
            "결정은 빠르게, 실행은 차분하게. 과속만 피하면 대길!",
            "집중력 최고. 30분 몰입이 하루를 바꿔요.",
            "작은 친절이 큰 인연으로 돌아옵니다.",
        ],
        "tomorrow": [
            "사람 운이 강해요. 약속/미팅에서 힌트가 나옵니다.",
            "새로운 정보가 들어옵니다. 비교 후 결정하면 유리해요.",
            "컨디션이 성과를 좌우합니다. 수면을 투자하세요.",
            "우선순위만 잡으면 술술 풀립니다.",
            "작은 소비가 큰 만족을 줍니다. 기분전환 OK!",
        ],
        "annual": [
            "올해는 ‘성장 곡선’. 작은 개선이 큰 성과로 이어져요.",
            "기회는 사람을 통해 들어옵니다. 관계가 곧 자산!",
            "정리/선택이 운을 엽니다. 버릴 것을 버리면 빨라져요.",
            "꾸준함이 대박을 만듭니다. 한 번 더가 승부!",
            "방향만 잃지 않으면 연말에 확실한 결과가 남습니다.",
        ],
        "love": ["호감 신호가 보여요. 먼저 안부 한 번!", "대화의 온도가 중요해요. 결론을 급하게 내지 마세요."],
        "money": ["새는 돈 막기가 이득! 구독/고정비 점검 추천.", "충동구매만 줄이면 재물운이 상승!"],
        "work": ["협업운 좋음. 공유 한 번 더 하면 속도가 붙어요.", "기본기로 승부하면 통합니다."],
        "health": ["카페인 과다만 조심하면 컨디션이 좋아져요.", "가벼운 산책이 기운을 끌어올립니다."],
        "tips": ["책상 3분 정리", "아침 10분 산책", "지출 1줄 기록", "오늘은 하나만 끝내기"],
        "cautions": ["충동구매 주의", "과로/야식 줄이기", "감정 폭발 주의"],
        "colors": ["골드","레드","블루","그린","퍼플","화이트","블랙"],
        "items": ["황금 액세서리","빨간 지갑","파란 키링","초록 식물","보라색 펜","심플한 시계"],
    },
    "en": {
        "saju_line": "Balanced elements → avoid overdoing and things go well.",
        "today": [
            "Cleanup opens your luck—finish one pending task.",
            "A single message can open doors—reach out first.",
            "Decide fast, execute calmly—avoid rushing.",
            "Great focus today—30 minutes of deep work changes everything.",
            "Small kindness returns as a big connection.",
        ],
        "tomorrow": [
            "People luck is strong—meetings bring clues.",
            "New info arrives—compare before deciding.",
            "Health affects results—invest in sleep.",
            "Once priorities are clear, everything flows.",
            "Small spending brings big joy—refresh is ok.",
        ],
        "annual": [
            "Small upgrades compound into big results.",
            "Opportunities come through people—relationships become assets.",
            "Declutter and your luck accelerates.",
            "Consistency wins—one more step becomes the breakthrough.",
            "Keep direction and you’ll see results near year-end.",
        ],
        "love": ["Send a light check-in first.", "Don’t rush conclusions—keep it warm."],
        "money": ["Stop leaks (subscriptions/fixed costs) first.", "Avoid impulse buys and money luck rises."],
        "work": ["Share one more update—things speed up.", "Win with fundamentals—your method works."],
        "health": ["Avoid too much caffeine and you’ll feel better.", "Light cardio boosts mood and luck."],
        "tips": ["Finish one thing", "10-min walk", "Write one expense line", "Reach out first"],
        "cautions": ["Avoid impulse shopping", "Reduce overwork", "Watch emotional spikes"],
        "colors": ["Gold","Red","Blue","Green","Purple","White","Black"],
        "items": ["Golden accessory","Red wallet","Blue keyring","Green plant","Purple pen","Minimal watch"],
    },
    "zh": {
        "saju_line": "五行均衡 → 不要过度用力，整体更顺。",
        "today": ["整理会打开好运：先完成一件拖延的事。", "主动联系更顺利。", "别急躁就大吉。"],
        "tomorrow": ["人际运强：约会/会议里会出现关键提示。", "比较后再决定更划算。", "把睡眠当投资。"],
        "annual": ["复利成长的一年：小改进带来大成果。", "机会来自人：关系就是资产。", "整理与取舍让好运加速。"],
        "love": ["先发个问候。", "别急着下结论，保持温度。"],
        "money": ["先堵住漏财：订阅/固定支出检查。", "减少冲动消费，财运上升。"],
        "work": ["协作运佳：多同步一次更快。", "用基本功稳扎稳打最有效。"],
        "health": ["注意咖啡因过量。", "轻松散步能提升能量。"],
        "tips": ["桌面整理3分钟", "早晨散步10分钟", "记一行支出"],
        "cautions": ["冲动购物", "熬夜/过劳", "情绪爆发"],
        "colors": ["金色","红色","蓝色","绿色","紫色","白色","黑色"],
        "items": ["金色饰品","红色钱包","蓝色挂件","绿植","紫色笔","简约手表"],
    },
    "ja": {
        "saju_line": "五行バランス → 無理しなければ全体運◎。",
        "today": ["片付けが運を開く。後回しを1つ終える。", "先に連絡で対人運UP。", "焦り注意、落ち着いて大吉。"],
        "tomorrow": ["人運が強い。約束にヒント。", "比較して決めると◎。", "睡眠に投資を。"],
        "annual": ["小さな改善が大きな成果へ。", "チャンスは人から来る。", "整理と選択が運を開く。"],
        "love": ["まず一言。", "結論を急がず温度感を大切に。"],
        "money": ["サブスク/固定費の見直し。", "衝動買いを抑えると金運UP。"],
        "work": ["共有をもう一回で加速。", "基礎で勝負が一番強い。"],
        "health": ["カフェイン過多に注意。", "軽い散歩が気を上げる。"],
        "tips": ["机を3分整理", "朝10分散歩", "支出を1行記録"],
        "cautions": ["衝動買い", "過労/夜更かし", "感情の爆発"],
        "colors": ["ゴールド","レッド","ブルー","グリーン","パープル","ホワイト","ブラック"],
        "items": ["金のアクセ","赤い財布","青いキーホルダー","観葉植物","紫のペン","シンプル時計"],
    },
    "ru": {
        "saju_line": "Баланс элементов → не перегружай себя, и всё сложится.",
        "today": ["Порядок открывает удачу: закройте одну задачу.", "Напишите первым — это даст шанс.", "Решайте быстро, действуйте спокойно."],
        "tomorrow": ["Встреча даст подсказку.", "Сравните перед выбором.", "Вложитесь в сон."],
        "annual": ["Малые улучшения дают большой эффект.", "Возможности приходят через людей.", "Расхламление ускоряет удачу."],
        "love": ["Короткое сообщение — лучший старт.", "Не торопите выводы, держите тепло."],
        "money": ["Проверьте подписки и расходы.", "Меньше импульсивных покупок — больше удачи."],
        "work": ["Ещё одно обновление команде — быстрее пойдёт.", "Ставка на базу — сильнее всего."],
        "health": ["Осторожно с кофеином.", "Лёгкая прогулка поднимет энергию."],
        "tips": ["3 минуты на порядок", "10 минут прогулки", "Запишите 1 расход"],
        "cautions": ["Импульсивные покупки", "Переутомление", "Эмоциональные всплески"],
        "colors": ["Золото","Красный","Синий","Зелёный","Фиолетовый","Белый","Чёрный"],
        "items": ["Золотой аксессуар","Красный кошелёк","Синий брелок","Зелёное растение","Фиолетовая ручка","Часы"],
    },
    "hi": {
        "saju_line": "तत्व संतुलित → ज़्यादा दबाव न लें, सब बेहतर होगा।",
        "today": ["सफाई से भाग्य खुलता है: एक काम पूरा करें।", "पहले संपर्क करें—मौका बढ़ेगा।", "जल्दबाज़ी से बचें, सब अच्छा होगा।"],
        "tomorrow": ["मुलाकात में संकेत मिलेगा।", "तुलना करके निर्णय लें।", "नींद में निवेश करें।"],
        "annual": ["छोटे सुधार बड़ा परिणाम देंगे।", "मौके लोगों से आते हैं।", "अनावश्यक चीज़ें हटाएँ।"],
        "love": ["हल्का सा संदेश भेजें।", "जल्दी निष्कर्ष न निकालें।"],
        "money": ["सब्सक्रिप्शन/फिक्स्ड खर्च देखें।", "इम्पल्स खरीद कम करें।"],
        "work": ["एक बार और साझा करें—स्पीड बढ़ेगी।", "बेसिक्स सबसे मजबूत।"],
        "health": ["कैफीन कम रखें।", "हल्की वॉक मदद करेगी।"],
        "tips": ["3 मिनट डेस्क साफ", "10 मिनट वॉक", "1 लाइन खर्च लिखें"],
        "cautions": ["इम्पल्स खरीद", "ओवरवर्क", "भावनात्मक उछाल"],
        "colors": ["गोल्ड","रेड","ब्लू","ग्रीन","पर्पल","व्हाइट","ब्लैक"],
        "items": ["गोल्ड एक्सेसरी","लाल वॉलेट","नीला की-रिंग","हरा पौधा","पर्पल पेन","घड़ी"],
    },
}

TAROT = {
    "The Fool": {"ko":"새로운 시작, 모험, 순수한 믿음","en":"New beginnings, adventure, innocence","zh":"新的开始、冒险、纯粹的信念","ja":"新しい始まり、冒険、純粋な信頼","ru":"Новые начала, приключение, искренность","hi":"नई शुरुआत, साहसिकता, सरल विश्वास"},
    "The Magician": {"ko":"창조력, 능력 발휘, 집중","en":"Skill, manifestation, focus","zh":"创造力、能力发挥、专注","ja":"創造力、才能の発揮、集中","ru":"Навык, проявление силы, фокус","hi":"कौशल, क्षमता, एकाग्रता"},
    "The High Priestess": {"ko":"직감, 내면의 목소리","en":"Intuition, inner voice","zh":"直觉、内在声音","ja":"直感、内なる声","ru":"Интуиция, внутренний голос","hi":"अंतर्ज्ञान, भीतर की आवाज़"},
    "The Sun": {"ko":"행복, 성공, 긍정 에너지","en":"Joy, success, positivity","zh":"幸福、成功、正能量","ja":"幸福、成功、ポジティブ","ru":"Радость, успех, позитив","hi":"खुशी, सफलता, सकारात्मकता"},
    "Wheel of Fortune": {"ko":"변화, 운, 사이클","en":"Change, luck, cycles","zh":"变化、运气、周期","ja":"変化、運、サイクル","ru":"Перемены, удача, циклы","hi":"परिवर्तन, भाग्य, चक्र"},
}

APP_URL = "https://my-fortune.streamlit.app"

# =========================================================
# Helpers
# =========================================================
def stable_seed(*parts) -> int:
    s = "|".join(map(str, parts))
    h = hashlib.sha256(s.encode("utf-8")).hexdigest()
    return int(h[:12], 16)

def validate_birth(y, m, d) -> bool:
    try:
        date(int(y), int(m), int(d))
        return True
    except Exception:
        return False

def get_zodiac(year: int, lang: str):
    if not (1900 <= year <= 2030):
        return None
    idx = (year - 4) % 12
    return ZODIAC_KO[idx] if lang == "ko" else ZODIAC_EN[idx]

def render_reserved_ad(text):
    st.markdown(
        f"""
        <div class="ad-reserved">
          <div style="font-weight:900; font-size:12px; letter-spacing:0.08em; opacity:0.8;">AD</div>
          <div style="opacity:0.78; font-size:13px; margin-top:6px;">{text}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_korean_ad(t):
    st.markdown(
        f"""
        <div class="ad-ko">
          <div class="badge">{t["ad_badge"]}</div>
          <h3 style="color:#d35400; margin:10px 0 6px 0;">{t["ad_title"]}</h3>
          <div style="font-size:14px; line-height:1.6; color:#222;">{t["ad_desc"]}</div>
          <a href="{t["ad_url"]}" target="_blank" style="text-decoration:none;">
            <button class="ad-btn">{t["ad_btn"]}</button>
          </a>
        </div>
        """,
        unsafe_allow_html=True
    )

def share_component(t, share_text: str):
    payload = (
        share_text.replace("\\", "\\\\")
        .replace("`", "\\`")
        .replace("${", "\\${")
    )
    components.html(
        f"""
        <div style="text-align:center; margin: 14px 0 6px 0;">
          <button id="shareBtn"
            style="background:#6d28d9; color:white; padding:14px 18px; border:none; border-radius:999px;
                   font-size:16px; font-weight:900; box-shadow:0 10px 24px rgba(109,40,217,0.28);
                   cursor:pointer; width:100%;">
            {t["share_btn"]}
          </button>
          <div style="margin-top:8px; font-size:13px; opacity:0.75;">{t["share_help"]}</div>
        </div>

        <script>
          const text = `{payload}`;
          const btn = document.getElementById("shareBtn");

          async function doShare() {{
            try {{
              if (navigator.share) {{
                await navigator.share({{
                  title: "{t['share_title']}",
                  text: text,
                  url: "{APP_URL}"
                }});
              }} else {{
                await navigator.clipboard.writeText(text);
                alert("{t['share_fail']}\\n{t['copied']}");
              }}
            }} catch(e) {{
              try {{
                await navigator.clipboard.writeText(text);
                alert("{t['share_fail']}\\n{t['copied']}");
              }} catch(_) {{
                alert("{t['share_fail']}");
              }}
            }}
          }}

          btn.addEventListener("click", doShare);
        </script>
        """,
        height=120
    )

def fortune_bank(lang: str):
    return FORTUNE.get(lang, FORTUNE["en"])

# =========================================================
# MBTI Influence & Combo Advice (6 languages)
# =========================================================
INFL = {
    "ko": {
        "E": {
            "love": "표현과 추진력이 강해요. 연락/만남을 먼저 잡으면 연애운이 빨리 열립니다.",
            "money": "기회가 ‘사람’에서 옵니다. 소개·추천·네트워킹이 수입으로 연결돼요.",
            "work": "협업/발표에서 빛나요. 다만 말이 앞서면 오해가 생길 수 있어요.",
            "health": "일정이 많아 과로 위험. 휴식도 약속처럼 ‘예약’하세요.",
        },
        "I": {
            "love": "깊이 있는 관계에 강해요. 천천히 신뢰를 쌓는 방식이 유리합니다.",
            "money": "분석/선택으로 새는 돈을 잘 막아요. 큰 한 방보다 ‘꾸준한 관리’가 답.",
            "work": "몰입력이 강점. 혼자 집중할 시간 확보가 성과를 키웁니다.",
            "health": "스트레스를 혼자 삼키기 쉬워요. 산책/호흡 등 작은 루틴이 도움.",
        },
        "S": {
            "love": "현실적인 배려가 매력. 약속/시간/작은 행동이 신뢰를 만듭니다.",
            "money": "지출 통제에 강해요. ‘고정비 정리’만 해도 재물운이 확 올라가요.",
            "work": "실행력/정확도가 무기. 체크리스트가 성공 확률을 올립니다.",
            "health": "몸의 신호를 잘 캐치해요. 수면/식단만 정리해도 회복 빨라요.",
        },
        "N": {
            "love": "설렘/아이디어가 관계를 살립니다. 다만 말보다 ‘확인’이 필요할 때가 있어요.",
            "money": "아이디어로 돈을 벌 수 있어요. 단, 계획 없이 지르면 지출이 커질 수 있어요.",
            "work": "기획/전략에 강함. 큰 그림을 ‘작은 실행’으로 쪼개면 대박.",
            "health": "생각이 많아 피로 누적. 짧은 운동/스트레칭이 효과적입니다.",
        },
        "T": {
            "love": "해결 중심이라 든든해요. 다만 감정 공감 한 마디가 연애운을 더 키웁니다.",
            "money": "합리적 소비에 강함. 손익/가성비 기준을 세우면 돈이 모입니다.",
            "work": "결단/최적화에 강해요. 숫자와 지표를 잡으면 승진운이 붙습니다.",
            "health": "무리해도 버티는 편. ‘쉬어야 오래 간다’를 기억하세요.",
        },
        "F": {
            "love": "공감/배려가 매력. 작은 말 한마디가 관계를 확 바꿉니다.",
            "money": "사람에 쓰는 돈이 많아질 수 있어요. 예산만 정하면 흐름이 좋아요.",
            "work": "분위기/팀워크를 살립니다. 다만 부탁을 거절 못하면 과부하!",
            "health": "감정 기복이 컨디션에 영향. 수면/햇빛/산책이 안정에 도움.",
        },
        "J": {
            "love": "확실한 약속/계획이 안정감을 줍니다. ‘선명한 표현’이 호감 포인트.",
            "money": "예산/저축 루틴이 강점. 자동이체만 세팅해도 운이 붙어요.",
            "work": "마감/관리 능력 최고. 책임감이 인정으로 이어집니다.",
            "health": "완벽주의로 긴장될 수 있어요. 휴식도 계획에 넣어주세요.",
        },
        "P": {
            "love": "자유롭고 재미있는 매력이 있어요. 다만 중요한 날은 약속을 ‘확정’하세요.",
            "money": "기분 소비 주의. ‘소비 전 10분 대기’ 규칙이 효과적입니다.",
            "work": "순발력/현장 대응이 무기. 단, 마감 관리만 보완하면 급상승!",
            "health": "생활 리듬이 흔들리기 쉬워요. 취침 시간만 고정해도 좋아집니다.",
        },
        "combo": {
            "growth": "올해 테마는 성장. {zodiac}의 흐름을 {mbti}의 장점(강점)으로 ‘꾸준히’ 끌고 가면 결과가 크게 옵니다.",
            "love": "연애는 ‘표현 ↔ 배려’ 균형이 핵심. {mbti} 스타일대로 하되 상대의 속도를 한 번 더 맞춰주세요.",
            "money": "재물은 ‘새는 돈 차단 + 기회 포착’이 답. {zodiac}의 기회운이 오면 {mbti} 방식으로 실행을 한 단계만 더 구체화하세요.",
            "work": "일/학업은 ‘작은 실행’이 승부. 오늘 해야 할 1개를 끝내면 전체 흐름이 열립니다.",
        }
    },
    "en": {
        "E": {
            "love": "You thrive on expression and momentum. Initiate plans and your love luck opens faster.",
            "money": "Opportunities come through people. Intros/referrals can turn into income.",
            "work": "You shine in collaboration and presenting. Watch for misunderstandings from rushing words.",
            "health": "Busy schedules risk burnout. Treat rest like an appointment.",
        },
        "I": {
            "love": "You’re strong at deep bonds. Slow trust-building works in your favor.",
            "money": "You block money leaks well. Steady management beats risky bets.",
            "work": "Deep focus is your edge. Protect quiet time to multiply results.",
            "health": "You may bottle stress. Small routines (walk/breathing) help a lot.",
        },
        "S": {
            "love": "Practical care is attractive. Small actions build big trust.",
            "money": "You’re good at control. Cutting fixed costs boosts money luck quickly.",
            "work": "Accuracy and execution are your weapons. Checklists raise success odds.",
            "health": "You notice body signals early. Sleep/food tweaks speed recovery.",
        },
        "N": {
            "love": "Your ideas add spark. Sometimes confirm with actions, not only words.",
            "money": "Ideas can become money, but unplanned spending can grow—add structure.",
            "work": "Great at planning and strategy. Break big visions into tiny steps.",
            "health": "Overthinking stacks fatigue. Short workouts/stretching are effective.",
        },
        "T": {
            "love": "You feel reliable with solutions. Add one empathic sentence to boost love luck.",
            "money": "Rational spending is your strength. Set ROI/value rules and savings follow.",
            "work": "Strong at decisions and optimization. Metrics can bring recognition.",
            "health": "You can push through—remember: rest sustains performance.",
        },
        "F": {
            "love": "Warm empathy is your charm. One kind phrase can change the vibe instantly.",
            "money": "You may spend on people. A simple budget keeps the flow healthy.",
            "work": "You lift teamwork. Avoid overload from saying yes to everything.",
            "health": "Mood affects energy. Sleep/sunlight/walks stabilize you.",
        },
        "J": {
            "love": "Clear plans feel safe. Direct, kind clarity is your attractiveness point.",
            "money": "Budget routines win. Auto-saving alone increases money luck.",
            "work": "Deadlines and organization are your superpower—recognition follows.",
            "health": "Perfectionism can tighten you. Schedule downtime deliberately.",
        },
        "P": {
            "love": "Your free, fun vibe is attractive. Lock in important dates to avoid friction.",
            "money": "Watch impulse spending. A 10-minute pause rule works well.",
            "work": "Fast adaptation is your weapon. Add deadline control and you level up.",
            "health": "Rhythm can drift. Fix bedtime and your energy improves.",
        },
        "combo": {
            "growth": "This year’s theme is growth. Ride {zodiac}'s flow and apply {mbti}'s strengths consistently.",
            "love": "Love needs balance between expression and care. Keep your {mbti} style, but match the other person's pace once more.",
            "money": "Money = block leaks + catch chances. When {zodiac}'s opportunity appears, make one more concrete action in {mbti} style.",
            "work": "Work/study is won by small execution. Finish one task today and the whole flow opens.",
        }
    },
    "zh": {
        "E": {
            "love": "你擅长表达与推进。主动约见/沟通，恋爱运更快打开。",
            "money": "机会多来自人脉。介绍/推荐可能直接变成收入。",
            "work": "你在协作与表达上发光。但说得太快可能引起误会。",
            "health": "行程多易过劳。把休息也当作“预约”。",
        },
        "I": {
            "love": "你擅长深度关系。慢慢建立信任更有利。",
            "money": "你会有效止损漏财。比起冒险，更适合稳健管理。",
            "work": "专注力强是优势。给自己留“独处深度工作”时间。",
            "health": "容易把压力闷在心里。散步/呼吸等小习惯很有用。",
        },
        "S": {
            "love": "现实的体贴很加分。守时与小行动能建立信任。",
            "money": "你善于控制支出。清理固定成本就能明显提升财运。",
            "work": "执行与准确是武器。清单化能提高成功率。",
            "health": "你能更早察觉身体信号。规律睡眠饮食恢复更快。",
        },
        "N": {
            "love": "你能带来心动与灵感。但有时需要用行动确认，而不是只靠话。",
            "money": "点子能赚钱，但无计划容易扩张消费，需要一点结构。",
            "work": "策划与大局观强。把大目标拆成小步骤会很强。",
            "health": "想太多会累。短运动/拉伸很有效。",
        },
        "T": {
            "love": "你解决问题很可靠。加一句共情，会让恋爱运更好。",
            "money": "理性消费强项。建立价值/收益规则，钱更容易聚。",
            "work": "决断与优化能力强。抓住指标与数据会更易被认可。",
            "health": "容易硬扛。记住：休息才能走更远。",
        },
        "F": {
            "love": "共情与温柔是魅力。一句体贴话能瞬间升温。",
            "money": "可能在人情上多花钱。设预算就能稳住财运。",
            "work": "你能带动氛围与团队。但别什么都答应，避免过载。",
            "health": "情绪影响状态。睡眠/晒太阳/散步能稳住能量。",
        },
        "J": {
            "love": "明确的计划带来安全感。清晰表达是加分点。",
            "money": "预算与储蓄习惯很强。自动转存就能提升财运。",
            "work": "管理与截止能力强，容易得到认可与晋升。",
            "health": "完美主义易紧绷。把休息写进计划里。",
        },
        "P": {
            "love": "自由有趣很吸引人。但重要日子请“确认”，避免误会。",
            "money": "注意情绪性消费。消费前等10分钟很有效。",
            "work": "应变快是武器。补上截止管理，会明显上升。",
            "health": "作息易漂。固定睡觉时间就会改善。",
        },
        "combo": {
            "growth": "今年主题是成长。顺着 {zodiac} 的走势，用 {mbti} 的优势持续推进，收获会更大。",
            "love": "恋爱关键在“表达与体贴”的平衡。保持 {mbti} 风格，同时再多对齐一次对方节奏。",
            "money": "财运=堵漏+抓机会。当 {zodiac} 的机会出现时，用 {mbti} 的方式把行动再具体一步。",
            "work": "事业/学业靠小执行取胜。今天完成一件事，整体流动就会打开。",
        }
    },
    "ja": {
        "E": {
            "love": "表現と推進力が強み。先に連絡/予定を取ると恋愛運が開きやすい。",
            "money": "チャンスは人から。紹介・推薦が収入につながりやすい。",
            "work": "協力や発表で輝く。ただし言葉が先走ると誤解に注意。",
            "health": "予定過多で疲れやすい。休息も“予定”として確保。",
        },
        "I": {
            "love": "深い関係づくりが得意。ゆっくり信頼を積むのが有利。",
            "money": "ムダ遣いを止めるのが上手。大勝負より安定運用が◎。",
            "work": "没頭力が武器。集中できる時間を守ると成果が伸びる。",
            "health": "ストレスを抱え込みがち。散歩/呼吸など小さな習慣が効く。",
        },
        "S": {
            "love": "現実的な気配りが魅力。約束/時間/行動が信頼を作る。",
            "money": "支出管理が得意。固定費を見直すだけで金運UP。",
            "work": "実行力と正確さが武器。チェックリストが成功率を上げる。",
            "health": "体のサインに気づきやすい。睡眠と食事で回復が早い。",
        },
        "N": {
            "love": "ときめきと発想で関係が進む。言葉だけでなく確認も大切。",
            "money": "アイデアが収益に。ただ無計画だと出費が増えやすい。",
            "work": "企画/戦略が強い。大きな構想を小さな行動に分解すると◎。",
            "health": "考えすぎで疲れがたまる。短い運動/ストレッチが効果的。",
        },
        "T": {
            "love": "解決志向で頼れる。共感の一言が恋愛運をさらに伸ばす。",
            "money": "合理的な判断が強み。基準を作るほど貯まりやすい。",
            "work": "決断と最適化が得意。数値と指標を押さえると評価UP。",
            "health": "無理しても耐えがち。休むほど長く走れる。",
        },
        "F": {
            "love": "共感と優しさが魅力。小さな一言で雰囲気が変わる。",
            "money": "人のための出費が増えがち。予算を決めると安定。",
            "work": "チームの空気を良くする。ただ抱え込み過ぎに注意。",
            "health": "気分が体調に出やすい。睡眠/日光/散歩で安定。",
        },
        "J": {
            "love": "はっきりした約束が安心感。丁寧に明確に伝えると好感度UP。",
            "money": "予算/貯蓄ルーティンが強み。自動積立が効果大。",
            "work": "締切管理が最強。責任感が評価につながる。",
            "health": "完璧主義で緊張しやすい。休息も計画に入れて。",
        },
        "P": {
            "love": "自由で楽しい魅力。大事な日は“確定”して摩擦を減らす。",
            "money": "気分買い注意。買う前に10分待つルールが効く。",
            "work": "臨機応変が武器。締切管理を補強すると一気に伸びる。",
            "health": "生活リズムが乱れやすい。就寝時間固定が効果的。",
        },
        "combo": {
            "growth": "今年のテーマは成長。{zodiac} の流れを {mbti} の強みで“継続”すると大きく実ります。",
            "love": "恋愛は「表現と配慮」のバランスが鍵。{mbti} らしさを保ちつつ相手のペースにもう一歩合わせて。",
            "money": "金運は「ムダの遮断＋チャンス捕捉」。{zodiac} の機会が来たら {mbti} 流で一段だけ具体化。",
            "work": "仕事/学業は小さな実行が勝負。今日1つ終えると流れが開きます。",
        }
    },
    "ru": {
        "E": {
            "love": "Сильны выражение и импульс. Инициируйте встречи — любовь откроется быстрее.",
            "money": "Шансы приходят через людей. Рекомендации могут стать доходом.",
            "work": "Вы ярки в команде и презентациях. Не торопитесь с словами, чтобы избежать недопонимания.",
            "health": "Риск выгорания из-за занятости. Планируйте отдых как встречу.",
        },
        "I": {
            "love": "Сильны глубокие связи. Медленное укрепление доверия выгоднее.",
            "money": "Хорошо перекрываете утечки. Стабильная стратегия лучше риска.",
            "work": "Ваш козырь — концентрация. Берегите тихое время для фокуса.",
            "health": "Стресс легко копится внутри. Помогают прогулки/дыхание/рутины.",
        },
        "S": {
            "love": "Практичная забота — ваш плюс. Пунктуальность и действия создают доверие.",
            "money": "Контроль расходов сильный. Пересмотр фиксированных затрат резко улучшит финансы.",
            "work": "Точность и исполнение — оружие. Чек-листы повышают успех.",
            "health": "Рано замечаете сигналы тела. Сон и питание дают быстрый эффект.",
        },
        "N": {
            "love": "Вы даёте искру и идеи. Но иногда нужны подтверждения действиями.",
            "money": "Идеи могут приносить деньги, но без плана растут траты — добавьте структуру.",
            "work": "Сильны в стратегии. Разбейте большой план на маленькие шаги.",
            "health": "Перемысливание копит усталость. Короткие упражнения/растяжка помогают.",
        },
        "T": {
            "love": "Вы надёжны в решениях. Добавьте фразу сочувствия — и отношения заиграют.",
            "money": "Рациональность — сила. Правила ценности/выгоды помогают копить.",
            "work": "Сильны в оптимизации. Метрики и цифры принесут признание.",
            "health": "Легко «тащите» до конца. Отдых = долгосрочная сила.",
        },
        "F": {
            "love": "Эмпатия — ваш шарм. Одно тёплое слово меняет атмосферу.",
            "money": "Можно много тратить на людей. Простой бюджет стабилизирует.",
            "work": "Вы укрепляете команду. Но не берите всё на себя — риск перегруза.",
            "health": "Эмоции влияют на энергию. Сон/свет/прогулки стабилизируют.",
        },
        "J": {
            "love": "Чёткие договорённости дают безопасность. Ясность — ваш плюс.",
            "money": "Сильны в режиме бюджета. Автосбережения заметно улучшают финансы.",
            "work": "Дедлайны и порядок — суперсила. Признание приходит естественно.",
            "health": "Перфекционизм напрягает. Планируйте отдых заранее.",
        },
        "P": {
            "love": "Свободный и лёгкий стиль привлекает. Важные даты лучше фиксировать.",
            "money": "Осторожно с импульсивными покупками. Правило «подождать 10 минут» работает.",
            "work": "Сильны в адаптации. Добавьте контроль дедлайнов — и рост будет быстрым.",
            "health": "Ритм легко сбивается. Фиксируйте время сна.",
        },
        "combo": {
            "growth": "Тема года — рост. Используйте поток {zodiac} и сильные стороны {mbti} регулярно — результат будет крупнее.",
            "love": "В любви важен баланс «выражение и забота». Сохраняйте стиль {mbti}, но ещё раз подстройтесь под темп партнёра.",
            "money": "Финансы = перекрыть утечки + поймать шанс. Когда появляется шанс {zodiac}, сделайте действие на шаг конкретнее в стиле {mbti}.",
            "work": "Работа/учёба решается маленькими действиями. Закройте одну задачу сегодня — и поток откроется.",
        }
    },
    "hi": {
        "E": {
            "love": "आपका एक्सप्रेशन और मोमेंटम मजबूत है। पहल करेंगे तो प्रेम-भाग्य जल्दी खुलेगा।",
            "money": "मौके लोगों से आते हैं। रेफरल/परिचय आय में बदल सकते हैं।",
            "work": "टीमवर्क और प्रेज़ेंटेशन में आप चमकते हैं। जल्दबाज़ी से गलतफहमी हो सकती है।",
            "health": "व्यस्तता से बर्नआउट का खतरा। आराम को भी अपॉइंटमेंट की तरह तय करें।",
        },
        "I": {
            "love": "गहरी रिश्तों में आप मजबूत हैं। धीरे-धीरे भरोसा बनाना फायदेमंद।",
            "money": "आप खर्च की ‘लीकेज’ रोकते हैं। जोखिम से अधिक स्थिर मैनेजमेंट बेहतर।",
            "work": "डीप-फोकस आपका हथियार है। शांत समय बचाकर रखें।",
            "health": "तनाव अंदर जमा हो सकता है। वॉक/ब्रीदिंग जैसी छोटी रूटीन मदद करेगी।",
        },
        "S": {
            "love": "व्यावहारिक देखभाल आकर्षक है। समय/वादा/कर्म से भरोसा बनता है।",
            "money": "खर्च नियंत्रण आपकी ताकत। फिक्स्ड कॉस्ट घटाएँ, धन-भाग्य बढ़ेगा।",
            "work": "एक्ज़िक्यूशन और सटीकता आपका प्लस। चेकलिस्ट सफलता बढ़ाती है।",
            "health": "शरीर के संकेत जल्दी पकड़ते हैं। नींद/डाइट सुधार से रिकवरी तेज।",
        },
        "N": {
            "love": "आप रिश्ते में स्पार्क और आइडिया लाते हैं। कभी-कभी शब्द नहीं, कार्रवाई जरूरी।",
            "money": "आइडिया से कमाई हो सकती है, पर बिना प्लान खर्च बढ़ेगा—थोड़ी संरचना रखें।",
            "work": "रणनीति में मजबूत। बड़े लक्ष्य को छोटे कदमों में तोड़ें।",
            "health": "ओवरथिंकिंग से थकान बढ़ती है। छोटा वर्कआउट/स्ट्रेचिंग असरदार।",
        },
        "T": {
            "love": "समाधान देने में आप भरोसेमंद हैं। एक सहानुभूति वाक्य प्रेम-भाग्य बढ़ाएगा।",
            "money": "तर्कसंगत खर्च आपकी ताकत। वैल्यू/ROI नियम बनाएं—बचत बढ़ेगी।",
            "work": "निर्णय और ऑप्टिमाइज़ेशन मजबूत। मीट्रिक्स से पहचान मिलेगी।",
            "health": "आप ज्यादा सह लेते हैं। याद रखें—आराम से लंबी दौड़ होती है।",
        },
        "F": {
            "love": "आपकी सहानुभूति आकर्षण है। एक नरम वाक्य माहौल बदल देता है।",
            "money": "लोगों पर खर्च बढ़ सकता है। सिंपल बजट से संतुलन बनेगा।",
            "work": "टीम का माहौल आप बनाते हैं। हर चीज़ ‘हाँ’ न कहें—ओवरलोड से बचें।",
            "health": "मूड का असर शरीर पर पड़ता है। नींद/धूप/वॉक स्थिरता देती है।",
        },
        "J": {
            "love": "स्पष्ट प्लान रिश्ते को सुरक्षा देता है। साफ और दयालु संप्रेषण प्लस है।",
            "money": "बजट रूटीन आपकी ताकत। ऑटो-सेविंग से धन-भाग्य बढ़ेगा।",
            "work": "डेडलाइन और संगठन मजबूत। जिम्मेदारी से पहचान मिलती है।",
            "health": "परफेक्शनिज़्म तनाव दे सकता है। आराम को भी प्लान में रखें।",
        },
        "P": {
            "love": "आपका फ्री और मज़ेदार अंदाज़ आकर्षक है। महत्वपूर्ण तारीखें पक्की करें।",
            "money": "इम्पल्स खर्च पर ध्यान दें। खरीद से पहले 10 मिनट रुकें।",
            "work": "एडाप्टेशन आपकी ताकत। डेडलाइन कंट्रोल जोड़ेंगे तो ग्रोथ तेज।",
            "health": "रूटीन बिगड़ सकता है। सोने का समय फिक्स करें।",
        },
        "combo": {
            "growth": "इस साल का थीम ग्रोथ है। {zodiac} के फ्लो के साथ {mbti} की ताकत को लगातार लगाएँ—नतीजा बड़ा होगा।",
            "love": "प्रेम में ‘अभिव्यक्ति और देखभाल’ का संतुलन जरूरी है। {mbti} स्टाइल रखें, पर साथी की गति से एक कदम और मिलाएँ।",
            "money": "धन = लीकेज रोकना + अवसर पकड़ना। {zodiac} का मौका आए तो {mbti} स्टाइल में एक कदम और ठोस कार्रवाई करें।",
            "work": "काम/पढ़ाई छोटे एक्शन से जीतती है। आज एक काम पूरा करें, फ्लो खुलेगा।",
        }
    },
}

def mbti_influence_text(lang: str, mbti: str):
    pack = INFL.get(lang, INFL["en"])
    # letters
    e = "E" if mbti[0] == "E" else "I"
    s = "S" if mbti[1] == "S" else "N"
    t = "T" if mbti[2] == "T" else "F"
    j = "J" if mbti[3] == "J" else "P"

    # For each category, blend 2 letters to feel meaningful (not too long)
    love = f"{pack[e]['love']} {pack[t]['love']}"
    money = f"{pack[s]['money']} {pack[j]['money']}"
    work = f"{pack[t]['work']} {pack[j]['work']}"
    health = f"{pack[e]['health']} {pack[s]['health']}"
    return love, money, work, health

def combo_advice_text(lang: str, zodiac: str, mbti: str, rng: random.Random):
    pack = INFL.get(lang, INFL["en"])["combo"]
    # pick 2 lines to keep it concise but rich
    keys = ["growth", "love", "money", "work"]
    rng.shuffle(keys)
    chosen = keys[:2]
    a = pack[chosen[0]].format(zodiac=zodiac, mbti=mbti)
    b = pack[chosen[1]].format(zodiac=zodiac, mbti=mbti)
    return a, b

# =========================================================
# Tests (12 / 16)
# =========================================================
SIMPLE_12 = {
    "ko": [
        ("주말에 친구가 갑자기 '놀자!' 하면?", "좋아! 바로 나감", "집에서 쉬고 싶어", "EI"),
        ("모임에서 처음 본 사람들과 대화", "재밌고 신나", "부담되고 피곤", "EI"),
        ("하루 종일 사람 만난 후", "아직 에너지 남음", "혼자 있고 싶음", "EI"),
        ("생각이 떠오르면", "말로 풀어냄", "머릿속 정리", "EI"),
        ("새 카페 가면 먼저 보는 건", "메뉴/가격", "분위기/컨셉", "SN"),
        ("책/영화 볼 때", "디테일/전개", "상징/의미", "SN"),
        ("쇼핑할 때", "필요한 것 바로", "미래 조합 상상", "SN"),
        ("의견 충돌 시", "논리/팩트", "배려/조율", "TF"),
        ("누가 울면서 상담", "해결책 제시", "공감 먼저", "TF"),
        ("친구가 늦어서 화날 때", "바로 지적", "부드럽게 말함", "TF"),
        ("여행 스타일", "계획대로", "즉흥으로", "JP"),
        ("마감 앞두면", "미리미리", "막판 몰아서", "JP"),
    ],
    "en": [
        ("Friends suddenly ask to hang out?", "Go out!", "Stay home", "EI"),
        ("Talking to strangers at a party", "Fun", "Tiring", "EI"),
        ("After meeting people all day", "Still energized", "Need alone time", "EI"),
        ("When an idea comes", "Say it out", "Think first", "EI"),
        ("At a new cafe you notice", "Menu/prices", "Vibe/concept", "SN"),
        ("When watching a movie", "Details/plot", "Symbols/meaning", "SN"),
        ("When shopping", "Buy needed items", "Imagine combinations", "SN"),
        ("When opinions clash", "Logic/facts", "Harmony/care", "TF"),
        ("When someone cries", "Give solutions", "Empathize first", "TF"),
        ("When friend is late", "Point it out", "Say gently", "TF"),
        ("Travel style", "Planned", "Spontaneous", "JP"),
        ("Before a deadline", "Finish early", "Last minute", "JP"),
    ],
    "zh": [
        ("周末朋友突然说“出来玩！”", "马上出门", "更想在家休息", "EI"),
        ("聚会和陌生人聊天", "很有趣", "很累/有压力", "EI"),
        ("见了一整天人之后", "还有精力", "想独处充电", "EI"),
        ("有想法时", "说出来/分享", "先在脑内整理", "EI"),
        ("去新咖啡店先注意", "菜单/价格", "氛围/概念", "SN"),
        ("看电影/读书时", "关注细节/剧情", "找象征/意义", "SN"),
        ("购物时", "买需要的", "想象搭配", "SN"),
        ("意见冲突时", "逻辑/事实", "照顾感受/协调", "TF"),
        ("有人哭着倾诉", "给解决方案", "先共情", "TF"),
        ("朋友迟到你生气", "直接指出", "温和表达", "TF"),
        ("旅行风格", "按计划", "随性即兴", "JP"),
        ("临近截止", "提前完成", "最后冲刺", "JP"),
    ],
    "ja": [
        ("週末に突然「遊ぼう！」と言われたら", "すぐ出かける", "家で休みたい", "EI"),
        ("初対面の人と話すのは", "楽しい", "疲れる", "EI"),
        ("一日中人に会った後", "まだ元気", "一人になりたい", "EI"),
        ("思いついたら", "口に出す", "頭の中で整理", "EI"),
        ("新しいカフェでまず見るのは", "メニュー/価格", "雰囲気/コンセプト", "SN"),
        ("映画/本では", "細部/展開", "象徴/意味", "SN"),
        ("買い物は", "必要な物を買う", "組み合わせを想像", "SN"),
        ("意見がぶつかったら", "論理/事実", "配慮/調整", "TF"),
        ("泣きながら相談されたら", "解決策を出す", "まず共感", "TF"),
        ("友だちが遅刻したら", "指摘する", "やさしく言う", "TF"),
        ("旅行スタイル", "計画派", "即興派", "JP"),
        ("締切前は", "早めにやる", "直前に追い込む", "JP"),
    ],
    "ru": [
        ("Друзья внезапно зовут гулять?", "Иду!", "Лучше дома", "EI"),
        ("Разговор с незнакомцами на встрече", "Интересно", "Утомляет", "EI"),
        ("После дня с людьми", "Ещё есть энергия", "Нужно побыть одному", "EI"),
        ("Когда приходит идея", "Говорю вслух", "Сначала думаю", "EI"),
        ("В новом кафе первым делом", "Меню/цены", "Атмосфера/концепт", "SN"),
        ("Фильм/книга", "Детали/сюжет", "Символы/смысл", "SN"),
        ("Шопинг", "Покупаю нужное", "Представляю сочетания", "SN"),
        ("Конфликт мнений", "Логика/факты", "Гармония/забота", "TF"),
        ("Кто-то плачет и просит совета", "Даю решения", "Сначала сочувствую", "TF"),
        ("Друг опаздывает", "Скажу прямо", "Скажу мягко", "TF"),
        ("Путешествия", "По плану", "Спонтанно", "JP"),
        ("Перед дедлайном", "Заранее", "В последний момент", "JP"),
    ],
    "hi": [
        ("वीकेंड पर दोस्त अचानक बुलाएँ?", "चलो!", "घर पर रहना", "EI"),
        ("पार्टी में अजनबियों से बात", "मज़ेदार", "थका देने वाला", "EI"),
        ("पूरा दिन लोगों के बाद", "ऊर्जा बची है", "अकेले समय चाहिए", "EI"),
        ("विचार आए तो", "बोल देता/देती हूँ", "पहले सोचता/सोचती हूँ", "EI"),
        ("नई कैफ़े में पहले", "मेन्यू/कीमत", "वाइब/कॉन्सेप्ट", "SN"),
        ("फिल्म/किताब में", "डिटेल/प्लॉट", "प्रतीक/अर्थ", "SN"),
        ("शॉपिंग में", "जरूरी चीज़", "कॉम्बिनेशन सोचता/सोचती", "SN"),
        ("मतभेद में", "लॉजिक/फैक्ट", "भावना/समझौता", "TF"),
        ("कोई रोकर सलाह माँगे", "हल बताता/बताती", "पहले सहानुभूति", "TF"),
        ("दोस्त लेट हो तो", "सीधा बोलूँ", "नरमी से बोलूँ", "TF"),
        ("ट्रैवल स्टाइल", "प्लान्ड", "स्पॉन्टेनियस", "JP"),
        ("डेडलाइन के पहले", "पहले खत्म", "आख़िरी समय", "JP"),
    ],
}

DETAIL_16 = {
    "ko": {
        "labels": {"yes": "그렇다", "no": "아니다"},
        "E": [
            "사람을 만나면 에너지가 채워진다",
            "혼자 있으면 금방 심심해진다",
            "생각을 말로 정리하는 편이다",
            "새로운 사람을 만나는 게 부담스럽지 않다",
        ],
        "S": [
            "구체적인 사실/경험을 더 믿는다",
            "설명은 예시와 디테일이 있어야 이해가 쉽다",
            "현재 할 수 있는 현실적인 방법을 먼저 찾는다",
            "감으로 보기보다 확인하고 진행하는 편이다",
        ],
        "T": [
            "결정할 때 논리/근거가 가장 중요하다",
            "문제는 감정보다 해결이 먼저라고 생각한다",
            "토론에서 맞고 틀림을 분명히 하는 편이다",
            "정 때문에 기준을 바꾸는 건 부담스럽다",
        ],
        "J": [
            "계획이 있어야 마음이 편하다",
            "마감은 미리 끝내는 편이다",
            "정리/정돈이 안 되면 스트레스를 받는다",
            "약속이 갑자기 바뀌면 불편하다",
        ],
    },
    "en": {
        "labels": {"yes": "Yes", "no": "No"},
        "E": [
            "Socializing recharges me",
            "I get bored quickly when I’m alone",
            "I organize my thoughts by speaking",
            "Meeting new people doesn’t feel stressful",
        ],
        "S": [
            "I trust concrete facts/experience more",
            "Examples and details help me understand",
            "I look for practical methods first",
            "I prefer to verify before acting",
        ],
        "T": [
            "Logic and evidence matter most in decisions",
            "Solving the problem comes before feelings",
            "I like to be clear about right/wrong in debates",
            "Changing standards just to be nice feels hard",
        ],
        "J": [
            "I feel comfortable with plans",
            "I usually finish before the deadline",
            "Messiness stresses me out",
            "Sudden schedule changes bother me",
        ],
    },
    "zh": {
        "labels": {"yes": "是", "no": "否"},
        "E": [
            "社交会让我充电",
            "独处久了会很快无聊",
            "我倾向于通过说出来整理思路",
            "结识新朋友不会让我有压力",
        ],
        "S": [
            "我更相信具体事实/经验",
            "有例子和细节会更容易理解",
            "我会先找现实可行的方法",
            "我倾向先确认再行动",
        ],
        "T": [
            "做决定时逻辑和证据最重要",
            "我更重视解决问题而不是情绪",
            "讨论时我喜欢把对错讲清楚",
            "为了照顾人而改变原则会让我为难",
        ],
        "J": [
            "有计划会让我更安心",
            "我通常会提前完成截止任务",
            "不整洁会让我压力大",
            "日程突然变动会让我不舒服",
        ],
    },
    "ja": {
        "labels": {"yes": "はい", "no": "いいえ"},
        "E": [
            "人と会うと元気になる",
            "一人だとすぐ退屈になる",
            "話すことで考えが整理される",
            "新しい人と会うのはあまり負担ではない",
        ],
        "S": [
            "具体的な事実や経験をより信じる",
            "例や細部があると理解しやすい",
            "まず現実的にできる方法を探す",
            "確認してから進めるタイプだ",
        ],
        "T": [
            "決定では論理と根拠が最重要",
            "感情より問題解決を優先する",
            "議論では白黒をはっきりさせたい",
            "気を使って基準を変えるのは苦手",
        ],
        "J": [
            "計画があると安心する",
            "締切は前倒しで終えることが多い",
            "散らかっているとストレス",
            "予定が急に変わると困る",
        ],
    },
    "ru": {
        "labels": {"yes": "Да", "no": "Нет"},
        "E": [
            "Общение меня заряжает",
            "Когда я один/одна, быстро становится скучно",
            "Я лучше формулирую мысли вслух",
            "Новые знакомства обычно не стресс",
        ],
        "S": [
            "Я больше доверяю фактам и опыту",
            "Примеры и детали помогают понять",
            "Сначала ищу практичный способ",
            "Предпочитаю проверять перед действием",
        ],
        "T": [
            "В решениях важнее логика и доказательства",
            "Сначала решение, потом эмоции",
            "В споре люблю ясность: что верно, а что нет",
            "Менять принципы «ради вежливости» трудно",
        ],
        "J": [
            "С планом мне спокойнее",
            "Чаще заканчиваю до дедлайна",
            "Беспорядок вызывает стресс",
            "Резкие изменения планов раздражают",
        ],
    },
    "hi": {
        "labels": {"yes": "हाँ", "no": "नहीं"},
        "E": [
            "लोगों से मिलकर मुझे ऊर्जा मिलती है",
            "अकेले रहने पर मुझे जल्दी बोरियत होती है",
            "बोलकर मैं अपने विचार स्पष्ट करता/करती हूँ",
            "नए लोगों से मिलना मुझे तनाव नहीं देता",
        ],
        "S": [
            "मैं ठोस तथ्य/अनुभव पर ज्यादा भरोसा करता/करती हूँ",
            "उदाहरण और डिटेल से समझना आसान होता है",
            "मैं पहले व्यावहारिक तरीका ढूंढता/ढूंढती हूँ",
            "मैं कार्रवाई से पहले पुष्टि करना पसंद करता/करती हूँ",
        ],
        "T": [
            "निर्णय में लॉजिक/सबूत सबसे अहम है",
            "मैं भावना से पहले समस्या-समाधान को रखता/रखती हूँ",
            "बहस में सही/गलत स्पष्ट करना मुझे पसंद है",
            "केवल ‘अच्छा लगने’ के लिए नियम बदलना कठिन है",
        ],
        "J": [
            "योजना होने पर मन शांत रहता है",
            "मैं डेडलाइन से पहले काम खत्म करता/करती हूँ",
            "अव्यवस्था से तनाव होता है",
            "अचानक शेड्यूल बदलने पर असहज लगता है",
        ],
    },
}

# =========================================================
# UI Header
# =========================================================
lang_labels = [x[0] for x in LANGS]
lang_codes = [x[1] for x in LANGS]
cur_idx = lang_codes.index(st.session_state.lang) if st.session_state.lang in lang_codes else 0

selected = st.radio(
    T["ko"]["lang_label"],
    lang_labels,
    index=cur_idx,
    horizontal=True
)
st.session_state.lang = lang_codes[lang_labels.index(selected)]
t = T[st.session_state.lang]

st.markdown(
    f"""
<div class="hero">
  <div class="hero-title">{t["title"]}</div>
  <div class="hero-sub">{t["caption"]}</div>
</div>
""",
    unsafe_allow_html=True
)

# 광고 자리(항상 표시)
render_reserved_ad(t.get("ad_reserved", "AD"))

# =========================================================
# Navigation / Validation
# =========================================================
def go_result():
    if not (1900 <= st.session_state.y <= 2030):
        st.error(t["err_year"])
        return
    if not validate_birth(st.session_state.y, st.session_state.m, st.session_state.d):
        st.error(t["err_birth"])
        return
    st.session_state.step = "result"
    st.rerun()

# =========================================================
# Input Screen
# =========================================================
def input_screen():
    if st.session_state.lang == "ko":
        render_korean_ad(T["ko"])

    st.markdown(f"<div class='card'><div class='card-title'>{t['input_title']}</div></div>", unsafe_allow_html=True)
    st.session_state.name = st.text_input(t["name_ph"], value=st.session_state.name)

    st.markdown(f"**{t['birth']}**")
    c1, c2, c3 = st.columns(3)
    st.session_state.y = int(c1.number_input(t["year"], min_value=1900, max_value=2030, value=int(st.session_state.y), step=1))
    st.session_state.m = int(c2.number_input(t["month"], min_value=1, max_value=12, value=int(st.session_state.m), step=1))
    st.session_state.d = int(c3.number_input(t["day"], min_value=1, max_value=31, value=int(st.session_state.d), step=1))

    mode = st.radio(
        t["mbti_mode"],
        [t["direct"], t["test12"], t["test16"]],
        index=0 if st.session_state.mbti_mode == "direct" else (1 if st.session_state.mbti_mode == "test12" else 2),
    )

    if mode == t["direct"]:
        st.session_state.mbti_mode = "direct"
        st.session_state.mbti = st.selectbox(
            t["choose_mbti"],
            MBTI_TYPES,
            index=MBTI_TYPES.index(st.session_state.mbti) if st.session_state.mbti in MBTI_TYPES else 0
        )
        if st.button(t["view_result"], use_container_width=True):
            go_result()

    elif mode == t["test12"]:
        st.session_state.mbti_mode = "test12"
        if st.button(t["start_test"], use_container_width=True):
            st.session_state.step = "test12"
            st.rerun()

    else:
        st.session_state.mbti_mode = "test16"
        if st.button(t["start_test"], use_container_width=True):
            st.session_state.step = "test16"
            st.rerun()

# =========================================================
# Test 12
# =========================================================
def test12_screen():
    qs = SIMPLE_12.get(st.session_state.lang, SIMPLE_12["en"])
    st.markdown(
        f"<div class='card'><div class='card-title'>{t['test12_title']}</div><div class='mini'>{t['test12_desc']}</div></div>",
        unsafe_allow_html=True
    )

    with st.form("form_test12", clear_on_submit=False):
        answers = []
        for i, (q, a, b, dim) in enumerate(qs):
            choice = st.radio(q, [a, b], key=f"t12_{st.session_state.lang}_{i}")
            answers.append((choice == a, dim))
        submitted = st.form_submit_button(t["view_result"], use_container_width=True)

    if submitted:
        ei = sn = tf = jp = 0
        for pick_a, dim in answers:
            if dim == "EI": ei += 1 if pick_a else -1
            if dim == "SN": sn += 1 if pick_a else -1
            if dim == "TF": tf += 1 if pick_a else -1
            if dim == "JP": jp += 1 if pick_a else -1
        mbti = ("E" if ei >= 0 else "I") + ("S" if sn >= 0 else "N") + ("T" if tf >= 0 else "F") + ("J" if jp >= 0 else "P")
        st.session_state.mbti = mbti
        go_result()

# =========================================================
# Test 16 (중복 질문 제거)
# =========================================================
def test16_screen():
    d = DETAIL_16.get(st.session_state.lang, DETAIL_16["en"])
    yes_label = d["labels"]["yes"]
    no_label = d["labels"]["no"]

    st.markdown(
        f"<div class='card'><div class='card-title'>{t['test16_title']}</div><div class='mini'>{t['test16_desc']}</div></div>",
        unsafe_allow_html=True
    )

    with st.form("form_test16", clear_on_submit=False):
        scores = {"E":0, "S":0, "T":0, "J":0}
        for axis in ["E","S","T","J"]:
            st.markdown("---")
            for i, q in enumerate(d[axis]):
                c = st.radio(q, [yes_label, no_label], key=f"t16_{st.session_state.lang}_{axis}_{i}")
                scores[axis] += 1 if c == yes_label else -1

        submitted = st.form_submit_button(t["view_result"], use_container_width=True)

    if submitted:
        mbti = ("E" if scores["E"] >= 0 else "I") + ("S" if scores["S"] >= 0 else "N") + ("T" if scores["T"] >= 0 else "F") + ("J" if scores["J"] >= 0 else "P")
        st.session_state.mbti = mbti
        go_result()

# =========================================================
# Result Screen
# =========================================================
def result_screen():
    lang = st.session_state.lang
    b = fortune_bank(lang)

    y, m, d = st.session_state.y, st.session_state.m, st.session_state.d
    mbti = st.session_state.mbti

    zodiac = get_zodiac(y, lang)
    if zodiac is None:
        zodiac = get_zodiac(y, "en")

    today_key = datetime.now().strftime("%Y%m%d")
    seed = stable_seed(lang, y, m, d, mbti, today_key)
    rng = random.Random(seed)

    today_msg = rng.choice(b["today"])
    tomorrow_msg = random.Random(stable_seed(seed, "tomorrow")).choice(b["tomorrow"])
    annual_msg = rng.choice(b["annual"])
    love_msg = rng.choice(b["love"])
    money_msg = rng.choice(b["money"])
    work_msg = rng.choice(b["work"])
    health_msg = rng.choice(b["health"])
    tip_msg = rng.choice(b["tips"])
    caution_msg = rng.choice(b["cautions"])
    lucky_color = rng.choice(b["colors"])
    lucky_item = rng.choice(b["items"])
    lucky_num = str(rng.randint(1, 9))

    # NEW: MBTI influence + combo advice
    infl_love, infl_money, infl_work, infl_health = mbti_influence_text(lang, mbti)
    c1, c2 = combo_advice_text(lang, zodiac, mbti, rng)

    name = st.session_state.name.strip()
    name_prefix = (name + ("님의" if lang == "ko" else "")) if name else ""

    st.markdown(
        f"""
<div class="hero">
  <div style="font-size:1.25rem; font-weight:900;">{name_prefix} {mbti}</div>
  <div class="hero-sub">{t["top_combo"]}</div>
</div>
""",
        unsafe_allow_html=True
    )

    z_desc = ZODIAC_DESC.get(lang, ZODIAC_DESC["en"]).get(zodiac, "")
    m_desc = MBTI_DESC.get(lang, MBTI_DESC["en"]).get(mbti, "")

    saju_line = b["saju_line"]

    st.markdown("<div class='card'>", unsafe_allow_html=True)

    st.markdown(
        f"""
**{t["zodiac_title"]}**: {z_desc}  
**{t["mbti_title"]}**: {m_desc}  
**{t["saju_title"]}**: {saju_line}

**{t["today"]}**: {today_msg}  
**{t["tomorrow"]}**: {tomorrow_msg}

**{t["annual"]}**: {annual_msg}

**{t["love"]}**: {love_msg}  
**{t["money"]}**: {money_msg}  
**{t["work"]}**: {work_msg}  
**{t["health"]}**: {health_msg}

**{t["luck"]}**: {t["lucky_color"]} **{lucky_color}** · {t["lucky_item"]} **{lucky_item}** · {t["lucky_num"]} **{lucky_num}**  
**{t["tip"]}**: {tip_msg}  
**{t["caution"]}**: {caution_msg}
""".strip()
    )

    st.markdown("---")
    st.markdown(f"### {t['mbti_influence']}")
    st.markdown(
        f"""
**{t["influence_love"]}**: {infl_love}  
**{t["influence_money"]}**: {infl_money}  
**{t["influence_work"]}**: {infl_work}  
**{t["influence_health"]}**: {infl_health}
""".strip()
    )

    st.markdown("---")
    st.markdown(f"### {t['combo_advice']}")
    st.markdown(f"- {c1}\n- {c2}")

    st.markdown("</div>", unsafe_allow_html=True)

    # 광고 (한국어만 다나눔렌탈)
    if lang == "ko":
        render_korean_ad(T["ko"])
    else:
        render_reserved_ad(t.get("ad_reserved", "AD"))

    # 타로
    with st.expander(t["tarot_btn"], expanded=False):
        tarot_key = rng.choice(list(TAROT.keys()))
        tarot_mean = TAROT[tarot_key].get(lang, TAROT[tarot_key]["en"])
        st.markdown("<div class='card' style='text-align:center;'>", unsafe_allow_html=True)
        st.markdown(f"**{t['tarot_title']}**")
        st.markdown(f"### {tarot_key}")
        st.markdown(tarot_mean)
        st.markdown("</div>", unsafe_allow_html=True)

    # 공유 텍스트 (MBTI 영향/조합도 포함)
    share_text = (
        f"{t['title']}\n"
        f"{name_prefix} {zodiac} / {mbti}\n\n"
        f"{t['today']}: {today_msg}\n"
        f"{t['tomorrow']}: {tomorrow_msg}\n\n"
        f"{t['mbti_influence']}:\n"
        f"- {t['influence_love']}: {infl_love}\n"
        f"- {t['influence_money']}: {infl_money}\n"
        f"- {t['influence_work']}: {infl_work}\n"
        f"- {t['influence_health']}: {infl_health}\n\n"
        f"{t['combo_advice']}:\n"
        f"- {c1}\n- {c2}\n\n"
        f"{APP_URL}"
    )
    share_component(t, share_text)

    if st.button(t["reset"], use_container_width=True):
        keep_lang = st.session_state.lang
        st.session_state.clear()
        ss_init()
        st.session_state.lang = keep_lang
        st.session_state.step = "input"
        st.rerun()

# =========================================================
# Router
# =========================================================
if st.session_state.step == "input":
    input_screen()
elif st.session_state.step == "test12":
    test12_screen()
elif st.session_state.step == "test16":
    test16_screen()
else:
    result_screen()
