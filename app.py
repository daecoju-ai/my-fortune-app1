# app.py
import os
import json
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, Tuple

import streamlit as st
import streamlit.components.v1 as components

# -----------------------------
# 기본 설정
# -----------------------------
KST = timezone(timedelta(hours=9))

APP_URL = "https://my-fortune.streamlit.app"  # 필요시 너 앱 주소로 유지/수정
SHEET_NAME = "시트1"  # 너가 말한 시트1
SPREADSHEET_ID = "1WvuKXx2if2WvxmQaxkqzFW-BzDEWWma9hZgCr2jJQYY"  # 기억해둔 ID

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

FORTUNE_FILE_BY_LANG = {
    "ko": "data/fortunes_ko.json",
    "en": "data/fortunes_en.json",
    "ja": "data/fortunes_ja.json",
    "zh": "data/fortunes_zh.json",
    "ru": "data/fortunes_ru.json",
    "hi": "data/fortunes_hi.json",
}

# -----------------------------
# 디자인(고정) + 스크롤 튐 방지 JS
# -----------------------------
BASE_CSS = """
<style>
/* 전체 폭/여백 최소, 기본 카드 톤 유지 */
.main .block-container { max-width: 720px; padding-top: 18px; padding-bottom: 60px; }

/* 버튼 스타일은 Streamlit 기본에 가깝게 유지(과한 커스텀 X) */
div.stButton > button {
  width: 100%;
  border-radius: 14px;
  padding: 14px 16px;
  font-weight: 700;
}

/* 안내 박스 */
.notice {
  background: #FFF3CD;
  border: 1px solid #FFE69C;
  color: #664D03;
  padding: 14px 14px;
  border-radius: 12px;
  margin: 12px 0 8px 0;
}

/* 결과 섹션 타이틀 */
.section-title{
  font-size: 20px;
  font-weight: 800;
  margin: 14px 0 8px 0;
}

/* 미니게임 카드 */
.game-card{
  background: #ffffff;
  border: 1px solid rgba(0,0,0,0.08);
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.06);
}

/* 스톱워치 디스플레이 */
.stopwatch{
  font-size: 44px;
  font-weight: 900;
  letter-spacing: 1px;
  text-align: center;
  padding: 10px 0 4px 0;
}

/* 광고 박스(미니게임 바로 위에 위치될 것) */
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
</style>
"""

# 스크롤 튐 방지: 버튼 클릭 등 리런 전 스크롤 위치 저장 -> 로드 후 복원
SCROLL_FIX_JS = """
<script>
(function(){
  try{
    // 클릭 시 현재 스크롤 저장
    document.addEventListener('click', function(){
      localStorage.setItem('st_scroll_y', String(window.scrollY || 0));
    }, true);

    // 로드 후 복원 (약간 지연)
    window.addEventListener('load', function(){
      const y = parseInt(localStorage.getItem('st_scroll_y') || "0", 10);
      setTimeout(()=>{ window.scrollTo(0, y); }, 80);
    });
  }catch(e){}
})();
</script>
"""


# -----------------------------
# 유틸: 데이터 로딩
# -----------------------------
@st.cache_data(show_spinner=False)
def load_fortunes(lang: str) -> Dict[str, Any]:
    """각 언어별 fortunes_XX.json 로딩. 누락/에러시 영어 fallback."""
    path = FORTUNE_FILE_BY_LANG.get(lang, FORTUNE_FILE_BY_LANG["en"])
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # fallback en
        try:
            with open(FORTUNE_FILE_BY_LANG["en"], "r", encoding="utf-8") as f:
            # type: ignore
                return json.load(f)
        except Exception:
            return {}


def safe_get(d: Dict[str, Any], *keys, default=None):
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


# -----------------------------
# Google Sheet (gspread) - append 방식으로 "1000행 초과" 해결
# -----------------------------
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
    """항상 마지막에 append. Range 지정 X -> 행 초과 에러 방지."""
    gc = get_gspread_client()
    sh = gc.open_by_key(SPREADSHEET_ID)
    ws = sh.worksheet(SHEET_NAME)
    ws.append_row(row, value_input_option="USER_ENTERED")


def count_success_winners_cached() -> int:
    """성공자(선착순 20명) 카운트. 너무 자주 읽지 않게 캐시."""
    # 캐시는 10초 정도면 충분
    now = time.time()
    last_t = st.session_state.get("_winner_count_cache_t", 0)
    last_v = st.session_state.get("_winner_count_cache_v", 0)
    if now - last_t < 10:
        return int(last_v)

    try:
        gc = get_gspread_client()
        sh = gc.open_by_key(SPREADSHEET_ID)
        ws = sh.worksheet(SHEET_NAME)
        values = ws.get_all_values()
        # 가정: 헤더 1행, game_result 컬럼이 6번째(F)라고 가정 (아래 저장컬럼 고정)
        # A ts, B phone, C name, D lang, E game_time, F game_result, G consult(O/X)
        cnt = 0
        for r in values[1:]:
            if len(r) >= 6 and (r[5] or "").strip().upper() == "SUCCESS":
                cnt += 1
        st.session_state["_winner_count_cache_t"] = now
        st.session_state["_winner_count_cache_v"] = cnt
        return cnt
    except Exception:
        return 0


# -----------------------------
# 공유(갤러리 공유 시트) - 네가 말한 "이 화면" 그대로
# -----------------------------
def render_native_share_button(share_title: str, share_text: str, share_url: str):
    """
    navigator.share로 모바일 공유 시트를 띄움.
    성공하면 URL에 ?shared=1 붙여서 Streamlit이 bonus 처리.
    """
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
      <div id="shareHint" style="margin-top:8px; font-size:12px; color:rgba(0,0,0,0.55);">
        (공유 성공 시 재도전 1회 추가)
      </div>
    </div>

    <script>
    (function(){{
      const title = {json.dumps(share_title)};
      const text  = {json.dumps(share_text)};
      const url   = {json.dumps(share_url)};
      const btn = document.getElementById('shareBtn');

      async function doShare(){{
        try {{
          if (navigator.share) {{
            await navigator.share({{ title, text, url }});
            // 공유 성공 -> shared=1 붙여서 리로드 (bonus 처리)
            const u = new URL(window.location.href);
            u.searchParams.set('shared','1');
            window.location.href = u.toString();
          }} else {{
            // share 미지원 -> 복사
            await navigator.clipboard.writeText(text + "\\n" + url);
            alert("공유 기능이 없어서 텍스트를 복사했습니다.\\n원하시는 곳에 붙여넣기 하세요.");
          }}
        }} catch(e) {{
          // 사용자가 취소해도 그냥 무시
        }}
      }}

      btn.addEventListener('click', doShare);
    }})();
    </script>
    """
    components.html(html, height=120)


def consume_shared_bonus_once():
    """URL 파라미터 shared=1 을 감지해서 bonus 1회만 지급."""
    q = st.query_params
    if q.get("shared", None) == "1":
        # 이미 지급했으면 또 지급하지 않음
        if not st.session_state.get("share_bonus_used", False):
            st.session_state["share_bonus_used"] = True
            st.session_state["game_attempts"] = st.session_state.get("game_attempts", 1) + 1

        # URL 깔끔하게 shared 제거
        try:
            st.query_params.clear()
        except Exception:
            pass


# -----------------------------
# 세션 상태 초기화
# -----------------------------
def init_state():
    st.session_state.setdefault("lang", "ko")
    st.session_state.setdefault("view", "input")  # input / result
    st.session_state.setdefault("result_payload", None)

    # 미니게임 상태 (한국어만 사용)
    st.session_state.setdefault("game_attempts", 1)  # 기본 1회
    st.session_state.setdefault("game_running", False)
    st.session_state.setdefault("game_start_t", None)
    st.session_state.setdefault("game_elapsed", None)  # stop 시 고정 값
    st.session_state.setdefault("game_outcome", None)  # SUCCESS / FAIL / None

    st.session_state.setdefault("share_bonus_used", False)

    # 상담신청 UI on/off
    st.session_state.setdefault("consult_enabled", False)  # 실패자만 ON
    st.session_state.setdefault("consult_done", False)     # 성공자는 OFF

    # 리프레시 제어
    st.session_state.setdefault("tick", 0)


# -----------------------------
# 결과 구성(간단/안정)
# -----------------------------
def build_result(fortunes: Dict[str, Any], lang: str) -> Dict[str, Any]:
    """
    기존 네 앱 로직 전체를 내가 여기서 알 수 없으니,
    '라벨이 Daily message 로 보이는 문제'는
    JSON에서 실제 문장을 꺼내는 방식으로 해결.
    (키가 없으면 fallback 문장을 넣음)
    """
    # 예시 키 구조를 최대한 폭넓게 허용
    # (너가 만든 master 데이터 구조를 그대로 쓰는 전제)
    today = safe_get(fortunes, "today", default=None)
    tomorrow = safe_get(fortunes, "tomorrow", default=None)
    year = safe_get(fortunes, "year_2026", default=None)
    love = safe_get(fortunes, "advice", "love", default=None)
    money = safe_get(fortunes, "advice", "money", default=None)
    work = safe_get(fortunes, "advice", "work", default=None)
    health = safe_get(fortunes, "advice", "health", default=None)

    def fallback(msg: str) -> str:
        # 언어별 간단 fallback
        if lang == "ko":
            return msg
        if lang == "ja":
            return "データが見つかりません。"
        if lang == "zh":
            return "未找到数据。"
        if lang == "ru":
            return "Данные не найдены."
        if lang == "hi":
            return "डेटा नहीं मिला।"
        return "Data not found."

    return {
        "today": today or fallback("오늘 운세 데이터가 없습니다."),
        "tomorrow": tomorrow or fallback("내일 운세 데이터가 없습니다."),
        "year": year or fallback("2026 전체 운세 데이터가 없습니다."),
        "love": love or fallback("연애운 조언 데이터가 없습니다."),
        "money": money or fallback("재물운 조언 데이터가 없습니다."),
        "work": work or fallback("직장/일 조언 데이터가 없습니다."),
        "health": health or fallback("건강운 조언 데이터가 없습니다."),
    }


# -----------------------------
# 미니게임 로직
# -----------------------------
def can_start_game() -> Tuple[bool, str]:
    if st.session_state.get("lang") != "ko":
        return False, "미니게임은 한국어에서만 진행됩니다."
    if st.session_state.get("consult_done", False):
        return False, "이미 성공하셨습니다."
    if st.session_state.get("game_attempts", 0) <= 0:
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
    st.session_state["game_elapsed"] = None
    st.session_state["game_outcome"] = None
    st.session_state["consult_enabled"] = False


def stop_game_and_judge():
    if not st.session_state.get("game_running", False):
        return
    start_t = st.session_state.get("game_start_t")
    if not start_t:
        return

    elapsed = time.perf_counter() - start_t
    elapsed_ms = round(elapsed, 3)

    # Stop 시 고정
    st.session_state["game_running"] = False
    st.session_state["game_elapsed"] = elapsed_ms

    # 시도 1회 차감
    st.session_state["game_attempts"] = max(0, int(st.session_state.get("game_attempts", 0)) - 1)

    # 선착순 마감 확인
    winner_cnt = count_success_winners_cached()
    if winner_cnt >= MAX_WINNERS:
        st.session_state["game_outcome"] = "FAIL"
        st.session_state["consult_enabled"] = True
        return

    # 성공 판정(허용오차: 20.260~20.269)
    if TARGET_MIN <= elapsed_ms <= TARGET_MAX:
        st.session_state["game_outcome"] = "SUCCESS"
        st.session_state["consult_enabled"] = False
        st.session_state["consult_done"] = True
        # 성공자는 상담신청 OFF
    else:
        st.session_state["game_outcome"] = "FAIL"
        st.session_state["consult_enabled"] = True


def game_tick_display() -> float:
    """진행 중이면 현재 경과, 아니면 고정 elapsed"""
    if st.session_state.get("game_running") and st.session_state.get("game_start_t"):
        return round(time.perf_counter() - st.session_state["game_start_t"], 3)
    if st.session_state.get("game_elapsed") is not None:
        return float(st.session_state["game_elapsed"])
    return 0.000


def maybe_autorefresh():
    """게임 running 중일 때만 부드럽게 갱신"""
    if st.session_state.get("game_running", False):
        # 100ms
        st.session_state["tick"] += 1
        st.experimental_rerun()


# -----------------------------
# 상담신청 저장 (실패자만, O 선택 시에만 저장)
# 저장 컬럼(바꾸지 말아달라)에 맞춰서 최소 컬럼만 append
# A ts, B phone, C name, D lang, E game_time, F game_result, G consult(O)
# -----------------------------
def save_consult(phone: str, name: str, lang: str, game_time: float, game_result: str):
    ts = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")
    row = [
        ts,
        phone,
        name,
        lang,
        f"{game_time:.3f}",
        game_result,
        "O",  # G열
    ]
    append_row_to_sheet(row)


# -----------------------------
# UI
# -----------------------------
def header_language_selector():
    # shared bonus 처리(공유 후 재도전 1회)
    consume_shared_bonus_once()

    cols = st.columns([1, 3])
    with cols[0]:
        pass
    with cols[1]:
        labels = [name for _, name in SUPPORTED_LANGS]
        codes = [code for code, _ in SUPPORTED_LANGS]
        current = st.session_state.get("lang", "ko")
        idx = codes.index(current) if current in codes else 0
        chosen = st.radio(
            "",
            options=codes,
            format_func=lambda c: dict(SUPPORTED_LANGS).get(c, c),
            index=idx,
            horizontal=True,
            label_visibility="collapsed",
        )
        st.session_state["lang"] = chosen


def render_results_section(result: Dict[str, Any], lang: str):
    # 결과 섹션(라벨은 각 언어별로 간단 처리)
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

    st.markdown(f"<div class='section-title'>{L['today']}</div>", unsafe_allow_html=True)
    st.write(result["today"])

    st.markdown(f"<div class='section-title'>{L['tomorrow']}</div>", unsafe_allow_html=True)
    st.write(result["tomorrow"])

    st.markdown(f"<div class='section-title'>{L['year']}</div>", unsafe_allow_html=True)
    st.write(result["year"])

    st.markdown(f"<div class='section-title'>{L['love']}</div>", unsafe_allow_html=True)
    st.write(result["love"])

    st.markdown(f"<div class='section-title'>{L['money']}</div>", unsafe_allow_html=True)
    st.write(result["money"])

    st.markdown(f"<div class='section-title'>{L['work']}</div>", unsafe_allow_html=True)
    st.write(result["work"])

    st.markdown(f"<div class='section-title'>{L['health']}</div>", unsafe_allow_html=True)
    st.write(result["health"])


def render_ad_block_ko_only():
    # "다나눔렌탈 광고"는 요청대로 미니게임 바로 위에서,
    # 한국어에서만 노출
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


def render_mini_game_ko_only(name: str, phone: str):
    # 한국어만
    if st.session_state.get("lang") != "ko":
        return

    st.markdown("<div class='game-card'>", unsafe_allow_html=True)
    st.markdown("### 🎁 미니게임: 선착순 20명 커피쿠폰 도전!", unsafe_allow_html=True)
    st.write("스톱워치를 **20.260s ~ 20.269s** 사이에 멈추면 성공입니다. (기본 1회, 친구 공유 시 1회 추가)")

    # 스톱 시 고정된 표시 유지
    current = game_tick_display()
    st.markdown(f"<div class='stopwatch'>{current:06.3f}</div>", unsafe_allow_html=True)

    # 버튼들
    colA, colB = st.columns(2)

    with colA:
        start_disabled = not can_start_game()[0]
        if st.button("Start", disabled=start_disabled, key="game_start_btn"):
            start_game()

    with colB:
        stop_disabled = not st.session_state.get("game_running", False)
        if st.button("Stop", disabled=stop_disabled, key="game_stop_btn"):
            stop_game_and_judge()

    st.caption(f"남은 시도 횟수: **{st.session_state.get('game_attempts', 0)}회**")

    # 결과 메시지
    outcome = st.session_state.get("game_outcome")
    if outcome == "SUCCESS":
        st.success("성공! 응모 시 선착순 20명에게 커피 쿠폰 보내드립니다.")
    elif outcome == "FAIL":
        # 실패: 공유 후 재도전 or 상담신청 유도
        st.warning("친구 공유 후 재도전.\n또는 다나눔렌탈 정수기 렌탈 정보 상담신청하고 커피쿠폰 응모.")

    st.markdown("</div>", unsafe_allow_html=True)

    # 상담신청 UI (실패자만 ON)
    if st.session_state.get("consult_enabled", False) and not st.session_state.get("consult_done", False):
        st.markdown("### 다나눔렌탈 상담신청(실패자만 가능)")
        st.write("상담 신청하시겠습니까?")

        # 전화번호는 이미 입력받은 값을 보여주되 수정은 가능하게
        phone_in = st.text_input("Phone / 전화번호", value=phone or "", key="consult_phone")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("O (신청)", key="consult_yes"):
                # 상담 신청 O -> DB 저장 (G열 O)
                try:
                    gt = float(st.session_state.get("game_elapsed") or 0.0)
                    gr = st.session_state.get("game_outcome") or "FAIL"
                    save_consult(phone_in.strip(), name.strip(), "ko", gt, gr)
                    st.success("커피쿠폰 응모가 접수되었습니다.")
                    # 접수 후에는 상담신청 off (중복 방지)
                    st.session_state["consult_enabled"] = False
                except Exception as e:
                    st.error(f"Sheet error: {e}")

        with col2:
            if st.button("X (취소)", key="consult_no"):
                # X 누르면 저장 안함 (요청대로 삭제/미기록)
                st.session_state["consult_enabled"] = False

    # 진행 중이면 부드럽게 갱신 (리런)
    if st.session_state.get("game_running", False):
        # 0.1초마다 갱신: 화면 튐은 SCROLL_FIX_JS가 잡아줌
        time.sleep(0.10)
        st.experimental_rerun()


def render():
    st.set_page_config(page_title="2026 운세", page_icon="🔮", layout="centered")
    st.markdown(BASE_CSS, unsafe_allow_html=True)
    components.html(SCROLL_FIX_JS, height=0)

    init_state()
    header_language_selector()

    lang = st.session_state.get("lang", "ko")
    fortunes = load_fortunes(lang)

    # -------------------------
    # 입력 화면
    # -------------------------
    if st.session_state.get("view") == "input":
        # (너가 기존에 쓰던 입력 UI가 여기 있을 텐데,
        #  디자인 고정 요청 때문에 구조는 최소로 둠)

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

        name = st.text_input("이름 입력 (결과에 표시돼요)", key="name_input")
        # 생년월일/MBTI/띠 선택 등은 기존 코드에 맞게 있겠지만,
        # 여기서는 결과 오류/번역/미니게임/시트 문제 해결이 핵심이라 최소화
        # 너 기존 로직 그대로 넣고 result_payload만 만들어도 됨.

        if st.button("운세 보기", key="go_result"):
            # 결과 payload 저장
            result = build_result(fortunes, lang)
            st.session_state["result_payload"] = {
                "name": name.strip(),
                "phone": st.session_state.get("phone_input", "").strip(),
                "lang": lang,
                "result": result,
            }
            st.session_state["view"] = "result"
            st.experimental_rerun()

        return

    # -------------------------
    # 결과 화면
    # -------------------------
    payload = st.session_state.get("result_payload") or {}
    name = (payload.get("name") or "").strip()
    phone = (payload.get("phone") or "").strip()
    result = payload.get("result") or build_result(fortunes, lang)

    render_results_section(result, lang)

    # ✅ 공유 버튼: “그 공유 시트” 방식 그대로 (다른 생각 X)
    share_title = "2026 운세 결과"
    # 너무 길면 공유앱이 잘릴 수 있어 짧게
    share_text = "내 2026 운세 결과 확인해봐! 🔮"
    render_native_share_button(share_title, share_text, APP_URL)

    # ✅ 광고는 “미니게임 바로 위” (한국어만)
    render_ad_block_ko_only()

    # ✅ 미니게임은 한국어만
    render_mini_game_ko_only(name=name, phone=phone)

    # ✅ 처음부터 다시하기: 입력값만 리셋, “시도횟수는 초기화하지 않음”
    # (요청: 처음부터 다시하기 후에도 시도횟수 유지)
    if st.button("처음부터 다시하기", key="restart"):
        # view만 input으로. attempts/share_bonus는 그대로 둠.
        st.session_state["view"] = "input"
        st.session_state["result_payload"] = None
        st.experimental_rerun()


if __name__ == "__main__":
    render()
