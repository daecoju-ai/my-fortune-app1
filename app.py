import json
import os
import hashlib
import time
from datetime import datetime, date, timedelta

import streamlit as st
import streamlit.components.v1 as components

# =========================
# 0) App Identity / Defaults
# =========================
APP_TITLE = "다나눔렌탈 상담/이벤트"
APP_SUBTITLE = "다나눔렌탈 1660-2445"

# 광고 문구(고정)
AD_TEXT = "[광고] 정수기 렌탈 제휴카드 적용시 월 렌탈비 0원, 설치당일 최대 현금50만원 + 사은품 증정"

# 데이터 파일(고정)
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_2026_PATH = os.path.join(DATA_DIR, "fortunes_ko_2026.json")
MBTI_PATH = os.path.join(DATA_DIR, "mbti_traits_ko.json")
SAJU_PATH = os.path.join(DATA_DIR, "saju_ko.json")
ZODIAC_PATH = os.path.join(DATA_DIR, "zodiac_fortunes_ko_2026.json")
LNY_PATH = os.path.join(DATA_DIR, "lunar_new_year_1920_2026.json")
TAROT_PATH = os.path.join(DATA_DIR, "tarot_db_ko.json")

# 구글시트 ID(기억된 고정값)
SHEET_ID = "1WvuKXx2if2WvxmQaxkqzFW-BzDEWWma9hZgCr2jJQYY"
SHEET_TAB_NAME = "시트1"

# 시트 컬럼(고정)
SHEET_COLUMNS = ["시간", "이름", "전화번호", "언어", "기록초", "공유여부", "상담신청"]

# 이벤트 목표 구간(고정)
TARGET_MIN = 20.260
TARGET_MAX = 20.269


# =========================
# 1) Utilities
# =========================
def _safe_read_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_required_json(path: str, label: str):
    """필수 DB는 없으면 바로 안내 후 중단."""
    if not os.path.exists(path):
        st.error(f"필수 DB 파일을 읽을 수 없습니다: {path}\n\n파일이 GitHub에 업로드되어 있는지 확인해주세요.")
        st.stop()
    try:
        return _safe_read_json(path)
    except Exception as e:
        st.error(f"필수 DB 파일을 읽는 중 오류가 발생했습니다: {path}\n\n에러: {e}")
        st.stop()


def load_optional_json(path: str, default):
    if not os.path.exists(path):
        return default
    try:
        return _safe_read_json(path)
    except Exception:
        return default


def stable_seed(*parts: str) -> int:
    """하루 동안 고정되는 시드(재현성)."""
    raw = "|".join([p or "" for p in parts])
    h = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return int(h[:12], 16)


def pick_from_pool(pool, seed: int):
    if not pool:
        return ""
    i = seed % len(pool)
    return pool[i]


def normalize_mbti(s: str) -> str:
    s = (s or "").strip().upper()
    if len(s) != 4:
        return ""
    valid = set("EINTFSJP")
    if any(ch not in valid for ch in s):
        return ""
    return s


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
            st.query_params[k] = str(v)
    except Exception:
        st.experimental_set_query_params(**{k: str(v) for k, v in params.items()})


def korean_zodiac_from_birth(birth: date, lny_table: dict) -> str:
    """
    한국 띠(12지) 계산:
    - 해당 연도의 '설(음력 1월 1일)' 날짜(양력)를 기준으로,
      설 이전 출생이면 전년도 띠, 이후면 해당년도 띠.
    """
    zodiac_order = ["쥐", "소", "호랑이", "토끼", "용", "뱀", "말", "양", "원숭이", "닭", "개", "돼지"]
    y = birth.year
    # 테이블 없으면 양력 기준으로(최후의 안전장치) -> 중단은 안 하고 계산만
    lny = None
    try:
        lny_str = lny_table.get(str(y))
        if lny_str:
            lny = datetime.strptime(lny_str, "%Y-%m-%d").date()
    except Exception:
        lny = None

    zodiac_year = y
    if lny and birth < lny:
        zodiac_year = y - 1

    # 1900년이 쥐띠(경자년)로 알려져 있어 1900을 기준으로 모듈러
    idx = (zodiac_year - 1900) % 12
    return zodiac_order[idx]


def format_seconds_only(sec: float) -> str:
    """00.000 형태로 표시."""
    if sec < 0:
        sec = 0.0
    # 2자리 정수 + 소수점 3자리
    return f"{sec:06.3f}"  # e.g. 20.263 -> '20.263', 0.5 -> '00.500'


# =========================
# 2) Google Sheet (optional)
# =========================
def sheet_available() -> bool:
    try:
        import gspread  # noqa
        from google.oauth2.service_account import Credentials  # noqa
        return True
    except Exception:
        return False


def append_to_sheet(row: list):
    """
    row는 SHEET_COLUMNS 순서로 append.
    secrets에 gcp_service_account 가 있으면 사용.
    """
    try:
        import gspread
        from google.oauth2.service_account import Credentials

        if "gcp_service_account" not in st.secrets:
            raise RuntimeError("Streamlit secrets에 gcp_service_account가 없습니다.")

        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(dict(st.secrets["gcp_service_account"]), scopes=scopes)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(SHEET_ID)
        ws = sh.worksheet(SHEET_TAB_NAME)

        # 헤더가 비어있으면 고정 컬럼으로 1행 세팅
        first_row = ws.row_values(1)
        if not first_row or [c.strip() for c in first_row[: len(SHEET_COLUMNS)]] != SHEET_COLUMNS:
            ws.clear()
            ws.append_row(SHEET_COLUMNS)

        ws.append_row(row)
        return True, ""
    except Exception as e:
        return False, str(e)


# =========================
# 3) UI Helpers
# =========================
def page_header():
    st.markdown(
        f"""
        <div style="padding:18px 14px 8px 14px;">
          <div style="font-size:28px; font-weight:800; line-height:1.25;">{APP_TITLE}</div>
          <div style="font-size:18px; font-weight:600; opacity:0.85; margin-top:6px;">{APP_SUBTITLE}</div>
          <div style="margin-top:14px; padding:12px 12px; border-radius:14px; background:#f7f7f9; border:1px solid rgba(0,0,0,0.06);">
            <div style="font-weight:700; margin-bottom:6px;">{AD_TEXT}</div>
            <div style="font-size:13px; opacity:0.8;">→ 이름, 전화번호 작성. 무료 상담하기 → 구글시트 연동</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def share_and_copy_buttons():
    """
    카카오 등에서 navigator.share가 막히는 경우가 있어
    - '친구에게 공유하기'는 시도
    - 실패 시 'URL 복사' 안내
    """
    components.html(
        """
        <div style="display:flex; gap:10px; margin:8px 0 16px 0;">
          <button id="shareBtn" style="flex:1; padding:12px 10px; border-radius:14px; border:1px solid rgba(0,0,0,0.15); background:#fff; font-weight:700;">
            친구에게 공유하기
          </button>
          <button id="copyBtn" style="flex:1; padding:12px 10px; border-radius:14px; border:1px solid rgba(0,0,0,0.15); background:#fff; font-weight:700;">
            URL 복사
          </button>
        </div>
        <div id="msg" style="font-size:13px; opacity:0.8;"></div>
        <script>
          const msg = document.getElementById("msg");
          async function copyUrl() {
            try {
              await navigator.clipboard.writeText(window.location.href);
              msg.innerText = "URL이 복사되었습니다.";
            } catch (e) {
              const ta = document.createElement("textarea");
              ta.value = window.location.href;
              document.body.appendChild(ta);
              ta.select();
              document.execCommand("copy");
              document.body.removeChild(ta);
              msg.innerText = "URL이 복사되었습니다.";
            }
          }
          document.getElementById("copyBtn").addEventListener("click", copyUrl);
          document.getElementById("shareBtn").addEventListener("click", async () => {
            try {
              if (!navigator.share) throw new Error("share not supported");
              await navigator.share({ title: document.title, url: window.location.href });
              msg.innerText = "공유가 열렸습니다. (만약 막히면 'URL 복사'를 눌러주세요)";
            } catch (e) {
              msg.innerText = "공유가 막혔습니다. 'URL 복사'로 우회해 주세요.";
            }
          });
        </script>
        """,
        height=110,
    )


def stopwatch_html():
    """
    HTML/JS 스톱워치:
    - Start 누르면 카운트 시작
    - Stop 누르면 현재 기록을 URL 파라미터 t=xx.xxx 로 넣고 리로드
    - 하루 1회 기본, 공유 성공 시 +1 (앱 로직)
    """
    # JS에서 사용되는 {}가 파이썬 f-string과 충돌하지 않도록 "f-string을 쓰지 않음"
    components.html(
        """
        <div style="padding:14px; border-radius:16px; border:1px solid rgba(0,0,0,0.12); background:#fff;">
          <div style="font-size:22px; font-weight:800;">스톱워치</div>
          <div style="font-size:13px; opacity:0.8; margin-top:6px;">
            분 단위 없이 초만 표시됩니다. (00.000)
          </div>

          <div id="time" style="margin-top:14px; font-size:42px; font-weight:900; letter-spacing:1px;">00.000</div>

          <div style="display:flex; gap:10px; margin-top:14px;">
            <button id="startBtn" style="flex:1; padding:12px 10px; border-radius:14px; border:1px solid rgba(0,0,0,0.15); background:#fff; font-weight:800;">
              START
            </button>
            <button id="stopBtn" disabled style="flex:1; padding:12px 10px; border-radius:14px; border:1px solid rgba(0,0,0,0.15); background:#f2f2f2; color:#888; font-weight:800;">
              STOP
            </button>
          </div>

          <div id="note" style="margin-top:12px; font-size:13px; opacity:0.85;"></div>
        </div>

        <script>
          let running = false;
          let start = 0;
          let raf = null;

          const startBtn = document.getElementById("startBtn");
          const stopBtn  = document.getElementById("stopBtn");
          const timeEl   = document.getElementById("time");
          const noteEl   = document.getElementById("note");

          function fmt(ms){
            const s = ms / 1000;
            return s.toFixed(3).padStart(6, "0");
          }

          function tick(){
            if(!running) return;
            const now = performance.now();
            timeEl.innerText = fmt(now - start);
            raf = requestAnimationFrame(tick);
          }

          startBtn.addEventListener("click", () => {
            if(running) return;
            running = true;
            start = performance.now();
            startBtn.disabled = true;
            startBtn.style.background = "#f2f2f2";
            startBtn.style.color = "#888";
            stopBtn.disabled = false;
            stopBtn.style.background = "#fff";
            stopBtn.style.color = "#000";
            noteEl.innerText = "STOP을 누르면 기록이 확정됩니다.";
            tick();
          });

          stopBtn.addEventListener("click", () => {
            if(!running) return;
            running = false;
            if(raf) cancelAnimationFrame(raf);
            const now = performance.now();
            const ms = now - start;
            const sec = (ms/1000).toFixed(3);

            stopBtn.disabled = true;
            stopBtn.style.background = "#f2f2f2";
            stopBtn.style.color = "#888";

            // URL에 기록 저장 후 reload
            const u = new URL(window.location.href);
            u.searchParams.set("t", sec);
            u.searchParams.set("done", "1");
            window.location.href = u.toString();
          });
        </script>
        """,
        height=260,
    )


# =========================
# 4) Fortune Logic (2026)
# =========================
def get_2026_fortune(db_2026: dict, birth: date, mbti: str, lang: str = "ko") -> dict:
    """
    db_2026 구조는:
    {
      "year_all": [...],
      "today": [...],
      "tomorrow": [...],
      "advice": [...]
    }
    """
    ymd = birth.strftime("%Y-%m-%d")
    today = date.today().isoformat()

    out = {}

    # 연운(2026)은 개인 고정 시드 (생년월일+mbti)로 고정
    seed_year = stable_seed("2026", ymd, mbti, lang)
    out["year_all"] = pick_from_pool(db_2026.get("year_all", []), seed_year)

    # 오늘/내일은 날짜 포함해서 하루 고정
    seed_today = stable_seed("today", today, ymd, mbti, lang)
    out["today"] = pick_from_pool(db_2026.get("today", []), seed_today)

    seed_tom = stable_seed("tomorrow", today, ymd, mbti, lang)  # 기준은 '오늘'을 넣어 하루 고정(내일 운세도 동일)
    out["tomorrow"] = pick_from_pool(db_2026.get("tomorrow", []), seed_tom)

    seed_adv = stable_seed("advice", today, ymd, mbti, lang)
    out["advice"] = pick_from_pool(db_2026.get("advice", []), seed_adv)

    return out


# =========================
# 5) Session State
# =========================
def init_state():
    st.session_state.setdefault("lang", "ko")
    st.session_state.setdefault("shared", False)
    st.session_state.setdefault("tries_base", 1)   # 기본 1회
    st.session_state.setdefault("tries_bonus", 0)  # 공유 성공 시 +1
    st.session_state.setdefault("used_try", False) # 오늘 도전 사용 여부(서버 메모리 기준: 세션)
    st.session_state.setdefault("last_result_sec", None)
    st.session_state.setdefault("last_success", None)
    st.session_state.setdefault("form_name", "")
    st.session_state.setdefault("form_phone", "")
    st.session_state.setdefault("apply_consult", False)


def tries_left() -> int:
    total = int(st.session_state.get("tries_base", 1)) + int(st.session_state.get("tries_bonus", 0))
    used = 1 if st.session_state.get("used_try", False) else 0
    left = total - used
    return max(left, 0)


# =========================
# 6) App
# =========================
st.set_page_config(page_title=APP_TITLE, page_icon="☕", layout="centered")

init_state()

db_2026 = load_required_json(DB_2026_PATH, "2026 운세 DB")
mbti_db = load_optional_json(MBTI_PATH, default={})
saju_db = load_optional_json(SAJU_PATH, default={})
zodiac_db = load_optional_json(ZODIAC_PATH, default={})
lny_table = load_optional_json(LNY_PATH, default={})
tarot_db = load_optional_json(TAROT_PATH, default={})

page_header()
share_and_copy_buttons()

tab1, tab2 = st.tabs(["운세 보기", "이벤트 스톱워치"])

# -------------------------
# Tab 1: Fortune
# -------------------------
with tab1:
    # 입력 UI (달력)
    col1, col2 = st.columns([1, 1])
    with col1:
        birth = st.date_input("생년월일", value=date(2000, 1, 1), min_value=date(1920, 1, 1), max_value=date(2026, 12, 31))
    with col2:
        mbti_in = st.text_input("MBTI (예: ENFP)", value="ENFP", max_chars=4)

    mbti = normalize_mbti(mbti_in)
    if not mbti:
        st.warning("MBTI는 4글자(예: ENFP)로 입력해주세요.")

    # 띠 계산 + 띠 운세(있으면)
    zodiac = korean_zodiac_from_birth(birth, lny_table) if birth else ""
    if zodiac:
        st.caption(f"띠: {zodiac}띠")

    # 메인 운세
    if mbti:
        fortune = get_2026_fortune(db_2026, birth, mbti, lang="ko")

        if fortune.get("year_all"):
            st.info(fortune["year_all"])
        else:
            st.warning("2026 연운 DB(year_all)가 비어 있습니다.")

        st.subheader("오늘 운세")
        st.success(fortune.get("today", "") or "오늘 운세 DB(today)가 비어 있습니다.")

        st.subheader("내일 운세")
        st.warning(fortune.get("tomorrow", "") or "내일 운세 DB(tomorrow)가 비어 있습니다.")

        st.subheader("조언")
        st.write(fortune.get("advice", "") or "조언 DB(advice)가 비어 있습니다.")

        # MBTI 한줄 특징(있으면)
        trait = mbti_db.get(mbti)
        if trait:
            st.markdown("### MBTI 한줄 요약")
            if isinstance(trait, dict):
                # {"title": "...", "text": "..."} 형태도 허용
                title = trait.get("title")
                text_ = trait.get("text") or trait.get("desc") or ""
                if title:
                    st.write(f"**{title}**")
                if text_:
                    st.write(text_)
            else:
                st.write(str(trait))

        # 띠 운세(있으면)
        if zodiac_db and zodiac in zodiac_db:
            st.markdown("### 2026 띠 운세")
            zd = zodiac_db.get(zodiac, {})
            if isinstance(zd, dict):
                # year/today/tomorrow/advice 중 일부라도 있으면 표시
                if zd.get("year"):
                    st.write(zd["year"])
                if zd.get("today"):
                    st.write(f"**오늘:** {zd['today']}")
                if zd.get("tomorrow"):
                    st.write(f"**내일:** {zd['tomorrow']}")
                if zd.get("advice"):
                    st.write(f"**조언:** {zd['advice']}")
            else:
                st.write(str(zd))


# -------------------------
# Tab 2: Stopwatch Event
# -------------------------
with tab2:
    st.title("☕ 커피쿠폰 이벤트")
    st.write("선착순 지급 / 소진 시 조기 종료될 수 있습니다")
    st.write(f"목표 구간: **{TARGET_MIN:.3f} ~ {TARGET_MAX:.3f}초**")
    st.write(f"도전 횟수: **{tries_left()}/{int(st.session_state['tries_base']) + int(st.session_state['tries_bonus'])}**")

    qp = get_query_params()
    done = (qp.get("done", ["0"])[0] if isinstance(qp.get("done"), list) else qp.get("done", "0"))
    t = (qp.get("t", [""])[0] if isinstance(qp.get("t"), list) else qp.get("t", ""))

    # 결과 처리(쿼리 파라미터에서 들어온 경우)
    if done == "1" and t:
        try:
            sec = float(t)
        except Exception:
            sec = None

        if sec is not None and not st.session_state.get("used_try", False):
            st.session_state["used_try"] = True
            st.session_state["last_result_sec"] = sec
            st.session_state["last_success"] = (TARGET_MIN <= sec <= TARGET_MAX)

        # 파라미터 초기화(새로고침 반복 방지)
        set_query_params({})

    # 도전 가능 여부
    if tries_left() <= 0:
        st.warning("오늘의 도전 기회를 모두 사용했습니다.")
    else:
        stopwatch_html()

    # 결과 표시 (스톱 누른 뒤)
    if st.session_state.get("last_result_sec") is not None:
        sec = float(st.session_state["last_result_sec"])
        formatted = format_seconds_only(sec)

        if st.session_state.get("last_success"):
            st.success(f"성공! 기록: {formatted}초\n\n쿠폰지급을 위해 이름, 전화번호 입력해주세요")
        else:
            st.error(f"실패! 기록: {formatted}초\n\n친구공유시 도전기회 1회추가 또는 정수기렌탈 상담신청 후 커피쿠폰 응모")

        st.divider()

        # 공유 체크(사용자가 실제로 공유했는지 자동 판별은 어려워서, 버튼 안내 후 체크박스로 확정)
        # (카카오에서 share가 막히는 케이스 때문에 URL복사를 제공하고, 사용자 동의로 공유 처리)
        shared = st.checkbox("친구에게 공유 완료(도전 1회 추가)", value=st.session_state.get("shared", False))
        if shared and not st.session_state.get("shared", False):
            st.session_state["shared"] = True
            st.session_state["tries_bonus"] = 1
            st.success("공유 완료 처리되었습니다. 도전 기회가 1회 추가되었습니다.")

        st.divider()

        # 상담/응모 폼
        with st.form("apply_form", clear_on_submit=False):
            name = st.text_input("이름", value=st.session_state.get("form_name", ""))
            phone = st.text_input("전화번호", value=st.session_state.get("form_phone", ""))
            consult = st.checkbox("정수기 렌탈 상담신청", value=st.session_state.get("apply_consult", False))
            submitted = st.form_submit_button("무료 상담하기 / 응모하기")

        if submitted:
            st.session_state["form_name"] = name
            st.session_state["form_phone"] = phone
            st.session_state["apply_consult"] = consult

            if not name.strip() or not phone.strip():
                st.warning("이름과 전화번호를 입력해주세요.")
            else:
                # 시트 저장
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                lang = st.session_state.get("lang", "ko")
                rec = f"{sec:.3f}"
                shared_val = str(bool(st.session_state.get("shared", False)))
                consult_val = "O(정수기)" if consult else ""
                row = [now_str, name.strip(), phone.strip(), lang, rec, shared_val, consult_val]

                ok, err = append_to_sheet(row)
                if ok:
                    st.success("접수 완료! 감사합니다.")
                else:
                    st.error(f"구글시트 저장 실패: {err}")

    # 처음부터 다시 (UI는 유지하되 로직만 초기화)
    reset_disabled = False if (st.session_state.get("last_result_sec") is not None) else True
    if st.button("처음부터 다시", disabled=reset_disabled):
        st.session_state["used_try"] = False
        st.session_state["last_result_sec"] = None
        st.session_state["last_success"] = None
        st.session_state["shared"] = False
        st.session_state["tries_bonus"] = 0
        st.session_state["form_name"] = ""
        st.session_state["form_phone"] = ""
        st.session_state["apply_consult"] = False
        st.rerun()
