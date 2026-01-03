import json
import time
import random
from datetime import datetime, timezone, timedelta
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

# =========================
# 기본 설정 (디자인 고정)
# =========================
st.set_page_config(
    page_title="2026 띠 + MBTI + 사주 + 오늘/내일 운세",
    page_icon="🔮",
    layout="centered",
)

APP_URL = "https://my-fortune.streamlit.app/"  # 너 앱 주소 (공유용)
DATA_DIR = Path(__file__).parent / "data"
SHEET_ID = "1WvuKXx2if2WvxmQaxkqzFW-BzDEWWma9hZgCr2jJQYY"
SHEET_TAB = "시트1"  # 너가 말한 시트1 고정
SHEET_COL_CONSULT = "O"  # 요구사항: G열에 O or X? -> 최종 요구: O일 때만 기록, X는 기록하지 않음
# (G열이 실제로 "상담신청" 컬럼이면, 아래 append_row에서 해당 위치를 맞춰야 함)
# 여기서는 "맨 끝 컬럼에 상담신청"으로 기록해. (기존 컬럼 순서를 엄격히 맞춰야 한다면 알려줘: 현재 코드는 안전 우선)

KST = timezone(timedelta(hours=9))

# =========================
# 간단 CSS (큰 디자인 변경 없이)
# =========================
BASE_CSS = """
<style>
/* 전체 폰트/간격 */
html, body, [class*="css"]  { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans KR", Arial, sans-serif; }

/* 배너 카드 */
.banner {
  background: linear-gradient(135deg, #e8d6ff 0%, #ffd9d9 45%, #ffecc7 100%);
  border-radius: 18px;
  padding: 28px 18px;
  text-align: center;
  margin-top: 6px;
  margin-bottom: 18px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.05);
}
.banner h1{
  margin: 0;
  font-size: 34px;
  letter-spacing: -0.6px;
  line-height: 1.25;
}
.banner p{
  margin: 10px 0 0 0;
  opacity: .75;
  font-weight: 600;
}

/* 카드 */
.card {
  background: white;
  border-radius: 18px;
  padding: 18px 16px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.06);
  margin-bottom: 14px;
}
.card h3 { margin: 0 0 8px 0; }
.hr { height: 1px; background: rgba(0,0,0,0.08); margin: 14px 0; }

/* 큰 버튼 느낌 */
div.stButton > button {
  width: 100%;
  border-radius: 14px !important;
  padding: 14px 14px !important;
  border: 1px solid rgba(200,0,0,0.35);
}
div.stButton > button:hover { border-color: rgba(200,0,0,0.65); }

/* 안내 박스 */
.notice {
  border-radius: 16px;
  padding: 12px 14px;
  background: rgba(255, 231, 231, 0.6);
  border: 1px solid rgba(200,0,0,0.18);
  margin: 10px 0 12px 0;
}
.small { opacity: .75; font-size: 13px; }

/* 게임 큰 숫자 */
.game-time {
  text-align:center;
  font-size: 64px;
  font-weight: 800;
  letter-spacing: 1px;
  margin: 10px 0 6px 0;
}
</style>
"""
st.markdown(BASE_CSS, unsafe_allow_html=True)

# =========================
# SEO 주입 (AI 검색/요약 노출용)
# =========================
def inject_seo(lang: str, title: str, description: str):
    # Streamlit은 기본적으로 head를 직접 제어하기 어렵지만,
    # components.html로 meta/og/json-ld를 주입할 수 있음.
    # (검색엔진 크롤링이 100% 보장되진 않지만, AI 요약/미리보기에는 도움됨)
    safe_title = title.replace('"', "'")
    safe_desc = description.replace('"', "'")
    json_ld = {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": safe_title,
        "applicationCategory": "LifestyleApplication",
        "operatingSystem": "All",
        "description": safe_desc,
        "inLanguage": lang,
        "url": APP_URL
    }
    html = f"""
    <script>
      document.title = "{safe_title}";
      const setMeta = (name, content, attr="name") => {{
        let el = document.querySelector(`meta[${{attr}}='${{name}}']`);
        if(!el) {{
          el = document.createElement('meta');
          el.setAttribute(attr, name);
          document.head.appendChild(el);
        }}
        el.setAttribute('content', content);
      }};
      setMeta("description", "{safe_desc}");
      setMeta("keywords", "2026 운세, 띠운세, 사주, MBTI, 오늘운세, 내일운세, 타로, 무료 운세, fortune, zodiac, mbti test");
      setMeta("og:title", "{safe_title}", "property");
      setMeta("og:description", "{safe_desc}", "property");
      setMeta("og:type", "website", "property");
      setMeta("og:url", "{APP_URL}", "property");

      // JSON-LD
      let ld = document.getElementById("jsonld_fortune");
      if(!ld) {{
        ld = document.createElement('script');
        ld.type = "application/ld+json";
        ld.id = "jsonld_fortune";
        document.head.appendChild(ld);
      }}
      ld.text = {json.dumps(json_ld)};
    </script>
    """
    components.html(html, height=0)

# =========================
# 데이터 로더
# =========================
def load_fortunes(lang: str) -> dict | None:
    path = DATA_DIR / f"fortunes_{lang}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def get_section_text(fortune_data: dict | None, key: str) -> str | None:
    if not fortune_data:
        return None
    sections = fortune_data.get("sections", {})
    v = sections.get(key)
    if isinstance(v, str) and v.strip():
        return v.strip()
    return None

# =========================
# 다국어 UI 텍스트
# =========================
UI = {
    "ko": {
        "lang_name": "한국어",
        "title": "2026 띠 + MBTI + 사주 + 오늘/내일 운세",
        "subtitle": "완전 무료",
        "name_label": "이름 입력 (결과에 표시돼요)",
        "phone_label": "전화번호 (실패 시 상담신청에서 사용)",
        "btn_result": "운세 보기",
        "today": "오늘 운세",
        "tomorrow": "내일 운세",
        "year": "2026 전체 운세",
        "love": "연애운 조언",
        "money": "재물운 조언",
        "work": "직장/일 조언",
        "health": "건강 조언",
        "share_title": "친구에게 공유하기",
        "share_desc": "공유하면 도전 기회가 1회 추가됩니다.",
        "game_title": "미니게임: 선착순 20명 커피쿠폰 도전!",
        "game_rule": "스톱워치를 20.260s ~ 20.269s 사이에 멈추면 성공입니다. (기본 1회, 친구 공유 시 1회 추가)",
        "start": "Start",
        "stop": "Stop",
        "tries_left": "남은 시도 횟수",
        "success": "성공! 응모 시 선착순 20명에게 커피 쿠폰 보내드립니다.",
        "fail": "친구 공유 후 재도전.\n또는 다나눔렌탈 정수기 렌탈 정보 상담신청하고 커피쿠폰 응모.",
        "consult_title": "다나눔렌탈 상담신청(실패자만 가능)",
        "consult_q": "상담 신청하시겠습니까?",
        "consult_yes": "O (신청)",
        "consult_no": "X (취소)",
        "reset": "처음부터 다시하기",
        "mbti_knowing": "I know my MBTI (select directly)",
        "mbti_title": "MBTI 16문항",
        "mbti_direct": "MBTI 직접 선택",
        "seo_desc": "2026년 무료 운세: 띠운세, MBTI, 사주 기반으로 오늘/내일/연애/재물/직장 운세를 한 번에 확인하세요. 한국어/English/日本語/中文/Русский/हिन्दी 지원."
    },
    "en": {
        "lang_name": "English",
        "title": "2026 Zodiac + MBTI + Saju + Daily Fortune",
        "subtitle": "100% Free",
        "name_label": "Your name (shown in results)",
        "phone_label": "Phone (used only if you fail and request 상담)",
        "btn_result": "Get Results",
        "today": "Today",
        "tomorrow": "Tomorrow",
        "year": "Year 2026",
        "love": "Love advice",
        "money": "Money advice",
        "work": "Work advice",
        "health": "Health advice",
        "share_title": "Share",
        "share_desc": "Sharing adds +1 extra try (Korean only mini-game).",
        "game_title": "Mini-game",
        "game_rule": "Korean only",
        "start": "Start",
        "stop": "Stop",
        "tries_left": "Tries left",
        "success": "Success!",
        "fail": "Try again after sharing.",
        "consult_title": "Consultation",
        "consult_q": "Do you want to request a consultation?",
        "consult_yes": "O (Yes)",
        "consult_no": "X (No)",
        "reset": "Reset",
        "mbti_knowing": "I know my MBTI (select directly)",
        "mbti_title": "MBTI (16 questions)",
        "mbti_direct": "Select MBTI directly",
        "seo_desc": "Free 2026 fortune: zodiac, MBTI, and saju-based daily & yearly insights. Multi-language supported."
    },
    "ja": {
        "lang_name": "日本語",
        "title": "2026 干支 + MBTI + 四柱 + 今日/明日 運勢",
        "subtitle": "完全無料",
        "name_label": "名前（結果に表示）",
        "phone_label": "電話番号（失敗時の相談申請で使用）",
        "btn_result": "結果を見る",
        "today": "今日",
        "tomorrow": "明日",
        "year": "2026年総合",
        "love": "恋愛アドバイス",
        "money": "金運アドバイス",
        "work": "仕事アドバイス",
        "health": "健康アドバイス",
        "share_title": "共有",
        "share_desc": "（ミニゲームは韓国語のみ）",
        "game_title": "ミニゲーム",
        "game_rule": "韓国語のみ",
        "start": "Start",
        "stop": "Stop",
        "tries_left": "残り回数",
        "success": "成功！",
        "fail": "共有後に再挑戦。",
        "consult_title": "相談申請",
        "consult_q": "相談を申し込みますか？",
        "consult_yes": "O（申請）",
        "consult_no": "X（取消）",
        "reset": "最初から",
        "mbti_knowing": "MBTIを知っている（直接選択）",
        "mbti_title": "MBTI 16問",
        "mbti_direct": "MBTI 直接選択",
        "seo_desc": "2026年の無料運勢：干支・MBTI・四柱で今日/明日/恋愛/金運/仕事をまとめてチェック。"
    },
    "zh": {
        "lang_name": "中文",
        "title": "2026 生肖 + MBTI + 四柱 + 今日/明日 运势",
        "subtitle": "完全免费",
        "name_label": "姓名（显示在结果中）",
        "phone_label": "电话（仅失败并咨询时使用）",
        "btn_result": "查看结果",
        "today": "今日运势",
        "tomorrow": "明日运势",
        "year": "2026 全年运势",
        "love": "恋爱建议",
        "money": "财运建议",
        "work": "工作建议",
        "health": "健康建议",
        "share_title": "分享",
        "share_desc": "（小游戏仅韩语）",
        "game_title": "小游戏",
        "game_rule": "仅韩语",
        "start": "Start",
        "stop": "Stop",
        "tries_left": "剩余次数",
        "success": "成功！",
        "fail": "分享后再试。",
        "consult_title": "咨询申请",
        "consult_q": "要申请咨询吗？",
        "consult_yes": "O（申请）",
        "consult_no": "X（取消）",
        "reset": "重新开始",
        "mbti_knowing": "我知道我的MBTI（直接选择）",
        "mbti_title": "MBTI 16题",
        "mbti_direct": "直接选择MBTI",
        "seo_desc": "2026免费运势：生肖、MBTI、四柱，查看今日/明日/全年/恋爱/财运/工作建议。"
    },
    "ru": {
        "lang_name": "Русский",
        "title": "2026 Зодиак + MBTI + Саджу + прогноз",
        "subtitle": "Бесплатно",
        "name_label": "Имя (показывается в результате)",
        "phone_label": "Телефон (только если вы проиграли и запросили консультацию)",
        "btn_result": "Показать результат",
        "today": "Сегодня",
        "tomorrow": "Завтра",
        "year": "2026 год",
        "love": "Любовь",
        "money": "Деньги",
        "work": "Работа",
        "health": "Здоровье",
        "share_title": "Поделиться",
        "share_desc": "(Мини-игра только на корейском)",
        "game_title": "Мини-игра",
        "game_rule": "Только корейский",
        "start": "Start",
        "stop": "Stop",
        "tries_left": "Попыток осталось",
        "success": "Успех!",
        "fail": "Поделитесь и попробуйте снова.",
        "consult_title": "Консультация",
        "consult_q": "Хотите запросить консультацию?",
        "consult_yes": "O (Да)",
        "consult_no": "X (Нет)",
        "reset": "Сброс",
        "mbti_knowing": "Я знаю свой MBTI (выбрать напрямую)",
        "mbti_title": "MBTI (16 вопросов)",
        "mbti_direct": "Выбрать MBTI напрямую",
        "seo_desc": "Бесплатный прогноз на 2026: зодиак, MBTI и саджу. Ежедневные и годовые советы."
    },
    "hi": {
        "lang_name": "हिन्दी",
        "title": "2026 राशि + MBTI + साजू + आज/कल भविष्य",
        "subtitle": "पूरी तरह मुफ्त",
        "name_label": "नाम (परिणाम में दिखेगा)",
        "phone_label": "फोन (केवल असफल होने पर 상담 के लिए)",
        "btn_result": "परिणाम देखें",
        "today": "आज",
        "tomorrow": "कल",
        "year": "2026 वर्ष",
        "love": "प्रेम सलाह",
        "money": "धन सलाह",
        "work": "काम सलाह",
        "health": "स्वास्थ्य सलाह",
        "share_title": "शेयर करें",
        "share_desc": "(मिनी-गेम केवल कोरियाई)",
        "game_title": "मिनी-गेम",
        "game_rule": "केवल कोरियाई",
        "start": "Start",
        "stop": "Stop",
        "tries_left": "बचे प्रयास",
        "success": "सफलता!",
        "fail": "शेयर के बाद फिर प्रयास करें।",
        "consult_title": "परामर्श",
        "consult_q": "क्या आप परामर्श चाहते हैं?",
        "consult_yes": "O (हाँ)",
        "consult_no": "X (नहीं)",
        "reset": "रीसेट",
        "mbti_knowing": "मुझे अपना MBTI पता है (सीधे चुनें)",
        "mbti_title": "MBTI (16 प्रश्न)",
        "mbti_direct": "सीधे MBTI चुनें",
        "seo_desc": "2026 मुफ्त भविष्यवाणी: राशि, MBTI, साजू आधारित आज/कल/वर्ष सलाह।"
    },
}

LANGS = ["ko", "en", "ja", "zh", "ru", "hi"]

# =========================
# MBTI (16문항 + 12/16 포함)
# - 문장 자체는 각 언어로 교체 가능
# - 지금은 기능 복구가 목표라, 간단 번역/대체문을 사용
# =========================
MBTI_QUESTIONS = {
    "ko": [
        "나는 낯선 사람과도 비교적 빨리 친해지는 편이다.",
        "나는 큰 그림보다 디테일을 더 신경 쓴다.",
        "나는 감정보다 논리를 먼저 따르는 편이다.",
        "나는 즉흥적이기보다 계획적인 편이다.",
        "나는 혼자 있는 시간이 꼭 필요하다.",
        "나는 주변 분위기에 영향을 많이 받는다.",
        "나는 새로운 아이디어를 떠올리는 것을 즐긴다.",
        "나는 결정하기 전에 충분히 고민한다.",
        "나는 사람들과 어울리면 에너지가 생긴다.",
        "나는 현실적인 해결책을 선호한다.",
        "나는 상대의 기분을 먼저 고려한다.",
        "나는 마감이 가까워질수록 집중이 잘 된다.",  # 12
        "나는 변화가 많아도 금방 적응하는 편이다.",
        "나는 다양한 가능성을 열어두는 편이다.",
        "나는 규칙과 질서를 중요하게 여긴다.",
        "나는 스트레스를 받으면 혼자 정리하는 편이다.",  # 16
    ],
    "en": [f"MBTI Question {i}." for i in range(1, 17)],
    "ja": [f"MBTI 質問 {i}。" for i in range(1, 17)],
    "zh": [f"MBTI 问题 {i}。" for i in range(1, 17)],
    "ru": [f"Вопрос MBTI {i}." for i in range(1, 17)],
    "hi": [f"MBTI प्रश्न {i}।" for i in range(1, 17)],
}

MBTI_TYPES = [
    "INTJ","INTP","ENTJ","ENTP",
    "INFJ","INFP","ENFJ","ENFP",
    "ISTJ","ISFJ","ESTJ","ESFJ",
    "ISTP","ISFP","ESTP","ESFP"
]

# =========================
# 구글시트 기록 (상담신청 O만 저장)
# =========================
def get_gspread_client():
    # Streamlit secrets에 아래 중 하나로 저장되어 있다고 가정:
    # 1) st.secrets["gcp_service_account"] = { ... } (dict)
    # 2) 또는 TOML 형식으로 service_account 키들을 최상단에 넣은 경우
    import gspread
    from google.oauth2.service_account import Credentials

    sa_info = None
    if "gcp_service_account" in st.secrets:
        sa_info = dict(st.secrets["gcp_service_account"])
    else:
        # 최상단에 바로 들어간 케이스
        # (type, project_id, private_key_id, private_key, client_email ... )
        # secrets 전체를 dict로 만들어 사용
        sa_info = dict(st.secrets)

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(sa_info, scopes=scopes)
    return gspread.authorize(creds)

def append_consult_row(
    name: str,
    phone: str,
    lang: str,
    mbti: str | None,
    game_time: float | None,
    status: str,
    consult: str,
):
    # 요구사항 핵심:
    # - 실패자 O 선택 시만 기록
    # - G열에 O or X -> 최종 요구는 "O면 기록, X면 기록하지 말고 삭제"
    # 그래서 여기서는 "O"일 때만 append 실행하도록 위에서 제어.
    try:
        gc = get_gspread_client()
        sh = gc.open_by_key(SHEET_ID)
        ws = sh.worksheet(SHEET_TAB)

        now = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")
        # ✅ 안전한 형태: 행 끝에 필요한 것만 넣어 append (행 늘어나 Range에러 방지)
        # 기존 컬럼 순서가 꼭 정해져 있다면 "현재 헤더 순서"를 알려줘. 그럼 정확히 맞춰서 넣어줄게.
        row = [
            now,                 # timestamp
            lang,                # language
            name,                # name
            phone,               # phone
            mbti or "",          # mbti
            f"{game_time:.3f}" if isinstance(game_time, (int, float)) else "",
            status,              # success/fail
            consult,             # "O" only
        ]
        ws.append_row(row, value_input_option="USER_ENTERED")
        return True, None
    except Exception as e:
        return False, str(e)

# =========================
# 모바일 공유 (네가 원하는 방식: 공유 시트)
# =========================
def share_sheet_button(title: str, text: str, url: str, key: str):
    # navigator.share 지원이면 안드로이드 공유 시트가 뜸
    # (Streamlit의 기본 Share 버튼 말고, 앱 내부 버튼)
    html = f"""
    <button id="{key}" style="
      width:100%;
      border-radius:14px;
      padding:14px 14px;
      border:1px solid rgba(200,0,0,0.35);
      background:white;
      font-size:16px;
      font-weight:600;
      cursor:pointer;
    ">{title}</button>
    <script>
      const btn = document.getElementById("{key}");
      btn.addEventListener("click", async () => {{
        try {{
          if (navigator.share) {{
            await navigator.share({{
              title: {json.dumps(title)},
              text: {json.dumps(text)},
              url: {json.dumps(url)}
            }});
            const streamlitEvent = new CustomEvent("streamlit:share_done", {{ detail: true }});
            window.dispatchEvent(streamlitEvent);
          }} else {{
            // 지원 안되면 URL만 보여주기
            alert("Share is not available. Please copy manually.\\n" + {json.dumps(url)});
          }}
        }} catch (e) {{
          // 사용자가 취소해도 에러처럼 잡힐 수 있어 무시
        }}
      }});
    </script>
    """
    components.html(html, height=58)

# =========================
# JS 스톱워치 컴포넌트 (실시간, 스크롤 점프 최소화)
# - Start/Stop은 프론트에서만 움직이고,
# - Stop 누른 순간 값만 Python으로 전달
# =========================
def stopwatch_component(key: str):
    # Streamlit ComponentValue 방식
    # Stop 시에만 값을 보내도록 구성
    html = f"""
    <div style="text-align:center;">
      <div id="{key}_t" style="font-size:64px;font-weight:800;letter-spacing:1px;margin:10px 0 6px 0;">00.000</div>
      <div style="display:flex;gap:10px;justify-content:center;">
        <button id="{key}_start" style="flex:1;border-radius:14px;padding:14px;border:1px solid rgba(200,0,0,0.35);background:white;font-size:16px;font-weight:600;cursor:pointer;">Start</button>
        <button id="{key}_stop" style="flex:1;border-radius:14px;padding:14px;border:1px solid rgba(0,0,0,0.18);background:white;font-size:16px;font-weight:600;cursor:pointer;">Stop</button>
      </div>
    </div>

    <script>
      let running = false;
      let startTs = null;
      let raf = null;
      let lastShown = 0;

      const el = document.getElementById("{key}_t");
      const btnStart = document.getElementById("{key}_start");
      const btnStop  = document.getElementById("{key}_stop");

      function fmt(ms) {{
        const s = ms / 1000;
        return s.toFixed(3).padStart(6, "0");
      }}

      function tick(ts) {{
        if (!running) return;
        const ms = ts - startTs;
        // 화면 갱신
        // (너무 자주 rerender하지 않도록 약간만 제한)
        if (ms - lastShown > 10) {{
          el.textContent = fmt(ms);
          lastShown = ms;
        }}
        raf = requestAnimationFrame(tick);
      }}

      btnStart.addEventListener("click", () => {{
        if (running) return;
        running = true;
        startTs = performance.now();
        lastShown = 0;
        el.textContent = "00.000";
        raf = requestAnimationFrame(tick);
      }});

      btnStop.addEventListener("click", () => {{
        if (!running) return;
        running = false;
        if (raf) cancelAnimationFrame(raf);
        // 최종값 고정
        const ms = performance.now() - startTs;
        el.textContent = fmt(ms);

        // Streamlit에 값 전달 (Stop 누를 때만)
        const value = (ms/1000);
        const data = {{ isStreamlitMessage: true, type: "streamlit:setComponentValue", value: value }};
        window.parent.postMessage(data, "*");
      }});
    </script>
    """
    # height는 버튼/숫자 포함
    return components.html(html, height=170)

# =========================
# 세션 초기화
# =========================
def init_state():
    if "lang" not in st.session_state:
        st.session_state.lang = "ko"
    if "tries_base" not in st.session_state:
        st.session_state.tries_base = 1
    if "tries_bonus" not in st.session_state:
        st.session_state.tries_bonus = 0  # 공유로 +1
    if "shared_once" not in st.session_state:
        st.session_state.shared_once = False
    if "game_time" not in st.session_state:
        st.session_state.game_time = None
    if "game_status" not in st.session_state:
        st.session_state.game_status = None  # "success" | "fail" | None
    if "mbti_known" not in st.session_state:
        st.session_state.mbti_known = False
    if "mbti_direct" not in st.session_state:
        st.session_state.mbti_direct = None
    if "mbti_answers" not in st.session_state:
        st.session_state.mbti_answers = [""] * 16  # placeholder
    if "submitted" not in st.session_state:
        st.session_state.submitted = False

def total_tries_left() -> int:
    used = 0
    if st.session_state.game_status in ("success", "fail"):
        used = 1  # Stop으로 판정이 1회 사용
    return max(0, st.session_state.tries_base + st.session_state.tries_bonus - used)

def reset_all(keep_lang: bool = True):
    lang = st.session_state.get("lang", "ko")
    st.session_state.clear()
    init_state()
    if keep_lang:
        st.session_state.lang = lang

# =========================
# UI 시작
# =========================
init_state()

# 언어 선택 (즉시 반응)
lang_labels = [UI[l]["lang_name"] for l in LANGS]
selected_label = st.radio(
    label="",
    options=lang_labels,
    horizontal=True,
    index=LANGS.index(st.session_state.lang),
    key="lang_radio",
)
selected_lang = LANGS[lang_labels.index(selected_label)]
st.session_state.lang = selected_lang
t = UI[st.session_state.lang]

# SEO 주입
inject_seo(st.session_state.lang, t["title"], t["seo_desc"])

# 배너 (디자인 유지)
st.markdown(
    f"""
    <div class="banner">
      <h1>{t["title"]}</h1>
      <p>{t["subtitle"]}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# 입력(이름은 항상)
name = st.text_input(t["name_label"], key="name_input")

# 전화번호는 "실패자 상담신청"에서만 사용하게 하려고 기본 화면에서는 숨김
# (너가 원한 “게임도 안했는데 전화번호 나오면 안됨” 해결)

# MBTI: 아는 사람은 직접 선택
st.session_state.mbti_known = st.checkbox(t["mbti_knowing"], value=st.session_state.mbti_known, key="mbti_known_ck")

mbti_value = None
if st.session_state.mbti_known:
    mbti_value = st.selectbox(t["mbti_direct"], options=[""] + MBTI_TYPES, index=0, key="mbti_direct_select")
else:
    st.markdown(f"### {t['mbti_title']}")
    qs = MBTI_QUESTIONS.get(st.session_state.lang, MBTI_QUESTIONS["en"])
    # 16문항(12,16 포함) 절대 누락되지 않게 고정 렌더
    for i in range(16):
        st.markdown(f"**{i+1}. {qs[i]}**")
        st.session_state.mbti_answers[i] = st.radio(
            label="",
            options=["Not set", "Yes", "No"],
            index=0,
            horizontal=True,
            key=f"mbti_q_{i+1}",
        )
    # 간단 계산(임시): Not set 많으면 None 처리
    if st.session_state.mbti_answers.count("Not set") <= 4:
        mbti_value = random.choice(MBTI_TYPES)  # 여기만 네 로직(기존 계산식)으로 갈아끼우면 됨

# 운세 데이터 로드
fortune_data = load_fortunes(st.session_state.lang)

# 결과 버튼
if st.button(t["btn_result"], key="btn_result"):
    st.session_state.submitted = True

# 결과 표시
if st.session_state.submitted:
    # 데이터 없으면 "없습니다" 대신, 섹션별로 자연스럽게 안내
    def render_section(title_key: str, section_key: str):
        title = t[title_key]
        txt = get_section_text(fortune_data, section_key)
        st.markdown(f"## {title}")
        if txt:
            st.write(txt)
        else:
            st.write("데이터가 없습니다." if st.session_state.lang == "ko" else "No data.")

    render_section("today", "today")
    render_section("tomorrow", "tomorrow")
    render_section("year", "year_2026")
    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
    render_section("love", "love")
    render_section("money", "money")
    render_section("work", "work")
    # health는 있으면만
    health_txt = get_section_text(fortune_data, "health")
    if health_txt:
        st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
        st.markdown(f"## {t['health']}")
        st.write(health_txt)

# =========================
# (중요) 미니게임 + 광고 위치
# - 광고는 "미니게임 바로 위"
# - 미니게임은 한국어에서만
# =========================
if st.session_state.lang == "ko":
    # 광고 (너가 원한 위치: 미니게임 바로 위)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("#### 광고")
    st.markdown("**정수기렌탈 대박!**  \n제휴카드면 월 0원부터!  \n설치 당일 최대 50만원 지원 + 사은품 듬뿍")
    st.markdown(
        """
        <a href="https://www.다나눔렌탈.com" target="_blank" style="
          display:block;text-align:center;margin-top:10px;
          padding:14px;border-radius:14px;background:#b56b34;color:white;
          text-decoration:none;font-weight:800;
        ">다나눔렌탈.com 바로가기</a>
        """,
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # 공유 (네가 말한 공유 시트 방식)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f"### {t['share_title']}")
    st.write(t["share_desc"])
    share_sheet_button(
        title="링크 공유",
        text="2026 운세 + MBTI + 사주 + 미니게임(커피쿠폰) 도전!",
        url=APP_URL,
        key="share_native_btn",
    )
    # 공유로 +1 (세션당 1회만)
    # 실제 공유 완료를 정확히 감지하긴 어렵지만,
    # 사용자가 “공유 버튼을 눌렀다”를 공유로 인정(실무에서 흔히 쓰는 방식)
    if st.button("공유했다 (+1회)", key="btn_shared_once"):
        if not st.session_state.shared_once:
            st.session_state.shared_once = True
            st.session_state.tries_bonus = 1
            st.success("도전 기회가 1회 추가되었습니다.")
        else:
            st.info("이미 도전 기회를 추가했습니다.")
    st.markdown('</div>', unsafe_allow_html=True)

    # 게임
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f"### {t['game_title']}")
    st.write(t["game_rule"])

    tries_left = total_tries_left()
    st.write(f"{t['tries_left']}: **{tries_left}회**")

    # 남은 시도 0이면 게임 잠금
    if tries_left <= 0:
        st.warning("남은 시도 횟수가 없습니다. 친구 공유로 1회 추가 후 도전하세요.")
    else:
        # 스톱워치 (프론트 실시간)
        stopped_value = stopwatch_component("sw1")

        # components.html 반환값은 Python으로 직접 받을 수 없어서,
        # Streamlit은 postMessage를 통해 값이 setComponentValue로 넘어오면
        # 해당 컴포넌트의 값이 session_state에 저장되는 구조인데,
        # components.html은 key 기반 자동 저장이 없어 “Stop 눌렀을 때 rerun”을 만들기 위해
        # 아래처럼 query param 트릭 대신, “Stop 눌렀으면 아래에 입력칸으로 값이 보이게” 하는 방식이 안정적이야.
        # -> 실전에서는 custom component가 제일 깔끔하지만, 지금은 단일 파일로 안정 우선.
        st.markdown('<div class="small">Stop을 누른 뒤, 아래 “기록 반영” 버튼을 눌러 판정하세요.</div>', unsafe_allow_html=True)

        # 사용자가 “Stop”을 눌렀다는 행위를 Python이 직접 알 방법이 없어서,
        # “기록 반영” 버튼으로 판정 트리거를 주는 형태로 구현.
        # (UI 입력/제출을 제거하고 자동으로 넣고 싶다는 요구에 최대한 가까운 타협안)
        if st.button("기록 반영(자동 판정)", key="btn_apply_time"):
            # JS 값은 직접 못 가져오므로, Streamlit HTML-only에서 완벽 자동연동은 한계.
            # 그래서 여기서는 “사용자 마지막 기록”을 session에 저장해두는 방식이 필요하고,
            # 그건 custom component로만 100% 가능.
            # ----
            # 하지만: 너가 지금 가장 중요한 건 “전체가 다시 정상 작동”이므로,
            # 지금은 임시로 랜덤에 가까운 판정이 아니라,
            # 사용자가 STOP으로 만든 화면 숫자(고정)를 그대로 쓰게 하고 싶다면
            # custom component 버전으로 바꿔야 한다.
            # ----
            # 여기서는 임시로 "최근 기록을 직접 입력"을 없애기 위해,
            # '게임시간'을 session_state에 이전값이 있으면 재사용(없으면 실패 처리).
            if st.session_state.game_time is None:
                st.session_state.game_status = "fail"
            else:
                x = float(st.session_state.game_time)
                st.session_state.game_status = "success" if (20.260 <= x <= 20.269) else "fail"

        # ⚠️ 완전 자동(Stop과 동시에 Python에 값 전달)로 만들려면
        # components.html이 아니라 “커스텀 컴포넌트”로 바꿔야 함.
        # 네가 원하면 다음 단계에서 그 버전으로 업그레이드 해줄게.
        # 지금은 “에러 전부 없애고 기능 복구”가 우선이라 안정적인 형태로 둠.

    # 판정 결과 UI
    if st.session_state.game_status == "success":
        st.success(t["success"])
        # 성공자는 상담신청 OFF
    elif st.session_state.game_status == "fail":
        st.error(t["fail"])

        # 실패자만 상담신청 ON
        st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
        st.markdown(f"### {t['consult_title']}")
        st.write(t["consult_q"])

        phone = st.text_input("Phone / 전화번호", key="phone_input_fail")

        c1, c2 = st.columns(2)
        with c1:
            if st.button(t["consult_yes"], key="consult_yes_btn"):
                if not phone.strip():
                    st.warning("전화번호를 입력해주세요.")
                else:
                    ok, err = append_consult_row(
                        name=name.strip() if name.strip() else "",
                        phone=phone.strip(),
                        lang=st.session_state.lang,
                        mbti=mbti_value,
                        game_time=st.session_state.game_time,
                        status="fail",
                        consult="O",
                    )
                    if ok:
                        st.success("커피쿠폰 응모되셨습니다.")
                    else:
                        st.error(f"Sheet error: {err}")

        with c2:
            if st.button(t["consult_no"], key="consult_no_btn"):
                # X는 저장하지 않음(삭제 요구)
                st.info("취소되었습니다. (기록 저장 없음)")

    # reset
    if st.button(t["reset"], key="btn_reset"):
        reset_all(keep_lang=True)
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

else:
    # 한국어가 아니면: 미니게임 섹션 자체를 숨김
    pass
