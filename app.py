import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, timedelta, date
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
/* Streamlit 기본 여백/헤더로 가려지는 문제 완화 */
header, footer {visibility:hidden;}
.block-container {padding-top: 0.7rem; padding-bottom: 2rem; max-width: 880px;}
html, body, [class*="css"] {font-family: system-ui, -apple-system, "Noto Sans KR", "Segoe UI", Arial, sans-serif;}

/* 상단 그라데이션 헤더 */
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

/* 카드 */
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

/* 광고 카드 */
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
        "err_year": "생년은 1900~2030년 사이로 입력해주세요!",
        "err_birth": "생년월일이 올바르지 않아요. 날짜를 다시 확인해 주세요!",
        "ad_badge": "광고",
        "ad_title": "정수기렌탈 궁금할 때?",
        "ad_desc": "다나눔렌탈 제휴카드 시 월 0원부터 + 설치당일 최대 현금50만원 페이백!",
        "ad_btn": "다나눔렌탈.com 바로가기",
        "ad_url": "https://www.다나눔렌탈.com",
        "ad_reserved": "AD (승인 후 이 위치에 광고가 표시됩니다)",
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
        "err_year": "Birth year must be 1900–2030!",
        "err_birth": "Invalid birth date. Please check again!",
        "ad_reserved": "AD (Ads will appear here after approval)",
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
        "err_year": "出生年份需在 1900–2030！",
        "err_birth": "生日不正确，请重新检查！",
        "ad_reserved": "AD（审核通过后此处显示广告）",
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
        "err_year": "1900〜2030年の範囲で入力してください！",
        "err_birth": "生年月日が正しくありません。確認してください！",
        "ad_reserved": "AD（承認後ここに広告が表示されます）",
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
        "err_year": "Год рождения должен быть 1900–2030!",
        "err_birth": "Неверная дата рождения. Проверьте!",
        "ad_reserved": "AD (после одобрения здесь будет реклама)",
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
        "err_year": "वर्ष 1900–2030 के बीच होना चाहिए!",
        "err_birth": "जन्मतिथि गलत है। कृपया जाँचें!",
        "ad_reserved": "AD (स्वीकृति के बाद यहाँ विज्ञापन दिखेगा)",
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
        "today": ["整理会打开好运：先完成一件拖延的事。", "主动联系更顺利。", "别急躁就大吉。", "30分钟沉浸就能改变节奏。", "小小善意会换来大人缘。"],
        "tomorrow": ["人际运强：约会/会议里会出现关键提示。", "比较后再决定更划算。", "把睡眠当投资。", "先定优先级，一切会更顺。", "适度放松OK。"],
        "annual": ["复利成长的一年：小改进带来大成果。", "机会来自人：关系就是资产。", "整理与取舍让好运加速。", "坚持就是爆发点。", "年底会收获明确结果。"],
        "love": ["先发个问候。", "别急着下结论，保持温度。"],
        "money": ["先堵住漏财：订阅/固定支出检查。", "减少冲动消费，财运上升。"],
        "work": ["协作运佳：多同步一次更快。", "用基本功稳扎稳打最有效。"],
        "health": ["注意咖啡因过量。", "轻松散步能提升能量。"],
        "tips": ["桌面整理3分钟", "早晨散步10分钟", "记一行支出", "今天只完成一件事"],
        "cautions": ["冲动购物", "熬夜/过劳", "情绪爆发"],
        "colors": ["金色","红色","蓝色","绿色","紫色","白色","黑色"],
        "items": ["金色饰品","红色钱包","蓝色挂件","绿植","紫色笔","简约手表"],
    },
    "ja": {
        "saju_line": "五行バランス → 無理しなければ全体運◎。",
        "today": ["片付けが運を開く。後回しを1つ終える。", "先に連絡で対人運UP。", "焦り注意、落ち着いて大吉。", "30分の没頭が一日を変える。", "小さな優しさがご縁に。"],
        "tomorrow": ["人運が強い。約束にヒント。", "比較して決めると◎。", "睡眠に投資を。", "優先順位でスムーズ。", "気分転換OK。"],
        "annual": ["小さな改善が大きな成果へ。", "チャンスは人から来る。", "整理と選択が運を開く。", "継続が爆発点。", "年末に結果が残る。"],
        "love": ["まず一言。", "結論を急がず温度感を大切に。"],
        "money": ["サブスク/固定費の見直し。", "衝動買いを抑えると金運UP。"],
        "work": ["共有をもう一回で加速。", "基礎で勝負が一番強い。"],
        "health": ["カフェイン過多に注意。", "軽い散歩が気を上げる。"],
        "tips": ["机を3分整理", "朝10分散歩", "支出を1行記録", "今日は1つだけ終える"],
        "cautions": ["衝動買い", "過労/夜更かし", "感情の爆発"],
        "colors": ["ゴールド","レッド","ブルー","グリーン","パープル","ホワイト","ブラック"],
        "items": ["金のアクセ","赤い財布","青いキーホルダー","観葉植物","紫のペン","シンプル時計"],
    },
    "ru": {
        "saju_line": "Баланс элементов → не перегружай себя, и всё сложится.",
        "today": ["Порядок открывает удачу: закройте одну задачу.", "Напишите первым — это даст шанс.", "Решайте быстро, действуйте спокойно.", "30 минут фокуса меняют день.", "Доброта вернётся поддержкой."],
        "tomorrow": ["Встреча даст подсказку.", "Сравните перед выбором.", "Вложитесь в сон.", "Приоритеты — и всё легче.", "Умеренно — можно и потратить."],
        "annual": ["Малые улучшения дают большой эффект.", "Возможности приходят через людей.", "Расхламление ускоряет удачу.", "Ещё один шаг — и прорыв.", "К концу года будет результат."],
        "love": ["Короткое сообщение — лучший старт.", "Не торопите выводы, держите тепло."],
        "money": ["Проверьте подписки и расходы.", "Меньше импульсивных покупок — больше удачи."],
        "work": ["Ещё одно обновление команде — быстрее пойдёт.", "Ставка на базу — сильнее всего."],
        "health": ["Осторожно с кофеином.", "Лёгкая прогулка поднимет энергию."],
        "tips": ["3 минуты на порядок", "10 минут прогулки", "Запишите 1 расход", "Закройте 1 задачу"],
        "cautions": ["Импульсивные покупки", "Переутомление/ночные перекусы", "Эмоциональные всплески"],
        "colors": ["Золото","Красный","Синий","Зелёный","Фиолетовый","Белый","Чёрный"],
        "items": ["Золотой аксессуар","Красный кошелёк","Синий брелок","Зелёное растение","Фиолетовая ручка","Минималистичные часы"],
    },
    "hi": {
        "saju_line": "तत्व संतुलित → ज़्यादा दबाव न लें, सब बेहतर होगा।",
        "today": ["सफाई से भाग्य खुलता है: एक काम पूरा करें।", "पहले संपर्क करें—मौका बढ़ेगा।", "जल्दबाज़ी से बचें, सब अच्छा होगा।", "30 मिनट फोकस काफी है।", "छोटी मदद बड़ा सहारा बनती है।"],
        "tomorrow": ["मुलाकात में संकेत मिलेगा।", "तुलना करके निर्णय लें।", "नींद में निवेश करें।", "प्राथमिकता तय करें।", "थोड़ा आराम ठीक है।"],
        "annual": ["छोटे सुधार बड़ा परिणाम देंगे।", "मौके लोगों से आते हैं।", "अनावश्यक चीज़ें हटाएँ।", "लगातार प्रयास से ब्रेकथ्रू।", "साल के अंत में स्पष्ट परिणाम।"],
        "love": ["हल्का सा संदेश भेजें।", "जल्दी निष्कर्ष न निकालें।"],
        "money": ["सब्सक्रिप्शन/फिक्स्ड खर्च देखें।", "इम्पल्स खरीद कम करें।"],
        "work": ["एक बार और साझा करें—स्पीड बढ़ेगी।", "बेसिक्स सबसे मजबूत।"],
        "health": ["कैफीन कम रखें।", "हल्की वॉक मदद करेगी।"],
        "tips": ["3 मिनट डेस्क साफ", "10 मिनट वॉक", "1 लाइन खर्च लिखें", "एक काम पूरा करें"],
        "cautions": ["इम्पल्स खरीद", "ओवरवर्क/लेट नाइट", "भावनात्मक उछाल"],
        "colors": ["गोल्ड","रेड","ब्लू","ग्रीन","पर्पल","व्हाइट","ब्लैक"],
        "items": ["गोल्ड एक्सेसरी","लाल वॉलेट","नीला की-रिंग","हरा पौधा","पर्पल पेन","मिनिमल घड़ी"],
    },
}

TAROT = {
    "The Fool": {
        "ko": "새로운 시작, 모험, 순수한 믿음",
        "en": "New beginnings, adventure, innocence",
        "zh": "新的开始、冒险、纯粹的信念",
        "ja": "新しい始まり、冒険、純粋な信頼",
        "ru": "Новые начала, приключение, искренность",
        "hi": "नई शुरुआत, साहसिकता, सरल विश्वास",
    },
    "The Magician": {
        "ko": "창조력, 능력 발휘, 집중",
        "en": "Skill, manifestation, focus",
        "zh": "创造力、能力发挥、专注",
        "ja": "創造力、才能の発揮、集中",
        "ru": "Навык, проявление силы, фокус",
        "hi": "कौशल, क्षमता, एकाग्रता",
    },
    "The High Priestess": {
        "ko": "직감, 내면의 목소리",
        "en": "Intuition, inner voice",
        "zh": "直觉、内在声音",
        "ja": "直感、内なる声",
        "ru": "Интуиция, внутренний голос",
        "hi": "अंतर्ज्ञान, भीतर की आवाज़",
    },
    "The Sun": {
        "ko": "행복, 성공, 긍정 에너지",
        "en": "Joy, success, positivity",
        "zh": "幸福、成功、正能量",
        "ja": "幸福、成功、ポジティブ",
        "ru": "Радость, успех, позитив",
        "hi": "खुशी, सफलता, सकारात्मकता",
    },
    "Wheel of Fortune": {
        "ko": "변화, 운, 사이클",
        "en": "Change, luck, cycles",
        "zh": "变化、运气、周期",
        "ja": "変化、運、サイクル",
        "ru": "Перемены, удача, циклы",
        "hi": "परिवर्तन, भाग्य, चक्र",
    },
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

def get_desc(dic, lang, key):
    # ko/en만 상세 설명, 나머지는 en fallback
    if lang in dic and key in dic[lang]:
        return dic[lang][key]
    return dic.get("en", {}).get(key, "")

def fortune_bank(lang: str):
    return FORTUNE.get(lang, FORTUNE["en"])

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

# =========================================================
# Tests (12 / 16) - 6개 언어 모두 제공
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
        "E": ("사람을 만나면 에너지가 채워진다", "그렇다", "아니다"),
        "S": ("구체적 사실/디테일을 먼저 본다", "그렇다", "아니다"),
        "T": ("결정 시 논리가 감정보다 우선이다", "그렇다", "아니다"),
        "J": ("계획이 있어야 마음이 편하다", "그렇다", "아니다"),
    },
    "en": {
        "E": ("Socializing recharges me", "Yes", "No"),
        "S": ("I notice concrete details first", "Yes", "No"),
        "T": ("Logic comes before feelings in decisions", "Yes", "No"),
        "J": ("I feel comfortable with plans", "Yes", "No"),
    },
    "zh": {
        "E": ("社交会让我充电", "是", "否"),
        "S": ("我会先注意具体细节", "是", "否"),
        "T": ("做决定时逻辑优先", "是", "否"),
        "J": ("有计划会更安心", "是", "否"),
    },
    "ja": {
        "E": ("人と会うと元気になる", "はい", "いいえ"),
        "S": ("具体的な事実や細部を先に見る", "はい", "いいえ"),
        "T": ("決定では論理が感情より優先", "はい", "いいえ"),
        "J": ("計画があると安心する", "はい", "いいえ"),
    },
    "ru": {
        "E": ("Общение меня заряжает", "Да", "Нет"),
        "S": ("Сначала замечаю конкретные детали", "Да", "Нет"),
        "T": ("В решениях логика важнее эмоций", "Да", "Нет"),
        "J": ("С планом мне спокойнее", "Да", "Нет"),
    },
    "hi": {
        "E": ("लोगों से मिलकर ऊर्जा मिलती है", "हाँ", "नहीं"),
        "S": ("मैं पहले ठोस डिटेल देखता/देखती हूँ", "हाँ", "नहीं"),
        "T": ("निर्णय में लॉजिक पहले", "हाँ", "नहीं"),
        "J": ("प्लान होने पर मन शांत रहता है", "हाँ", "नहीं"),
    },
}

# =========================================================
# UI Header
# =========================================================
# Language selector (가려짐 방지: horizontal + 카드 위)
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
# Input Screen
# =========================================================
def input_screen():
    # 한국어 버전에서만 다나눔렌탈 광고 (복구)
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
# Test 12 Screen (form submit = 무반응 해결)
# =========================================================
def test12_screen():
    qs = SIMPLE_12.get(st.session_state.lang, SIMPLE_12["en"])

    st.markdown("<div class='card'><div class='card-title'>MBTI – 12</div><div class='mini'>Submit을 누르면 바로 결과로 넘어갑니다.</div></div>", unsafe_allow_html=True)

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
# Test 16 Screen (form submit = 무반응 해결)
# =========================================================
def test16_screen():
    d = DETAIL_16.get(st.session_state.lang, DETAIL_16["en"])

    st.markdown("<div class='card'><div class='card-title'>MBTI – 16</div><div class='mini'>각 축 4문항씩, 제출하면 결과로 넘어갑니다.</div></div>", unsafe_allow_html=True)

    with st.form("form_test16", clear_on_submit=False):
        scores = {"E":0, "S":0, "T":0, "J":0}
        for axis in ["E","S","T","J"]:
            q, yes, no = d[axis]
            st.markdown(f"**{q}**")
            for i in range(4):
                c = st.radio(f"{i+1}/4", [yes, no], key=f"t16_{st.session_state.lang}_{axis}_{i}")
                scores[axis] += 1 if c == yes else -1
            st.markdown("---")
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

    # 랜덤이지만 "날짜/생일/mbti/언어"로 안정적(새로고침해도 유지)
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

    name = st.session_state.name.strip()
    name_prefix = (name + ("님의" if lang == "ko" else "")) if name else ""

    # 헤더
    st.markdown(
        f"""
<div class="hero">
  <div style="font-size:1.25rem; font-weight:900;">{name_prefix} {mbti}</div>
  <div class="hero-sub">{t["top_combo"]}</div>
</div>
""",
        unsafe_allow_html=True
    )

    # 결과 카드 (HTML 태그 없이 Markdown만)
    z_desc = get_desc(ZODIAC_DESC, lang, zodiac) if zodiac else ""
    m_desc = get_desc(MBTI_DESC, lang, mbti)
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
    st.markdown("</div>", unsafe_allow_html=True)

    # 광고 (한국어만 다나눔렌탈)
    if lang == "ko":
        render_korean_ad(T["ko"])
    else:
        render_reserved_ad(t.get("ad_reserved", "AD"))

    # 타로(정상 작동)
    with st.expander(t["tarot_btn"], expanded=False):
        tarot_key = rng.choice(list(TAROT.keys()))
        tarot_mean = TAROT[tarot_key].get(lang, TAROT[tarot_key]["en"])
        st.markdown("<div class='card' style='text-align:center;'>", unsafe_allow_html=True)
        st.markdown(f"**{t['tarot_title']}**")
        st.markdown(f"### {tarot_key}")
        st.markdown(tarot_mean)
        st.markdown("</div>", unsafe_allow_html=True)

    # 공유 텍스트
    share_text = (
        f"{t['title']}\n"
        f"{name_prefix} {zodiac} / {mbti}\n\n"
        f"{t['today']}: {today_msg}\n"
        f"{t['tomorrow']}: {tomorrow_msg}\n\n"
        f"{t['annual']}: {annual_msg}\n\n"
        f"{t['love']}: {love_msg}\n"
        f"{t['money']}: {money_msg}\n"
        f"{t['work']}: {work_msg}\n"
        f"{t['health']}: {health_msg}\n\n"
        f"{t['luck']}: {t['lucky_color']} {lucky_color} / {t['lucky_item']} {lucky_item} / {t['lucky_num']} {lucky_num}\n"
        f"{t['tip']}: {tip_msg}\n"
        f"{t['caution']}: {caution_msg}\n\n"
        f"{APP_URL}"
    )

    # 공유 버튼 (모바일: 공유창 / PC: 복사)
    share_component(t, share_text)

    # ✅ “입력화면으로” 버튼은 삭제됨 (요청 반영)
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
