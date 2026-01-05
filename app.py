
import streamlit as st
import json, os, hashlib
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

# =========================
# 0) App Config
# =========================
APP_TITLE = "2026 운세 | 띠 + MBTI + 사주 + 오늘/내일 운세 (타로 포함)"
DB_PATHS = [
    os.path.join("data", "fortunes_ko_2026.json"),
    os.path.join("data", "fortunes_ko_2026_LARGE.json"),  # optional alt name
]

st.set_page_config(page_title=APP_TITLE, page_icon="🔮", layout="centered")

# =========================
# 1) Utilities (No fallback)
# =========================
@st.cache_data(show_spinner=False)
def load_json_first(paths: List[str]) -> Dict[str, Any]:
    for p in paths:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
    # fallback 금지: 여기서 바로 에러
    raise FileNotFoundError("DB 파일을 찾을 수 없습니다: " + ", ".join(paths))

def require_pools(db: Dict[str, Any], keys: List[str]) -> Dict[str, List[str]]:
    pools = db.get("pools")
    if not isinstance(pools, dict):
        raise TypeError("DB 형식 오류: 최상위 'pools'가 없습니다.")
    missing = [k for k in keys if not pools.get(k)]
    if missing:
        raise KeyError("DB에 필요한 pool이 비어있습니다: " + ", ".join(missing))
    return pools  # type: ignore

def stable_int_hash(s: str) -> int:
    h = hashlib.sha256(s.encode("utf-8")).hexdigest()
    return int(h[:16], 16)

def pick_from_pool(pool: List[str], seed_key: str) -> str:
    if not pool:
        raise ValueError("pool이 비어있습니다.")
    idx = stable_int_hash(seed_key) % len(pool)
    return pool[idx]

def fmt_seconds(ms: float) -> str:
    # seconds with 3 decimals, no minutes
    sec = max(0.0, ms / 1000.0)
    return f"{sec:0.3f}"

def phone_normalize(s: str) -> str:
    return "".join(ch for ch in s if ch.isdigit())


def get_query_params() -> Dict[str, List[str]]:
    """
    Streamlit 버전별 query param 호환.
    - 최신: st.query_params (mapping-like, 값이 str 또는 list일 수 있음)
    - 구버전: st.experimental_get_query_params()
    """
    try:
        qp = getattr(st, "query_params", None)
        if qp is not None:
            # qp는 mapping-like
            out: Dict[str, List[str]] = {}
            for k in qp.keys():
                v = qp.get(k)
                if v is None:
                    continue
                if isinstance(v, list):
                    out[k] = [str(x) for x in v]
                else:
                    out[k] = [str(v)]
            return out
    except Exception:
        pass
    try:
        return st.experimental_get_query_params()  # type: ignore[attr-defined]
    except Exception:
        return {}

def set_query_params(params: Dict[str, str]):
    try:
        qp = getattr(st, "query_params", None)
        if qp is not None:
            # clear then set
            try:
                qp.clear()
            except Exception:
                pass
            for k, v in params.items():
                qp[k] = v
            return
    except Exception:
        pass
    try:
        st.experimental_set_query_params(**params)  # type: ignore[attr-defined]
    except Exception:
        return


# =========================
# 2) Share block (Kakao webview safe)
# =========================
def share_block(title: str, subtitle: str):
    st.markdown(f"## {title}")
    st.markdown(subtitle)

    st.components.v1.html(
        """
        <div style="display:flex; gap:10px; flex-wrap:wrap; margin: 10px 0 4px 0;">
          <button id="shareBtn" style="padding:10px 14px; border-radius:10px; border:1px solid #ddd; background:white; font-weight:600;">
            친구에게 공유하기
          </button>
          <button id="copyBtn" style="padding:10px 14px; border-radius:10px; border:1px solid #ddd; background:white; font-weight:600;">
            URL 복사
          </button>
        </div>
        <div id="msg" style="font-size:14px; color:#444; margin-top:6px;"></div>

        <script>
          const msg = document.getElementById("msg");
          function show(t){ msg.textContent = t; }

          async function copyUrl(){
            const url = window.location.href;
            // 1) Clipboard API
            try{
              if (navigator.clipboard && navigator.clipboard.writeText){
                await navigator.clipboard.writeText(url);
                show("URL이 복사되었습니다.");
                return true;
              }
            }catch(e){}
            // 2) execCommand fallback
            try{
              const ta = document.createElement("textarea");
              ta.value = url;
              ta.style.position = "fixed";
              ta.style.left = "-9999px";
              document.body.appendChild(ta);
              ta.focus();
              ta.select();
              const ok = document.execCommand("copy");
              document.body.removeChild(ta);
              if(ok){ show("URL이 복사되었습니다."); return true; }
            }catch(e){}
            show("이 브라우저에서는 자동 복사가 막혔습니다. 주소창 URL을 길게 눌러 복사해 주세요.");
            return false;
          }

          document.getElementById("copyBtn").addEventListener("click", async () => {
            await copyUrl();
          });

          document.getElementById("shareBtn").addEventListener("click", async () => {
            const url = window.location.href;
            // Kakao/인앱 브라우저에서 navigator.share가 막히는 경우가 많아서 try/catch 후 URL 복사로 우회
            try{
              if (navigator.share){
                await navigator.share({ title: document.title, text: document.title, url });
                try{
                  const u = new URL(window.location.href);
                  u.searchParams.set('shared','1');
                  window.location.href = u.toString();
                }catch(e){}
                show("공유 창이 열렸습니다.");
              } else {
                await copyUrl();
              }
            } catch(e){
              await copyUrl();
            }
          });
        </script>
        """,
        height=120,
    )

# =========================
# 3) Stopwatch component (no manual input)
# =========================
def stopwatch_component(disabled: bool):
    disabled_js = "true" if disabled else "false"

    st.components.v1.html(
        f"""
        <div style="
          background: rgba(255,255,255,0.96);
          border-radius: 18px;
          padding: 16px;
          border: 1px solid rgba(140,120,200,0.25);
          box-shadow: 0 10px 28px rgba(0,0,0,0.08);
          max-width: 520px;
        ">
          <div style="font-weight:800; font-size: 18px; margin-bottom: 10px;">⏱️ STOPWATCH</div>

          <div id="timeBox" style="
            width: 100%;
            border-radius: 16px;
            padding: 18px 10px;
            text-align:center;
            font-size: 54px;
            font-weight: 900;
            letter-spacing: 2px;
            background: rgba(120,90,200,0.08);
            border: 1px solid rgba(120,90,200,0.18);
          ">00.000</div>

          <div style="display:flex; gap:12px; margin-top:14px;">
            <button id="startBtn" style="
              flex:1; padding:14px 0; border:none; border-radius: 14px;
              background:#6f59d9; color:white; font-weight:900; font-size:18px;
              opacity: 1;
            ">START</button>
            <button id="stopBtn" style="
              flex:1; padding:14px 0; border:none; border-radius: 14px;
              background:#f09a63; color:white; font-weight:900; font-size:18px;
              opacity: 1;
            ">STOP</button>
          </div>

          <div style="margin-top:10px; color:#444; font-size:14px;">
            START 후 STOP을 눌러 기록을 제출하세요.
          </div>
        </div>

        <script>
          const disabled = {disabled_js};

          const timeBox = document.getElementById("timeBox");
          const startBtn = document.getElementById("startBtn");
          const stopBtn = document.getElementById("stopBtn");

          let running = false;
          let t0 = 0;
          let raf = null;

          function fmt(ms){
            const sec = Math.max(0, ms/1000);
            return sec.toFixed(3).padStart(6, "0"); // e.g., 00.000 ~ 99.999
          }

          function setDisabled(on){
            startBtn.disabled = on;
            stopBtn.disabled = on;
            const op = on ? 0.45 : 1;
            startBtn.style.opacity = op;
            stopBtn.style.opacity = op;
          }

          function tick(){
            if (!running) return;
            const ms = performance.now() - t0;
            timeBox.textContent = fmt(ms);
            raf = requestAnimationFrame(tick);
          }

          function redirectWithResult(s){
            try{
              const u = new URL(window.location.href);
              u.searchParams.set('sw', s);
              u.searchParams.set('sw_ts', String(Date.now()));
              window.location.href = u.toString();
            }catch(e){}
          }

          function sendValue(obj){
            // Streamlit component protocol
            window.parent.postMessage(
              {{
                isStreamlitMessage: true,
                type: "streamlit:setComponentValue",
                value: obj
              }},
              "*"
            );
          }

          if (disabled){
            setDisabled(true);
          }

          startBtn.addEventListener("click", () => {{
            if (disabled) return;
            if (running) return;
            running = true;
            t0 = performance.now();
            timeBox.textContent = "00.000";
            tick();
          }});

          stopBtn.addEventListener("click", () => {{
            if (disabled) return;
            if (!running) return;
            running = false;
            if (raf) cancelAnimationFrame(raf);
            const ms = performance.now() - t0;
            const s = fmt(ms);
            timeBox.textContent = s;
            // disable immediately after one attempt
            setDisabled(true);
            redirectWithResult(s);
          }});
        </script>
        """,
        height=310,
    )

# =========================
# 4) UI (keep simple, don't redesign ads)
# =========================
def header_card(birth: Optional[date], mbti: Optional[str]):
    btxt = birth.isoformat() if birth else "생년월일 입력"
    mtxt = mbti if mbti else "MBTI 선택"
    st.markdown(
        f"""
        <div style="
          background: linear-gradient(135deg, rgba(173,127,255,0.35), rgba(120,190,255,0.35));
          border-radius: 22px;
          padding: 18px 18px;
          border: 1px solid rgba(255,255,255,0.55);
          box-shadow: 0 14px 30px rgba(0,0,0,0.08);
          margin-bottom: 12px;
        ">
          <div style="font-size: 28px; font-weight: 900; margin-bottom: 6px;">🔮 2026년 운세</div>
          <div style="font-size: 16px; opacity: 0.9;">{btxt} · {mtxt}</div>
          <div style="margin-top: 10px; display:inline-block; padding: 8px 14px; border-radius: 999px; border: 1px solid rgba(255,255,255,0.65); background: rgba(255,255,255,0.25); font-weight: 800;">
            🃏 타로 포함
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

MBTI_TYPES = [
    "ISTJ","ISFJ","INFJ","INTJ",
    "ISTP","ISFP","INFP","INTP",
    "ESTP","ESFP","ENFP","ENTP",
    "ESTJ","ESFJ","ENFJ","ENTJ"
]

MBTI_QS = [
    ("에너지", "사람들과 있으면 에너지가 차나요?", "혼자 있을 때 에너지가 차나요?", "E", "I"),
    ("정보", "사실/경험 중심으로 판단하나요?", "직감/가능성 중심으로 판단하나요?", "S", "N"),
    ("판단", "논리/원칙이 중요하나요?", "감정/관계가 중요하나요?", "T", "F"),
    ("생활", "계획대로 하는 편인가요?", "즉흥적으로 하는 편인가요?", "J", "P"),
]*4  # 16문항

def mbti_from_answers(ans: List[str]) -> str:
    # 16문항 -> 4축 다수결
    cnt = {"E":0,"I":0,"S":0,"N":0,"T":0,"F":0,"J":0,"P":0}
    for a in ans:
        if a in cnt: cnt[a]+=1
    return ("E" if cnt["E"]>=cnt["I"] else "I") + \
           ("S" if cnt["S"]>=cnt["N"] else "N") + \
           ("T" if cnt["T"]>=cnt["F"] else "F") + \
           ("J" if cnt["J"]>=cnt["P"] else "P")

# =========================
# 5) Main
# =========================
def main():
    # Ads (do not change)
    share_block("다나눔렌탈 상담/이벤트", "다나눔렌탈 1660-2445")

    # Load DB (no fallback)
    try:
        db = load_json_first(DB_PATHS)
        pools = require_pools(db, [
            "year_all","today","tomorrow",
            "advice","love_advices","money_advices","work_study_advices","health_advices","action_tips",
            "saju_one_liner"
        ])
    except Exception as e:
        st.error(str(e))
        st.stop()

    tab1, tab2 = st.tabs(["운세 보기", "이벤트 스톱워치"])

    # -------------------------
    # TAB 1: Fortune
    # -------------------------
    with tab1:
        # Inputs
        col1, col2 = st.columns([1,1])
        with col1:
            birth = st.date_input("생년월일", value=None)
        with col2:
            mbti_mode = st.radio("MBTI 입력 방식", ["드롭다운 선택", "MBTI 모르면 질문 16개"], horizontal=True)

        mbti = None
        if mbti_mode == "드롭다운 선택":
            mbti = st.selectbox("MBTI", ["선택"] + MBTI_TYPES)
            if mbti == "선택":
                mbti = None
        else:
            st.caption("MBTI를 모르면 아래 16개 질문에 답하면 자동 계산됩니다.")
            answers=[]
            for i, (title, a_txt, b_txt, a_key, b_key) in enumerate(MBTI_QS, start=1):
                choice = st.radio(f"{i}. {title}", [a_txt, b_txt], horizontal=False, key=f"mbti_q_{i}")
                answers.append(a_key if choice==a_txt else b_key)
            mbti = mbti_from_answers(answers)
            st.info(f"추정 MBTI: **{mbti}**")

        header_card(birth if isinstance(birth, date) else None, mbti)

        if birth is None or mbti is None:
            st.warning("생년월일과 MBTI를 입력하면 운세가 표시됩니다.")
        else:
            # Seeds (no combo keys; only pools)
            birth_key = birth.isoformat()
            today_d = date.today()
            tomorrow_d = today_d + timedelta(days=1)

            year_text = pick_from_pool(pools["year_all"], f"2026|year_all|{birth_key}|{mbti}")
            today_text = pick_from_pool(pools["today"], f"2026|today|{today_d.isoformat()}|{birth_key}|{mbti}")
            tomorrow_text = pick_from_pool(pools["tomorrow"], f"2026|tomorrow|{tomorrow_d.isoformat()}|{birth_key}|{mbti}")
            saju_one = pick_from_pool(pools["saju_one_liner"], f"2026|saju|{birth_key}|{mbti}")

            # advice categories are fixed per day
            love = pick_from_pool(pools["love_advices"], f"2026|love|{today_d.isoformat()}|{birth_key}|{mbti}")
            money = pick_from_pool(pools["money_advices"], f"2026|money|{today_d.isoformat()}|{birth_key}|{mbti}")
            work = pick_from_pool(pools["work_study_advices"], f"2026|work|{today_d.isoformat()}|{birth_key}|{mbti}")
            health = pick_from_pool(pools["health_advices"], f"2026|health|{today_d.isoformat()}|{birth_key}|{mbti}")
            action = pick_from_pool(pools["action_tips"], f"2026|action|{today_d.isoformat()}|{birth_key}|{mbti}")
            advice = pick_from_pool(pools["advice"], f"2026|advice|{today_d.isoformat()}|{birth_key}|{mbti}")

            st.markdown("## 결과")
            st.write(f"**사주 한 줄:** {saju_one}")
            st.write("")
            st.write(f"**2026 전체 운세:** {year_text}")
            st.write("")
            st.write(f"**오늘 운세:** {today_text}")
            st.write("")
            st.write(f"**내일 운세:** {tomorrow_text}")

            st.markdown("### 조언")
            st.write(f"- **연애:** {love}")
            st.write(f"- **금전:** {money}")
            st.write(f"- **일/학업:** {work}")
            st.write(f"- **건강:** {health}")
            st.write(f"- **오늘의 액션:** {action}")
            st.write(f"- **한 줄 조언:** {advice}")

    # -------------------------
    # TAB 2: Stopwatch event
    # -------------------------
    with tab2:
        st.markdown("## ☕ 커피쿠폰 이벤트")
        st.write("선착순 지급 / 소진 시 조기 종료될 수 있습니다.")
        st.write("**목표 구간: 20.260 ~ 20.269초**")

        if "tries_left" not in st.session_state:
            st.session_state.tries_left = 1
        if "sw_result" not in st.session_state:
            st.session_state.sw_result = None  # dict

        st.write(f"**도전 횟수: {st.session_state.tries_left}/1**")

        disabled = st.session_state.tries_left <= 0 or st.session_state.sw_result is not None
        stopwatch_component(disabled=disabled)

        # Query params processing (STOP 결과/공유 보너스)
        qp = get_query_params()

        # 공유 보너스: shared=1 이면 1회 추가(최대 1회만)
        if qp.get("shared", ["0"])[0] == "1":
            if not st.session_state.get("shared_bonus_given", False):
                st.session_state.shared_bonus_given = True
                st.session_state.tries_left = min(2, st.session_state.tries_left + 1)  # +1회, 상한 2
            # shared 파라미터는 지워서 반복 적용 방지
            set_query_params({k: v[0] for k, v in qp.items() if k != "shared"})

        sw = qp.get("sw", [None])[0]
        sw_ts = qp.get("sw_ts", [None])[0]
        last_ts = st.session_state.get("_last_sw_ts")

        if sw and sw_ts and sw_ts != last_ts:
            st.session_state._last_sw_ts = sw_ts
            # 1회 차감
            if st.session_state.tries_left > 0:
                st.session_state.tries_left -= 1

            # 성공 판정
            try:
                t = float(sw)
            except Exception:
                t = -1.0

            success = (20.260 <= t <= 20.269)
            st.session_state.sw_result = {"t": t, "success": success}

            # sw 파라미터 제거(새로고침 시 반복 차감 방지)
            set_query_params({k: v[0] for k, v in qp.items() if k not in ("sw", "sw_ts")})

        # 결과 표시
        if st.session_state.sw_result:
            t = st.session_state.sw_result["t"]
            success = st.session_state.sw_result["success"]
            st.markdown("### 결과")
            st.write(f"기록: **{t:0.3f}초**")
            if success:
                st.success("성공! 쿠폰지급을 위해 아래 정보를 입력해주세요.")
                with st.form("winner_form"):
                    name = st.text_input("이름")
                    phone = st.text_input("전화번호")
                    submitted = st.form_submit_button("제출")
                if submitted:
                    if not name.strip() or len(phone_normalize(phone)) < 10:
                        st.error("이름과 전화번호를 정확히 입력해주세요.")
                    else:
                        st.success("접수되었습니다. 담당자가 확인 후 안내드립니다.")
            else:
                st.error("아쉽게도 실패! 공유하면 도전기회 1회 추가됩니다. 또는 정수기렌탈 상담신청 후 커피쿠폰 응모!")

        st.markdown("---")
        st.write("성공 구간: **20.260 ~ 20.269초**")
        st.write("성공시 00.000초 기록. 쿠폰지급을 위해 이름, 전화번호 입력해주세요")
        st.write("실패시 00.000초 기록 친구공유시 도전기회 1회추가 또는 정수기렌탈 상담신청 후 커피쿠폰 응모")

        # URL 복사 버튼은 상단 공유 블록에 있음.

if __name__ == "__main__":
    main()
