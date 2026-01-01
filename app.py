import streamlit as st
from datetime import datetime, date
import random
import json
from pathlib import Path
import streamlit.components.v1 as components


# =========================================
# 0) Language options
# =========================================
LANG_OPTIONS = {
    "ko": "한국어",
    "en": "English",
    "hi": "हिन्दी",
    "zh": "中文(简体)",
    "ru": "Русский",
    "ja": "日本語"
}
LANG_KEYS = list(LANG_OPTIONS.keys())

UI = {
    "ko": {
        "title": "⭐ 2026년 운세 ⭐",
        "subtitle": "띠 + MBTI + 사주 + 오늘/내일 운세",
        "lang_label": "언어 / Language",
        "name_label": "이름 입력 (결과에 표시돼요)",
        "birth_label": "생년월일 입력",
        "mbti_mode": "MBTI는 어떻게 할까요?",
        "mbti_direct": "직접 선택(이미 알아요)",
        "mbti_test": "간단 테스트(12문항)",
        "btn_view": "2026년 운세 보기!",
        "btn_view_test": "테스트 결과로 운세 보기!",
        "combo": "최고 조합!",
        "zodiac_title": "띠",
        "mbti_title": "MBTI",
        "saju_title": "사주 한 마디",
        "today_title": "오늘 운세",
        "tomorrow_title": "내일 운세",
        "overall_title": "2026 전체 운세",
        "combo_title": "조합 한 마디",
        "lucky_color_title": "럭키 컬러",
        "lucky_item_title": "럭키 아이템",
        "tip_title": "팁",
        "tarot_btn": "오늘의 타로 카드 보기",
        "tarot_title": "오늘의 타로 카드",
        "share_btn": "친구에게 공유하기",
        "reset_btn": "처음부터 다시하기",
        "error_year": "생년은 1900~2030년 사이로 입력해주세요!",
        "test_caption": "총 12문항(약 30초) — 솔직하게 고르면 더 잘 맞아요 🙂",
        "sec_ei": "1) 에너지(E/I)",
        "sec_sn": "2) 인식(S/N)",
        "sec_tf": "3) 판단(T/F)",
        "sec_jp": "4) 생활(J/P)",
        "share_title": "2026년 운세",
        "share_fail_copy": "공유 기능이 지원되지 않아 텍스트를 복사했어요!\n카톡에 붙여넣기 해주세요.",
        "share_manual_prompt": "아래 내용을 복사해서 카톡에 붙여넣기 해주세요:",
        "share_cancel": "공유가 취소되었거나 지원되지 않아요.\n복사 후 붙여넣기 해주세요.",
    },
    "en": {
        "title": "⭐ 2026 Fortune ⭐",
        "subtitle": "Zodiac + MBTI + Today/Tomorrow Luck",
        "lang_label": "Language",
        "name_label": "Name (shown in result)",
        "birth_label": "Birth date",
        "mbti_mode": "How to do MBTI?",
        "mbti_direct": "Select directly (I know it)",
        "mbti_test": "Quick test (12 questions)",
        "btn_view": "See my 2026 fortune!",
        "btn_view_test": "See fortune from test result!",
        "combo": "Best Combo!",
        "zodiac_title": "Zodiac",
        "mbti_title": "MBTI",
        "saju_title": "Fortune comment",
        "today_title": "Today's luck",
        "tomorrow_title": "Tomorrow's luck",
        "overall_title": "2026 annual luck",
        "combo_title": "Combination meaning",
        "lucky_color_title": "Lucky color",
        "lucky_item_title": "Lucky item",
        "tip_title": "Tip",
        "tarot_btn": "Draw today's tarot card",
        "tarot_title": "Today's tarot card",
        "share_btn": "Share with friends",
        "reset_btn": "Start over",
        "error_year": "Please enter a birth year between 1900 and 2030!",
        "test_caption": "12 questions (~30 sec) — answer honestly 🙂",
        "sec_ei": "1) Energy (E/I)",
        "sec_sn": "2) Perception (S/N)",
        "sec_tf": "3) Decision (T/F)",
        "sec_jp": "4) Lifestyle (J/P)",
        "share_title": "2026 Fortune",
        "share_fail_copy": "Sharing isn't supported here, so the text was copied.\nPaste it in KakaoTalk or message.",
        "share_manual_prompt": "Copy and paste this text to share:",
        "share_cancel": "Sharing was canceled or not supported.\nPlease copy & paste.",
    },
    "hi": {
        "title": "⭐ 2026 भाग्य ⭐",
        "subtitle": "Zodiac + MBTI + Today/Tomorrow Luck",
        "lang_label": "भाषा / Language",
        "name_label": "नाम (परिणाम में दिखेगा)",
        "birth_label": "जन्म तिथि",
        "mbti_mode": "MBTI कैसे करें?",
        "mbti_direct": "सीधा चुनें",
        "mbti_test": "त्वरित टेस्ट (12 प्रश्न)",
        "btn_view": "2026 भाग्य देखें!",
        "btn_view_test": "टेस्ट के साथ देखें!",
        "combo": "Best Combo!",
        "zodiac_title": "Zodiac",
        "mbti_title": "MBTI",
        "saju_title": "Fortune comment",
        "today_title": "Today's luck",
        "tomorrow_title": "Tomorrow's luck",
        "overall_title": "2026 annual luck",
        "combo_title": "Combination meaning",
        "lucky_color_title": "Lucky color",
        "lucky_item_title": "Lucky item",
        "tip_title": "Tip",
        "tarot_btn": "आज का टैरो कार्ड",
        "tarot_title": "आज का टैरो",
        "share_btn": "Share with friends",
        "reset_btn": "Start over",
        "error_year": "1900–2030 के बीच जन्म वर्ष दर्ज करें!",
        "test_caption": "12 प्रश्न (~30 सेकंड) — ईमानदारी से चुनें 🙂",
        "sec_ei": "1) Energy (E/I)",
        "sec_sn": "2) Perception (S/N)",
        "sec_tf": "3) Decision (T/F)",
        "sec_jp": "4) Lifestyle (J/P)",
        "share_title": "2026 Fortune",
        "share_fail_copy": "Sharing is not supported here, so the text was copied.\nPlease paste it in your messenger.",
        "share_manual_prompt": "Copy and paste this text:",
        "share_cancel": "Sharing canceled or not supported.\nPlease copy & paste.",
    },
    "zh": {
        "title": "⭐ 2026 运势 ⭐",
        "subtitle": "生肖 + MBTI + 今日/明日运势",
        "lang_label": "语言 / Language",
        "name_label": "姓名（显示在结果）",
        "birth_label": "出生日期",
        "mbti_mode": "MBTI 怎么做？",
        "mbti_direct": "直接选择",
        "mbti_test": "快速测试（12题）",
        "btn_view": "查看 2026 运势！",
        "btn_view_test": "用测试结果查看！",
        "combo": "最佳组合！",
        "zodiac_title": "生肖",
        "mbti_title": "MBTI",
        "saju_title": "一句话运势",
        "today_title": "今日运势",
        "tomorrow_title": "明日运势",
        "overall_title": "2026 全年运势",
        "combo_title": "组合一句话",
        "lucky_color_title": "幸运颜色",
        "lucky_item_title": "幸运物品",
        "tip_title": "提示",
        "tarot_btn": "抽今日塔罗牌",
        "tarot_title": "今日塔罗",
        "share_btn": "分享给朋友",
        "reset_btn": "重新开始",
        "error_year": "请输入 1900–2030 之间的出生年份！",
        "test_caption": "12题（约30秒）— 真诚作答更准 🙂",
        "sec_ei": "1) Energy (E/I)",
        "sec_sn": "2) Perception (S/N)",
        "sec_tf": "3) Decision (T/F)",
        "sec_jp": "4) Lifestyle (J/P)",
        "share_title": "2026 运势",
        "share_fail_copy": "当前环境不支持分享，已复制文本。\n请粘贴到聊天软件发送。",
        "share_manual_prompt": "复制并粘贴以下内容：",
        "share_cancel": "分享取消或不支持。\n请复制并粘贴。",
    },
    "ru": {
        "title": "⭐ 2026 Удача ⭐",
        "subtitle": "Zodiac + MBTI + Today/Tomorrow Luck",
        "lang_label": "Язык / Language",
        "name_label": "Имя (в результате)",
        "birth_label": "Дата рождения",
        "mbti_mode": "Как выбрать MBTI?",
        "mbti_direct": "Выбрать напрямую",
        "mbti_test": "Быстрый тест (12 вопросов)",
        "btn_view": "Показать удачу 2026!",
        "btn_view_test": "Показать по тесту!",
        "combo": "Лучшее сочетание!",
        "zodiac_title": "Zodiac",
        "mbti_title": "MBTI",
        "saju_title": "Комментарий",
        "today_title": "Сегодня",
        "tomorrow_title": "Завтра",
        "overall_title": "2026 год",
        "combo_title": "Сочетание",
        "lucky_color_title": "Цвет",
        "lucky_item_title": "Предмет",
        "tip_title": "Совет",
        "tarot_btn": "Таро дня",
        "tarot_title": "Таро",
        "share_btn": "Поделиться",
        "reset_btn": "Сначала",
        "error_year": "Введите год рождения 1900–2030!",
        "test_caption": "12 вопросов (~30 сек) — отвечайте честно 🙂",
        "sec_ei": "1) Energy (E/I)",
        "sec_sn": "2) Perception (S/N)",
        "sec_tf": "3) Decision (T/F)",
        "sec_jp": "4) Lifestyle (J/P)",
        "share_title": "2026 Fortune",
        "share_fail_copy": "Sharing isn't supported here, so the text was copied.\nPlease paste it in messenger.",
        "share_manual_prompt": "Copy and paste this text:",
        "share_cancel": "Sharing canceled or not supported.\nPlease copy & paste.",
    },
    "ja": {
        "title": "⭐ 2026 運勢 ⭐",
        "subtitle": "干支 + MBTI + 今日/明日の運勢",
        "lang_label": "言語 / Language",
        "name_label": "名前（結果に表示）",
        "birth_label": "生年月日",
        "mbti_mode": "MBTI はどうする？",
        "mbti_direct": "直接選ぶ",
        "mbti_test": "クイックテスト（12問）",
        "btn_view": "2026運勢を見る！",
        "btn_view_test": "テスト結果で見る！",
        "combo": "最高の組み合わせ！",
        "zodiac_title": "干支",
        "mbti_title": "MBTI",
        "saju_title": "ひと言",
        "today_title": "今日",
        "tomorrow_title": "明日",
        "overall_title": "2026全体運",
        "combo_title": "組み合わせ",
        "lucky_color_title": "ラッキーカラー",
        "lucky_item_title": "ラッキーアイテム",
        "tip_title": "ヒント",
        "tarot_btn": "今日のタロット",
        "tarot_title": "タロット",
        "share_btn": "友達に共有",
        "reset_btn": "最初から",
        "error_year": "1900〜2030の年を入力してください！",
        "test_caption": "12問（約30秒）— 素直に選ぶと当たりやすい🙂",
        "sec_ei": "1) Energy (E/I)",
        "sec_sn": "2) Perception (S/N)",
        "sec_tf": "3) Decision (T/F)",
        "sec_jp": "4) Lifestyle (J/P)",
        "share_title": "2026運勢",
        "share_fail_copy": "共有が使えないためテキストをコピーしました。\nメッセンジャーに貼り付けてください。",
        "share_manual_prompt": "以下をコピーして貼り付けてください：",
        "share_cancel": "共有がキャンセル/非対応です。\nコピーして貼り付けてください。",
    }
}


# =========================================
# 1) 12-question MBTI test (PER LANGUAGE)
#    ✅ This is the 핵심: language별 질문/선택지
# =========================================
TEST_Q = {
    "ko": {
        "EI": [
            ("주말에 갑자기 약속 생기면?", "좋아! 바로 나가자 (E)", "집에서 쉬고 싶어 (I)"),
            ("에너지는 어디서 충전돼?", "사람 만나면서 (E)", "혼자 있을 때 (I)"),
            ("생각이 떠오르면?", "말하면서 정리 (E)", "머릿속에서 정리 (I)"),
        ],
        "SN": [
            ("새로운 걸 볼 때 먼저 보는 건?", "사실/디테일 (S)", "의미/가능성 (N)"),
            ("설명 들을 때 더 좋은 건?", "예시와 구체 (S)", "큰 그림과 방향 (N)"),
            ("아이디어 스타일은?", "검증된 방법 (S)", "새로운 방식 (N)"),
        ],
        "TF": [
            ("갈등이 생기면?", "원칙/논리 (T)", "배려/조화 (F)"),
            ("결정 기준은?", "효율/정확 (T)", "가치/감정 (F)"),
            ("피드백할 때?", "직설적/명확 (T)", "부드럽게/상처 최소 (F)"),
        ],
        "JP": [
            ("일정 스타일은?", "미리 계획 (J)", "즉흥/유동 (P)"),
            ("마감 앞두면?", "미리 끝냄 (J)", "막판 몰아 (P)"),
            ("정리정돈은?", "깔끔 유지 (J)", "필요할 때만 (P)"),
        ],
    },
    "en": {
        "EI": [
            ("If a plan comes up suddenly on weekend?", "Awesome! Let's go (E)", "I'd rather rest at home (I)"),
            ("You recharge by…", "Meeting people (E)", "Being alone (I)"),
            ("When a thought appears, you…", "Sort it while talking (E)", "Sort it in your head first (I)"),
        ],
        "SN": [
            ("When you see something new, you notice…", "Facts & details (S)", "Meaning & possibilities (N)"),
            ("You prefer explanations with…", "Examples & specifics (S)", "Big picture & direction (N)"),
            ("Your idea style is…", "Proven methods (S)", "New approaches (N)"),
        ],
        "TF": [
            ("In conflict, you choose…", "Logic & principles (T)", "Care & harmony (F)"),
            ("Your decision base is…", "Efficiency & accuracy (T)", "Values & feelings (F)"),
            ("When giving feedback…", "Direct & clear (T)", "Gentle & considerate (F)"),
        ],
        "JP": [
            ("Your schedule style?", "Planned (J)", "Spontaneous (P)"),
            ("Before a deadline…", "Finish early (J)", "Rush at the end (P)"),
            ("Tidying up is…", "Keep it neat (J)", "Only when needed (P)"),
        ],
    },
    "hi": {
        "EI": [
            ("वीकेंड पर अचानक प्लान बन जाए?", "चलो! तुरंत (E)", "घर पर आराम (I)"),
            ("आप ऊर्जा कैसे भरते हैं?", "लोगों से मिलकर (E)", "अकेले रहकर (I)"),
            ("जब विचार आए तो?", "बोलते हुए सुलझाता/सुलझाती हूँ (E)", "पहले मन में सुलझाता/सुलझाती हूँ (I)"),
        ],
        "SN": [
            ("नई चीज़ में आप पहले देखते हैं…", "तथ्य/डिटेल (S)", "अर्थ/संभावना (N)"),
            ("समझाने का पसंदीदा तरीका…", "उदाहरण/विशेष (S)", "बड़ी तस्वीर (N)"),
            ("आपके आइडिया आमतौर पर…", "आजमाए हुए (S)", "नए तरीके (N)"),
        ],
        "TF": [
            ("टकराव में आप चुनते हैं…", "तर्क/सिद्धांत (T)", "देखभाल/सामंजस्य (F)"),
            ("निर्णय का आधार…", "कुशलता/सटीकता (T)", "मूल्य/भावना (F)"),
            ("फीडबैक देते समय…", "सीधा/स्पष्ट (T)", "नरम/विचारशील (F)"),
        ],
        "JP": [
            ("आपकी योजना शैली…", "पहले से तय (J)", "तुरंत/लचीला (P)"),
            ("डेडलाइन से पहले…", "पहले खत्म (J)", "आख़िर में तेज़ (P)"),
            ("सफाई/व्यवस्था…", "हमेशा साफ (J)", "ज़रूरत पर (P)"),
        ],
    },
    "zh": {
        "EI": [
            ("周末突然有人约你？", "太好了！马上走 (E)", "更想在家休息 (I)"),
            ("你如何充电？", "和人相处 (E)", "独处 (I)"),
            ("有想法时你会？", "边说边整理 (E)", "先在脑中整理 (I)"),
        ],
        "SN": [
            ("看到新事物你先注意？", "事实/细节 (S)", "意义/可能性 (N)"),
            ("你更喜欢的说明方式？", "例子与具体 (S)", "大局与方向 (N)"),
            ("你的点子通常是？", "成熟方法 (S)", "新思路 (N)"),
        ],
        "TF": [
            ("发生冲突时你更倾向？", "逻辑/原则 (T)", "体贴/和谐 (F)"),
            ("做决定更看重？", "效率/准确 (T)", "价值/感受 (F)"),
            ("给反馈时你更常？", "直接清晰 (T)", "委婉体贴 (F)"),
        ],
        "JP": [
            ("你的行程风格？", "提前规划 (J)", "随性灵活 (P)"),
            ("临近截止日期？", "提前完成 (J)", "最后冲刺 (P)"),
            ("整理房间？", "保持整洁 (J)", "需要时才整理 (P)"),
        ],
    },
    "ru": {
        "EI": [
            ("Если планы внезапно появляются на выходных?", "Отлично! Пошли (E)", "Лучше отдохнуть дома (I)"),
            ("Вы восстанавливаетесь благодаря…", "общению (E)", "одиночеству (I)"),
            ("Когда появляется мысль, вы…", "проясняете её в разговоре (E)", "сначала обдумываете (I)"),
        ],
        "SN": [
            ("В новом вы замечаете…", "факты и детали (S)", "смысл и возможности (N)"),
            ("Вы любите объяснения через…", "примеры и конкретику (S)", "общую картину (N)"),
            ("Ваши идеи обычно…", "проверенные (S)", "новые подходы (N)"),
        ],
        "TF": [
            ("В конфликте вы выбираете…", "логику и принципы (T)", "заботу и гармонию (F)"),
            ("Основа решения…", "эффективность/точность (T)", "ценности/чувства (F)"),
            ("Обратная связь у вас…", "прямая и ясная (T)", "мягкая и деликатная (F)"),
        ],
        "JP": [
            ("Ваш стиль планирования?", "по плану (J)", "спонтанно (P)"),
            ("Перед дедлайном…", "закончить заранее (J)", "в последний момент (P)"),
            ("Уборка — это…", "держать в порядке (J)", "по необходимости (P)"),
        ],
    },
    "ja": {
        "EI": [
            ("週末に突然誘われたら？", "いいね！すぐ行く (E)", "家で休みたい (I)"),
            ("充電方法は？", "人と会う (E)", "一人の時間 (I)"),
            ("思いついたら？", "話しながら整理 (E)", "頭の中で整理 (I)"),
        ],
        "SN": [
            ("新しいものを見るとき？", "事実/細部 (S)", "意味/可能性 (N)"),
            ("説明はどちらが好き？", "具体例 (S)", "全体像 (N)"),
            ("アイデアの傾向は？", "実績ある方法 (S)", "新しい方法 (N)"),
        ],
        "TF": [
            ("対立が起きたら？", "論理/原則 (T)", "配慮/調和 (F)"),
            ("判断基準は？", "効率/正確 (T)", "価値観/気持ち (F)"),
            ("フィードバックは？", "率直/明確 (T)", "やさしく/丁寧 (F)"),
        ],
        "JP": [
            ("予定の立て方？", "計画的 (J)", "その場で (P)"),
            ("締切前は？", "早めに終える (J)", "直前に追い込む (P)"),
            ("片付けは？", "常に整える (J)", "必要な時だけ (P)"),
        ],
    }
}


# =========================================
# 2) Other data
# =========================================
ZODIAC_LIST = {
    "ko": ["쥐띠","소띠","호랑이띠","토끼띠","용띠","뱀띠","말띠","양띠","원숭이띠","닭띠","개띠","돼지띠"],
    "en": ["Rat","Ox","Tiger","Rabbit","Dragon","Snake","Horse","Goat","Monkey","Rooster","Dog","Pig"],
    "hi": ["Rat","Ox","Tiger","Rabbit","Dragon","Snake","Horse","Goat","Monkey","Rooster","Dog","Pig"],
    "zh": ["鼠","牛","虎","兔","龙","蛇","马","羊","猴","鸡","狗","猪"],
    "ru": ["Rat","Ox","Tiger","Rabbit","Dragon","Snake","Horse","Goat","Monkey","Rooster","Dog","Pig"],
    "ja": ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]
}

MBTIS = {
    "ko": {
        "INTJ":"냉철 전략가","INTP":"아이디어 천재","ENTJ":"보스","ENTP":"토론왕",
        "INFJ":"마음 마스터","INFP":"감성 예술가","ENFJ":"모두 선생님","ENFP":"인간 비타민",
        "ISTJ":"규칙 지킴이","ISFJ":"세상 따뜻함","ESTJ":"리더","ESFJ":"분위기 메이커",
        "ISTP":"고치는 장인","ISFP":"감성 힐러","ESTP":"모험왕","ESFP":"파티 주인공"
    },
    "en": {
        "INTJ":"Strategist","INTP":"Thinker","ENTJ":"Commander","ENTP":"Debater",
        "INFJ":"Advocate","INFP":"Mediator","ENFJ":"Protagonist","ENFP":"Campaigner",
        "ISTJ":"Logistician","ISFJ":"Defender","ESTJ":"Executive","ESFJ":"Consul",
        "ISTP":"Virtuoso","ISFP":"Adventurer","ESTP":"Entrepreneur","ESFP":"Entertainer"
    },
    "hi": {
        "INTJ":"Strategist","INTP":"Thinker","ENTJ":"Commander","ENTP":"Debater",
        "INFJ":"Advocate","INFP":"Mediator","ENFJ":"Protagonist","ENFP":"Campaigner",
        "ISTJ":"Logistician","ISFJ":"Defender","ESTJ":"Executive","ESFJ":"Consul",
        "ISTP":"Virtuoso","ISFP":"Adventurer","ESTP":"Entrepreneur","ESFP":"Entertainer"
    },
    "zh": {
        "INTJ":"战略家","INTP":"思考者","ENTJ":"指挥官","ENTP":"辩论家",
        "INFJ":"提倡者","INFP":"调停者","ENFJ":"主人公","ENFP":"竞选者",
        "ISTJ":"物流师","ISFJ":"守护者","ESTJ":"总经理","ESFJ":"执政官",
        "ISTP":"鉴赏家","ISFP":"探险家","ESTP":"企业家","ESFP":"表演者"
    },
    "ru": {
        "INTJ":"Strategist","INTP":"Thinker","ENTJ":"Commander","ENTP":"Debater",
        "INFJ":"Advocate","INFP":"Mediator","ENFJ":"Protagonist","ENFP":"Campaigner",
        "ISTJ":"Logistician","ISFJ":"Defender","ESTJ":"Executive","ESFJ":"Consul",
        "ISTP":"Virtuoso","ISFP":"Adventurer","ESTP":"Entrepreneur","ESFP":"Entertainer"
    },
    "ja": {
        "INTJ":"Strategist","INTP":"Thinker","ENTJ":"Commander","ENTP":"Debater",
        "INFJ":"Advocate","INFP":"Mediator","ENFJ":"Protagonist","ENFP":"Campaigner",
        "ISTJ":"Logistician","ISFJ":"Defender","ESTJ":"Executive","ESFJ":"Consul",
        "ISTP":"Virtuoso","ISFP":"Adventurer","ESTP":"Entrepreneur","ESFP":"Entertainer"
    }
}

SAJU_MSGS = {
    "ko": ["목(木) 기운 강함 → 성장과 발전의 해!","화(火) 기운 강함 → 열정 폭발!","토(土) 기운 강함 → 안정과 재물운","금(金) 기운 강함 → 결단력 좋음!","수(水) 기운 강함 → 지혜와 흐름","오행 균형 → 행복한 한 해","양기 강함 → 도전 성공","음기 강함 → 내면 성찰"],
    "en": ["Strong Wood → A year of growth!","Strong Fire → Passion explodes!","Strong Earth → Stability & wealth","Strong Metal → Decisive energy!","Strong Water → Wisdom & flow","Balanced elements → Happy year","Strong Yang → Challenge & success","Strong Yin → Inner reflection"],
    "hi": ["Strong Wood → A year of growth!","Strong Fire → Passion explodes!","Strong Earth → Stability & wealth","Strong Metal → Decisive energy!","Strong Water → Wisdom & flow","Balanced elements → Happy year","Strong Yang → Challenge & success","Strong Yin → Inner reflection"],
    "zh": ["木旺：成长之年","火旺：热情爆发","土旺：稳定与财运","金旺：果断有力","水旺：智慧与顺流","五行平衡：幸福之年","阳气强：挑战成功","阴气强：内省成长"],
    "ru": ["Strong Wood → A year of growth!","Strong Fire → Passion explodes!","Strong Earth → Stability & wealth","Strong Metal → Decisive energy!","Strong Water → Wisdom & flow","Balanced elements → Happy year","Strong Yang → Challenge & success","Strong Yin → Inner reflection"],
    "ja": ["木が強い→成長の年","火が強い→情熱の年","土が強い→安定と金運","金が強い→決断力","水が強い→知恵と流れ","バランス→幸福の年","陽が強い→挑戦成功","陰が強い→内省"]
}

TAROT_CARDS = {
    "The Fool": {"ko":"바보 - 새로운 시작, 모험","en":"New beginnings, adventure","hi":"New beginnings, adventure","zh":"新的开始、冒险","ru":"New beginnings, adventure","ja":"新しい始まり・冒険"},
    "The Magician": {"ko":"마법사 - 집중, 능력 발휘","en":"Skill, focus","hi":"Skill, focus","zh":"专注与能力","ru":"Skill, focus","ja":"集中と実現力"},
    "The High Priestess": {"ko":"여사제 - 직감, 내면","en":"Intuition, inner voice","hi":"Intuition, inner voice","zh":"直觉与内在","ru":"Intuition, inner voice","ja":"直感と内面"},
    "The Empress": {"ko":"여제 - 풍요, 창작","en":"Abundance, creativity","hi":"Abundance, creativity","zh":"丰盛与创造","ru":"Abundance, creativity","ja":"豊かさ・創造"},
    "The Emperor": {"ko":"황제 - 안정, 구조","en":"Stability, structure","hi":"Stability, structure","zh":"稳定与秩序","ru":"Stability, structure","ja":"安定・秩序"},
    "The Lovers": {"ko":"연인 - 사랑, 선택","en":"Love, choices","hi":"Love, choices","zh":"爱情与选择","ru":"Love, choices","ja":"愛と選択"},
    "The Star": {"ko":"별 - 희망, 치유","en":"Hope, healing","hi":"Hope, healing","zh":"希望与疗愈","ru":"Hope, healing","ja":"希望・癒し"},
    "The Sun": {"ko":"태양 - 행복, 성공","en":"Joy, success","hi":"Joy, success","zh":"快乐与成功","ru":"Joy, success","ja":"幸福・成功"},
    "The World": {"ko":"세계 - 완성, 성취","en":"Completion, achievement","hi":"Completion, achievement","zh":"完成与成就","ru":"Completion, achievement","ja":"完成・達成"}
}


# =========================================
# 3) Fortune DB load (optional)
# =========================================
def _safe_read_json(fp: Path):
    try:
        with open(fp, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

@st.cache_data
def load_fortune_db(lang: str):
    fp = Path(__file__).parent / "data" / f"fortunes_{lang}.json"
    if fp.exists():
        db = _safe_read_json(fp)
        if isinstance(db, dict) and "daily" in db:
            return db, True
    return generate_big_db(lang), False

def generate_big_db(lang: str):
    # 기본은 간단 템플릿(나중에 언어별 DB 파일로 교체 권장)
    rng = random.Random(20260101 + len(lang))
    daily_pool = [
        "Today is a good day to organize your plans.",
        "Small kindness brings big luck.",
        "Focus on one thing and finish it.",
        "Rest is also productivity.",
        "A message you send first can change the flow.",
        "Avoid impulsive spending today.",
        "Take a short walk to refresh your mind.",
        "Your consistency will be rewarded."
    ]
    daily = {
        "money": daily_pool[:],
        "love": daily_pool[:],
        "health": daily_pool[:],
        "work": daily_pool[:],
        "relationship": daily_pool[:],
        "study": daily_pool[:],
        "travel": daily_pool[:],
        "mindset": daily_pool[:]
    }
    yearly = {"general": daily_pool[:]}

    combo = {"zodiac_mbti": ["{zodiac} + {mbti_desc}: Today, try 'plan → execute' in one shot!"] * 40}
    lucky = {
        "colors": ["Gold", "Red", "Blue", "Green", "Purple"],
        "items": ["Notebook", "Card wallet", "Perfume", "Power bank", "Umbrella"],
        "tips": daily_pool[:]
    }
    # 한국어만 살짝 자연스럽게
    if lang == "ko":
        daily_ko = [
            "오늘은 계획을 정리하면 운이 더 좋아져요.",
            "작은 친절이 큰 행운을 불러와요.",
            "한 가지에 집중해서 끝내보세요.",
            "휴식도 생산성이에요.",
            "먼저 보내는 연락이 흐름을 바꿔요.",
            "충동구매만 피하면 돈운이 좋아요.",
            "가벼운 산책으로 머리를 환기해요.",
            "꾸준함이 보상으로 돌아와요."
        ]
        for k in daily:
            daily[k] = daily_ko[:]
        yearly["general"] = daily_ko[:]
        combo["zodiac_mbti"] = ["{zodiac} + {mbti_desc}: 오늘은 ‘정리→실행’이 핵심!"] * 40
        lucky["items"] = ["작은 노트", "카드지갑", "미니 향수", "보조배터리", "우산"]

    return {"daily": daily, "yearly": yearly, "combo": combo, "lucky": lucky}


# =========================================
# 4) Utils
# =========================================
def get_zodiac(year: int, lang: str):
    if not (1900 <= year <= 2030):
        return None
    idx = (year - 4) % 12
    return ZODIAC_LIST.get(lang, ZODIAC_LIST["en"])[idx]

def get_saju(y: int, m: int, d: int, lang: str):
    arr = SAJU_MSGS.get(lang, SAJU_MSGS["en"])
    return arr[(y + m + d) % len(arr)]

def stable_rng(name: str, y: int, m: int, d: int, mbti: str, lang: str):
    key = f"{lang}|{name}|{y:04d}-{m:02d}-{d:02d}|{mbti}"
    seed = abs(hash(key)) % (10**9)
    return random.Random(seed)


# =========================================
# 5) Streamlit setup
# =========================================
st.set_page_config(page_title="2026 Fortune", layout="centered")

# session defaults
if "lang" not in st.session_state:
    st.session_state.lang = "ko"
if "result" not in st.session_state:
    st.session_state.result = False
if "name" not in st.session_state:
    st.session_state.name = ""
if "birthdate" not in st.session_state:
    st.session_state.birthdate = date(2005, 1, 1)
if "mbti" not in st.session_state:
    st.session_state.mbti = "ENFJ"

# mobile CSS
st.markdown(
    """
    <style>
      header {visibility: hidden;}
      #MainMenu {visibility: hidden;}
      footer {visibility: hidden;}
      .stApp { background: #efe9ff; }
      .block-container {
        padding-top: 10px !important;
        padding-bottom: 30px !important;
        max-width: 760px;
      }
      .title { font-size: 28px; font-weight: 900; color:#2b2b2b; text-align:center; margin: 14px 0 4px;}
      .subtitle { font-size: 14px; font-weight: 700; color:#555; text-align:center; margin: 0 0 14px;}
      .card {
        background: rgba(255,255,255,0.80);
        border: 1px solid rgba(140,120,200,0.25);
        border-radius: 18px;
        padding: 16px;
        box-shadow: 0 10px 22px rgba(0,0,0,0.08);
        margin: 10px 0 16px;
      }
      .card p { margin: 6px 0; line-height: 1.65; font-size: 14.5px; color:#2b2b2b; }
      .kv { font-weight: 900; }
      .bigline { font-size: 20px; font-weight: 900; text-align: center; color: #2b2b2b; margin: 8px 0 4px;}
      @media (max-width: 480px) {.title { font-size: 24px; } .bigline { font-size: 18px; }}
    </style>
    """,
    unsafe_allow_html=True
)

# Language selector (IMPORTANT: no overwrite assignment)
st.radio(
    UI.get(st.session_state.lang, UI["en"])["lang_label"],
    LANG_KEYS,
    format_func=lambda k: LANG_OPTIONS[k],
    key="lang",
    horizontal=True
)
lang = st.session_state.lang
t = UI.get(lang, UI["en"])
APP_URL = "https://my-fortune.streamlit.app"


# =========================================
# 6) Input screen
# =========================================
if not st.session_state.result:
    st.markdown(f"<div class='title'>{t['title']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='subtitle'>{t['subtitle']}</div>", unsafe_allow_html=True)

    st.session_state.name = st.text_input(t["name_label"], value=st.session_state.name)

    st.session_state.birthdate = st.date_input(
        t["birth_label"],
        value=st.session_state.birthdate,
        min_value=date(1900, 1, 1),
        max_value=date(2030, 12, 31),
    )

    mbti_mode = st.radio(t["mbti_mode"], [t["mbti_direct"], t["mbti_test"]], horizontal=True)

    # Direct MBTI
    if mbti_mode == t["mbti_direct"]:
        st.session_state.mbti = st.selectbox("MBTI", sorted(MBTIS.get(lang, MBTIS["en"]).keys()))
        if st.button(t["btn_view"], use_container_width=True):
            st.session_state.result = True
            st.rerun()

    # 12-question Test (✅ language 적용)
    else:
        st.caption(t["test_caption"])

        tq = TEST_Q.get(lang, TEST_Q["en"])  # ✅ 핵심: 언어별 문항 사용

        score_ei = score_sn = score_tf = score_jp = 0

        st.subheader(t["sec_ei"])
        for i, (q, a, b) in enumerate(tq["EI"]):
            if st.radio(q, [a, b], key=f"ei_{lang}_{i}") == a:
                score_ei += 1

        st.subheader(t["sec_sn"])
        for i, (q, a, b) in enumerate(tq["SN"]):
            if st.radio(q, [a, b], key=f"sn_{lang}_{i}") == a:
                score_sn += 1

        st.subheader(t["sec_tf"])
        for i, (q, a, b) in enumerate(tq["TF"]):
            if st.radio(q, [a, b], key=f"tf_{lang}_{i}") == a:
                score_tf += 1

        st.subheader(t["sec_jp"])
        for i, (q, a, b) in enumerate(tq["JP"]):
            if st.radio(q, [a, b], key=f"jp_{lang}_{i}") == a:
                score_jp += 1

        if st.button(t["btn_view_test"], use_container_width=True):
            mbti = ""
            mbti += "E" if score_ei >= 2 else "I"
            mbti += "S" if score_sn >= 2 else "N"
            mbti += "T" if score_tf >= 2 else "F"
            mbti += "J" if score_jp >= 2 else "P"
            st.session_state.mbti = mbti
            st.session_state.result = True
            st.rerun()


# =========================================
# 7) Result screen
# =========================================
if st.session_state.result:
    y = st.session_state.birthdate.year
    m = st.session_state.birthdate.month
    d = st.session_state.birthdate.day
    name = st.session_state.name.strip()
    mbti = st.session_state.mbti

    zodiac = get_zodiac(y, lang)
    if zodiac is None:
        st.error(t["error_year"])
        if st.button(t["reset_btn"], use_container_width=True):
            st.session_state.result = False
            st.rerun()
        st.stop()

    mbti_desc = MBTIS.get(lang, MBTIS["en"]).get(mbti, mbti)
    saju = get_saju(y, m, d, lang)

    db, _ = load_fortune_db(lang)
    rng = stable_rng(name, y, m, d, mbti, lang)

    daily_categories = list(db["daily"].keys())
    today_msg = rng.choice(db["daily"][rng.choice(daily_categories)])
    tomorrow_msg = rng.choice(db["daily"][rng.choice(daily_categories)])
    overall = rng.choice(db["yearly"]["general"])
    combo_comment = rng.choice(db["combo"]["zodiac_mbti"]).format(zodiac=zodiac, mbti_desc=mbti_desc, mbti=mbti)
    lucky_color = rng.choice(db["lucky"]["colors"])
    lucky_item = rng.choice(db["lucky"]["items"])
    tip = rng.choice(db["lucky"]["tips"])

    name_display = (f"{name}" + ("님의" if lang == "ko" else "")) if name else ""
    line_head = f"{name_display} {zodiac} · {mbti}" if name_display else f"{zodiac} · {mbti}"

    st.markdown(f"<div class='title'>{t['title']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='bigline'>🔮 {line_head}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='subtitle'>{t['combo']}</div>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="card">
          <p><span class="kv">✨ {t['zodiac_title']}</span>: {zodiac}</p>
          <p><span class="kv">🧠 {t['mbti_title']}</span>: {mbti_desc} ({mbti})</p>
          <p><span class="kv">🍀 {t['saju_title']}</span>: {saju}</p>
          <hr style="border:none;height:1px;background:rgba(120,100,180,0.18);margin:12px 0;">
          <p><span class="kv">💗 {t['today_title']}</span>: {today_msg}</p>
          <p><span class="kv">🌙 {t['tomorrow_title']}</span>: {tomorrow_msg}</p>
          <hr style="border:none;height:1px;background:rgba(120,100,180,0.18);margin:12px 0;">
          <p><span class="kv">💝 {t['overall_title']}</span>: {overall}</p>
          <p><span class="kv">💬 {t['combo_title']}</span>: {combo_comment}</p>
          <p><span class="kv">🎨 {t['lucky_color_title']}</span>: {lucky_color} &nbsp; | &nbsp;
             <span class="kv">🧿 {t['lucky_item_title']}</span>: {lucky_item}</p>
          <p><span class="kv">✅ {t['tip_title']}</span>: {tip}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # tarot
    with st.expander(t["tarot_btn"], expanded=False):
        tarot_rng = random.Random(abs(hash(f"tarot|{datetime.now().strftime('%Y%m%d')}|{name}|{mbti}|{lang}")) % (10**9))
        tarot_card = tarot_rng.choice(list(TAROT_CARDS.keys()))
        tarot_meaning = TAROT_CARDS[tarot_card].get(lang, TAROT_CARDS[tarot_card]["en"])
        st.markdown(
            f"""
            <div class="card" style="text-align:center;">
              <p style="font-weight:900; color:#7c3aed;">{t["tarot_title"]}</p>
              <p style="font-size:22px; font-weight:900; margin-top:6px;">{tarot_card}</p>
              <p style="margin-top:8px;">{tarot_meaning}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # share text
    share_text = (
        f"{line_head}\n"
        f"{t['combo']}\n\n"
        f"{t['today_title']}: {today_msg}\n"
        f"{t['tomorrow_title']}: {tomorrow_msg}\n\n"
        f"{t['overall_title']}: {overall}\n"
        f"{t['combo_title']}: {combo_comment}\n"
        f"{t['lucky_color_title']}: {lucky_color} | {t['lucky_item_title']}: {lucky_item}\n"
        f"{t['tip_title']}: {tip}\n\n"
        f"{APP_URL}"
    )

    share_payload = json.dumps(share_text, ensure_ascii=False)
    share_title_payload = json.dumps(t["share_title"], ensure_ascii=False)
    fail_copy_payload = json.dumps(t["share_fail_copy"], ensure_ascii=False)
    manual_prompt_payload = json.dumps(t["share_manual_prompt"], ensure_ascii=False)
    cancel_payload = json.dumps(t["share_cancel"], ensure_ascii=False)

    components.html(
        f"""
        <div style="text-align:center; margin:22px 0 10px;">
          <button onclick="doShare()"
            style="background:#7c3aed; color:#ffffff; padding:16px 64px; border:none; border-radius:999px;
                   font-size:1.1em; font-weight:900; box-shadow: 0 8px 25px rgba(124,58,237,0.35);
                   cursor:pointer;">
            {t["share_btn"]}
          </button>
        </div>

        <script>
        async function doShare() {{
          const text = {share_payload};
          const title = {share_title_payload};

          try {{
            if (navigator.share) {{
              await navigator.share({{ title: title, text: text }});
              return;
            }}

            if (navigator.clipboard && navigator.clipboard.writeText) {{
              await navigator.clipboard.writeText(text);
              alert({fail_copy_payload});
              return;
            }}

            prompt({manual_prompt_payload}, text);

          }} catch (e) {{
            alert({cancel_payload});
            try {{
              if (navigator.clipboard && navigator.clipboard.writeText) {{
                await navigator.clipboard.writeText(text);
              }}
            }} catch (_) {{}}
          }}
        }}
        </script>
        """,
        height=110
    )

    if st.button(t["reset_btn"], use_container_width=True):
        st.session_state.result = False
        st.rerun()
