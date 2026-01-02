import streamlit as st
from datetime import datetime, timedelta
import random
import time
import hashlib

# (선택) 구글시트 사용: requirements.txt에 gspread/google-auth 추가 + Streamlit Secrets 설정 필요
USE_GOOGLE_SHEETS = True
try:
    import gspread
    from google.oauth2.service_account import Credentials
except Exception:
    USE_GOOGLE_SHEETS = False


# =========================
# 0) 설정값 (여기만 네 걸로 바꾸면 됨)
# =========================
APP_URL = "https://my-fortune.streamlit.app"  # 배포 URL

# 구글시트 저장용
SHEET_ID = "여기에_너의_구글시트_ID를_넣어줘"   # https://docs.google.com/spreadsheets/d/1WvuKXx2if2WvxmQaxkqzFW-BzDEWWma9hZgCr2jJQYY/edit?gid=0#gid=0
WORKSHEET_NAME = "Sheet1"                    # 첫 시트 이름(기본 Sheet1)

# 쿠폰 이벤트 옵션
EVENT_ENABLED = True
EVENT_LANGUAGE_ONLY = "ko"    # 한국어에서만 이벤트 표시
WINNER_LIMIT = 20
TARGET_SECONDS = 20.26
PASS_TOLERANCE = 0.15         # 허용 오차(초): 0.15면 20.11~20.41
BASE_ATTEMPTS = 1             # 기본 기회 1회
EXTRA_ATTEMPTS_ON_SHARE = 1   # 친구공유 클릭 시 +1회

# 개인정보 보관 기간(문구/실제 운영 정책에 맞춰 조정)
DATA_RETENTION_DAYS = 90      # 90일 보관 예시


# =========================
# 1) 다국어 텍스트 (핵심 UI 텍스트만)
# =========================
translations = {
    "ko": {
        "lang_label": "언어 / Language",
        "title": "2026 띠 + MBTI + 사주 + 오늘/내일 운세",
        "caption": "완전 무료",
        "birth": "### 생년월일 입력",
        "name_placeholder": "이름 입력 (결과에 표시돼요)",
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

        # 한국어에서만 노출할 광고(요청 반영)
        "ad_title": "정수기렌탈 궁금할 때?",
        "ad_body": "다나눔렌탈 제휴카드 시 월 0원부터 + 설치당일 최대 현금 50만원 페이백!",
        "ad_btn": "보러가기",

        # 이벤트(커피쿠폰)
        "event_title": "🎁 미니게임: 선착순 20명 커피쿠폰 도전!",
        "event_desc": "타이머를 정확히 20.26초에 맞추면 응모 가능! (기본 1회, 친구공유 누르면 1회 추가)",
        "event_closed": "😢 선착순 20명이 마감되었습니다. 다음 이벤트를 기대해주세요!",
        "event_attempts_left": "남은 기회",
        "event_start": "시작",
        "event_stop": "멈춤",
        "event_success": "✅ 성공! (기준 시간에 매우 근접했어요)",
        "event_fail": "❌ 아쉽게 실패! 다시 도전해보세요.",
        "event_elapsed": "기록",
        "event_need_share": "추가기회를 원하면 ‘친구에게 결과 공유하기’를 한 번 눌러주세요.",
        "event_form_title": "☕ 커피쿠폰 응모 정보 입력",
        "consent_title": "개인정보 수집·이용 동의",
        "consent_check": "위 내용을 읽었으며, 개인정보 수집·이용에 동의합니다. (필수)",
        "consent_more": "동의하지 않으면 쿠폰 응모는 할 수 없지만, 운세 서비스 이용은 가능합니다.",
        "submit_entry": "응모하기",
        "entry_ok": "🎉 응모가 완료되었습니다! (선착순 여부는 시트에 기록된 순서로 확정됩니다.)",
        "entry_dup": "이미 응모하신 전화번호입니다. (중복 응모 불가)",
        "entry_error": "저장 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
        "phone_label": "전화번호(쿠폰 발송용)",
        "name_label": "이름(응모자)",
        "phone_hint": "예: 01012345678 (하이픈 없이)",

        # MBTI 12문항(각 축 3문항)
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

        # 16문항(각 축 4문항)
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

        # 콘텐츠(간단)
        "overall_fortunes": [
            "성장과 재물이 함께하는 해! 기회가 자주 와요.",
            "안정과 행복이 커지는 해! 관계운이 좋아요.",
            "도전과 성과의 해! 실력이 인정받아요.",
            "인연과 사랑운이 강해지는 해! 마음이 따뜻해져요.",
            "변화와 새출발의 해! 아이디어가 빛나요."
        ],
        "lucky_colors": ["골드", "레드", "블루", "그린", "퍼플"],
        "lucky_items": ["황금 액세서리", "빨간 지갑", "파란 목걸이", "초록 식물", "보라색 펜"],
        "tips": [
            "작은 약속을 지키면 큰 운이 따라와요.",
            "과감한 결정보단 ‘검증 후 실행’이 유리해요.",
            "컨디션 관리가 곧 운 관리! 수면을 챙겨요.",
            "가까운 사람과의 대화가 행운의 열쇠예요.",
            "배움/취미 하나를 시작하면 흐름이 바뀌어요."
        ],
        "daily_msgs": [
            "재물운이 좋아요! 작은 선택이 이득으로 이어져요.",
            "연애/인연운이 좋아요! 먼저 연락해도 좋아요.",
            "건강운 체크! 무리하지 말고 리듬을 지켜요.",
            "전체운 상승! 타이밍이 좋아요.",
            "인간관계운 호조! 도움 받을 일이 생겨요.",
            "일/학업운 호조! 집중력이 올라가요.",
            "이동/여행운 좋음! 기분전환 추천!",
            "기분 좋은 하루! 웃음이 더 큰 운을 불러요."
        ],
        "tarot_cards": {
            "The Fool": "새로운 시작, 모험, 순수한 믿음",
            "The Magician": "창조력, 능력 발휘, 집중",
            "The High Priestess": "직감, 신비, 내면의 목소리",
            "The Empress": "풍요, 사랑, 창작",
            "The Emperor": "안정, 구조, 권위",
            "The Lovers": "사랑, 조화, 선택",
            "The Chariot": "승리, 의지, 방향",
            "Strength": "용기, 인내, 부드러운 통제",
            "Wheel of Fortune": "변화, 운, 사이클",
            "The Sun": "행복, 성공, 긍정 에너지",
        },
    },

    # 영어(최소 유지)
    "en": {
        "lang_label": "Language",
        "title": "2026 Zodiac + MBTI + Fortune (Today/Tomorrow)",
        "caption": "Completely Free",
        "birth": "### Enter Birth Date",
        "name_placeholder": "Enter name (shown in result)",
        "mbti_mode": "How to do MBTI?",
        "direct": "Direct input",
        "test12": "Quick test (12 Q)",
        "test16": "Detailed test (16 Q)",
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
        "overall_fortunes": [
            "A year of growth and opportunities!",
            "A stable year with stronger relationships!",
            "A year of challenges and achievements!",
            "A warmer year with love and connections!",
            "A year of change and fresh starts!"
        ],
        "lucky_colors": ["Gold", "Red", "Blue", "Green", "Purple"],
        "lucky_items": ["Golden accessory", "Red wallet", "Blue necklace", "Green plant", "Purple pen"],
        "tips": [
            "Small consistency brings big luck.",
            "Validate before acting; it pays off.",
            "Health is luck: protect your sleep.",
            "Talk with close people; it opens doors.",
            "Start a hobby; it changes the flow."
        ],
        "daily_msgs": [
            "Wealth luck is good; small choices pay off.",
            "Love/connection luck is good; reach out first.",
            "Mind your health; keep your rhythm.",
            "Overall luck rises; timing is on your side.",
            "Relationships are smooth; help comes in.",
            "Work/study luck is good; focus increases.",
            "Travel/move luck is good; refresh yourself!",
            "A happy day: laughter attracts luck."
        ],
        "tarot_cards": {
            "The Fool": "New beginnings, adventure, trust",
            "The Magician": "Power, focus, manifestation",
            "The High Priestess": "Intuition, inner voice",
            "The Empress": "Abundance, love, creativity",
            "The Emperor": "Stability, structure",
            "The Lovers": "Love, harmony, choice",
            "The Chariot": "Victory, will, direction",
            "Strength": "Courage, patience",
            "Wheel of Fortune": "Change, cycles",
            "The Sun": "Joy, success, positivity",
        },

        # 간단한 12/16문항은 영어로 유지(필수 텍스트만)
        "q12_ei": ["Weekend invite?", "Talking to strangers?", "After social day?"],
        "q12_sn": ["New cafe first notice?", "In movies/books?", "When shopping?"],
        "q12_tf": ["Friend late?", "When conflict?", "When someone cries?"],
        "q12_jp": ["Planning trips?", "Before deadlines?", "Cleaning room?"],
        "a12_e": ["Go out (E)", "Enjoy (E)", "Still energized (E)"],
        "a12_i": ["Stay home (I)", "A bit tired (I)", "Need alone time (I)"],
        "a12_s": ["Practical (S)", "Details (S)", "Buy essentials (S)"],
        "a12_n": ["Vibe (N)", "Meaning (N)", "Imagine future (N)"],
        "a12_t": ["Be direct (T)", "Use logic (T)", "Offer solutions (T)"],
        "a12_f": ["Be gentle (F)", "Mediate (F)", "Empathize (F)"],
        "a12_j": ["Plan tight (J)", "Finish early (J)", "Organize (J)"],
        "a12_p": ["Go with flow (P)", "Last-minute (P)", "Messy ok (P)"],

        "q_energy": ["Weekend invite?", "Talk to strangers?", "After social day?", "When you think?"],
        "q_info": ["New cafe first notice?", "Friend worries?", "Books/movies?", "Shopping?"],
        "q_decision": ["Friend late?", "Team conflict?", "Someone cries?", "Spot a lie?"],
        "q_life": ["Trip planning?", "Before deadline?", "Cleaning room?", "Choosing?"],
        "options_e": ["Go right away (E)", "Fun! (E)", "Still energized (E)", "Speak it out (E)"],
        "options_i": ["Stay home (I)", "A bit tired (I)", "Need alone time (I)", "Process in head (I)"],
        "options_s": ["Prices/items (S)", "Facts (S)", "Details (S)", "Buy essentials (S)"],
        "options_n": ["Vibe/concept (N)", "Possibilities (N)", "Symbols (N)", "Imagine future use (N)"],
        "options_t": ["Be direct (T)", "Logic (T)", "Suggest fix (T)", "Point out (T)"],
        "options_f": ["Be gentle (F)", "Mediate (F)", "Empathize (F)", "Let it pass (F)"],
        "options_j": ["Plan tight (J)", "Finish early (J)", "Neat (J)", "Decide fast (J)"],
        "options_p": ["Spontaneous (P)", "Last-minute (P)", "Messy ok (P)", "Explore more (P)"],
    },

    # 다른 언어는 “기능 유지용” 최소 텍스트만 (원하면 나중에 번역 풀셋 확장 가능)
    "ja": {"lang_label": "言語", "title": "2026 運勢 + MBTI", "caption": "無料", "birth": "### 生年月日", "name_placeholder": "名前", "mbti_mode": "MBTI", "direct": "直接入力", "test12": "簡単テスト(12)", "test16": "詳細テスト(16)", "test_start_12": "簡単テスト開始", "test_start_16": "詳細テスト開始", "result_btn": "結果", "fortune_btn": "運勢を見る", "reset": "最初から", "share_btn": "共有", "tarot_btn": "タロット", "tarot_title": "今日のタロット", "zodiac_title": "干支", "mbti_title": "MBTI", "saju_title": "一言", "today_title": "今日", "tomorrow_title": "明日", "overall_title": "2026 全体", "combo_title": "アドバイス", "lucky_color_title": "ラッキーカラー", "lucky_item_title": "ラッキーアイテム", "tip_title": "ヒント",
           "overall_fortunes": ["良い年です!"], "lucky_colors": ["Gold"], "lucky_items": ["Pen"], "tips": ["Smile"], "daily_msgs": ["Good day"], "tarot_cards": {"The Sun": "Joy"}},
    "zh": {"lang_label": "语言", "title": "2026 运势 + MBTI", "caption": "免费", "birth": "### 出生日期", "name_placeholder": "姓名", "mbti_mode": "MBTI", "direct": "直接输入", "test12": "简测(12)", "test16": "详测(16)", "test_start_12": "简测开始", "test_start_16": "详测开始", "result_btn": "结果", "fortune_btn": "查看运势", "reset": "重新开始", "share_btn": "分享", "tarot_btn": "塔罗", "tarot_title": "今日塔罗", "zodiac_title": "生肖", "mbti_title": "MBTI", "saju_title": "一句话", "today_title": "今天", "tomorrow_title": "明天", "overall_title": "2026 总体", "combo_title": "建议", "lucky_color_title": "幸运色", "lucky_item_title": "幸运物", "tip_title": "提示",
           "overall_fortunes": ["祝你好运!"], "lucky_colors": ["Gold"], "lucky_items": ["Pen"], "tips": ["Smile"], "daily_msgs": ["Good day"], "tarot_cards": {"The Sun": "Joy"}},
    "ru": {"lang_label": "Язык", "title": "2026 Удача + MBTI", "caption": "Бесплатно", "birth": "### Дата рождения", "name_placeholder": "Имя", "mbti_mode": "MBTI", "direct": "Ввести", "test12": "Тест 12", "test16": "Тест 16", "test_start_12": "Старт 12", "test_start_16": "Старт 16", "result_btn": "Результат", "fortune_btn": "Удача", "reset": "Сначала", "share_btn": "Поделиться", "tarot_btn": "Таро", "tarot_title": "Таро", "zodiac_title": "Знак", "mbti_title": "MBTI", "saju_title": "Комментарий", "today_title": "Сегодня", "tomorrow_title": "Завтра", "overall_title": "2026", "combo_title": "Совет", "lucky_color_title": "Цвет", "lucky_item_title": "Предмет", "tip_title": "Совет",
           "overall_fortunes": ["Удачи!"], "lucky_colors": ["Gold"], "lucky_items": ["Pen"], "tips": ["Smile"], "daily_msgs": ["Good day"], "tarot_cards": {"The Sun": "Joy"}},
}

LANGS = ["ko", "en", "ja", "zh", "ru"]


# =========================
# 2) MBTI / 띠 / 사주(간단)
# =========================
MBTI_LABELS = {
    "ko": {
        "INTJ": "냉철 전략가", "INTP": "아이디어 천재", "ENTJ": "리더형", "ENTP": "토론왕",
        "INFJ": "마음 마스터", "INFP": "감성 예술가", "ENFJ": "모두 선생님", "ENFP": "인간 비타민",
        "ISTJ": "규칙 지킴이", "ISFJ": "세상 따뜻함", "ESTJ": "현실 리더", "ESFJ": "분위기 메이커",
        "ISTP": "고치는 장인", "ISFP": "감성 힐러", "ESTP": "모험왕", "ESFP": "파티 주인공"
    },
    "en": {
        "INTJ": "Strategist", "INTP": "Thinker", "ENTJ": "Commander", "ENTP": "Debater",
        "INFJ": "Advocate", "INFP": "Mediator", "ENFJ": "Protagonist", "ENFP": "Campaigner",
        "ISTJ": "Logistician", "ISFJ": "Defender", "ESTJ": "Executive", "ESFJ": "Consul",
        "ISTP": "Virtuoso", "ISFP": "Adventurer", "ESTP": "Entrepreneur", "ESFP": "Entertainer"
    }
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

def get_zodiac(year: int, lang: str):
    z_list = ZODIAC_NAMES.get(lang, ZODIAC_NAMES["en"])
    if 1900 <= year <= 2030:
        return z_list[(year - 4) % 12]
    return None

def get_saju(year: int, month: int, day: int, lang: str):
    if lang != "ko":
        # 최소 기능 유지용
        return "A calm and balanced message."
    total = year + month + day
    return SAJU_MSG_KO[total % len(SAJU_MSG_KO)]

def deterministic_daily_msg(lang: str, zodiac_index: int, offset_days: int, msgs: list[str]):
    now = datetime.now() + timedelta(days=offset_days)
    seed = int(now.strftime("%Y%m%d")) + zodiac_index * 97 + 13
    random.seed(seed)
    return random.choice(msgs)

def sha_phone(phone: str) -> str:
    normalized = "".join([c for c in phone if c.isdigit()])
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


# =========================
# 3) 구글시트 연결
# =========================
def get_sheet():
    if not (USE_GOOGLE_SHEETS and SHEET_ID and SHEET_ID != "여기에_너의_구글시트_ID를_넣어줘"):
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
    # 시트 구조:
    # A: 이름, B: 전화(원문), C: 전화해시, D: 언어, E: 참여시간, F: 기록(초), G: 메모
    values = ws.get_all_values()
    if len(values) <= 1:
        return 0, set()
    rows = values[1:]
    hashed_set = set()
    for r in rows:
        if len(r) >= 3 and r[2]:
            hashed_set.add(r[2])
    return len(rows), hashed_set

def sheet_append_entry(ws, name, phone, lang, elapsed):
    phone_hash = sha_phone(phone)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ws.append_row([name, phone, phone_hash, lang, ts, f"{elapsed:.3f}", "coffee_coupon"])
    return phone_hash


# =========================
# 4) Streamlit 세션 초기화
# =========================
st.set_page_config(page_title="2026 Fortune", layout="centered")

if "lang" not in st.session_state:
    st.session_state.lang = "ko"
if "step" not in st.session_state:
    st.session_state.step = "input"   # input | result
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

# 공유 클릭 여부(추가기회용)
if "share_clicked" not in st.session_state:
    st.session_state.share_clicked = False

# 미니게임 상태
if "mg_attempts_used" not in st.session_state:
    st.session_state.mg_attempts_used = 0
if "mg_started_at" not in st.session_state:
    st.session_state.mg_started_at = None
if "mg_last_elapsed" not in st.session_state:
    st.session_state.mg_last_elapsed = None
if "mg_passed" not in st.session_state:
    st.session_state.mg_passed = False
if "mg_entry_done" not in st.session_state:
    st.session_state.mg_entry_done = False


# =========================
# 5) 공통 CSS (모바일 가독성 강화)
# =========================
st.markdown("""
<style>
    html, body, [class*="css"] {font-family: 'Noto Sans KR', sans-serif;}
    .app-wrap {max-width: 820px; margin: 0 auto;}
    .hero {text-align:center; padding: 16px 10px 6px;}
    .hero h1 {margin: 0; font-size: 1.75rem; line-height: 1.25;}
    .hero p {margin: 8px 0 0; color: #666; font-size: 0.95rem;}
    .card {
        background: #ffffff;
        border: 1px solid rgba(0,0,0,0.08);
        border-radius: 18px;
        padding: 16px 14px;
        margin: 12px 0;
        box-shadow: 0 8px 24px rgba(0,0,0,0.06);
    }
    .result-bg{
        background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 50%, #8ec5fc 100%);
        border-radius: 20px;
        padding: 14px;
        margin-top: 10px;
    }
    .title-white{
        color: #fff;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.25);
        text-align:center;
        margin: 6px 0 10px;
        font-size: 1.55rem;
        line-height: 1.25;
    }
    .sub-white{
        color: #fff;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.20);
        text-align:center;
        margin: 0 0 10px;
        font-size: 1.15rem;
    }
    .kpi {font-size: 1.02rem; line-height: 1.75; color: #111;}
    .kpi b {color: #111;}
    .ad-box{
        border: 2px solid rgba(230,126,34,0.65);
        border-radius: 18px;
        padding: 14px 12px;
        background: rgba(255,252,240,0.92);
        text-align:center;
        margin: 14px 0;
    }
    .ad-box h3{margin: 0 0 6px; color:#d35400; font-size: 1.05rem;}
    .ad-box p{margin: 0 0 10px; color:#333; font-size: 0.95rem; line-height:1.45;}
    .btn-like{
        display:inline-block;
        background:#e67e22;
        color:white;
        padding:10px 18px;
        border-radius:14px;
        text-decoration:none;
        font-weight:700;
    }
    .mini-grid{
        display:flex;
        gap:10px;
        flex-wrap:wrap;
        justify-content:center;
    }
    .pill{
        display:inline-block;
        padding:6px 10px;
        border-radius:999px;
        background: rgba(0,0,0,0.06);
        font-size:0.9rem;
        margin: 0 6px 6px 0;
    }
</style>
""", unsafe_allow_html=True)


# =========================
# 6) 언어 선택
# =========================
with st.container():
    st.markdown('<div class="app-wrap">', unsafe_allow_html=True)

lang = st.radio(
    translations[st.session_state.lang]["lang_label"],
    LANGS,
    index=LANGS.index(st.session_state.lang) if st.session_state.lang in LANGS else 0,
    horizontal=True
)
st.session_state.lang = lang
t = translations.get(lang, translations["en"])
mbti_dict = MBTI_LABELS["ko"] if lang == "ko" else MBTI_LABELS["en"]


# =========================
# 7) 입력 화면
# =========================
def go_result(mbti_code: str):
    st.session_state.mbti = mbti_code
    st.session_state.step = "result"
    st.rerun()

def reset_all():
    st.session_state.clear()
    st.rerun()

if st.session_state.step == "input":
    st.markdown(f"""
    <div class="hero">
        <h1>{t['title']}</h1>
        <p>{t['caption']}</p>
    </div>
    """, unsafe_allow_html=True)

    # (한국어만) 광고 박스 + 테두리
    if lang == "ko":
        st.markdown(f"""
        <div class="ad-box">
            <h3>{t['ad_title']}</h3>
            <p>{t['ad_body']}</p>
            <a class="btn-like" href="https://www.다나눔렌탈.com" target="_blank">{t['ad_btn']}</a>
        </div>
        """, unsafe_allow_html=True)

    st.session_state.name = st.text_input(t["name_placeholder"], value=st.session_state.name)

    st.markdown(f"<div class='card'>{t['birth']}</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    st.session_state.year = c1.number_input("Year" if lang != "ko" else "년", 1900, 2030, st.session_state.year, 1)
    st.session_state.month = c2.number_input("Month" if lang != "ko" else "월", 1, 12, st.session_state.month, 1)
    st.session_state.day = c3.number_input("Day" if lang != "ko" else "일", 1, 31, st.session_state.day, 1)

    choice = st.radio(t["mbti_mode"], [t["direct"], t["test12"], t["test16"]])

    if choice == t["direct"]:
        mbti_input = st.selectbox("MBTI", sorted(mbti_dict.keys()))
        if st.button(t["fortune_btn"], use_container_width=True):
            go_result(mbti_input)

    elif choice == t["test12"]:
        st.markdown(f"<div class='card'><b>{t['test_start_12']}</b></div>", unsafe_allow_html=True)

        # 12문항: EI/SN/TF/JP 각각 3문항씩
        ei = sn = tf = jp = 0

        st.subheader(t["energy"])
        for i in range(3):
            ans = st.radio(t["q12_ei"][i], [t["a12_e"][i], t["a12_i"][i]], key=f"t12_ei_{i}")
            if ans == t["a12_e"][i]:
                ei += 1

        st.subheader(t["info"])
        for i in range(3):
            ans = st.radio(t["q12_sn"][i], [t["a12_s"][i], t["a12_n"][i]], key=f"t12_sn_{i}")
            if ans == t["a12_s"][i]:
                sn += 1

        st.subheader(t["decision"])
        for i in range(3):
            ans = st.radio(t["q12_tf"][i], [t["a12_t"][i], t["a12_f"][i]], key=f"t12_tf_{i}")
            if ans == t["a12_t"][i]:
                tf += 1

        st.subheader(t["life"])
        for i in range(3):
            ans = st.radio(t["q12_jp"][i], [t["a12_j"][i], t["a12_p"][i]], key=f"t12_jp_{i}")
            if ans == t["a12_j"][i]:
                jp += 1

        if st.button(t["result_btn"], use_container_width=True):
            mbti_code = ("E" if ei >= 2 else "I") + ("S" if sn >= 2 else "N") + ("T" if tf >= 2 else "F") + ("J" if jp >= 2 else "P")
            go_result(mbti_code)

    else:
        st.markdown(f"<div class='card'><b>{t['test_start_16']}</b></div>", unsafe_allow_html=True)

        e_i = s_n = t_f = j_p = 0

        st.subheader(t["energy"])
        for i in range(4):
            ans = st.radio(t["q_energy"][i], [t["options_e"][i], t["options_i"][i]], key=f"t16_ei_{i}")
            if ans == t["options_e"][i]:
                e_i += 1

        st.subheader(t["info"])
        for i in range(4):
            ans = st.radio(t["q_info"][i], [t["options_s"][i], t["options_n"][i]], key=f"t16_sn_{i}")
            if ans == t["options_s"][i]:
                s_n += 1

        st.subheader(t["decision"])
        for i in range(4):
            ans = st.radio(t["q_decision"][i], [t["options_t"][i], t["options_f"][i]], key=f"t16_tf_{i}")
            if ans == t["options_t"][i]:
                t_f += 1

        st.subheader(t["life"])
        for i in range(4):
            ans = st.radio(t["q_life"][i], [t["options_j"][i], t["options_p"][i]], key=f"t16_jp_{i}")
            if ans == t["options_j"][i]:
                j_p += 1

        if st.button(t["result_btn"], use_container_width=True):
            mbti_code = ("E" if e_i >= 3 else "I") + ("S" if s_n >= 3 else "N") + ("T" if t_f >= 3 else "F") + ("J" if j_p >= 3 else "P")
            go_result(mbti_code)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    if st.button(t["reset"], use_container_width=True):
        reset_all()


# =========================
# 8) 결과 화면
# =========================
if st.session_state.step == "result":
    mbti = st.session_state.mbti
    zodiac = get_zodiac(st.session_state.year, lang)
    if zodiac is None:
        st.error("Please enter a birth year between 1900 and 2030!" if lang != "ko" else "생년은 1900~2030년 사이로 입력해주세요!")
        if st.button(t["reset"], use_container_width=True):
            reset_all()
        st.stop()

    # MBTI 표시 텍스트
    mbti_desc = (MBTI_LABELS["ko"].get(mbti) if lang == "ko" else MBTI_LABELS["en"].get(mbti)) or mbti

    # 띠 설명(한국어만 풍부)
    if lang == "ko":
        zodiac_desc = ZODIAC_DESC_KO.get(zodiac, "")
        zodiac_display = zodiac
        zodiac_index = ZODIAC_NAMES["ko"].index(zodiac)
    else:
        zodiac_desc = zodiac
        zodiac_display = zodiac
        zodiac_index = ZODIAC_NAMES.get(lang, ZODIAC_NAMES["en"]).index(zodiac)

    saju = get_saju(st.session_state.year, st.session_state.month, st.session_state.day, lang)

    today_msg = deterministic_daily_msg(lang, zodiac_index, 0, t["daily_msgs"])
    tomorrow_msg = deterministic_daily_msg(lang, zodiac_index, 1, t["daily_msgs"])

    overall = random.choice(t["overall_fortunes"])
    lucky_color = random.choice(t["lucky_colors"])
    lucky_item = random.choice(t["lucky_items"])
    tip = random.choice(t["tips"])

    # 조합 조언(요청: MBTI가 운세에 미치는 영향 형태)
    if lang == "ko":
        combo_advice = (
            f"'{mbti}' 성향은 {('계획/통제' if 'J' in mbti else '유연/즉흥')}에 강점이 있어요. "
            f"올해 '{zodiac_display}' 흐름에서는 "
            f"{('루틴을 만들면 운이 폭발' if 'J' in mbti else '기회를 잡는 순발력이 복' )}합니다. "
            f"{('결정 전에 1번 더 검증' if 'T' in mbti else '감정 소진 방지선부터 확보')}이 핵심!"
        )
    else:
        combo_advice = (
            f"Your MBTI ({mbti}) affects your decision style. "
            f"Use your strength (planning vs flexibility) to ride this year's flow."
        )

    name_display = st.session_state.name.strip()
    if lang == "ko" and name_display:
        name_display = f"{name_display}님"

    st.markdown(f"""
    <div class="result-bg">
        <div class="title-white">{name_display + " " if name_display else ""}2026 {("운세" if lang=="ko" else "Fortune")}</div>
        <div class="sub-white">{zodiac_display} + {mbti}</div>
    </div>
    """, unsafe_allow_html=True)

    # 메인 카드
    st.markdown(f"""
    <div class="card kpi">
        <div class="pill"><b>{t['zodiac_title']}</b>: {zodiac_desc}</div>
        <div class="pill"><b>{t['mbti_title']}</b>: {mbti_desc}</div>
        <div class="pill"><b>{t['saju_title']}</b>: {saju}</div>
        <hr style="border:none;border-top:1px solid rgba(0,0,0,0.08); margin:10px 0;">
        <div><b>{t['today_title']}</b>: {today_msg}</div>
        <div><b>{t['tomorrow_title']}</b>: {tomorrow_msg}</div>
        <hr style="border:none;border-top:1px solid rgba(0,0,0,0.08); margin:10px 0;">
        <div><b>{t['overall_title']}</b>: {overall}</div>
        <div><b>{t['combo_title']}</b>: {combo_advice}</div>
        <div><b>{t['lucky_color_title']}</b>: {lucky_color}  |  <b>{t['lucky_item_title']}</b>: {lucky_item}</div>
        <div><b>{t['tip_title']}</b>: {tip}</div>
    </div>
    """, unsafe_allow_html=True)

    # =========================
    # 8-1) 공유 버튼 (모바일: 공유 시트, PC: 복사)
    # =========================
    share_text = (
        f"{(name_display + ' ' if name_display else '')}2026 운세\n\n"
        f"{zodiac_display} + {mbti}\n\n"
        f"{t['today_title']}: {today_msg}\n"
        f"{t['tomorrow_title']}: {tomorrow_msg}\n\n"
        f"{t['overall_title']}: {overall}\n"
        f"{t['combo_title']}: {combo_advice}\n"
        f"{t['lucky_color_title']}: {lucky_color} / {t['lucky_item_title']}: {lucky_item}\n"
        f"{t['tip_title']}: {tip}\n\n"
        f"{APP_URL}"
    )

    # 버튼 UI(스트림릿 버튼 + JS)
    # - 클릭 시: navigator.share 지원이면 공유 시트 호출
    # - 아니면 클립보드 복사
    # - 추가기회: 클릭만 해도 1회 추가(요청대로 "공유 버튼 누르면" 기준)
    st.markdown(f"""
    <div class="card" style="text-align:center;">
        <button id="shareBtn"
            style="background:#ffffff; color:#8e44ad; padding:14px 22px; border:none; border-radius:999px;
                   font-size:1.05rem; font-weight:800; box-shadow: 0 8px 22px rgba(142,68,173,0.18);
                   width:100%; max-width:520px; cursor:pointer;">
            {t["share_btn"]}
        </button>
        <div style="margin-top:10px; font-size:0.92rem; color:#666;">
            {("공유를 누르면 미니게임 기회가 1회 늘어나요!" if lang=="ko" else "Sharing gives +1 extra attempt for the mini game.")}
        </div>
    </div>

    <script>
    const shareText = {repr(share_text)};
    const shareBtn = document.getElementById("shareBtn");

    function notifyStreamlitShareClicked(){{
        const ev = new CustomEvent("share-clicked");
        window.dispatchEvent(ev);
    }}

    shareBtn.addEventListener("click", async () => {{
        try {{
            if (navigator.share) {{
                await navigator.share({{ text: shareText, title: "2026 Fortune", url: "{APP_URL}" }});
            }} else {{
                await navigator.clipboard.writeText(shareText);
                alert("{'결과가 복사됐어요! 카톡/메시지에 붙여넣기 해주세요.' if lang=='ko' else 'Copied! Paste it anywhere.'}");
            }}
        }} catch (e) {{
            // 사용자가 공유 취소해도 기회는 준다(요청 기준)
        }}
        notifyStreamlitShareClicked();
    }});
    </script>
    """, unsafe_allow_html=True)

    # JS 이벤트를 Streamlit로 받기 위한 간단 트릭:
    # streamlit은 window event 직접 수신이 어려워서, share_clicked는 "다음 rerun 시"에 반영되게 버튼도 하나 둠.
    # (모바일 공유 후 돌아오면 rerun이 자주 발생함. 혹시 안 되면 아래 숨은 버튼을 한 번 누르게 안내)
    # 실사용에서 무반응 방지: '공유 완료 체크' 버튼 제공(겉으로는 작게)
    cA, cB = st.columns([3, 1])
    with cB:
        if st.button("✓", help="공유를 눌렀다면 한번만 눌러주세요 (추가기회 체크)", use_container_width=True):
            st.session_state.share_clicked = True
            st.toast("추가기회 +1 적용!", icon="🎁")

    # =========================
    # 8-2) 타로(정상 작동 유지)
    # =========================
    if st.button(t["tarot_btn"], use_container_width=True):
        tarot_card = random.choice(list(t["tarot_cards"].keys()))
        tarot_meaning = t["tarot_cards"][tarot_card]
        st.markdown(f"""
        <div class="card" style="text-align:center;">
            <h3 style="margin:0; color:#9b59b6;">{t['tarot_title']}</h3>
            <h2 style="margin:8px 0 4px; color:#333;">{tarot_card}</h2>
            <p style="margin:0; font-size:1.05rem; line-height:1.6; color:#111;">{tarot_meaning}</p>
        </div>
        """, unsafe_allow_html=True)

    # =========================
    # 8-3) (한국어만) 미니게임 + 선착순20 + 중복방지 + 개인정보 동의 + 시트저장
    # =========================
    if EVENT_ENABLED and lang == EVENT_LANGUAGE_ONLY:
        st.markdown(f"""
        <div class="card">
            <h3 style="margin:0 0 6px;">{t["event_title"]}</h3>
            <div style="color:#444; font-size:0.95rem; line-height:1.5;">
                {t["event_desc"]}<br>
                <span style="color:#666;">목표: <b>{TARGET_SECONDS:.2f}s</b> / 허용오차: <b>±{PASS_TOLERANCE:.2f}s</b></span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        ws = get_sheet()
        if ws is None:
            st.warning("구글시트 연결이 아직 안 되어 있어요. (SHEET_ID/Secrets/requirements 확인 필요)")
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

                st.markdown(f"<div class='card'><b>{t['event_attempts_left']}</b>: {attempts_left} / {total_attempts}</div>", unsafe_allow_html=True)

                if not st.session_state.share_clicked:
                    st.caption(t["event_need_share"])

                # 미니게임 UI
                mg_box = st.container()
                with mg_box:
                    cols = st.columns(2)
                    with cols[0]:
                        start_clicked = st.button(t["event_start"], use_container_width=True, disabled=(attempts_left <= 0 or st.session_state.mg_started_at is not None))
                    with cols[1]:
                        stop_clicked = st.button(t["event_stop"], use_container_width=True, disabled=(st.session_state.mg_started_at is None or attempts_left <= 0))

                    if start_clicked:
                        st.session_state.mg_started_at = time.time()
                        st.session_state.mg_last_elapsed = None
                        st.session_state.mg_passed = False
                        st.rerun()

                    if stop_clicked and st.session_state.mg_started_at is not None:
                        elapsed = time.time() - st.session_state.mg_started_at
                        st.session_state.mg_started_at = None
                        st.session_state.mg_last_elapsed = elapsed
                        st.session_state.mg_attempts_used += 1

                        if abs(elapsed - TARGET_SECONDS) <= PASS_TOLERANCE:
                            st.session_state.mg_passed = True
                        else:
                            st.session_state.mg_passed = False
                        st.rerun()

                    if st.session_state.mg_last_elapsed is not None:
                        st.markdown(
                            f"<div class='card'><b>{t['event_elapsed']}</b>: {st.session_state.mg_last_elapsed:.3f}s</div>",
                            unsafe_allow_html=True
                        )
                        if st.session_state.mg_passed:
                            st.success(t["event_success"])
                        else:
                            st.error(t["event_fail"])

                # 통과 시 응모 폼
                if st.session_state.mg_passed and not st.session_state.mg_entry_done:
                    st.markdown(f"<div class='card'><h3 style='margin:0 0 8px;'>{t['event_form_title']}</h3></div>", unsafe_allow_html=True)

                    # 개인정보 동의 문구 (필수 고지 항목 포함)
                    consent_text = f"""
- **수집 항목**: 이름, 휴대폰번호  
- **이용 목적**: 커피쿠폰 당첨자 확인 및 쿠폰 발송, 문의 응대  
- **보유·이용 기간**: 응모일로부터 {DATA_RETENTION_DAYS}일 또는 경품 발송/문의 응대 완료 시까지(먼저 도래하는 시점)  
- **동의 거부 권리**: 동의를 거부할 수 있으며, 거부 시 쿠폰 응모는 제한됩니다. (운세 서비스 이용은 가능)  
- **처리/보관 방식**: 구글 스프레드시트에 저장되며, 목적 달성 후 지체 없이 파기합니다.  
                    """.strip()

                    st.markdown(f"<div class='card'><b>{t['consent_title']}</b><br><br>{consent_text}</div>", unsafe_allow_html=True)

                    consent_ok = st.checkbox(t["consent_check"], value=False)
                    st.caption(t["consent_more"])

                    entry_name = st.text_input(t["name_label"], value=st.session_state.name.strip())
                    entry_phone = st.text_input(t["phone_label"], placeholder=t["phone_hint"])

                    if st.button(t["submit_entry"], use_container_width=True, disabled=not consent_ok):
                        # 입력 검증
                        phone_digits = "".join([c for c in entry_phone if c.isdigit()])
                        if len(phone_digits) < 10 or len(phone_digits) > 11:
                            st.error("전화번호를 정확히 입력해주세요. (숫자만 10~11자리)")
                        elif not entry_name.strip():
                            st.error("이름을 입력해주세요.")
                        else:
                            try:
                                # 최신 상태 재조회(동시성 대비)
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

    # 하단 URL + 리셋
    st.markdown(f"<div style='text-align:center; margin-top:8px; color:#666; font-size:0.9rem;'>{APP_URL}</div>", unsafe_allow_html=True)

    if st.button(t["reset"], use_container_width=True):
        reset_all()

    st.markdown("</div>", unsafe_allow_html=True)
