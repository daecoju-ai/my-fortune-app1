import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, timedelta
import random

# =========================
# 1) 언어 목록 (id 제거)
# =========================
LANGS = [
    ("ko", "한국어"),
    ("en", "English"),
    ("ja", "日本語"),
    ("zh", "中文"),
    ("ru", "Русский"),
    ("hi", "हिन्दी"),
]

# =========================
# 2) UI 텍스트 i18n (부족하면 EN fallback)
# =========================
I18N = {
    "ko": {
        "lang_label": "언어 / Language",
        "title": "2026 띠 + MBTI + 사주 + 오늘/내일 운세",
        "caption": "완전 무료",
        "name_placeholder": "이름 입력 (결과에 표시돼요)",
        "birth_title": "### 생년월일 입력",
        "mbti_mode": "MBTI 어떻게 할까?",
        "direct": "직접 입력",
        "test16": "상세 테스트 (16문제)",
        "test_start": "상세 테스트 시작! 하나씩 답해주세요",
        "energy": "에너지 방향",
        "info": "정보 수집",
        "decision": "결정 방식",
        "life": "생활 방식",
        "result_btn": "결과 보기!",
        "fortune_btn": "2026년 운세 보기!",
        "reset": "처음부터 다시하기",
        "share_btn": "친구에게 결과 공유하기",
        "share_hint": "모바일에서는 공유창(카톡/문자 등)이 뜹니다. PC에서는 복사로 동작할 수 있어요.",
        "tarot_btn": "오늘의 타로 카드 보기",
        "tarot_title": "오늘의 타로 카드",
        "zodiac_title": "띠 운세",
        "mbti_title": "MBTI 특징",
        "saju_title": "사주 한 마디",
        "today_title": "오늘 운세",
        "tomorrow_title": "내일 운세",
        "combo": "최고 조합!",
        "overall_title": "2026 전체 운세",
        "combo_title": "조합 한 마디",
        "lucky_color_title": "럭키 컬러",
        "lucky_item_title": "럭키 아이템",
        "tip_title": "팁",
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
        "copy_fallback": "공유가 안 되면 아래 텍스트를 복사해서 보내세요.",
    },
    "en": {
        "lang_label": "Language",
        "title": "2026 Zodiac + MBTI + Fortune (Today/Tomorrow)",
        "caption": "Completely Free",
        "name_placeholder": "Enter name (shown in result)",
        "birth_title": "### Enter Birth Date",
        "mbti_mode": "How to do MBTI?",
        "direct": "Direct input",
        "test16": "Detailed test (16 questions)",
        "test_start": "Detailed test start! Please answer one by one",
        "energy": "Energy Direction",
        "info": "Information Gathering",
        "decision": "Decision Making",
        "life": "Lifestyle",
        "result_btn": "View Result!",
        "fortune_btn": "View 2026 Fortune!",
        "reset": "Start Over",
        "share_btn": "Share with friends",
        "share_hint": "On mobile, the share sheet should open. On PC it may copy instead.",
        "tarot_btn": "See Today's Tarot",
        "tarot_title": "Today's Tarot",
        "zodiac_title": "Zodiac Fortune",
        "mbti_title": "MBTI Traits",
        "saju_title": "Fortune Comment",
        "today_title": "Today's Luck",
        "tomorrow_title": "Tomorrow's Luck",
        "combo": "Best Combo!",
        "overall_title": "2026 Annual Luck",
        "combo_title": "Combination Meaning",
        "lucky_color_title": "Lucky Color",
        "lucky_item_title": "Lucky Item",
        "tip_title": "Tip",
        "ad_slot_label": "AD",
        "ad_slot_sub": "(Ads will appear here after approval)",
        "year": "Year", "month": "Month", "day": "Day",
        "invalid_year": "Please enter a birth year between 1900 and 2030!",
        "mbti_select": "Select MBTI",
        "copy_fallback": "If share doesn't work, copy the text below and send it.",
    },
    "ja": {
        "lang_label": "言語 / Language",
        "title": "2026 干支 + MBTI + 運勢（今日/明日）",
        "caption": "完全無料",
        "name_placeholder": "名前（結果に表示）",
        "birth_title": "### 生年月日",
        "mbti_mode": "MBTI は？",
        "direct": "直接選択",
        "test16": "詳細テスト（16問）",
        "test_start": "詳細テスト開始！順番に答えてください",
        "energy": "エネルギーの方向",
        "info": "情報の集め方",
        "decision": "意思決定",
        "life": "生活スタイル",
        "result_btn": "結果を見る！",
        "fortune_btn": "2026年の運勢を見る！",
        "reset": "最初から",
        "share_btn": "友達に結果を共有",
        "share_hint": "モバイルでは共有画面が開きます。PCはコピーになる場合があります。",
        "tarot_btn": "今日のタロットを見る",
        "tarot_title": "今日のタロット",
        "today_title": "今日の運勢",
        "tomorrow_title": "明日の運勢",
        "year": "年", "month": "月", "day": "日",
        "invalid_year": "1900〜2030の間で入力してください。",
        "mbti_select": "MBTI を選択",
        "copy_fallback": "共有できない場合は、下のテキストをコピーして送ってください。",
    },
    "zh": {
        "lang_label": "语言 / Language",
        "title": "2026 生肖 + MBTI + 运势（今天/明天）",
        "caption": "完全免费",
        "name_placeholder": "输入姓名（显示在结果中）",
        "birth_title": "### 输入生日",
        "mbti_mode": "MBTI 怎么做？",
        "direct": "直接选择",
        "test16": "详细测试（16题）",
        "test_start": "开始详细测试！请依次回答",
        "energy": "精力方向",
        "info": "信息获取",
        "decision": "决策方式",
        "life": "生活方式",
        "result_btn": "查看结果！",
        "fortune_btn": "查看2026运势！",
        "reset": "重新开始",
        "share_btn": "分享给朋友",
        "share_hint": "手机会弹出分享面板；电脑可能改为复制。",
        "tarot_btn": "抽取今日塔罗",
        "tarot_title": "今日塔罗",
        "today_title": "今天运势",
        "tomorrow_title": "明天运势",
        "year": "年", "month": "月", "day": "日",
        "invalid_year": "请输入1900到2030之间的年份。",
        "mbti_select": "选择 MBTI",
        "copy_fallback": "若分享无反应，请复制下方文本发送。",
    },
    "ru": {
        "lang_label": "Язык / Language",
        "title": "2026 Зодиак + MBTI + Удача (Сегодня/Завтра)",
        "caption": "Бесплатно",
        "name_placeholder": "Имя (в результате)",
        "birth_title": "### Дата рождения",
        "mbti_mode": "Как выбрать MBTI?",
        "direct": "Выбрать вручную",
        "test16": "Тест (16 вопросов)",
        "test_start": "Начинаем тест! Ответьте по порядку",
        "energy": "Направление энергии",
        "info": "Сбор информации",
        "decision": "Принятие решений",
        "life": "Стиль жизни",
        "result_btn": "Показать результат!",
        "fortune_btn": "Показать удачу 2026!",
        "reset": "Сначала",
        "share_btn": "Поделиться с друзьями",
        "share_hint": "На телефоне откроется панель «Поделиться». На ПК может копировать.",
        "tarot_btn": "Таро на сегодня",
        "tarot_title": "Таро на сегодня",
        "today_title": "Удача сегодня",
        "tomorrow_title": "Удача завтра",
        "year": "Год", "month": "Месяц", "day": "День",
        "invalid_year": "Введите год рождения от 1900 до 2030.",
        "mbti_select": "Выберите MBTI",
        "copy_fallback": "Если не работает, скопируйте текст ниже и отправьте.",
    },
    "hi": {
        "lang_label": "भाषा / Language",
        "title": "2026 राशि + MBTI + भाग्य (आज/कल)",
        "caption": "पूरी तरह मुफ्त",
        "name_placeholder": "नाम (परिणाम में दिखेगा)",
        "birth_title": "### जन्म तिथि",
        "mbti_mode": "MBTI कैसे?",
        "direct": "सीधे चुनें",
        "test16": "टेस्ट (16 प्रश्न)",
        "test_start": "टेस्ट शुरू! एक-एक करके जवाब दें",
        "energy": "ऊर्जा दिशा",
        "info": "जानकारी जुटाना",
        "decision": "निर्णय तरीका",
        "life": "जीवन शैली",
        "result_btn": "परिणाम देखें!",
        "fortune_btn": "2026 भाग्य देखें!",
        "reset": "फिर से शुरू",
        "share_btn": "दोस्तों को साझा करें",
        "share_hint": "मोबाइल पर शेयर स्क्रीन खुलेगी; PC पर कॉपी हो सकता है।",
        "tarot_btn": "आज का टैरो",
        "tarot_title": "आज का टैरो",
        "today_title": "आज का भाग्य",
        "tomorrow_title": "कल का भाग्य",
        "year": "वर्ष", "month": "महीना", "day": "दिन",
        "invalid_year": "कृपया 1900 से 2030 के बीच वर्ष दर्ज करें।",
        "mbti_select": "MBTI चुनें",
        "copy_fallback": "यदि शेयर न चले, नीचे का टेक्स्ट कॉपी करके भेजें।",
    },
}

def T(lang: str, key: str) -> str:
    return I18N.get(lang, {}).get(key) or I18N["en"].get(key) or key


# =========================
# 3) 데이터 (HTML 태그 없음: plain text)
# =========================
ZODIAC_LIST = {
    "ko": ["쥐띠", "소띠", "호랑이띠", "토끼띠", "용띠", "뱀띠", "말띠", "양띠", "원숭이띠", "닭띠", "개띠", "돼지띠"],
    "en": ["Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake", "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"],
    "ja": ["鼠", "牛", "虎", "兎", "龍", "蛇", "馬", "羊", "猿", "鶏", "犬", "猪"],
    "zh": ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"],
    "ru": ["Крыса", "Бык", "Тигр", "Кролик", "Дракон", "Змея", "Лошадь", "Коза", "Обезьяна", "Петух", "Собака", "Свинья"],
    "hi": ["चूहा", "बैल", "बाघ", "खरगोश", "ड्रैगन", "साँप", "घोड़ा", "बकरी", "बंदर", "मुर्गा", "कुत्ता", "सूअर"],
}

ZODIAC_DESC = {
    "ko": [
        "안정 속 새로운 기회! 민첩한 판단이 빛나요.",
        "꾸준함의 결실! 안정된 성장과 가족운.",
        "도전과 성공! 리더십이 크게 빛나는 해.",
        "변화에는 신중! 안정적인 선택이 유리해요.",
        "운기 상승! 승진·인정 기회가 늘어요.",
        "직감과 실속! 예상치 못한 재물운.",
        "추진력 최고! 균형 잡기가 핵심이에요.",
        "편안함과 돈운! 가정의 행복도 커져요.",
        "창의력 폭발! 변화 속에 기회가 숨어요.",
        "노력 결실! 실력이 인정받기 쉬워요.",
        "귀인운! 네트워킹이 성과로 이어져요.",
        "여유와 재물운! 즐기며 성장하는 해.",
    ],
    "en": [
        "New chances in stability. Quick judgment helps.",
        "Perseverance pays off. Stable growth and family luck.",
        "Challenge and success. Leadership shines.",
        "Be cautious with changes. Choose stability.",
        "Fortune rising. Recognition and promotion chances.",
        "Intuition and gain. Unexpected money luck.",
        "Strong drive. Balance is the key.",
        "Comfort and money luck. Home happiness grows.",
        "Creativity shines. Opportunities in change.",
        "Effort rewarded. Easier to be recognized.",
        "Helpful people. Networking brings results.",
        "Relaxation and wealth luck. Enjoy and grow.",
    ],
}

MBTI_DESC = {
    "ko": {
        "INTJ": "냉철 전략가", "INTP": "아이디어 천재", "ENTJ": "리더형", "ENTP": "토론왕",
        "INFJ": "통찰가", "INFP": "감성 예술가", "ENFJ": "선생님형", "ENFP": "에너지 폭발",
        "ISTJ": "원칙주의", "ISFJ": "따뜻한 수호자", "ESTJ": "관리자형", "ESFJ": "분위기 메이커",
        "ISTP": "장인", "ISFP": "감성 힐러", "ESTP": "모험가", "ESFP": "핵인싸",
    },
    "en": {
        "INTJ": "Strategist", "INTP": "Thinker", "ENTJ": "Commander", "ENTP": "Debater",
        "INFJ": "Advocate", "INFP": "Mediator", "ENFJ": "Protagonist", "ENFP": "Campaigner",
        "ISTJ": "Logistician", "ISFJ": "Defender", "ESTJ": "Executive", "ESFJ": "Consul",
        "ISTP": "Virtuoso", "ISFP": "Adventurer", "ESTP": "Entrepreneur", "ESFP": "Entertainer",
    },
    "ja": {
        "INTJ": "戦略家", "INTP": "論理学者", "ENTJ": "指揮官", "ENTP": "討論者",
        "INFJ": "提唱者", "INFP": "仲介者", "ENFJ": "主人公", "ENFP": "運動家",
        "ISTJ": "管理者", "ISFJ": "擁護者", "ESTJ": "幹部", "ESFJ": "領事",
        "ISTP": "巨匠", "ISFP": "冒険家", "ESTP": "起業家", "ESFP": "エンターテイナー",
    },
    "zh": {
        "INTJ": "策划者", "INTP": "逻辑学家", "ENTJ": "指挥官", "ENTP": "辩论家",
        "INFJ": "倡导者", "INFP": "调停者", "ENFJ": "主人公", "ENFP": "竞选者",
        "ISTJ": "物流师", "ISFJ": "守护者", "ESTJ": "总经理", "ESFJ": "执政官",
        "ISTP": "鉴赏家", "ISFP": "探险家", "ESTP": "企业家", "ESFP": "表演者",
    },
    "ru": {
        "INTJ": "Стратег", "INTP": "Логик", "ENTJ": "Командир", "ENTP": "Полемист",
        "INFJ": "Защитник", "INFP": "Посредник", "ENFJ": "Протагонист", "ENFP": "Активист",
        "ISTJ": "Логист", "ISFJ": "Опора", "ESTJ": "Администратор", "ESFJ": "Консул",
        "ISTP": "Виртуоз", "ISFP": "Авантюрист", "ESTP": "Предприниматель", "ESFP": "Артист",
    },
    "hi": {
        "INTJ": "रणनीतिक", "INTP": "तार्किक", "ENTJ": "कमांडर", "ENTP": "बहसकर्ता",
        "INFJ": "समर्थक", "INFP": "मध्यस्थ", "ENFJ": "नायक", "ENFP": "अभियानकर्ता",
        "ISTJ": "व्यवस्थापक", "ISFJ": "रक्षक", "ESTJ": "कार्यकारी", "ESFJ": "सलाहकार",
        "ISTP": "कुशल", "ISFP": "साहसी", "ESTP": "उद्यमी", "ESFP": "मनोरंजक",
    },
}

SAJU_MSG = {
    "ko": [
        "목(木) 기운 강함 → 성장과 발전의 해!",
        "화(火) 기운 강함 → 열정 폭발!",
        "토(土) 기운 강함 → 안정과 재물운",
        "금(金) 기운 강함 → 결단력이 좋아요!",
        "수(水) 기운 강함 → 지혜와 흐름",
        "오행 균형 → 행복한 한 해",
        "양기 강함 → 도전 성공",
        "음기 강함 → 내면 성찰",
    ],
    "en": [
        "Strong Wood → Growth year!",
        "Strong Fire → Passion boost!",
        "Strong Earth → Stability and wealth",
        "Strong Metal → Great decisiveness!",
        "Strong Water → Wisdom and flow",
        "Balanced elements → Happy year",
        "Strong Yang → Challenge success",
        "Strong Yin → Inner reflection",
    ],
}

DAILY_MSG = {
    "ko": [
        "재물운 좋음! 작은 투자도 이득 볼 수 있어요.",
        "연애운 최고! 고백이나 데이트에 좋아요.",
        "건강 주의! 과로를 피하고 휴식하세요.",
        "전체운 상승! 좋은 소식이 들어올 수 있어요.",
        "인간관계 운 좋음! 귀인 만남 가능.",
        "일/학업 운 최고! 집중력이 좋아요.",
        "여행운 좋음! 즉흥적인 일정도 OK.",
        "기분 좋은 하루! 웃음이 많아져요.",
    ],
    "en": [
        "Money luck is good. Small moves can pay off.",
        "Love luck is strong. Great for dates or confessions.",
        "Health caution. Rest and avoid burnout.",
        "Overall luck rising. Good news may arrive.",
        "Relationships are lucky. You may meet a helper.",
        "Work/study luck is high. Strong focus today.",
        "Travel luck is good. Spontaneous plans are fine.",
        "A cheerful day. More smiles and lightness.",
    ],
}

OVERALL_2026 = {
    "ko": [
        "성장과 재물이 함께하는 최고의 해!",
        "안정과 행복이 넘치는 한 해!",
        "도전과 성공의 해! 큰 성과가 기대돼요.",
        "사랑과 인연이 피어나는 로맨틱한 해!",
        "변화와 새로운 시작! 창의력이 빛나요.",
    ],
    "en": [
        "A year of growth and wealth!",
        "A year full of stability and happiness!",
        "A year of challenge and success!",
        "A romantic year where connections bloom!",
        "A year of change and fresh starts!",
    ],
}

COMBO_COMMENTS = {
    "ko": [
        "{}의 추진력과 {}의 장점이 만나 시너지가 커져요!",
        "{}의 안정감과 {}의 감각이 균형을 잡아줘요!",
        "{}의 직감과 {}의 현실감이 함께 빛나요!",
        "{}의 성실함과 {}의 유연함이 강점이에요!",
        "{}의 결단과 {}의 센스가 좋은 결과로 이어져요!",
    ],
    "en": [
        "A strong synergy between {} and {}!",
        "Great balance between {} and {}.",
        "Intuition and practicality align: {} + {}.",
        "Consistency meets flexibility: {} + {}.",
        "Decisiveness and sense work well: {} + {}.",
    ],
}

LUCKY_COLORS = {"ko": ["골드", "레드", "블루", "그린", "퍼플"], "en": ["Gold", "Red", "Blue", "Green", "Purple"]}
LUCKY_ITEMS = {"ko": ["황금 액세서리", "빨간 지갑", "파란 목걸이", "초록 식물", "보라색 펜"], "en": ["Golden accessory", "Red wallet", "Blue necklace", "Green plant", "Purple pen"]}
TIPS = {
    "ko": [
        "새로운 사람 만나는 기회가 많아요. 적극적으로!",
        "작은 투자에 집중하면 성과가 나기 쉬워요.",
        "건강 관리에 신경 쓰세요. 가벼운 운동 추천!",
        "가족/친구와 시간 보내며 에너지 충전!",
        "창의적인 취미를 시작해보세요. 재능이 빛나요!",
    ],
    "en": [
        "Be proactive meeting new people.",
        "Focus on small investments and steady progress.",
        "Take care of your health. Light exercise helps.",
        "Spend time with family/friends to recharge.",
        "Start a creative hobby. Your talent will shine.",
    ],
}

TAROT = {
    "The Fool": {"ko": "바보 - 새로운 시작, 모험", "en": "New beginnings, adventure"},
    "The Magician": {"ko": "마법사 - 창조력, 집중", "en": "Manifestation, focus"},
    "The High Priestess": {"ko": "여사제 - 직감, 내면의 목소리", "en": "Intuition, inner voice"},
    "The Empress": {"ko": "여제 - 풍요, 창작", "en": "Abundance, creativity"},
    "The Emperor": {"ko": "황제 - 안정, 구조", "en": "Stability, structure"},
    "The Sun": {"ko": "태양 - 행복, 성공", "en": "Joy, success"},
    "The World": {"ko": "세계 - 완성, 성취", "en": "Completion, fulfillment"},
}

# =========================
# 4) MBTI 상세 16문항 (여기서는 ko/en만 충분히 유지)
#    (필요하면 ja/zh/ru/hi도 추가로 확장 가능)
# =========================
Q16 = {
    "ko": {
        "q_energy": ["주말에 친구들이 갑자기 '놀자!' 하면?", "모임에서 처음 본 사람들과 대화하는 거?", "하루 종일 사람 만난 후에?", "생각이 떠오르면?"],
        "q_info": ["새로운 카페 가면 뭐가 먼저 눈에 들어?", "친구가 고민 상담하면?", "책이나 영화 볼 때?", "쇼핑할 때?"],
        "q_decision": ["친구가 늦어서 화날 때?", "팀 프로젝트에서 의견 충돌 시?", "누가 울면서 상담하면?", "거짓말 탐지 시?"],
        "q_life": ["여행 갈 때?", "숙제/과제 마감 앞두고?", "방 정리할 때?", "선택해야 할 때?"],
        "options_e": ["와 좋아! 바로 나감 (E)", "재밌고 신나! (E)", "아직 에너지 넘쳐! (E)", "바로 말로 풀어냄 (E)"],
        "options_i": ["집에서 쉬고 싶어... (I)", "조금 피곤하고 부담 (I)", "완전 지쳐서 혼자 (I)", "머릿속에서 먼저 정리 (I)"],
        "options_s": ["메뉴판 가격과 메뉴 (S)", "사실 위주로 들어줌 (S)", "스토리/디테일 집중 (S)", "필요한 거 보고 바로 사 (S)"],
        "options_n": ["분위기/컨셉 (N)", "가능성과 미래로 생각 (N)", "상징/숨은 의미 (N)", "코디 상상 (N)"],
        "options_t": ["솔직히 말함 (T)", "논리적으로 따짐 (T)", "해결책 조언 (T)", "바로 지적 (T)"],
        "options_f": ["부드럽게 말함 (F)", "조율함 (F)", "공감부터 (F)", "넘김 (F)"],
        "options_j": ["일정 촘촘히 (J)", "미리 끝냄 (J)", "기준대로 깔끔히 (J)", "빨리 결정 (J)"],
        "options_p": ["즉흥적으로 (P)", "마감 직전 몰아 (P)", "대충도 OK (P)", "더 알아보고 싶음 (P)"],
    },
    "en": {
        "q_energy": ["Friends suddenly say 'Let's hang out!' on weekend?", "Talking to strangers at a gathering?", "After meeting people all day?", "When a thought comes to mind?"],
        "q_info": ["What catches your eye first in a new cafe?", "When a friend shares worries?", "When reading/watching a movie?", "When shopping?"],
        "q_decision": ["When a friend is late and you're upset?", "When opinions clash in a project?", "When someone cries to you?", "When spotting a lie?"],
        "q_life": ["When planning a trip?", "Before a deadline?", "When cleaning your room?", "When you must choose?"],
        "options_e": ["Yes! Go out right away (E)", "Fun and exciting (E)", "Still full of energy (E)", "Say it out loud (E)"],
        "options_i": ["Stay home and rest (I)", "A bit tired (I)", "Need alone time (I)", "Organize in my head (I)"],
        "options_s": ["Menu/prices first (S)", "Listen to facts (S)", "Details and plot (S)", "Buy what I need (S)"],
        "options_n": ["Vibe/concept (N)", "Possibilities/future (N)", "Symbols/hidden meaning (N)", "Imagine styling later (N)"],
        "options_t": ["Be direct (T)", "Argue logically (T)", "Offer solutions (T)", "Point it out (T)"],
        "options_f": ["Say gently (F)", "Mediate feelings (F)", "Empathize first (F)", "Let it pass (F)"],
        "options_j": ["Plan tightly (J)", "Finish early (J)", "Neat & structured (J)", "Decide quickly (J)"],
        "options_p": ["Go with the flow (P)", "Do it at the end (P)", "Messy is okay (P)", "Want more options (P)"],
    },
}

def pick_lang(dct, lang):
    return dct.get(lang) or dct.get("en")

# =========================
# 5) 설정 + 세션
# =========================
st.set_page_config(page_title="2026 Fortune", layout="centered")

if "lang" not in st.session_state:
    st.session_state.lang = "ko"
if "mbti" not in st.session_state:
    st.session_state.mbti = None
if "result_shown" not in st.session_state:
    st.session_state.result_shown = False
if "name" not in st.session_state:
    st.session_state.name = ""
if "year" not in st.session_state:
    st.session_state.year = 2005
if "month" not in st.session_state:
    st.session_state.month = 1
if "day" not in st.session_state:
    st.session_state.day = 1

APP_URL = "https://my-fortune.streamlit.app"

# =========================
# 6) CSS (라디오 가림 + 모바일)
# =========================
st.markdown("""
<style>
.block-container{
    padding-top: 1.1rem !important;
    padding-bottom: 2.0rem !important;
}
div[data-baseweb="radio"] label{
    white-space: normal !important;
    line-height: 1.2 !important;
}
html, body, [class*="css"]{
    font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Noto Sans KR","Apple SD Gothic Neo","Malgun Gothic",sans-serif;
}
.stButton > button{
    border-radius: 18px !important;
    padding: 0.85rem 1rem !important;
    font-weight: 800 !important;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 7) 유틸
# =========================
def get_zodiac_index(year: int) -> int:
    return (year - 4) % 12

def get_zodiac_name(lang: str, idx: int) -> str:
    return ZODIAC_LIST.get(lang, ZODIAC_LIST["en"])[idx]

def saju_message(lang: str, y: int, m: int, d: int) -> str:
    msgs = pick_lang(SAJU_MSG, lang)
    return msgs[(y + m + d) % len(msgs)]

def daily_fortune(lang: str, zodiac_idx: int, offset_days: int) -> str:
    msgs = pick_lang(DAILY_MSG, lang)
    base = datetime.now() + timedelta(days=offset_days)
    seed = int(base.strftime("%Y%m%d")) * 100 + zodiac_idx
    random.seed(seed)
    return random.choice(msgs)

def render_ad_placeholder(lang: str):
    st.markdown(f"""
    <div style="
        margin: 16px 6px 10px 6px;
        padding: 14px 14px;
        border: 1.6px dashed rgba(142,68,173,0.45);
        border-radius: 18px;
        background: rgba(255,255,255,0.55);
        text-align: center;
    ">
        <div style="font-size:0.82em; color:#6f42c1; font-weight:900; letter-spacing:1px; margin-bottom:4px;">
            {T(lang, "ad_slot_label")}
        </div>
        <div style="font-size:0.9em; color:#888;">
            {T(lang, "ad_slot_sub")}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_dananum_ad_ko_only(lang: str):
    if lang != "ko":
        return
    st.markdown(f"""
    <div style="
        margin: 16px 6px 10px 6px;
        padding: 16px 14px;
        border: 2px solid rgba(231,76,60,0.35);
        border-radius: 18px;
        background: rgba(255,255,255,0.75);
        text-align: center;
        box-shadow: 0 8px 24px rgba(0,0,0,0.10);
    ">
        <div style="display:flex; justify-content:center; align-items:center; gap:8px; margin-bottom:8px;">
            <span style="
                font-size:0.78em; padding:4px 10px; border-radius:999px;
                background: rgba(231,76,60,0.10);
                border: 1px solid rgba(231,76,60,0.25);
                color:#e74c3c; font-weight:900;">
                {T(lang, "ad_badge")}
            </span>
            <span style="font-weight:900; color:#d35400;">{T(lang, "dananum_title")}</span>
        </div>
        <div style="font-size:1.0em; color:#333; line-height:1.6; margin:6px 0 4px 0;">
            {T(lang, "dananum_line1")}
        </div>
        <div style="font-size:1.0em; color:#333; line-height:1.6; margin:0 0 14px 0;">
            {T(lang, "dananum_line2")}
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
            ">{T(lang, "dananum_btn")}</button>
        </a>
    </div>
    """, unsafe_allow_html=True)

def share_button_component(button_label: str, share_text: str, share_url: str, hint_text: str):
    # navigator.share(텍스트+URL) → 모바일 공유 시트(카톡/문자/기타 앱)
    # 미지원이면 클립보드 복사로 대체
    safe_text = share_text.replace("\\", "\\\\").replace("`", "\\`")
    safe_url = share_url.replace("\\", "\\\\").replace("`", "\\`")
    safe_hint = hint_text.replace("\\", "\\\\").replace("`", "\\`")

    components.html(
        f"""
        <div style="text-align:center; margin: 10px 0 14px 0;">
            <button id="shareBtn" style="
                background:#6f42c1; color:white; padding:16px 22px;
                border:none; border-radius:999px; font-size:1.05em; font-weight:900;
                box-shadow: 0 10px 24px rgba(111,66,193,0.25); cursor:pointer;
                width: min(520px, 92%);
            ">{button_label}</button>
            <div style="margin-top:10px; font-size:0.92em; color:#666;">{safe_hint}</div>
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
                }} catch (e) {{
                    // user cancelled or error
                }}

                // fallback: clipboard copy
                try {{
                    if (navigator.clipboard && navigator.clipboard.writeText) {{
                        await navigator.clipboard.writeText(text + "\\n" + url);
                        alert("Copied! Paste it to share.");
                    }} else {{
                        alert("Share not supported on this browser. Copy text manually below.");
                    }}
                }} catch (e) {{
                    alert("Share not supported. Copy text manually below.");
                }}
            }});
        }})();
        </script>
        """,
        height=110,
    )

# =========================
# 8) 언어 선택
# =========================
lang_codes = [c for c, _ in LANGS]
lang_labels = [f"{name} ({code})" for code, name in LANGS]
default_idx = lang_codes.index(st.session_state.lang) if st.session_state.lang in lang_codes else 0

selected_label = st.radio(
    T(st.session_state.lang, "lang_label"),
    lang_labels,
    index=default_idx,
    horizontal=True
)
st.session_state.lang = lang_codes[lang_labels.index(selected_label)]
lang = st.session_state.lang

# =========================
# 9) 입력 화면
# =========================
if not st.session_state.result_shown:
    st.markdown(
        f"<h1 style='text-align:center; color:#6f42c1; margin:10px 0 6px 0;'>{T(lang,'title')}</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"<p style='text-align:center; color:#777; margin:0 0 14px 0;'>{T(lang,'caption')}</p>",
        unsafe_allow_html=True
    )

    render_dananum_ad_ko_only(lang)
    render_ad_placeholder(lang)

    st.session_state.name = st.text_input(T(lang, "name_placeholder"), value=st.session_state.name)

    st.markdown(f"<h3 style='text-align:center; margin:10px 0 8px 0;'>{T(lang,'birth_title')}</h3>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    st.session_state.year = c1.number_input(T(lang, "year"), min_value=1900, max_value=2030, value=st.session_state.year, step=1)
    st.session_state.month = c2.number_input(T(lang, "month"), min_value=1, max_value=12, value=st.session_state.month, step=1)
    st.session_state.day = c3.number_input(T(lang, "day"), min_value=1, max_value=31, value=st.session_state.day, step=1)

    choice = st.radio(T(lang, "mbti_mode"), [T(lang, "direct"), T(lang, "test16")])

    if choice == T(lang, "direct"):
        mbti_input = st.selectbox(T(lang, "mbti_select"), sorted(MBTI_DESC["en"].keys()))
        if st.button(T(lang, "fortune_btn"), use_container_width=True):
            st.session_state.mbti = mbti_input
            st.session_state.result_shown = True
            st.rerun()
    else:
        st.markdown(
            f"<h3 style='text-align:center; color:#3498db; margin-top:10px;'>{T(lang,'test_start')}</h3>",
            unsafe_allow_html=True
        )

        qpack = Q16.get(lang) or Q16["en"]

        e_i = s_n = t_f = j_p = 0

        st.subheader(T(lang, "energy"))
        for i in range(4):
            if st.radio(qpack["q_energy"][i], [qpack["options_e"][i], qpack["options_i"][i]], key=f"energy_{i}") == qpack["options_e"][i]:
                e_i += 1

        st.subheader(T(lang, "info"))
        for i in range(4):
            if st.radio(qpack["q_info"][i], [qpack["options_s"][i], qpack["options_n"][i]], key=f"info_{i}") == qpack["options_s"][i]:
                s_n += 1

        st.subheader(T(lang, "decision"))
        for i in range(4):
            if st.radio(qpack["q_decision"][i], [qpack["options_t"][i], qpack["options_f"][i]], key=f"decision_{i}") == qpack["options_t"][i]:
                t_f += 1

        st.subheader(T(lang, "life"))
        for i in range(4):
            if st.radio(qpack["q_life"][i], [qpack["options_j"][i], qpack["options_p"][i]], key=f"life_{i}") == qpack["options_j"][i]:
                j_p += 1

        if st.button(T(lang, "result_btn"), use_container_width=True):
            ei = "E" if e_i >= 3 else "I"
            sn = "S" if s_n >= 3 else "N"
            tf = "T" if t_f >= 3 else "F"
            jp = "J" if j_p >= 3 else "P"
            st.session_state.mbti = ei + sn + tf + jp
            st.session_state.result_shown = True
            st.rerun()

# =========================
# 10) 결과 화면
# =========================
if st.session_state.result_shown:
    if not (1900 <= st.session_state.year <= 2030):
        st.error(T(lang, "invalid_year"))
        if st.button(T(lang, "reset"), use_container_width=True):
            st.session_state.clear()
            st.rerun()
        st.stop()

    zodiac_idx = get_zodiac_index(st.session_state.year)
    zodiac_name = get_zodiac_name(lang, zodiac_idx)
    zodiac_desc = (ZODIAC_DESC.get(lang) or ZODIAC_DESC["en"])[zodiac_idx]

    mbti = st.session_state.mbti
    mbti_desc = (MBTI_DESC.get(lang) or MBTI_DESC["en"]).get(mbti, mbti)

    saju = saju_message(lang, st.session_state.year, st.session_state.month, st.session_state.day)
    today = daily_fortune(lang, zodiac_idx, 0)
    tomorrow = daily_fortune(lang, zodiac_idx, 1)

    overall = random.choice(pick_lang(OVERALL_2026, lang))
    combo = random.choice(pick_lang(COMBO_COMMENTS, lang)).format(zodiac_name, mbti_desc)
    lucky_color = random.choice(pick_lang(LUCKY_COLORS, lang))
    lucky_item = random.choice(pick_lang(LUCKY_ITEMS, lang))
    tip = random.choice(pick_lang(TIPS, lang))

    name_display = st.session_state.name.strip()
    name_line = f"{name_display} " if name_display else ""

    st.markdown(f"""
    <div style="
        margin: 10px 6px 10px 6px;
        padding: 16px 14px;
        border-radius: 18px;
        background: linear-gradient(135deg, rgba(161,140,209,0.30), rgba(251,194,235,0.28), rgba(142,197,252,0.28));
        border: 1px solid rgba(142,68,173,0.18);
        text-align: center;
    ">
        <div style="font-size:1.55em; font-weight:900; color:#5e2b97;">
            {name_line}2026
        </div>
        <div style="font-size:1.15em; font-weight:900; color:#222; margin-top:6px;">
            {zodiac_name} · {mbti}
        </div>
        <div style="font-size:1.05em; font-weight:900; color:#6f42c1; margin-top:8px;">
            {T(lang, "combo")}
        </div>
    </div>
    """, unsafe_allow_html=True)

    render_ad_placeholder(lang)

    st.markdown(f"""
    <div style="
        margin: 12px 6px 12px 6px;
        padding: 18px 16px;
        border-radius: 18px;
        background: rgba(255,255,255,0.92);
        border: 1.6px solid rgba(142,68,173,0.22);
        box-shadow: 0 10px 26px rgba(0,0,0,0.10);
    ">
        <div style="font-size:1.02em; line-height:1.95; color:#111;">
            <b>{T(lang,'zodiac_title')}</b>: {zodiac_desc}<br>
            <b>{T(lang,'mbti_title')}</b>: {mbti_desc}<br>
            <b>{T(lang,'saju_title')}</b>: {saju}<br><br>

            <b>{T(lang,'today_title')}</b>: {today}<br>
            <b>{T(lang,'tomorrow_title')}</b>: {tomorrow}<br><br>

            <b>{T(lang,'overall_title')}</b>: {overall}<br>
            <b>{T(lang,'combo_title')}</b>: {combo}<br>
            <b>{T(lang,'lucky_color_title')}</b>: {lucky_color} &nbsp; | &nbsp; <b>{T(lang,'lucky_item_title')}</b>: {lucky_item}<br>
            <b>{T(lang,'tip_title')}</b>: {tip}
        </div>
    </div>
    """, unsafe_allow_html=True)

    render_dananum_ad_ko_only(lang)

    with st.expander(T(lang, "tarot_btn"), expanded=False):
        card = random.choice(list(TAROT.keys()))
        meaning = TAROT[card].get(lang) or TAROT[card].get("en")
        st.markdown(f"""
        <div style="
            margin: 6px 2px 8px 2px;
            padding: 16px 14px;
            border-radius: 18px;
            background: rgba(255,255,255,0.90);
            border: 1.6px solid rgba(155,89,182,0.22);
            text-align:center;
        ">
            <div style="font-size:1.0em; font-weight:900; color:#9b59b6; margin-bottom:6px;">
                {T(lang, "tarot_title")}
            </div>
            <div style="font-size:1.6em; font-weight:900; color:#333;">
                {card}
            </div>
            <div style="font-size:1.05em; color:#111; line-height:1.65; margin-top:8px;">
                {meaning}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 공유용 텍스트(순수 텍스트)
    share_text = (
        f"{name_line}2026\n"
        f"{zodiac_name} · {mbti}\n"
        f"{T(lang,'combo')}\n\n"
        f"{T(lang,'today_title')}: {today}\n"
        f"{T(lang,'tomorrow_title')}: {tomorrow}\n\n"
        f"{T(lang,'overall_title')}: {overall}\n"
        f"{T(lang,'combo_title')}: {combo}\n"
        f"{T(lang,'lucky_color_title')}: {lucky_color} / {T(lang,'lucky_item_title')}: {lucky_item}\n"
        f"{T(lang,'tip_title')}: {tip}\n"
    )

    # ✅ 핵심: 모바일 공유시트 열기 (navigator.share)
    share_button_component(
        button_label=T(lang, "share_btn"),
        share_text=share_text,
        share_url=APP_URL,
        hint_text=T(lang, "share_hint"),
    )

    st.caption(T(lang, "copy_fallback"))
    st.text_area("Share Text", share_text + "\n" + APP_URL, height=200)
    st.caption(APP_URL)

    if st.button(T(lang, "reset"), use_container_width=True):
        st.session_state.clear()
        st.rerun()
