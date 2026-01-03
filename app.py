# app.py
import json
import os
import random
import time
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st
import streamlit.components.v1 as components

# =========================
# 기본 설정
# =========================
KST = timezone(timedelta(hours=9))

APP_URL = "https://my-fortune.streamlit.app"  # 네 앱 주소 (그대로 유지)
SPREADSHEET_ID = "1WvuKXx2if2WvxmQaxkqzFW-BzDEWWma9hZgCr2jJQYY"
SHEET_NAME = "시트1"

TARGET_MIN = 20.260
TARGET_MAX = 20.269
MAX_WINNERS = 20

SUPPORTED_LANGS = [
    ("ko", "한국어"),
    ("en", "English"),
    ("ja", "日本語"),
    ("zh", "中文"),
    ("ru", "Русский"),
    ("hi", "हिन्दी"),
]

DATA_DIR = "data"
FORTUNE_FILE_BY_LANG = {
    "ko": os.path.join(DATA_DIR, "fortunes_ko.json"),
    "en": os.path.join(DATA_DIR, "fortunes_en.json"),
    "ja": os.path.join(DATA_DIR, "fortunes_ja.json"),
    "zh": os.path.join(DATA_DIR, "fortunes_zh.json"),
    "ru": os.path.join(DATA_DIR, "fortunes_ru.json"),
    "hi": os.path.join(DATA_DIR, "fortunes_hi.json"),
}

# =========================
# 디자인: 절대 바꾸지 않기(최소 CSS만)
# =========================
BASE_CSS = """
<style>
.main .block-container { max-width: 720px; padding-top: 18px; padding-bottom: 60px; }

div.stButton > button {
  width: 100%;
  border-radius: 14px;
  padding: 14px 16px;
  font-weight: 700;
}

.section-title{
  font-size: 20px;
  font-weight: 800;
  margin: 14px 0 8px 0;
}

.game-card{
  background: #ffffff;
  border: 1px solid rgba(0,0,0,0.08);
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.06);
}

.stopwatch{
  font-size: 44px;
  font-weight: 900;
  letter-spacing: 1px;
  text-align: center;
  padding: 10px 0 4px 0;
}

.ad-box{
  border: 2px solid rgba(255, 153, 0, 0.55);
  border-radius: 16px;
  padding: 16px;
  text-align: center;
  margin: 16px 0 12px 0;
}
.ad-badge{
  display:inline-block;
  font-size: 12px;
  font-weight: 800;
  color: #B54708;
  border: 1px solid rgba(181,71,8,0.3);
  padding: 2px 8px;
  border-radius: 999px;
  margin-bottom: 8px;
}
.ad-title{ font-size: 22px; font-weight: 900; margin: 4px 0 6px 0; }
.ad-desc{ font-size: 14px; color: rgba(0,0,0,0.75); line-height: 1.35; margin-bottom: 10px; }
.ad-btn{
  display:inline-block;
  text-decoration:none;
  background:#FF8A00;
  color:#fff !important;
  padding: 12px 16px;
  border-radius: 12px;
  font-weight: 900;
}
.ad-btn:active, .ad-btn:hover{ opacity:0.95; }

/* SEO 텍스트는 사람 눈에 안 띄게(스팸처럼 과도하지 않게) */
.seo-hidden{
  position:absolute;
  left:-9999px;
  top:auto;
  width:1px;
  height:1px;
  overflow:hidden;
}
</style>
"""

# 스크롤 튐 방지(버튼 눌러도 위로 안 튀게)
SCROLL_FIX_JS = """
<script>
(function(){
  try{
    document.addEventListener('click', function(){
      localStorage.setItem('st_scroll_y', String(window.scrollY || 0));
    }, true);

    window.addEventListener('load', function(){
      const y = parseInt(localStorage.getItem('st_scroll_y') || "0", 10);
      setTimeout(()=>{ window.scrollTo(0, y); }, 80);
    });
  }catch(e){}
})();
</script>
"""


# =========================
# SEO/AI 검색 노출 섹션 (삭제되면 안 됨)
# =========================
def inject_seo(lang: str):
    title = {
        "ko": "2026 운세 | 띠 + MBTI + 사주 + 오늘/내일 운세",
        "en": "2026 Fortune | Zodiac + MBTI + Saju + Daily/Tomorrow",
        "ja": "2026年 運勢 | 干支 + MBTI + 四柱 + 今日/明日",
        "zh": "2026 运势 | 生肖 + MBTI + 四柱 + 今日/明日",
        "ru": "Гороскоп 2026 | Зодиак + MBTI + Саджу + Сегодня/Завтра",
        "hi": "2026 भाग्य | राशि + MBTI + साजू + आज/कल",
    }.get(lang, "2026 Fortune")

    desc = {
        "ko": "2026년 띠운세, MBTI, 사주 기반으로 오늘/내일 운세와 2026 전체 운세를 확인하고 미니게임 커피쿠폰 이벤트에 참여하세요.",
        "en": "Check 2026 fortune based on zodiac, MBTI and saju. Daily & tomorrow messages, plus a mini-game event.",
        "ja": "干支・MBTI・四柱で2026年の運勢をチェック。今日/明日メッセージとミニゲームイベント。",
        "zh": "基于生肖、MBTI、四柱，查看2026运势。包含今日/明日运势与小游戏活动。",
        "ru": "Узнайте прогноз на 2026 по зодиаку, MBTI и саджу. Сообщения на сегодня/завтра и мини-игра.",
        "hi": "राशि, MBTI और साजू के आधार पर 2026 भाग्य देखें। आज/कल संदेश और मिनी-गेम।",
    }.get(lang, "Fortune app")

    # JSON-LD (AI 검색에도 도움이 되는 구조화 데이터)
    json_ld = {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": title,
        "url": APP_URL,
        "applicationCategory": "LifestyleApplication",
        "operatingSystem": "Web",
        "description": desc,
        "inLanguage": lang,
    }

    meta_html = f"""
    <script type="application/ld+json">{json.dumps(json_ld, ensure_ascii=False)}</script>
    <meta name="description" content="{desc}"/>
    <meta property="og:title" content="{title}"/>
    <meta property="og:description" content="{desc}"/>
    <meta property="og:url" content="{APP_URL}"/>
    <meta name="twitter:card" content="summary"/>
    """
    components.html(meta_html, height=0)


def render_seo_hidden_text():
    # 과도하게 길면 스팸처럼 보일 수 있어서 핵심 키워드만
    keywords = """
    2026 운세, 2026년 운세, 띠운세, 띠 운세, MBTI 운세, 사주 운세, 오늘 운세, 내일 운세, 2026 전체 운세,
    zodiac fortune 2026, mbti fortune, saju fortune, daily fortune, tomorrow fortune,
    2026年 運勢, 干支 運勢, 四柱 運勢, 今日 運勢, 明日 運勢,
    2026 运势, 生肖 运势, 四柱 运势, 今日 运势, 明日 运势,
    гороскоп 2026, судьба 2026, आज का भाग्य, कल का भाग्य
    """
    st.markdown(f"<div class='seo-hidden'>{keywords}</div>", unsafe_allow_html=True)


# =========================
# Query params 호환(에러 방지)
# =========================
def get_query_params() -> Dict[str, List[str]]:
    try:
        # 구버전/호환
        return st.experimental_get_query_params()
    except Exception:
        return {}


def set_query_params(**kwargs):
    try:
        st.experimental_set_query_params(**kwargs)
    except Exception:
        pass


# =========================
# 데이터 로딩/파싱 (데이터 없음 해결)
# =========================
@st.cache_data(show_spinner=False)
def load_json_file(path: str) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _first_non_empty(*vals):
    for v in vals:
        if v is None:
            continue
        if isinstance(v, str) and v.strip() == "":
            continue
        return v
    return None


def normalize_fortune_record(raw: Any) -> Dict[str, str]:
    """
    fortunes_XX.json이 어떤 구조든 최대한 맞춰서
    today/tomorrow/year/love/money/work/health 키로 변환
    """
    out = {
        "today": "",
        "tomorrow": "",
        "year": "",
        "love": "",
        "money": "",
        "work": "",
        "health": "",
    }

    if raw is None:
        return out

    # raw가 dict일 때
    if isinstance(raw, dict):
        # 흔한 키들 폭넓게 지원
        out["today"] = str(_first_non_empty(
            raw.get("today"),
            raw.get("daily"),
            raw.get("daily_message"),
            raw.get("today_message"),
            raw.get("message_today"),
        ) or "")

        out["tomorrow"] = str(_first_non_empty(
            raw.get("tomorrow"),
            raw.get("tomorrow_message"),
            raw.get("message_tomorrow"),
        ) or "")

        out["year"] = str(_first_non_empty(
            raw.get("year"),
            raw.get("year_2026"),
            raw.get("overall_2026"),
            raw.get("total_2026"),
        ) or "")

        # advice가 dict로 들어있는 케이스
        adv = raw.get("advice")
        if isinstance(adv, dict):
            out["love"] = str(adv.get("love") or "")
            out["money"] = str(adv.get("money") or "")
            out["work"] = str(adv.get("work") or adv.get("career") or "")
            out["health"] = str(adv.get("health") or "")

        # 또는 love/money/work/health가 최상위에 있는 케이스
        out["love"] = str(_first_non_empty(out["love"], raw.get("love")) or "")
        out["money"] = str(_first_non_empty(out["money"], raw.get("money")) or "")
        out["work"] = str(_first_non_empty(out["work"], raw.get("work"), raw.get("career")) or "")
        out["health"] = str(_first_non_empty(out["health"], raw.get("health")) or "")

        return out

    return out


def pick_fortune(data: Any) -> Dict[str, str]:
    """
    - data가 list면 랜덤 1개 선택
    - data가 dict면 entries/items/list 중 하나 있으면 그 안에서 선택
    - dict 자체가 1개 레코드면 그대로 normalize
    """
    if data is None:
        return normalize_fortune_record(None)

    if isinstance(data, list) and len(data) > 0:
        return normalize_fortune_record(random.choice(data))

    if isinstance(data, dict):
        for k in ["entries", "items", "data", "fortunes", "records", "list"]:
            v = data.get(k)
            if isinstance(v, list) and len(v) > 0:
                return normalize_fortune_record(random.choice(v))
        # dict 자체가 레코드일 수 있음
        return normalize_fortune_record(data)

    return normalize_fortune_record(None)


def ensure_not_empty(rec: Dict[str, str], lang: str) -> Dict[str, str]:
    # 완전 공백이면 fallback 문장
    fb = {
        "ko": "데이터가 없습니다.",
        "en": "No data.",
        "ja": "データがありません。",
        "zh": "暂无数据。",
        "ru": "Нет данных.",
        "hi": "डेटा नहीं मिला।",
    }.get(lang, "No data.")

    for k in rec.keys():
        if not isinstance(rec[k], str) or rec[k].strip() == "":
            rec[k] = fb
    return rec


# =========================
# Google Sheet: append_row (1000행 초과 에러 방지)
# 저장 컬럼 변경 금지:
# A ts, B phone, C name, D lang, E game_time, F game_result, G consult(O/X)
# =========================
def get_gspread_client():
    import gspread
    from google.oauth2.service_account import Credentials

    sa_info = st.secrets.get("gcp_service_account")
    if not sa_info:
        raise RuntimeError("Secrets에 gcp_service_account 가 없습니다.")

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(sa_info, scopes=scopes)
    return gspread.authorize(creds)


def append_row_to_sheet(row: list):
    gc = get_gspread_client()
    sh = gc.open_by_key(SPREADSHEET_ID)
    ws = sh.worksheet(SHEET_NAME)
    ws.append_row(row, value_input_option="USER_ENTERED")


def count_success_winners_cached() -> int:
    # 10초 캐시
    now = time.time()
    t = st.session_state.get("_winner_cnt_t", 0.0)
    v = st.session_state.get("_winner_cnt_v", 0)
    if now - t < 10:
        return int(v)

    try:
        gc = get_gspread_client()
        sh = gc.open_by_key(SPREADSHEET_ID)
        ws = sh.worksheet(SHEET_NAME)
        values = ws.get_all_values()
        cnt = 0
        for r in values[1:]:
            if len(r) >= 6 and (r[5] or "").strip().upper() == "SUCCESS":
                cnt += 1
        st.session_state["_winner_cnt_t"] = now
        st.session_state["_winner_cnt_v"] = cnt
        return cnt
    except Exception:
        return 0


def save_consult(phone: str, name: str, lang: str, game_time: float, game_result: str, consult: str):
    ts = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")
    row = [
        ts,
        phone,
        name,
        lang,
        f"{game_time:.3f}",
        game_result,
        consult,  # G열 O/X
    ]
    append_row_to_sheet(row)


# =========================
# 공유: 네가 말한 “공유 시트” 그대로 (navigator.share)
# =========================
def render_native_share_button(title: str, text: str, url: str):
    html = f"""
    <div style="margin: 14px 0 10px 0;">
      <button id="shareBtn"
        style="
          width:100%;
          padding:14px 16px;
          border-radius:14px;
          border:0;
          background: #6f42c1;
          color:white;
          font-weight:900;
          font-size:16px;
        ">
        친구에게 결과 공유하기
      </button>
      <div style="margin-top:8px; font-size:12px; color:rgba(0,0,0,0.55);">
        (공유 성공 시 재도전 1회 추가)
      </div>
    </div>

    <script>
    (function(){{
      const title = {json.dumps(title)};
      const text  = {json.dumps(text)};
      const url   = {json.dumps(url)};
      const btn = document.getElementById('shareBtn');

      async function doShare(){{
        try {{
          if (navigator.share) {{
            await navigator.share({{ title, text, url }});
            const u = new URL(window.location.href);
            u.searchParams.set('shared','1');
            window.location.href = u.toString();
          }} else {{
            try {{
              await navigator.clipboard.writeText(text + "\\n" + url);
              alert("공유 기능이 없어 텍스트를 복사했습니다.\\n원하시는 곳에 붙여넣기 하세요.");
            }} catch(e) {{
              alert("공유 기능이 없습니다.\\nURL을 직접 복사해주세요: " + url);
            }}
          }}
        }} catch(e) {{
          // 사용자가 취소해도 그냥 종료
        }}
      }}

      btn.addEventListener('click', doShare);
    }})();
    </script>
    """
    components.html(html, height=120)


def consume_shared_bonus_once():
    qp = get_query_params()
    shared = (qp.get("shared", ["0"])[0] if isinstance(qp.get("shared"), list) else "0")
    if shared == "1":
        if not st.session_state.get("share_bonus_used", False):
            st.session_state["share_bonus_used"] = True
            st.session_state["game_attempts"] = int(st.session_state.get("game_attempts", 1)) + 1
        # 파라미터 제거(호환)
        set_query_params()


# =========================
# 16문항(12,16 포함) + 다국어
# =========================
QUESTIONS_16 = {
    "ko": [
        "1. 낯선 사람과도 금방 친해지는 편이다.",
        "2. 혼자만의 시간이 꼭 필요하다.",
        "3. 즉흥적으로 계획을 바꾸는 걸 좋아한다.",
        "4. 일을 시작하기 전에 전체 계획을 세운다.",
        "5. 감정보다 논리가 더 중요하다고 느낀다.",
        "6. 상대의 기분을 먼저 고려하는 편이다.",
        "7. 여러 사람과 함께 있을 때 에너지가 난다.",
        "8. 소수 친한 사람과 깊게 지내는 편이다.",
        "9. 큰 그림/가능성을 떠올리는 걸 좋아한다.",
        "10. 현실적이고 구체적인 정보를 선호한다.",
        "11. 마감 직전 몰아서 하는 편이다.",
        "12. (복구) 작은 약속도 꼼꼼히 지키려고 한다.",
        "13. 갈등이 생기면 바로 해결하려 한다.",
        "14. 갈등이 생기면 시간을 두고 생각한다.",
        "15. 결정을 빠르게 내리는 편이다.",
        "16. (복구) 결정을 내리기 전 충분히 고민한다.",
    ],
    "en": [
        "1. I quickly get along with strangers.",
        "2. I need alone time regularly.",
        "3. I like changing plans spontaneously.",
        "4. I plan the whole flow before starting.",
        "5. Logic feels more important than emotion.",
        "6. I consider others' feelings first.",
        "7. I gain energy around many people.",
        "8. I prefer deep bonds with a few.",
        "9. I like imagining big possibilities.",
        "10. I prefer practical, concrete details.",
        "11. I often do things near the deadline.",
        "12. (Restored) I try to keep even small promises.",
        "13. I try to solve conflicts right away.",
        "14. I reflect before dealing with conflicts.",
        "15. I decide quickly.",
        "16. (Restored) I think carefully before deciding.",
    ],
    "ja": [
        "1. 初対面の人ともすぐ仲良くなれる。",
        "2. 一人の時間が必要だ。",
        "3. 即興で予定を変えるのが好きだ。",
        "4. 始める前に全体計画を立てる。",
        "5. 感情より論理が大事だと思う。",
        "6. 相手の気持ちを先に考える。",
        "7. 大勢といると元気になる。",
        "8. 少数と深く付き合う。",
        "9. 大きな可能性を考えるのが好き。",
        "10. 現実的で具体的な情報が好き。",
        "11. 締切直前にまとめてやりがち。",
        "12. (復元) 小さな約束も守ろうとする。",
        "13. 衝突はすぐ解決したい。",
        "14. 衝突は少し考えてから向き合う。",
        "15. 決断が早い。",
        "16. (復元) 決断前に十分悩む。",
    ],
    "zh": [
        "1. 我很快能和陌生人熟络起来。",
        "2. 我经常需要独处时间。",
        "3. 我喜欢临时改变计划。",
        "4. 我开始前会先做好整体规划。",
        "5. 我觉得逻辑比情绪更重要。",
        "6. 我会先考虑对方的感受。",
        "7. 和很多人在一起会更有能量。",
        "8. 我更喜欢和少数人深交。",
        "9. 我喜欢思考大方向与可能性。",
        "10. 我偏好现实且具体的信息。",
        "11. 我常在截止前集中完成。",
        "12. (已恢复) 我会尽量遵守小承诺。",
        "13. 我倾向马上解决冲突。",
        "14. 我会先想清楚再处理冲突。",
        "15. 我做决定很快。",
        "16. (已恢复) 我会充分思考后再决定。",
    ],
    "ru": [
        "1. Я быстро нахожу общий язык с незнакомыми.",
        "2. Мне регулярно нужно время наедине.",
        "3. Мне нравится спонтанно менять планы.",
        "4. Я планирую всё заранее перед началом.",
        "5. Логика важнее эмоций.",
        "6. Я сначала думаю о чувствах других.",
        "7. Я заряжаюсь в компании многих людей.",
        "8. Я предпочитаю близкое общение с немногими.",
        "9. Мне нравится думать о больших возможностях.",
        "10. Я предпочитаю практичные детали.",
        "11. Часто делаю всё перед дедлайном.",
        "12. (Восстановлено) Стараюсь держать даже маленькие обещания.",
        "13. Хочу решать конфликты сразу.",
        "14. Сначала обдумываю, потом решаю конфликт.",
        "15. Решаю быстро.",
        "16. (Восстановлено) Долго думаю перед решением.",
    ],
    "hi": [
        "1. मैं अजनबियों से जल्दी घुल-मिल जाता/जाती हूँ।",
        "2. मुझे अक्सर अकेले समय की ज़रूरत होती है।",
        "3. मुझे अचानक योजना बदलना पसंद है।",
        "4. शुरू करने से पहले मैं पूरा प्लान बनाता/बनाती हूँ।",
        "5. मुझे लगता है तर्क भावनाओं से ज़्यादा महत्वपूर्ण है।",
        "6. मैं पहले दूसरों की भावनाएँ सोचता/सोचती हूँ।",
        "7. बहुत लोगों के साथ रहने से ऊर्जा मिलती है।",
        "8. मैं कुछ लोगों के साथ गहरा रिश्ता पसंद करता/करती हूँ।",
        "9. मुझे बड़ी संभावनाएँ सोचना पसंद है।",
        "10. मुझे व्यावहारिक और ठोस जानकारी पसंद है।",
        "11. मैं अक्सर डेडलाइन के पास काम करता/करती हूँ।",
        "12. (बहाल) मैं छोटे वादे भी निभाने की कोशिश करता/करती हूँ।",
        "13. मैं तुरंत संघर्ष सुलझाना चाहता/चाहती हूँ।",
        "14. मैं सोचकर फिर संघर्ष सुलझाता/सुलझाती हूँ।",
        "15. मैं जल्दी निर्णय लेता/लेती हूँ।",
        "16. (बहाल) मैं निर्णय से पहले अच्छे से सोचता/सोचती हूँ।",
    ],
}


# =========================
# 세션 초기화
# =========================
def init_state():
    st.session_state.setdefault("lang", "ko")
    st.session_state.setdefault("view", "home")  # home / result
    st.session_state.setdefault("name", "")
    st.session_state.setdefault("phone", "")

    # 16문항 응답 저장
    st.session_state.setdefault("q_answers", [None] * 16)

    # 미니게임
    st.session_state.setdefault("game_attempts", 1)  # 기본 1회
    st.session_state.setdefault("share_bonus_used", False)

    st.session_state.setdefault("game_running", False)
    st.session_state.setdefault("game_start_t", None)
    st.session_state.setdefault("game_elapsed", 0.0)
    st.session_state.setdefault("game_outcome", None)  # SUCCESS / FAIL / None

    st.session_state.setdefault("consult_enabled", False)
    st.session_state.setdefault("consult_done", False)

    # 결과 캐시
    st.session_state.setdefault("fortune_cache", None)


# =========================
# 언어 선택(반응 안 하는 문제 해결)
# =========================
def render_language_selector():
    consume_shared_bonus_once()

    codes = [c for c, _ in SUPPORTED_LANGS]
    name_map = {c: n for c, n in SUPPORTED_LANGS}

    cur = st.session_state.get("lang", "ko")
    if cur not in codes:
        cur = "ko"

    selected = st.radio(
        "",
        options=codes,
        format_func=lambda x: name_map.get(x, x),
        index=codes.index(cur),
        horizontal=True,
        key="lang_radio_key",  # key 고정
        label_visibility="collapsed",
    )

    # 즉시 반영
    if selected != st.session_state.get("lang"):
        st.session_state["lang"] = selected
        # 언어 바뀌면 결과 캐시도 초기화
        st.session_state["fortune_cache"] = None
        st.rerun()


# =========================
# 미니게임 로직 + 실시간 표시
# =========================
def can_start_game() -> Tuple[bool, str]:
    if st.session_state.get("lang") != "ko":
        return False, "미니게임은 한국어에서만 진행됩니다."
    if st.session_state.get("consult_done", False):
        return False, "이미 성공하셨습니다."
    if int(st.session_state.get("game_attempts", 0)) <= 0:
        return False, "남은 시도 횟수가 없습니다. 친구 공유 후 재도전 1회가 가능합니다."
    if st.session_state.get("game_running", False):
        return False, "이미 진행 중입니다."
    return True, ""


def start_game():
    ok, _ = can_start_game()
    if not ok:
        return
    st.session_state["game_running"] = True
    st.session_state["game_start_t"] = time.perf_counter()
    st.session_state["game_elapsed"] = 0.0
    st.session_state["game_outcome"] = None
    st.session_state["consult_enabled"] = False


def stop_game_and_judge():
    if not st.session_state.get("game_running", False):
        return
    start_t = st.session_state.get("game_start_t")
    if not start_t:
        return

    elapsed = round(time.perf_counter() - start_t, 3)

    st.session_state["game_running"] = False
    st.session_state["game_elapsed"] = elapsed

    # 시도 횟수 차감
    st.session_state["game_attempts"] = max(0, int(st.session_state.get("game_attempts", 0)) - 1)

    # 선착순 마감
    winner_cnt = count_success_winners_cached()
    if winner_cnt >= MAX_WINNERS:
        st.session_state["game_outcome"] = "FAIL"
        st.session_state["consult_enabled"] = True
        return

    if TARGET_MIN <= elapsed <= TARGET_MAX:
        st.session_state["game_outcome"] = "SUCCESS"
        st.session_state["consult_done"] = True
        st.session_state["consult_enabled"] = False
    else:
        st.session_state["game_outcome"] = "FAIL"
        st.session_state["consult_enabled"] = True


def get_live_elapsed() -> float:
    if st.session_state.get("game_running") and st.session_state.get("game_start_t"):
        return round(time.perf_counter() - st.session_state["game_start_t"], 3)
    return float(st.session_state.get("game_elapsed", 0.0))


# =========================
# 광고(미니게임 바로 위, 한국어만)
# =========================
def render_ad_block_ko_only():
    if st.session_state.get("lang") != "ko":
        return
    st.markdown(
        """
        <div class="ad-box">
          <div class="ad-badge">광고</div>
          <div class="ad-title">정수기렌탈 대박!</div>
          <div class="ad-desc">
            제휴카드면 월 0원부터!<br/>
            설치 당일 최대 50만원 지원 + 사은품 듬뿍
          </div>
          <a class="ad-btn" href="https://xn--910b51a1r88nu39a.com" target="_blank" rel="noopener">다나눔렌탈.com 바로가기</a>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================
# 결과 렌더링 (다국어 + 데이터 파싱)
# =========================
def render_result_blocks(rec: Dict[str, str], lang: str):
    labels = {
        "ko": {
            "today": "오늘 운세",
            "tomorrow": "내일 운세",
            "year": "2026 전체 운세",
            "love": "연애운 조언",
            "money": "재물운 조언",
            "work": "직장/일 조언",
            "health": "건강운 조언",
        },
        "en": {
            "today": "Today's fortune",
            "tomorrow": "Tomorrow's fortune",
            "year": "2026 overall fortune",
            "love": "Love advice",
            "money": "Money advice",
            "work": "Work advice",
            "health": "Health advice",
        },
        "ja": {
            "today": "今日の運勢",
            "tomorrow": "明日の運勢",
            "year": "2026年総合運",
            "love": "恋愛アドバイス",
            "money": "金運アドバイス",
            "work": "仕事アドバイス",
            "health": "健康アドバイス",
        },
        "zh": {
            "today": "今日运势",
            "tomorrow": "明日运势",
            "year": "2026全年运势",
            "love": "爱情建议",
            "money": "财运建议",
            "work": "事业/工作建议",
            "health": "健康建议",
        },
        "ru": {
            "today": "Сегодня",
            "tomorrow": "Завтра",
            "year": "2026 общий прогноз",
            "love": "Совет: любовь",
            "money": "Совет: деньги",
            "work": "Совет: работа",
            "health": "Совет: здоровье",
        },
        "hi": {
            "today": "आज का भाग्य",
            "tomorrow": "कल का भाग्य",
            "year": "2026 समग्र भाग्य",
            "love": "प्रेम सलाह",
            "money": "धन सलाह",
            "work": "काम सलाह",
            "health": "स्वास्थ्य सलाह",
        },
    }
    L = labels.get(lang, labels["en"])

    for k in ["today", "tomorrow", "year", "love", "money", "work", "health"]:
        st.markdown(f"<div class='section-title'>{L[k]}</div>", unsafe_allow_html=True)
        st.write(rec.get(k, ""))


# =========================
# 메인 UI
# =========================
def render_home():
    lang = st.session_state.get("lang", "ko")

    st.markdown(
        """
        <div style="
          background: linear-gradient(135deg, rgba(122,74,255,0.20), rgba(255,153,0,0.18));
          border-radius: 18px;
          padding: 20px 16px;
          text-align:center;
          font-weight:900;
          font-size:28px;
          margin: 10px 0 16px 0;
        ">
          2026 띠 + MBTI + 사주 + 오늘/내일 운세
          <div style="font-size:14px; font-weight:800; margin-top:6px; opacity:0.7;">완전 무료</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.session_state["name"] = st.text_input("이름 입력 (결과에 표시돼요)", value=st.session_state.get("name", ""), key="name_input")
    st.session_state["phone"] = st.text_input("전화번호 (실패 시 상담신청에서 사용)", value=st.session_state.get("phone", ""), key="phone_input")

    # 16문항 (12,16 포함) 복구
    st.markdown("### MBTI 16문항")
    qs = QUESTIONS_16.get(lang, QUESTIONS_16["en"])
    for i in range(16):
        st.session_state["q_answers"][i] = st.radio(
            qs[i],
            options=["선택 안함", "예", "아니오"] if lang == "ko" else ["Not set", "Yes", "No"],
            index=0 if st.session_state["q_answers"][i] is None else st.session_state["q_answers"][i],
            key=f"q_{i+1}",
        )

    if st.button("운세 보기", key="go_result_btn"):
        st.session_state["view"] = "result"
        st.session_state["fortune_cache"] = None
        st.rerun()


def render_result():
    lang = st.session_state.get("lang", "ko")

    # 데이터 로딩
    path = FORTUNE_FILE_BY_LANG.get(lang, FORTUNE_FILE_BY_LANG["en"])
    data = load_json_file(path)

    # 결과 캐시(언어 변경/다시보기 시 초기화)
    if st.session_state.get("fortune_cache") is None:
        rec = pick_fortune(data)
        rec = ensure_not_empty(rec, lang)
        st.session_state["fortune_cache"] = rec
    else:
        rec = st.session_state["fortune_cache"]

    render_result_blocks(rec, lang)

    # 공유 버튼(네가 말한 방식 그대로)
    render_native_share_button(
        title="2026 운세 결과",
        text="내 2026 운세 결과 확인해봐! 🔮",
        url=APP_URL,
    )

    # 한국어에서만: 광고(미니게임 바로 위) + 미니게임
    if lang == "ko":
        render_ad_block_ko_only()
        render_mini_game_and_consult()

    if st.button("처음부터 다시하기", key="restart_btn"):
        # 시도횟수는 초기화하지 않음(요청)
        st.session_state["view"] = "home"
        st.session_state["fortune_cache"] = None
        st.rerun()


def render_mini_game_and_consult():
    st.markdown("<div class='game-card'>", unsafe_allow_html=True)
    st.markdown("### 🎁 미니게임: 선착순 20명 커피쿠폰 도전!")
    st.write("스톱워치를 **20.260s ~ 20.269s** 사이에 멈추면 성공입니다. (기본 1회, 친구 공유 시 1회 추가)")

    # 실시간 표시
    live = get_live_elapsed()
    st.markdown(f"<div class='stopwatch'>{live:06.3f}</div>", unsafe_allow_html=True)

    # 버튼
    c1, c2 = st.columns(2)

    with c1:
        start_ok, msg = can_start_game()
        if st.button("Start", disabled=not start_ok, key="game_start_btn"):
            start_game()

    with c2:
        if st.button("Stop", disabled=not st.session_state.get("game_running", False), key="game_stop_btn"):
            stop_game_and_judge()

    st.caption(f"남은 시도 횟수: **{int(st.session_state.get('game_attempts', 0))}회**")

    outcome = st.session_state.get("game_outcome")

    if outcome == "SUCCESS":
        st.success("성공! 응모 시 선착순 20명에게 커피 쿠폰 보내드립니다.")
        # 성공자: 상담신청 기능 OFF
        st.session_state["consult_enabled"] = False

    elif outcome == "FAIL":
        st.warning("친구 공유 후 재도전.\n또는 다나눔렌탈 정수기 렌탈 정보 상담신청하고 커피쿠폰 응모.")
        # 실패자: 상담신청 ON
        st.session_state["consult_enabled"] = True

    st.markdown("</div>", unsafe_allow_html=True)

    # 실패자만 상담신청
    if st.session_state.get("consult_enabled", False) and not st.session_state.get("consult_done", False):
        st.markdown("### 다나눔렌탈 상담신청(실패자만 가능)")
        st.write("상담 신청하시겠습니까?")

        phone = st.text_input("Phone / 전화번호", value=st.session_state.get("phone", ""), key="consult_phone")
        name = st.session_state.get("name", "")
        game_time = float(st.session_state.get("game_elapsed", 0.0))
        game_result = st.session_state.get("game_outcome", "FAIL")

        b1, b2 = st.columns(2)
        with b1:
            if st.button("O (신청)", key="consult_yes"):
                # O 선택 시 저장 (G열 O)
                try:
                    save_consult(
                        phone=str(phone).strip(),
                        name=str(name).strip(),
                        lang="ko",
                        game_time=game_time,
                        game_result=str(game_result),
                        consult="O",
                    )
                    st.success("커피쿠폰 응모되셨습니다.")
                    st.session_state["consult_enabled"] = False
                except Exception as e:
                    st.error(f"Sheet error: {e}")

        with b2:
            if st.button("X (취소)", key="consult_no"):
                # X 누르면 저장하지 않음(요청: DB 기록 삭제/미저장)
                st.session_state["consult_enabled"] = False

    # ✅ 실시간 타이머를 위해 running 중이면 자동 rerun (0.1초)
    if st.session_state.get("game_running", False):
        time.sleep(0.10)
        st.rerun()


# =========================
# 앱 엔트리
# =========================
def main():
    st.set_page_config(page_title="2026 운세", page_icon="🔮", layout="centered")
    st.markdown(BASE_CSS, unsafe_allow_html=True)
    components.html(SCROLL_FIX_JS, height=0)

    init_state()

    # SEO 항상 주입 (삭제되면 안 됨)
    inject_seo(st.session_state.get("lang", "ko"))
    render_seo_hidden_text()

    # 언어 선택
    render_language_selector()

    # 화면
    if st.session_state.get("view") == "home":
        render_home()
    else:
        render_result()


if __name__ == "__main__":
    main()
