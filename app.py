import streamlit as st
from datetime import datetime, date, timedelta
import json, os, hashlib, random
import streamlit.components.v1 as components

# ============================================================
# 2026 띠 + MBTI + 사주 + 타로  | 다나눔렌탈
# - Strict DB (no fallback): DB에 없으면 에러로 안내하고 중단
# - 생년월일: 달력(date_input)로 입력
# - 오늘/내일/연간 운세: seed 고정(동일 날짜엔 동일 결과)
# - 미니게임(스톱워치): START/STOP 1회 클릭 후 비활성화 + 1회 도전
# - 공유: Web Share API 시도 → 실패 시 URL 복사 버튼 제공
# ============================================================

APP_TITLE = "2026 띠 + MBTI + 사주 + 타로 운세"
APP_CAPTION = "완전 무료"
AD_TEXT = "다나눔렌탈 1660-2445"

DB_CANDIDATES = [
    "data/fortunes_ko.json",
    "data/fortune_db.json",
    "data/fortunes_ko_seeded.json",
]

MBTI_TYPES = [
    "ISTJ","ISFJ","INFJ","INTJ",
    "ISTP","ISFP","INFP","INTP",
    "ESTP","ESFP","ENFP","ENTP",
    "ESTJ","ESFJ","ENFJ","ENTJ",
]

ZODIAC_ORDER = ["rat","ox","tiger","rabbit","dragon","snake","horse","goat","monkey","rooster","dog","pig"]
ZODIAC_LABELS = {
    "rat":"쥐","ox":"소","tiger":"호랑이","rabbit":"토끼","dragon":"용","snake":"뱀",
    "horse":"말","goat":"양","monkey":"원숭이","rooster":"닭","dog":"개","pig":"돼지",
}

# ------------------------------
# DB
# ------------------------------
@st.cache_data(show_spinner=False)
def load_db():
    for p in DB_CANDIDATES:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f), p
    raise FileNotFoundError("DB 파일을 찾을 수 없습니다. data/fortunes_ko.json 을 업로드/커밋했는지 확인하세요.")

def get_pool(db: dict, *keys: str) -> list:
    pools = db.get("pools", {})
    for k in keys:
        v = pools.get(k)
        if isinstance(v, list) and len(v) > 0:
            return v
    return []

def require_pool(db: dict, label: str, *keys: str) -> list:
    pool = get_pool(db, *keys)
    if not pool:
        st.error(f"DB에 '{label}' 풀이 없습니다. (찾은 키: {', '.join(keys)})\n\n"
                 f"→ data/fortunes_ko.json 의 pools에 해당 리스트를 추가/업로드하세요.\n"
                 f"※ fallback(대체값) 금지 정책이라 여기서 중단합니다.")
        st.stop()
    return pool

def seed_int(*parts) -> int:
    s = "|".join(str(x) for x in parts)
    h = hashlib.sha256(s.encode("utf-8")).hexdigest()
    return int(h[:12], 16)

def pick_seeded(pool: list, seed: int) -> str:
    r = random.Random(seed)
    return r.choice(pool)

# ------------------------------
# Zodiac (solar year 기반; 음력 띠로 바꾸려면 별도 로직 필요)
# ------------------------------
def zodiac_from_year_solar(year: int):
    idx = (year - 1900) % 12
    key = ZODIAC_ORDER[idx]
    return key, ZODIAC_LABELS.get(key, key)

# ------------------------------
# MBTI Quiz (16문항 간단 버전)
# ------------------------------
MBTI_QUESTIONS = [
    ("사람 많은 모임이 끝나면 더 에너지가 생긴다", "E", "I"),
    ("새로운 사람에게 먼저 말을 거는 편이다", "E", "I"),
    ("말하기보다 듣는 게 편하다", "I", "E"),
    ("혼자 있는 시간이 꼭 필요하다", "I", "E"),
    ("사실/경험 기반이 더 믿음직하다", "S", "N"),
    ("상상/아이디어가 자주 떠오른다", "N", "S"),
    ("디테일을 놓치지 않는 편이다", "S", "N"),
    ("큰 그림/가능성을 먼저 본다", "N", "S"),
    ("결정할 때 논리/원칙이 우선이다", "T", "F"),
    ("결정할 때 사람 마음/관계가 우선이다", "F", "T"),
    ("피드백을 직설적으로 하는 편이다", "T", "F"),
    ("상대 기분을 먼저 살핀다", "F", "T"),
    ("계획을 세우고 그대로 하는 게 편하다", "J", "P"),
    ("즉흥적으로 바꾸는 게 편하다", "P", "J"),
    ("마감 전에 여유 있게 끝내고 싶다", "J", "P"),
    ("열어두고 상황 봐서 정한다", "P", "J"),
]

def calc_mbti_from_answers(ans: dict) -> str:
    score = {"E":0,"I":0,"S":0,"N":0,"T":0,"F":0,"J":0,"P":0}
    for i,(q,a,b) in enumerate(MBTI_QUESTIONS):
        v = ans.get(f"q{i}")
        if v == "예":
            score[a]+=1
        elif v == "아니오":
            score[b]+=1
    def pick(a,b): 
        return a if score[a]>=score[b] else b
    return pick("E","I")+pick("S","N")+pick("T","F")+pick("J","P")

# ------------------------------
# Share component (Web Share → fallback copy)
# ------------------------------
def share_component(title: str, text: str):
    # Streamlit 안드로이드/카톡 웹뷰에서 navigator.share가 막히는 경우가 많아,
    # 실패하면 곧바로 URL 복사 버튼으로 우회
    components.html(f"""
    <div style="display:flex; gap:8px; align-items:center;">
      <button id="shareBtn" style="padding:10px 14px; border-radius:10px; border:1px solid #ddd; background:#fff; cursor:pointer;">
        친구에게 공유하기
      </button>
      <button id="copyBtn" style="padding:10px 14px; border-radius:10px; border:1px solid #ddd; background:#fff; cursor:pointer;">
        URL 복사
      </button>
      <span id="msg" style="font-size:12px; color:#666;"></span>
    </div>
    <script>
      const msg = document.getElementById("msg");
      const copyUrl = async () => {{
        try {{
          await navigator.clipboard.writeText(window.location.href);
          msg.textContent = "복사 완료!";
          setTimeout(()=>msg.textContent="", 1500);
        }} catch (e) {{
          msg.textContent = "복사 실패(브라우저 제한). 주소창에서 복사해주세요.";
        }}
      }};
      document.getElementById("copyBtn").addEventListener("click", (e)=>{{ e.preventDefault(); copyUrl(); }});
      document.getElementById("shareBtn").addEventListener("click", async (e)=>{{
        e.preventDefault();
        const payload = {{ title: {json.dumps(title)}, text: {json.dumps(text)}, url: window.location.href }};
        try {{
          if (!navigator.share) throw new Error("no share api");
          await navigator.share(payload);
          msg.textContent = "공유 창 열림";
          setTimeout(()=>msg.textContent="", 1500);
        }} catch (err) {{
          // 카톡 인앱/일부 브라우저에서 share 막힘 → URL 복사로 우회
          await copyUrl();
        }}
      }});
    </script>
    """, height=70)

# ------------------------------
# Stopwatch mini-game component
# ------------------------------
def stopwatch_component(disabled: bool):
    dis = "true" if disabled else "false"
    components.html(f"""
    <div style="max-width:520px;margin:0 auto;padding:16px;border-radius:18px;border:1px solid rgba(0,0,0,0.08);
                box-shadow:0 10px 28px rgba(0,0,0,0.08); background:rgba(255,255,255,0.96);">
      <div style="font-size:22px;font-weight:800;letter-spacing:0.5px;margin-bottom:12px;">⏱️ STOPWATCH</div>
      <div id="time" style="font-size:64px;font-weight:900; text-align:center; padding:14px; border-radius:16px;
                            border:1px solid rgba(80,80,120,0.18); background:rgba(245,246,255,0.9);">00:00.00</div>
      <div style="display:flex; gap:12px; justify-content:center; margin-top:14px;">
        <button id="startBtn" style="flex:1;padding:14px;border-radius:14px;border:0;background:#6C5CE7;color:white;font-weight:800;cursor:pointer;">
          START
        </button>
        <button id="stopBtn" style="flex:1;padding:14px;border-radius:14px;border:0;background:#F2994A;color:white;font-weight:800;cursor:pointer;">
          STOP
        </button>
      </div>
      <div style="margin-top:10px; font-size:14px; color:#333;">
        START 후 STOP을 눌러 기록을 제출하세요.
      </div>
      <div id="hint" style="margin-top:6px; font-size:12px; color:#666;"></div>
    </div>

    <script>
      const disabled = {dis};
      const startBtn = document.getElementById("startBtn");
      const stopBtn  = document.getElementById("stopBtn");
      const timeEl   = document.getElementById("time");
      const hintEl   = document.getElementById("hint");

      let running=false;
      let t0=0;
      let raf=null;

      function fmt(ms) {{
        const s = ms/1000.0;
        const mm = Math.floor(s/60);
        const ss = Math.floor(s%60);
        const cs = Math.floor((s - Math.floor(s))*100);
        const pad2 = (n)=>String(n).padStart(2,"0");
        return `${{pad2(mm)}}:${{pad2(ss)}}.${{pad2(cs)}}`;
      }}

      function tick() {{
        if(!running) return;
        const ms = performance.now() - t0;
        timeEl.textContent = fmt(ms);
        raf = requestAnimationFrame(tick);
      }}

      function setDisabledAll(v) {{
        startBtn.disabled=v;
        stopBtn.disabled=v;
        startBtn.style.opacity = v ? 0.5 : 1;
        stopBtn.style.opacity  = v ? 0.5 : 1;
        startBtn.style.cursor  = v ? "not-allowed" : "pointer";
        stopBtn.style.cursor   = v ? "not-allowed" : "pointer";
      }}

      if (disabled) {{
        setDisabledAll(true);
        hintEl.textContent = "오늘 도전 횟수를 모두 사용했습니다.";
      }}

      startBtn.addEventListener("click", ()=>{{
        if(disabled) return;
        if(running) return;
        running=true;
        t0=performance.now();
        startBtn.disabled=true;               // START 1회 클릭 후 비활성화
        startBtn.style.opacity=0.5;
        startBtn.style.cursor="not-allowed";
        hintEl.textContent = "측정 중... STOP을 누르세요.";
        tick();
      }});

      stopBtn.addEventListener("click", ()=>{{
        if(disabled) return;
        if(!running) return;
        running=false;
        if(raf) cancelAnimationFrame(raf);
        stopBtn.disabled=true;                // STOP 1회 클릭 후 비활성화
        stopBtn.style.opacity=0.5;
        stopBtn.style.cursor="not-allowed";
        hintEl.textContent = "기록을 아래 입력칸에 붙여넣고 제출하세요.";
      }});
    </script>
    """, height=250)

# ------------------------------
# State
# ------------------------------
def init_state():
    st.session_state.setdefault("page", "input")
    st.session_state.setdefault("name", "")
    st.session_state.setdefault("birthdate", date(2000,1,1))
    st.session_state.setdefault("mbti_mode", "dropdown")  # dropdown | quiz
    st.session_state.setdefault("mbti", "ENTJ")
    st.session_state.setdefault("mbti_quiz", {})
    st.session_state.setdefault("result", None)

    # mini-game
    st.session_state.setdefault("max_attempts", 1)
    st.session_state.setdefault("attempts_used", 0)
    st.session_state.setdefault("last_record", None)

def reset_to_input():
    # 입력만 초기화(미니게임 기록/횟수는 유지)
    st.session_state.page = "input"
    st.session_state.result = None

# ------------------------------
# Fortune compute
# ------------------------------
def compute_result(db: dict, name: str, bday: date, mbti: str) -> dict:
    zodiac_key, zodiac_label = zodiac_from_year_solar(bday.year)

    # seed: 생년월일 + mbti + 날짜(오늘/내일/연간)로 고정
    today = date.today()
    seed_base = seed_int(name.strip().lower(), bday.isoformat(), mbti)

    # pools (aliases까지 모두 허용하되, 없으면 중단)
    pool_today    = require_pool(db, "오늘 운세", "today_fortune", "today_fortunes", "today")
    pool_tomorrow = require_pool(db, "내일 운세", "tomorrow_fortune", "tomorrow_fortunes", "tomorrow")
    pool_year     = require_pool(db, "2026 전체 운세", "year_all", "year_overall", "year")

    # 사주 한줄 + 행동팁(옵션)
    pool_saju  = get_pool(db, "saju_one_liner", "saju")
    pool_act   = get_pool(db, "action_tip", "action_tips")
    pool_advice = get_pool(db, "advice", "advices")

    res = {
        "name": name,
        "birthdate": bday.isoformat(),
        "zodiac": zodiac_label,
        "mbti": mbti,
        "today_fortune": pick_seeded(pool_today, seed_int(seed_base, today.isoformat(), "today")),
        "tomorrow_fortune": pick_seeded(pool_tomorrow, seed_int(seed_base, (today+timedelta(days=1)).isoformat(), "tomorrow")),
        "year_all": pick_seeded(pool_year, seed_int(seed_base, "2026", "year")),
        "saju_one_liner": pick_seeded(pool_saju, seed_int(seed_base, "saju")) if pool_saju else "",
        "action_tip": pick_seeded(pool_act, seed_int(seed_base, today.isoformat(), "act")) if pool_act else "",
        "advice": pick_seeded(pool_advice, seed_int(seed_base, today.isoformat(), "adv")) if pool_advice else "",
    }
    return res

# ------------------------------
# Pages
# ------------------------------
def page_input(db_path: str, db: dict):
    st.title(APP_TITLE)
    st.caption(APP_CAPTION)
    st.caption(f"DB 경로: {db_path}")

    st.subheader("기본 정보")
    c1,c2 = st.columns([2,1])
    with c1:
        st.session_state.name = st.text_input("이름(닉네임)", value=st.session_state.name, placeholder="예: 나눔")
    with c2:
        st.session_state.birthdate = st.date_input("생년월일", value=st.session_state.birthdate)

    st.divider()

    st.subheader("MBTI")
    mbti_mode = st.radio("MBTI 입력 방식", ["드롭다운(직접 선택)", "질문 16개(모르면 추천)"], horizontal=True)
    st.session_state.mbti_mode = "dropdown" if "드롭다운" in mbti_mode else "quiz"

    if st.session_state.mbti_mode == "dropdown":
        st.session_state.mbti = st.selectbox("MBTI 선택", MBTI_TYPES, index=MBTI_TYPES.index(st.session_state.mbti) if st.session_state.mbti in MBTI_TYPES else 0)
    else:
        st.write("아래 16문항에 **예/아니오**로 답하면 MBTI를 추천해요.")
        ans = st.session_state.mbti_quiz
        for i,(q,a,b) in enumerate(MBTI_QUESTIONS):
            ans[f"q{i}"] = st.radio(f"{i+1}. {q}", ["선택", "예", "아니오"], horizontal=True, index=["선택","예","아니오"].index(ans.get(f"q{i}","선택")))
        if st.button("MBTI 추천 계산"):
            st.session_state.mbti = calc_mbti_from_answers(ans)
            st.success(f"추천 MBTI: {st.session_state.mbti}")
        st.info(f"현재 선택된 MBTI: {st.session_state.mbti}")

    st.divider()

    colA,colB = st.columns([1,1])
    with colA:
        if st.button("운세 보기", type="primary", use_container_width=True):
            if not st.session_state.name.strip():
                st.warning("이름(닉네임)을 입력해주세요.")
                return
            res = compute_result(db, st.session_state.name, st.session_state.birthdate, st.session_state.mbti)
            st.session_state.result = res
            st.session_state.page = "result"
            st.rerun()
    with colB:
        st.button("다시 입력", on_click=reset_to_input, use_container_width=True)

    st.markdown("---")
    st.markdown(f"**{AD_TEXT}**")

def page_result(db_path: str, db: dict):
    st.title(APP_TITLE)
    st.caption(APP_CAPTION)
    st.caption(f"DB 경로: {db_path}")

    res = st.session_state.result
    if not res:
        st.warning("결과가 없습니다. 다시 입력해주세요.")
        st.session_state.page = "input"
        st.rerun()

    st.subheader("결과")
    st.write(f"**띠 운세:** {res['zodiac']}")
    st.write(f"**MBTI 특징:** {res['mbti']}")

    st.markdown("### 2026 전체 운세")
    st.info(res["year_all"])

    st.markdown("### 오늘 운세")
    st.success(res["today_fortune"])

    st.markdown("### 내일 운세")
    st.success(res["tomorrow_fortune"])

    if res.get("saju_one_liner"):
        st.markdown("### 사주 한줄")
        st.write(res["saju_one_liner"])

    if res.get("action_tip"):
        st.markdown("### 오늘의 액션")
        st.write(res["action_tip"])

    if res.get("advice"):
        st.markdown("### 조언")
        st.write(res["advice"])

    st.divider()
    share_component(APP_TITLE, "내 운세 결과를 확인해봐요!")

    st.divider()
    st.subheader("🎮 스톱워치 미니게임 (1일 1회)")
    remaining = max(0, st.session_state.max_attempts - st.session_state.attempts_used)
    st.write(f"시도횟수: **{remaining}/{st.session_state.max_attempts}**")

    stopwatch_component(disabled=(remaining <= 0))

    record = st.text_input("STOP 후 뜨는 기록(예: 20.163)을 여기에 붙여넣고 제출", value="")
    if st.button("기록 제출", use_container_width=True, disabled=(remaining <= 0)):
        # 단순 숫자 파싱
        s = record.strip()
        s = s.replace(":", "").replace(" ", "")
        try:
            # 지원: "00:20.16" 또는 "20.16"
            if "." in s and s.count(".")==1 and s.replace(".","").isdigit():
                val = float(s)
            else:
                # 00:20.16 형태를 대비(콜론 제거 후 처리)
                val = float(s)
            st.session_state.last_record = val
            st.session_state.attempts_used += 1
            st.success(f"기록: {val:.3f}s")
            st.rerun()
        except Exception:
            st.error("기록 형식이 올바르지 않습니다. 예: 20.16 또는 00:20.16")

    st.divider()
    col1,col2 = st.columns([1,1])
    with col1:
        if st.button("처음부터 다시", use_container_width=True):
            reset_to_input()
            st.rerun()
    with col2:
        st.markdown(f"**{AD_TEXT}**")

# ------------------------------
# Main
# ------------------------------
def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="🔮", layout="centered")
    init_state()

    db, db_path = load_db()

    if st.session_state.page == "input":
        page_input(db_path, db)
    else:
        page_result(db_path, db)

if __name__ == "__main__":
    main()
