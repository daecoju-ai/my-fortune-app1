# app.py
# 2026 운세 (Streamlit) - UI(그라데이션) 고정 + DB(JSON) 기반
# 주의: JS/HTML은 반드시 문자열로만 주입 (Python 문법에 섞지 않기)

import json
import random
from datetime import date, datetime
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


# -----------------------------
# UI (절대 임의 수정 금지 영역)
# -----------------------------
def _inject_ui_gradient():
    st.set_page_config(page_title="2026년 운세", page_icon="✨", layout="centered")

    st.markdown(
        """
<style>
/* 전체 배경 그라데이션 */
.stApp {
  background: radial-gradient(1200px 600px at 30% 10%, rgba(255, 99, 132, 0.15), transparent 60%),
              radial-gradient(1000px 500px at 80% 30%, rgba(54, 162, 235, 0.15), transparent 60%),
              radial-gradient(900px 450px at 40% 80%, rgba(255, 206, 86, 0.12), transparent 60%),
              linear-gradient(180deg, #ffffff 0%, #f6f7fb 100%);
}

/* 헤더 타이포 */
h1, h2, h3, h4 {
  letter-spacing: -0.02em;
}

/* 카드 느낌 */
.block-container {
  padding-top: 2rem;
  padding-bottom: 3rem;
  max-width: 720px;
}

div[data-testid="stTabs"] button {
  font-size: 1.02rem;
  font-weight: 700;
}

div[data-testid="stTabs"] button[aria-selected="true"] {
  color: #e05a5a !important;
  border-bottom: 3px solid #e05a5a !important;
}

div[data-testid="stSelectbox"] > div {
  border-radius: 14px;
}

div[data-testid="stTextInput"] input, div[data-testid="stDateInput"] input {
  border-radius: 14px;
}

.stAlert > div {
  border-radius: 16px;
}
</style>
""",
        unsafe_allow_html=True,
    )


# -----------------------------
# 경로/로더
# -----------------------------
DATA_DIR = Path(__file__).parent / "data"

FILES = {
    "today": DATA_DIR / "fortunes_ko_today.json",
    "tomorrow": DATA_DIR / "fortunes_ko_tomorrow.json",
    "year": DATA_DIR / "fortunes_ko_2026.json",
    "zodiac": DATA_DIR / "zodiac_fortunes_ko_2026.json",
    "lunar_new_year": DATA_DIR / "lunar_new_year_1920_2026.json",
    "mbti": DATA_DIR / "mbti_traits_ko.json",
    "saju": DATA_DIR / "saju_ko.json",
    "tarot": DATA_DIR / "tarot_db_ko.json",
}


@st.cache_data(show_spinner=False)
def load_json(path: Path):
    if not path.exists():
        raise FileNotFoundError(str(path))
    return json.loads(path.read_text(encoding="utf-8"))


def safe_pick(pool):
    """리스트/문자열/딕셔너리 어디든 안전하게 1개 뽑기."""
    if pool is None:
        return None
    if isinstance(pool, str):
        return pool.strip() if pool.strip() else None
    if isinstance(pool, list):
        candidates = [x for x in pool if isinstance(x, str) and x.strip()]
        return random.choice(candidates).strip() if candidates else None
    # dict이면 values에서 문자열 모아 뽑기
    if isinstance(pool, dict):
        candidates = []
        for v in pool.values():
            if isinstance(v, str) and v.strip():
                candidates.append(v.strip())
            elif isinstance(v, list):
                candidates.extend([x.strip() for x in v if isinstance(x, str) and x.strip()])
        return random.choice(candidates) if candidates else None
    return None


# -----------------------------
# 띠 계산 (한국 설 기준)
# -----------------------------
ZODIAC_ORDER = ["rat", "ox", "tiger", "rabbit", "dragon", "snake", "horse", "goat", "monkey", "rooster", "dog", "pig"]
ZODIAC_KO = {
    "rat": "쥐띠",
    "ox": "소띠",
    "tiger": "호랑이띠",
    "rabbit": "토끼띠",
    "dragon": "용띠",
    "snake": "뱀띠",
    "horse": "말띠",
    "goat": "양띠",
    "monkey": "원숭이띠",
    "rooster": "닭띠",
    "dog": "개띠",
    "pig": "돼지띠",
}

def zodiac_from_solar_birth(birth: date, lunar_new_year_table: dict) -> str:
    """
    birth: 양력 생년월일
    lunar_new_year_table: { "years": [{"year": 1920, "date": "1920-02-20"}, ...] } 형태 가정
    - 생일이 해당 연도의 설날(음력 1/1, 한국설) 이전이면 띠는 전년도 기준
    """
    y = birth.year

    # 테이블에서 해당 연도 설날 찾기
    lny_map = {}
    years = lunar_new_year_table.get("years") or lunar_new_year_table.get("data") or lunar_new_year_table.get("items") or []
    for item in years:
        try:
            yy = int(item.get("year"))
            dd = item.get("date")
            if dd:
                lny_map[yy] = datetime.strptime(dd, "%Y-%m-%d").date()
        except Exception:
            continue

    lny = lny_map.get(y)
    zodiac_year = y
    if lny and birth < lny:
        zodiac_year = y - 1

    # 기준년 1900이 쥐띠가 아니므로, 가장 안전하게 1924(쥐) 기준으로 계산
    # 1924년 = 쥐띠
    base_year = 1924
    idx = (zodiac_year - base_year) % 12
    return ZODIAC_ORDER[idx]


# -----------------------------
# MBTI
# -----------------------------
def normalize_mbti(s: str) -> str:
    if not s:
        return ""
    s = re.sub(r"[^A-Za-z]", "", s).upper()
    if len(s) != 4:
        return ""
    return s

def get_mbti_summary(mbti_db: dict, mbti_code: str) -> dict | None:
    """
    mbti_traits_ko.json 구조:
      { "meta":..., "traits": { "ENFP": {...} , ... } }
    """
    traits = (mbti_db.get("traits") or {})
    return traits.get(mbti_code)


# -----------------------------
# 사주(간단): DB에 있는 문장만 가져오기 (계산 최소화)
# -----------------------------
def get_saju_one_liner(saju_db: dict, year_db: dict) -> str | None:
    # fortunes_ko_2026.json 안의 pools.saju_one_liner를 최우선 사용
    pools = year_db.get("pools") or {}
    s = safe_pick(pools.get("saju_one_liner"))
    if s:
        return s
    # fallback: saju_ko.json 안에서 아무 문장 1개
    return safe_pick(saju_db)


# -----------------------------
# Toast + Copy (JS는 components.html로만!)
# -----------------------------
def copy_to_clipboard_block(text_to_copy: str, button_label: str = "복사하기"):
    """
    Streamlit에서 안전하게 클립보드 복사 + 토스트(간단)
    """
    # id 충돌 방지
    rid = str(random.randint(100000, 999999))
    safe_text = json.dumps(text_to_copy)  # JS 문자열로 안전하게
    safe_label = button_label.replace("<", "").replace(">", "")

    html = """
<div style="margin-top:8px; margin-bottom:8px;">
  <button id="btn___RID___"
          style="border:1px solid #e05a5a; color:#e05a5a; background:white; padding:10px 14px; border-radius:12px; font-weight:700; cursor:pointer;">
    ___LABEL___
  </button>

  <div id="toast___RID___"
       style="display:none; margin-top:10px; padding:10px 12px; border-radius:12px; background:rgba(224,90,90,0.12); color:#7b2f2f; font-weight:700;">
    복사 완료!
  </div>
</div>

<script>
(function(){
  const btn = document.getElementById("btn___RID___");
  const toast = document.getElementById("toast___RID___");
  if(!btn) return;

  btn.addEventListener("click", async () => {
    try{
      await navigator.clipboard.writeText(___TEXT___);
      if(toast){
        toast.style.display = "block";
        setTimeout(() => { toast.style.display = "none"; }, 1200);
      }
    }catch(e){
      // 클립보드 권한 실패 시 fallback
      try{
        const ta = document.createElement("textarea");
        ta.value = ___TEXT___;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand("copy");
        document.body.removeChild(ta);
        if(toast){
          toast.innerText = "복사 완료! (fallback)";
          toast.style.display = "block";
          setTimeout(() => { toast.style.display = "none"; }, 1200);
        }
      }catch(e2){}
    }
  });
})();
</script>
"""
    html = html.replace("___RID___", rid).replace("___TEXT___", safe_text).replace("___LABEL___", safe_label)
    components.html(html, height=90)


# -----------------------------
# 메인 렌더
# -----------------------------
def main():
    _inject_ui_gradient()

    st.title("2026년 운세")

    # DB 로드 (파일명/경로는 data 폴더 기준 고정)
    try:
        db_today = load_json(FILES["today"])
        db_tomorrow = load_json(FILES["tomorrow"])
        db_year = load_json(FILES["year"])
        db_zodiac = load_json(FILES["zodiac"])
        db_lny = load_json(FILES["lunar_new_year"])
        db_mbti = load_json(FILES["mbti"])
        db_saju = load_json(FILES["saju"])
        # tarot는 나중에 사용
    except Exception as e:
        st.error(f"필수 DB 파일을 읽을 수 없습니다: {e}")
        st.stop()

    tab_today, tab_tomorrow, tab_year = st.tabs(["오늘의 운세", "내일의 운세", "2026년 전체 운세"])

    # -------------------------
    # 오늘의 운세
    # -------------------------
    with tab_today:
        pools = (db_today.get("pools") or {})
        if not pools:
            st.warning("오늘 DB(pools)가 비어있습니다.")
            st.stop()

        st.subheader("카테고리 선택")
        category = st.selectbox("오늘의 운세 카테고리", list(pools.keys()), index=0)

        text = safe_pick(pools.get(category))
        if not text:
            st.info("표시할 문장이 없습니다. (DB를 확인해 주세요)")
        else:
            st.write(text)

        # 간단 공유용 복사
        copy_to_clipboard_block(text_to_copy=text or "", button_label="문장 복사")

    # -------------------------
    # 내일의 운세
    # -------------------------
    with tab_tomorrow:
        pools = (db_tomorrow.get("pools") or {})
        if not pools:
            st.warning("내일 DB(pools)가 비어있습니다.")
            st.stop()

        st.subheader("카테고리 선택")
        category = st.selectbox("내일의 운세 카테고리", list(pools.keys()), index=0, key="tom_cat")

        text = safe_pick(pools.get(category))
        if not text:
            st.info("표시할 문장이 없습니다. (DB를 확인해 주세요)")
        else:
            st.write(text)

        copy_to_clipboard_block(text_to_copy=text or "", button_label="문장 복사")

    # -------------------------
    # 2026년 전체 운세
    # -------------------------
    with tab_year:
        st.subheader("생년월일 / MBTI")
        birth = st.date_input("생년월일", value=date(2000, 1, 1))
        mbti_in = st.text_input("MBTI (예: ENFP)", value="", placeholder="ENFP").strip()
        mbti_code = normalize_mbti(mbti_in)

        # 2026 전체운세 문장 (DB: fortunes_ko_2026.json)
        year_pools = (db_year.get("pools") or {})

        year_text = safe_pick(year_pools.get("year_all")) or safe_pick(year_pools.get("today")) or safe_pick(year_pools.get("advice"))
        if year_text:
            st.write(year_text)

        st.markdown("### 조언")
        advice = safe_pick(year_pools.get("advice")) or safe_pick(year_pools.get("action_tips")) or safe_pick(year_pools.get("work_study_advices"))
        if advice:
            st.write(f"조언: {advice}")
        else:
            st.write("조언: (내용 없음)")

        # 사주(간단)
        saju_one = get_saju_one_liner(db_saju, db_year)
        if saju_one:
            st.caption(f"사주(간단 참고): {saju_one}")

        # MBTI 요약
        if mbti_code:
            mb = get_mbti_summary(db_mbti, mbti_code)
            if not mb:
                st.warning(f"MBTI DB에 없음: {mbti_code} (data/mbti_traits_ko.json 확인)")
            else:
                st.markdown(f"### {mbti_code} 특징")
                # 핵심만
                if mb.get("one_liner"):
                    st.write(mb["one_liner"])
                bullets = []
                for k in ["strengths", "weaknesses", "tips"]:
                    v = mb.get(k)
                    if isinstance(v, list) and v:
                        bullets.append((k, v[:4]))
                if bullets:
                    for k, arr in bullets:
                        label = {"strengths":"강점", "weaknesses":"주의점", "tips":"팁"}.get(k, k)
                        st.write(f"**{label}**")
                        for x in arr:
                            st.write(f"- {x}")

        # 띠 섹션
        st.markdown("### 띠 선택")
        try:
            auto_z = zodiac_from_solar_birth(birth, db_lny)
        except Exception:
            auto_z = "rat"

        options = list(ZODIAC_ORDER)
        default_idx = options.index(auto_z) if auto_z in options else 0
        z_key = st.selectbox("띠", options=[ZODIAC_KO[o] for o in options], index=default_idx)

        # 선택된 한글을 다시 key로
        selected_animal = options[[ZODIAC_KO[o] for o in options].index(z_key)]

        # zodiac_fortunes 구조: { "rat": { "today":[], "tomorrow":[], "year":[] } ... }
        z_pack = db_zodiac.get(selected_animal) or {}

        z_year_pool = z_pack.get("year") or z_pack.get("year_2026") or z_pack.get("annual") or z_pack.get("yearAll")
        z_text = safe_pick(z_year_pool)

        if not z_text:
            st.info("표시할 문장이 없습니다. (DB를 확인해 주세요)")
        else:
            st.write(z_text)

        copy_to_clipboard_block(text_to_copy=z_text or "", button_label="띠 운세 복사")

        # (타로는 나중에 연결)


if __name__ == "__main__":
    main()
