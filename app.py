import streamlit as st
import json, os, hashlib
from datetime import date, datetime, timedelta
import streamlit.components.v1 as components

# ============================================================
# 2026 운세 + 타로 + 이벤트 스톱워치 (Streamlit)
# - DB 조합(combo) 금지: DB는 "pools"만 사용
# - DB 파일명 고정: data/fortunes_ko_2026.json
# ============================================================

APP_TITLE = "2026 운세 | 띠 + MBTI + 사주 + 오늘/내일 운세 + 타로"
DB_PATH = "data/fortunes_ko_2026.json"

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def _sha_int(s: str) -> int:
    return int(hashlib.sha256(s.encode("utf-8")).hexdigest(), 16)

@st.cache_data(show_spinner=False)
def load_db() -> dict:
    if not os.path.exists(DB_PATH):
        st.error(f"DB 파일이 없습니다: {DB_PATH}\n\nGitHub 저장소에 이 파일이 업로드되어 있는지 확인해주세요.")
        st.stop()
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def pick_pool(pools: dict, key: str, seed: str) -> str:
    arr = pools.get(key) or []
    if not arr:
        return ""
    idx = _sha_int(seed) % len(arr)
    return arr[idx]

def norm_mbti(s: str) -> str:
    s = (s or "").strip().upper()
    if len(s) != 4:
        return ""
    ok = set("EISNTFJP")
    return s if all(c in ok for c in s) else ""

def zodiac_from_year_solar(y: int) -> str:
    # 1900=rat 기준
    order = ["쥐","소","호랑이","토끼","용","뱀","말","양","원숭이","닭","개","돼지"]
    return order[(y - 1900) % 12]

def seed_for_day(birth: date, mbti: str, d: date, salt: str) -> str:
    # 날짜별(오늘/내일) 고정 결과: 같은 날 같은 입력이면 동일
    return f"{birth.isoformat()}|{mbti}|{d.isoformat()}|{salt}|2026"

# ------------------------------------------------------------
# Share component (Web Share API + URL copy)
# ------------------------------------------------------------
def share_block(title: str, text: str):
    # 공유가 막히면 URL 복사로 안내
    html = f"""
    <div style="display:flex; gap:10px; flex-wrap:wrap;">
      <button id="shareBtn" style="padding:10px 14px;border-radius:12px;border:1px solid rgba(120,120,160,.35);background:white;cursor:pointer;">
        친구에게 공유하기
      </button>
      <button id="copyBtn" style="padding:10px 14px;border-radius:12px;border:1px solid rgba(120,120,160,.35);background:white;cursor:pointer;">
        URL 복사
      </button>
      <span id="msg" style="font-size:14px; color: #444;"></span>
    </div>
    <script>
      const msg = document.getElementById('msg');
      async function copyUrl() {{
        try {{
          await navigator.clipboard.writeText(window.location.href);
          msg.textContent = "URL이 복사되었습니다.";
        }} catch(e) {{
          msg.textContent = "복사가 막혔습니다. 주소창 URL을 길게 눌러 복사해주세요.";
        }}
      }}
      document.getElementById('copyBtn').addEventListener('click', copyUrl);
      document.getElementById('shareBtn').addEventListener('click', async () => {{
        try {{
          if (!navigator.share) throw new Error("no share");
          await navigator.share({{
            title: {json.dumps(title)},
            text: {json.dumps(text)},
            url: window.location.href
          }});
          msg.textContent = "공유창을 열었습니다.";
        }} catch(e) {{
          // 카톡 인앱 브라우저 등에서 share가 막힐 수 있음 -> URL 복사로 우회
          await copyUrl();
        }}
      }});
    </script>
    """
    components.html(html, height=80)

# ------------------------------------------------------------
# Stopwatch component (Start/Stop -> stop 순간 기록을 Streamlit로 전달)
# - 표시: 00.000 (초만, 소수 3자리)
# - Stop 누르면 즉시 멈춘 화면/기록이 유지됨
# - Start/Stop 버튼 비활성화 상태 표시
# ------------------------------------------------------------
def stopwatch_component(disabled: bool, key: str = "sw") -> float | None:
    disabled_js = "true" if disabled else "false"

    html = """
    <div style="
      background: rgba(255,255,255,0.96);
      border-radius: 18px;
      padding: 16px;
      border: 1px solid rgba(120,120,160,0.18);
      box-shadow: 0 10px 28px rgba(0,0,0,0.10);
      max-width: 520px;
    ">
      <div style="font-size: 18px; font-weight: 700; margin-bottom: 10px;">⏱️ STOPWATCH</div>
      <div id="time" style="
        font-size: 64px; font-weight: 800; letter-spacing: 1px;
        padding: 16px 18px; border-radius: 16px;
        background: rgba(84, 84, 255, 0.08);
        border: 1px solid rgba(84,84,255,0.15);
        text-align:center;
      ">00.000</div>

      <div style="display:flex; gap:12px; margin-top:14px;">
        <button id="startBtn" style="
          flex:1; padding: 14px 0; border-radius: 14px; border:0;
          background: #6B5BFF; color: white; font-size: 18px; font-weight: 700; cursor: pointer;
          opacity: 1;
        ">START</button>
        <button id="stopBtn" style="
          flex:1; padding: 14px 0; border-radius: 14px; border:0;
          background: #F39B63; color: white; font-size: 18px; font-weight: 700; cursor: pointer;
          opacity: 0.55;
        " disabled>STOP</button>
      </div>

      <div style="margin-top:10px; font-size:14px; color:#444;">
        START 후 STOP을 눌러 기록을 제출하세요.
      </div>
    </div>

    <script>
      const DISABLED = __DISABLED__;
      const timeEl = document.getElementById("time");
      const startBtn = document.getElementById("startBtn");
      const stopBtn = document.getElementById("stopBtn");

      let running = false;
      let startTs = 0;
      let raf = null;
      let frozen = false;
      let lastValue = 0;

      function fmt(sec) {
        // 00.000 형태 (초만 표시)
        const s = Math.max(0, sec);
        return s.toFixed(3).padStart(6, "0");
      }

      function setBtnState() {
        if (DISABLED) {
          startBtn.disabled = true;
          stopBtn.disabled = true;
          startBtn.style.opacity = "0.55";
          stopBtn.style.opacity = "0.55";
          return;
        }
        // frozen이면 둘 다 비활성
        if (frozen) {
          startBtn.disabled = true;
          stopBtn.disabled = true;
          startBtn.style.opacity = "0.55";
          stopBtn.style.opacity = "0.55";
          return;
        }
        startBtn.disabled = running;
        stopBtn.disabled = !running;

        startBtn.style.opacity = running ? "0.55" : "1";
        stopBtn.style.opacity = running ? "1" : "0.55";
      }

      function tick() {
        if (!running) return;
        const now = performance.now();
        const sec = (now - startTs) / 1000.0;
        lastValue = sec;
        timeEl.textContent = fmt(sec);
        raf = requestAnimationFrame(tick);
      }

      function sendValue(v) {
        try {
          const u = new URL(window.location.href);
          u.searchParams.set("sw", String(v));
          u.searchParams.set("sw_ts", String(Date.now()));
          window.location.href = u.toString();
        } catch(e) {
          // 마지막 수단: alert
          alert("기록: " + String(v));
        }
      }

      startBtn.addEventListener("click", () => {
        if (DISABLED || frozen) return;
        running = true;
        frozen = false;
        startTs = performance.now();
        lastValue = 0;
        timeEl.textContent = "00.000";
        setBtnState();
        raf = requestAnimationFrame(tick);
      });

      stopBtn.addEventListener("click", () => {
        if (DISABLED || frozen) return;
        if (!running) return;
        running = false;
        frozen = true;
        if (raf) cancelAnimationFrame(raf);
        // timeEl은 이미 마지막 tick 값이 표시되어 있음
        setBtnState();
        sendValue(lastValue);
      });

      // init
      setBtnState();
    </script>
    """
    html = html.replace("__DISABLED__", disabled_js)
    return components.html(html, height=320, key=key)

# ------------------------------------------------------------
# MBTI 16문항 (모르는 사람용)
# ------------------------------------------------------------
MBTI_Q = [
    ("사람들과 함께 있을 때 에너지가 차는 편이다", "E", "I"),
    ("새로운 사람을 만나는 것이 비교적 편하다", "E", "I"),
    ("말로 생각을 정리하는 편이다", "E", "I"),
    ("혼자 있는 시간이 꼭 필요하다", "I", "E"),
    ("현실적/구체적인 정보를 더 신뢰한다", "S", "N"),
    ("아이디어/가능성을 떠올리는 게 즐겁다", "N", "S"),
    ("경험으로 검증된 방법을 선호한다", "S", "N"),
    ("비유/상징/숨은 의미를 잘 찾는 편이다", "N", "S"),
    ("결정할 때 논리가 더 중요하다", "T", "F"),
    ("결정할 때 사람의 감정이 더 중요하다", "F", "T"),
    ("피드백이 직설적일 수 있다", "T", "F"),
    ("분위기를 해치지 않으려 배려한다", "F", "T"),
    ("계획대로 진행될 때 편하다", "J", "P"),
    ("즉흥적으로 바꾸는 것도 괜찮다", "P", "J"),
    ("마감 전에 여유 있게 끝내는 편", "J", "P"),
    ("마감 직전에 집중력이 올라간다", "P", "J"),
]

def mbti_quiz() -> str:
    st.markdown("### MBTI를 모르는 분은 16문항으로 선택해보세요")
    scores = {c: 0 for c in "EISNTFJP"}
    for i,(q,a,b) in enumerate(MBTI_Q, start=1):
        v = st.radio(f"{i}. {q}", ["그렇다", "아니다"], horizontal=True, key=f"q{i}")
        pick = a if v == "그렇다" else b
        scores[pick] += 1
    mbti = ""
    mbti += "E" if scores["E"] >= scores["I"] else "I"
    mbti += "S" if scores["S"] >= scores["N"] else "N"
    mbti += "T" if scores["T"] >= scores["F"] else "F"
    mbti += "J" if scores["J"] >= scores["P"] else "P"
    st.info(f"예상 MBTI: **{mbti}**")
    return mbti

# ------------------------------------------------------------
# UI
# ------------------------------------------------------------
def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="🔮", layout="centered")
    db = load_db()
    pools = db.get("pools") or {}

    # pool 필수 확인(없으면 바로 원인 표시)
    required = ["year_all", "today", "tomorrow", "advice", "action_tip"]
    missing = [k for k in required if not (pools.get(k) and len(pools.get(k)) > 0)]
    if missing:
        st.error("DB에 필요한 풀이 비어있습니다: " + ", ".join(missing))
        st.stop()

    st.markdown(
        """
        <div style="
          background: linear-gradient(135deg, rgba(142, 78, 255, .22), rgba(110, 170, 255, .22));
          border: 1px solid rgba(120,120,160,0.15);
          border-radius: 18px;
          padding: 18px 16px;
          box-shadow: 0 10px 30px rgba(0,0,0,0.06);
          margin-bottom: 12px;
        ">
          <div style="font-size:32px; font-weight:800; margin-bottom:6px;">🔮 2026년 운세</div>
          <div style="font-size:16px; opacity:.85;">띠 + MBTI + 사주 + 오늘/내일 운세 + 타로</div>
          <div style="font-size:14px; opacity:.75; margin-top:4px;">완전 무료</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    tab1, tab2 = st.tabs(["운세 보기", "이벤트 스톱워치"])

    with tab1:
        colA, colB = st.columns([1,1])
        with colA:
            birth = st.date_input("생년월일", value=date(2000,1,1), min_value=date(1900,1,1), max_value=date(2026,12,31))
        with colB:
            mbti_mode = st.radio("MBTI 입력 방식", ["직접 선택", "16문항"], horizontal=True)

        mbti = ""
        if mbti_mode == "직접 선택":
            mbti = st.selectbox("MBTI 선택", [
                "","ISTJ","ISFJ","INFJ","INTJ",
                "ISTP","ISFP","INFP","INTP",
                "ESTP","ESFP","ENFP","ENTP",
                "ESTJ","ESFJ","ENFJ","ENTJ"
            ])
        else:
            mbti = mbti_quiz()

        mbti = norm_mbti(mbti)
        if not mbti:
            st.warning("MBTI를 선택/완료하면 결과를 보여드릴게요.")
            return

        zodiac = zodiac_from_year_solar(birth.year)

        st.markdown("## 결과")
        st.write(f"띠 운세: **{zodiac}**")
        st.write(f"MBTI 특징: **{mbti}**")

        # 2026 전체운세: birth+mbti 기반으로 고정
        seed_year = f"{birth.isoformat()}|{mbti}|year_all|2026"
        year_text = pick_pool(pools, "year_all", seed_year)

        # 오늘/내일: 날짜별 seed (같은 날엔 고정)
        today = date.today()
        tomorrow = today + timedelta(days=1)
        today_text = pick_pool(pools, "today", seed_for_day(birth, mbti, today, "today"))
        tomorrow_text = pick_pool(pools, "tomorrow", seed_for_day(birth, mbti, tomorrow, "tomorrow"))

        advice_text = pick_pool(pools, "advice", seed_for_day(birth, mbti, today, "advice"))
        action_tip = pick_pool(pools, "action_tip", seed_for_day(birth, mbti, today, "action_tip"))

        st.markdown("### 2026년 전체 운세")
        st.info(year_text)

        st.markdown("### 오늘 운세")
        st.success(today_text)

        st.markdown("### 내일 운세")
        st.warning(tomorrow_text)

        st.markdown("### 조언")
        st.write(advice_text)
        st.write(action_tip)

        st.markdown("---")
        st.markdown("### 다나눔렌탈 상담/이벤트")
        st.write("다나눔렌탈 1660-2445")

        share_block("2026년 운세", "내 2026년 운세 확인해봐! (띠+MBTI+오늘/내일 운세)")

    with tab2:
        st.markdown("### ☕ 커피쿠폰 이벤트")
        st.caption("선착순 지급 / 소진 시 조기 종료될 수 있습니다.")
        st.write("목표 구간: **20.260 ~ 20.269초**")
        # tries
        if "tries_left" not in st.session_state:
            st.session_state.tries_left = 1
        st.write(f"도전 횟수: **{st.session_state.tries_left}/1**")

        disabled = st.session_state.tries_left <= 0

        value = stopwatch_component(disabled=disabled, key="stopwatch_2026")

        # STOP을 누르면 JS가 URL에 ?sw=<seconds>&sw_ts=<ms> 를 붙여서 새로고침합니다.
        qp = dict(st.query_params) if hasattr(st, "query_params") else st.experimental_get_query_params()
        sw = None
        try:
            if isinstance(qp.get("sw"), list):
                sw = qp.get("sw", [None])[0]
            else:
                sw = qp.get("sw")
        except Exception:
            sw = None

        if sw is not None:
            # 같은 값이 새로고침마다 반복 소비되는 것 방지
            if st.session_state.get("_last_sw_ts") == (qp.get("sw_ts")[0] if isinstance(qp.get("sw_ts"), list) else qp.get("sw_ts")):
                sw = None

        if sw is not None:

            # consume try
            if st.session_state.tries_left > 0:
                st.session_state.tries_left -= 1

            record = float(sw)
            # query param 정리
            ts_val = (qp.get("sw_ts")[0] if isinstance(qp.get("sw_ts"), list) else qp.get("sw_ts"))
            st.session_state["_last_sw_ts"] = ts_val
            try:
                st.query_params.clear()
            except Exception:
                try:
                    st.experimental_set_query_params()
                except Exception:
                    pass

            st.markdown("#### 기록")
            st.write(f"**{record:0.3f}초**")

            success = (20.260 <= record <= 20.269)
            if success:
                st.success(f"성공! **{record:0.3f}초** 기록. 쿠폰 지급을 위해 정보를 입력해주세요.")
                with st.form("winner_form"):
                    name = st.text_input("이름")
                    phone = st.text_input("전화번호")
                    submitted = st.form_submit_button("쿠폰 지급 신청")
                if submitted:
                    if name.strip() and phone.strip():
                        st.success("접수되었습니다. 확인 후 쿠폰을 발송해드릴게요.")
                    else:
                        st.error("이름/전화번호를 모두 입력해주세요.")
            else:
                st.error(f"실패! **{record:0.3f}초** 기록.")
                st.markdown("도전 기회 추가:")
                st.write("- 친구 공유 시 도전 기회 1회 추가")
                st.write("- 또는 정수기 렌탈 상담 신청 후 커피쿠폰 응모")

                share_block("커피쿠폰 도전!", "20.260~20.269초 맞추면 커피쿠폰! 같이 해보자.")
                st.markdown("#### 정수기 렌탈 상담")
                st.write("다나눔렌탈 1660-2445")

                if st.button("처음부터 다시"):
                    # 버튼은 기록 확인 후에만 보이므로, 누르면 새로고침/초기화
                    st.session_state.tries_left = 1
                    st.rerun()

        else:
            # value=None인 경우, 여기는 대기 상태
            if disabled:
                st.info("도전 횟수를 모두 사용했습니다. 공유/상담으로 기회 추가 후 다시 시도하세요.")

if __name__ == "__main__":
    main()
