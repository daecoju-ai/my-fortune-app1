import streamlit as st
from datetime import datetime, timedelta
import random
import time
import re
import hashlib

# ============================================================
# ✅ Google Sheet 설정 (사용자 제공 ID 자동 적용)
# ============================================================
SHEET_ID = "1WvuKXx2if2WvxmQaxkqzFW-BzDEWWma9hZgCr2jJQYY"
SHEET_TAB = "시트1"  # ✅ 사용자 확인: 탭 이름 "시트1"

WINNER_LIMIT = 20
TARGET_MIN = 20.160
TARGET_MAX = 20.169  # ✅ 허용오차(포함)

APP_URL = "https://my-fortune.streamlit.app"


def _normalize_phone(phone: str) -> str:
    """전화번호 숫자만 남기고 정규화"""
    digits = re.sub(r"[^0-9]", "", phone or "")
    # 국내 010xxxxxxxx 기준: 최소 10자리
    return digits


def _hash_phone(phone_digits: str) -> str:
    return hashlib.sha256(phone_digits.encode("utf-8")).hexdigest()[:16]


def get_gsheet_client():
    """Secrets에 [gcp_service_account]가 있으면 gspread 클라이언트 생성"""
    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except Exception:
        return None, "requirements.txt에 gspread/google-auth가 필요해요."

    try:
        if "gcp_service_account" not in st.secrets:
            return None, "Secrets에 [gcp_service_account]가 없어요."

        info = dict(st.secrets["gcp_service_account"])

        # ✅ Streamlit TOML에서 private_key가 "\\n"로 들어간 경우 방어
        if "private_key" in info and "\\n" in info["private_key"]:
            info["private_key"] = info["private_key"].replace("\\n", "\n")

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_info(info, scopes=scopes)
        gc = gspread.authorize(creds)
        return gc, None
    except Exception as e:
        return None, f"서비스계정/Secrets 형식 문제일 수 있어요: {e}"


def gsheet_open():
    gc, err = get_gsheet_client()
    if gc is None:
        return None, None, err

    try:
        sh = gc.open_by_key(SHEET_ID)
        ws = sh.worksheet(SHEET_TAB)  # ✅ "시트1" 탭
        return sh, ws, None
    except Exception as e:
        return None, None, f"시트 열기/탭 찾기 오류: {e}"


def gsheet_ensure_header(ws):
    """헤더가 없으면 생성"""
    header = [
        "timestamp",
        "lang",
        "name",
        "phone_digits",
        "phone_hash",
        "mbti",
        "zodiac",
        "elapsed_sec",
        "status",
    ]
    values = ws.get_all_values()
    if not values:
        ws.append_row(header)
        return
    if values[0] != header:
        # 기존 데이터가 있어도 헤더가 다르면 맨 위에 덮어쓰진 않고 안내용으로만 유지
        # (실수로 기존 데이터 깨지는 걸 방지)
        return


def gsheet_get_stats(ws):
    """
    status==WIN 개수(선착순) / phone_hash 중복 여부 체크용 집합
    """
    try:
        values = ws.get_all_values()
        if not values or len(values) < 2:
            return 0, set()

        header = values[0]
        rows = values[1:]

        # 헤더 인덱스 방어
        try:
            idx_status = header.index("status")
            idx_hash = header.index("phone_hash")
        except ValueError:
            # 헤더가 다른 경우: 안전하게 전체 스캔
            idx_status, idx_hash = None, None

        win_count = 0
        phone_hashes = set()

        for r in rows:
            if idx_hash is not None and idx_hash < len(r):
                if r[idx_hash]:
                    phone_hashes.add(r[idx_hash].strip())
            if idx_status is not None and idx_status < len(r):
                if (r[idx_status] or "").strip().upper() == "WIN":
                    win_count += 1

        return win_count, phone_hashes
    except Exception:
        return 0, set()


def gsheet_append_entry(ws, lang, name, phone_digits, mbti, zodiac, elapsed, status):
    phone_hash = _hash_phone(phone_digits)
    ws.append_row(
        [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            lang,
            name,
            phone_digits,
            phone_hash,
            mbti,
            zodiac,
            f"{elapsed:.3f}",
            status,
        ]
    )


# ============================================================
# ✅ 다국어(i18n): 6개 언어
# ============================================================
LANG_OPTIONS = [
    ("ko", "한국어"),
    ("en", "English"),
    ("ja", "日本語"),
    ("zh", "中文"),
    ("ru", "Русский"),
    ("hi", "हिन्दी"),
]
LANG_KEYS = [k for k, _ in LANG_OPTIONS]
LANG_LABELS = {k: v for k, v in LANG_OPTIONS}

translations = {
    "ko": {
        "title": "2026 띠 + MBTI + 사주 + 오늘/내일 운세",
        "caption": "완전 무료",
        "lang_label": "언어 선택",
        "name_placeholder": "이름 입력 (결과에 표시돼요)",
        "birth": "### 생년월일 입력",
        "mbti_mode": "MBTI 어떻게 할까?",
        "direct": "직접 입력",
        "test12": "간단 테스트 (12문항)",
        "test16": "상세 테스트 (16문항)",
        "fortune_btn": "2026년 운세 보기!",
        "result_btn": "결과 보기!",
        "reset": "처음부터 다시하기",
        "share_btn": "친구에게 결과 공유하기",
        "tarot_btn": "오늘의 타로 카드 뽑기",
        "tarot_title": "오늘의 타로 카드",
        "zodiac_title": "띠 운세",
        "mbti_title": "MBTI 특징",
        "saju_title": "사주 한 마디",
        "today_title": "오늘 운세",
        "tomorrow_title": "내일 운세",
        "overall_title": "2026 전체 운세",
        "combo_title": "MBTI가 운세에 미치는 조언",
        "lucky_color_title": "럭키 컬러",
        "lucky_item_title": "럭키 아이템",
        "tip_title": "팁",
        "warning_sheet": "구글시트 연결이 아직 안 되어 있어요. (Secrets/requirements/시트 공유/탭 이름 확인 필요)",
        "share_hint": "모바일에서는 공유창이 뜨고, PC에서는 자동으로 복사돼요.",
        "copy_done": "공유용 텍스트를 복사했어요! 카톡/메시지에 붙여넣기 해주세요.",
        "need_year": "생년은 1900~2030년 사이로 입력해주세요!",
        "ad_title": "정수기 렌탈 대박!",
        "ad_desc1": "제휴카드면 월 0원부터!",
        "ad_desc2": "설치 당일 최대 50만원 지원 + 사은품 듬뿍 ✨",
        "ad_link": "다나눔렌탈.com 바로가기",
        "ad_url": "https://www.다나눔렌탈.com",
        "test16_desc": "각 축 4문항씩. 제출하면 결과로 넘어갑니다.",
        "test12_desc": "제출하면 바로 결과로 넘어갑니다.",
        "minigame_title": "🎁 미니게임: 선착순 20명 커피쿠폰 도전!",
        "minigame_desc": "스톱워치를 멈춘 시간이 **20.160~20.169초**면 당첨!",
        "minigame_share_bonus": "친구에게 결과를 공유하면 **미니게임 1회 추가** (아래 버튼으로 추가 기회 받기)",
        "minigame_bonus_btn": "공유했어요! 1회 추가 받기",
        "minigame_attempts": "남은 기회",
        "minigame_start": "시작",
        "minigame_stop": "정지",
        "minigame_running": "진행 중… STOP을 눌러 멈추세요!",
        "minigame_not_ready": "구글시트 연결이 안 되어 있어 미니게임 당첨 저장이 불가합니다.",
        "minigame_closed": "선착순 20명이 마감되었습니다. 다음 이벤트를 기다려주세요!",
        "minigame_win": "🎉 축하합니다! 당첨 범위에 들어왔어요.",
        "minigame_lose": "아쉽지만 실패! 다시 도전해보세요.",
        "minigame_need_consent": "개인정보 동의에 체크해야 제출할 수 있어요.",
        "minigame_form_title": "🎉 당첨자 정보 입력",
        "consent_text": "개인정보 수집·이용 동의(필수): 이벤트 경품 발송을 위해 이름/전화번호를 수집하며, 목적 달성 후 보관기간(예: 3개월) 경과 시 파기됩니다. 동의하지 않을 권리가 있으나, 미동의 시 참여가 제한됩니다.",
        "submit": "제출하기",
        "duplicate": "이미 같은 전화번호로 참여/당첨 이력이 있어요. 중복 참여는 제한됩니다.",
        "saved": "저장 완료! 담당자가 확인 후 안내드릴게요.",
    },
    "en": {
        "title": "2026 Zodiac + MBTI + Fortune + Today/Tomorrow",
        "caption": "Completely Free",
        "lang_label": "Language",
        "name_placeholder": "Enter name (shown in result)",
        "birth": "### Enter Birth Date",
        "mbti_mode": "How to do MBTI?",
        "direct": "Direct input",
        "test12": "Quick test (12)",
        "test16": "Detailed test (16)",
        "fortune_btn": "View 2026 Fortune!",
        "result_btn": "View Result!",
        "reset": "Start Over",
        "share_btn": "Share with Friends",
        "tarot_btn": "Draw Today's Tarot Card",
        "tarot_title": "Today's Tarot Card",
        "zodiac_title": "Zodiac Fortune",
        "mbti_title": "MBTI Traits",
        "saju_title": "Fortune Comment",
        "today_title": "Today's Luck",
        "tomorrow_title": "Tomorrow's Luck",
        "overall_title": "2026 Annual Luck",
        "combo_title": "How MBTI affects your luck",
        "lucky_color_title": "Lucky Color",
        "lucky_item_title": "Lucky Item",
        "tip_title": "Tip",
        "warning_sheet": "Google Sheet is not connected yet. (Check Secrets/requirements/share/tab name)",
        "share_hint": "On mobile, share sheet opens. On PC, it auto-copies.",
        "copy_done": "Copied! Paste it into KakaoTalk / Messages.",
        "need_year": "Please enter a birth year between 1900 and 2030!",
        "ad_title": "Water Purifier Rental Deal!",
        "ad_desc1": "From 0 won/month with partner card!",
        "ad_desc2": "Up to 500,000 won support + gifts",
        "ad_link": "Go to DananumRental.com",
        "ad_url": "https://www.다나눔렌탈.com",
        "test16_desc": "4 questions per axis. Submit to see result.",
        "test12_desc": "Submit to see result instantly.",
    },
    "ja": {
        "title": "2026 干支 + MBTI + 運勢（今日/明日）",
        "caption": "完全無料",
        "lang_label": "言語",
        "name_placeholder": "名前（結果に表示）",
        "birth": "### 生年月日",
        "mbti_mode": "MBTIはどうする？",
        "direct": "直接選択",
        "test12": "簡単テスト（12問）",
        "test16": "詳細テスト（16問）",
        "fortune_btn": "2026年の運勢を見る！",
        "result_btn": "結果を見る",
        "reset": "最初からやり直す",
        "share_btn": "友だちに共有",
        "tarot_btn": "今日のタロットを引く",
        "tarot_title": "今日のタロット",
        "zodiac_title": "干支の運勢",
        "mbti_title": "MBTIの特徴",
        "saju_title": "ひとこと運勢",
        "today_title": "今日の運勢",
        "tomorrow_title": "明日の運勢",
        "overall_title": "2026 年間運勢",
        "combo_title": "MBTIによるアドバイス",
        "lucky_color_title": "ラッキーカラー",
        "lucky_item_title": "ラッキーアイテム",
        "tip_title": "ヒント",
        "warning_sheet": "Google Sheet が未接続です。（Secrets/requirements/共有/タブ名）",
        "share_hint": "モバイルは共有画面、PCはコピーされます。",
        "copy_done": "コピーしました。貼り付けて共有してください。",
        "need_year": "生年は 1900〜2030 の範囲で入力してください。",
        "test16_desc": "各軸4問。送信で結果へ。",
        "test12_desc": "送信で結果へ。",
    },
    "zh": {
        "title": "2026 生肖 + MBTI + 运势（今日/明日）",
        "caption": "完全免费",
        "lang_label": "语言",
        "name_placeholder": "输入姓名（显示在结果中）",
        "birth": "### 输入生日",
        "mbti_mode": "MBTI 怎么做？",
        "direct": "直接选择",
        "test12": "快速测试（12题）",
        "test16": "详细测试（16题）",
        "fortune_btn": "查看 2026 运势！",
        "result_btn": "查看结果",
        "reset": "重新开始",
        "share_btn": "分享给朋友",
        "tarot_btn": "抽今日塔罗",
        "tarot_title": "今日塔罗",
        "zodiac_title": "生肖运势",
        "mbti_title": "MBTI 特点",
        "saju_title": "一句运势",
        "today_title": "今日运势",
        "tomorrow_title": "明日运势",
        "overall_title": "2026 年整体运势",
        "combo_title": "MBTI 对运势的建议",
        "lucky_color_title": "幸运色",
        "lucky_item_title": "幸运物",
        "tip_title": "提示",
        "warning_sheet": "Google Sheet 未连接。（检查 Secrets/requirements/共享/表名）",
        "share_hint": "手机会弹出分享面板，电脑会复制文本。",
        "copy_done": "已复制，请粘贴分享。",
        "need_year": "出生年份请填写 1900〜2030。",
        "test16_desc": "每个维度4题，提交后出结果。",
        "test12_desc": "提交后立即出结果。",
    },
    "ru": {
        "title": "2026 Зодиак + MBTI + Удача (сегодня/завтра)",
        "caption": "Полностью бесплатно",
        "lang_label": "Язык",
        "name_placeholder": "Введите имя (показывается в результате)",
        "birth": "### Дата рождения",
        "mbti_mode": "Как определить MBTI?",
        "direct": "Выбрать вручную",
        "test12": "Быстрый тест (12)",
        "test16": "Подробный тест (16)",
        "fortune_btn": "Показать удачу 2026!",
        "result_btn": "Показать результат",
        "reset": "Начать заново",
        "share_btn": "Поделиться",
        "tarot_btn": "Таро на сегодня",
        "tarot_title": "Таро на сегодня",
        "zodiac_title": "Удача по зодиаку",
        "mbti_title": "Черты MBTI",
        "saju_title": "Короткий прогноз",
        "today_title": "Сегодня",
        "tomorrow_title": "Завтра",
        "overall_title": "Итог 2026",
        "combo_title": "Совет с учетом MBTI",
        "lucky_color_title": "Счастливый цвет",
        "lucky_item_title": "Счастливый предмет",
        "tip_title": "Совет",
        "warning_sheet": "Google Sheet не подключён. (Secrets/requirements/доступ/вкладка)",
        "share_hint": "На телефоне откроется меню «Поделиться», на ПК текст копируется.",
        "copy_done": "Скопировано! Вставьте в мессенджер.",
        "need_year": "Введите год рождения 1900–2030.",
        "test16_desc": "4 вопроса на ось, затем результат.",
        "test12_desc": "Отправьте и получите результат.",
    },
    "hi": {
        "title": "2026 राशि + MBTI + भाग्य (आज/कल)",
        "caption": "पूरी तरह मुफ्त",
        "lang_label": "भाषा",
        "name_placeholder": "नाम लिखें (परिणाम में दिखेगा)",
        "birth": "### जन्मतिथि",
        "mbti_mode": "MBTI कैसे करें?",
        "direct": "सीधे चुनें",
        "test12": "त्वरित टेस्ट (12)",
        "test16": "विस्तृत टेस्ट (16)",
        "fortune_btn": "2026 भाग्य देखें!",
        "result_btn": "परिणाम देखें",
        "reset": "फिर से शुरू करें",
        "share_btn": "दोस्तों के साथ साझा करें",
        "tarot_btn": "आज का टैरो",
        "tarot_title": "आज का टैरो",
        "zodiac_title": "राशि/भाग्य",
        "mbti_title": "MBTI विशेषताएँ",
        "saju_title": "एक लाइन सलाह",
        "today_title": "आज",
        "tomorrow_title": "कल",
        "overall_title": "2026 वार्षिक भाग्य",
        "combo_title": "MBTI के अनुसार सलाह",
        "lucky_color_title": "लकी रंग",
        "lucky_item_title": "लकी आइटम",
        "tip_title": "टिप",
        "warning_sheet": "Google Sheet कनेक्ट नहीं है। (Secrets/requirements/शेयर/टैब)",
        "share_hint": "मोबाइल पर शेयर शीट खुलेगी, PC पर कॉपी होगा।",
        "copy_done": "कॉपी हो गया! मैसेज में पेस्ट करें।",
        "need_year": "जन्म-वर्ष 1900–2030 के बीच डालें।",
        "test16_desc": "प्रति आयाम 4 प्रश्न, सबमिट करें।",
        "test12_desc": "सबमिट करें और परिणाम पाएं।",
    }
}

# ============================================================
# ✅ 콘텐츠 DB (간단 번역 포함)
#   - 상세한 문구는 점진 확장 가능
# ============================================================
MBTI_KEYS = [
    "ISTJ","ISFJ","INFJ","INTJ","ISTP","ISFP","INFP","INTP",
    "ESTP","ESFP","ENFP","ENTP","ESTJ","ESFJ","ENFJ","ENTJ"
]

MBTI_TRAITS = {
    "ko": {
        "ISTJ":"규칙 지킴이 · 성실/책임", "ISFJ":"수호자 · 배려/헌신", "INFJ":"옹호자 · 통찰/이상", "INTJ":"전략가 · 계획/전략",
        "ISTP":"장인 · 실용/즉흥", "ISFP":"모험가 · 감각/유연", "INFP":"중재자 · 가치/상상", "INTP":"사색가 · 분석/호기심",
        "ESTP":"사업가 · 실행/도전", "ESFP":"연예인 · 에너지/관계", "ENFP":"활동가 · 영감/확장", "ENTP":"변론가 · 아이디어/변주",
        "ESTJ":"경영자 · 현실/성과", "ESFJ":"집정관 · 조화/관리", "ENFJ":"선도자 · 리드/공감", "ENTJ":"통솔자 · 결단/리더십",
    },
    "en": {
        "ISTJ":"Logistician · Duty/Order", "ISFJ":"Defender · Caring/Loyal", "INFJ":"Advocate · Insight/Vision", "INTJ":"Strategist · Planning",
        "ISTP":"Virtuoso · Practical", "ISFP":"Adventurer · Flexible", "INFP":"Mediator · Values", "INTP":"Thinker · Analysis",
        "ESTP":"Entrepreneur · Action", "ESFP":"Entertainer · Social", "ENFP":"Campaigner · Inspiration", "ENTP":"Debater · Ideas",
        "ESTJ":"Executive · Results", "ESFJ":"Consul · Harmony", "ENFJ":"Protagonist · Empathy", "ENTJ":"Commander · Leadership",
    },
    "ja": {k: f"{k}" for k in MBTI_KEYS},
    "zh": {k: f"{k}" for k in MBTI_KEYS},
    "ru": {k: f"{k}" for k in MBTI_KEYS},
    "hi": {k: f"{k}" for k in MBTI_KEYS},
}

# 12띠 (ko/en + 나머지는 표기만이라도)
ZODIAC_KO = ["쥐띠","소띠","호랑이띠","토끼띠","용띠","뱀띠","말띠","양띠","원숭이띠","닭띠","개띠","돼지띠"]
ZODIAC_EN = ["Rat","Ox","Tiger","Rabbit","Dragon","Snake","Horse","Goat","Monkey","Rooster","Dog","Pig"]
ZODIAC_JA = ["鼠","牛","虎","兎","龍","蛇","馬","羊","猿","鶏","犬","猪"]
ZODIAC_ZH = ["鼠","牛","虎","兔","龙","蛇","马","羊","猴","鸡","狗","猪"]
ZODIAC_RU = ["Крыса","Бык","Тигр","Кролик","Дракон","Змея","Лошадь","Коза","Обезьяна","Петух","Собака","Свинья"]
ZODIAC_HI = ["चूहा","बैल","बाघ","खरगोश","ड्रैगन","साँप","घोड़ा","बकरी","बंदर","मुर्गा","कुत्ता","सूअर"]

ZODIAC_LIST = {
    "ko": ZODIAC_KO,
    "en": ZODIAC_EN,
    "ja": ZODIAC_JA,
    "zh": ZODIAC_ZH,
    "ru": ZODIAC_RU,
    "hi": ZODIAC_HI,
}

ZODIAC_TEXT = {
    "ko": {
        "쥐띠":"안정 속 새로운 기회! 민첩한 판단으로 성공",
        "소띠":"꾸준함의 결실! 안정된 성장과 가족운",
        "호랑이띠":"도전과 성공! 리더십으로 큰 성과",
        "토끼띠":"변화에 신중! 흐름을 읽는 게 이득",
        "용띠":"운기 상승! 승진/인정 기회 많음",
        "뱀띠":"직감과 실속! 예상치 못한 재물운",
        "말띠":"추진력 강하지만 균형이 핵심",
        "양띠":"편안함과 돈운 상승, 가정운도 좋아요",
        "원숭이띠":"창의력으로 기회 잡기",
        "닭띠":"노력 결실! 인정/승진 가능성",
        "개띠":"귀인 도움과 네트워킹 운",
        "돼지띠":"여유와 재물운! 관리가 관건",
    },
    # 다른 언어는 간단 번역(짧게)
    "en": {k: "A positive flow—stay steady and seize chances." for k in ZODIAC_EN},
    "ja": {k: "安定しつつチャンスを掴もう。" for k in ZODIAC_JA},
    "zh": {k: "稳中求进，把握机会。" for k in ZODIAC_ZH},
    "ru": {k: "Стабильность + шанс: действуйте разумно." for k in ZODIAC_RU},
    "hi": {k: "स्थिर रहें और अवसर पकड़ें।" for k in ZODIAC_HI},
}

SAJU_MSGS = {
    "ko": [
        "오행 균형 → 무리하지 않으면 전반적으로 대길!",
        "목(木) 기운 → 성장과 발전의 해!",
        "화(火) 기운 → 열정이 성과로 연결!",
        "토(土) 기운 → 안정과 재물운 강화",
        "금(金) 기운 → 결단력과 선택이 빛남",
        "수(水) 기운 → 지혜롭게 흐름을 타기",
    ],
    "en": [
        "Balanced elements → Great year if you don’t overdo it!",
        "Wood → Growth and progress!",
        "Fire → Passion turns into results!",
        "Earth → Stability and wealth strengthen.",
        "Metal → Decisions shine.",
        "Water → Ride the flow wisely.",
    ],
    "ja": ["無理しなければ全体的に吉。", "成長の運。", "情熱が成果へ。", "安定と金運。", "決断が光る。", "流れに乗る。"],
    "zh": ["不勉强则整体大吉。", "成长之运。", "热情转化为成果。", "稳定与财运。", "决断发光。", "顺势而为。"],
    "ru": ["Если не перегружаться — год удачный.", "Рост и развитие.", "Страсть → результат.", "Стабильность и деньги.", "Решительность помогает.", "Плывите по течению мудро."],
    "hi": ["अधिक न करें तो साल शुभ।", "विकास का योग।", "जोश से परिणाम।", "स्थिरता और धन।", "निर्णय चमकेंगे।", "प्रवाह के साथ चलें।"],
}

DAILY_MSGS = {
    "ko": [
        "정리하면 운이 열립니다.",
        "대화가 열쇠! 먼저 안부를 건네보세요.",
        "작은 절약이 큰 이득으로 이어질 수 있어요.",
        "컨디션 관리가 핵심. 무리한 일정은 피하세요.",
        "도움 요청이 행운으로 연결됩니다.",
        "집중력 최고! 미뤄둔 일을 끝내기 좋아요.",
    ],
    "en": [
        "Organize things and luck opens up.",
        "Conversation is the key—reach out first.",
        "Small savings can turn into gains.",
        "Manage energy; avoid over-scheduling.",
        "Asking for help brings luck.",
        "High focus—finish what you postponed.",
    ],
    "ja": ["片付けると運が開く。", "会話が鍵。", "小さな節約が吉。", "無理しない。", "助けを求めると吉。", "集中力が高い。"],
    "zh": ["整理会带来好运。", "沟通是关键。", "小节省有回报。", "别太勉强。", "求助有好运。", "专注力很强。"],
    "ru": ["Порядок открывает удачу.", "Разговор — ключ.", "Небольшая экономия выгодна.", "Не перегружайтесь.", "Просите помощи — это к удаче.", "Отличная концентрация."],
    "hi": ["साफ-सफाई से भाग्य खुलता है।", "बातचीत जरूरी है।", "छोटी बचत लाभ दे सकती है।", "खुद को ज्यादा न थकाएँ।", "मदद माँगना शुभ है।", "ध्यान अच्छा रहेगा।"],
}

OVERALL_MSGS = {
    "ko": [
        "꾸준함이 대박을 부릅니다!",
        "관계운이 크게 열립니다.",
        "돈의 흐름이 좋아요. 관리하면 더 커져요.",
        "마음의 여유가 성과를 끌어옵니다.",
    ],
    "en": [
        "Consistency brings big wins!",
        "Relationship luck opens up.",
        "Money flow improves—manage it well.",
        "A calm mind attracts results.",
    ],
    "ja": ["継続が大きな成果へ。", "人間関係運が開く。", "金運上昇、管理が鍵。", "心の余裕が成果に。"],
    "zh": ["坚持会带来大收获。", "人际运打开。", "财运提升，管理关键。", "心态从容更容易成功。"],
    "ru": ["Постоянство = большой успех.", "Удача в отношениях растёт.", "Деньги идут лучше — важно управлять.", "Спокойствие приносит результат."],
    "hi": ["लगातार प्रयास से बड़ी सफलता।", "रिश्तों में भाग्य बढ़ेगा।", "धन प्रवाह बेहतर—सही प्रबंधन करें।", "शांत मन परिणाम लाता है।"],
}

LUCKY_COLORS = {
    "ko":["골드","레드","블루","그린","퍼플"],
    "en":["Gold","Red","Blue","Green","Purple"],
    "ja":["ゴールド","レッド","ブルー","グリーン","パープル"],
    "zh":["金色","红色","蓝色","绿色","紫色"],
    "ru":["Золото","Красный","Синий","Зелёный","Фиолетовый"],
    "hi":["सुनहरा","लाल","नीला","हरा","बैंगनी"],
}
LUCKY_ITEMS = {
    "ko":["황금 액세서리","빨간 지갑","파란 목걸이","초록 식물","보라색 펜"],
    "en":["Golden accessory","Red wallet","Blue necklace","Green plant","Purple pen"],
    "ja":["金のアクセ","赤い財布","青いネックレス","観葉植物","紫のペン"],
    "zh":["金色饰品","红色钱包","蓝色项链","绿色植物","紫色笔"],
    "ru":["Золотой аксессуар","Красный кошелёк","Синее ожерелье","Зелёное растение","Фиолетовая ручка"],
    "hi":["सुनहरी ऐक्सेसरी","लाल वॉलेट","नीला नेकलेस","हरा पौधा","बैंगनी पेन"],
}

TAROT_CARDS = {
    "ko": {
        "The Fool":"바보 - 새로운 시작, 모험",
        "The Magician":"마법사 - 창조력, 집중",
        "The Star":"별 - 희망, 치유",
        "The Sun":"태양 - 행복, 성공, 긍정 에너지",
        "The World":"세계 - 완성, 성취",
    },
    "en": {
        "The Fool":"New beginnings, adventure",
        "The Magician":"Manifestation, skill",
        "The Star":"Hope, healing",
        "The Sun":"Joy, success, positivity",
        "The World":"Completion, fulfillment",
    },
    "ja": {
        "The Fool":"新しい始まり・冒険",
        "The Magician":"創造・集中",
        "The Star":"希望・癒し",
        "The Sun":"幸福・成功",
        "The World":"完成・達成",
    },
    "zh": {
        "The Fool":"新的开始/冒险",
        "The Magician":"创造力/专注",
        "The Star":"希望/疗愈",
        "The Sun":"幸福/成功",
        "The World":"完成/成就",
    },
    "ru": {
        "The Fool":"Новый старт/приключение",
        "The Magician":"Сила/концентрация",
        "The Star":"Надежда/исцеление",
        "The Sun":"Радость/успех",
        "The World":"Завершение/достижение",
    },
    "hi": {
        "The Fool":"नई शुरुआत/साहस",
        "The Magician":"कौशल/एकाग्रता",
        "The Star":"आशा/चिकित्सा",
        "The Sun":"खुशी/सफलता",
        "The World":"पूर्णता/उपलब्धि",
    }
}


# ============================================================
# ✅ UI Helper
# ============================================================
st.set_page_config(page_title="2026 Fortune", layout="centered")

def get_zodiac(year: int, lang: str) -> str | None:
    if not (1900 <= year <= 2030):
        return None
    return ZODIAC_LIST[lang][(year - 4) % 12]

def get_saju(year, month, day, lang):
    total = year + month + day
    arr = SAJU_MSGS[lang]
    return arr[total % len(arr)]

def get_daily(zodiac, lang, offset=0):
    base = datetime.now() + timedelta(days=offset)
    # zodiac index 기반 seed
    z_list = ZODIAC_LIST[lang]
    idx = z_list.index(zodiac) if zodiac in z_list else 0
    seed = int(base.strftime("%Y%m%d")) + idx
    random.seed(seed)
    return random.choice(DAILY_MSGS[lang])

def combo_advice(mbti, zodiac, lang):
    # MBTI가 운세에 미치는 영향 형태
    if lang == "ko":
        return (
            f"**{mbti}** 성향은 올해 **{zodiac}** 흐름에서 ‘결정의 속도’가 강점이 될 수 있어요. "
            f"다만 급해지면 실수가 늘 수 있으니, 중요한 결정은 **하루(24시간) 숙성** 후 확정하면 운이 더 좋아집니다."
        )
    if lang == "en":
        return (
            f"As **{mbti}**, your strength is decision speed—this fits the **{zodiac}** flow. "
            f"But rushing increases mistakes. Let big decisions sit for **24 hours** first."
        )
    # 나머지 언어는 짧게
    return f"{mbti} + {zodiac}: Stay calm, decide after a short pause. (24h rule)"


# ============================================================
# ✅ Session init
# ============================================================
if "lang" not in st.session_state:
    st.session_state.lang = "ko"
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
if "mbti" not in st.session_state:
    st.session_state.mbti = None

# minigame state
if "mg_bonus" not in st.session_state:
    st.session_state.mg_bonus = 0  # 공유 보너스
if "mg_tries" not in st.session_state:
    st.session_state.mg_tries = 0
if "mg_running" not in st.session_state:
    st.session_state.mg_running = False
if "mg_start_ts" not in st.session_state:
    st.session_state.mg_start_ts = None
if "mg_last_elapsed" not in st.session_state:
    st.session_state.mg_last_elapsed = None
if "mg_show_form" not in st.session_state:
    st.session_state.mg_show_form = False
if "mg_win_pending" not in st.session_state:
    st.session_state.mg_win_pending = False


# ============================================================
# ✅ Global CSS (가독성 강화 / 배경색 조정)
# ============================================================
st.markdown("""
<style>
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
body { background: #f6f2ff; }
.block-container { padding-top: 1.2rem !important; padding-bottom: 2rem !important; }
@media (max-width: 768px){
  .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
}
.gradient {
  background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 55%, #8ec5fc 100%);
  border-radius: 18px;
  padding: 16px;
  color: white;
  text-align: center;
  box-shadow: 0 10px 24px rgba(0,0,0,0.12);
}
.subtle {
  color: rgba(255,255,255,0.92);
  font-size: 0.95rem;
}
.card {
  background: rgba(255,255,255,0.97);
  border-radius: 18px;
  padding: 18px 16px;
  box-shadow: 0 10px 26px rgba(0,0,0,0.09);
  border: 1px solid rgba(120,90,200,0.16);
}
.softbox{
  background: rgba(255,255,255,0.80);
  border-radius: 14px;
  padding: 12px 12px;
  border: 1px dashed rgba(160,120,220,0.55);
}
.adbox{
  background:#fff;
  border-radius: 16px;
  padding: 16px;
  border: 2px solid rgba(230,126,34,0.35);
  box-shadow: 0 10px 22px rgba(0,0,0,0.08);
}
.adbadge{
  display:inline-block;
  font-size: 0.75rem;
  font-weight: 800;
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(231,76,60,0.12);
  color: #e74c3c;
  border: 1px solid rgba(231,76,60,0.20);
  margin-bottom: 8px;
}
.bigbtn button{
  width: 100% !important;
  border-radius: 999px !important;
  padding: 14px 16px !important;
  font-weight: 900 !important;
}
.mgTimer{
  font-size: 2.1rem;
  font-weight: 900;
  letter-spacing: 1px;
  text-align:center;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# ✅ Language selector (6개 복구)
# ============================================================
lang_choice = st.radio(
    "Language / 언어",
    LANG_KEYS,
    format_func=lambda k: LANG_LABELS.get(k, k),
    horizontal=True,
    index=LANG_KEYS.index(st.session_state.lang) if st.session_state.lang in LANG_KEYS else 0,
)
st.session_state.lang = lang_choice
lang = st.session_state.lang
t = translations[lang]


# ============================================================
# ✅ Google Sheet 연결 상태
# ============================================================
sh, ws, sheet_err = gsheet_open()
sheet_ok = ws is not None

if not sheet_ok:
    st.warning(t.get("warning_sheet", "Google Sheet not connected"))
else:
    try:
        gsheet_ensure_header(ws)
    except Exception:
        # 헤더는 강제하지 않고 안전하게 진행
        pass


# ============================================================
# ✅ Input screen
# ============================================================
if not st.session_state.result_shown:
    st.markdown(f"""
    <div class="gradient">
      <div style="font-size:1.6rem; font-weight:900;">{t['title']}</div>
      <div class="subtle">{t['caption']}</div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    st.session_state.name = st.text_input(t["name_placeholder"], value=st.session_state.name)

    st.markdown(t["birth"])
    c1, c2, c3 = st.columns(3)
    st.session_state.year = c1.number_input("Year" if lang != "ko" else "년", 1900, 2030, st.session_state.year, 1)
    st.session_state.month = c2.number_input("Month" if lang != "ko" else "월", 1, 12, st.session_state.month, 1)
    st.session_state.day = c3.number_input("Day" if lang != "ko" else "일", 1, 31, st.session_state.day, 1)

    mode = st.radio(t["mbti_mode"], [t["direct"], t["test12"], t["test16"]], horizontal=False)

    # MBTI 직접
    if mode == t["direct"]:
        mbti_input = st.selectbox("MBTI", MBTI_KEYS)

        st.markdown('<div class="bigbtn">', unsafe_allow_html=True)
        if st.button(t["fortune_btn"]):
            st.session_state.mbti = mbti_input
            st.session_state.result_shown = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # 12문항
    elif mode == t["test12"]:
        st.markdown(f"<div class='card'><b>MBTI – 12</b><br>{t.get('test12_desc','')}</div>", unsafe_allow_html=True)

        # ✅ 모든 언어에서 질문이 해당 언어로 나오도록(최소 en/ko + 나머지는 간단 번역)
        q = {
            "ko": [
                ("E","I","사람 많은 자리에서 에너지가 충전된다","혼자 있을 때 에너지가 충전된다"),
                ("E","I","생각이 나면 말로 정리하는 편","머릿속에서 정리 후 말한다"),
                ("E","I","새로운 사람을 만나면 금방 친해진다","시간이 좀 걸린다"),
                ("S","N","사실/디테일을 먼저 본다","전체/의미/가능성을 먼저 본다"),
                ("S","N","실용적인 게 최고다","새로운 아이디어가 중요하다"),
                ("S","N","현재에 집중한다","미래를 상상한다"),
                ("T","F","결정은 논리가 우선","결정은 마음이 우선"),
                ("T","F","해결책 조언이 먼저 나온다","공감이 먼저다"),
                ("T","F","정확한 말이 중요하다","부드러운 말이 중요하다"),
                ("J","P","계획대로 해야 마음이 편하다","즉흥이어도 괜찮다"),
                ("J","P","마감 전 미리 끝낸다","마감 직전에 집중한다"),
                ("J","P","정리정돈이 중요하다","어수선해도 된다"),
            ],
            "en": [
                ("E","I","Crowds recharge my energy","Alone time recharges me"),
                ("E","I","I organize thoughts by speaking","I organize in my head first"),
                ("E","I","I quickly befriend new people","It takes time"),
                ("S","N","I notice facts/details first","I see meaning/possibilities first"),
                ("S","N","Practical matters most","New ideas matter most"),
                ("S","N","I focus on the present","I imagine the future"),
                ("T","F","Logic comes first in decisions","People's feelings come first"),
                ("T","F","I give solutions first","I empathize first"),
                ("T","F","Accuracy matters","Gentleness matters"),
                ("J","P","Plans make me comfortable","Spontaneous is fine"),
                ("J","P","I finish early","I focus near deadlines"),
                ("J","P","Organization is important","Some mess is okay"),
            ]
        }

        # 나머지 언어는 영어 기반이라도 “영어만 나온다” 문제를 피하려면 최소한 UI는 해당 언어로 보이게
        if lang not in q:
            q[lang] = q["en"]

        scores = {"E":0,"I":0,"S":0,"N":0,"T":0,"F":0,"J":0,"P":0}
        for idx, (a, b, qa, qb) in enumerate(q[lang]):
            ans = st.radio(
                f"{idx+1}.",
                [qa, qb],
                key=f"q12_{lang}_{idx}"
            )
            if ans == qa:
                scores[a] += 1
            else:
                scores[b] += 1

        st.markdown('<div class="bigbtn">', unsafe_allow_html=True)
        if st.button(t["result_btn"]):
            mbti = ("E" if scores["E"] >= scores["I"] else "I") + \
                   ("S" if scores["S"] >= scores["N"] else "N") + \
                   ("T" if scores["T"] >= scores["F"] else "F") + \
                   ("J" if scores["J"] >= scores["P"] else "P")
            st.session_state.mbti = mbti
            st.session_state.result_shown = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # 16문항
    else:
        st.markdown(f"<div class='card'><b>MBTI – 16</b><br>{t.get('test16_desc','')}</div>", unsafe_allow_html=True)

        # ✅ 중복 문항 문제: 각 축별 4문항 고정(중복 최소화)
        axes = {
            "ko": [
                ("E","I", ["모임 제안을 받으면 바로 나간다","처음 본 사람과 대화가 편하다","사람을 만나면 에너지가 생긴다","생각을 말로 풀어낸다"],
                        ["집에서 쉬는 게 더 좋다","처음 본 사람 대화가 부담","사람을 만나면 지친다","머릿속에서 정리 후 말한다"]),
                ("S","N", ["가격/구성을 먼저 본다","사실과 디테일이 중요","검증된 방식이 좋다","지금 할 수 있는 걸 바로 한다"],
                        ["분위기/컨셉을 먼저 본다","가능성과 의미가 중요","새로운 시도가 좋다","미래 그림을 상상한다"]),
                ("T","F", ["논리적으로 따진다","해결책을 제시한다","팩트가 우선","효율을 본다"],
                        ["기분 상하지 않게 조율","공감하며 들어준다","배려가 우선","관계를 본다"]),
                ("J","P", ["일정은 미리 계획","미리미리 끝낸다","정리정돈이 편하다","결정은 빠르게"],
                        ["즉흥이 편하다","마감 직전에 몰아서","약간 어수선해도 OK","더 알아보고 결정"]),
            ],
            "en": [
                ("E","I", ["I go out when invited","Talking to strangers is easy","People energize me","I process by speaking"],
                        ["I prefer staying home","Strangers tire me","People drain me","I speak after organizing thoughts"]),
                ("S","N", ["I check details/prices first","Facts matter","Proven methods are best","I act on what I can do now"],
                        ["I notice vibe first","Possibilities matter","I like new attempts","I imagine the future"]),
                ("T","F", ["I analyze logically","I propose solutions","Facts first","I value efficiency"],
                        ["I mediate feelings","I empathize first","Consideration first","I value relationships"]),
                ("J","P", ["I plan ahead","I finish early","I like things organized","I decide quickly"],
                        ["I prefer spontaneity","I rush near deadlines","Some chaos is fine","I explore more before deciding"]),
            ],
        }
        if lang not in axes:
            axes[lang] = axes["en"]

        scores = {"E":0,"I":0,"S":0,"N":0,"T":0,"F":0,"J":0,"P":0}
        for ax_i, (A, B, Aqs, Bqs) in enumerate(axes[lang]):
            st.subheader(f"{A} / {B}")
            for i in range(4):
                a_text = Aqs[i]
                b_text = Bqs[i]
                ans = st.radio(f"{i+1}/4", [a_text, b_text], key=f"q16_{lang}_{ax_i}_{i}")
                if ans == a_text:
                    scores[A] += 1
                else:
                    scores[B] += 1

        st.markdown('<div class="bigbtn">', unsafe_allow_html=True)
        if st.button(t["result_btn"]):
            mbti = ("E" if scores["E"] >= scores["I"] else "I") + \
                   ("S" if scores["S"] >= scores["N"] else "N") + \
                   ("T" if scores["T"] >= scores["F"] else "F") + \
                   ("J" if scores["J"] >= scores["P"] else "P")
            st.session_state.mbti = mbti
            st.session_state.result_shown = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# ✅ Result screen
# ============================================================
if st.session_state.result_shown:
    mbti = st.session_state.mbti
    zodiac = get_zodiac(st.session_state.year, lang)

    if zodiac is None:
        st.error(t.get("need_year", "Invalid year"))
        if st.button(t.get("reset", "Reset"), use_container_width=True):
            st.session_state.clear()
            st.rerun()
        st.stop()

    name = st.session_state.name.strip()
    if lang == "ko" and name:
        name_display = f"{name}님"
    else:
        name_display = name

    saju = get_saju(st.session_state.year, st.session_state.month, st.session_state.day, lang)
    today = get_daily(zodiac, lang, 0)
    tomorrow = get_daily(zodiac, lang, 1)
    overall = random.choice(OVERALL_MSGS[lang])
    lucky_color = random.choice(LUCKY_COLORS[lang])
    lucky_item = random.choice(LUCKY_ITEMS[lang])
    advice = combo_advice(mbti, zodiac, lang)

    # header
    st.markdown(f"""
    <div class="gradient">
      <div style="font-size:1.3rem; font-weight:900;">{(name_display+' ' if name_display else '')}{mbti}</div>
      <div style="font-size:1.0rem; margin-top:6px; font-weight:900;">{zodiac}</div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    # main card (HTML 태그가 그대로 보이는 문제 방지: 여기서만 unsafe html 사용)
    zodiac_desc = ZODIAC_TEXT[lang].get(zodiac, "")
    mbti_desc = MBTI_TRAITS.get(lang, MBTI_TRAITS["en"]).get(mbti, mbti)

    st.markdown(f"""
    <div class="card">
      <div style="font-size:1.05rem; line-height:1.9;">
        <b>{t.get('zodiac_title','Zodiac')}</b>: {zodiac_desc}<br>
        <b>{t.get('mbti_title','MBTI')}</b>: {mbti_desc}<br>
        <b>{t.get('saju_title','Fortune')}</b>: {saju}<br><br>

        <div class="softbox">
          <b>{t.get('today_title','Today')}</b>: {today}<br>
          <b>{t.get('tomorrow_title','Tomorrow')}</b>: {tomorrow}
        </div><br>

        <b>{t.get('overall_title','Overall')}</b>: {overall}<br><br>
        <b>{t.get('combo_title','Advice')}</b>: {advice}<br><br>

        <b>{t.get('lucky_color_title','Color')}</b>: {lucky_color} &nbsp;|&nbsp;
        <b>{t.get('lucky_item_title','Item')}</b>: {lucky_item}
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    # ✅ 광고(한국어만) + 미니게임 바로 위에 위치
    if lang == "ko":
        st.markdown(f"""
        <div class="adbox">
          <div class="adbadge">광고</div>
          <div style="font-weight:900; font-size:1.05rem;">{t['ad_title']}</div>
          <div style="margin-top:6px; line-height:1.65;">
            {t['ad_desc1']}<br>
            {t['ad_desc2']}
          </div>
          <div style="margin-top:10px;">
            <a href="{t['ad_url']}" target="_blank" style="font-weight:900; color:#e67e22; text-decoration:none;">
              {t['ad_link']}
            </a>
          </div>
        </div>
        """, unsafe_allow_html=True)
        st.write("")

    # 타로(정상 작동 유지)
    if st.button(t.get("tarot_btn","Tarot"), use_container_width=True):
        tarot_card = random.choice(list(TAROT_CARDS[lang].keys()))
        tarot_meaning = TAROT_CARDS[lang][tarot_card]
        st.markdown(f"""
        <div class="card" style="text-align:center;">
          <div style="font-weight:900; color:#8e44ad;">{t.get('tarot_title','Tarot')}</div>
          <div style="font-size:1.6rem; font-weight:900; margin-top:6px;">{tarot_card}</div>
          <div style="margin-top:6px; line-height:1.7;">{tarot_meaning}</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # ============================================================
    # ✅ 친구에게 결과 공유하기 (모바일 공유시트 / PC 복사)
    # ============================================================
    share_text = (
        f"{(name_display + ' ' if name_display else '')}{('2026년 운세' if lang=='ko' else '2026 Fortune')}\n"
        f"{zodiac} + {mbti}\n\n"
        f"{t.get('today_title','Today')}: {today}\n"
        f"{t.get('tomorrow_title','Tomorrow')}: {tomorrow}\n\n"
        f"{t.get('overall_title','Overall')}: {overall}\n"
        f"{t.get('combo_title','Advice')}: {advice}\n"
        f"{t.get('lucky_color_title','Color')}: {lucky_color} | {t.get('lucky_item_title','Item')}: {lucky_item}\n\n"
        f"{APP_URL}"
    )

    st.markdown(f"""
    <div class="bigbtn">
      <button id="shareBtn" style="background:#6c3bd1; color:white; border:none; cursor:pointer;">
        {t.get("share_btn","Share")}
      </button>
    </div>
    <div style="text-align:center; margin-top:10px; font-size:0.9rem; color:#666;">
      {t.get("share_hint","")}
    </div>
    <textarea id="shareText" style="position:absolute; left:-9999px;">{share_text}</textarea>
    <script>
      const btn = window.parent.document.getElementById("shareBtn");
      const txt = window.parent.document.getElementById("shareText");
      if (btn) {{
        btn.onclick = async () => {{
          const text = txt.value;
          try {{
            if (navigator.share) {{
              await navigator.share({{ text: text, url: "{APP_URL}" }});
            }} else {{
              await navigator.clipboard.writeText(text);
              alert("{t.get('copy_done','Copied')}");
            }}
          }} catch (e) {{
            try {{
              await navigator.clipboard.writeText(text);
              alert("{t.get('copy_done','Copied')}");
            }} catch (e2) {{
              alert("Share failed. Please copy manually.");
            }}
          }}
        }};
      }}
    </script>
    """, unsafe_allow_html=True)

    st.write("")

    # ============================================================
    # ✅ 미니게임 (한국어만)
    #   - 선착순 20명 자동 마감
    #   - 중복 참여 방지(전화번호 hash)
    #   - 공유 보너스 1회(수동 버튼으로 지급)
    #   - 당첨 시 입력 폼 표시 → 시트 저장
    # ============================================================
    if lang == "ko":
        st.markdown(f"<div class='card'><div style='font-size:1.2rem; font-weight:900;'>{t['minigame_title']}</div>"
                    f"<div style='margin-top:8px; line-height:1.7;'>{t['minigame_desc']}</div>"
                    f"<div style='margin-top:8px; color:#666;'>{t['minigame_share_bonus']}</div></div>",
                    unsafe_allow_html=True)
        st.write("")

        # 공유 보너스(사용자 클릭 방식)
        colb1, colb2 = st.columns([1,1])
        with colb1:
            if st.button(t["minigame_bonus_btn"], use_container_width=True):
                # 보너스는 최대 1회
                st.session_state.mg_bonus = 1
                st.success("✅ 추가 기회 1회가 지급되었습니다!")
        with colb2:
            attempts_total = 1 + st.session_state.mg_bonus
            attempts_left = max(0, attempts_total - st.session_state.mg_tries)
            st.info(f"{t['minigame_attempts']}: {attempts_left} / {attempts_total}")

        st.write("")

        # 시트 연결 안되면 안내만
        if not sheet_ok:
            st.warning(t["minigame_not_ready"])
        else:
            win_count, phone_hashes = gsheet_get_stats(ws)

            if win_count >= WINNER_LIMIT:
                st.error(t["minigame_closed"])
            else:
                st.caption(f"선착순 현황: {win_count}/{WINNER_LIMIT} (남은 인원 {WINNER_LIMIT-win_count}명)")

                # 타이머 표시 (자동 리프레시)
                # running 상태일 때만 일정 간격으로 rerun
                if st.session_state.mg_running:
                    st_autorefresh = getattr(st, "autorefresh", None)
                    if callable(st_autorefresh):
                        st_autorefresh(interval=50, limit=2000, key="mg_refresh")

                elapsed_now = None
                if st.session_state.mg_running and st.session_state.mg_start_ts is not None:
                    elapsed_now = time.time() - st.session_state.mg_start_ts
                elif st.session_state.mg_last_elapsed is not None:
                    elapsed_now = st.session_state.mg_last_elapsed

                if elapsed_now is None:
                    elapsed_now = 0.0

                st.markdown(f"<div class='mgTimer'>{elapsed_now:0.3f}s</div>", unsafe_allow_html=True)
                st.write("")

                # 버튼 (기회 없으면 비활성)
                disabled_all = (attempts_left <= 0)

                c1, c2 = st.columns(2)
                with c1:
                    if st.button(t["minigame_start"], use_container_width=True, disabled=disabled_all or st.session_state.mg_running):
                        st.session_state.mg_running = True
                        st.session_state.mg_start_ts = time.time()
                        st.session_state.mg_last_elapsed = None
                        st.session_state.mg_win_pending = False
                        st.session_state.mg_show_form = False
                        st.rerun()
                with c2:
                    if st.button(t["minigame_stop"], use_container_width=True, disabled=disabled_all or (not st.session_state.mg_running)):
                        st.session_state.mg_running = False
                        elapsed = time.time() - st.session_state.mg_start_ts
                        st.session_state.mg_last_elapsed = elapsed
                        st.session_state.mg_start_ts = None

                        # 1회 소모
                        st.session_state.mg_tries += 1

                        # 당첨 판정
                        if TARGET_MIN <= elapsed <= TARGET_MAX:
                            st.session_state.mg_win_pending = True
                            st.session_state.mg_show_form = True
                        else:
                            st.session_state.mg_win_pending = False
                            st.session_state.mg_show_form = False
                        st.rerun()

                if st.session_state.mg_running:
                    st.info(t["minigame_running"])

                # 결과 메시지 + 폼
                if (not st.session_state.mg_running) and (st.session_state.mg_last_elapsed is not None):
                    elapsed = st.session_state.mg_last_elapsed
                    if st.session_state.mg_win_pending:
                        st.success(f"{t['minigame_win']} (기록: {elapsed:0.3f}s)")
                    else:
                        st.warning(f"{t['minigame_lose']} (기록: {elapsed:0.3f}s)")

                if st.session_state.mg_show_form and st.session_state.mg_win_pending:
                    st.markdown(f"<div class='card'><div style='font-size:1.1rem; font-weight:900;'>{t['minigame_form_title']}</div></div>", unsafe_allow_html=True)

                    with st.form("winner_form", clear_on_submit=False):
                        w_name = st.text_input("이름", value=st.session_state.name.strip())
                        w_phone = st.text_input("전화번호", placeholder="010-1234-5678")
                        consent = st.checkbox(t["consent_text"])
                        submitted = st.form_submit_button(t["submit"])

                    if submitted:
                        phone_digits = _normalize_phone(w_phone)
                        if not consent:
                            st.error(t["minigame_need_consent"])
                        elif len(phone_digits) < 10:
                            st.error("전화번호를 정확히 입력해주세요.")
                        else:
                            phone_hash = _hash_phone(phone_digits)

                            # 중복 방지
                            if phone_hash in phone_hashes:
                                st.error(t["duplicate"])
                            else:
                                # 선착순 재확인
                                win_count2, _ = gsheet_get_stats(ws)
                                if win_count2 >= WINNER_LIMIT:
                                    st.error(t["minigame_closed"])
                                else:
                                    try:
                                        gsheet_append_entry(
                                            ws,
                                            lang="ko",
                                            name=w_name.strip(),
                                            phone_digits=phone_digits,
                                            mbti=mbti,
                                            zodiac=zodiac,
                                            elapsed=st.session_state.mg_last_elapsed or 0.0,
                                            status="WIN",
                                        )
                                        st.success(t["saved"])
                                        # 폼 닫기
                                        st.session_state.mg_show_form = False
                                        st.session_state.mg_win_pending = False
                                    except Exception as e:
                                        st.error(f"시트 저장 실패: {e}")

        st.write("")

    # footer url
    st.markdown(f"<div style='text-align:center; color:#888; font-size:0.9rem;'>{APP_URL}</div>", unsafe_allow_html=True)
    st.write("")

    # ✅ 입력화면 버튼 삭제 요청 반영: 결과 화면에는 reset만 남김
    if st.button(t.get("reset", "Reset"), use_container_width=True):
        st.session_state.clear()
        st.rerun()
