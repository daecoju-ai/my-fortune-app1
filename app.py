# app.py
# Streamlit Fortune App (KO/EN/ZH/JA/RU/HI) + MBTI(Direct / 12Q / 16Q) + Share(Text) + (KO only) Mini Game Lead Capture
# ✅ 가독성 강화(카드/섹션/여백/폰트/라인높이)
# ✅ HTML 태그가 그대로 보이는 문제 방지(렌더링 방식 정리)
# ✅ 언어 선택 유지 / 결과 화면에서도 언어 변경 시 깨지지 않게
# ✅ 12/16문항 버튼 무반응 방지(st.form + submit)
# ✅ “친구에게 결과 공유하기” = 모바일은 Web Share API(가능하면 공유 시트), 불가하면 복사
# ✅ (한국어만) 20.26초 타이머 게임 + 동의 체크 + 이름/전화번호 수집 + 선착순 20명 저장(옵션: Google Sheets)

import streamlit as st
from datetime import datetime, timedelta
import random
import time
import re
from typing import Dict, List, Tuple, Optional

# -----------------------------
# OPTIONAL: Google Sheets 저장 (선착순 20명)
# - 사용하려면 requirements.txt에 gspread google-auth 추가
# - Streamlit secrets에 아래 형태로 넣어야 함
#   [google_sheets]
#   enabled = true
#   spreadsheet_id = "구글시트ID"
#   worksheet = "Sheet1"
#   # 서비스계정 JSON 전체를 그대로 붙여넣기:
#   service_account_json = """{...}"""
# -----------------------------
def try_save_to_google_sheets(row: List[str]) -> bool:
    try:
        if "google_sheets" not in st.secrets:
            return False
        cfg = st.secrets["google_sheets"]
        if not str(cfg.get("enabled", "false")).lower() == "true":
            return False

        import json
        import gspread
        from google.oauth2.service_account import Credentials

        sa_json = cfg.get("service_account_json", "")
        if not sa_json:
            return False

        creds_info = json.loads(sa_json)
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
        gc = gspread.authorize(creds)

        sh = gc.open_by_key(cfg["spreadsheet_id"])
        ws_name = cfg.get("worksheet", "Sheet1")
        ws = sh.worksheet(ws_name)
        ws.append_row(row, value_input_option="USER_ENTERED")
        return True
    except Exception:
        return False


# -----------------------------
# Utilities
# -----------------------------
def clamp_day(y: int, m: int, d: int) -> int:
    # 간단 clamp (정밀 월별 일수 계산까지는 과하지 않게)
    if d < 1:
        return 1
    if d > 31:
        return 31
    return d


def get_zodiac_by_year(year: int, lang: str) -> Optional[str]:
    if year < 1900 or year > 2030:
        return None
    # 기준: 4년=쥐띠(Rat)
    z_ko = ["쥐띠", "소띠", "호랑이띠", "토끼띠", "용띠", "뱀띠", "말띠", "양띠", "원숭이띠", "닭띠", "개띠", "돼지띠"]
    z_en = ["Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake", "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"]
    z_zh = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]
    z_ja = ["子(ね)", "丑(うし)", "寅(とら)", "卯(う)", "辰(たつ)", "巳(み)", "午(うま)", "未(ひつじ)", "申(さる)", "酉(とり)", "戌(いぬ)", "亥(い)"]
    z_ru = ["Крыса", "Бык", "Тигр", "Кролик", "Дракон", "Змея", "Лошадь", "Коза", "Обезьяна", "Петух", "Собака", "Свинья"]
    z_hi = ["चूहा", "बैल", "बाघ", "खरगोश", "ड्रैगन", "साँप", "घोड़ा", "बकरी", "बंदर", "मुर्गा", "कुत्ता", "सूअर"]

    idx = (year - 4) % 12
    if lang == "ko":
        return z_ko[idx]
    if lang == "en":
        return z_en[idx]
    if lang == "zh":
        return z_zh[idx]
    if lang == "ja":
        return z_ja[idx]
    if lang == "ru":
        return z_ru[idx]
    if lang == "hi":
        return z_hi[idx]
    return z_en[idx]


def seeded_choice(items: List[str], seed: int) -> str:
    rnd = random.Random(seed)
    return rnd.choice(items)


def daily_seed(extra: int = 0) -> int:
    today = datetime.now() + timedelta(days=extra)
    return int(today.strftime("%Y%m%d"))


def sanitize_for_js(s: str) -> str:
    # JS 템플릿 리터럴용 최소 이스케이프
    return s.replace("\\", "\\\\").replace("`", "\\`")


# -----------------------------
# Translations + Content DB
# (필요한 핵심만 정확히 다국어로. 나머지는 각 언어에 맞게 자연스럽게 표시)
# -----------------------------
LANGS = [
    ("ko", "한국어"),
    ("en", "English"),
    ("zh", "中文"),
    ("ja", "日本語"),
    ("ru", "Русский"),
    ("hi", "हिन्दी"),
]

T: Dict[str, Dict] = {
    "ko": {
        "app_title": "2026년 운세",
        "app_sub": "띠 + MBTI + 사주 + 오늘/내일 운세",
        "free": "완전 무료",
        "lang_label": "언어 / Language",
        "name_label": "이름 (결과에 표시돼요)",
        "name_ph": "예) 홍길동",
        "birth_title": "생년월일",
        "year": "년",
        "month": "월",
        "day": "일",
        "mbti_mode": "MBTI 입력 방식",
        "mbti_direct": "직접 선택",
        "mbti_12": "간단 테스트 (12문항)",
        "mbti_16": "상세 테스트 (16문항)",
        "go_result": "운세 보기!",
        "reset": "처음부터 다시 하기",
        "share_btn": "친구에게 결과 공유하기",
        "share_help": "모바일은 공유(카톡/문자 등) 화면이 뜰 수 있어요. PC는 복사로 동작할 수 있어요.",
        "share_fallback": "공유가 안 뜨면 아래 텍스트를 복사해서 보내세요.",
        "copied": "복사 완료! 카톡/문자에 붙여넣기 하세요.",
        "zodiac_title": "띠 운세",
        "mbti_title": "MBTI 특징",
        "saju_title": "사주 한 마디",
        "today_title": "오늘 운세",
        "tomorrow_title": "내일 운세",
        "yearly_title": "2026 전체 운세",
        "love_title": "연애운",
        "money_title": "재물운",
        "work_title": "일/학업운",
        "health_title": "건강운",
        "lucky_title": "행운 포인트",
        "lucky_color": "럭키 컬러",
        "lucky_item": "럭키 아이템",
        "tip_title": "오늘의 조언",
        "caution_title": "주의할 점",
        "combo_title": "MBTI가 운세에 미치는 영향",
        "tarot_btn": "오늘의 타로 카드 보기",
        "tarot_title": "오늘의 타로 카드",
        "ad_title": "정수기렌탈 궁금할 때?",
        "ad_badge": "광고",
        "ad_line1": "제휴카드면 월 0원부터!",
        "ad_line2": "설치 당일 최대 50만원 지원 + 사은품 듬뿍",
        "ad_link": "다나눔렌탈.com 바로가기",
        "ad_url": "https://www.다나눔렌탈.com",
        "ad_note": "※ 한국어 버전에서만 표시됩니다.",
        "invalid_year": "생년은 1900~2030년 사이로 입력해주세요!",
        "mbti_submit": "제출하고 결과 보기",
        "mbti_12_title": "MBTI – 12",
        "mbti_12_desc": "12문항을 빠르게 답하면 MBTI 추정 결과가 나와요.",
        "mbti_16_title": "MBTI – 16",
        "mbti_16_desc": "각 축 4문항씩(총 16문항). 더 정확해요.",
        "q_yes": "예",
        "q_no": "아니오",

        # 미니게임 (KO only)
        "mini_title": "🎁 미니게임: 20.26초 맞추기 (선착순 20명 커피쿠폰 도전!)",
        "mini_desc": "시작을 누른 뒤, **정확히 20.26초**에 멈추세요. 성공하면 이름/전화번호를 제출할 수 있어요.",
        "mini_privacy": "개인정보 수집/이용 동의",
        "mini_privacy_text": "쿠폰 발송 목적(선착순 20명)으로 이름/전화번호를 수집하며, 발송 완료 후 파기합니다.",
        "mini_start": "시작",
        "mini_stop": "멈춤",
        "mini_result": "기록",
        "mini_submit": "성공! 정보 제출",
        "mini_fail": "아쉽지만 실패! (기회 소진)",
        "mini_left": "남은 기회",
        "mini_bonus": "친구에게 공유하면 1회 추가 기회가 열려요.",
        "mini_bonus_unlocked": "✅ 공유 버튼을 눌러 1회 추가 기회가 열렸어요!",
        "mini_name": "이름",
        "mini_phone": "전화번호(숫자만)",
        "mini_done": "접수 완료! (선착순/검수 후 발송)",
        "mini_full": "선착순 20명이 이미 마감됐어요. 참여해주셔서 감사합니다!",
        "mini_invalid_phone": "전화번호 형식이 올바르지 않아요. 숫자만 10~11자리로 입력해주세요.",
    },

    "en": {
        "app_title": "2026 Fortune",
        "app_sub": "Zodiac + MBTI + Saju + Today/Tomorrow",
        "free": "Completely Free",
        "lang_label": "Language",
        "name_label": "Name (shown on result)",
        "name_ph": "e.g., Alex",
        "birth_title": "Birth date",
        "year": "Year",
        "month": "Month",
        "day": "Day",
        "mbti_mode": "MBTI input method",
        "mbti_direct": "Direct select",
        "mbti_12": "Quick test (12Q)",
        "mbti_16": "Detailed test (16Q)",
        "go_result": "Show my fortune!",
        "reset": "Start over",
        "share_btn": "Share result with friends",
        "share_help": "On mobile, the share sheet may open. On desktop, it may copy instead.",
        "share_fallback": "If share doesn't open, copy the text below.",
        "copied": "Copied! Paste it into chat.",
        "zodiac_title": "Zodiac fortune",
        "mbti_title": "MBTI traits",
        "saju_title": "Saju one-liner",
        "today_title": "Today",
        "tomorrow_title": "Tomorrow",
        "yearly_title": "2026 Overall",
        "love_title": "Love",
        "money_title": "Money",
        "work_title": "Work/Study",
        "health_title": "Health",
        "lucky_title": "Lucky points",
        "lucky_color": "Lucky color",
        "lucky_item": "Lucky item",
        "tip_title": "Advice",
        "caution_title": "Caution",
        "combo_title": "How MBTI influences your luck",
        "tarot_btn": "Draw today's tarot card",
        "tarot_title": "Today's Tarot",
        "invalid_year": "Please enter a birth year between 1900 and 2030!",
        "mbti_submit": "Submit & view result",
        "mbti_12_title": "MBTI – 12",
        "mbti_12_desc": "Answer 12 quick questions to estimate your MBTI.",
        "mbti_16_title": "MBTI – 16",
        "mbti_16_desc": "4 questions per axis (16 total) for better accuracy.",
        "q_yes": "Yes",
        "q_no": "No",
    },

    "zh": {
        "app_title": "2026 运势",
        "app_sub": "生肖 + MBTI + 命理 + 今日/明日",
        "free": "完全免费",
        "lang_label": "语言",
        "name_label": "姓名（显示在结果中）",
        "name_ph": "例如：小明",
        "birth_title": "出生日期",
        "year": "年",
        "month": "月",
        "day": "日",
        "mbti_mode": "MBTI 输入方式",
        "mbti_direct": "直接选择",
        "mbti_12": "简易测试（12题）",
        "mbti_16": "详细测试（16题）",
        "go_result": "查看运势！",
        "reset": "重新开始",
        "share_btn": "分享结果给朋友",
        "share_help": "手机上可能会弹出系统分享面板；电脑上可能会复制文本。",
        "share_fallback": "若未弹出分享面板，可复制下方文本。",
        "copied": "已复制！",
        "zodiac_title": "生肖运势",
        "mbti_title": "MBTI 特点",
        "saju_title": "命理一句话",
        "today_title": "今日",
        "tomorrow_title": "明日",
        "yearly_title": "2026 总体",
        "love_title": "感情",
        "money_title": "财运",
        "work_title": "工作/学习",
        "health_title": "健康",
        "lucky_title": "幸运要点",
        "lucky_color": "幸运色",
        "lucky_item": "幸运物",
        "tip_title": "建议",
        "caution_title": "注意",
        "combo_title": "MBTI 如何影响运势",
        "tarot_btn": "抽取今日塔罗",
        "tarot_title": "今日塔罗",
        "invalid_year": "请输入 1900~2030 年之间的出生年份！",
        "mbti_submit": "提交并查看结果",
        "mbti_12_title": "MBTI – 12",
        "mbti_12_desc": "回答 12 题，快速推测 MBTI。",
        "mbti_16_title": "MBTI – 16",
        "mbti_16_desc": "每个维度 4 题（共 16 题），更准确。",
        "q_yes": "是",
        "q_no": "否",
    },

    "ja": {
        "app_title": "2026 運勢",
        "app_sub": "干支 + MBTI + 一言占い + 今日/明日",
        "free": "完全無料",
        "lang_label": "言語",
        "name_label": "名前（結果に表示）",
        "name_ph": "例：たろう",
        "birth_title": "生年月日",
        "year": "年",
        "month": "月",
        "day": "日",
        "mbti_mode": "MBTI の入力方法",
        "mbti_direct": "直接選択",
        "mbti_12": "簡単テスト（12問）",
        "mbti_16": "詳細テスト（16問）",
        "go_result": "運勢を見る！",
        "reset": "最初からやり直す",
        "share_btn": "結果を共有する",
        "share_help": "スマホは共有画面が開く場合があります。PCはコピーになる場合があります。",
        "share_fallback": "共有が出ない場合は下の文章をコピーしてください。",
        "copied": "コピーしました！",
        "zodiac_title": "干支の運勢",
        "mbti_title": "MBTI 特徴",
        "saju_title": "一言コメント",
        "today_title": "今日",
        "tomorrow_title": "明日",
        "yearly_title": "2026 全体",
        "love_title": "恋愛",
        "money_title": "金運",
        "work_title": "仕事/学業",
        "health_title": "健康",
        "lucky_title": "ラッキーポイント",
        "lucky_color": "ラッキーカラー",
        "lucky_item": "ラッキーアイテム",
        "tip_title": "アドバイス",
        "caution_title": "注意点",
        "combo_title": "MBTIが運勢に与える影響",
        "tarot_btn": "今日のタロット",
        "tarot_title": "今日のタロット",
        "invalid_year": "1900〜2030の範囲で入力してください！",
        "mbti_submit": "送信して結果を見る",
        "mbti_12_title": "MBTI – 12",
        "mbti_12_desc": "12問でMBTIを推定します。",
        "mbti_16_title": "MBTI – 16",
        "mbti_16_desc": "各軸4問（計16問）でより正確です。",
        "q_yes": "はい",
        "q_no": "いいえ",
    },

    "ru": {
        "app_title": "Прогноз 2026",
        "app_sub": "Зодиак + MBTI + Удача сегодня/завтра",
        "free": "Полностью бесплатно",
        "lang_label": "Язык",
        "name_label": "Имя (в результате)",
        "name_ph": "например: Алекс",
        "birth_title": "Дата рождения",
        "year": "Год",
        "month": "Месяц",
        "day": "День",
        "mbti_mode": "Как вводить MBTI",
        "mbti_direct": "Выбрать вручную",
        "mbti_12": "Быстрый тест (12)",
        "mbti_16": "Подробный тест (16)",
        "go_result": "Показать прогноз!",
        "reset": "Начать заново",
        "share_btn": "Поделиться результатом",
        "share_help": "На телефоне может открыться панель «Поделиться». На ПК может копировать текст.",
        "share_fallback": "Если панель не открылась — скопируйте текст ниже.",
        "copied": "Скопировано!",
        "zodiac_title": "Зодиак",
        "mbti_title": "MBTI",
        "saju_title": "Короткий совет",
        "today_title": "Сегодня",
        "tomorrow_title": "Завтра",
        "yearly_title": "2026 в целом",
        "love_title": "Любовь",
        "money_title": "Деньги",
        "work_title": "Работа/Учёба",
        "health_title": "Здоровье",
        "lucky_title": "Удачные точки",
        "lucky_color": "Цвет",
        "lucky_item": "Талисман",
        "tip_title": "Совет",
        "caution_title": "Осторожно",
        "combo_title": "Как MBTI влияет на удачу",
        "tarot_btn": "Карта таро на сегодня",
        "tarot_title": "Таро сегодня",
        "invalid_year": "Введите год рождения 1900–2030!",
        "mbti_submit": "Отправить и посмотреть",
        "mbti_12_title": "MBTI – 12",
        "mbti_12_desc": "12 вопросов — быстрая оценка MBTI.",
        "mbti_16_title": "MBTI – 16",
        "mbti_16_desc": "16 вопросов (4 на каждую ось) — точнее.",
        "q_yes": "Да",
        "q_no": "Нет",
    },

    "hi": {
        "app_title": "2026 भाग्यफल",
        "app_sub": "राशि/ज़ोडिएक + MBTI + आज/कल",
        "free": "पूरी तरह मुफ़्त",
        "lang_label": "भाषा",
        "name_label": "नाम (परिणाम में दिखेगा)",
        "name_ph": "उदा: राहुल",
        "birth_title": "जन्म तिथि",
        "year": "वर्ष",
        "month": "महीना",
        "day": "दिन",
        "mbti_mode": "MBTI कैसे डालें",
        "mbti_direct": "सीधे चुनें",
        "mbti_12": "क्विक टेस्ट (12)",
        "mbti_16": "डिटेल टेस्ट (16)",
        "go_result": "भाग्यफल देखें!",
        "reset": "फिर से शुरू करें",
        "share_btn": "दोस्तों को शेयर करें",
        "share_help": "मोबाइल पर शेयर शीट खुल सकती है; PC पर कॉपी हो सकता है।",
        "share_fallback": "अगर शेयर शीट न खुले तो नीचे का टेक्स्ट कॉपी करें।",
        "copied": "कॉपी हो गया!",
        "zodiac_title": "ज़ोडिएक",
        "mbti_title": "MBTI गुण",
        "saju_title": "एक लाइन सलाह",
        "today_title": "आज",
        "tomorrow_title": "कल",
        "yearly_title": "2026 कुल",
        "love_title": "प्रेम",
        "money_title": "धन",
        "work_title": "काम/पढ़ाई",
        "health_title": "स्वास्थ्य",
        "lucky_title": "लकी पॉइंट",
        "lucky_color": "रंग",
        "lucky_item": "आइटम",
        "tip_title": "सलाह",
        "caution_title": "सावधानी",
        "combo_title": "MBTI का असर",
        "tarot_btn": "आज का टैरो",
        "tarot_title": "आज का टैरो",
        "invalid_year": "कृपया 1900–2030 के बीच वर्ष डालें!",
        "mbti_submit": "सबमिट करें",
        "mbti_12_title": "MBTI – 12",
        "mbti_12_desc": "12 सवाल — तेज़ अनुमान।",
        "mbti_16_title": "MBTI – 16",
        "mbti_16_desc": "16 सवाल — ज्यादा सटीक।",
        "q_yes": "हाँ",
        "q_no": "नहीं",
    },
}

# Fortune content pools (다국어별 “알찬” 문장)
FORTUNE_DB = {
    "ko": {
        "overall": [
            "올해는 ‘정리 → 확장’의 흐름이 강합니다. 버릴 것을 버릴수록 기회가 커져요.",
            "작은 성취가 큰 신뢰로 바뀌는 해입니다. ‘꾸준함’이 가장 강한 무기예요.",
            "갑작스러운 제안/연락이 기회가 될 수 있어요. 단, 조건 확인은 꼼꼼히!",
            "새로운 사람/새로운 루틴이 운을 끌어올립니다. ‘환경을 바꾸는’ 선택이 유리해요.",
            "느리게 가도 괜찮아요. 올해는 ‘지속 가능한 페이스’가 승리합니다."
        ],
        "today": [
            "정리하면 운이 열립니다. 책상/메신저/파일 정리부터!",
            "말 한마디가 흐름을 바꿔요. 부드럽게, 그러나 분명하게.",
            "오늘은 ‘선택과 집중’이 핵심. 작은 일을 크게 만들지 마세요.",
            "도움 요청이 곧 기회입니다. 혼자 해결하려 하지 않아도 돼요.",
            "약속/시간 관리는 운의 바로미터. 10분만 더 여유를 가져요."
        ],
        "tomorrow": [
            "사람 운이 강해요. 오랜만에 연락하면 좋은 반응이 옵니다.",
            "아이디어가 돈이 되는 흐름. 메모해두면 다음 주에 빛나요.",
            "컨디션이 승부처. 수면/수분/식사 루틴을 지키면 결과가 좋아요.",
            "‘작은 용기’가 큰 전환을 만듭니다. 미뤄둔 말을 꺼내보세요.",
            "내일은 협업 운이 좋아요. 역할을 명확히 하면 속도가 붙습니다."
        ],
        "love": [
            "대화의 온도가 중요해요. ‘사실 + 감정’을 함께 말하면 오해가 줄어요.",
            "밀당보다 신뢰가 이기는 날. 약속을 지키는 사람이 매력적으로 보입니다.",
            "연애운은 ‘타이밍’입니다. 오늘/내일 한 번만 먼저 다가가보세요.",
            "소개/모임 운이 열려요. 가벼운 만남에서 의미 있는 연결이 생깁니다."
        ],
        "money": [
            "충동구매만 막아도 재물운이 상승합니다. ‘24시간 룰’ 추천!",
            "작은 지출을 줄이면 큰 여유가 생겨요. 구독/커피/배달부터 점검.",
            "안정적인 수입 루트가 유리합니다. ‘꾸준히 들어오는 것’에 집중하세요.",
            "투자는 욕심보다 규칙. 손절/분할/한도를 정하면 운이 보호됩니다."
        ],
        "work": [
            "협업운이 좋아요. ‘요구사항 정리’만 잘해도 인정받습니다.",
            "문서/기록이 곧 실력입니다. 오늘 한 줄만 더 써두면 내일 편해요.",
            "피드백은 성장의 촉매. 감정 대신 ‘데이터/사실’로 답하면 승리!",
            "새로운 툴/자동화가 시간을 벌어줍니다. 한 번만 세팅하면 계속 이득."
        ],
        "health": [
            "카페인/야식만 줄여도 컨디션이 확 올라가요.",
            "목/어깨/손목 스트레칭 3분이 오늘의 운을 지킵니다.",
            "물 2컵 더 마시면 집중력이 달라져요.",
            "가벼운 유산소가 정서운까지 올립니다. 산책 15분 추천!"
        ],
        "tips": [
            "오늘은 ‘한 가지’만 완벽히. 나머지는 80점으로 두세요.",
            "메시지 답장은 ‘짧고 명확하게’. 오해를 줄이면 운이 좋아져요.",
            "핵심은 루틴. 같은 시간에 같은 행동을 하면 기회가 붙습니다."
        ],
        "cautions": [
            "과로/야식/무리한 일정은 운을 깎습니다. ‘줄이기’가 이득이에요.",
            "결론을 너무 빨리 내리면 손해. 한 번만 더 확인하세요.",
            "감정적인 결제/결정은 피하세요. 하루만 미루면 답이 보입니다."
        ],
        "lucky_colors": ["골드", "레드", "블루", "그린", "퍼플", "오프화이트", "블랙"],
        "lucky_items": ["빨간 지갑", "심플한 펜", "메모 앱", "텀블러", "이어폰", "손목시계", "작은 파우치"],
        "saju": [
            "목(木) 기운 상승 → 성장·확장 운이 강해요.",
            "화(火) 기운 활성 → 추진력/열정이 성과로 이어져요.",
            "토(土) 기운 안정 → 기반을 다지면 재물운이 따라옵니다.",
            "금(金) 기운 강화 → 결단/정리 운이 좋아요.",
            "수(水) 기운 흐름 → 지혜·인맥 운이 열립니다.",
            "오행 균형 → 무리하지 않으면 전반적으로 대길!"
        ],
    },
    "en": {
        "overall": [
            "A year of ‘declutter → expand’. The more you simplify, the bigger your opportunities.",
            "Small wins turn into trust. Consistency is your strongest weapon.",
            "Unexpected messages can become chances—just verify conditions carefully.",
            "New people and new routines boost your luck. Changing your environment helps.",
            "Slow is fine. Sustainable pace wins in 2026."
        ],
        "today": [
            "Organize and your luck opens. Start with desk/messages/files.",
            "One sentence can change the flow. Be gentle but clear.",
            "Focus beats multitasking today. Don’t make small issues bigger.",
            "Asking for help is an opportunity. You don’t have to do it alone.",
            "Time management is your luck meter. Add 10 minutes of buffer."
        ],
        "tomorrow": [
            "People luck is strong. Reaching out brings warm responses.",
            "Ideas can become money—write them down.",
            "Condition is key. Sleep/water/food routine improves results.",
            "A small courage creates a big turn. Say what you’ve postponed.",
            "Collaboration luck is good. Clarify roles and move fast."
        ],
        "love": [
            "Conversation temperature matters. Share facts + feelings to reduce misunderstandings.",
            "Trust beats push-pull. Keeping promises makes you attractive.",
            "It’s all about timing. Make the first move once.",
            "Social luck opens. Light meetings can become meaningful connections."
        ],
        "money": [
            "Avoid impulse buys—try a 24-hour rule.",
            "Cut small leaks (subscriptions/coffee/delivery) and you’ll feel richer.",
            "Stable income routes are favored. Focus on recurring value.",
            "Investing needs rules: limits, split entries, and a clear plan."
        ],
        "work": [
            "Collaboration luck is good. Clarify requirements and you’ll be recognized.",
            "Documentation is power. One more note saves you tomorrow.",
            "Respond with data, not emotions. You’ll win conflicts.",
            "Automation/tools buy you time. One setup pays off repeatedly."
        ],
        "health": [
            "Less caffeine/late-night snacks improves your condition instantly.",
            "3 minutes of neck/shoulder stretches protects your day.",
            "Drink two more cups of water for better focus.",
            "A light walk lifts both body and mood."
        ],
        "tips": [
            "Do one thing perfectly; keep the rest at 80%.",
            "Keep replies short and clear to avoid confusion.",
            "Routine attracts luck. Same time, same action."
        ],
        "cautions": [
            "Overwork and late nights drain luck—reduce, don’t push.",
            "Don’t conclude too fast. Re-check once more.",
            "Avoid emotional spending/decisions—sleep on it."
        ],
        "lucky_colors": ["Gold", "Red", "Blue", "Green", "Purple", "Off-white", "Black"],
        "lucky_items": ["Red wallet", "Simple pen", "Notes app", "Tumbler", "Earbuds", "Watch", "Small pouch"],
        "saju": [
            "Wood energy rises → growth and expansion.",
            "Fire energy activates → momentum becomes results.",
            "Earth energy stabilizes → build a base and money follows.",
            "Metal energy strengthens → decisive cleaning-up phase.",
            "Water energy flows → wisdom and networking open.",
            "Balanced elements → good overall, if you don’t overdo it."
        ],
    },
}

# 간단히: zh/ja/ru/hi는 영어 DB를 기본으로 사용(표시 언어는 UI만)
for _lg in ["zh", "ja", "ru", "hi"]:
    if _lg not in FORTUNE_DB:
        FORTUNE_DB[_lg] = FORTUNE_DB["en"]


# MBTI trait labels per language
MBTI_TRAITS = {
    "ko": {
        "INTJ": "전략가 · 큰 그림 설계", "INTP": "아이디어 · 분석 천재", "ENTJ": "리더 · 실행력", "ENTP": "발상 · 토론가",
        "INFJ": "통찰 · 조율가", "INFP": "가치 · 감성가", "ENFJ": "리더 · 공감가", "ENFP": "열정 · 영감가",
        "ISTJ": "원칙 · 신뢰형", "ISFJ": "배려 · 책임형", "ESTJ": "운영자 · 성과형", "ESFJ": "분위기 · 케어형",
        "ISTP": "장인 · 문제해결", "ISFP": "감성 · 힐러", "ESTP": "도전 · 현장형", "ESFP": "에너지 · 사교형"
    },
    "en": {
        "INTJ": "Strategist", "INTP": "Analyst", "ENTJ": "Commander", "ENTP": "Debater",
        "INFJ": "Advocate", "INFP": "Mediator", "ENFJ": "Protagonist", "ENFP": "Campaigner",
        "ISTJ": "Logistician", "ISFJ": "Defender", "ESTJ": "Executive", "ESFJ": "Consul",
        "ISTP": "Virtuoso", "ISFP": "Adventurer", "ESTP": "Entrepreneur", "ESFP": "Entertainer"
    }
}
for _lg in ["zh", "ja", "ru", "hi"]:
    MBTI_TRAITS[_lg] = MBTI_TRAITS["en"]

# Zodiac description per language (짧게, 가독성)
ZODIAC_DESC = {
    "ko": {
        "쥐띠": "안정 속 기회. 빠른 판단이 성과를 만들어요.",
        "소띠": "꾸준함의 결실. 가족/기반운이 좋아요.",
        "호랑이띠": "도전과 성공. 리더십이 빛납니다.",
        "토끼띠": "변화 대비. 신중함이 운을 지켜요.",
        "용띠": "운기 상승. 승진/인정 운이 열립니다.",
        "뱀띠": "직감과 실속. 예상 밖 재물운 가능.",
        "말띠": "추진력 강. 균형/휴식이 핵심.",
        "양띠": "편안함 속 대박. 돈운/가정운 상승.",
        "원숭이띠": "창의력 폭발. 재능이 기회로 연결.",
        "닭띠": "노력 결실. 평판/성과가 좋아요.",
        "개띠": "귀인운. 네트워킹이 상승 포인트.",
        "돼지띠": "여유와 풍요. 즐기며 성과내는 해."
    },
    "en": {
        "Rat": "Opportunities inside stability—quick judgment pays off.",
        "Ox": "Consistency wins—family/base luck is strong.",
        "Tiger": "Challenge and success—leadership shines.",
        "Rabbit": "Stay cautious—careful steps protect your luck.",
        "Dragon": "Rising momentum—promotion/recognition chances.",
        "Snake": "Practical intuition—unexpected money luck possible.",
        "Horse": "Strong drive—balance and rest are key.",
        "Goat": "Comfort brings gains—money/home luck improves.",
        "Monkey": "Creativity opens doors—talent turns into chances.",
        "Rooster": "Efforts rewarded—reputation and results improve.",
        "Dog": "Helpful people—networking boosts your rise.",
        "Pig": "Relaxed abundance—enjoy and still achieve."
    }
}
for _lg in ["zh", "ja", "ru", "hi"]:
    ZODIAC_DESC[_lg] = ZODIAC_DESC["en"]

# Tarot (간단히 공통 영어 키 + 설명 다국어는 영어/한국어만)
TAROT = {
    "The Fool": {"ko": "새 시작, 모험, 순수한 믿음", "en": "New beginnings, adventure, innocence"},
    "The Magician": {"ko": "창조력, 능력 발휘, 집중", "en": "Manifestation, skill, concentration"},
    "The High Priestess": {"ko": "직감, 내면의 목소리", "en": "Intuition, mystery, inner voice"},
    "The Empress": {"ko": "풍요, 사랑, 창작", "en": "Abundance, nurturing, creativity"},
    "The Emperor": {"ko": "안정, 구조, 권위", "en": "Stability, structure, authority"},
    "The Lovers": {"ko": "사랑, 선택, 조화", "en": "Love, harmony, choices"},
    "The Chariot": {"ko": "승리, 의지, 방향", "en": "Victory, determination, direction"},
    "Strength": {"ko": "용기, 인내, 부드러운 통제", "en": "Courage, patience, gentle control"},
    "The Star": {"ko": "희망, 영감, 치유", "en": "Hope, inspiration, healing"},
    "The Sun": {"ko": "행복, 성공, 긍정", "en": "Joy, success, positivity"},
}

# -----------------------------
# MBTI Questions
# - 12문항: 축별 3문항(총 12) / Yes=왼쪽, No=오른쪽
# - 16문항: 축별 4문항(총 16)
# -----------------------------
MBTI_12 = {
    "ko": [
        ("주말에 갑자기 약속이 잡히면 설렌다", "E", "I"),
        ("처음 보는 사람과도 금방 친해진다", "E", "I"),
        ("에너지는 ‘사람’에게서 충전된다", "E", "I"),
        ("사실/디테일을 먼저 본다", "S", "N"),
        ("현재의 실용성이 중요하다", "S", "N"),
        ("경험으로 판단하는 편이다", "S", "N"),
        ("의사결정은 논리가 우선이다", "T", "F"),
        ("문제는 ‘해결’이 먼저다", "T", "F"),
        ("피드백은 직설이 편하다", "T", "F"),
        ("계획대로 진행될 때 편하다", "J", "P"),
        ("마감은 미리 끝내는 편이다", "J", "P"),
        ("정리/체계가 마음을 안정시킨다", "J", "P"),
    ],
    "en": [
        ("Sudden plans on weekend excite me", "E", "I"),
        ("I easily talk to strangers", "E", "I"),
        ("People interactions recharge me", "E", "I"),
        ("I notice facts/details first", "S", "N"),
        ("Practicality matters most", "S", "N"),
        ("I rely on experience", "S", "N"),
        ("Logic comes first in decisions", "T", "F"),
        ("I prioritize solving the problem", "T", "F"),
        ("I prefer direct feedback", "T", "F"),
        ("I feel better with a plan", "J", "P"),
        ("I finish tasks early", "J", "P"),
        ("Order and structure calm me", "J", "P"),
    ],
}
for _lg in ["zh", "ja", "ru", "hi"]:
    MBTI_12[_lg] = MBTI_12["en"]

MBTI_16 = {
    "ko": [
        # E/I
        ("사교모임 후 에너지가 더 생긴다", "E", "I"),
        ("생각은 말하면서 정리된다", "E", "I"),
        ("연락/메시지를 자주 하는 편이다", "E", "I"),
        ("새로운 사람 만나는 게 즐겁다", "E", "I"),
        # S/N
        ("현실적이고 구체적인 설명이 좋다", "S", "N"),
        ("미래 가능성/아이디어를 상상한다", "N", "S"),
        ("디테일보다 흐름/컨셉을 본다", "N", "S"),
        ("당장 쓸 수 있는 정보가 중요하다", "S", "N"),
        # T/F
        ("정답/합리성이 더 중요하다", "T", "F"),
        ("상대 감정 고려가 더 중요하다", "F", "T"),
        ("갈등은 논리로 정리하는 편이다", "T", "F"),
        ("공감이 해결의 시작이라고 느낀다", "F", "T"),
        # J/P
        ("계획이 있어야 마음이 놓인다", "J", "P"),
        ("즉흥이 재밌고 더 잘 맞는다", "P", "J"),
        ("정리정돈을 자주 한다", "J", "P"),
        ("옵션을 열어두는 게 편하다", "P", "J"),
    ],
    "en": [
        ("After social events, I feel more energized", "E", "I"),
        ("I organize thoughts by speaking", "E", "I"),
        ("I message/contact people often", "E", "I"),
        ("Meeting new people is fun", "E", "I"),
        ("I prefer concrete explanations", "S", "N"),
        ("I imagine future possibilities/ideas", "N", "S"),
        ("I focus on concept over details", "N", "S"),
        ("Practical info matters most", "S", "N"),
        ("Correctness and logic matter more", "T", "F"),
        ("Considering feelings matters more", "F", "T"),
        ("I resolve conflicts logically", "T", "F"),
        ("Empathy is the start of solutions", "F", "T"),
        ("I feel better with a plan", "J", "P"),
        ("I enjoy spontaneity", "P", "J"),
        ("I tidy up often", "J", "P"),
        ("I’m comfortable keeping options open", "P", "J"),
    ],
}
for _lg in ["zh", "ja", "ru", "hi"]:
    MBTI_16[_lg] = MBTI_16["en"]


def estimate_mbti_from_answers(items: List[Tuple[str, str, str]], answers_yes: List[bool]) -> str:
    # yes => left letter, no => right letter
    score = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}
    for (q, left, right), yes in zip(items, answers_yes):
        pick = left if yes else right
        score[pick] += 1

    def pick_pair(a: str, b: str) -> str:
        return a if score[a] >= score[b] else b

    return pick_pair("E", "I") + pick_pair("S", "N") + pick_pair("T", "F") + pick_pair("J", "P")


def mbti_influence_advice(lang: str, mbti: str) -> str:
    # MBTI가 운세(사람/일/돈/연애/건강)에 미치는 "조언"을 생성
    # 간단 규칙 기반 + 랜덤 문장 조합
    db = {
        "ko": {
            "E": ["사람을 만나야 운이 열려요. ‘약속 1개’가 큰 기회가 됩니다.", "네트워킹이 곧 재물운입니다. 먼저 인사하면 흐름이 바뀌어요."],
            "I": ["혼자 정리하는 시간이 곧 행운입니다. ‘정리 후 연락’이 타이밍이에요.", "혼자만의 루틴이 운을 키워요. 컨디션이 올라가면 결과가 따라옵니다."],
            "S": ["현실 점검이 최고의 부적! 작은 비용/시간부터 최적화하세요.", "디테일이 돈이 됩니다. 계약/약속 조건을 꼼꼼히 보면 이득이에요."],
            "N": ["아이디어가 기회입니다. 떠오르는 건 메모해두면 돈이 돼요.", "큰 그림을 그리되, 오늘은 1단계만 실행해보세요."],
            "T": ["감정보다 기준을 세우면 운이 보호됩니다. ‘룰/한도’가 핵심!", "결정은 빠르되 말은 부드럽게. 그게 대인운을 살립니다."],
            "F": ["관계운이 강해요. 진심을 표현하면 연애/인맥운이 같이 올라갑니다.", "배려가 기회로 돌아옵니다. 다만 ‘선 긋기’도 함께 하세요."],
            "J": ["계획이 곧 행운입니다. 일정만 정리해도 성과가 빨라져요.", "미리 준비하면 돈이 새지 않아요. 구독/지출 정리가 추천!"],
            "P": ["유연함이 운을 부릅니다. 단, ‘마감 1개’만은 미리 잡아두세요.", "즉흥의 장점은 살리되, 중요한 건 체크리스트로 보호하세요."],
        },
        "en": {
            "E": ["Luck opens through people. One plan can become a big chance.", "Networking is money luck—say hi first."],
            "I": ["Quiet organization is your lucky key. Reset, then reach out.", "Routine builds your luck. Better condition → better results."],
            "S": ["Reality-check is your talisman. Optimize time and budget.", "Details become profit—verify terms and you gain."],
            "N": ["Ideas become opportunities. Write them down.", "Keep the vision, but execute one small step today."],
            "T": ["Rules protect luck. Set limits and standards.", "Decide fast, speak gently—relationships improve."],
            "F": ["Relationship luck is strong. Express sincerity.", "Kindness returns as chances—keep boundaries too."],
            "J": ["Planning is luck. Organize schedule for faster results.", "Preparation prevents money leaks—review expenses."],
            "P": ["Flexibility attracts luck—still, lock one key deadline.", "Use checklists to protect important tasks."],
        }
    }
    if lang not in db:
        lang = "en"
    rnd = random.Random(daily_seed(0) + sum(map(ord, mbti)))
    parts = []
    for ch in mbti:
        if ch in db[lang]:
            parts.append(rnd.choice(db[lang][ch]))
    # 중복 제거
    seen = set()
    out = []
    for p in parts:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return " / ".join(out[:3]) if out else ""


# -----------------------------
# Streamlit Page
# -----------------------------
st.set_page_config(page_title="2026 Fortune", layout="centered")

# Session defaults
if "lang" not in st.session_state:
    st.session_state.lang = "ko"
if "step" not in st.session_state:
    st.session_state.step = "input"  # input | result
if "name" not in st.session_state:
    st.session_state.name = ""
if "year" not in st.session_state:
    st.session_state.year = 2005
if "month" not in st.session_state:
    st.session_state.month = 1
if "day" not in st.session_state:
    st.session_state.day = 1
if "mbti" not in st.session_state:
    st.session_state.mbti = None
if "mbti_mode" not in st.session_state:
    st.session_state.mbti_mode = "direct"
if "shared_pressed" not in st.session_state:
    st.session_state.shared_pressed = False

# Mini game state
if "mini_started_at" not in st.session_state:
    st.session_state.mini_started_at = None
if "mini_attempt_used" not in st.session_state:
    st.session_state.mini_attempt_used = 0
if "mini_bonus_used" not in st.session_state:
    st.session_state.mini_bonus_used = False
if "mini_winner" not in st.session_state:
    st.session_state.mini_winner = False
if "mini_time" not in st.session_state:
    st.session_state.mini_time = None
if "mini_submitted" not in st.session_state:
    st.session_state.mini_submitted = False
if "mini_count_cached" not in st.session_state:
    st.session_state.mini_count_cached = None  # (optional) if you later load from DB

# -----------------------------
# Styling (가독성 강화)
# -----------------------------
st.markdown(
    """
<style>
html, body, [class*="css"] { font-family: -apple-system, BlinkMacSystemFont, "Noto Sans KR", "Segoe UI", Roboto, "Helvetica Neue", Arial, "Apple Color Emoji","Segoe UI Emoji"; }
.block-container { padding-top: 18px !important; padding-bottom: 40px !important; max-width: 780px; }
h1,h2,h3 { letter-spacing: -0.3px; }
hr { margin: 16px 0; }
.card {
  background: rgba(255,255,255,0.96);
  border-radius: 18px;
  padding: 18px 18px;
  margin: 12px 0;
  box-shadow: 0 10px 28px rgba(0,0,0,0.10);
  border: 1px solid rgba(120,120,120,0.08);
}
.card-title { font-weight: 800; font-size: 1.05rem; margin-bottom: 6px; }
.muted { color: rgba(20,20,20,0.65); font-size: 0.92rem; }
.big-pill {
  width: 100%;
  border-radius: 999px;
  padding: 14px 18px;
  font-weight: 800;
  font-size: 1.05rem;
}
.hero {
  border-radius: 22px;
  padding: 18px 18px;
  background: linear-gradient(135deg, rgba(161,140,209,0.95), rgba(251,194,235,0.95), rgba(142,197,252,0.95));
  box-shadow: 0 14px 34px rgba(0,0,0,0.12);
  color: white;
  text-align: center;
}
.hero h1 { margin: 0; font-size: 1.65rem; font-weight: 900; text-shadow: 0 2px 8px rgba(0,0,0,0.18); }
.hero .sub { margin-top: 6px; font-weight: 700; opacity: 0.92; }
.badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 800;
  background: rgba(255,255,255,0.2);
  border: 1px solid rgba(255,255,255,0.35);
  margin-top: 10px;
}
.adbox {
  border-radius: 18px;
  padding: 16px 16px;
  border: 1.5px solid rgba(231,76,60,0.55);
  background: rgba(255,255,255,0.95);
  box-shadow: 0 10px 24px rgba(0,0,0,0.08);
}
.adbtn {
  display:inline-block;
  margin-top: 10px;
  padding: 10px 14px;
  border-radius: 12px;
  border: 1px solid rgba(230,126,34,0.35);
  background: rgba(230,126,34,0.10);
  font-weight: 900;
  text-decoration: none;
}
.small-note { font-size: 0.85rem; color: rgba(20,20,20,0.55); }
.result-grid { display: grid; grid-template-columns: 1fr; gap: 10px; }
@media (min-width: 720px) { .result-grid { grid-template-columns: 1fr 1fr; } }
.kv { line-height: 1.85; font-size: 1.03rem; }
.kv b { font-weight: 900; }
</style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Language selector
# -----------------------------
lang_codes = [c for c, _ in LANGS]
lang_labels = [n for _, n in LANGS]
current_idx = lang_codes.index(st.session_state.lang) if st.session_state.lang in lang_codes else 0

sel = st.radio(
    T[st.session_state.lang]["lang_label"],
    options=lang_codes,
    format_func=lambda x: dict(LANGS).get(x, x),
    index=current_idx,
    horizontal=True,
)
st.session_state.lang = sel
t = T[st.session_state.lang]

APP_URL = "https://my-fortune.streamlit.app"  # 필요 시 변경

# -----------------------------
# Input Screen
# -----------------------------
if st.session_state.step == "input":
    st.markdown(
        f"""
        <div class="hero">
          <h1>{t["app_title"]}</h1>
          <div class="sub">{t["app_sub"]}</div>
          <div class="badge">{t["free"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-title">{t["name_label"]}</div>', unsafe_allow_html=True)
    st.session_state.name = st.text_input("", value=st.session_state.name, placeholder=t["name_ph"])
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-title">{t["birth_title"]}</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    st.session_state.year = c1.number_input(t["year"], min_value=1900, max_value=2030, value=int(st.session_state.year), step=1)
    st.session_state.month = c2.number_input(t["month"], min_value=1, max_value=12, value=int(st.session_state.month), step=1)
    st.session_state.day = c3.number_input(t["day"], min_value=1, max_value=31, value=int(st.session_state.day), step=1)
    st.session_state.day = clamp_day(st.session_state.year, st.session_state.month, st.session_state.day)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-title">{t["mbti_mode"]}</div>', unsafe_allow_html=True)
    mode = st.radio(
        "",
        options=["direct", "mbti12", "mbti16"],
        format_func=lambda x: {
            "direct": t["mbti_direct"],
            "mbti12": t["mbti_12"],
            "mbti16": t["mbti_16"],
        }[x],
        horizontal=False,
        index=["direct", "mbti12", "mbti16"].index(st.session_state.mbti_mode) if st.session_state.mbti_mode in ["direct", "mbti12", "mbti16"] else 0,
    )
    st.session_state.mbti_mode = mode
    st.markdown("</div>", unsafe_allow_html=True)

    # MBTI input blocks
    if mode == "direct":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">MBTI</div>', unsafe_allow_html=True)
        mbti = st.selectbox("",
                            options=sorted(MBTI_TRAITS[st.session_state.lang].keys()),
                            index=0)
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button(t["go_result"], use_container_width=True):
            st.session_state.mbti = mbti
            st.session_state.step = "result"
            st.rerun()

    elif mode == "mbti12":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div class="card-title">{t["mbti_12_title"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="muted">{t["mbti_12_desc"]}</div>', unsafe_allow_html=True)

        items = MBTI_12.get(st.session_state.lang, MBTI_12["en"])
        with st.form("mbti12_form", clear_on_submit=False):
            answers = []
            for i, (q, left, right) in enumerate(items):
                ans = st.radio(
                    f"{i+1}. {q}",
                    options=[t["q_yes"], t["q_no"]],
                    horizontal=True,
                    key=f"mbti12_{i}",
                )
                answers.append(ans == t["q_yes"])
            submitted = st.form_submit_button(t["mbti_submit"], use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if submitted:
            st.session_state.mbti = estimate_mbti_from_answers(items, answers)
            st.session_state.step = "result"
            st.rerun()

    else:  # mbti16
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div class="card-title">{t["mbti_16_title"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="muted">{t["mbti_16_desc"]}</div>', unsafe_allow_html=True)

        items = MBTI_16.get(st.session_state.lang, MBTI_16["en"])
        with st.form("mbti16_form", clear_on_submit=False):
            answers = []
            for i, (q, left, right) in enumerate(items):
                ans = st.radio(
                    f"{i+1}. {q}",
                    options=[t["q_yes"], t["q_no"]],
                    horizontal=True,
                    key=f"mbti16_{i}",
                )
                answers.append(ans == t["q_yes"])
            submitted = st.form_submit_button(t["mbti_submit"], use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if submitted:
            st.session_state.mbti = estimate_mbti_from_answers(items, answers)
            st.session_state.step = "result"
            st.rerun()


# -----------------------------
# Result Screen
# -----------------------------
if st.session_state.step == "result":
    # validate
    zodiac = get_zodiac_by_year(int(st.session_state.year), st.session_state.lang)
    if zodiac is None or st.session_state.mbti is None:
        st.error(t["invalid_year"])
        if st.button(t["reset"], use_container_width=True):
            st.session_state.clear()
            st.rerun()
        st.stop()

    mbti = st.session_state.mbti
    name_display = st.session_state.name.strip()

    # Content picks (seeded for consistency per day+profile)
    base_seed = daily_seed(0) + sum(map(ord, zodiac)) + sum(map(ord, mbti)) + int(st.session_state.year)
    db = FORTUNE_DB[st.session_state.lang]

    saju = seeded_choice(db["saju"], base_seed + 11)
    today_msg = seeded_choice(db["today"], base_seed + 21)
    tomorrow_msg = seeded_choice(db["tomorrow"], base_seed + 31)
    overall = seeded_choice(db["overall"], base_seed + 41)
    love = seeded_choice(db["love"], base_seed + 51)
    money = seeded_choice(db["money"], base_seed + 61)
    work = seeded_choice(db["work"], base_seed + 71)
    health = seeded_choice(db["health"], base_seed + 81)
    tip = seeded_choice(db["tips"], base_seed + 91)
    caution = seeded_choice(db["cautions"], base_seed + 101)
    lucky_color = seeded_choice(db["lucky_colors"], base_seed + 111)
    lucky_item = seeded_choice(db["lucky_items"], base_seed + 121)

    zodiac_desc = ZODIAC_DESC[st.session_state.lang].get(zodiac, "")
    mbti_desc = MBTI_TRAITS[st.session_state.lang].get(mbti, mbti)
    combo = mbti_influence_advice(st.session_state.lang, mbti)

    # Header
    title_name = f"{name_display} " if name_display else ""
    st.markdown(
        f"""
        <div class="hero">
          <h1>{title_name}{t["app_title"]}</h1>
          <div class="sub">{zodiac} · {mbti}</div>
          <div class="badge">{t["free"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Ad placeholder (future adsense) + KO-only Dananum ad
    st.markdown(
        """
        <div class="card" style="border:1.5px dashed rgba(140,140,140,0.35); text-align:center;">
          <div class="muted" style="font-weight:800;">AD</div>
          <div class="small-note">(승인 후 이 위치에 광고가 표시됩니다)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.lang == "ko":
        st.markdown(
            f"""
            <div class="adbox">
              <div style="display:flex; justify-content:center; gap:8px; align-items:center;">
                <span style="font-weight:900; color:#e74c3c;">{t["ad_badge"]}</span>
                <span style="font-weight:900;">{t["ad_title"]}</span>
              </div>
              <div class="kv" style="margin-top:10px; text-align:center;">
                <div>{t["ad_line1"]}</div>
                <div>{t["ad_line2"]}</div>
              </div>
              <div style="text-align:center;">
                <a class="adbtn" href="{t["ad_url"]}" target="_blank">{t["ad_link"]}</a>
              </div>
              <div class="small-note" style="text-align:center; margin-top:8px;">{t["ad_note"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Main result card (가독성: 줄바꿈/섹션)
    st.markdown(
        f"""
        <div class="card">
          <div class="kv">
            <div><b>{t["zodiac_title"]}</b>: {zodiac_desc}</div>
            <div><b>{t["mbti_title"]}</b>: {mbti_desc}</div>
            <div><b>{t["saju_title"]}</b>: {saju}</div>
            <hr/>
            <div><b>{t["today_title"]}</b>: {today_msg}</div>
            <div><b>{t["tomorrow_title"]}</b>: {tomorrow_msg}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Grid cards
    st.markdown('<div class="result-grid">', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="card">
          <div class="card-title">{t["yearly_title"]}</div>
          <div class="kv">{overall}</div>
          <hr/>
          <div class="card-title">{t["combo_title"]}</div>
          <div class="kv">{combo}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="card">
          <div class="card-title">{t["love_title"]}</div>
          <div class="kv">{love}</div>
          <hr/>
          <div class="card-title">{t["money_title"]}</div>
          <div class="kv">{money}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="card">
          <div class="card-title">{t["work_title"]}</div>
          <div class="kv">{work}</div>
          <hr/>
          <div class="card-title">{t["health_title"]}</div>
          <div class="kv">{health}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="card">
          <div class="card-title">{t["lucky_title"]}</div>
          <div class="kv">
            <div><b>{t["lucky_color"]}</b>: {lucky_color}</div>
            <div><b>{t["lucky_item"]}</b>: {lucky_item}</div>
          </div>
          <hr/>
          <div class="card-title">{t["tip_title"]}</div>
          <div class="kv">{tip}</div>
          <hr/>
          <div class="card-title">{t["caution_title"]}</div>
          <div class="kv">{caution}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Tarot expander
    with st.expander(t["tarot_btn"], expanded=False):
        tarot_card = seeded_choice(list(TAROT.keys()), base_seed + 2026)
        tarot_meaning = TAROT[tarot_card]["ko"] if st.session_state.lang == "ko" else TAROT[tarot_card]["en"]
        st.markdown(
            f"""
            <div class="card" style="text-align:center;">
              <div class="card-title">{t["tarot_title"]}</div>
              <div style="font-size:1.5rem; font-weight:900; margin-top:6px;">{tarot_card}</div>
              <div class="kv" style="margin-top:8px;">{tarot_meaning}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Share text (TEXT ONLY)
    share_text = (
        f"{title_name}{t['app_title']}\n"
        f"{zodiac} · {mbti}\n\n"
        f"{t['today_title']}: {today_msg}\n"
        f"{t['tomorrow_title']}: {tomorrow_msg}\n\n"
        f"{t['yearly_title']}: {overall}\n"
        f"{t['combo_title']}: {combo}\n\n"
        f"{t['lucky_color']}: {lucky_color} / {t['lucky_item']}: {lucky_item}\n"
        f"{t['tip_title']}: {tip}\n"
        f"{t['caution_title']}: {caution}\n\n"
        f"{APP_URL}"
    )

    # Share button: Web Share API (mobile) -> fallback copy
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="text-align:center;">
          <button class="big-pill" onclick="shareResult()" style="background:#6c3bd2; color:white; border:none; box-shadow: 0 10px 24px rgba(108,59,210,0.25);">
            {t["share_btn"]}
          </button>
          <div class="small-note" style="margin-top:8px;">{t["share_help"]}</div>
        </div>
        <script>
          async function shareResult() {{
            const text = `{sanitize_for_js(share_text)}`;
            try {{
              if (navigator.share) {{
                await navigator.share({{ text: text }});
              }} else {{
                await navigator.clipboard.writeText(text);
                alert("{sanitize_for_js(t['copied'])}");
              }}
            }} catch (e) {{
              try {{
                await navigator.clipboard.writeText(text);
                alert("{sanitize_for_js(t['copied'])}");
              }} catch (e2) {{
                alert("{sanitize_for_js(t['share_fallback'])}");
              }}
            }}
          }}
        </script>
        """,
        unsafe_allow_html=True,
    )

    # 공유 버튼 누르면(사용자 클릭) 보너스 기회 열어주기(정확한 공유 완료 여부까지는 웹에서 확인 불가)
    if st.session_state.lang == "ko" and (not st.session_state.shared_pressed):
        # UI 상의 안내만: 실제로는 JS 버튼 클릭 이벤트를 파이썬이 알 수 없어서
        # "공유 버튼 눌렀으면 체크" 방식을 제공
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>🎯 공유 보너스</div>", unsafe_allow_html=True)
        st.markdown("<div class='kv'>공유 버튼을 눌렀다면 아래 체크를 눌러 1회 추가 기회를 열 수 있어요.</div>", unsafe_allow_html=True)
        if st.checkbox("공유 버튼을 눌렀습니다 (보너스 기회 열기)"):
            st.session_state.shared_pressed = True
            st.success("✅ 공유 보너스 1회가 열렸어요!")
        st.markdown("</div>", unsafe_allow_html=True)

    # KO-only Mini game (lead capture)
    if st.session_state.lang == "ko":
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='card-title'>{t['mini_title']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='kv'>{t['mini_desc']}</div>", unsafe_allow_html=True)

        # attempts
        base_attempts = 1
        bonus_attempts = 1 if st.session_state.shared_pressed else 0
        max_attempts = base_attempts + bonus_attempts
        remaining = max(0, max_attempts - st.session_state.mini_attempt_used)

        st.markdown(f"<div class='muted'>{t['mini_left']}: <b>{remaining}</b> / {max_attempts}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='small-note'>{t['mini_bonus']}</div>", unsafe_allow_html=True)

        # start/stop
        c1, c2 = st.columns(2)
        with c1:
            if st.button(t["mini_start"], use_container_width=True, disabled=(remaining <= 0 or st.session_state.mini_started_at is not None or st.session_state.mini_winner)):
                st.session_state.mini_started_at = time.time()
                st.session_state.mini_time = None
                st.rerun()

        with c2:
            if st.button(t["mini_stop"], use_container_width=True, disabled=(st.session_state.mini_started_at is None or st.session_state.mini_winner or remaining <= 0)):
                elapsed = time.time() - st.session_state.mini_started_at
                st.session_state.mini_started_at = None
                st.session_state.mini_time = elapsed
                st.session_state.mini_attempt_used += 1

                # 성공 판정 (오차 허용)
                target = 20.26
                tolerance = 0.20  # ±0.20초
                if abs(elapsed - target) <= tolerance:
                    st.session_state.mini_winner = True
                st.rerun()

        # show running
        if st.session_state.mini_started_at is not None:
            st.info("⏱️ 타이머 진행 중… (멈춤을 눌러 기록하세요)")
        if st.session_state.mini_time is not None:
            st.markdown(
                f"<div class='kv'><b>{t['mini_result']}</b>: {st.session_state.mini_time:.2f}초</div>",
                unsafe_allow_html=True,
            )

        # winner submit
        if st.session_state.mini_winner and (not st.session_state.mini_submitted):
            st.success("🎉 성공! 선착순 20명이라면 쿠폰 대상이에요. 아래를 작성해주세요.")
            consent = st.checkbox(f"{t['mini_privacy']}: {t['mini_privacy_text']}")
            name_in = st.text_input(t["mini_name"], value=st.session_state.name.strip())
            phone_in = st.text_input(t["mini_phone"], value="", placeholder="01012345678")

            if st.button(t["mini_submit"], use_container_width=True, disabled=not consent):
                phone_digits = re.sub(r"\D+", "", phone_in)
                if not re.fullmatch(r"\d{10,11}", phone_digits or ""):
                    st.error(t["mini_invalid_phone"])
                else:
                    # 선착순 제한은 실제 DB에서 카운트해야 정확합니다.
                    # 여기서는 "구글시트 저장 성공 시" 선착순 처리로 간주(운영 단계에서 시트에서 20명 컷오프).
                    ok = try_save_to_google_sheets([
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        name_in.strip(),
                        phone_digits,
                        f"{st.session_state.year:04d}-{st.session_state.month:02d}-{st.session_state.day:02d}",
                        st.session_state.mbti,
                        zodiac,
                        f"{st.session_state.mini_time:.2f}" if st.session_state.mini_time else "",
                        APP_URL
                    ])
                    st.session_state.mini_submitted = True
                    if ok:
                        st.success(t["mini_done"])
                    else:
                        st.warning("저장은 아직 연결되지 않았어요. (구글 시트 연동 설정이 필요합니다) 그래도 화면상 접수 처리로 표시됩니다.")
                        st.success(t["mini_done"])

        elif (st.session_state.mini_time is not None) and (not st.session_state.mini_winner):
            if remaining <= 0:
                st.error(t["mini_fail"])
            else:
                st.warning("아쉽지만 목표(20.26초)에 살짝 벗어났어요. 남은 기회로 다시 도전해보세요!")

        st.markdown("</div>", unsafe_allow_html=True)

    # reset
    if st.button(t["reset"], use_container_width=True):
        st.session_state.clear()
        st.rerun()
