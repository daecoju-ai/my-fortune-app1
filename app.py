import streamlit as st
import streamlit.components.v1 as components
from datetime import date, datetime, timedelta
import random
import hashlib

# =========================
# 0) Page
# =========================
st.set_page_config(page_title="2026 Fortune × MBTI", layout="centered", initial_sidebar_state="collapsed")

# =========================
# 1) Languages (6)
# =========================
LANGS = [
    ("한국어", "ko"),
    ("English", "en"),
    ("中文", "zh"),
    ("日本語", "ja"),
    ("Русский", "ru"),
    ("हिन्दी", "hi"),
]

# =========================
# 2) UI Text
# =========================
T = {
    "ko": {
        "lang_label": "언어 / Language",
        "title": "2026 띠 + MBTI + 사주 + 오늘/내일 운세",
        "caption": "완전 무료",
        "input_title": "정보 입력",
        "name_ph": "이름 입력 (결과에 표시돼요)",
        "birth": "생년월일 입력",
        "mbti_mode": "MBTI 어떻게 할까?",
        "direct": "직접 입력",
        "simple": "간단 테스트 (12문항)",
        "detail": "상세 테스트 (16문항)",
        "mbti_label": "MBTI 선택",
        "btn_result": "운세 보기!",
        "btn_back": "입력 화면으로",
        "btn_reset": "처음부터 다시 하기",
        "share_btn": "친구에게 결과 공유하기",
        "share_help": "모바일: 시스템 공유창 / PC: 복사",
        "share_title": "내 운세 결과 공유",
        "share_fallback": "공유 기능이 없어 텍스트를 복사했어요.",
        "copied": "복사 완료! 카톡/메시지에 붙여넣기 해주세요.",
        "tarot_btn": "오늘의 타로 카드 보기",
        "tarot_title": "오늘의 타로 카드",
        "top_combo": "최고 조합!",
        "zodiac_title": "띠 운세",
        "mbti_title": "MBTI 특징",
        "saju_title": "사주 한 마디",
        "today_title": "오늘 운세",
        "tomorrow_title": "내일 운세",
        "annual_title": "2026 전체 운세",
        "love_title": "연애운",
        "money_title": "재물운",
        "work_title": "일/학업운",
        "health_title": "건강운",
        "tip_title": "팁",
        "caution_title": "주의",
        "luck_title": "행운 포인트",
        "lucky_color_title": "럭키 컬러",
        "lucky_item_title": "럭키 아이템",
        "lucky_num_title": "럭키 넘버",
        "err_birth": "생년월일이 올바르지 않아요. 날짜를 다시 확인해 주세요!",
        "err_year": "생년은 1900~2030년 사이로 입력해주세요!",
        "test_help": "질문에 답하면 MBTI가 자동 계산됩니다.",
        "ad_badge": "광고",
        "ad_title": "정수기렌탈 궁금할 때?",
        "ad_desc": "다나눔렌탈 제휴카드 시 월 0원부터 + 설치당일 최대 현금50만원 페이백!",
        "ad_btn": "보러가기",
        "ad_url": "https://www.다나눔렌탈.com",
        "ad_reserved": "AD (승인 후 이 위치에 광고가 표시됩니다)",
    },
    "en": {
        "lang_label": "Language",
        "title": "2026 Zodiac + MBTI + Fortune (Today/Tomorrow)",
        "caption": "Completely Free",
        "input_title": "Input",
        "name_ph": "Enter name (optional)",
        "birth": "Birth date",
        "mbti_mode": "MBTI method",
        "direct": "Direct input",
        "simple": "Quick test (12)",
        "detail": "Detailed test (16)",
        "mbti_label": "Choose MBTI",
        "btn_result": "View Fortune!",
        "btn_back": "Back to input",
        "btn_reset": "Start over",
        "share_btn": "Share with friends",
        "share_help": "Mobile: Share sheet / Desktop: Copy",
        "share_title": "Share my fortune",
        "share_fallback": "Share isn't supported here. Copied text instead.",
        "copied": "Copied! Paste into chat.",
        "tarot_btn": "Draw today's tarot",
        "tarot_title": "Today's Tarot",
        "top_combo": "Best Combo!",
        "zodiac_title": "Zodiac fortune",
        "mbti_title": "MBTI traits",
        "saju_title": "Fortune line",
        "today_title": "Today",
        "tomorrow_title": "Tomorrow",
        "annual_title": "2026 Overall",
        "love_title": "Love",
        "money_title": "Money",
        "work_title": "Work/Study",
        "health_title": "Health",
        "tip_title": "Tip",
        "caution_title": "Caution",
        "luck_title": "Lucky points",
        "lucky_color_title": "Lucky color",
        "lucky_item_title": "Lucky item",
        "lucky_num_title": "Lucky number",
        "err_birth": "Invalid birth date. Please check again!",
        "err_year": "Birth year must be between 1900 and 2030!",
        "test_help": "Answer questions and we calculate your MBTI.",
        "ad_badge": "AD",
        "ad_title": "Ad space",
        "ad_desc": "Reserved for AdSense / sponsors",
        "ad_btn": "Open",
        "ad_url": "https://example.com",
        "ad_reserved": "AD (This area will display ads after approval)",
    },
    "zh": {
        "lang_label": "语言",
        "title": "2026 运势：生肖 + MBTI + 今日/明日",
        "caption": "完全免费",
        "input_title": "输入",
        "name_ph": "姓名（可选）",
        "birth": "生日",
        "mbti_mode": "MBTI 方式",
        "direct": "直接输入",
        "simple": "简易测试（12题）",
        "detail": "详细测试（16题）",
        "mbti_label": "选择 MBTI",
        "btn_result": "查看运势！",
        "btn_back": "返回输入",
        "btn_reset": "重新开始",
        "share_btn": "分享给朋友",
        "share_help": "手机：系统分享 / 电脑：复制",
        "share_title": "分享我的结果",
        "share_fallback": "当前环境不支持分享，已复制文本。",
        "copied": "已复制！可粘贴到聊天应用。",
        "tarot_btn": "抽取今日塔罗",
        "tarot_title": "今日塔罗",
        "top_combo": "最佳组合！",
        "zodiac_title": "生肖运势",
        "mbti_title": "MBTI 特点",
        "saju_title": "一句话",
        "today_title": "今日",
        "tomorrow_title": "明日",
        "annual_title": "2026 总运",
        "love_title": "恋爱运",
        "money_title": "财运",
        "work_title": "事业/学业",
        "health_title": "健康运",
        "tip_title": "建议",
        "caution_title": "注意",
        "luck_title": "幸运点",
        "lucky_color_title": "幸运色",
        "lucky_item_title": "幸运物",
        "lucky_num_title": "幸运数字",
        "err_birth": "生日不正确，请重新检查！",
        "err_year": "出生年份需在 1900~2030 之间！",
        "test_help": "回答问题后自动计算 MBTI。",
        "ad_badge": "AD",
        "ad_title": "广告位",
        "ad_desc": "用于 AdSense / 赞助",
        "ad_btn": "打开",
        "ad_url": "https://example.com",
        "ad_reserved": "AD（审核通过后此处显示广告）",
    },
    "ja": {
        "lang_label": "言語",
        "title": "2026 運勢：干支 + MBTI + 今日/明日",
        "caption": "完全無料",
        "input_title": "入力",
        "name_ph": "名前（任意）",
        "birth": "生年月日",
        "mbti_mode": "MBTI の方法",
        "direct": "直接入力",
        "simple": "簡単テスト（12問）",
        "detail": "詳細テスト（16問）",
        "mbti_label": "MBTI を選択",
        "btn_result": "運勢を見る！",
        "btn_back": "入力へ戻る",
        "btn_reset": "最初から",
        "share_btn": "友だちに共有",
        "share_help": "スマホ：共有 / PC：コピー",
        "share_title": "結果を共有",
        "share_fallback": "共有が使えないため、テキストをコピーしました。",
        "copied": "コピー完了！貼り付けてください。",
        "tarot_btn": "今日のタロット",
        "tarot_title": "今日のタロット",
        "top_combo": "最高の組み合わせ！",
        "zodiac_title": "干支運勢",
        "mbti_title": "MBTI 特徴",
        "saju_title": "一言",
        "today_title": "今日",
        "tomorrow_title": "明日",
        "annual_title": "2026 総合運",
        "love_title": "恋愛運",
        "money_title": "金運",
        "work_title": "仕事/学業",
        "health_title": "健康運",
        "tip_title": "ヒント",
        "caution_title": "注意",
        "luck_title": "ラッキーポイント",
        "lucky_color_title": "ラッキーカラー",
        "lucky_item_title": "ラッキーアイテム",
        "lucky_num_title": "ラッキーナンバー",
        "err_birth": "生年月日が正しくありません。確認してください！",
        "err_year": "1900〜2030年の範囲で入力してください！",
        "test_help": "質問に答えるとMBTIを自動計算します。",
        "ad_badge": "AD",
        "ad_title": "広告枠",
        "ad_desc": "AdSense / スポンサー用",
        "ad_btn": "開く",
        "ad_url": "https://example.com",
        "ad_reserved": "AD（承認後ここに広告が表示されます）",
    },
    "ru": {
        "lang_label": "Язык",
        "title": "Удача 2026: Зодиак + MBTI + Сегодня/Завтра",
        "caption": "Бесплатно",
        "input_title": "Ввод",
        "name_ph": "Имя (необязательно)",
        "birth": "Дата рождения",
        "mbti_mode": "Способ MBTI",
        "direct": "Ввести вручную",
        "simple": "Быстрый тест (12)",
        "detail": "Подробный тест (16)",
        "mbti_label": "Выберите MBTI",
        "btn_result": "Показать результат!",
        "btn_back": "Назад",
        "btn_reset": "Сначала",
        "share_btn": "Поделиться",
        "share_help": "Телефон: поделиться / ПК: копировать",
        "share_title": "Поделиться результатом",
        "share_fallback": "Поделиться нельзя — скопировали текст.",
        "copied": "Скопировано! Вставьте в чат.",
        "tarot_btn": "Таро дня",
        "tarot_title": "Таро дня",
        "top_combo": "Лучшее сочетание!",
        "zodiac_title": "Зодиак",
        "mbti_title": "MBTI",
        "saju_title": "Фраза",
        "today_title": "Сегодня",
        "tomorrow_title": "Завтра",
        "annual_title": "Итог 2026",
        "love_title": "Любовь",
        "money_title": "Деньги",
        "work_title": "Работа/Учёба",
        "health_title": "Здоровье",
        "tip_title": "Совет",
        "caution_title": "Осторожно",
        "luck_title": "Счастливые пункты",
        "lucky_color_title": "Цвет",
        "lucky_item_title": "Талисман",
        "lucky_num_title": "Число",
        "err_birth": "Неверная дата рождения. Проверьте!",
        "err_year": "Год рождения должен быть 1900–2030!",
        "test_help": "Ответьте на вопросы — мы вычислим MBTI.",
        "ad_badge": "AD",
        "ad_title": "Рекламное место",
        "ad_desc": "Для AdSense / спонсоров",
        "ad_btn": "Открыть",
        "ad_url": "https://example.com",
        "ad_reserved": "AD (после одобрения здесь будет реклама)",
    },
    "hi": {
        "lang_label": "भाषा",
        "title": "2026 भाग्य: राशि + MBTI + आज/कल",
        "caption": "पूरी तरह मुफ्त",
        "input_title": "इनपुट",
        "name_ph": "नाम (वैकल्पिक)",
        "birth": "जन्मतिथि",
        "mbti_mode": "MBTI तरीका",
        "direct": "सीधा 입력",
        "simple": "त्वरित टेस्ट (12)",
        "detail": "विस्तृत टेस्ट (16)",
        "mbti_label": "MBTI चुनें",
        "btn_result": "परिणाम देखें!",
        "btn_back": "वापस",
        "btn_reset": "फिर से शुरू",
        "share_btn": "दोस्तों को शेयर करें",
        "share_help": "मोबाइल: शेयर / PC: कॉपी",
        "share_title": "मेरा परिणाम शेयर",
        "share_fallback": "यहाँ शेयर सपोर्ट नहीं है, टेक्स्ट कॉपी किया।",
        "copied": "कॉपी हो गया! चैट में पेस्ट करें।",
        "tarot_btn": "आज का टैरो",
        "tarot_title": "आज का टैरो",
        "top_combo": "सबसे अच्छा कॉम्बो!",
        "zodiac_title": "राशि",
        "mbti_title": "MBTI",
        "saju_title": "एक लाइन",
        "today_title": "आज",
        "tomorrow_title": "कल",
        "annual_title": "2026 कुल",
        "love_title": "प्रेम",
        "money_title": "धन",
        "work_title": "कार्य/पढ़ाई",
        "health_title": "स्वास्थ्य",
        "tip_title": "टिप",
        "caution_title": "सावधानी",
        "luck_title": "लकी पॉइंट्स",
        "lucky_color_title": "रंग",
        "lucky_item_title": "आइटम",
        "lucky_num_title": "नंबर",
        "err_birth": "जन्मतिथि गलत है। कृपया जाँचें!",
        "err_year": "वर्ष 1900–2030 के बीच होना चाहिए!",
        "test_help": "प्रश्नों के उत्तर दें, MBTI स्वतः निकलेगा।",
        "ad_badge": "AD",
        "ad_title": "विज्ञापन स्थान",
        "ad_desc": "AdSense / स्पॉन्सर हेतु",
        "ad_btn": "खोलें",
        "ad_url": "https://example.com",
        "ad_reserved": "AD (स्वीकृति के बाद यहाँ विज्ञापन दिखेगा)",
    },
}

# =========================
# 3) MBTI / Tests
# =========================
MBTI_TYPES = [
    "INTJ","INTP","ENTJ","ENTP",
    "INFJ","INFP","ENFJ","ENFP",
    "ISTJ","ISFJ","ESTJ","ESFJ",
    "ISTP","ISFP","ESTP","ESFP"
]

SIMPLE_12 = {
    "ko": [
        ("주말에 친구가 갑자기 '놀자!' 하면?", "좋아! 나감", "집에서 쉬고 싶어", "EI", "E"),
        ("모임에서 처음 본 사람들과 대화", "재밌고 신나", "부담되고 피곤", "EI", "E"),
        ("하루 종일 사람 만난 후", "아직 에너지 남음", "혼자 있고 싶음", "EI", "E"),
        ("생각이 떠오르면", "말로 풀어냄", "머릿속 정리", "EI", "E"),
        ("새 카페 가면 먼저 보는 건", "메뉴/가격", "분위기/컨셉", "SN", "S"),
        ("책/영화 볼 때", "디테일/전개", "상징/의미", "SN", "S"),
        ("쇼핑할 때", "필요한 것 바로", "미래 조합 상상", "SN", "S"),
        ("의견 충돌 시", "논리/팩트", "배려/조율", "TF", "T"),
        ("누가 울면서 상담", "해결책 제시", "공감 먼저", "TF", "T"),
        ("친구가 늦어서 화날 때", "바로 지적", "부드럽게 말함", "TF", "T"),
        ("여행은", "계획대로", "즉흥으로", "JP", "J"),
        ("마감 앞두면", "미리미리", "막판 몰아서", "JP", "J"),
    ],
    "en": [
        ("Friends suddenly ask to hang out?", "Go out!", "Stay home", "EI", "E"),
        ("Talking to strangers at a party", "Fun", "Tiring", "EI", "E"),
        ("After meeting people all day", "Still energized", "Need alone time", "EI", "E"),
        ("When an idea comes", "Say it out", "Think first", "EI", "E"),
        ("At a new cafe you notice", "Menu/prices", "Vibe/concept", "SN", "S"),
        ("When watching a movie", "Details/plot", "Symbols/meaning", "SN", "S"),
        ("When shopping", "Buy needed items", "Imagine combinations", "SN", "S"),
        ("When opinions clash", "Logic/facts", "Harmony/care", "TF", "T"),
        ("When someone cries", "Give solutions", "Empathize first", "TF", "T"),
        ("When friend is late", "Point it out", "Say gently", "TF", "T"),
        ("Travel style", "Planned", "Spontaneous", "JP", "J"),
        ("Before a deadline", "Finish early", "Last minute", "JP", "J"),
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
}

# =========================
# 4) Fortune Data (ko/en rich, other fallback to en)
# =========================
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
            "Keep direction and you’ll see clear results near year-end.",
        ],
        "love": ["Send a light check-in first.", "Don’t rush conclusions—keep it warm."],
        "money": ["Stop leaks (subscriptions/fixed costs) first.", "Avoid impulse buys and money luck rises."],
        "work": ["Share one more update—things speed up.", "Win with fundamentals—your usual method works."],
        "health": ["Avoid too much caffeine and you’ll feel better.", "Light cardio boosts mood and luck."],
        "tips": ["Finish one thing", "10-min walk", "Write one expense line", "Reach out first"],
        "cautions": ["Avoid impulse shopping", "Reduce overwork", "Watch emotional spikes"],
        "colors": ["Gold","Red","Blue","Green","Purple","White","Black"],
        "items": ["Golden accessory","Red wallet","Blue keyring","Green plant","Purple pen","Minimal watch"],
    }
}

TAROT = {
    "The Fool": {"ko": "새로운 시작, 모험, 순수한 믿음", "en": "New beginnings, adventure, innocence"},
    "The Magician": {"ko": "창조력, 능력 발휘, 집중", "en": "Skill, manifestation, focus"},
    "The High Priestess": {"ko": "직감, 내면의 목소리", "en": "Intuition, inner voice"},
    "The Sun": {"ko": "행복, 성공, 긍정 에너지", "en": "Joy, success, positivity"},
    "Wheel of Fortune": {"ko": "변화, 운, 사이클", "en": "Change, luck, cycles"},
}

APP_URL = "https://my-fortune.streamlit.app"

# =========================
# Helpers
# =========================
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
    if lang in dic and key in dic[lang]:
        return dic[lang][key]
    # fallback en
    return dic["en"].get(key, "")

def bank(lang):
    if lang in FORTUNE:
        return FORTUNE[lang]
    return FORTUNE["en"]

def compute_mbti_simple(lang: str):
    qs = SIMPLE_12.get(lang, SIMPLE_12["en"])
    ei = sn = tf = jp = 0
    for i, (q, a, b, dim, a_side) in enumerate(qs):
        choice = st.radio(q, [a, b], key=f"simple_{lang}_{i}")
        pick_a = (choice == a)

        if dim == "EI":
            ei += 1 if pick_a else -1  # a=E
        elif dim == "SN":
            sn += 1 if pick_a else -1  # a=S
        elif dim == "TF":
            tf += 1 if pick_a else -1  # a=T
        elif dim == "JP":
            jp += 1 if pick_a else -1  # a=J

    return ("E" if ei >= 0 else "I") + ("S" if sn >= 0 else "N") + ("T" if tf >= 0 else "F") + ("J" if jp >= 0 else "P")

def compute_mbti_detail(lang: str):
    d = DETAIL_16.get(lang, DETAIL_16["en"])
    ei = sn = tf = jp = 0

    for axis in ["E", "S", "T", "J"]:
        q, yes, no = d[axis]
        for i in range(4):
            c = st.radio(f"{q} ({i+1}/4)", [yes, no], key=f"detail_{lang}_{axis}_{i}")
            pick_yes = (c == yes)
            if axis == "E": ei += 1 if pick_yes else -1
            if axis == "S": sn += 1 if pick_yes else -1
            if axis == "T": tf += 1 if pick_yes else -1
            if axis == "J": jp += 1 if pick_yes else -1

    return ("E" if ei >= 0 else "I") + ("S" if sn >= 0 else "N") + ("T" if tf >= 0 else "F") + ("J" if jp >= 0 else "P")

def render_reserved_ad(t):
    st.markdown(
        f"""
        <div style="border:2px dashed rgba(160,120,220,0.55); border-radius:18px; padding:12px; text-align:center; margin:12px 0;">
          <div style="font-weight:900; font-size:12px; letter-spacing:0.08em; opacity:0.8;">AD</div>
          <div style="opacity:0.8; font-size:13px; margin-top:4px;">{t["ad_reserved"]}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_korean_ad(t):
    st.markdown(
        f"""
        <div style="background:#fffbe6; padding:18px; border-radius:20px; text-align:center; margin:14px 0;
                    border:2px solid rgba(230,126,34,0.35);">
          <div style="display:inline-block; padding:4px 10px; border-radius:999px;
                      background:rgba(231,76,60,0.10); color:#e74c3c; font-weight:900; font-size:12px; border:1px solid rgba(231,76,60,0.25);">
            {t["ad_badge"]}
          </div>
          <h3 style="color:#d35400; margin:10px 0 6px 0;">{t["ad_title"]}</h3>
          <div style="font-size:14px; line-height:1.6; color:#222;">{t["ad_desc"]}</div>
          <a href="{t["ad_url"]}" target="_blank" style="text-decoration:none;">
            <button style="margin-top:12px; background:#e67e22; color:white; padding:12px 22px; border:none; border-radius:999px; font-weight:900; cursor:pointer;">
              {t["ad_btn"]}
            </button>
          </a>
        </div>
        """,
        unsafe_allow_html=True
    )

def share_button(t, share_text: str):
    payload = share_text.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
    components.html(
        f"""
        <div style="text-align:center; margin: 14px 0 6px 0;">
          <button id="shareBtn"
            style="background:#6d28d9; color:white; padding:14px 18px; border:none; border-radius:999px;
                   font-size:16px; font-weight:900; box-shadow:0 10px 24px rgba(109,40,217,0.28); cursor:pointer; width:100%;">
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
                alert("{t['share_fallback']}\\n{t['copied']}");
              }}
            }} catch(e) {{
              try {{
                await navigator.clipboard.writeText(text);
                alert("{t['share_fallback']}\\n{t['copied']}");
              }} catch(_) {{
                alert("{t['share_fallback']}");
              }}
            }}
          }}

          btn.addEventListener("click", doShare);
        </script>
        """,
        height=120
    )

# =========================
# CSS (모바일 상단/레이아웃)
# =========================
st.markdown("""
<style>
header, footer {visibility:hidden;}
.block-container {padding-top:0.7rem; padding-bottom:2rem; max-width:820px;}
html, body, [class*="css"] {font-family: system-ui, -apple-system, "Noto Sans KR", "Segoe UI", Arial, sans-serif;}
.bg {
  background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 50%, #8ec5fc 100%);
  border-radius: 24px;
  padding: 14px;
  margin-top: 6px;
  color: white;
  text-align:center;
  text-shadow:0 2px 10px rgba(0,0,0,0.25);
}
.card {
  background: rgba(255,255,255,0.96);
  border-radius: 22px;
  padding: 16px 16px;
  box-shadow: 0 10px 28px rgba(0,0,0,0.12);
  border: 1px solid rgba(140, 120, 180, 0.18);
}
.h1 {font-size: 1.85rem; font-weight: 900; margin: 0;}
.small {opacity:0.86; font-size: 0.95rem; margin-top:6px;}
</style>
""", unsafe_allow_html=True)

# =========================
# Session State
# =========================
if "lang" not in st.session_state:
    st.session_state.lang = "ko"
if "step" not in st.session_state:
    st.session_state.step = "input"
if "name" not in st.session_state:
    st.session_state.name = ""
if "y" not in st.session_state:
    st.session_state.y = 2005
if "m" not in st.session_state:
    st.session_state.m = 1
if "d" not in st.session_state:
    st.session_state.d = 1
if "mode" not in st.session_state:
    st.session_state.mode = "direct"  # direct/simple/detail
if "mbti" not in st.session_state:
    st.session_state.mbti = "ENFJ"

# =========================
# Language UI
# =========================
labels = [x[0] for x in LANGS]
codes = [x[1] for x in LANGS]
cur_idx = codes.index(st.session_state.lang) if st.session_state.lang in codes else 0
sel = st.radio(T["ko"]["lang_label"], labels, index=cur_idx, horizontal=True)
st.session_state.lang = codes[labels.index(sel)]
t = T[st.session_state.lang]

# =========================
# Header
# =========================
st.markdown(f"""
<div class="bg">
  <div class="h1">{t["title"]}</div>
  <div class="small">{t["caption"]}</div>
</div>
""", unsafe_allow_html=True)

render_reserved_ad(t)

# =========================
# INPUT
# =========================
if st.session_state.step == "input":
    if st.session_state.lang == "ko":
        render_korean_ad(t)

    st.markdown(f"<div class='card'><b>{t['input_title']}</b></div>", unsafe_allow_html=True)
    st.session_state.name = st.text_input(t["name_ph"], value=st.session_state.name)

    st.markdown(f"**{t['birth']}**")
    c1, c2, c3 = st.columns(3)
    st.session_state.y = int(c1.number_input("Year" if st.session_state.lang != "ko" else "년", min_value=1900, max_value=2030, value=int(st.session_state.y), step=1))
    st.session_state.m = int(c2.number_input("Month" if st.session_state.lang != "ko" else "월", min_value=1, max_value=12, value=int(st.session_state.m), step=1))
    st.session_state.d = int(c3.number_input("Day" if st.session_state.lang != "ko" else "일", min_value=1, max_value=31, value=int(st.session_state.d), step=1))

    mode_label = st.radio(
        t["mbti_mode"],
        [t["direct"], t["simple"], t["detail"]],
        index=0 if st.session_state.mode == "direct" else (1 if st.session_state.mode == "simple" else 2),
    )

    # mode 저장
    if mode_label == t["direct"]:
        st.session_state.mode = "direct"
    elif mode_label == t["simple"]:
        st.session_state.mode = "simple"
    else:
        st.session_state.mode = "detail"

    # MBTI 입력/테스트 (form 밖이라 즉시 반응)
    if st.session_state.mode == "direct":
        st.session_state.mbti = st.selectbox(t["mbti_label"], MBTI_TYPES, index=MBTI_TYPES.index(st.session_state.mbti) if st.session_state.mbti in MBTI_TYPES else 0)

    elif st.session_state.mode == "simple":
        st.caption(t["test_help"])
        test_lang = st.session_state.lang if st.session_state.lang in SIMPLE_12 else "en"
        st.session_state.mbti = compute_mbti_simple(test_lang)
        st.info(f"MBTI: **{st.session_state.mbti}**")

    else:
        st.caption(t["test_help"])
        test_lang = st.session_state.lang if st.session_state.lang in DETAIL_16 else "en"
        st.session_state.mbti = compute_mbti_detail(test_lang)
        st.info(f"MBTI: **{st.session_state.mbti}**")

    # 운세 보기
    if st.button(t["btn_result"], use_container_width=True):
        if not (1900 <= st.session_state.y <= 2030):
            st.error(t["err_year"])
        elif not validate_birth(st.session_state.y, st.session_state.m, st.session_state.d):
            st.error(t["err_birth"])
        else:
            st.session_state.step = "result"
            st.rerun()

# =========================
# RESULT
# =========================
if st.session_state.step == "result":
    y, m, d = st.session_state.y, st.session_state.m, st.session_state.d

    if not (1900 <= y <= 2030):
        st.error(t["err_year"])
    elif not validate_birth(y, m, d):
        st.error(t["err_birth"])
    else:
        lang = st.session_state.lang
        mbti = st.session_state.mbti

        zodiac = get_zodiac(y, lang)
        if zodiac is None:
            st.error(t["err_year"])
        else:
            today_key = datetime.now().strftime("%Y%m%d")
            seed = stable_seed(lang, y, m, d, mbti, today_key)
            rng = random.Random(seed)

            b = bank(lang)
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

            # 상단 배너
            st.markdown(f"""
            <div class="bg">
              <div style="font-size:1.15rem; font-weight:900;">{name_prefix} {mbti}</div>
              <div class="small">{t["top_combo"]}</div>
            </div>
            """, unsafe_allow_html=True)

            # 결과 카드 (HTML 태그 사용 안 함 => 태그 깨짐 방지)
            z_desc = get_desc(ZODIAC_DESC, lang, zodiac)
            m_desc = get_desc(MBTI_DESC, lang, mbti)

            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown(
                f"""
**{t["zodiac_title"]}**: {z_desc}  
**{t["mbti_title"]}**: {m_desc}  
**{t["saju_title"]}**: {("오행 균형 → 무리하지 않으면 전반적으로 대길!" if lang=="ko" else "Balanced elements → overall good if you avoid overdoing.")}

**{t["today_title"]}**: {today_msg}  
**{t["tomorrow_title"]}**: {tomorrow_msg}

**{t["annual_title"]}**: {annual_msg}

**{t["love_title"]}**: {love_msg}  
**{t["money_title"]}**: {money_msg}  
**{t["work_title"]}**: {work_msg}  
**{t["health_title"]}**: {health_msg}

**{t["luck_title"]}**: {t["lucky_color_title"]} **{lucky_color}** · {t["lucky_item_title"]} **{lucky_item}** · {t["lucky_num_title"]} **{lucky_num}**  
**{t["tip_title"]}**: {tip_msg}  
**{t["caution_title"]}**: {caution_msg}
                """
            )
            st.markdown("</div>", unsafe_allow_html=True)

            # 한국어에서만 광고
            if lang == "ko":
                render_korean_ad(T["ko"])
            else:
                render_reserved_ad(t)

            # 타로
            with st.expander(t["tarot_btn"], expanded=False):
                tarot_key = rng.choice(list(TAROT.keys()))
                tarot_mean = TAROT[tarot_key].get(lang, TAROT[tarot_key]["en"])
                st.markdown(f"<div class='card' style='text-align:center;'>", unsafe_allow_html=True)
                st.markdown(f"**{t['tarot_title']}**")
                st.markdown(f"### {tarot_key}")
                st.markdown(tarot_mean)
                st.markdown("</div>", unsafe_allow_html=True)

            # 공유 텍스트 (이모지/HTML 제거)
            share_text = (
                f"{t['title']}\n"
                f"{name_prefix} {zodiac} / {mbti}\n\n"
                f"{t['today_title']}: {today_msg}\n"
                f"{t['tomorrow_title']}: {tomorrow_msg}\n\n"
                f"{t['annual_title']}: {annual_msg}\n\n"
                f"{t['love_title']}: {love_msg}\n"
                f"{t['money_title']}: {money_msg}\n"
                f"{t['work_title']}: {work_msg}\n"
                f"{t['health_title']}: {health_msg}\n\n"
                f"{t['luck_title']}: {t['lucky_color_title']} {lucky_color} / {t['lucky_item_title']} {lucky_item} / {t['lucky_num_title']} {lucky_num}\n"
                f"{t['tip_title']}: {tip_msg}\n"
                f"{t['caution_title']}: {caution_msg}\n\n"
                f"{APP_URL}"
            )
            share_button(t, share_text)

            # 버튼들
            cA, cB = st.columns(2)
            with cA:
                if st.button(t["btn_back"], use_container_width=True):
                    st.session_state.step = "input"
                    st.rerun()
            with cB:
                if st.button(t["btn_reset"], use_container_width=True):
                    keep_lang = st.session_state.lang
                    st.session_state.clear()
                    st.session_state.lang = keep_lang
                    st.session_state.step = "input"
                    st.session_state.name = ""
                    st.session_state.y = 2005
                    st.session_state.m = 1
                    st.session_state.d = 1
                    st.session_state.mode = "direct"
                    st.session_state.mbti = "ENFJ"
                    st.rerun()
