import streamlit as st
from datetime import datetime, timedelta
import random
import time
import hashlib
import json

import streamlit.components.v1 as components

# =========================
# 0) 설정값 (필수만 바꿔서 쓰면 됨)
# =========================
APP_URL = "https://my-fortune.streamlit.app"  # 배포 URL

# ✅ 사용자 요청: 구글시트 ID 고정 적용
SHEET_ID = "1WvuKXx2if2WvxmQaxkqzFW-BzDEWWma9hZgCr2jJQYY"
WORKSHEET_NAME = "Sheet1"  # 시트 탭 이름

# 이벤트(한국어에서만)
EVENT_ENABLED = True
EVENT_LANGUAGE_ONLY = "ko"
WINNER_LIMIT = 20
TARGET_SECONDS = 20.26
PASS_TOLERANCE = 0.15

BASE_ATTEMPTS = 1
EXTRA_ATTEMPTS_ON_SHARE = 1

DATA_RETENTION_DAYS = 90  # 개인정보 보관 기간(문구에 사용)

# 구글시트 사용
USE_GOOGLE_SHEETS = True
try:
    import gspread
    from google.oauth2.service_account import Credentials
except Exception:
    USE_GOOGLE_SHEETS = False


# =========================
# 1) 텍스트/번역(핵심 UI 위주)
# =========================
LANGS = ["ko", "en", "ja", "zh", "ru"]

translations = {
    "ko": {
        "lang_label": "언어 / Language",
        "title": "2026 띠 + MBTI + 사주 + 오늘/내일 운세",
        "caption": "완전 무료",
        "birth": "생년월일 입력",
        "name_placeholder": "이름 입력 (선택)",
        "mbti_mode": "MBTI 어떻게 할까?",
        "direct": "직접 입력",
        "test12": "간단 테스트 (12문항)",
        "test16": "상세 테스트 (16문항)",
        "test_start_12": "간단 테스트(12문항) 시작! 빠르게 답해주세요",
        "test_start_16": "상세 테스트(16문항) 시작! 하나씩 답해주세요",
        "energy": "에너지 방향 (E/I)",
        "info": "정보 수집 (S/N)",
        "decision": "결정 방식 (T/F)",
        "life": "생활 방식 (J/P)",
        "result_btn": "결과 보기!",
        "fortune_btn": "운세 보기!",
        "reset": "처음부터 다시 하기",
        "share_btn": "친구에게 결과 공유하기",
        "tarot_btn": "오늘의 타로 카드 뽑기",
        "tarot_title": "오늘의 타로 카드",
        "zodiac_title": "띠 운세",
        "mbti_title": "MBTI 특징",
        "saju_title": "사주 한 마디",
        "today_title": "오늘 운세",
        "tomorrow_title": "내일 운세",
        "overall_title": "2026 전체 운세",
        "combo_title": "조합 조언",
        "lucky_color_title": "럭키 컬러",
        "lucky_item_title": "럭키 아이템",
        "tip_title": "팁",
        "copied": "결과가 복사됐어요! 카톡/메시지에 붙여넣기 해주세요.",
        "share_hint": "모바일은 공유창이 열려요. PC는 자동 복사돼요.",

        # 한국어 광고
        "ad_title": "정수기렌탈 궁금할 때?",
        "ad_body": "<b>다나눔렌탈</b> 제휴카드 시 <b>월 0원부터</b> + <b>설치당일 최대 현금 50만원 페이백</b>!",
        "ad_btn": "보러가기",

        # 이벤트(미니게임)
        "event_title": "🎁 미니게임: 선착순 20명 커피쿠폰 도전!",
        "event_desc": "스톱워치를 <b>20.26초</b>에 맞추면 응모 가능! (기본 1회, 친구공유 누르면 1회 추가)",
        "event_closed": "😢 선착순 20명이 마감되었습니다. 다음 이벤트를 기대해주세요!",
        "event_attempts_left": "남은 기회",
        "event_start": "시작",
        "event_stop": "멈춤",
        "event_success": "✅ 성공! (기준 시간에 매우 근접했어요)",
        "event_fail": "❌ 아쉽게 실패! 다시 도전해보세요.",
        "event_elapsed": "기록",
        "event_need_share": "추가기회가 필요하면 위의 ‘친구에게 결과 공유하기’를 눌러주세요.",
        "event_form_title": "☕ 커피쿠폰 응모 정보 입력",

        "consent_title": "개인정보 수집·이용 동의",
        "consent_check": "위 내용을 읽었으며, 개인정보 수집·이용에 동의합니다. (필수)",
        "consent_more": "동의하지 않으면 쿠폰 응모는 할 수 없지만, 운세 서비스 이용은 가능합니다.",
        "submit_entry": "응모하기",
        "entry_ok": "🎉 응모가 완료되었습니다! (선착순 여부는 시트 기록 순서로 확정됩니다.)",
        "entry_dup": "이미 응모하신 전화번호입니다. (중복 응모 불가)",
        "entry_error": "저장 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
        "phone_label": "전화번호(쿠폰 발송용)",
        "name_label": "이름(응모자)",
        "phone_hint": "예: 01012345678 (하이픈 없이)",

        # 12문항(축별 3문항)
        "q12_ei": [
            "주말에 친구가 갑자기 나오자고 하면?",
            "모임에서 처음 본 사람들과 대화하는 건?",
            "하루 종일 사람을 만난 뒤 나는?"
        ],
        "q12_sn": [
            "새로운 카페에 가면 먼저 보는 건?",
            "영화/책을 볼 때 더 끌리는 건?",
            "쇼핑할 때 나는?"
        ],
        "q12_tf": [
            "친구가 늦어서 화날 때 나는?",
            "의견 충돌이 생기면 나는?",
            "누가 울면서 고민을 말하면 나는?"
        ],
        "q12_jp": [
            "여행 계획을 세울 때 나는?",
            "마감이 다가오면 나는?",
            "방 정리는 나는?"
        ],
        "a12_e": ["바로 나감(E)", "대화가 즐겁다(E)", "그래도 에너지 남아있다(E)"],
        "a12_i": ["집에 있고 싶다(I)", "조금 부담스럽다(I)", "혼자 쉬어야 한다(I)"],
        "a12_s": ["메뉴/가격/실용(S)", "디테일/현실감(S)", "필요한 것만 산다(S)"],
        "a12_n": ["분위기/컨셉/감성(N)", "상징/해석/의미(N)", "미래 활용을 상상한다(N)"],
        "a12_t": ["원칙대로 말한다(T)", "논리로 정리한다(T)", "해결책을 제시한다(T)"],
        "a12_f": ["기분 상할까 배려한다(F)", "감정도 고려해 조율한다(F)", "공감부터 한다(F)"],
        "a12_j": ["일정 촘촘히(J)", "미리미리(J)", "정리정돈 확실(J)"],
        "a12_p": ["즉흥/유동(P)", "몰아서 한다(P)", "대충해도 OK(P)"],

        # 16문항(축별 4문항)
        "q_energy": ["주말에 친구들이 갑자기 '놀자!' 하면?", "모임에서 처음 본 사람들과 대화하는 거?", "하루 종일 사람 만난 후에?", "생각이 떠오르면?"],
        "q_info": ["새로운 카페 가면 뭐가 먼저 눈에 들어?", "친구가 고민 상담하면?", "책이나 영화 볼 때?", "쇼핑할 때?"],
        "q_decision": ["친구가 늦어서 화날 때?", "팀 프로젝트에서 의견 충돌 시?", "누가 울면서 상담하면?", "거짓말 탐지 시?"],
        "q_life": ["여행 갈 때?", "숙제나 과제 마감 앞두고?", "방 정리할 때?", "선택해야 할 때?"],
        "options_e": ["와 좋아! 바로 나감 (E)", "재밌고 신나! (E)", "아직 에너지 넘쳐! (E)", "바로 말로 풀어냄 (E)"],
        "options_i": ["집에서 쉬고 싶어... (I)", "조금 피곤하고 부담스러워 (I)", "완전 지쳐서 혼자 있고 싶어 (I)", "머릿속에서 먼저 정리함 (I)"],
        "options_s": ["메뉴판 가격과 메뉴 (S)", "지금 상황과 사실 위주로 들어줌 (S)", "스토리와 디테일에 집중 (S)", "필요한 거 보고 바로 사 (S)"],
        "options_n": ["분위기, 인테리어, 컨셉 (N)", "가능성과 미래 방향으로 생각함 (N)", "상징과 숨은 의미 찾는 재미 (N)", "이거 사면 나중에 뭐랑 입히지? 상상함 (N)"],
        "options_t": ["늦었으면 늦었다고 솔직히 말함 (T)", "논리적으로 누가 맞는지 따짐 (T)", "문제 해결 방법 조언해줌 (T)", "바로 지적함 (T)"],
        "options_f": ["기분 상할까 봐 부드럽게 말함 (F)", "다른 사람 기분 상하지 않게 조율 (F)", "일단 공감하고 들어줌 (F)", "상처 줄까 봐 넘김 (F)"],
        "options_j": ["일정 꽉꽉 짜서 효율적으로 (J)", "미리미리 끝냄 (J)", "정해진 기준으로 깔끔히 (J)", "빨리 결정하고 넘김 (J)"],
        "options_p": ["그때그때 기분 따라 즉흥적으로 (P)", "마감 직전에 몰아서 함 (P)", "대충 써도 괜찮아 (P)", "옵션 더 알아보고 싶어 (P)"],
    },

    "en": {
        "lang_label": "Language",
        "title": "2026 Zodiac + MBTI + Fortune",
        "caption": "Completely Free",
        "birth": "Birth date",
        "name_placeholder": "Name (optional)",
        "mbti_mode": "How to do MBTI?",
        "direct": "Direct input",
        "test12": "Quick test (12)",
        "test16": "Detailed test (16)",
        "test_start_12": "Quick test starts!",
        "test_start_16": "Detailed test starts!",
        "energy": "Energy (E/I)",
        "info": "Information (S/N)",
        "decision": "Decision (T/F)",
        "life": "Lifestyle (J/P)",
        "result_btn": "See Result!",
        "fortune_btn": "See Fortune!",
        "reset": "Start Over",
        "share_btn": "Share result",
        "tarot_btn": "Draw today's tarot",
        "tarot_title": "Today's Tarot",
        "zodiac_title": "Zodiac",
        "mbti_title": "MBTI",
        "saju_title": "Comment",
        "today_title": "Today",
        "tomorrow_title": "Tomorrow",
        "overall_title": "2026 Overall",
        "combo_title": "Combo advice",
        "lucky_color_title": "Lucky color",
        "lucky_item_title": "Lucky item",
        "tip_title": "Tip",
        "copied": "Copied! Paste it anywhere.",
        "share_hint": "Mobile opens share sheet. PC copies text.",

        # 12/16 질문(영어로 유지)
        "q12_ei": ["Weekend invite?", "Talking to strangers?", "After social day?"],
        "q12_sn": ["New cafe first notice?", "In books/movies?", "When shopping?"],
        "q12_tf": ["Friend late?", "When conflict?", "When someone cries?"],
        "q12_jp": ["Trip planning?", "Before deadlines?", "Cleaning room?"],
        "a12_e": ["Go out (E)", "Enjoy (E)", "Still energized (E)"],
        "a12_i": ["Stay home (I)", "A bit tired (I)", "Need alone time (I)"],
        "a12_s": ["Practical (S)", "Details (S)", "Essentials (S)"],
        "a12_n": ["Vibe (N)", "Meaning (N)", "Imagine future (N)"],
        "a12_t": ["Direct (T)", "Logic (T)", "Offer solutions (T)"],
        "a12_f": ["Gentle (F)", "Mediate (F)", "Empathize (F)"],
        "a12_j": ["Plan (J)", "Finish early (J)", "Neat (J)"],
        "a12_p": ["Spontaneous (P)", "Last-minute (P)", "Messy ok (P)"],

        "q_energy": ["Weekend invite?", "Talk to strangers?", "After social day?", "When you think?"],
        "q_info": ["New cafe first notice?", "Friend worries?", "Books/movies?", "Shopping?"],
        "q_decision": ["Friend late?", "Team conflict?", "Someone cries?", "Spot a lie?"],
        "q_life": ["Trip planning?", "Before deadline?", "Cleaning room?", "Choosing?"],
        "options_e": ["Go right away (E)", "Fun! (E)", "Still energized (E)", "Speak it out (E)"],
        "options_i": ["Stay home (I)", "A bit tired (I)", "Need alone time (I)", "Process in head (I)"],
        "options_s": ["Prices/items (S)", "Facts (S)", "Details (S)", "Buy essentials (S)"],
        "options_n": ["Vibe/concept (N)", "Possibilities (N)", "Symbols (N)", "Imagine future use (N)"],
        "options_t": ["Direct (T)", "Logic (T)", "Suggest fix (T)", "Point out (T)"],
        "options_f": ["Gentle (F)", "Mediate (F)", "Empathize (F)", "Let it pass (F)"],
        "options_j": ["Plan (J)", "Finish early (J)", "Neat (J)", "Decide fast (J)"],
        "options_p": ["Spontaneous (P)", "Last-minute (P)", "Messy ok (P)", "Explore more (P)"],
    },

    # 다른 언어는 최소 UI만(깨지지 않게)
    "ja": {"lang_label": "言語", "title": "2026 運勢 + MBTI", "caption": "無料", "birth": "生年月日", "name_placeholder": "名前(任意)",
           "mbti_mode": "MBTI", "direct": "直接入力", "test12": "簡単(12)", "test16": "詳細(16)",
           "test_start_12": "開始(12)", "test_start_16": "開始(16)", "energy":"E/I","info":"S/N","decision":"T/F","life":"J/P",
           "result_btn":"結果","fortune_btn":"運勢","reset":"最初から","share_btn":"共有","tarot_btn":"タロット","tarot_title":"今日のタロット",
           "zodiac_title":"干支","mbti_title":"MBTI","saju_title":"一言","today_title":"今日","tomorrow_title":"明日","overall_title":"2026",
           "combo_title":"助言","lucky_color_title":"色","lucky_item_title":"物","tip_title":"ヒント","copied":"コピーしました","share_hint":"共有/コピー"},
    "zh": {"lang_label": "语言", "title": "2026 运势 + MBTI", "caption": "免费", "birth": "出生日期", "name_placeholder": "姓名(可选)",
           "mbti_mode": "MBTI", "direct": "直接输入", "test12": "简测(12)", "test16": "详测(16)",
           "test_start_12": "开始(12)", "test_start_16": "开始(16)", "energy":"E/I","info":"S/N","decision":"T/F","life":"J/P",
           "result_btn":"结果","fortune_btn":"查看运势","reset":"重新开始","share_btn":"分享","tarot_btn":"塔罗","tarot_title":"今日塔罗",
           "zodiac_title":"生肖","mbti_title":"MBTI","saju_title":"一句话","today_title":"今天","tomorrow_title":"明天","overall_title":"2026",
           "combo_title":"建议","lucky_color_title":"幸运色","lucky_item_title":"幸运物","tip_title":"提示","copied":"已复制","share_hint":"分享/复制"},
    "ru": {"lang_label": "Язык", "title": "2026 Удача + MBTI", "caption": "Бесплатно", "birth": "Дата рождения", "name_placeholder": "Имя(необяз.)",
           "mbti_mode": "MBTI", "direct": "Ввести", "test12": "Тест(12)", "test16": "Тест(16)",
           "test_start_12": "Старт(12)", "test_start_16": "Старт(16)", "energy":"E/I","info":"S/N","decision":"T/F","life":"J/P",
           "result_btn":"Результат","fortune_btn":"Удача","reset":"Сначала","share_btn":"Поделиться","tarot_btn":"Таро","tarot_title":"Таро",
           "zodiac_title":"Знак","mbti_title":"MBTI","saju_title":"Комментарий","today_title":"Сегодня","tomorrow_title":"Завтра","overall_title":"2026",
           "combo_title":"Совет","lucky_color_title":"Цвет","lucky_item_title":"Предмет","tip_title":"Совет","copied":"Скопировано","share_hint":"Share/Copy"},
}


# =========================
# 2) 데이터(띠/MBTI/문구)
# =========================
MBTI_LABELS_KO = {
    "INTJ": "냉철 전략가", "INTP": "아이디어 천재", "ENTJ": "리더형", "ENTP": "토론왕",
    "INFJ": "마음 마스터", "INFP": "감성 예술가", "ENFJ": "모두 선생님", "ENFP": "인간 비타민",
    "ISTJ": "규칙 지킴이", "ISFJ": "세상 따뜻함", "ESTJ": "현실 리더", "ESFJ": "분위기 메이커",
    "ISTP": "고치는 장인", "ISFP": "감성 힐러", "ESTP": "모험왕", "ESFP": "파티 주인공"
}
MBTI_LABELS_EN = {
    "INTJ": "Strategist", "INTP": "Thinker", "ENTJ": "Commander", "ENTP": "Debater",
    "INFJ": "Advocate", "INFP": "Mediator", "ENFJ": "Protagonist", "ENFP": "Campaigner",
    "ISTJ": "Logistician", "ISFJ": "Defender", "ESTJ": "Executive", "ESFJ": "Consul",
    "ISTP": "Virtuoso", "ISFP": "Adventurer", "ESTP": "Entrepreneur", "ESFP": "Entertainer"
}

ZODIAC_NAMES = {
    "ko": ["쥐띠", "소띠", "호랑이띠", "토끼띠", "용띠", "뱀띠", "말띠", "양띠", "원숭이띠", "닭띠", "개띠", "돼지띠"],
    "en": ["Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake", "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"],
    "ja": ["鼠", "牛", "虎", "兎", "龍", "蛇", "馬", "羊", "猿", "鶏", "犬", "猪"],
    "zh": ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"],
    "ru": ["Крыса", "Бык", "Тигр", "Кролик", "Дракон", "Змея", "Лошадь", "Коза", "Обезьяна", "Петух", "Собака", "Свинья"],
}

ZODIAC_DESC_KO = {
    "쥐띠": "기회 감지력이 좋아요. 빠른 선택이 복이 됩니다.",
    "소띠": "꾸준함이 강점! 한 번 정한 목표는 밀어붙이세요.",
    "호랑이띠": "도전운 상승! 리더십이 빛나는 시기입니다.",
    "토끼띠": "변화에 유연하게. 안전장치를 만들면 더 좋아요.",
    "용띠": "운기 상승! 인정받고 성장할 가능성이 큽니다.",
    "뱀띠": "직감과 실속의 해. 정보력이 곧 돈입니다.",
    "말띠": "추진력 최고! 다만 과속은 금물, 균형이 핵심.",
    "양띠": "편안함 속 성과. 주변 도움을 잘 받는 운입니다.",
    "원숭이띠": "재능 발휘! 아이디어가 성과로 연결됩니다.",
    "닭띠": "노력 결실! 꾸준히 하면 눈에 띄는 결과가 나와요.",
    "개띠": "귀인운! 협업/네트워킹이 행운의 열쇠입니다.",
    "돼지띠": "여유 속 대박운! 좋은 타이밍이 찾아옵니다."
}

SAJU_MSG_KO = [
    "목(木) 기운 → 성장/확장 운이 좋아요.",
    "화(火) 기운 → 열정/도전 운이 강해요.",
    "토(土) 기운 → 안정/재물 운이 좋아요.",
    "금(金) 기운 → 결단/성과 운이 좋아요.",
    "수(水) 기운 → 지혜/흐름 운이 좋아요.",
    "오행 균형 → 무리하지 않으면 안정적이에요.",
    "양기 강함 → 도전하면 크게 얻을 수 있어요.",
    "음기 강함 → 내면 정리/관계 정리가 행운입니다."
]


# =========================
# 3) 유틸 함수
# =========================
def get_zodiac(year: int, lang: str):
    z_list = ZODIAC_NAMES.get(lang, ZODIAC_NAMES["en"])
    if 1900 <= year <= 2030:
        return z_list[(year - 4) % 12]
    return None

def get_saju(year: int, month: int, day: int, lang: str):
    if lang != "ko":
        return "A calm and balanced message."
    total = year + month + day
    return SAJU_MSG_KO[total % len(SAJU_MSG_KO)]

def deterministic_daily_msg(zodiac_index: int, offset_days: int, msgs: list[str]):
    now = datetime.now() + timedelta(days=offset_days)
    seed = int(now.strftime("%Y%m%d")) + zodiac_index * 97 + 13
    random.seed(seed)
    return random.choice(msgs)

def sha_phone(phone: str) -> str:
    digits = "".join([c for c in phone if c.isdigit()])
    return hashlib.sha256(digits.encode("utf-8")).hexdigest()


# =========================
# 4) 구글시트
# =========================
def get_sheet():
    if not USE_GOOGLE_SHEETS:
        return None
    try:
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        client = gspread.authorize(creds)
        sh = client.open_by_key(SHEET_ID)
        ws = sh.worksheet(WORKSHEET_NAME)
        return ws
    except Exception:
        return None

def sheet_get_stats(ws):
    values = ws.get_all_values()
    if len(values) <= 1:
        return 0, set()
    rows = values[1:]
    hashed = set()
    for r in rows:
        if len(r) >= 3 and r[2]:
            hashed.add(r[2])
    return len(rows), hashed

def sheet_append_entry(ws, name, phone, lang, elapsed):
    phone_hash = sha_phone(phone)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # A:이름 B:전화 C:해시 D:언어 E:시간 F:기록 G:메모
    ws.append_row([name, phone, phone_hash, lang, ts, f"{elapsed:.3f}", "coffee_coupon"])
    return phone_hash


# =========================
# 5) 세션 초기화
# =========================
st.set_page_config(page_title="2026 Fortune", layout="centered")

defaults = {
    "lang": "ko",
    "step": "input",  # input | result
    "name": "",
    "year": 2005,
    "month": 1,
    "day": 1,
    "mbti": None,

    # 공유/추가기회
    "share_clicked": False,

    # 미니게임 상태
    "mg_attempts_used": 0,
    "mg_started_at": None,
    "mg_last_elapsed": None,
    "mg_passed": False,
    "mg_entry_done": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# =========================
# 6) 공유 버튼 무반응 복구 방식
#   - HTML(JS) 버튼 클릭 → URL에 ?shared=1 붙이고 리로드
#   - Python에서 shared=1 감지 → share_clicked=True 적용 → 파라미터 제거
# =========================
qp = st.experimental_get_query_params()
if qp.get("shared", ["0"])[0] == "1":
    st.session_state.share_clicked = True
    # 파라미터 제거(무한 루프 방지)
    st.experimental_set_query_params()


# =========================
# 7) CSS (결과 가독성 + 배경색 개선)
# =========================
st.markdown("""
<style>
    :root{
        --bg: #f5f7fb;
        --card: #ffffff;
        --text: #1f2a37;
        --muted: #6b7280;
        --border: rgba(0,0,0,0.08);
        --shadow: 0 10px 28px rgba(0,0,0,0.08);
        --accent: #8e44ad;
        --accent2: #2d6cdf;
        --ok: #16a34a;
        --bad: #dc2626;
        --warn: #f59e0b;
    }
    html, body, [class*="css"] {font-family: 'Noto Sans KR', sans-serif;}
    body {background: var(--bg);}
    .wrap {max-width: 860px; margin: 0 auto; padding: 6px 10px 30px;}
    .hero {text-align:center; padding: 10px 8px 6px;}
    .hero h1 {margin: 0; font-size: 1.65rem; line-height: 1.2; color: var(--text);}
    .hero p {margin: 8px 0 0; color: var(--muted); font-size: 0.95rem;}
    .card{
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 16px 14px;
        margin: 12px 0;
        box-shadow: var(--shadow);
    }
    .result-head{
        background: linear-gradient(180deg, #ffffff 0%, #faf7ff 100%);
        border: 1px solid rgba(142,68,173,0.18);
        border-radius: 18px;
        padding: 16px 14px;
        margin: 12px 0;
        box-shadow: 0 12px 30px rgba(142,68,173,0.10);
        text-align:center;
    }
    .result-title{
        font-size: 1.45rem;
        font-weight: 900;
        color: #2b1a3a;
        margin: 0 0 6px;
        line-height:1.25;
    }
    .result-sub{
        font-size: 1.05rem;
        color: var(--muted);
        margin: 0;
        line-height:1.35;
    }
    .kv{
        font-size: 1.02rem;
        color: var(--text);
        line-height: 1.75;
    }
    .kv b{color: var(--text);}
    .divider{height:1px;background:rgba(0,0,0,0.06);margin:10px 0;}
    .ad-box{
        border: 2px solid rgba(230,126,34,0.55);
        border-radius: 18px;
        padding: 14px 12px;
        background: rgba(255,252,240,0.92);
        text-align:center;
        margin: 14px 0;
    }
    .ad-box h3{margin: 0 0 6px; color:#d35400; font-size: 1.05rem;}
    .ad-box p{margin: 0 0 10px; color:#333; font-size: 0.95rem; line-height:1.45;}
    .btn-link{
        display:inline-block;
        background:#e67e22;
        color:white;
        padding:10px 18px;
        border-radius:14px;
        text-decoration:none;
        font-weight:900;
    }
    .hint{
        text-align:center;
        font-size:0.92rem;
        color: var(--muted);
        margin-top: 6px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='wrap'>", unsafe_allow_html=True)


# =========================
# 8) 언어 선택
# =========================
lang = st.radio(
    translations.get(st.session_state.lang, translations["en"])["lang_label"],
    LANGS,
    index=LANGS.index(st.session_state.lang) if st.session_state.lang in LANGS else 0,
    horizontal=True
)
st.session_state.lang = lang
t = translations.get(lang, translations["en"])


# =========================
# 9) 화면 전환 유틸
# =========================
def go_result(mbti_code: str):
    st.session_state.mbti = mbti_code
    st.session_state.step = "result"
    st.rerun()

def reset_all():
    st.session_state.clear()
    st.rerun()


# =========================
# 10) 입력 화면
# =========================
if st.session_state.step == "input":
    st.markdown(f"""
    <div class="hero">
        <h1>{t.get("title","2026 Fortune")}</h1>
        <p>{t.get("caption","")}</p>
    </div>
    """, unsafe_allow_html=True)

    # 한국어만 광고
    if lang == "ko":
        st.markdown(f"""
        <div class="ad-box">
            <h3>{t["ad_title"]}</h3>
            <p>{t["ad_body"]}</p>
            <a class="btn-link" href="https://www.다나눔렌탈.com" target="_blank">{t["ad_btn"]}</a>
        </div>
        """, unsafe_allow_html=True)

    st.session_state.name = st.text_input(t.get("name_placeholder","Name"), value=st.session_state.name)

    st.markdown(f"<div class='card'><b>{t.get('birth','Birth')}</b></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    st.session_state.year = c1.number_input("Year" if lang != "ko" else "년", 1900, 2030, st.session_state.year, 1)
    st.session_state.month = c2.number_input("Month" if lang != "ko" else "월", 1, 12, st.session_state.month, 1)
    st.session_state.day = c3.number_input("Day" if lang != "ko" else "일", 1, 31, st.session_state.day, 1)

    mbti_choice = st.radio(t.get("mbti_mode","MBTI"), [t.get("direct","Direct"), t.get("test12","12"), t.get("test16","16")])

    mbti_keys = sorted(MBTI_LABELS_KO.keys())

    if mbti_choice == t.get("direct","Direct"):
        mbti_input = st.selectbox("MBTI", mbti_keys)
        if st.button(t.get("fortune_btn","Go"), use_container_width=True):
            go_result(mbti_input)

    elif mbti_choice == t.get("test12","12"):
        st.markdown(f"<div class='card'><b>{t.get('test_start_12','Start')}</b></div>", unsafe_allow_html=True)

        ei = sn = tf = jp = 0

        st.subheader(t.get("energy","Energy"))
        for i in range(3):
            ans = st.radio(t["q12_ei"][i], [t["a12_e"][i], t["a12_i"][i]], key=f"t12_ei_{i}")
            if ans == t["a12_e"][i]:
                ei += 1

        st.subheader(t.get("info","Info"))
        for i in range(3):
            ans = st.radio(t["q12_sn"][i], [t["a12_s"][i], t["a12_n"][i]], key=f"t12_sn_{i}")
            if ans == t["a12_s"][i]:
                sn += 1

        st.subheader(t.get("decision","Decision"))
        for i in range(3):
            ans = st.radio(t["q12_tf"][i], [t["a12_t"][i], t["a12_f"][i]], key=f"t12_tf_{i}")
            if ans == t["a12_t"][i]:
                tf += 1

        st.subheader(t.get("life","Life"))
        for i in range(3):
            ans = st.radio(t["q12_jp"][i], [t["a12_j"][i], t["a12_p"][i]], key=f"t12_jp_{i}")
            if ans == t["a12_j"][i]:
                jp += 1

        if st.button(t.get("result_btn","Result"), use_container_width=True):
            mbti_code = ("E" if ei >= 2 else "I") + ("S" if sn >= 2 else "N") + ("T" if tf >= 2 else "F") + ("J" if jp >= 2 else "P")
            go_result(mbti_code)

    else:
        st.markdown(f"<div class='card'><b>{t.get('test_start_16','Start')}</b></div>", unsafe_allow_html=True)
        e_i = s_n = t_f = j_p = 0

        st.subheader(t.get("energy","Energy"))
        for i in range(4):
            ans = st.radio(t["q_energy"][i], [t["options_e"][i], t["options_i"][i]], key=f"t16_ei_{i}")
            if ans == t["options_e"][i]:
                e_i += 1

        st.subheader(t.get("info","Info"))
        for i in range(4):
            ans = st.radio(t["q_info"][i], [t["options_s"][i], t["options_n"][i]], key=f"t16_sn_{i}")
            if ans == t["options_s"][i]:
                s_n += 1

        st.subheader(t.get("decision","Decision"))
        for i in range(4):
            ans = st.radio(t["q_decision"][i], [t["options_t"][i], t["options_f"][i]], key=f"t16_tf_{i}")
            if ans == t["options_t"][i]:
                t_f += 1

        st.subheader(t.get("life","Life"))
        for i in range(4):
            ans = st.radio(t["q_life"][i], [t["options_j"][i], t["options_p"][i]], key=f"t16_jp_{i}")
            if ans == t["options_j"][i]:
                j_p += 1

        if st.button(t.get("result_btn","Result"), use_container_width=True):
            mbti_code = ("E" if e_i >= 3 else "I") + ("S" if s_n >= 3 else "N") + ("T" if t_f >= 3 else "F") + ("J" if j_p >= 3 else "P")
            go_result(mbti_code)

    if st.button(t.get("reset","Reset"), use_container_width=True):
        reset_all()


# =========================
# 11) 결과 화면
# =========================
if st.session_state.step == "result":
    mbti = st.session_state.mbti
    zodiac = get_zodiac(st.session_state.year, lang)
    if zodiac is None:
        st.error("Please enter a birth year between 1900 and 2030!" if lang != "ko" else "생년은 1900~2030년 사이로 입력해주세요!")
        if st.button(t.get("reset","Reset"), use_container_width=True):
            reset_all()
        st.stop()

    # MBTI 설명
    mbti_desc = (MBTI_LABELS_KO.get(mbti) if lang == "ko" else MBTI_LABELS_EN.get(mbti)) or mbti

    # 띠 설명(한국어는 풍부)
    if lang == "ko":
        zodiac_desc = ZODIAC_DESC_KO.get(zodiac, "")
        zodiac_index = ZODIAC_NAMES["ko"].index(zodiac)
    else:
        zodiac_desc = zodiac
        zodiac_index = ZODIAC_NAMES.get(lang, ZODIAC_NAMES["en"]).index(zodiac)

    # 운세 문구
    daily_msgs = translations["ko"]["options_e"]  # placeholder 방지(아래서 교체)
    if lang == "ko":
        daily_pool = [
            "재물운이 좋아요! 작은 선택이 이득으로 이어져요.",
            "연애/인연운이 좋아요! 먼저 연락해도 좋아요.",
            "건강운 체크! 무리하지 말고 리듬을 지켜요.",
            "전체운 상승! 타이밍이 좋아요.",
            "인간관계운 호조! 도움 받을 일이 생겨요.",
            "일/학업운 호조! 집중력이 올라가요.",
            "이동/여행운 좋음! 기분전환 추천!",
            "기분 좋은 하루! 웃음이 더 큰 운을 불러요."
        ]
    else:
        daily_pool = [
            "Wealth luck is good; small choices pay off.",
            "Love/connection luck is good; reach out first.",
            "Mind your health; keep your rhythm.",
            "Overall luck rises; timing is on your side.",
            "Relationships are smooth; help comes in.",
            "Work/study luck is good; focus increases.",
            "Travel/move luck is good; refresh yourself!",
            "A happy day: laughter attracts luck."
        ]

    overall_pool = ([
        "성장과 재물이 함께하는 해! 기회가 자주 와요.",
        "안정과 행복이 커지는 해! 관계운이 좋아요.",
        "도전과 성과의 해! 실력이 인정받아요.",
        "인연과 사랑운이 강해지는 해! 마음이 따뜻해져요.",
        "변화와 새출발의 해! 아이디어가 빛나요."
    ] if lang == "ko" else [
        "A year of growth and opportunities!",
        "A stable year with stronger relationships!",
        "A year of challenges and achievements!",
        "A warmer year with love and connections!",
        "A year of change and fresh starts!"
    ])

    tips_pool = ([
        "작은 약속을 지키면 큰 운이 따라와요.",
        "과감한 결정보단 ‘검증 후 실행’이 유리해요.",
        "컨디션 관리가 곧 운 관리! 수면을 챙겨요.",
        "가까운 사람과의 대화가 행운의 열쇠예요.",
        "배움/취미 하나를 시작하면 흐름이 바뀌어요."
    ] if lang == "ko" else [
        "Small consistency brings big luck.",
        "Validate before acting; it pays off.",
        "Health is luck: protect your sleep.",
        "Talk with close people; it opens doors.",
        "Start a hobby; it changes the flow."
    ])

    saju = get_saju(st.session_state.year, st.session_state.month, st.session_state.day, lang)

    today_msg = deterministic_daily_msg(zodiac_index, 0, daily_pool)
    tomorrow_msg = deterministic_daily_msg(zodiac_index, 1, daily_pool)

    overall = random.choice(overall_pool)
    lucky_color = random.choice((["골드","레드","블루","그린","퍼플"] if lang == "ko" else ["Gold","Red","Blue","Green","Purple"]))
    lucky_item = random.choice((["황금 액세서리","빨간 지갑","파란 목걸이","초록 식물","보라색 펜"] if lang == "ko" else ["Golden accessory","Red wallet","Blue necklace","Green plant","Purple pen"]))
    tip = random.choice(tips_pool)

    # 조합 조언(요청: MBTI 영향 반영)
    if lang == "ko":
        combo_advice = (
            f"'{mbti}'는 {('계획/정리' if 'J' in mbti else '유연/즉흥')}에 강점이 있어요. "
            f"올해 '{zodiac}' 흐름에서는 "
            f"{('루틴을 만들면 운이 커지고' if 'J' in mbti else '기회를 잡는 순발력이 복이 되고')} "
            f"{('결정 전 1번 더 검증' if 'T' in mbti else '감정 소진 방지선 확보')}이 핵심이에요."
        )
    else:
        combo_advice = f"Your MBTI ({mbti}) shapes your decision style. Use your strengths to ride this year's flow."

    # 이름 표시
    name_display = st.session_state.name.strip()
    if lang == "ko" and name_display:
        name_display = f"{name_display}님"

    # 결과 헤더(가독성 강화)
    st.markdown(f"""
    <div class="result-head">
        <div class="result-title">{(name_display + " " if name_display else "")}{("2026 운세" if lang=="ko" else "2026 Fortune")}</div>
        <div class="result-sub">{zodiac}  ·  {mbti} ({mbti_desc})</div>
    </div>
    """, unsafe_allow_html=True)

    # 결과 카드
    st.markdown(f"""
    <div class="card kv">
        <div><b>{t.get("zodiac_title","Zodiac")}</b>: {zodiac_desc}</div>
        <div><b>{t.get("mbti_title","MBTI")}</b>: {mbti_desc}</div>
        <div><b>{t.get("saju_title","Comment")}</b>: {saju}</div>
        <div class="divider"></div>
        <div><b>{t.get("today_title","Today")}</b>: {today_msg}</div>
        <div><b>{t.get("tomorrow_title","Tomorrow")}</b>: {tomorrow_msg}</div>
        <div class="divider"></div>
        <div><b>{t.get("overall_title","Overall")}</b>: {overall}</div>
        <div><b>{t.get("combo_title","Advice")}</b>: {combo_advice}</div>
        <div><b>{t.get("lucky_color_title","Color")}</b>: {lucky_color}  |  <b>{t.get("lucky_item_title","Item")}</b>: {lucky_item}</div>
        <div><b>{t.get("tip_title","Tip")}</b>: {tip}</div>
    </div>
    """, unsafe_allow_html=True)

    # =========================
    # 11-1) 공유 버튼(복구)
    #  - HTML 버튼 클릭 시 navigator.share(모바일) / clipboard(PC)
    #  - 그리고 URL에 ?shared=1 붙여서 Python이 share_clicked=True로 인식
    # =========================
    share_text = (
        f"{(name_display + ' ' if name_display else '')}{('2026 운세' if lang=='ko' else '2026 Fortune')}\n\n"
        f"{zodiac} + {mbti}\n\n"
        f"{t.get('today_title','Today')}: {today_msg}\n"
        f"{t.get('tomorrow_title','Tomorrow')}: {tomorrow_msg}\n\n"
        f"{t.get('overall_title','Overall')}: {overall}\n"
        f"{t.get('combo_title','Advice')}: {combo_advice}\n"
        f"{t.get('lucky_color_title','Color')}: {lucky_color} / {t.get('lucky_item_title','Item')}: {lucky_item}\n"
        f"{t.get('tip_title','Tip')}: {tip}\n\n"
        f"{APP_URL}"
    )

    share_payload = json.dumps({"text": share_text, "title": "2026 Fortune", "url": APP_URL}, ensure_ascii=False)

    components.html(
        f"""
        <div style="width:100%; text-align:center; margin: 8px 0 0;">
          <button id="shareBtn"
            style="width:100%; max-width:640px; background:#ffffff; color:#8e44ad; padding:14px 18px; border:none;
                   border-radius:999px; font-size:1.05rem; font-weight:900;
                   box-shadow: 0 10px 22px rgba(142,68,173,0.18); cursor:pointer;">
            {t.get("share_btn","Share")}
          </button>
          <div style="margin-top:8px; font-size:0.92rem; color:#6b7280;">
            {t.get("share_hint","")}
          </div>
        </div>

        <script>
          const payload = {share_payload};
          const btn = document.getElementById("shareBtn");

          btn.addEventListener("click", async () => {{
            try {{
              if (navigator.share) {{
                await navigator.share(payload);
              }} else {{
                await navigator.clipboard.writeText(payload.text);
                alert({json.dumps(t.get("copied","Copied!"), ensure_ascii=False)});
              }}
            }} catch(e) {{
              // 사용자가 공유 취소해도 아래 로직으로 추가기회는 부여(요청 반영)
            }}

            // 공유 클릭 기록: URL에 shared=1 붙여 리로드 → Python에서 share_clicked=True 처리
            const base = window.location.origin + window.location.pathname;
            window.location.href = base + "?shared=1";
          }});
        </script>
        """,
        height=120
    )

    # =========================
    # 11-2) 타로
    # =========================
    tarot_cards = (translations["ko"]["tarot_cards"] if "tarot_cards" in translations["ko"] else {
        "The Sun": "행복, 성공, 긍정 에너지"
    })
    if st.button(t.get("tarot_btn","Tarot"), use_container_width=True):
        tarot_card = random.choice(list(tarot_cards.keys()))
        tarot_meaning = tarot_cards[tarot_card]
        st.markdown(f"""
        <div class="card" style="text-align:center;">
            <h3 style="margin:0; color:#8e44ad;">{t.get("tarot_title","Tarot")}</h3>
            <div style="font-size:1.5rem; font-weight:900; margin-top:8px; color:#111;">{tarot_card}</div>
            <div style="margin-top:6px; color:#333; font-size:1.05rem; line-height:1.6;">{tarot_meaning}</div>
        </div>
        """, unsafe_allow_html=True)

    # =========================
    # 11-3) (한국어만) 미니게임 + 선착순 + 중복방지 + 구글시트 저장
    #  - 스톱워치: JS로 "이미지처럼 큰 디지털 표시"
    # =========================
    if EVENT_ENABLED and lang == EVENT_LANGUAGE_ONLY:
        st.markdown(f"""
        <div class="card">
            <div style="font-weight:900; font-size:1.15rem; color:#111;">{t["event_title"]}</div>
            <div style="margin-top:6px; color:#374151; font-size:0.98rem; line-height:1.55;">
              {t["event_desc"]}<br>
              <span style="color:#6b7280;">목표: <b>{TARGET_SECONDS:.2f}s</b> / 허용오차: <b>±{PASS_TOLERANCE:.2f}s</b></span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        ws = get_sheet()
        if ws is None:
            st.warning("구글시트 연결이 아직 안 되어 있어요. (Secrets/requirements/시트 공유 확인 필요)")
        else:
            try:
                current_count, hashed_set = sheet_get_stats(ws)
            except Exception:
                current_count, hashed_set = 0, set()

            if current_count >= WINNER_LIMIT:
                st.info(t["event_closed"])
            else:
                total_attempts = BASE_ATTEMPTS + (EXTRA_ATTEMPTS_ON_SHARE if st.session_state.share_clicked else 0)
                attempts_left = max(0, total_attempts - st.session_state.mg_attempts_used)

                st.markdown(f"""
                <div class="card">
                    <b>{t["event_attempts_left"]}</b>: {attempts_left} / {total_attempts}
                    <div style="margin-top:6px; color:#6b7280; font-size:0.92rem;">
                        {"(공유 클릭됨: 추가 기회 +1 적용)" if st.session_state.share_clicked else t["event_need_share"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # --- 스톱워치 디지털 표시(이미지처럼 보이게) ---
                start_ts = st.session_state.mg_started_at
                start_ts_js = "null" if start_ts is None else str(float(start_ts))

                components.html(
                    f"""
                    <div style="width:100%; display:flex; justify-content:center; margin: 6px 0 0;">
                      <div id="watch"
                        style="
                          width:100%;
                          max-width:640px;
                          background: linear-gradient(180deg, #0b1220 0%, #111827 100%);
                          border: 1px solid rgba(255,255,255,0.10);
                          border-radius: 18px;
                          padding: 18px 16px;
                          box-shadow: 0 18px 40px rgba(0,0,0,0.18);
                          text-align:center;
                        ">
                        <div style="color: rgba(255,255,255,0.75); font-size:0.92rem; margin-bottom:10px;">
                          STOPWATCH
                        </div>
                        <div id="time"
                          style="
                            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
                            font-size: 3.2rem;
                            font-weight: 900;
                            letter-spacing: 0.06em;
                            color: #e5e7eb;
                            text-shadow: 0 0 18px rgba(45,108,223,0.35);
                            line-height:1;
                          ">00.000</div>
                        <div style="margin-top:10px; color: rgba(255,255,255,0.65); font-size:0.92rem;">
                          Target: <b style="color:#fff;">{TARGET_SECONDS:.2f}s</b>
                        </div>
                      </div>
                    </div>

                    <script>
                      const startTs = {start_ts_js};
                      const timeEl = document.getElementById("time");
                      let raf = null;

                      function tick(){{
                        if(startTs === null){{
                          timeEl.textContent = "00.000";
                          return;
                        }}
                        const now = Date.now()/1000.0;
                        const elapsed = Math.max(0, now - startTs);
                        timeEl.textContent = elapsed.toFixed(3).padStart(6,'0');
                        raf = requestAnimationFrame(tick);
                      }}

                      if(startTs !== null) {{
                        tick();
                      }}
                    </script>
                    """,
                    height=170
                )

                # 버튼
                cA, cB = st.columns(2)
                start_disabled = (attempts_left <= 0) or (st.session_state.mg_started_at is not None)
                stop_disabled = (st.session_state.mg_started_at is None) or (attempts_left <= 0)

                with cA:
                    if st.button(t["event_start"], use_container_width=True, disabled=start_disabled):
                        st.session_state.mg_started_at = time.time()
                        st.session_state.mg_last_elapsed = None
                        st.session_state.mg_passed = False
                        st.rerun()

                with cB:
                    if st.button(t["event_stop"], use_container_width=True, disabled=stop_disabled):
                        elapsed = time.time() - st.session_state.mg_started_at
                        st.session_state.mg_started_at = None
                        st.session_state.mg_last_elapsed = elapsed
                        st.session_state.mg_attempts_used += 1
                        st.session_state.mg_passed = (abs(elapsed - TARGET_SECONDS) <= PASS_TOLERANCE)
                        st.rerun()

                # 결과 표시
                if st.session_state.mg_last_elapsed is not None:
                    st.markdown(
                        f"<div class='card'><b>{t['event_elapsed']}</b>: {st.session_state.mg_last_elapsed:.3f}s</div>",
                        unsafe_allow_html=True
                    )
                    if st.session_state.mg_passed:
                        st.success(t["event_success"])
                    else:
                        st.error(t["event_fail"])

                # 통과하면 응모 폼
                if st.session_state.mg_passed and (not st.session_state.mg_entry_done):
                    consent_text = f"""
- **수집 항목**: 이름, 휴대폰번호  
- **이용 목적**: 커피쿠폰 당첨자 확인 및 쿠폰 발송, 문의 응대  
- **보유·이용 기간**: 응모일로부터 {DATA_RETENTION_DAYS}일 또는 경품 발송/문의 응대 완료 시까지(먼저 도래하는 시점)  
- **동의 거부 권리**: 동의를 거부할 수 있으며, 거부 시 쿠폰 응모는 제한됩니다. (운세 서비스 이용은 가능)  
- **처리/보관 방식**: 구글 스프레드시트에 저장되며, 목적 달성 후 지체 없이 파기합니다.  
                    """.strip()

                    st.markdown(f"<div class='card'><b>{t['event_form_title']}</b></div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='card'><b>{t['consent_title']}</b><br><br>{consent_text}</div>", unsafe_allow_html=True)

                    consent_ok = st.checkbox(t["consent_check"], value=False)
                    st.caption(t["consent_more"])

                    entry_name = st.text_input(t["name_label"], value=st.session_state.name.strip())
                    entry_phone = st.text_input(t["phone_label"], placeholder=t["phone_hint"])

                    if st.button(t["submit_entry"], use_container_width=True, disabled=not consent_ok):
                        phone_digits = "".join([c for c in entry_phone if c.isdigit()])
                        if len(phone_digits) < 10 or len(phone_digits) > 11:
                            st.error("전화번호를 정확히 입력해주세요. (숫자만 10~11자리)")
                        elif not entry_name.strip():
                            st.error("이름을 입력해주세요.")
                        else:
                            try:
                                # 최신 상태 재조회
                                current_count2, hashed_set2 = sheet_get_stats(ws)
                                if current_count2 >= WINNER_LIMIT:
                                    st.info(t["event_closed"])
                                else:
                                    h = sha_phone(phone_digits)
                                    if h in hashed_set2:
                                        st.warning(t["entry_dup"])
                                    else:
                                        sheet_append_entry(ws, entry_name.strip(), phone_digits, lang, st.session_state.mg_last_elapsed or 0.0)
                                        st.session_state.mg_entry_done = True
                                        st.success(t["entry_ok"])
                            except Exception:
                                st.error(t["entry_error"])

                if st.session_state.mg_entry_done:
                    st.markdown("<div class='card'><b>✅ 응모 완료</b><br>선착순/중복 여부는 시트 기록 순서로 확정됩니다.</div>", unsafe_allow_html=True)

    # 하단 URL
    st.markdown(f"<div class='hint'>{APP_URL}</div>", unsafe_allow_html=True)

    if st.button(t.get("reset","Reset"), use_container_width=True):
        reset_all()

st.markdown("</div>", unsafe_allow_html=True)
