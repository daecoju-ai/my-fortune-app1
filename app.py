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
    "ja": "日本語",
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
        "share_fail_copy": "공유가 지원되지 않아 텍스트를 복사했어요!\n카톡에 붙여넣기 해주세요.",
        "share_manual_prompt": "아래 내용을 복사해서 카톡에 붙여넣기 해주세요:",
        "share_cancel": "공유가 취소되었거나 지원되지 않아요.\n복사 후 붙여넣기 해주세요.",
        "db_tools_title": "📦 운세 DB 다운로드/업로드(추천)",
        "db_tools_desc": "아래에서 이 언어의 운세 DB(JSON)를 다운로드해서 GitHub에 올리면, 앱이 DB를 읽어 더 다양하게 보여줘요.",
        "download_db_btn": "이 언어 DB(JSON) 다운로드",
        "db_path_hint": "다운받은 파일을 GitHub에 data/fortunes_{lang}.json 으로 업로드하세요.",
        "db_status_external": "✅ 외부 DB 사용 중 (data 폴더 JSON 읽음)",
        "db_status_generated": "⚠️ 외부 DB 파일이 없어서 자동 생성 DB로 동작 중",
        "ad_badge": "제휴 혜택",
        "ad_title": "렌탈 상담 최대 페이백",
        "ad_sub": "정수기·비데·공기청정기·안마의자",
        "ad_chip_1": "제휴카드 시 월 0원~",
        "ad_chip_2": "설치당일 최대 50만원",
        "ad_chip_3": "사은품 + 빠른설치",
        "ad_cta": "다나눔렌탈 보러가기",
        "ad_disclaimer": "광고",
    },
    "en": {
        "title": "⭐ 2026 Fortune ⭐",
        "subtitle": "Zodiac + MBTI + Today/Tomorrow Luck",
        "lang_label": "Language",
        "name_label": "Name (shown in result)",
        "birth_label": "Birth date",
        "mbti_mode": "How to do MBTI?",
        "mbti_direct": "Select directly",
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
        "share_fail_copy": "Sharing isn't supported, so the text was copied.\nPaste it in your messenger.",
        "share_manual_prompt": "Copy and paste this text:",
        "share_cancel": "Sharing canceled or not supported.\nPlease copy & paste.",
        "db_tools_title": "📦 Fortune DB download/upload",
        "db_tools_desc": "Download DB(JSON) for this language and upload it to GitHub so the app can read it.",
        "download_db_btn": "Download DB(JSON) for this language",
        "db_path_hint": "Upload as data/fortunes_{lang}.json",
        "db_status_external": "✅ External DB loaded (from data/ JSON)",
        "db_status_generated": "⚠️ No external DB file, using generated DB",
        "ad_badge": "Partner Deal",
        "ad_title": "Max Cashback for Rental",
        "ad_sub": "Purifier · Bidet · Air Purifier · Massage Chair",
        "ad_chip_1": "From 0 won/month",
        "ad_chip_2": "Up to 500,000 won",
        "ad_chip_3": "Gifts + Fast setup",
        "ad_cta": "Go to Dananum Rental",
        "ad_disclaimer": "Ad",
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
        "share_fail_copy": "Sharing isn't supported here, so the text was copied.\nPlease paste it in your messenger.",
        "share_manual_prompt": "Copy and paste this text:",
        "share_cancel": "Sharing canceled or not supported.\nPlease copy & paste.",
        "db_tools_title": "📦 DB डाउनलोड/अपलोड",
        "db_tools_desc": "इस भाषा का DB(JSON) डाउनलोड करें और GitHub में अपलोड करें।",
        "download_db_btn": "इस भाषा का DB(JSON) डाउनलोड",
        "db_path_hint": "GitHub: data/fortunes_{lang}.json",
        "db_status_external": "✅ External DB loaded",
        "db_status_generated": "⚠️ Generated DB in use",
        "ad_badge": "Partner Deal",
        "ad_title": "Max Cashback for Rental",
        "ad_sub": "Purifier · Bidet · Air Purifier · Massage Chair",
        "ad_chip_1": "From 0 won/month",
        "ad_chip_2": "Up to 500,000 won",
        "ad_chip_3": "Gifts + Fast setup",
        "ad_cta": "Go to Dananum Rental",
        "ad_disclaimer": "Ad",
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
        "db_tools_title": "📦 生成/下载 DB",
        "db_tools_desc": "下载该语言 DB(JSON) 并上传到 GitHub。",
        "download_db_btn": "下载该语言 DB(JSON)",
        "db_path_hint": "GitHub：data/fortunes_{lang}.json",
        "db_status_external": "✅ 已加载外部 DB",
        "db_status_generated": "⚠️ 未找到外部 DB，使用自动生成 DB",
        "ad_badge": "合作福利",
        "ad_title": "租赁最大返现",
        "ad_sub": "净水器 · 智能马桶盖 · 空气净化器 · 按摩椅",
        "ad_chip_1": "月租低至 0 韩元",
        "ad_chip_2": "最高 50万韩元",
        "ad_chip_3": "礼品 + 快速安装",
        "ad_cta": "前往 Dananum Rental",
        "ad_disclaimer": "广告",
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
        "db_tools_title": "📦 Скачать/загрузить DB",
        "db_tools_desc": "Скачайте DB(JSON) и загрузите в GitHub.",
        "download_db_btn": "Скачать DB(JSON) для языка",
        "db_path_hint": "GitHub: data/fortunes_{lang}.json",
        "db_status_external": "✅ External DB loaded",
        "db_status_generated": "⚠️ Generated DB in use",
        "ad_badge": "Partner Deal",
        "ad_title": "Max Cashback for Rental",
        "ad_sub": "Purifier · Bidet · Air Purifier · Massage Chair",
        "ad_chip_1": "From 0 won/month",
        "ad_chip_2": "Up to 500,000 won",
        "ad_chip_3": "Gifts + Fast setup",
        "ad_cta": "Go to Dananum Rental",
        "ad_disclaimer": "Ad",
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
        "share_fail_copy": "共有が使えないためテキストをコピーしました。\n貼り付けて送ってください。",
        "share_manual_prompt": "以下をコピーして貼り付けてください：",
        "share_cancel": "共有がキャンセル/非対応です。\nコピーして貼り付けてください。",
        "db_tools_title": "📦 DBダウンロード/アップ",
        "db_tools_desc": "DB(JSON)をダウンロードしてGitHubにアップできます。",
        "download_db_btn": "この言語のDB(JSON)をダウンロード",
        "db_path_hint": "GitHub: data/fortunes_{lang}.json",
        "db_status_external": "✅ External DB loaded",
        "db_status_generated": "⚠️ Generated DB in use",
        "ad_badge": "Partner Deal",
        "ad_title": "Max Cashback for Rental",
        "ad_sub": "Purifier · Bidet · Air Purifier · Massage Chair",
        "ad_chip_1": "From 0 won/month",
        "ad_chip_2": "Up to 500,000 won",
        "ad_chip_3": "Gifts + Fast setup",
        "ad_cta": "Go to Dananum Rental",
        "ad_disclaimer": "Ad",
    }
}

# =========================================
# 1) 12-question MBTI test (PER LANGUAGE)
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
# 2) Zodiac / MBTI / Saju / Tarot
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
# 3) Fortune DB generator (big + 192 combo)
# =========================================
CATEGORIES = ["money", "love", "health", "work", "relationship", "study", "mindset"]

def _uniq_keep_order(items):
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out

def build_generated_db(lang: str):
    if lang == "ko":
        openers = ["오늘은", "지금은", "이번엔", "특히", "의외로", "가볍게"]
        actions = [
            "한 번만 정리해도", "조금만 줄여도", "딱 한 번 확인하면", "작게 시작해도",
            "부담 없이 움직이면", "핵심만 잡으면", "시간을 10분만 써도"
        ]
        effects = [
            "운이 확 올라가요.", "흐름이 좋아져요.", "손해를 줄일 수 있어요.", "기회가 붙어요.",
            "마음이 가벼워져요.", "성과로 이어져요.", "좋은 소식이 따라옵니다."
        ]
        tips = [
            "완벽보다 완료!", "오늘 할 일 1개만 끝내기", "지출/구독 한 번 정리",
            "물 1컵 더 마시기", "스트레칭 1분", "연락은 짧고 따뜻하게",
            "메모로 생각 정리", "10분 산책", "파일/사진 정리", "감사 1줄"
        ]
        yearly = [
            "2026년은 ‘정리 후 확장’의 흐름이 강합니다.",
            "상반기엔 기반을 다지고, 하반기에 성과가 커져요.",
            "인맥과 기회가 연결되는 해입니다.",
            "하나를 꾸준히 밀면 결과가 확실히 나옵니다.",
            "돈은 ‘새는 구멍’을 막는 순간 늘어납니다.",
            "결정은 빠르게, 실행은 꾸준히!"
        ]
        luck_colors = ["골드","레드","블루","그린","퍼플","네이비","민트","핑크","오프화이트","실버","오렌지","버건디"]
        luck_items = ["작은 노트","카드지갑","미니 향수","보조배터리","우산","텀블러","이어폰","손세정제","키링","손거울","볼펜","파우치"]

        cat_base = {
            "money": ["지출을 점검", "구독을 정리", "가격을 비교", "충동구매를 피하기", "정산/환불 확인", "예산을 메모"],
            "love": ["먼저 연락하기", "칭찬 한 마디", "오해 풀기", "말투를 부드럽게", "약속 지키기", "질문 하나 던지기"],
            "health": ["수면을 보강", "목/어깨 스트레칭", "물 한 컵", "가벼운 산책", "카페인 줄이기", "심호흡"],
            "work": ["우선순위를 1개로", "기록을 남기기", "검수 체크", "짧은 회의", "요청을 구체적으로", "마감 정리"],
            "relationship": ["먼저 인사", "경계 정하기", "요약+공감", "부탁은 간단히", "비교 줄이기", "시간 지키기"],
            "study": ["시작 5분", "한 장 요약", "개념도 그리기", "방해 요소 제거", "복습 1번", "장소 바꾸기"],
            "mindset": ["정리하기", "작은 성공 쌓기", "통제 가능한 것에 집중", "감사 한 줄", "도움 요청", "급할수록 천천히"]
        }

        mbti_strength = {
            "E": ["확장력", "추진력", "네트워킹"],
            "I": ["집중력", "깊이", "자기정리"],
            "S": ["현실감", "디테일", "실행력"],
            "N": ["통찰", "상상력", "큰 그림"],
            "T": ["논리", "결정력", "문제해결"],
            "F": ["공감", "배려", "관계감각"],
            "J": ["계획성", "완성도", "정리력"],
            "P": ["유연함", "적응력", "순발력"]
        }

        def mbti_profile(mbti: str):
            parts = []
            for ch in mbti:
                parts.append(random.choice(mbti_strength.get(ch, [])))
            return _uniq_keep_order([p for p in parts if p])

        def combo_sentence(zodiac, mbti, mbti_desc):
            prof = mbti_profile(mbti)
            patterns = [
                f"{zodiac}의 흐름에 {mbti_desc}의 {prof[0]}이(가) 붙어 ‘정리→실행’이 대박이에요.",
                f"{zodiac} 운이 들어올 때 {mbti}의 {prof[1] if len(prof)>1 else prof[0]}으로 ‘선택과 집중’하면 성과가 커져요.",
                f"{zodiac}의 기회운을 {mbti_desc}의 {prof[2] if len(prof)>2 else prof[0]}이(가) 현실 성과로 바꿔줘요.",
                f"올해 {zodiac}는 {mbti}처럼 ‘속도보다 방향’으로 가면 운이 붙습니다.",
                f"{zodiac} + {mbti_desc}: 작은 루틴을 만들면 큰 복으로 돌아오는 조합!"
            ]
            return patterns
    else:
        # simple but varied non-KO
        if lang == "zh":
            openers = ["今天", "现在", "这次", "尤其", "意外地", "轻松地"]
            actions = ["只要整理一次", "稍微减少一点", "确认一次", "从小开始", "保持轻松节奏", "抓住关键点", "花10分钟"]
            effects = ["运势会更顺。", "节奏会更好。", "能减少损失。", "机会会靠近。", "心会更轻。", "更容易出成果。", "好消息会跟来。"]
            tips = ["完成比完美重要", "只完成一件重要的事", "整理一次开支/订阅", "多喝一杯水", "拉伸1分钟", "发一条温暖信息",
                    "用备忘录整理思路", "散步10分钟", "整理照片/文件", "写一行感谢"]
            yearly = ["2026年适合先整理，再扩张。", "上半年打基础，下半年收获更大。", "人脉会带来机会。", "持续会产生结果。", "堵住漏财点，钱就会变多。", "快速决定、稳步执行。"]
            luck_colors = ["金","红","蓝","绿","紫","藏青","薄荷","粉","米白","银","橙","酒红"]
            luck_items = ["小本子","卡包","香水","充电宝","雨伞","水杯","耳机","免洗洗手液","钥匙扣","小镜子","笔","收纳袋"]
            cat_base = {
                "money": ["核对支出", "整理订阅", "比价", "避免冲动消费", "确认结算/退款", "记一笔预算"],
                "love": ["先发消息", "给出夸奖", "解开误会", "语气更柔和", "守住小承诺", "问一个好问题"],
                "health": ["补充睡眠", "肩颈拉伸", "多喝水", "短暂散步", "减少咖啡因", "深呼吸"],
                "work": ["只定一个优先级", "留下记录", "多检查一次", "短会更省时", "需求说具体", "整理截止事项"],
                "relationship": ["先打招呼", "设定边界", "总结+共情", "请求简单具体", "少比较", "守时"],
                "study": ["开始5分钟", "一页总结", "画概念图", "去掉干扰", "复习一次", "换个地方"],
                "mindset": ["整理一下", "堆小胜利", "专注可控", "写感谢", "寻求帮助", "慢下来"]
            }
            mbti_strength = {
                "E": ["拓展力","推动力","社交资源"],
                "I": ["专注","深度","自我整理"],
                "S": ["务实","细节","执行力"],
                "N": ["洞察","想象","大局观"],
                "T": ["逻辑","决断","解决问题"],
                "F": ["共情","体贴","关系感"],
                "J": ["规划","完成度","整理力"],
                "P": ["灵活","适应","反应快"]
            }

            def mbti_profile(mbti: str):
                parts = []
                for ch in mbti:
                    parts.append(random.choice(mbti_strength.get(ch, [])))
                return _uniq_keep_order([p for p in parts if p])

            def combo_sentence(zodiac, mbti, mbti_desc):
                prof = mbti_profile(mbti)
                patterns = [
                    f"{zodiac}的机会配上{mbti_desc}的「{prof[0]}」，更容易把好运变成成果。",
                    f"当{zodiac}运势上升时，用{mbti}的「{prof[1] if len(prof)>1 else prof[0]}」做选择与聚焦。",
                    f"{mbti_desc}的「{prof[2] if len(prof)>2 else prof[0]}」会帮你把{zodiac}的流转化为现实进展。",
                    f"{zodiac}+{mbti_desc}：比速度更重要的是方向，稳步更旺。",
                    f"{zodiac}+{mbti_desc}：建立小习惯，会收获大回报。"
                ]
                return patterns
        elif lang == "ja":
            openers = ["今日は", "今は", "今回は", "特に", "意外と", "気楽に"]
            actions = ["一度整理するだけで", "少し減らすだけで", "一回確認すれば", "小さく始めても", "力を抜いて動けば", "要点だけ押さえれば", "10分使うだけで"]
            effects = ["運が上向きます。", "流れが良くなります。", "損を減らせます。", "チャンスが寄ってきます。", "心が軽くなります。", "成果につながりやすい。", "良い知らせが来ます。"]
            tips = ["完璧より完了", "大事なことを1つ終える", "支出/サブスクを1回整理", "水を1杯多く", "ストレッチ1分", "短く温かい連絡",
                    "メモで整理", "10分散歩", "写真/ファイル整理", "感謝を一行"]
            yearly = ["2026年は『整える→広げる』が強い年。", "上半期は基盤、下半期は成果。", "つながりが機会を呼ぶ。", "継続が結果になる。", "漏れを止めると金運が上がる。", "決断は早く、実行は着実に。"]
            luck_colors = ["Gold","Red","Blue","Green","Purple","Navy","Mint","Pink","Off-white","Silver","Orange","Burgundy"]
            luck_items = ["小さなノート","カード財布","ミニ香水","モバイルバッテリー","傘","タンブラー","イヤホン","除菌ジェル","キーホルダー","手鏡","ペン","ポーチ"]
            cat_base = {
                "money": ["支出を見直す", "サブスク整理", "価格比較", "衝動買いを避ける", "精算/返金確認", "簡単に予算メモ"],
                "love": ["先に連絡する", "褒め言葉", "誤解を解く", "言い方を柔らかく", "小さな約束を守る", "良い質問をする"],
                "health": ["睡眠を増やす", "肩首ストレッチ", "水を飲む", "短い散歩", "カフェイン控えめ", "深呼吸"],
                "work": ["優先順位を1つ", "記録を残す", "確認を増やす", "短い会議", "依頼を具体的に", "締切整理"],
                "relationship": ["先に挨拶", "境界線", "要約+共感", "お願いはシンプルに", "比較を減らす", "時間を守る"],
                "study": ["5分だけ始める", "1枚要約", "概念マップ", "邪魔を消す", "復習1回", "場所を変える"],
                "mindset": ["整理する", "小さな成功", "可控に集中", "感謝を一行", "助けを求める", "急がば回れ"]
            }
            mbti_strength = {
                "E": ["拡張力","推進力","交流"],
                "I": ["集中","深さ","自己整理"],
                "S": ["現実感","細部","実行"],
                "N": ["洞察","発想","全体像"],
                "T": ["論理","決断","解決力"],
                "F": ["共感","配慮","関係感"],
                "J": ["計画","整理","完了力"],
                "P": ["柔軟","適応","瞬発"]
            }

            def mbti_profile(mbti: str):
                parts = []
                for ch in mbti:
                    parts.append(random.choice(mbti_strength.get(ch, [])))
                return _uniq_keep_order([p for p in parts if p])

            def combo_sentence(zodiac, mbti, mbti_desc):
                prof = mbti_profile(mbti)
                patterns = [
                    f"{zodiac}の流れに{mbti_desc}の「{prof[0]}」が乗ると、成果に繋がりやすいです。",
                    f"{zodiac}運が来たら、{mbti}の「{prof[1] if len(prof)>1 else prof[0]}」で選択と集中。",
                    f"{mbti_desc}の「{prof[2] if len(prof)>2 else prof[0]}」が{zodiac}の運を現実化します。",
                    f"{zodiac}+{mbti_desc}：速度より方向、着実が吉。",
                    f"{zodiac}+{mbti_desc}：小さな習慣が大きな運を呼びます。"
                ]
                return patterns
        else:
            openers = ["Today", "Right now", "This time", "Especially", "Surprisingly", "Gently"]
            actions = ["a quick cleanup", "a small reduction", "one extra check", "starting small", "moving lightly", "focusing on the key", "spending 10 minutes"]
            effects = ["boosts your luck.", "improves your flow.", "reduces losses.", "pulls opportunities closer.", "makes your mind lighter.", "turns into results.", "brings good news."]
            tips = ["Done over perfect", "Finish one important task", "Clean up one expense/subscription", "Drink one more glass of water",
                    "Stretch for one minute", "Send a short warm message", "Write a quick memo", "Walk for 10 minutes", "Organize photos/files", "Write one gratitude line"]
            yearly = [
                "2026 favors ‘organize first, expand next’.",
                "Build foundations early; results grow later.",
                "Connections create opportunities this year.",
                "Consistency brings clear outcomes.",
                "Stop money leaks and wealth grows.",
                "Decide fast, execute steadily."
            ]
            luck_colors = ["Gold","Red","Blue","Green","Purple","Navy","Mint","Pink","Off-white","Silver","Orange","Burgundy"]
            luck_items = ["Small notebook","Card wallet","Mini perfume","Power bank","Umbrella","Tumbler","Earbuds","Sanitizer","Keychain","Hand mirror","Pen","Pouch"]
            cat_base = {
                "money": ["checking expenses", "cleaning subscriptions", "comparing prices", "avoiding impulse buys", "reviewing refunds", "writing a tiny budget note"],
                "love": ["sending the first message", "giving a small compliment", "clearing a misunderstanding", "softening your tone", "keeping a small promise", "asking one good question"],
                "health": ["sleeping a bit more", "neck/shoulder stretch", "one extra glass of water", "a short walk", "less caffeine", "deep breathing"],
                "work": ["choosing one priority", "leaving a note/record", "one extra review", "a short meeting", "making requests specific", "closing deadlines"],
                "relationship": ["saying hello first", "setting boundaries", "summarizing with empathy", "keeping requests simple", "less comparing", "being on time"],
                "study": ["starting for 5 minutes", "one-page summary", "concept map", "removing distractions", "one review session", "changing your place"],
                "mindset": ["organizing your space", "stacking small wins", "focusing on control", "writing gratitude", "asking for support", "slowing down"]
            }
            mbti_strength = {
                "E": ["reach", "drive", "networking"],
                "I": ["focus", "depth", "self-order"],
                "S": ["practicality", "details", "execution"],
                "N": ["insight", "imagination", "big-picture"],
                "T": ["logic", "decisiveness", "problem-solving"],
                "F": ["empathy", "care", "people-sense"],
                "J": ["planning", "organization", "completion"],
                "P": ["flexibility", "adaptation", "quick-response"]
            }

            def mbti_profile(mbti: str):
                parts = []
                for ch in mbti:
                    parts.append(random.choice(mbti_strength.get(ch, [])))
                return _uniq_keep_order([p for p in parts if p])

            def combo_sentence(zodiac, mbti, mbti_desc):
                prof = mbti_profile(mbti)
                patterns = [
                    f"{zodiac} energy + {mbti_desc}'s {prof[0]} makes ‘plan → execute’ very strong.",
                    f"When {zodiac} luck rises, use {mbti}'s {prof[1] if len(prof)>1 else prof[0]} for focus and gains.",
                    f"{mbti_desc}'s {prof[2] if len(prof)>2 else prof[0]} turns {zodiac} luck into real progress.",
                    f"{zodiac} + {mbti_desc}: direction beats speed—steady wins.",
                    f"{zodiac} + {mbti_desc}: small routines bring big returns."
                ]
                return patterns

    rng = random.Random(12345)
    daily = {}
    for cat in CATEGORIES:
        base_list = cat_base.get(cat, [])
        msgs = []
        for b in base_list:
            for o in openers:
                for a in actions:
                    for e in effects:
                        if lang == "ko":
                            msgs.append(f"{o} {b} {a} {e}")
                        elif lang == "zh":
                            msgs.append(f"{o}{b}，{a}{e}")
                        elif lang == "ja":
                            msgs.append(f"{o}{b}、{a}{e}")
                        else:
                            msgs.append(f"{o}, {b} + {a} {e}")
        rng.shuffle(msgs)
        msgs = _uniq_keep_order(msgs)
        daily[cat] = msgs[:160] if len(msgs) > 160 else msgs

    zlist = ZODIAC_LIST.get(lang, ZODIAC_LIST["en"])
    mkeys = sorted(MBTIS.get(lang, MBTIS["en"]).keys())
    combo_matrix = {}
    for z in zlist:
        combo_matrix[z] = {}
        for mbti in mkeys:
            mbti_desc = MBTIS.get(lang, MBTIS["en"]).get(mbti, mbti)
            combo_matrix[z][mbti] = combo_sentence(z, mbti, mbti_desc)

    db = {
        "daily": daily,
        "yearly": {"general": _uniq_keep_order(yearly)},
        "combo_matrix": combo_matrix,
        "lucky": {
            "colors": _uniq_keep_order(luck_colors),
            "items": _uniq_keep_order(luck_items),
            "tips": _uniq_keep_order(tips),
        }
    }
    return db

# =========================================
# 4) DB loader (data/fortunes_{lang}.json -> else generated)
# =========================================
def _safe_read_json(fp: Path):
    try:
        with open(fp, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def _validate_db(db: dict):
    return isinstance(db, dict) and "daily" in db and "lucky" in db

@st.cache_data
def load_fortune_db(lang: str):
    fp = Path(__file__).parent / "data" / f"fortunes_{lang}.json"
    if fp.exists():
        db = _safe_read_json(fp)
        if _validate_db(db):
            return db, True
    return build_generated_db(lang), False

# =========================================
# 5) Utils
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

def pick_daily(db, rng: random.Random, offset_days: int, zodiac: str, mbti: str):
    day_seed = abs(hash(f"{datetime.now().date().isoformat()}|{offset_days}|{zodiac}|{mbti}")) % (10**9)
    rr = random.Random(day_seed ^ rng.randint(0, 10**9))
    cats = list(db["daily"].keys())
    cat = rr.choice(cats)
    msg = rr.choice(db["daily"][cat])
    return msg

def pick_combo(db, rng: random.Random, zodiac: str, mbti: str, mbti_desc: str):
    cm = db.get("combo_matrix", {})
    if isinstance(cm, dict) and zodiac in cm and mbti in cm[zodiac] and isinstance(cm[zodiac][mbti], list) and cm[zodiac][mbti]:
        return rng.choice(cm[zodiac][mbti])
    return f"{zodiac} + {mbti_desc}: small routines bring big returns."

# =========================================
# 6) Streamlit setup + Mobile UI CSS
# =========================================
st.set_page_config(page_title="2026 Fortune", layout="centered")

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

st.markdown(
    """
    <style>
      header {visibility: hidden;}
      #MainMenu {visibility: hidden;}
      footer {visibility: hidden;}

      /* 모바일 상단 잘림 방지 + 폭 최적화 */
      .block-container {
        padding-top: 12px !important;
        padding-bottom: 36px !important;
        padding-left: 12px !important;
        padding-right: 12px !important;
        max-width: 760px;
      }

      .stApp {
        background: radial-gradient(1200px 800px at 10% 0%, #f6f0ff 0%, #efe9ff 35%, #eaf4ff 100%);
      }

      .title { font-size: 28px; font-weight: 950; color:#1f1f1f; text-align:center; margin: 12px 0 4px; letter-spacing:-0.2px;}
      .subtitle { font-size: 14px; font-weight: 750; color:#4b4b4b; text-align:center; margin: 0 0 14px;}
      .hint { font-size: 12px; color:#666; text-align:center; margin-top: -6px; }

      .card {
        background: rgba(255,255,255,0.88);
        border: 1px solid rgba(124,58,237,0.16);
        border-radius: 18px;
        padding: 16px 16px;
        box-shadow: 0 10px 24px rgba(0,0,0,0.08);
        margin: 10px 0 14px;
      }
      .card p { margin: 6px 0; line-height: 1.65; font-size: 14.7px; color:#202020; }
      .kv { font-weight: 950; }

      .bigline { font-size: 19px; font-weight: 950; text-align: center; color: #202020; margin: 8px 0 2px;}

      /* 광고 카드 */
      .ad-wrap {
        border-radius: 22px;
        padding: 1px;
        background: linear-gradient(135deg, rgba(124,58,237,0.9), rgba(59,130,246,0.85), rgba(236,72,153,0.75));
        box-shadow: 0 14px 34px rgba(17,24,39,0.14);
        margin: 10px 0 16px;
      }
      .ad-card {
        border-radius: 21px;
        padding: 16px;
        background: rgba(255,255,255,0.92);
        position: relative;
        overflow: hidden;
      }
      .ad-badge {
        display:inline-block;
        font-size: 12px;
        font-weight: 900;
        padding: 6px 10px;
        border-radius: 999px;
        background: rgba(124,58,237,0.10);
        color: #6d28d9;
        border: 1px solid rgba(124,58,237,0.18);
      }
      .ad-disclaimer {
        position:absolute;
        top: 12px;
        right: 12px;
        font-size: 11px;
        font-weight: 900;
        padding: 5px 9px;
        border-radius: 999px;
        background: rgba(239,68,68,0.10);
        color: #b91c1c;
        border: 1px solid rgba(239,68,68,0.20);
      }
      .ad-title { font-size: 18px; font-weight: 950; margin: 10px 0 4px; color:#111827; letter-spacing:-0.2px;}
      .ad-sub { font-size: 12.6px; font-weight: 750; margin: 0 0 10px; color:#4b5563; }
      .chips { display:flex; flex-wrap: wrap; gap: 8px; margin: 10px 0 14px; }
      .chip {
        font-size: 12px;
        font-weight: 850;
        padding: 8px 10px;
        border-radius: 999px;
        background: rgba(17,24,39,0.04);
        border: 1px solid rgba(17,24,39,0.08);
        color:#111827;
      }
      .ad-cta {
        display:flex;
        align-items:center;
        justify-content:center;
        width: 100%;
        padding: 12px 14px;
        border-radius: 14px;
        background: linear-gradient(135deg, #7c3aed, #2563eb);
        color: white;
        font-weight: 950;
        font-size: 14.8px;
        text-decoration: none;
        box-shadow: 0 10px 20px rgba(37,99,235,0.25);
      }
      .ad-cta:active { transform: scale(0.99); }

      @media (max-width: 480px) {
        .title { font-size: 24px; }
        .bigline { font-size: 18px; }
        .card { padding: 14px; }
      }
    </style>
    """,
    unsafe_allow_html=True
)

st.radio(
    UI.get(st.session_state.lang, UI["en"])["lang_label"],
    LANG_KEYS,
    format_func=lambda k: LANG_OPTIONS[k],
    key="lang",
    horizontal=True
)

lang = st.session_state.lang
t = UI.get(lang, UI["en"])
APP_URL = "https://my-fortune.streamlit.app"  # 너의 실제 배포 URL로 바꿔도 됨
AD_URL = "https://www.다나눔렌탈.com"

# =========================================
# 7) Beautiful Ad Card (HTML)
# =========================================
def render_ad_card():
    components.html(
        f"""
        <div class="ad-wrap">
          <div class="ad-card">
            <div class="ad-disclaimer">{t["ad_disclaimer"]}</div>
            <span class="ad-badge">✨ {t["ad_badge"]}</span>
            <div class="ad-title">{t["ad_title"]}</div>
            <div class="ad-sub">{t["ad_sub"]}</div>

            <div class="chips">
              <span class="chip">💳 {t["ad_chip_1"]}</span>
              <span class="chip">💸 {t["ad_chip_2"]}</span>
              <span class="chip">🎁 {t["ad_chip_3"]}</span>
            </div>

            <a class="ad-cta" href="{AD_URL}" target="_blank" rel="noopener noreferrer">
              {t["ad_cta"]} ↗
            </a>
          </div>
        </div>
        """,
        height=215,
    )

# =========================================
# 8) Input screen
# =========================================
if not st.session_state.result:
    st.markdown(f"<div class='title'>{t['title']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='subtitle'>{t['subtitle']}</div>", unsafe_allow_html=True)
    render_ad_card()

    st.session_state.name = st.text_input(t["name_label"], value=st.session_state.name)

    st.session_state.birthdate = st.date_input(
        t["birth_label"],
        value=st.session_state.birthdate,
        min_value=date(1900, 1, 1),
        max_value=date(2030, 12, 31),
    )

    mbti_mode = st.radio(t["mbti_mode"], [t["mbti_direct"], t["mbti_test"]], horizontal=True)

    if mbti_mode == t["mbti_direct"]:
        st.session_state.mbti = st.selectbox("MBTI", sorted(MBTIS.get(lang, MBTIS["en"]).keys()))
        if st.button(t["btn_view"], use_container_width=True):
            st.session_state.result = True
            st.rerun()
    else:
        st.caption(t["test_caption"])
        tq = TEST_Q.get(lang, TEST_Q["en"])  # ✅ 언어별 12문항

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
# 9) Result screen
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

    db, used_external = load_fortune_db(lang)
    rng = stable_rng(name, y, m, d, mbti, lang)

    mbti_desc = MBTIS.get(lang, MBTIS["en"]).get(mbti, mbti)
    saju = get_saju(y, m, d, lang)

    today_msg = pick_daily(db, rng, 0, zodiac, mbti)
    tomorrow_msg = pick_daily(db, rng, 1, zodiac, mbti)

    overall_list = db.get("yearly", {}).get("general", [])
    overall = rng.choice(overall_list) if isinstance(overall_list, list) and overall_list else "Good flow in 2026."

    combo_comment = pick_combo(db, rng, zodiac, mbti, mbti_desc)

    lucky_color = rng.choice(db["lucky"]["colors"]) if db.get("lucky", {}).get("colors") else "Gold"
    lucky_item = rng.choice(db["lucky"]["items"]) if db.get("lucky", {}).get("items") else "Notebook"
    tip = rng.choice(db["lucky"]["tips"]) if db.get("lucky", {}).get("tips") else "Done over perfect."

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
          <hr style="border:none;height:1px;background:rgba(124,58,237,0.12);margin:12px 0;">
          <p><span class="kv">💗 {t['today_title']}</span>: {today_msg}</p>
          <p><span class="kv">🌙 {t['tomorrow_title']}</span>: {tomorrow_msg}</p>
          <hr style="border:none;height:1px;background:rgba(124,58,237,0.12);margin:12px 0;">
          <p><span class="kv">💝 {t['overall_title']}</span>: {overall}</p>
          <p><span class="kv">💬 {t['combo_title']}</span>: {combo_comment}</p>
          <p><span class="kv">🎨 {t['lucky_color_title']}</span>: {lucky_color} &nbsp; | &nbsp;
             <span class="kv">🧿 {t['lucky_item_title']}</span>: {lucky_item}</p>
          <p><span class="kv">✅ {t['tip_title']}</span>: {tip}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 광고 카드 (결과에도 1번 더 노출)
    render_ad_card()

    # tarot
    with st.expander(t["tarot_btn"], expanded=False):
        tarot_rng = random.Random(abs(hash(f"tarot|{datetime.now().strftime('%Y%m%d')}|{name}|{mbti}|{lang}")) % (10**9))
        tarot_card = tarot_rng.choice(list(TAROT_CARDS.keys()))
        tarot_meaning = TAROT_CARDS[tarot_card].get(lang, TAROT_CARDS[tarot_card]["en"])
        st.markdown(
            f"""
            <div class="card" style="text-align:center;">
              <p style="font-weight:950; color:#7c3aed;">{t["tarot_title"]}</p>
              <p style="font-size:22px; font-weight:950; margin-top:6px;">{tarot_card}</p>
              <p style="margin-top:8px;">{tarot_meaning}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # share (text only)
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
        <div style="text-align:center; margin:16px 0 6px;">
          <button onclick="doShare()"
            style="background:#7c3aed; color:#ffffff; padding:16px 64px; border:none; border-radius:999px;
                   font-size:1.06em; font-weight:950; box-shadow: 0 10px 22px rgba(124,58,237,0.30);
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
        height=98
    )

    # DB tools
    with st.expander(t["db_tools_title"], expanded=False):
        st.write(t["db_tools_desc"])
        generated_db = build_generated_db(lang)
        st.download_button(
            t["download_db_btn"],
            data=json.dumps(generated_db, ensure_ascii=False, indent=2).encode("utf-8"),
            file_name=f"fortunes_{lang}.json",
            mime="application/json"
        )
        st.caption(t["db_path_hint"].format(lang=lang))
        st.caption(t["db_status_external"] if used_external else t["db_status_generated"])

    if st.button(t["reset_btn"], use_container_width=True):
        st.session_state.result = False
        st.rerun()
