import streamlit as st
from datetime import datetime, date
import random
import json
from pathlib import Path
import streamlit.components.v1 as components


# =========================================
# 0) 언어 옵션
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
        "db_tools_title": "📦 (초보용) 운세 DB 파일 만들기/다운로드",
        "db_tools_desc": "지금 보이는 문장들을 'DB(JSON 파일)'로 저장해 GitHub에 올리면 더 다양하게 운영할 수 있어요.",
        "download_db_btn": "이 언어 DB(JSON) 다운로드",
        "db_path_hint": "다운받은 파일을 GitHub에 data/fortunes_{lang}.json 으로 업로드하면 DB 기반으로 동작해요."
    },
    "en": {
        "title": "⭐ 2026 Fortune ⭐",
        "subtitle": "Zodiac + MBTI + Today/Tomorrow Luck",
        "lang_label": "Language / 언어",
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
        "db_tools_title": "📦 DB generator/download",
        "db_tools_desc": "Download DB(JSON) and upload to GitHub to run with a real DB.",
        "download_db_btn": "Download DB(JSON) for this language",
        "db_path_hint": "Upload as data/fortunes_{lang}.json"
    },
    "hi": {
        "title": "⭐ 2026 भाग्य ⭐",
        "subtitle": "Zodiac + MBTI + Today/Tomorrow Luck",
        "lang_label": "Language / भाषा",
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
        "db_tools_title": "📦 DB डाउनलोड",
        "db_tools_desc": "DB(JSON) डाउनलोड करके GitHub पर अपलोड कर सकते हैं।",
        "download_db_btn": "इस भाषा का DB(JSON) डाउनलोड",
        "db_path_hint": "GitHub में data/fortunes_{lang}.json के रूप में अपलोड करें।"
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
        "db_tools_desc": "可以下载 DB(JSON) 上传到 GitHub。",
        "download_db_btn": "下载该语言 DB(JSON)",
        "db_path_hint": "上传到 GitHub：data/fortunes_{lang}.json"
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
        "db_tools_title": "📦 Скачать DB",
        "db_tools_desc": "Скачайте DB(JSON) и загрузите в GitHub.",
        "download_db_btn": "Скачать DB(JSON) для языка",
        "db_path_hint": "Загрузите как data/fortunes_{lang}.json"
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
        "db_tools_title": "📦 DBダウンロード",
        "db_tools_desc": "DB(JSON)をダウンロードしてGitHubにアップできます。",
        "download_db_btn": "この言語のDB(JSON)をダウンロード",
        "db_path_hint": "GitHubの data/fortunes_{lang}.json としてアップロード"
    }
}


# =========================================
# 1) 기본 데이터
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
# 2) DB(JSON) 로드 / 없으면 자동 생성
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
    bank = {
        "ko": {
            "open": ["오늘은", "지금은", "이번 흐름은", "오늘의 포인트는", "핵심은"],
            "money_a": ["지출 정리", "고정비 점검", "비교 구매", "환불/정산", "작은 절약", "기록 습관", "충동 억제", "가치 소비"],
            "money_b": ["가 유리해요.", "부터 하면 이득이에요.", "만 해도 흐름이 좋아져요.", "가 돈운을 살려줘요.", "로 손해를 막을 수 있어요."],
            "love_a": ["한 줄 진심", "가벼운 칭찬", "타이밍 좋은 연락", "공감 먼저", "시간 약속", "부드러운 표현", "비교 줄이기", "웃는 표정"],
            "love_b": ["이 관계운을 올려줘요.", "이 분위기를 바꿔요.", "이 오해를 줄여줘요.", "이 신뢰를 키워줘요.", "이 매력으로 보여요."],
            "health_a": ["수면", "수분", "목/어깨 스트레칭", "가벼운 산책", "호흡", "체온 관리", "눈 휴식", "짧은 루틴"],
            "health_b": ["이 컨디션을 좌우해요.", "을 챙기면 하루가 편해요.", "만 해도 피로가 줄어요.", "이 기운을 회복해줘요.", "이 운의 흐름을 바꿔요."],
            "work_a": ["마감 정리", "기록 남기기", "우선순위 재정렬", "협업 요청", "검수 체크", "짧은 회의", "자동화 아이디어", "조건 확인"],
            "work_b": ["가 성과로 이어져요.", "가 실수를 줄여줘요.", "가 인정받는 포인트예요.", "가 시간을 아껴줘요.", "가 스트레스를 낮춰줘요."],
            "rel_a": ["질문하기", "인사 먼저", "오해 바로 풀기", "경계 정하기", "작은 배려", "칭찬 한 마디", "요약+공감", "함께 하기"],
            "rel_b": ["가 관계를 부드럽게 해요.", "가 사람운을 올려줘요.", "가 도움을 불러와요.", "가 갈등을 줄여줘요.", "가 신뢰를 만들어요."],
            "study_a": ["시작 5분", "개념도", "복습", "질문", "한 장 요약", "장소 전환", "방해 요소 제거", "작은 목표"],
            "study_b": ["만 지켜도 충분해요.", "이 효율을 키워줘요.", "이 기억을 오래가게 해요.", "가 집중을 살려줘요.", "이 점수를 올려줘요."],
            "travel_a": ["10분 버퍼", "가까운 외출", "새 루트", "사진 기록", "여유 있는 계획", "보조배터리", "우산", "대체 플랜"],
            "travel_b": ["가 스트레스를 줄여줘요.", "가 만족도를 키워줘요.", "가 돌발 상황을 막아줘요.", "가 좋은 추억이 돼요.", "가 운을 살려줘요."],
            "mind_a": ["완료", "정리", "작은 성공", "비교 줄이기", "통제 가능한 것", "도움 받기", "메모", "감사 1줄"],
            "mind_b": ["를 선택하면 마음이 편해져요.", "만 해도 흐름이 좋아져요.", "가 자신감을 올려줘요.", "가 불안을 줄여줘요.", "가 내일을 가볍게 해요."]
        }
    }

    # 다른 언어는 영어 템플릿을 쓰도록(키에러 방지)
    if lang != "ko":
        bank[lang] = bank["ko"]

    b = bank[lang]
    rng = random.Random(20260101 + len(lang))

    def build_list(kind_a, kind_b, count=24):
        out = []
        for _ in range(count * 2):
            s = f"{rng.choice(b['open'])} {rng.choice(b[kind_a])}{rng.choice(b[kind_b])}"
            out.append(s)
        out = list(dict.fromkeys(out))
        while len(out) < count:
            out.append(f"{rng.choice(b['open'])} {rng.choice(b[kind_a])}{rng.choice(b[kind_b])}")
            out = list(dict.fromkeys(out))
        return out[:count]

    daily = {
        "money": build_list("money_a", "money_b"),
        "love": build_list("love_a", "love_b"),
        "health": build_list("health_a", "health_b"),
        "work": build_list("work_a", "work_b"),
        "relationship": build_list("rel_a", "rel_b"),
        "study": build_list("study_a", "study_b"),
        "travel": build_list("travel_a", "travel_b"),
        "mindset": build_list("mind_a", "mind_b")
    }

    yearly = {
        "general": daily["mindset"][:12],
        "career": daily["work"][:12],
        "money": daily["money"][:12],
        "love": daily["love"][:12]
    }

    combo = {"zodiac_mbti": ["{zodiac} + {mbti_desc} 조합은 ‘정리→실행’이 강해요."] * 40}
    lucky = {
        "colors": ["Gold","Red","Blue","Green","Purple","Silver","Navy","Mint","Pink","Off-white"],
        "items": ["Small notebook","Card wallet","Mini perfume","Power bank","Keychain","Tumbler","Wristwatch","Earbuds","Umbrella","Lip balm"],
        "tips": daily["mindset"][:20]
    }
    return {"daily": daily, "yearly": yearly, "combo": combo, "lucky": lucky}


# =========================================
# 3) 유틸
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
# 4) Streamlit 기본/UI
# =========================================
st.set_page_config(page_title="2026 Fortune", layout="centered")

# ---- 세션 기본값 (중요: 여기서 lang을 강제로 덮어쓰지 않음)
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

# 모바일 최적화 CSS
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
        background: rgba(255,255,255,0.78);
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

# ✅ 언어 선택 (중요: key로만 관리, session_state에 직접 대입 금지)
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
# 5) 입력 화면
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

    if mbti_mode == t["mbti_direct"]:
        st.session_state.mbti = st.selectbox("MBTI", sorted(MBTIS.get(lang, MBTIS["en"]).keys()))
        if st.button(t["btn_view"], use_container_width=True):
            st.session_state.result = True
            st.rerun()

    else:
        st.caption(t["test_caption"])

        q_ei = [
            ("If plans come up suddenly?", "Awesome! Let's go (E)", "I'd rather stay home (I)"),
            ("You recharge by…", "Meeting people (E)", "Being alone (I)"),
            ("When talking, you…", "Think while speaking (E)", "Think first, then speak (I)")
        ]
        q_sn = [
            ("When seeing new info?", "Facts & details (S)", "Possibilities & meaning (N)"),
            ("You prefer explanations with…", "Examples & specifics (S)", "Big picture (N)"),
            ("Your ideas are usually…", "Proven methods (S)", "New approaches (N)")
        ]
        q_tf = [
            ("In conflict, you choose…", "Logic & principles (T)", "Care & harmony (F)"),
            ("Your decision base is…", "Efficiency & accuracy (T)", "Values & feelings (F)"),
            ("When giving feedback…", "Direct & clear (T)", "Gentle & considerate (F)")
        ]
        q_jp = [
            ("Your schedule style?", "Planned (J)", "Spontaneous (P)"),
            ("Before a deadline…", "Finish early (J)", "Rush at the end (P)"),
            ("Tidying up is…", "Keep it neat (J)", "Only when needed (P)")
        ]

        ei = sn = tf = jp = 0

        st.subheader(t["sec_ei"])
        for i, (q, a, b) in enumerate(q_ei):
            if st.radio(q, [a, b], key=f"ei_{lang}_{i}") == a:
                ei += 1

        st.subheader(t["sec_sn"])
        for i, (q, a, b) in enumerate(q_sn):
            if st.radio(q, [a, b], key=f"sn_{lang}_{i}") == a:
                sn += 1

        st.subheader(t["sec_tf"])
        for i, (q, a, b) in enumerate(q_tf):
            if st.radio(q, [a, b], key=f"tf_{lang}_{i}") == a:
                tf += 1

        st.subheader(t["sec_jp"])
        for i, (q, a, b) in enumerate(q_jp):
            if st.radio(q, [a, b], key=f"jp_{lang}_{i}") == a:
                jp += 1

        if st.button(t["btn_view_test"], use_container_width=True):
            mbti = ""
            mbti += "E" if ei >= 2 else "I"
            mbti += "S" if sn >= 2 else "N"
            mbti += "T" if tf >= 2 else "F"
            mbti += "J" if jp >= 2 else "P"
            st.session_state.mbti = mbti
            st.session_state.result = True
            st.rerun()


# =========================================
# 6) 결과 화면
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

    db, used_external = load_fortune_db(lang)
    rng = stable_rng(name, y, m, d, mbti, lang)

    daily_categories = list(db["daily"].keys())
    cat_today = rng.choice(daily_categories)
    cat_tomorrow = rng.choice(daily_categories)

    today_msg = rng.choice(db["daily"][cat_today])
    tomorrow_msg = rng.choice(db["daily"][cat_tomorrow])

    overall = rng.choice(db["yearly"]["general"]) if "yearly" in db and "general" in db["yearly"] else rng.choice(db["daily"]["mindset"])
    combo_template = rng.choice(db["combo"]["zodiac_mbti"]) if "combo" in db and "zodiac_mbti" in db["combo"] else "{zodiac} + {mbti_desc}"
    combo_comment = combo_template.format(zodiac=zodiac, mbti=mbti, mbti_desc=mbti_desc)

    lucky_color = rng.choice(db["lucky"]["colors"]) if "lucky" in db and "colors" in db["lucky"] else "Gold"
    lucky_item = rng.choice(db["lucky"]["items"]) if "lucky" in db and "items" in db["lucky"] else "Notebook"
    tip = rng.choice(db["lucky"]["tips"]) if "lucky" in db and "tips" in db["lucky"] else rng.choice(db["daily"]["mindset"])

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

    # 타로
    with st.expander(t["tarot_btn"], expanded=False):
        tarot_rng = random.Random(abs(hash(f"tarot|{datetime.now().strftime('%Y%m%d')}|{name}|{mbti}|{lang}")) % (10**9))
        tarot_card = tarot_rng.choice(list(TAROT_CARDS.keys()))
        tarot_meaning = TAROT_CARDS[tarot_card].get(lang, TAROT_CARDS[tarot_card]["en"])
        st.markdown(
            f"""
            <div class="card" style="text-align:center;">
              <p style="font-weight:900; color:#7c3aed;">{t['tarot_title']}</p>
              <p style="font-size:22px; font-weight:900; margin-top:6px;">{tarot_card}</p>
              <p style="margin-top:8px;">{tarot_meaning}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 공유(텍스트)
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

    share_payload = json.dumps(share_text)
    share_title_payload = json.dumps(t["share_title"])
    fail_copy_payload = json.dumps(t["share_fail_copy"])
    manual_prompt_payload = json.dumps(t["share_manual_prompt"])
    cancel_payload = json.dumps(t["share_cancel"])

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
              await navigator.share({{
                title: title,
                text: text
              }});
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

    st.markdown(f"<div style='text-align:center; color:#6b6b6b; font-size:12px; margin-top:6px;'>{APP_URL}</div>", unsafe_allow_html=True)

    # DB 다운로드 도구
    with st.expander(t["db_tools_title"], expanded=False):
        st.write(t["db_tools_desc"])
        db_json_bytes = json.dumps(db, ensure_ascii=False, indent=2).encode("utf-8")
        st.download_button(
            t["download_db_btn"],
            data=db_json_bytes,
            file_name=f"fortunes_{lang}.json",
            mime="application/json"
        )
        st.caption(t["db_path_hint"].format(lang=lang))
        st.caption(f"현재 상태: {'✅ 외부 DB 사용 중' if used_external else '⚠️ 파일이 없어서 자동 생성 DB 사용 중'}")

    # reset (clear() 금지)
    if st.button(t["reset_btn"], use_container_width=True):
        st.session_state.result = False
        st.rerun()
