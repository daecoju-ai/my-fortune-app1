import streamlit as st
from datetime import datetime
import random
import re
import json
from pathlib import Path

# ---- Google Sheet ----
try:
    import gspread
    from google.oauth2.service_account import Credentials
except Exception:
    gspread = None
    Credentials = None

# =========================================================
# 0) App Config
# =========================================================
APP_URL = "https://my-fortune.streamlit.app"
SPREADSHEET_ID = "1WvuKXx2if2WvxmQaxkqzFW-BzDEWWma9hZgCr2jJQYY"
SHEET_NAME = "시트1"

DATA_DIR = Path(__file__).parent / "data"

st.set_page_config(
    page_title="2026 Fortune | 띠+MBTI+사주+오늘/내일",
    page_icon="🔮",
    layout="centered"
)

# =========================================================
# 1) Helpers
# =========================================================
def safe_toast(msg: str):
    if not msg:
        return
    try:
        if hasattr(st, "toast"):
            st.toast(msg)
        else:
            st.success(msg)
    except Exception:
        st.success(msg)

def normalize_phone(phone: str) -> str:
    return re.sub(r"[^0-9]", "", phone or "")

def get_query_params():
    try:
        return dict(st.query_params)
    except Exception:
        try:
            return st.experimental_get_query_params()
        except Exception:
            return {}

def set_query_params(params: dict):
    try:
        st.query_params.clear()
        for k, v in params.items():
            st.query_params[k] = v
    except Exception:
        st.experimental_set_query_params(**params)

def clear_param(param_key: str):
    try:
        params = get_query_params()
        if param_key in params:
            params.pop(param_key, None)
            set_query_params(params)
    except Exception:
        pass

# =========================================================
# 2) SEO Inject (안전하게)
# =========================================================
def inject_seo(lang_code: str):
    desc_map = {
        "ko": "2026년 띠운세 + MBTI + 사주 + 오늘/내일 운세 + 타로까지 무료로! (한국어 미니게임 이벤트 포함)",
        "en": "Free 2026 Zodiac + MBTI + Saju + Daily/Tomorrow fortune + Tarot.",
        "ja": "2026年の干支運勢＋MBTI＋四柱＋今日/明日＋タロットを無料で。",
        "zh": "免费：2026生肖运势 + MBTI + 四柱 + 今日/明日 + 塔罗。",
        "ru": "Бесплатно: 2026 зодиак + MBTI + саджу + сегодня/завтра + таро。",
        "hi": "मुफ़्त: 2026 राशि + MBTI + साजू + आज/कल + टैरो।",
    }
    kw_map = {
        "ko": "2026 운세, 띠운세, MBTI 운세, 사주, 오늘 운세, 내일 운세, 무료 운세, 타로, 연애운, 재물운, 건강운",
        "en": "2026 fortune, zodiac, MBTI, saju, today fortune, tomorrow fortune, free, tarot",
        "ja": "2026 運勢, 干支, MBTI, 四柱, 今日, 明日, 無料, タロット",
        "zh": "2026 运势, 生肖, MBTI, 四柱, 今日, 明日, 免费, 塔罗",
        "ru": "2026 гороскоп, зодиак, MBTI, саджу, сегодня, завтра, бесплатно, таро",
        "hi": "2026 राशिफल, राशि, MBTI, साजू, आज, कल, मुफ्त, टैरो",
    }

    description = desc_map.get(lang_code, desc_map["en"])
    keywords = kw_map.get(lang_code, kw_map["en"])
    title = "2026 Fortune | Zodiac + MBTI + Saju + Today/Tomorrow"
    if lang_code == "ko":
        title = "2026 운세 | 띠 + MBTI + 사주 + 오늘/내일 운세"

    webapp_ld = {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": title,
        "url": APP_URL,
        "applicationCategory": "LifestyleApplication",
        "operatingSystem": "Web",
        "description": description
    }

    try:
        st.components.v1.html(
            f"""
<script>
(function() {{
  try {{
    const description = {json.dumps(description, ensure_ascii=False)};
    const keywords = {json.dumps(keywords, ensure_ascii=False)};
    const title = {json.dumps(title, ensure_ascii=False)};
    const appUrl = {json.dumps(APP_URL, ensure_ascii=False)};

    const metas = [
      ['name','description', description],
      ['name','keywords', keywords],
      ['property','og:title', title],
      ['property','og:description', description],
      ['property','og:type','website'],
      ['property','og:url', appUrl],
      ['name','twitter:card','summary'],
      ['name','robots','index,follow']
    ];

    metas.forEach(([attr, key, val]) => {{
      let el = document.head.querySelector(`meta[${{attr}}="${{key}}"]`);
      if(!el) {{
        el = document.createElement('meta');
        el.setAttribute(attr, key);
        document.head.appendChild(el);
      }}
      el.setAttribute('content', val);
    }});

    let canonical = document.head.querySelector('link[rel="canonical"]');
    if(!canonical) {{
      canonical = document.createElement('link');
      canonical.setAttribute('rel','canonical');
      document.head.appendChild(canonical);
    }}
    canonical.setAttribute('href', appUrl);

    const webappLd = {json.dumps(json.dumps(webapp_ld, ensure_ascii=False))};
    let s1 = document.head.querySelector('script[data-jsonld="fortune-webapp"]');
    if(!s1) {{
      s1 = document.createElement('script');
      s1.type = 'application/ld+json';
      s1.setAttribute('data-jsonld','fortune-webapp');
      document.head.appendChild(s1);
    }}
    s1.text = webappLd;

  }} catch(e) {{}}
}})();
</script>
""",
            height=0
        )
    except Exception:
        pass

# =========================================================
# 3) Language / Text
# =========================================================
LANGS = [
    ("ko", "한국어"),
    ("en", "English"),
    ("ja", "日本語"),
    ("zh", "中文"),
    ("ru", "Русский"),
    ("hi", "हिन्दी"),
]

T = {
    "ko": {
        "lang_pick": "언어 선택",
        "title": "2026 띠 + MBTI + 사주 + 오늘/내일 운세",
        "subtitle": "완전 무료",
        "name": "이름 입력 (결과에 표시돼요)",
        "birth": "생년월일 입력",
        "year": "년", "month": "월", "day": "일",
        "mbti_mode": "MBTI를 어떻게 할까요?",
        "mbti_direct": "직접 선택",
        "mbti_12": "간단 테스트 (12문항)",
        "mbti_16": "상세 테스트 (16문항)",
        "mbti_submit": "제출하고 MBTI 확정",
        "go_result": "2026년 운세 보기!",
        "reset": "처음부터 다시하기",
        "share_link_btn": "🔗 링크 공유하기",
        "share_link_hint": "버튼을 누르면 ‘링크 공유’ 창이 뜹니다.",
        "share_bonus_done": "공유 확인! 미니게임 1회 추가 지급 🎁",
        "tarot_btn": "오늘의 타로 카드 뽑기",
        "tarot_title": "오늘의 타로 카드",
        "sections": {
            "zodiac": "띠 운세",
            "mbti": "MBTI 특징",
            "saju": "사주 한 마디",
            "today": "오늘 운세",
            "tomorrow": "내일 운세",
            "year_all": "2026 전체 운세",
            "love": "연애운 조언",
            "money": "재물운 조언",
            "work": "직장/일 조언",
            "health": "건강 조언",
            "lucky": "행운 포인트",
            "action": "오늘의 액션팁",
            "caution": "주의할 점",
        },
        "ad_placeholder": "AD (심사 통과 후 이 위치에 광고가 표시됩니다)",
        "ad_kr_title": "정수기렌탈 대박!",
        "ad_kr_body1": "제휴카드면 월 0원부터!",
        "ad_kr_body2": "설치 당일 최대 50만원 지원 + 사은품 듬뿍",
        "ad_kr_link": "다나눔렌탈.com 바로가기",
        "ad_kr_url": "https://www.다나눔렌탈.com",
        "mini_title": "🎁 미니게임: 선착순 20명 커피쿠폰 도전!",
        "mini_desc": "스톱워치를 **20.16초**에 맞추면 당첨!\n\n- 기본 1회\n- **링크 공유하기**를 누르면 1회 추가\n- 목표 구간: **20.160 ~ 20.169초**",
        "mini_try_left": "남은 시도",
        "mini_closed": "이벤트가 종료되었습니다. (선착순 20명 마감)",
        "mini_dup": "이미 참여한 번호입니다. (중복 참여 불가)",
        "win_title": "🎉 당첨! 정보 입력",
        "win_name": "이름",
        "win_phone": "전화번호",
        "win_consent": "개인정보 수집·이용 동의(필수)",
        "win_consent_text": "이벤트 경품 발송을 위해 이름/전화번호를 수집하며, 목적 달성 후 지체 없이 파기합니다. 동의 거부 시 참여가 제한됩니다.",
        "win_submit": "제출",
        "win_thanks": "접수 완료! 커피쿠폰 발송 대상에 등록되었습니다.",
        "sheet_fail": "구글시트 연결이 아직 안 되어 있어요. (Secrets/시트 공유/탭 이름 확인 필요)",
        "sheet_ok": "구글시트 연결 완료",
        "faq_title": "🔎 검색/AI 노출용 정보(FAQ)",
        "stopwatch_note": "START 후 STOP을 누르면 기록이 자동 입력됩니다.",
        "mbti_test_12_title": "MBTI 12문항",
        "mbti_test_16_title": "MBTI 16문항",
        "mbti_test_help": "각 문항에서 더 가까운 쪽을 선택하세요.",
        "try_over": "남은 시도가 없습니다.",
        "miss": "아쉽게도 미달/초과! 다시 도전해보세요 🙂",
        "share_not_supported": "이 기기에서는 시스템 공유가 지원되지 않습니다.",
        "time_input_label": "STOP을 누르면 기록이 자동으로 들어옵니다.",
        "submit_record": "기록 제출",
        "no_tries_block": "남은 시도가 0이라 START/STOP이 비활성화됩니다.",
        "data_missing": "운세 데이터 로딩 실패: 파일/키가 없습니다. (임의 생성하지 않음)",
        "data_debug_title": "데이터 로딩 디버그(원인)",
    },
    "en": {"lang_pick":"Language","title":"2026 Zodiac + MBTI + Saju + Today/Tomorrow","subtitle":"Completely Free",
           "name":"Name (shown in result)","birth":"Birth date","year":"Year","month":"Month","day":"Day",
           "mbti_mode":"MBTI setting","mbti_direct":"Pick directly","mbti_12":"Quick test (12)","mbti_16":"Full test (16)",
           "mbti_submit":"Submit & set MBTI","go_result":"See result","reset":"Start over",
           "share_link_btn":"🔗 Share link","share_link_hint":"Opens native share sheet when supported.",
           "tarot_btn":"Draw today's tarot","tarot_title":"Today's Tarot",
           "sections":{"zodiac":"Zodiac","mbti":"MBTI","saju":"Saju","today":"Today","tomorrow":"Tomorrow","year_all":"2026 Overall",
                       "love":"Love","money":"Money","work":"Work","health":"Health","lucky":"Lucky point","action":"Action tip","caution":"Caution"},
           "ad_placeholder":"AD","faq_title":"FAQ","stopwatch_note":"Press START then STOP to auto-fill the time.",
           "mbti_test_12_title":"MBTI 12 Questions","mbti_test_16_title":"MBTI 16 Questions","mbti_test_help":"Pick the closer option.",
           "time_input_label":"Time will be auto-filled after STOP.","submit_record":"Submit record","share_not_supported":"Native share not supported.",
           "data_missing":"Failed to load fortune data (no auto-generation).","data_debug_title":"Data debug"},
    "ja": {"lang_pick":"言語","title":"2026年 干支 + MBTI + 四柱 + 今日/明日","subtitle":"完全無料",
           "name":"名前（結果に表示）","birth":"生年月日","year":"年","month":"月","day":"日",
           "mbti_mode":"MBTI 設定","mbti_direct":"直接選択","mbti_12":"簡易テスト（12）","mbti_16":"詳細テスト（16）",
           "mbti_submit":"送信して確定","go_result":"結果を見る","reset":"最初から",
           "share_link_btn":"🔗 リンク共有","share_link_hint":"対応端末では共有シートが開きます。",
           "tarot_btn":"今日のタロット","tarot_title":"今日のタロット",
           "sections":{"zodiac":"干支運勢","mbti":"MBTI特徴","saju":"四柱コメント","today":"今日","tomorrow":"明日","year_all":"2026年総合",
                       "love":"恋愛","money":"金運","work":"仕事","health":"健康","lucky":"ラッキー","action":"行動","caution":"注意"},
           "ad_placeholder":"AD","faq_title":"FAQ","stopwatch_note":"START→STOPで記録を自動入力します。",
           "mbti_test_12_title":"MBTI 12問","mbti_test_16_title":"MBTI 16問","mbti_test_help":"近い方を選択してください。",
           "time_input_label":"STOP後に自動入力されます。","submit_record":"送信","share_not_supported":"この端末では共有が使えません。",
           "data_missing":"データの読み込みに失敗（自動生成しません）","data_debug_title":"データ原因"},
    "zh": {"lang_pick":"语言","title":"2026 生肖 + MBTI + 四柱 + 今日/明日","subtitle":"完全免费",
           "name":"姓名（结果显示）","birth":"出生日期","year":"年","month":"月","day":"日",
           "mbti_mode":"MBTI 设置","mbti_direct":"直接选择","mbti_12":"快速测试（12）","mbti_16":"详细测试（16）",
           "mbti_submit":"提交并确定","go_result":"查看结果","reset":"重新开始",
           "share_link_btn":"🔗 分享链接","share_link_hint":"支持时打开系统分享。",
           "tarot_btn":"抽今日塔罗","tarot_title":"今日塔罗",
           "sections":{"zodiac":"生肖运势","mbti":"MBTI 特点","saju":"四柱短评","today":"今天","tomorrow":"明天","year_all":"2026 总运",
                       "love":"恋爱","money":"财运","work":"工作","health":"健康","lucky":"幸运","action":"行动","caution":"注意"},
           "ad_placeholder":"AD","faq_title":"FAQ","stopwatch_note":"按 START 再按 STOP 自动填入时间。",
           "mbti_test_12_title":"MBTI 12题","mbti_test_16_title":"MBTI 16题","mbti_test_help":"选择更符合你的选项。",
           "time_input_label":"STOP 后会自动填入。","submit_record":"提交记录","share_not_supported":"此设备不支持系统分享。",
           "data_missing":"运势数据加载失败（不自动生成）","data_debug_title":"数据原因"},
    "ru": {"lang_pick":"Язык","title":"2026: Зодиак + MBTI + Саджу + Сегодня/Завтра","subtitle":"Бесплатно",
           "name":"Имя (в результате)","birth":"Дата рождения","year":"Год","month":"Месяц","day":"День",
           "mbti_mode":"MBTI","mbti_direct":"Выбрать","mbti_12":"Тест (12)","mbti_16":"Тест (16)",
           "mbti_submit":"Отправить","go_result":"Показать","reset":"Сначала",
           "share_link_btn":"🔗 Поделиться","share_link_hint":"Системное меню при поддержке.",
           "tarot_btn":"Таро дня","tarot_title":"Таро дня",
           "sections":{"zodiac":"Зодиак","mbti":"MBTI","saju":"Саджу","today":"Сегодня","tomorrow":"Завтра","year_all":"Итог 2026",
                       "love":"Любовь","money":"Деньги","work":"Работа","health":"Здоровье","lucky":"Удача","action":"Действие","caution":"Осторожно"},
           "ad_placeholder":"AD","faq_title":"FAQ","stopwatch_note":"START затем STOP — время заполнится автоматически.",
           "mbti_test_12_title":"MBTI 12","mbti_test_16_title":"MBTI 16","mbti_test_help":"Выберите ближе к вам.",
           "time_input_label":"После STOP заполнится автоматически.","submit_record":"Отправить","share_not_supported":"Нет системного шеринга.",
           "data_missing":"Не удалось загрузить данные (без автогенерации)","data_debug_title":"Причина"},
    "hi": {"lang_pick":"भाषा","title":"2026 राशि + MBTI + साजू + आज/कल","subtitle":"मुफ़्त",
           "name":"नाम","birth":"जन्मतिथि","year":"वर्ष","month":"महीना","day":"दिन",
           "mbti_mode":"MBTI","mbti_direct":"सीधे चुनें","mbti_12":"टेस्ट (12)","mbti_16":"टेस्ट (16)",
           "mbti_submit":"सबमिट","go_result":"परिणाम","reset":"फिर से",
           "share_link_btn":"🔗 शेयर","share_link_hint":"समर्थित हो तो सिस्टम शेयर खुलेगा।",
           "tarot_btn":"आज का टैरो","tarot_title":"आज का टैरो",
           "sections":{"zodiac":"राशि","mbti":"MBTI","saju":"साजू","today":"आज","tomorrow":"कल","year_all":"2026",
                       "love":"प्यार","money":"धन","work":"काम","health":"स्वास्थ्य","lucky":"लकी","action":"एक्शन","caution":"सावधानी"},
           "ad_placeholder":"AD","faq_title":"FAQ","stopwatch_note":"START फिर STOP — समय ऑटो भर जाएगा।",
           "mbti_test_12_title":"MBTI 12","mbti_test_16_title":"MBTI 16","mbti_test_help":"जो फिट हो चुनें।",
           "time_input_label":"STOP के बाद ऑटो भर जाएगा।","submit_record":"सबमिट","share_not_supported":"Native share समर्थित नहीं।",
           "data_missing":"डेटा लोड नहीं हुआ (ऑटो-जनरेट नहीं)","data_debug_title":"कारण"},
}

# =========================================================
# 4) Tarot (localized)
# =========================================================
TAROT = {
    "Wheel of Fortune": {
        "name": {"ko":"운명의 수레바퀴","en":"Wheel of Fortune","ja":"運命の輪","zh":"命运之轮","ru":"Колесо Фортуны","hi":"भाग्य का पहिया"},
        "meaning": {"ko":"변화, 전환점","en":"Change, turning point","ja":"変化・転機","zh":"变化、转机","ru":"Перемены, поворот","hi":"बदलाव, टर्निंग पॉइंट"},
    },
    "The Sun": {
        "name": {"ko":"태양","en":"The Sun","ja":"太陽","zh":"太阳","ru":"Солнце","hi":"सूर्य"},
        "meaning": {"ko":"행복, 성공, 긍정 에너지","en":"Happiness, success, positive energy","ja":"幸福・成功・前向き","zh":"幸福、成功、积极","ru":"Счастье, успех, позитив","hi":"खुशी, सफलता, सकारात्मक"},
    },
    "Strength": {
        "name": {"ko":"힘","en":"Strength","ja":"力","zh":"力量","ru":"Сила","hi":"शक्ति"},
        "meaning": {"ko":"용기, 인내","en":"Courage, patience","ja":"勇気・忍耐","zh":"勇气、耐心","ru":"Смелость, терпение","hi":"साहस, धैर्य"},
    },
    "The World": {
        "name": {"ko":"세계","en":"The World","ja":"世界","zh":"世界","ru":"Мир","hi":"विश्व"},
        "meaning": {"ko":"완성, 성취","en":"Completion, achievement","ja":"完成・達成","zh":"完成、成就","ru":"Завершение, достижение","hi":"पूर्णता, उपलब्धि"},
    },
}

# =========================================================
# 5) OFFLINE DATA LOADING (근본 해결 버전)
#    - 한국어만 안 뜨는 원인 1순위: UTF-8 BOM
#    - 해결: encoding="utf-8-sig"로 읽기
# =========================================================
@st.cache_data(show_spinner=False)
def load_json_utf8sig(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"missing file: {path.as_posix()}")
    # ✅ BOM 제거 포함 로딩
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def fortunes_path(lang: str) -> Path:
    return DATA_DIR / f"fortunes_{lang}.json"

def require_combo_record(data: dict, combo_key: str) -> dict:
    # 우리가 기대하는 구조: data["combos"][combo_key] 또는 data[combo_key]
    if isinstance(data, dict):
        if "combos" in data and isinstance(data["combos"], dict):
            if combo_key in data["combos"]:
                return data["combos"][combo_key]
            raise KeyError(f"combos['{combo_key}'] not found")
        # 일부 파일은 최상위에 바로 키로 있을 수 있음
        if combo_key in data and isinstance(data[combo_key], dict):
            return data[combo_key]
    raise KeyError("no combos structure found")

# =========================================================
# 6) Zodiac 계산 (연도→띠)
# =========================================================
ZODIAC_ORDER = ["쥐","소","호랑이","토끼","용","뱀","말","양","원숭이","닭","개","돼지"]

def zodiac_ko_from_year(year: int) -> str:
    idx = (year - 4) % 12
    return ZODIAC_ORDER[idx]

# =========================================================
# 7) MBTI 12/16 (질문 데이터는 기존 그대로 유지)
# =========================================================
MBTI_DESC = {
    "INTJ":{"ko":"전략가 · 목표지향","en":"Strategist","ja":"戦略家","zh":"战略家","ru":"Стратег","hi":"रणनीतिक"},
    "INTP":{"ko":"아이디어 · 분석가","en":"Analyst","ja":"分析家","zh":"分析者","ru":"Аналитик","hi":"विश्लेषक"},
    "ENTJ":{"ko":"리더 · 추진력","en":"Leader","ja":"指揮官","zh":"领导者","ru":"Лидер","hi":"नेता"},
    "ENTP":{"ko":"토론가 · 발상가","en":"Inventor","ja":"討論者","zh":"辩论家","ru":"Спорщик","hi":"बहसकर्ता"},
    "INFJ":{"ko":"통찰 · 조언자","en":"Advisor","ja":"提唱者","zh":"洞察者","ru":"Советник","hi":"सलाहकार"},
    "INFP":{"ko":"가치 · 감성","en":"Idealist","ja":"仲介者","zh":"调停者","ru":"Идеалист","hi":"आदर्शवादी"},
    "ENFJ":{"ko":"조율 · 리더","en":"Coordinator","ja":"主人公","zh":"主人公","ru":"Наставник","hi":"समन्वयक"},
    "ENFP":{"ko":"열정 · 아이디어","en":"Energetic","ja":"運動家","zh":"竞选者","ru":"Энтузиаст","hi":"उत्साही"},
    "ISTJ":{"ko":"원칙 · 책임","en":"Responsible","ja":"管理者","zh":"物流师","ru":"Исполнитель","hi":"जिम्मेदार"},
    "ISFJ":{"ko":"배려 · 헌신","en":"Caring","ja":"擁護者","zh":"守卫者","ru":"Защитник","hi":"देखभाल"},
    "ESTJ":{"ko":"관리자 · 현실","en":"Executor","ja":"幹部","zh":"总经理","ru":"Администратор","hi":"प्रबंधक"},
    "ESFJ":{"ko":"분위기 · 케어","en":"Warm","ja":"領事","zh":"执政官","ru":"Консул","hi":"मिलनसार"},
    "ISTP":{"ko":"장인 · 문제해결","en":"Solver","ja":"巨匠","zh":"鉴赏家","ru":"Мастер","hi":"कुशल"},
    "ISFP":{"ko":"감성 · 힐러","en":"Artist","ja":"冒険家","zh":"探险家","ru":"Художник","hi":"कलात्मक"},
    "ESTP":{"ko":"모험 · 실행","en":"Action","ja":"起業家","zh":"企业家","ru":"Делец","hi":"साहसी"},
    "ESFP":{"ko":"사교 · 즐거움","en":"Fun","ja":"エンターテイナー","zh":"表演者","ru":"Артист","hi":"मस्ती"},
}
MBTI_LIST = sorted(MBTI_DESC.keys())

MBTI_Q_12_L10N = [
    ("EI",
     {"ko":"사람들과 있을 때 에너지가 더 생긴다", "en":"I gain energy with people", "ja":"人といると元気になる", "zh":"与人相处更有能量", "ru":"С людьми я заряжаюсь", "hi":"लोगों के साथ ऊर्जा बढ़ती है"},
     {"ko":"혼자 있을 때 에너지가 더 생긴다", "en":"I gain energy alone", "ja":"一人でいると元気になる", "zh":"独处更有能量", "ru":"В одиночестве я заряжаюсь", "hi":"अकेले रहने से ऊर्जा बढ़ती है"}),
    ("SN",
     {"ko":"현실적인 정보가 편하다", "en":"I prefer practical facts", "ja":"現実的な情報が楽", "zh":"更偏好现实信息", "ru":"Предпочитаю факты", "hi":"व्यावहारिक तथ्य पसंद हैं"},
     {"ko":"가능성/아이디어가 편하다", "en":"I prefer ideas/possibilities", "ja":"可能性やアイデアが楽", "zh":"更偏好可能性/想法", "ru":"Предпочитаю идеи/возможности", "hi":"विचार/संभावनाएँ पसंद हैं"}),
    ("TF",
     {"ko":"결정은 논리/원칙이 우선", "en":"Logic/principles first", "ja":"論理/原則が優先", "zh":"逻辑/原则优先", "ru":"Логика/принципы важнее", "hi":"तर्क/सिद्धांत पहले"},
     {"ko":"결정은 사람/상황 배려가 우선", "en":"People/context first", "ja":"人/状況への配慮が優先", "zh":"人/情境优先", "ru":"Люди/контекст важнее", "hi":"लोग/परिस्थिति पहले"}),
    ("JP",
     {"ko":"계획대로 진행해야 마음이 편하다", "en":"I feel better with plans", "ja":"計画通りが安心", "zh":"按计划更安心", "ru":"С планом спокойнее", "hi":"योजना से आराम"},
     {"ko":"유연하게 바뀌어도 괜찮다", "en":"I'm okay with changes", "ja":"柔軟に変わってもOK", "zh":"灵活改变也可以", "ru":"Нормально, если меняется", "hi":"लचीलापन ठीक"}),
    ("EI",
     {"ko":"말하며 생각이 정리된다", "en":"I think while speaking", "ja":"話しながら整理する", "zh":"边说边整理思路", "ru":"Думаю, говоря", "hi":"बोलते हुए सोचता/ती हूँ"},
     {"ko":"생각한 뒤 말하는 편이다", "en":"I speak after thinking", "ja":"考えてから話す", "zh":"想好再说", "ru":"Сначала думаю, потом говорю", "hi":"सोचकर बोलता/ती हूँ"}),
    ("SN",
     {"ko":"경험/사실을 믿는 편", "en":"I trust experience/facts", "ja":"経験/事実を信じる", "zh":"更相信经验/事实", "ru":"Верю опыту/фактам", "hi":"अनुभव/तथ्य पर भरोसा"},
     {"ko":"직감/영감을 믿는 편", "en":"I trust intuition", "ja":"直感/ひらめきを信じる", "zh":"更相信直觉", "ru":"Верю интуиции", "hi":"अंतर्ज्ञान पर भरोसा"}),
    ("TF",
     {"ko":"피드백은 직설이 낫다", "en":"Direct feedback is better", "ja":"率直な指摘が良い", "zh":"直接反馈更好", "ru":"Лучше прямо", "hi":"सीधा फीडबैक बेहतर"},
     {"ko":"피드백은 부드럽게가 낫다", "en":"Gentle feedback is better", "ja":"やわらかい方が良い", "zh":"温和反馈更好", "ru":"Лучше мягко", "hi":"नरम फीडबैक बेहतर"}),
    ("JP",
     {"ko":"마감 전에 미리 끝내는 편", "en":"I finish early", "ja":"締切前に終える", "zh":"提前完成", "ru":"Заканчиваю заранее", "hi":"पहले खत्म करता/ती हूँ"},
     {"ko":"마감 직전에 몰아서 하는 편", "en":"I do it near the deadline", "ja":"締切直前にまとめて", "zh":"临近截止再做", "ru":"Делаю перед дедлайном", "hi":"डेडलाइन पर करता/ती हूँ"}),
    ("EI",
     {"ko":"주말엔 약속이 있으면 좋다", "en":"I like weekend plans", "ja":"週末は予定が欲しい", "zh":"周末喜欢安排", "ru":"Хочу планы на выходные", "hi":"वीकेंड प्लान पसंद"},
     {"ko":"주말엔 혼자 쉬고 싶다", "en":"I want to rest alone", "ja":"週末は一人で休みたい", "zh":"周末想独自休息", "ru":"Хочу отдохнуть один/одна", "hi":"अकेले आराम चाहता/ती हूँ"}),
    ("SN",
     {"ko":"설명은 구체적으로", "en":"I prefer concrete details", "ja":"具体的に説明", "zh":"喜欢具体说明", "ru":"Нужны детали", "hi":"ठोस विवरण"},
     {"ko":"설명은 큰그림으로", "en":"I prefer the big picture", "ja":"全体像で説明", "zh":"喜欢大局说明", "ru":"Нужна общая картина", "hi":"बिग पिक्चर"}),
    ("TF",
     {"ko":"갈등은 원인/해결이 우선", "en":"Cause/solution first", "ja":"原因/解決が優先", "zh":"原因/解决优先", "ru":"Причина/решение важнее", "hi":"कारण/समाधान पहले"},
     {"ko":"갈등은 감정/관계가 우선", "en":"Feelings/relationship first", "ja":"感情/関係が優先", "zh":"情绪/关系优先", "ru":"Чувства/отношения важнее", "hi":"भावना/रिश्ता पहले"}),
    ("JP",
     {"ko":"정리/정돈이 잘 되어야 편하다", "en":"I like things organized", "ja":"整理整頓が安心", "zh":"喜欢井然有序", "ru":"Люблю порядок", "hi":"व्यवस्था पसंद"},
     {"ko":"어수선해도 일단 진행 가능", "en":"Messy is fine; keep going", "ja":"多少散らかってもOK", "zh":"乱一点也能推进", "ru":"Хаос терпим, лишь бы шло", "hi":"थोड़ा बिखरा भी चलेगा"}),
]

MBTI_Q_16_EXTRA_L10N = [
    ("EI",
     {"ko":"새로운 사람을 만나면 설렌다", "en":"Meeting new people excites me", "ja":"新しい出会いにワクワクする", "zh":"结识新朋友很兴奋", "ru":"Новые люди вдохновляют", "hi":"नए लोग उत्साहित करते हैं"},
     {"ko":"새로운 사람은 적응 시간이 필요", "en":"I need time to adapt to new people", "ja":"新しい人には慣れる時間が必要", "zh":"需要适应时间", "ru":"Нужно время привыкнуть", "hi":"अभ्यस्त होने में समय चाहिए"}),
    ("SN",
     {"ko":"지금 필요한 현실이 중요", "en":"Current reality matters more", "ja":"今必要な現実が重要", "zh":"当下现实更重要", "ru":"Важнее текущая реальность", "hi":"वर्तमान वास्तविकता महत्वपूर्ण"},
     {"ko":"미래 가능성이 더 중요", "en":"Future possibilities matter more", "ja":"未来の可能性が重要", "zh":"未来可能性更重要", "ru":"Важнее будущие возможности", "hi":"भविष्य की संभावना महत्वपूर्ण"}),
    ("TF",
     {"ko":"공정함이 최우선", "en":"Fairness is top priority", "ja":"公平さが最優先", "zh":"公平最重要", "ru":"Справедливость важнее всего", "hi":"न्याय सबसे ऊपर"},
     {"ko":"조화로움이 최우선", "en":"Harmony is top priority", "ja":"調和が最優先", "zh":"和谐最重要", "ru":"Гармония важнее всего", "hi":"सामंजस्य सबसे ऊपर"}),
    ("JP",
     {"ko":"일정이 확정되어야 안심", "en":"I feel safe when schedules are fixed", "ja":"予定が確定すると安心", "zh":"日程确定更安心", "ru":"Спокойнее при фиксированном плане", "hi":"योजना तय हो तो आराम"},
     {"ko":"상황에 따라 바뀌는 게 자연스러움", "en":"It’s natural for plans to change", "ja":"状況で変わるのが自然", "zh":"计划变化很正常", "ru":"Нормально, если планы меняются", "hi":"बदलाव स्वाभाविक"}),
]

def compute_mbti_from_answers(answers, default="ENFP"):
    scores = {"EI":0, "SN":0, "TF":0, "JP":0}
    counts = {"EI":0, "SN":0, "TF":0, "JP":0}
    for axis, pick_left in answers:
        if axis in scores:
            counts[axis] += 1
            if pick_left:
                scores[axis] += 1

    def decide(axis, left_char, right_char):
        if counts[axis] == 0:
            return left_char
        return left_char if scores[axis] >= (counts[axis]/2) else right_char

    mbti = f"{decide('EI','E','I')}{decide('SN','S','N')}{decide('TF','T','F')}{decide('JP','J','P')}"
    return mbti if mbti in MBTI_DESC else default

def build_mbti_questions(lang: str, mode: str):
    base = []
    for axis, left_map, right_map in MBTI_Q_12_L10N:
        left = left_map.get(lang, left_map.get("en"))
        right = right_map.get(lang, right_map.get("en"))
        base.append((axis, left, right))
    if mode == "16":
        for axis, left_map, right_map in MBTI_Q_16_EXTRA_L10N:
            left = left_map.get(lang, left_map.get("en"))
            right = right_map.get(lang, right_map.get("en"))
            base.append((axis, left, right))
    return base

def render_mbti_test(t, questions, title: str, key_prefix: str):
    st.markdown(f"<div class='card'><b>{title}</b><br><span style='opacity:0.85;'>{t['mbti_test_help']}</span></div>", unsafe_allow_html=True)
    answers = []
    for i, (axis, left_txt, right_txt) in enumerate(questions, start=1):
        choice = st.radio(f"{i}. {axis}", options=[left_txt, right_txt], index=0, key=f"{key_prefix}_{i}")
        answers.append((axis, choice == left_txt))
    if st.button(t["mbti_submit"], use_container_width=True):
        st.session_state.mbti = compute_mbti_from_answers(answers)
        return True
    return False

# =========================================================
# 8) Google Sheet (행 제한 근본 해결 포함)
# =========================================================
def get_sheet():
    try:
        if gspread is None or Credentials is None:
            return None
        if "gcp_service_account" not in st.secrets:
            return None

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        info = dict(st.secrets["gcp_service_account"])
        if "private_key" in info and isinstance(info["private_key"], str):
            info["private_key"] = info["private_key"].replace("\\n", "\n")

        creds = Credentials.from_service_account_info(info, scopes=scopes)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(SPREADSHEET_ID)
        ws = sh.worksheet(SHEET_NAME)
        return ws
    except Exception:
        return None

def read_all_rows(ws):
    try:
        return ws.get_all_values()
    except Exception:
        return []

def ensure_sheet_capacity(ws, need_row_index_1based: int):
    """
    구글시트 'grid limits' 근본 해결:
    - 현재 rows 보다 append 대상 행이 크면 add_rows()로 늘림
    """
    try:
        props = ws.spreadsheet.fetch_sheet_metadata()
        sheet_id = ws._properties.get("sheetId")
        sheets = props.get("sheets", [])
        current_rows = None
        for s in sheets:
            if s.get("properties", {}).get("sheetId") == sheet_id:
                grid = s.get("properties", {}).get("gridProperties", {})
                current_rows = grid.get("rowCount")
                break
        if current_rows is None:
            return
        if need_row_index_1based > current_rows:
            add = max(100, need_row_index_1based - current_rows + 50)
            ws.add_rows(add)
    except Exception:
        # metadata를 못 가져와도 append 시도는 하고, 실패 시 에러가 보이게 둠
        return

def count_winners(ws) -> int:
    values = read_all_rows(ws)
    winners = 0
    for row in values[1:] if len(values) > 1 else []:
        if len(row) < 6:
            continue
        try:
            sec = float(row[4])
        except Exception:
            continue
        if 20.160 <= sec <= 20.169:
            winners += 1
    return winners

def phone_exists(ws, phone_norm: str) -> bool:
    values = read_all_rows(ws)
    for row in values[1:] if len(values) > 1 else []:
        if len(row) < 3:
            continue
        if normalize_phone(row[2]) == phone_norm and phone_norm != "":
            return True
    return False

def append_entry(ws, name, phone, lang, seconds, shared_bool):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    values = read_all_rows(ws)
    next_row = (len(values) + 1) if values else 1
    ensure_sheet_capacity(ws, next_row)
    ws.append_row([now_str, name, phone, lang, f"{seconds:.3f}", str(bool(shared_bool))])

# =========================================================
# 9) Share Button (시스템 공유창만)
# =========================================================
def share_button_native_only(label: str, not_supported_text: str):
    st.components.v1.html(
        f"""
<div style="margin: 8px 0;">
  <button id="btnShare" style="
    width:100%;
    border:none;border-radius:999px;
    padding:12px 14px;
    font-weight:900;
    background:#6b4fd6;color:white;
    cursor:pointer;
  ">{label}</button>
</div>
<script>
(function() {{
  const btn = document.getElementById("btnShare");
  const url = {json.dumps(APP_URL, ensure_ascii=False)};
  const notSupported = {json.dumps(not_supported_text, ensure_ascii=False)};
  btn.addEventListener("click", async () => {{
    if (!navigator.share) {{
      alert(notSupported);
      return;
    }}
    try {{
      await navigator.share({{ title: "2026 Fortune", text: url, url }});
      // 공유 성공 시 보너스 지급
      window.location.href = url + "?shared=1";
    }} catch (e) {{
      // user cancelled → do nothing
    }}
  }});
}})();
</script>
""",
        height=70
    )

# =========================================================
# 10) Stopwatch (스크롤 튐 근본 해결: scrollY 저장/복원)
# =========================================================
def stopwatch_component_auto_fill(note_text: str, tries_left: int):
    disabled = "true" if tries_left <= 0 else "false"
    st.components.v1.html(
        f"""
<div style="
  background: rgba(255,255,255,0.96);
  border-radius: 18px;
  padding: 16px;
  border: 1px solid rgba(140,120,200,0.18);
  box-shadow: 0 10px 28px rgba(0,0,0,0.08);
  text-align:center;
">
  <div style="font-weight:900;font-size:1.15rem;color:#2b2350;margin-bottom:10px;">
    ⏱️ STOPWATCH
  </div>

  <div id="display" style="
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace;
    font-weight:900;
    font-size: 54px;
    letter-spacing: 2px;
    padding: 14px 10px;
    border-radius: 14px;
    background: rgba(245,245,255,0.85);
    border: 1px solid rgba(130,95,220,0.20);
    color: #1f1747;
  ">00:00.000</div>

  <div style="display:flex; gap:10px; justify-content:center; margin-top:12px;">
    <button id="startBtn" style="
      flex:1; max-width: 240px;
      border:none; border-radius: 999px;
      padding: 12px 14px;
      font-weight:900;
      background:#6b4fd6; color:white;
      cursor:pointer;
      opacity: { "0.45" if tries_left <= 0 else "1" };
    ">START</button>

    <button id="stopBtn" style="
      flex:1; max-width: 240px;
      border:none; border-radius: 999px;
      padding: 12px 14px;
      font-weight:900;
      background:#ff8c50; color:white;
      cursor:pointer;
      opacity: { "0.45" if tries_left <= 0 else "1" };
    ">STOP</button>
  </div>

  <div style="margin-top:10px; font-size:0.92rem; opacity:0.85;">
    {note_text}
  </div>
</div>

<script>
(function() {{
  // ✅ 새로고침/리다이렉트 후 스크롤 복원
  try {{
    const saved = sessionStorage.getItem("scrollY_fortune");
    if (saved) {{
      setTimeout(() => window.scrollTo(0, parseInt(saved, 10) || 0), 80);
      sessionStorage.removeItem("scrollY_fortune");
    }}
  }} catch(e) {{}}

  const disabled = {disabled};
  const startBtn = document.getElementById("startBtn");
  const stopBtn = document.getElementById("stopBtn");
  if (disabled) {{
    startBtn.disabled = true;
    stopBtn.disabled = true;
    startBtn.style.cursor = "not-allowed";
    stopBtn.style.cursor = "not-allowed";
    return;
  }}

  let running = false;
  let startTime = 0;
  let rafId = null;
  const display = document.getElementById("display");

  function fmt(ms) {{
    const total = Math.max(0, ms);
    const m = Math.floor(total / 60000);
    const s = Math.floor((total % 60000) / 1000);
    const mm = Math.floor(total % 1000);
    return String(m).padStart(2,'0') + ":" + String(s).padStart(2,'0') + "." + String(mm).padStart(3,'0');
  }}

  function tick() {{
    if (!running) return;
    const now = performance.now();
    display.textContent = fmt(now - startTime);
    rafId = requestAnimationFrame(tick);
  }}

  startBtn.addEventListener("click", () => {{
    running = true;
    startTime = performance.now();
    display.textContent = "00:00.000";
    if (rafId) cancelAnimationFrame(rafId);
    rafId = requestAnimationFrame(tick);
  }});

  stopBtn.addEventListener("click", () => {{
    if (!running) return;
    running = false;
    if (rafId) cancelAnimationFrame(rafId);
    const now = performance.now();
    const elapsedSec = (now - startTime) / 1000.0;
    const v = elapsedSec.toFixed(3);

    try {{
      sessionStorage.setItem("scrollY_fortune", String(window.scrollY || 0));
    }} catch(e) {{}}

    try {{
      const u = new URL(window.location.href);
      u.searchParams.set("t", v);
      window.location.href = u.toString();
    }} catch (e) {{
      window.location.href = {json.dumps(APP_URL, ensure_ascii=False)} + "?t=" + v;
    }}
  }});
}})();
</script>
""",
        height=270
    )

# =========================================================
# 11) Session State
# =========================================================
if "lang" not in st.session_state: st.session_state.lang = "ko"
if "name" not in st.session_state: st.session_state.name = ""
if "y" not in st.session_state: st.session_state.y = 2005
if "m" not in st.session_state: st.session_state.m = 1
if "d" not in st.session_state: st.session_state.d = 1
if "stage" not in st.session_state: st.session_state.stage = "input"
if "mbti" not in st.session_state: st.session_state.mbti = None
if "mbti_mode" not in st.session_state: st.session_state.mbti_mode = "direct"

# 미니게임 상태
if "shared" not in st.session_state: st.session_state.shared = False
if "max_attempts" not in st.session_state: st.session_state.max_attempts = 1
if "attempts_used" not in st.session_state: st.session_state.attempts_used = 0
if "show_win_form" not in st.session_state: st.session_state.show_win_form = False
if "win_seconds" not in st.session_state: st.session_state.win_seconds = None
if "elapsed_input" not in st.session_state: st.session_state.elapsed_input = ""

# ---- shared=1 감지(보너스 1회) ----
qp = get_query_params()
shared_val = qp.get("shared", "0")
if isinstance(shared_val, list):
    shared_val = shared_val[0] if shared_val else "0"
if str(shared_val) == "1":
    if not st.session_state.shared:
        st.session_state.shared = True
        st.session_state.max_attempts = 2
        safe_toast(T["ko"]["share_bonus_done"] if st.session_state.lang == "ko" else "Share bonus applied!")
    clear_param("shared")

# ---- STOP 기록 t= 감지 → 자동 입력칸 채우기 ----
t_val = qp.get("t", None)
if isinstance(t_val, list):
    t_val = t_val[0] if t_val else None
if t_val is not None:
    try:
        _v = float(str(t_val).strip())
        st.session_state.elapsed_input = f"{_v:.3f}"
    except Exception:
        pass
    clear_param("t")

# =========================================================
# 12) Style (디자인 고정)
# =========================================================
st.markdown("""
<style>
.block-container { padding-top: 1.0rem; padding-bottom: 2.5rem; max-width: 720px; }
.card {
  background: rgba(255,255,255,0.96);
  border-radius: 18px;
  padding: 18px 16px;
  box-shadow: 0 10px 28px rgba(0,0,0,0.10);
  border: 1px solid rgba(140,120,200,0.18);
  margin: 12px 0;
}
.header-hero {
  border-radius: 20px;
  padding: 18px 16px;
  background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 50%, #8ec5fc 100%);
  color: white;
  text-align: center;
  box-shadow: 0 12px 30px rgba(0,0,0,0.18);
  margin-bottom: 14px;
}
.hero-title { font-size: 1.5rem; font-weight: 900; margin: 0; }
.hero-sub { font-size: 0.95rem; opacity: 0.95; margin-top: 6px; }
.badge {
  display:inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.85rem;
  background: rgba(255,255,255,0.20);
  border: 1px solid rgba(255,255,255,0.25);
  margin-top: 10px;
}
.soft-box {
  background: rgba(245,245,255,0.78);
  border: 1px solid rgba(130,95,220,0.18);
  padding: 12px 12px;
  border-radius: 14px;
  line-height: 1.65;
  font-size: 1.0rem;
}
.bigbtn > button {
  border-radius: 999px !important;
  font-weight: 900 !important;
  padding: 0.75rem 1.2rem !important;
}
.adbox {
  background: rgba(255,255,255,0.96);
  border-radius: 18px;
  padding: 16px;
  margin: 12px 0;
  border: 2px solid rgba(255, 140, 80, 0.55);
  box-shadow: 0 10px 28px rgba(0,0,0,0.08);
  text-align:center;
}
.adplaceholder {
  background: rgba(255,255,255,0.75);
  border-radius: 18px;
  padding: 14px;
  margin: 12px 0;
  border: 2px dashed rgba(170, 130, 220, 0.55);
  text-align:center;
  color: rgba(60,40,110,0.85);
}
.small-note { font-size: 0.92rem; opacity: 0.88; text-align:center; margin-top: 8px; }
hr.soft { border:0; height:1px; background: rgba(120, 90, 210, 0.15); margin: 14px 0; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 13) Language picker + SEO
# =========================================================
if st.session_state.lang not in T:
    st.session_state.lang = "ko"

lang_labels = [label for _, label in LANGS]
lang_codes = [code for code, _ in LANGS]
current_idx = lang_codes.index(st.session_state.lang) if st.session_state.lang in lang_codes else 0

try:
    picked = st.radio(T[st.session_state.lang]["lang_pick"], lang_labels, index=current_idx, horizontal=True)
except TypeError:
    picked = st.radio(T[st.session_state.lang]["lang_pick"], lang_labels, index=current_idx)

st.session_state.lang = lang_codes[lang_labels.index(picked)]
t = T[st.session_state.lang]
inject_seo(st.session_state.lang)

# =========================================================
# 14) Fortune Data Resolver (임의 생성 금지 / 근본 원인 표시)
# =========================================================
def resolve_fortune_record(lang: str, year: int, mbti: str):
    """
    ✅ 절대 '없으면 생성'하지 않음
    - data/fortunes_{lang}.json을 BOM 대응 로딩
    - ko일 때 combo_key = "{띠}_{MBTI}" (예: 쥐_ISTP)
    - 그 키가 없으면 즉시 에러를 띄워 원인을 보여줌
    """
    path = fortunes_path(lang)
    data = load_json_utf8sig(path)  # ✅ BOM 해결 핵심

    animal_ko = zodiac_ko_from_year(year)
    combo_key = f"{animal_ko}_{mbti}"

    rec = require_combo_record(data, combo_key)

    # 우리가 화면에 쓸 필수 키들(없으면 바로 원인 노출)
    required_keys = [
        "zodiac_fortune", "mbti_trait", "saju_message",
        "today", "tomorrow", "year_2026",
        "love", "money", "work", "health",
        "lucky_point", "action_tip", "caution"
    ]
    missing = [k for k in required_keys if k not in rec]
    if missing:
        raise KeyError(f"record '{combo_key}' missing keys: {missing}")

    return combo_key, rec

def pick_tarot(lang: str):
    key = random.choice(list(TAROT.keys()))
    name_local = TAROT[key]["name"].get(lang, TAROT[key]["name"]["en"])
    meaning_local = TAROT[key]["meaning"].get(lang, TAROT[key]["meaning"]["en"])
    return key, name_local, meaning_local

# =========================================================
# 15) Reset (미니게임 시도/공유는 유지)
# =========================================================
def reset_input_only_keep_minigame():
    keep_keys = {
        "lang",
        "shared", "max_attempts", "attempts_used", "show_win_form", "win_seconds",
        "elapsed_input",
    }
    current = dict(st.session_state)
    st.session_state.clear()
    for k, v in current.items():
        if k in keep_keys:
            st.session_state[k] = v

    st.session_state.name = ""
    st.session_state.y = 2005
    st.session_state.m = 1
    st.session_state.d = 1
    st.session_state.stage = "input"
    st.session_state.mbti = None
    st.session_state.mbti_mode = "direct"

# =========================================================
# 16) Screens
# =========================================================
def render_input():
    st.markdown(f"""
    <div class="header-hero">
      <p class="hero-title">🔮 {t["title"]}</p>
      <p class="hero-sub">{t["subtitle"]}</p>
      <span class="badge">2026</span>
    </div>
    """, unsafe_allow_html=True)

    st.session_state.name = st.text_input(t["name"], value=st.session_state.name)

    st.markdown(f"<div class='card'><b>{t['birth']}</b></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    st.session_state.y = c1.number_input(t["year"], 1900, 2030, st.session_state.y, 1)
    st.session_state.m = c2.number_input(t["month"], 1, 12, st.session_state.m, 1)
    st.session_state.d = c3.number_input(t["day"], 1, 31, st.session_state.d, 1)

    st.markdown(f"<div class='card'><b>{t['mbti_mode']}</b></div>", unsafe_allow_html=True)

    try:
        mode = st.radio(
            "",
            [t["mbti_direct"], t["mbti_12"], t["mbti_16"]],
            index=0 if st.session_state.mbti_mode=="direct" else (1 if st.session_state.mbti_mode=="12" else 2),
            horizontal=True
        )
    except TypeError:
        mode = st.radio(
            "",
            [t["mbti_direct"], t["mbti_12"], t["mbti_16"]],
            index=0 if st.session_state.mbti_mode=="direct" else (1 if st.session_state.mbti_mode=="12" else 2)
        )

    if mode == t["mbti_direct"]:
        st.session_state.mbti_mode = "direct"
    elif mode == t["mbti_12"]:
        st.session_state.mbti_mode = "12"
    else:
        st.session_state.mbti_mode = "16"

    if st.session_state.mbti_mode == "direct":
        idx = MBTI_LIST.index(st.session_state.mbti) if st.session_state.mbti in MBTI_LIST else (MBTI_LIST.index("ENFP") if "ENFP" in MBTI_LIST else 0)
        st.session_state.mbti = st.selectbox("MBTI", MBTI_LIST, index=idx)
    elif st.session_state.mbti_mode == "12":
        questions = build_mbti_questions(st.session_state.lang, "12")
        done = render_mbti_test(t, questions, t["mbti_test_12_title"], "q12")
        if done: st.success(f"MBTI: {st.session_state.mbti}")
    else:
        questions = build_mbti_questions(st.session_state.lang, "16")
        done = render_mbti_test(t, questions, t["mbti_test_16_title"], "q16")
        if done: st.success(f"MBTI: {st.session_state.mbti}")

    st.markdown('<div class="bigbtn">', unsafe_allow_html=True)
    if st.button(t["go_result"], use_container_width=True):
        if not st.session_state.mbti:
            st.session_state.mbti = "ENFP"
        st.session_state.stage = "result"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def render_result():
    lang = st.session_state.lang
    s = t["sections"]

    y = st.session_state.y
    mbti = st.session_state.mbti or "ENFP"

    name = (st.session_state.name or "").strip()
    display_name = f"{name}님" if (lang == "ko" and name) else (name if name else "")

    # ✅ 여기서 데이터 로딩 실패하면 “데이터 없음”으로 뭉개지 않고 원인을 보여줌
    debug_err = None
    debug_combo = None
    rec = None
    try:
        debug_combo, rec = resolve_fortune_record(lang, y, mbti)
    except Exception as e:
        debug_err = str(e)

    st.markdown(f"""
    <div class="header-hero">
      <p class="hero-title">{display_name} {('2026년 운세' if lang=='ko' else '2026 Fortune')}</p>
      <p class="hero-sub">{debug_combo or ''} · {mbti}</p>
      <span class="badge">2026</span>
    </div>
    """, unsafe_allow_html=True)

    if rec is None:
        st.error(t["data_missing"])
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown(f"### {t.get('data_debug_title','Debug')}")
        st.code(f"lang={lang}\nfile={fortunes_path(lang).as_posix()}\nexpected_combo={zodiac_ko_from_year(y)}_{mbti}\nerror={debug_err}")
        st.markdown("</div>", unsafe_allow_html=True)
        # 결과를 못 보여주면 여기서 중단
        if st.button(t["reset"], use_container_width=True):
            reset_input_only_keep_minigame()
            st.rerun()
        st.caption(APP_URL)
        return

    # ✅ 정상 로드된 데이터로만 출력 (임의 메시지 생성 금지)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"**{s['zodiac']}**: {rec['zodiac_fortune']}")
    st.markdown(f"**{s['mbti']}**: {rec['mbti_trait']}")
    st.markdown(f"**{s['saju']}**: {rec['saju_message']}")
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown(f"**{s['today']}**: {rec['today']}")
    st.markdown(f"**{s['tomorrow']}**: {rec['tomorrow']}")
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown(f"**{s['year_all']}**: {rec['year_2026']}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"**{s['love']}**: {rec['love']}")
    st.markdown(f"**{s['money']}**: {rec['money']}")
    st.markdown(f"**{s['work']}**: {rec['work']}")
    st.markdown(f"**{s['health']}**: {rec['health']}")
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)

    lp = rec.get("lucky_point", {})
    if isinstance(lp, dict):
        st.markdown(f"**{s['lucky']}**: color={lp.get('color','')} · item={lp.get('item','')} · number={lp.get('number','')} · direction={lp.get('direction','')}")
    st.markdown(f"**{s['action']}**: {rec.get('action_tip','')}")
    st.markdown(f"**{s['caution']}**: {rec.get('caution','')}")
    st.markdown("</div>", unsafe_allow_html=True)

    # ---- Tarot ----
    if st.button(t["tarot_btn"], use_container_width=True):
        eng_key, local_name, local_meaning = pick_tarot(lang)
        st.markdown(f"""
        <div class="card" style="text-align:center;">
          <div style="font-weight:900;color:#6b4fd6;">{t["tarot_title"]}</div>
          <div style="font-size:1.45rem;font-weight:900;margin-top:6px;">{local_name}</div>
          <div style="opacity:0.75;margin-top:2px;">{eng_key}</div>
          <div style="margin-top:10px;" class="soft-box">{local_meaning}</div>
        </div>
        """, unsafe_allow_html=True)

    # ---- Share (시스템 공유창만) ----
    share_button_native_only(t["share_link_btn"], t.get("share_not_supported", "Share not supported."))
    st.caption(t["share_link_hint"])

    # ---- 광고 위치: 미니게임 바로 위 ----
    st.markdown(f"<div class='adplaceholder'>{t['ad_placeholder']}</div>", unsafe_allow_html=True)
    if lang == "ko":
        st.markdown(f"""
        <div class="adbox">
          <small style="font-weight:900;color:#e74c3c;">광고</small><br>
          <div style="font-size:1.15rem;font-weight:900;margin-top:6px;">{t["ad_kr_title"]}</div>
          <div style="margin-top:6px;">{t["ad_kr_body1"]}</div>
          <div>{t["ad_kr_body2"]}</div>
          <div style="margin-top:10px;">
            <a href="{t["ad_kr_url"]}" target="_blank"
               style="display:inline-block;background:#ff8c50;color:white;
               padding:10px 16px;border-radius:999px;font-weight:900;text-decoration:none;">
              {t["ad_kr_link"]}
            </a>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ---- 미니게임 (한국어만) ----
    if lang == "ko":
        st.markdown(
            f"<div class='card'><div style='font-weight:900;font-size:1.2rem;'>{t['mini_title']}</div>"
            f"<div style='margin-top:8px;' class='soft-box'>{t['mini_desc']}</div></div>",
            unsafe_allow_html=True
        )

        ws = get_sheet()
        sheet_ready = ws is not None
        if not sheet_ready:
            st.warning(t["sheet_fail"])
        else:
            st.success(t["sheet_ok"])

        closed = False
        if sheet_ready:
            try:
                closed = (count_winners(ws) >= 20)
            except Exception:
                closed = False

        tries_left = max(0, st.session_state.max_attempts - st.session_state.attempts_used)
        st.markdown(
            f"<div class='small-note'>{t['mini_try_left']}: <b>{tries_left}</b> / {st.session_state.max_attempts}</div>",
            unsafe_allow_html=True
        )

        if tries_left <= 0:
            st.info(t["no_tries_block"])

        if closed:
            st.info(t["mini_closed"])
        else:
            stopwatch_component_auto_fill(t["stopwatch_note"], tries_left)

            st.text_input(
                t["time_input_label"],
                value=st.session_state.elapsed_input,
                key="elapsed_input"
            )

            if st.button(t["submit_record"], use_container_width=True):
                if tries_left <= 0:
                    st.warning(t["try_over"])
                else:
                    try:
                        elapsed_val = float((st.session_state.elapsed_input or "").strip())
                    except Exception:
                        elapsed_val = None

                    if elapsed_val is None:
                        st.warning("기록이 아직 없습니다. START → STOP을 먼저 눌러주세요.")
                    else:
                        st.session_state.attempts_used += 1
                        st.markdown(f"<div class='card'><b>기록</b>: {elapsed_val:.3f}s</div>", unsafe_allow_html=True)

                        if 20.160 <= elapsed_val <= 20.169:
                            st.session_state.show_win_form = True
                            st.session_state.win_seconds = elapsed_val
                        else:
                            st.info(t["miss"])

            # ✅ 당첨 시에만 전화번호 입력 폼 노출
            if st.session_state.show_win_form and st.session_state.win_seconds is not None:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown(f"### {t['win_title']}")
                st.markdown(f"**기록:** {st.session_state.win_seconds:.3f}s")

                nm = st.text_input(t["win_name"], value=(st.session_state.name or "").strip(), key="win_name_input")
                ph = st.text_input(t["win_phone"], value="", key="win_phone_input")
                ph_norm = normalize_phone(ph)

                consent = st.checkbox(
                    f"{t['win_consent']}  \n{t['win_consent_text']}",
                    value=False,
                    key="consent_chk"
                )

                if st.button(t["win_submit"], use_container_width=True):
                    if not sheet_ready:
                        st.error(t["sheet_fail"])
                    elif not consent:
                        st.warning("동의가 필요합니다.")
                    elif nm.strip() == "" or ph_norm == "":
                        st.warning("이름/전화번호를 정확히 입력해주세요.")
                    else:
                        try:
                            if phone_exists(ws, ph_norm):
                                st.warning(t["mini_dup"])
                            else:
                                if count_winners(ws) >= 20:
                                    st.info(t["mini_closed"])
                                else:
                                    append_entry(ws, nm.strip(), ph_norm, lang, float(st.session_state.win_seconds), st.session_state.shared)
                                    st.success(t["win_thanks"])
                                    st.session_state.show_win_form = False
                                    st.session_state.win_seconds = None
                        except Exception as e:
                            st.error(f"저장 중 오류: {e}")

                st.markdown("</div>", unsafe_allow_html=True)

    # ---- 검색/AI 노출 섹션 ----
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"### {t['faq_title']}")
    if lang == "ko":
        st.markdown("- **2026 운세/띠운세/MBTI 운세/사주/오늘운세/내일운세/타로**를 무료로 제공합니다.")
        st.markdown("- MBTI 성향을 반영해 **연애·재물·일/학업·건강** 조언을 제공합니다.")
        st.markdown("- 한국어 화면에는 선착순 이벤트 미니게임(구글시트 저장)이 포함됩니다.")
    else:
        st.markdown("- Free 2026 zodiac + MBTI advice + saju + today/tomorrow + tarot.")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button(t["reset"], use_container_width=True):
        reset_input_only_keep_minigame()
        st.rerun()

    st.caption(APP_URL)

# =========================================================
# 17) Router
# =========================================================
if st.session_state.stage == "input":
    render_input()
else:
    render_result()
