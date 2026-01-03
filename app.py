import streamlit as st
from datetime import datetime
import json
import os
import random
import re

# =========================================================
# 0) App Config
# =========================================================
APP_URL = "https://my-fortune.streamlit.app"
FORTUNE_DB_PATH = os.path.join("data", "fortunes_ko.json")

st.set_page_config(
    page_title="2026 운세 | 띠 + MBTI + 사주 + 오늘/내일",
    page_icon="🔮",
    layout="centered"
)

# =========================================================
# 1) Helpers
# =========================================================
def normalize_phone(phone: str) -> str:
    return re.sub(r"[^0-9]", "", phone or "")

def inject_seo():
    desc = "2026년 띠운세 + MBTI + 사주 + 오늘/내일 운세 + 타로까지 무료로!"
    kw = "2026 운세, 띠운세, MBTI 운세, 사주, 오늘 운세, 내일 운세, 무료 운세, 타로"
    title = "2026 운세 | 띠 + MBTI + 사주 + 오늘/내일 운세"
    try:
        st.components.v1.html(
            f"""
<script>
(function(){{
  try {{
    const metas = [
      ['name','description',{json.dumps(desc, ensure_ascii=False)}],
      ['name','keywords',{json.dumps(kw, ensure_ascii=False)}],
      ['property','og:title',{json.dumps(title, ensure_ascii=False)}],
      ['property','og:description',{json.dumps(desc, ensure_ascii=False)}],
      ['property','og:type','website'],
      ['property','og:url',{json.dumps(APP_URL, ensure_ascii=False)}],
      ['name','robots','index,follow'],
    ];
    metas.forEach(([attr,key,val])=>{{
      let el = document.head.querySelector(`meta[${{attr}}="${{key}}"]`);
      if(!el){{ el=document.createElement('meta'); el.setAttribute(attr,key); document.head.appendChild(el); }}
      el.setAttribute('content', val);
    }});
  }} catch(e) {{}}
}})();
</script>
""",
            height=0
        )
    except Exception:
        pass

def load_fortune_db():
    if not os.path.exists(FORTUNE_DB_PATH):
        st.error(f"데이터 파일이 없습니다: `{FORTUNE_DB_PATH}` (깃허브에 업로드/커밋 필요)")
        st.stop()
    try:
        with open(FORTUNE_DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        st.error(f"fortunes_ko.json 파싱 실패: {e}")
        st.stop()
    return data

def calc_zodiac_animal(year: int) -> str:
    # 네 DB 키(쥐/소/호랑이/토끼/용/뱀/말/양/원숭이/닭/개/돼지) 기준으로 맞춤
    animals = ["쥐","소","호랑이","토끼","용","뱀","말","양","원숭이","닭","개","돼지"]
    return animals[(year - 4) % 12]

def get_combo_key(year: int, mbti: str) -> str:
    return f"{calc_zodiac_animal(year)}_{mbti}"

def list_available_combos(db: dict, zodiac_animal: str) -> list:
    # DB에서 해당 띠로 시작하는 키만 모아줌 (디버그 도움)
    prefix = f"{zodiac_animal}_"
    keys = [k for k in db.keys() if isinstance(k, str) and k.startswith(prefix)]
    keys.sort()
    return keys

def validate_record(record: dict) -> list:
    # 네 스샷에 보이는 필드 기준
    required = [
        "zodiac_fortune","mbti_trait","mbti_influence","saju_message",
        "today","tomorrow","year_2026","love","money","work","health",
        "lucky_point","action_tip","caution"
    ]
    missing = [k for k in required if k not in record]
    # lucky_point 내부도 체크
    if "lucky_point" in record and isinstance(record["lucky_point"], dict):
        for k in ["color","item","number","direction"]:
            if k not in record["lucky_point"]:
                missing.append(f"lucky_point.{k}")
    return missing

# =========================================================
# 2) UI Text + Style (네가 좋아한 디자인 유지)
# =========================================================
t = {
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
    "tarot_btn": "오늘의 타로 카드 뽑기",
    "sections": {
        "zodiac": "띠 운세",
        "mbti": "MBTI 특징",
        "mbti_influence": "MBTI가 운세에 미치는 영향",
        "saju": "사주 한 마디",
        "today": "오늘 운세",
        "tomorrow": "내일 운세",
        "year_all": "2026 전체 운세",
        "love": "연애운",
        "money": "재물운",
        "work": "일/학업운",
        "health": "건강운",
        "lucky": "행운 포인트",
        "action": "오늘의 액션팁",
        "caution": "주의할 점",
    },
}

MBTI_LIST = [
    "INTJ","INTP","ENTJ","ENTP",
    "INFJ","INFP","ENFJ","ENFP",
    "ISTJ","ISFJ","ESTJ","ESFJ",
    "ISTP","ISFP","ESTP","ESFP"
]

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
.bigbtn > button {
  border-radius: 999px !important;
  font-weight: 900 !important;
  padding: 0.75rem 1.2rem !important;
}
hr.soft { border:0; height:1px; background: rgba(120, 90, 210, 0.15); margin: 14px 0; }
</style>
""", unsafe_allow_html=True)

inject_seo()

# =========================================================
# 3) Session State
# =========================================================
if "stage" not in st.session_state: st.session_state.stage = "input"
if "name" not in st.session_state: st.session_state.name = ""
if "y" not in st.session_state: st.session_state.y = 2005
if "m" not in st.session_state: st.session_state.m = 1
if "d" not in st.session_state: st.session_state.d = 1
if "mbti" not in st.session_state: st.session_state.mbti = "ENFP"
if "mbti_mode" not in st.session_state: st.session_state.mbti_mode = "direct"

# =========================================================
# 4) DB Load
# =========================================================
DB = load_fortune_db()

# =========================================================
# 5) Screens
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
    st.session_state.mbti = st.selectbox("MBTI", MBTI_LIST, index=MBTI_LIST.index(st.session_state.mbti))

    st.markdown('<div class="bigbtn">', unsafe_allow_html=True)
    if st.button(t["go_result"], use_container_width=True):
        st.session_state.stage = "result"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def render_result():
    s = t["sections"]
    y = st.session_state.y
    mbti = st.session_state.mbti
    zodiac_animal = calc_zodiac_animal(y)
    combo = get_combo_key(y, mbti)

    # ✅ 조합 레코드 조회 (없으면 생성하지 않고 정확히 안내)
    if combo not in DB:
        st.error(f"데이터에 조합 키가 없습니다: **{combo}**")
        avail = list_available_combos(DB, zodiac_animal)
        if avail:
            st.info(f"현재 DB에 있는 '{zodiac_animal}_XXXX' 키 예시(일부):\n\n- " + "\n- ".join(avail[:12]))
        else:
            st.info(f"DB에서 '{zodiac_animal}_' 로 시작하는 키가 하나도 없습니다. (띠 이름 표기가 다른지 확인 필요)")
        st.stop()

    record = DB[combo]
    if not isinstance(record, dict):
        st.error(f"{combo} 값이 dict가 아닙니다. JSON 구조를 확인해주세요.")
        st.stop()

    missing = validate_record(record)
    if missing:
        st.error("레코드에 필수 필드가 누락되었습니다.\n\n누락:\n- " + "\n- ".join(missing))
        st.stop()

    name = (st.session_state.name or "").strip()
    display_name = f"{name}님" if name else ""

    st.markdown(f"""
    <div class="header-hero">
      <p class="hero-title">{display_name} 2026년 운세</p>
      <p class="hero-sub">{zodiac_animal}띠 · {mbti}</p>
      <span class="badge">2026</span>
    </div>
    """, unsafe_allow_html=True)

    # ✅ “태그처럼 보임” 방지: 텍스트는 일반 markdown으로만 출력
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"**{s['zodiac']}**: {record['zodiac_fortune']}")
    st.markdown(f"**{s['mbti']}**: {record['mbti_trait']}")
    st.markdown(f"**{s['mbti_influence']}**: {record['mbti_influence']}")
    st.markdown(f"**{s['saju']}**: {record['saju_message']}")
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown(f"**{s['today']}**: {record['today']}")
    st.markdown(f"**{s['tomorrow']}**: {record['tomorrow']}")
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown(f"**{s['year_all']}**: {record['year_2026']}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"**{s['love']}**: {record['love']}")
    st.markdown(f"**{s['money']}**: {record['money']}")
    st.markdown(f"**{s['work']}**: {record['work']}")
    st.markdown(f"**{s['health']}**: {record['health']}")
    st.markdown("</div>", unsafe_allow_html=True)

    lp = record["lucky_point"]
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"**{s['lucky']}**")
    st.markdown(f"- color: **{lp['color']}**")
    st.markdown(f"- item: **{lp['item']}**")
    st.markdown(f"- number: **{lp['number']}**")
    st.markdown(f"- direction: **{lp['direction']}**")
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown(f"**{s['action']}**: {record['action_tip']}")
    st.markdown(f"**{s['caution']}**: {record['caution']}")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button(t["reset"], use_container_width=True):
        st.session_state.stage = "input"
        st.rerun()

# =========================================================
# 6) Router
# =========================================================
if st.session_state.stage == "input":
    render_input()
else:
    render_result()
