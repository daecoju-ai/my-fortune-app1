# app.py (v2026.0002)
# - v2026.0001 기준(그라데이션/카드형 UI) "디자인 임의 수정 금지" 준수
# - 변경점(요청사항만):
#   1) 타로: back 흔들림(5초) + mystery 사운드 5초 재생 후 reveal 사운드/앞면 공개
#   2) 타로 클릭 시 화면 위로 튀는 현상 완화(스크롤 위치 저장/복원)
#   3) 띠 운세 문장에 영어키/끝 (숫자) 표기 섞이면 정리
#   4) "DB 연결 확인용" expander 기본 숨김(DEBUG_MODE=False)

import streamlit as st
import streamlit.components.v1 as components
from datetime import date, timedelta
import json
import re
import random
import hashlib
import base64
from pathlib import Path

# =========================================================
# 0) 고정값/버전
# =========================================================
APP_VERSION = "v2026.0002"
APP_URL = "https://my-fortune.streamlit.app"
DANANEUM_LANDING_URL = "https://fascinating-parfait-92a985.netlify.app/"
DEBUG_MODE = False  # DB 연결 확인용 UI 숨김

st.set_page_config(
    page_title="2026 운세 | 띠 + MBTI + 사주 + 오늘/내일 + 타로",
    page_icon="🔮",
    layout="centered",
)

# =========================================================
# 1) 경로/DB 로더
# =========================================================
DATA_DIR = Path("data")

def _load_json_by_candidates(candidates):
    for p in candidates:
        fp = Path(p)
        if fp.exists():
            with open(fp, "r", encoding="utf-8") as f:
                return json.load(f), str(fp)
    raise FileNotFoundError(
        "필수 DB 파일을 찾지 못했습니다.\n"
        + "\n".join([f"- {c}" for c in candidates])
        + "\n\nGitHub에 업로드한 data 폴더 파일명을 다시 확인해주세요."
    )

def load_all_dbs():
    fortunes_year, path_year = _load_json_by_candidates([
        "data/fortunes_ko_2026.json",
        "data/fortunes_ko_2026 (1).json",
    ])
    fortunes_today, path_today = _load_json_by_candidates([
        "data/fortunes_ko_today.json",
        "data/fortunes_ko_today (1).json",
        "data/fortunes_ko_today (2).json",
        "data/fortunes_ko_today (3).json",
    ])
    fortunes_tomorrow, path_tomorrow = _load_json_by_candidates([
        "data/fortunes_ko_tomorrow.json",
        "data/fortunes_ko_tomorrow (1).json",
        "data/fortunes_ko_tomorrow (2).json",
    ])
    lunar_lny, path_lny = _load_json_by_candidates([
        "data/lunar_new_year_1920_2026.json",
    ])
    zodiac_db, path_zodiac = _load_json_by_candidates([
        "data/zodiac_fortunes_ko_2026.json",
        "data/zodiac_fortunes_ko_2026_FIXED.json",
        "data/zodiac_fortunes_ko_2026_FIXED (1).json",
    ])
    mbti_db, path_mbti = _load_json_by_candidates([
        "data/mbti_traits_ko.json",
    ])
    saju_db, path_saju = _load_json_by_candidates([
        "data/saju_ko.json",
    ])
    tarot_db, path_tarot = _load_json_by_candidates([
        "data/tarot_db_ko.json",
        "data/tarot_db_ko (1).json",
        "tarot_db_ko (1).json",
        "tarot_db_ko.json",
    ])

    return {
        "fortunes_year": fortunes_year,
        "fortunes_today": fortunes_today,
        "fortunes_tomorrow": fortunes_tomorrow,
        "lunar_lny": lunar_lny,
        "zodiac_db": zodiac_db,
        "mbti_db": mbti_db,
        "saju_db": saju_db,
        "tarot_db": tarot_db,
        "paths": {
            "year": path_year,
            "today": path_today,
            "tomorrow": path_tomorrow,
            "lny": path_lny,
            "zodiac": path_zodiac,
            "mbti": path_mbti,
            "saju": path_saju,
            "tarot": path_tarot,
        }
    }

# =========================================================
# 2) 유틸
# =========================================================
def stable_seed(*parts: str) -> int:
    s = "|".join([str(p) for p in parts])
    h = hashlib.sha256(s.encode("utf-8")).hexdigest()
    return int(h[:12], 16)

def pick_one(pool, seed_int: int):
    if not isinstance(pool, list) or len(pool) == 0:
        return None
    r = random.Random(seed_int)
    return r.choice(pool)

def safe_str(x):
    if x is None:
        return ""
    if isinstance(x, (dict, list)):
        return json.dumps(x, ensure_ascii=False)
    return str(x)

def strip_html_like(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]*>", "", text)
    return text.strip()

def read_file_b64(path: Path) -> str | None:
    """바이너리 파일을 base64로 읽기(이미지/오디오 공용)."""
    try:
        if not path.exists():
            return None
        b = path.read_bytes()
        if not b:
            return None
        return base64.b64encode(b).decode("ascii")
    except Exception:
        return None

def read_image_b64(path: Path) -> str | None:
    """이미지 파일만 base64로 읽기(비이미지는 None)."""
    try:
        if not path.exists():
            return None
        b = path.read_bytes()
        if len(b) < 12:
            return None
        sig = b[:12]
        # PNG, JPG, WEBP(RIFF)
        if not (sig.startswith(b"\x89PNG") or sig.startswith(b"\xFF\xD8") or sig[0:4] == b"RIFF"):
            return None
        return base64.b64encode(b).decode("ascii")
    except Exception:
        return None

# =========================================================
# 3) 음력 설 기준 띠 계산
# =========================================================
ZODIAC_ORDER = ["rat","ox","tiger","rabbit","dragon","snake","horse","goat","monkey","rooster","dog","pig"]
ZODIAC_LABEL_KO = {
    "rat":"쥐띠","ox":"소띠","tiger":"호랑이띠","rabbit":"토끼띠","dragon":"용띠","snake":"뱀띠",
    "horse":"말띠","goat":"양띠","monkey":"원숭이띠","rooster":"닭띠","dog":"개띠","pig":"돼지띠",
}
ZODIAC_EN_TO_KO_INLINE = dict(ZODIAC_LABEL_KO)

def parse_lny_map(lny_json):
    out = {}
    if isinstance(lny_json, dict):
        for y, dstr in lny_json.items():
            try:
                yy = int(str(y))
                a, b, c = str(dstr).split("-")
                out[yy] = date(int(a), int(b), int(c))
            except Exception:
                continue
    return out

def zodiac_key_from_year(gregorian_year: int) -> str:
    idx = (gregorian_year - 4) % 12
    return ZODIAC_ORDER[idx]

def zodiac_by_birth(birth: date, lny_map: dict) -> tuple[str, int]:
    y = birth.year
    lny = lny_map.get(y)
    zodiac_year = y
    if lny and birth < lny:
        zodiac_year = y - 1
    zk = zodiac_key_from_year(zodiac_year)
    return zk, zodiac_year

def normalize_zodiac_text(text: str) -> str:
    """띠 운세 문장에 영어키(예: rooster띠)가 섞여 있으면 한국어로 치환."""
    if not text:
        return text
    t = str(text)
    for en, ko in ZODIAC_EN_TO_KO_INLINE.items():
        t = re.sub(rf"\b{re.escape(en)}\s*띠\b", ko, t, flags=re.IGNORECASE)
        t = re.sub(rf"\b{re.escape(en)}\b", ko.replace("띠",""), t, flags=re.IGNORECASE)
    return t

def strip_trailing_index(text: str) -> str:
    """문장 끝에 붙은 (숫자) 같은 인덱스 표기 제거."""
    if not text:
        return text
    return re.sub(r"\s*\(\d+\)\s*$", "", str(text)).strip()

# =========================================================
# 4) MBTI
# =========================================================
MBTI_TYPES = [
    "INTJ","INTP","ENTJ","ENTP",
    "INFJ","INFP","ENFJ","ENFP",
    "ISTJ","ISFJ","ESTJ","ESFJ",
    "ISTP","ISFP","ESTP","ESFP",
]

MBTI_Q16 = [
    ("EI","사람들과 함께 있을 때 에너지가 올라간다","혼자 있는 시간이 에너지를 채운다"),
    ("EI","처음 보는 사람과도 금방 친해지는 편이다","낯선 사람은 적응 시간이 필요하다"),
    ("EI","생각을 말하면서 정리하는 편이다","생각을 정리한 뒤 말하는 편이다"),
    ("EI","주말엔 약속이 있으면 좋다","주말엔 혼자 쉬고 싶다"),
    ("SN","구체적인 사실/데이터가 편하다","가능성/아이디어가 편하다"),
    ("SN","현재의 현실 문제 해결이 우선이다","미래의 큰 방향이 우선이다"),
    ("SN","경험을 기반으로 판단한다","직감/영감을 믿는 편이다"),
    ("SN","설명은 디테일이 중요하다","설명은 큰 그림이 중요하다"),
    ("TF","결정은 논리/원칙이 우선이다","결정은 사람/상황 배려가 우선이다"),
    ("TF","피드백은 직설이 좋다","피드백은 부드러운 방식이 좋다"),
    ("TF","갈등은 원인-해결이 핵심이다","갈등은 감정-관계가 핵심이다"),
    ("TF","공정함이 최우선이다","조화로움이 최우선이다"),
    ("JP","계획대로 진행해야 마음이 편하다","유연하게 바뀌어도 괜찮다"),
    ("JP","마감 전에 미리 끝내는 편이다","마감 직전에 몰아서 하는 편이다"),
    ("JP","정리/정돈이 되어야 편하다","어수선해도 진행 가능하다"),
    ("JP","일정이 확정되어야 안심된다","상황 따라 바뀌는 게 자연스럽다"),
]

def compute_mbti_from_answers(answers):
    scores = {"EI":0,"SN":0,"TF":0,"JP":0}
    counts = {"EI":0,"SN":0,"TF":0,"JP":0}
    for axis, pick_left in answers:
        if axis in scores:
            counts[axis] += 1
            if pick_left:
                scores[axis] += 1

    def decide(axis, left_char, right_char):
        if counts[axis] == 0:
            return left_char
        return left_char if scores[axis] >= (counts[axis]/2) else right_char

    mbti = decide("EI","E","I")+decide("SN","S","N")+decide("TF","T","F")+decide("JP","J","P")
    return mbti if mbti in MBTI_TYPES else "ENFP"

def get_mbti_trait_text(mbti_db: dict, mbti: str) -> str:
    """
    mbti_traits_ko.json 구조 대응:
    - {"traits": {"ENFP": {...}} , ...}
    - {"ENFP": "..."} 형태도 대응
    """
    if not isinstance(mbti_db, dict):
        return ""
    if "traits" in mbti_db and isinstance(mbti_db["traits"], dict):
        t = mbti_db["traits"].get(mbti)
        if isinstance(t, str):
            return t
        if isinstance(t, dict):
            kw = t.get("keywords") or t.get("키워드") or []
            tips = t.get("tips") or t.get("action_tips") or []
            parts = []
            if isinstance(kw, list) and kw:
                parts.append("키워드: " + " · ".join([strip_html_like(str(x)) for x in kw][:6]))
            if isinstance(tips, list) and tips:
                parts.append(json.dumps([strip_html_like(str(x)) for x in tips][:6], ensure_ascii=False))
            return " ".join(parts).strip()
        return ""
    v = mbti_db.get(mbti, "")
    return strip_html_like(safe_str(v))

# =========================================================
# 5) 친구 공유 (URL 복사 포함)
# =========================================================
def share_block():
    share_html = f"""
<div style="text-align:center; margin: 12px 0 6px 0;">
  <button id="btnShare" style="
    width:100%;
    border:none;border-radius:999px;
    padding:14px 16px;
    font-weight:900;
    background:#6b4fd6;color:white;
    cursor:pointer;
    box-shadow: 0 10px 26px rgba(0,0,0,0.10);
  ">친구에게 공유하기</button>
</div>

<div style="text-align:center; margin: 10px 0 0 0;">
  <button id="btnCopy" style="
    width:100%;
    border:1px solid rgba(120,90,210,0.25);
    border-radius:999px;
    padding:12px 16px;
    font-weight:900;
    background: rgba(255,255,255,0.85);
    color:#2b2350;
    cursor:pointer;
  ">URL 복사</button>
</div>

<div id="copy_toast" style="
  display:none;
  margin-top: 10px;
  font-weight:900;
  color:#2b2350;
  background: rgba(245,245,255,0.85);
  border: 1px solid rgba(130,95,220,0.20);
  border-radius: 14px;
  padding: 10px 12px;
">복사 완료! 카톡/문자에 붙여넣기 하세요.</div>

<script>
(function() {{
  const url = {json.dumps(APP_URL, ensure_ascii=False)};
  const btnShare = document.getElementById("btnShare");
  const btnCopy = document.getElementById("btnCopy");
  const toast = document.getElementById("copy_toast");

  btnShare.addEventListener("click", async () => {{
    try {{
      if (!navigator.share) {{
        await navigator.clipboard.writeText(url);
        toast.style.display = "block";
        return;
      }}
      await navigator.share({{ title: "2026 운세", text: url, url }});
    }} catch (e) {{
      try {{
        await navigator.clipboard.writeText(url);
        toast.style.display = "block";
      }} catch (e2) {{}}
    }}
  }});

  btnCopy.addEventListener("click", async () => {{
    try {{
      await navigator.clipboard.writeText(url);
      toast.style.display = "block";
    }} catch (e) {{
      const ta = document.createElement("textarea");
      ta.value = url;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
      toast.style.display = "block";
    }}
  }});
}})();
</script>
"""
    components.html(share_html, height=170)

# =========================================================
# 6) 타로 (하루 동안 고정 + back→shake→reveal + 효과음)
# =========================================================
def get_tarot_of_day(tarot_db: dict, user_seed: int, today_: date):
    """타로카드 1장 (하루 고정).
    - DB가 78장(메이저+마이너) 전부 들어있으면 전체 풀에서 랜덤 선택
    - 기존 구조(majors/cards/list)도 그대로 호환
    """
    cards_raw = []

    # 1) 가장 흔한 구조: {"cards":[...]} 또는 list
    if isinstance(tarot_db, dict) and isinstance(tarot_db.get("cards"), list):
        cards_raw = tarot_db["cards"]
    elif isinstance(tarot_db, list):
        cards_raw = tarot_db
    else:
        # 2) 기존 majors 호환
        if isinstance(tarot_db, dict) and isinstance(tarot_db.get("majors"), list):
            cards_raw.extend(tarot_db.get("majors", []))

        # 3) 마이너 아르카나/기타 키들까지 전부 흡수 (list of dict)
        if isinstance(tarot_db, dict):
            for k, v in tarot_db.items():
                if k in ("cards", "majors"):
                    continue
                if isinstance(v, list) and v and all(isinstance(x, dict) for x in v):
                    cards_raw.extend(v)

    cleaned = []
    for c in cards_raw:
        if not isinstance(c, dict):
            continue
        name = c.get("name_ko") or c.get("name") or c.get("title") or c.get("card")
        img = c.get("image") or c.get("img") or ""
        meaning = ""
        if isinstance(c.get("upright"), dict) and c["upright"].get("summary"):
            meaning = c["upright"]["summary"]
        else:
            meaning = c.get("meaning") or c.get("desc") or c.get("text") or ""
        if name and meaning:
            cleaned.append({
                "name": strip_html_like(str(name)),
                "meaning": strip_html_like(str(meaning)),
                "image": str(img).strip()
            })

    if not cleaned:
        return None

    # ✅ 하루 고정: (날짜 + 사용자 seed)로 선택
    seed_int = stable_seed(str(today_), str(user_seed), "tarot")
    r = random.Random(seed_int)
    return r.choice(cleaned)

def _pick_existing_path(candidates: list[str]) -> Path | None:
    for c in candidates:
        p = Path(c)
        if p.exists():
            return p
    return None

def tarot_ui(tarot_db: dict, birth: date, name: str, mbti: str):
    st.markdown("<div class='card tarot-card'>", unsafe_allow_html=True)
    st.markdown("### 🃏 오늘의 타로카드 (하루 1회 가능)", unsafe_allow_html=True)
    st.markdown("<div class='soft-box'>뒷면 카드를 보고 <b>뽑기</b>를 누르면 카드가 공개됩니다. 오늘 하루 동안은 <b>같은 카드(같은 의미/이미지)</b>로 고정됩니다.</div>", unsafe_allow_html=True)

    # back.png
    back_path = _pick_existing_path([
        "assets/tarot/back.png",
        "assets/back.png",
        "back.png",
    ])
    back_b64 = read_image_b64(back_path) if back_path else None

    # 오늘 카드(사용자+날짜로 고정)
    user_seed = stable_seed(str(birth), (name or ""), (mbti or ""))
    card = get_tarot_of_day(tarot_db, user_seed, date.today())

    # 상태
    if "tarot_revealed" not in st.session_state:
        st.session_state.tarot_revealed = False

    # 버튼 클릭 직전 스크롤 저장(JS에서 처리) → rerun 시 복원
    if st.button("타로카드 뽑기", use_container_width=True, key="btn_tarot_draw"):
        st.session_state.tarot_revealed = True
        st.rerun()

    # 이미지 준비
    front_b64 = None
    front_label = ""
    front_meaning = ""
    if card:
        front_label = card["name"]
        front_meaning = card["meaning"]
        img_path = Path(card.get("image", ""))
        if img_path.exists():
            front_b64 = read_image_b64(img_path)

    # back 없으면 앱 죽지 않게 안내
    if not back_b64:
        st.info("tarot back.png 를 찾지 못했습니다. (assets/tarot/back.png 확인)")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    revealed = bool(st.session_state.tarot_revealed)

    # revealed인데 front가 없으면 안내
    if revealed and (not card or not front_b64):
        st.info("타로 DB 또는 이미지 경로를 읽지 못했습니다. (data/tarot_db_ko.json 및 assets/tarot 폴더 확인)")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # 효과음 파일 후보(사용자 폴더 구성 다양성 대응)
    sfx_mystery_path = _pick_existing_path([
        "assets/tarot/mystery.mp3",
        "assets/tarot/sfx_mystery.mp3",
        "assets/mystery.mp3",
        "assets/sfx_mystery.mp3",
        "mystery.mp3",
    ])
    sfx_reveal_path = _pick_existing_path([
        "assets/tarot/reveal.mp3",
        "assets/tarot/sfx_reveal.mp3",
        "assets/reveal.mp3",
        "assets/sfx_reveal.mp3",
        "reveal.mp3",
    ])
    sfx_mystery_b64 = read_file_b64(sfx_mystery_path) if sfx_mystery_path else None
    sfx_reveal_b64 = read_file_b64(sfx_reveal_path) if sfx_reveal_path else None

    def _data_uri(b64: str, mime: str) -> str:
        return f"data:{mime};base64,{b64}"

    back_src = _data_uri(back_b64, "image/png")
    front_src = _data_uri(front_b64, "image/png") if front_b64 else ""

    audio_html = ""
    if revealed:
        if sfx_mystery_b64:
            audio_html += f"<audio id='mystery' src='{_data_uri(sfx_mystery_b64,'audio/mpeg')}'></audio>"
        if sfx_reveal_b64:
            audio_html += f"<audio id='reveal' src='{_data_uri(sfx_reveal_b64,'audio/mpeg')}'></audio>"

    # ✅ 5초 흔들림 + 5초 뒤 공개
    tarot_html = f"""
<div class="tarot-wrap">
  {audio_html}
  <div class="tarot-stage {'revealed' if revealed else ''}">
    <img class="tarot-back" src="{back_src}" alt="tarot back" />
    {"<img class='tarot-front' src='"+front_src+"' alt='tarot front' />" if revealed else ""}
  </div>
</div>

<style>
.tarot-wrap {{
  margin-top: 10px;
}}
.tarot-stage {{
  position: relative;
  width: 100%;
  max-width: 360px;
  margin: 0 auto;
  aspect-ratio: 1 / 1;
}}
.tarot-stage img {{
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 18px;
  box-shadow: 0 12px 32px rgba(0,0,0,0.18);
  border: 1px solid rgba(140,120,200,0.20);
}}
.tarot-back {{
  animation: none;
}}
.tarot-stage.revealed .tarot-back {{
  animation: shake 5s ease-in-out 1;
}}
.tarot-front {{
  opacity: 0;
  transform: scale(0.98);
  animation: popin 0.35s ease-out forwards;
  animation-delay: 5.02s;
}}
@keyframes shake {{
  0% {{ transform: translate(0px,0px) rotate(0deg); }}
  10% {{ transform: translate(-3px,1px) rotate(-1deg); }}
  20% {{ transform: translate(3px,-1px) rotate(1deg); }}
  30% {{ transform: translate(-3px,1px) rotate(-1deg); }}
  40% {{ transform: translate(3px,-1px) rotate(1deg); }}
  50% {{ transform: translate(-3px,1px) rotate(-1deg); }}
  60% {{ transform: translate(3px,-1px) rotate(1deg); }}
  70% {{ transform: translate(-2px,1px) rotate(0deg); }}
  80% {{ transform: translate(2px,-1px) rotate(0deg); }}
  90% {{ transform: translate(-1px,1px) rotate(0deg); }}
  100% {{ transform: translate(0px,0px) rotate(0deg); }}
}}
@keyframes popin {{
  from {{ opacity: 0; transform: scale(0.98); }}
  to   {{ opacity: 1; transform: scale(1.00); }}
}}
</style>

<script>
(function(){{
  // ✅ 스크롤 튐 완화: 복원
  try {{
    const y = localStorage.getItem("scrollY");
    if (y) {{
      window.scrollTo(0, parseInt(y, 10));
      localStorage.removeItem("scrollY");
    }}
  }} catch(e){{}}

  // ✅ revealed 상태면: mystery 5초 → reveal
  const revealed = {str(revealed).lower()};
  if (revealed) {{
    try {{
      const m = document.getElementById("mystery");
      const r = document.getElementById("reveal");
      if (m) {{
        m.volume = 0.85;
        m.currentTime = 0;
        m.play().catch(()=>{{}});
        setTimeout(()=>{{ try{{ m.pause(); }}catch(e){{}} }}, 5000);
      }}
      if (r) {{
        r.volume = 0.95;
        r.currentTime = 0;
        setTimeout(()=>{{ r.play().catch(()=>{{}}); }}, 5000);
      }}
    }} catch(e){{}}
  }}
}})();
</script>
"""
    components.html(tarot_html, height=430 if revealed else 420)

    if revealed and front_label:
        st.markdown(
            f"""
            <div class="reveal">
              <div class="reveal-title">✨ {front_label}</div>
              <div class="reveal-meaning">{front_meaning}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 7) 다나눔렌탈 광고(고정)
# =========================================================
def dananeum_ad_block():
    st.markdown(
        f"""
        <div class="adbox">
          <div class="ad-badge">광고</div>
          <div class="ad-title">[광고] 정수기 렌탈</div>
          <div class="ad-body">
            제휴카드 적용시 <b>월 렌탈비 0원</b>, 설치당일 <b>최대 현금50만원</b> + <b>사은품 증정</b>
          </div>
          <div style="margin-top:12px;">
            <a class="ad-btn" href="{DANANEUM_LANDING_URL}" target="_blank">무료 상담하기</a>
          </div>
          <div class="ad-sub">이름/전화번호 작성 · 개인정보처리방침 동의 후 신청완료</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# 8) 스타일 (그라데이션 + 카드형 고정)
# =========================================================
st.markdown("""
<style>
.block-container { padding-top: 1.0rem; padding-bottom: 2.2rem; max-width: 720px; }

.header-hero {
  border-radius: 22px;
  padding: 18px 16px;
  background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 45%, #8ec5fc 100%);
  color: white;
  text-align: center;
  box-shadow: 0 12px 30px rgba(0,0,0,0.18);
  margin-bottom: 14px;
}
.hero-title { font-size: 1.55rem; font-weight: 900; margin: 0; }
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

.card {
  background: rgba(255,255,255,0.96);
  border-radius: 18px;
  padding: 18px 16px;
  box-shadow: 0 10px 28px rgba(0,0,0,0.10);
  border: 1px solid rgba(140,120,200,0.18);
  margin: 12px 0;
}

.result-card {
  background: linear-gradient(135deg, rgba(245,245,255,0.96), rgba(255,255,255,0.96));
  border-radius: 18px;
  padding: 18px 16px;
  box-shadow: 0 10px 28px rgba(0,0,0,0.10);
  border: 1px solid rgba(140,120,200,0.18);
  margin: 12px 0;
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
  padding: 0.78rem 1.15rem !important;
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
.ad-badge{
  display:inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 900;
  background: rgba(255,140,80,0.18);
  border: 1px solid rgba(255,140,80,0.35);
  color:#c0392b;
}
.ad-title{
  margin-top: 8px;
  font-weight: 900;
  font-size: 1.15rem;
  color:#2b2350;
}
.ad-body{
  margin-top: 8px;
  font-size: 0.98rem;
  color:#2b2350;
  line-height:1.6;
}
.ad-btn{
  display:inline-block;
  background:#ff8c50;
  color:white;
  padding:10px 18px;
  border-radius:999px;
  font-weight:900;
  text-decoration:none;
  box-shadow: 0 10px 26px rgba(0,0,0,0.10);
}
.ad-sub{
  margin-top: 10px;
  font-size: 0.86rem;
  opacity: 0.85;
}

.reveal{
  margin-top: 12px;
  border-radius: 18px;
  padding: 14px 14px;
  background: rgba(245,245,255,0.85);
  border: 1px solid rgba(130,95,220,0.18);
  animation: pop 0.25s ease-out;
}
.reveal-title{
  font-weight: 900;
  font-size: 1.2rem;
  color:#2b2350;
}
.reveal-meaning{
  margin-top: 8px;
  line-height: 1.7;
  color:#1f1747;
}
@keyframes pop{
  from { transform: scale(0.97); opacity: 0.5; }
  to { transform: scale(1.0); opacity: 1; }
}
</style>
""", unsafe_allow_html=True)

# ✅ 전역 스크롤 저장(버튼 클릭 직전 위치 저장)
components.html("""
<script>
(function(){
  document.addEventListener("click", function(){
    try { localStorage.setItem("scrollY", String(window.scrollY || 0)); } catch(e){}
  }, true);
})();
</script>
""", height=0)

# =========================================================
# 9) 세션 상태
# =========================================================
if "stage" not in st.session_state:
    st.session_state.stage = "input"  # input / result
if "name" not in st.session_state:
    st.session_state.name = ""
if "birth" not in st.session_state:
    st.session_state.birth = date(2005, 1, 1)
if "mbti_mode" not in st.session_state:
    st.session_state.mbti_mode = "direct"  # direct / q16
if "mbti" not in st.session_state:
    st.session_state.mbti = "ENFP"

# =========================================================
# 10) 메인 렌더
# =========================================================
def render_input(dbs):
    st.markdown(f"""
    <div class="header-hero">
      <p class="hero-title">🔮 2026 운세 | 띠 + MBTI + 사주 + 오늘/내일 + 타로</p>
      <p class="hero-sub">이름 + 생년월일 + MBTI로 결과가 고정 출력됩니다</p>
      <span class="badge">2026 · {APP_VERSION}</span>
    </div>
    """, unsafe_allow_html=True)

    st.session_state.name = st.text_input("이름", value=st.session_state.name, placeholder="예) 홍길동")

    st.session_state.birth = st.date_input(
        "생년월일",
        value=st.session_state.birth,
        min_value=date(1920, 1, 1),
        max_value=date(2026, 12, 31),
    )

    lny_map = parse_lny_map(dbs["lunar_lny"])
    zk, zy = zodiac_by_birth(st.session_state.birth, lny_map)
    st.markdown(
        f"<div class='card'><b>자동 띠 결정(한국 설 기준)</b><br>"
        f"<div class='soft-box'>당신의 띠: <b>{ZODIAC_LABEL_KO.get(zk, zk)}</b> (기준년도: {zy}년)</div></div>",
        unsafe_allow_html=True
    )

    st.markdown("<div class='card'><b>MBTI</b></div>", unsafe_allow_html=True)

    mode = st.radio(
        "MBTI를 어떻게 할까요?",
        ["직접 선택", "16문항 테스트"],
        index=0 if st.session_state.mbti_mode == "direct" else 1,
        horizontal=True
    )
    st.session_state.mbti_mode = "direct" if mode == "직접 선택" else "q16"

    if st.session_state.mbti_mode == "direct":
        st.session_state.mbti = st.selectbox("MBTI 직접 선택", MBTI_TYPES, index=MBTI_TYPES.index(st.session_state.mbti))
        trait_text = get_mbti_trait_text(dbs["mbti_db"], st.session_state.mbti)
        if trait_text:
            st.markdown(f"<div class='soft-box'><b>{st.session_state.mbti}</b> · {strip_html_like(trait_text)}</div>", unsafe_allow_html=True)

    else:
        st.markdown("<div class='soft-box'>각 문항에서 더 가까운 쪽을 선택하세요. 제출하면 MBTI가 확정됩니다.</div>", unsafe_allow_html=True)
        answers = []
        for i, (axis, left, right) in enumerate(MBTI_Q16, start=1):
            choice = st.radio(
                f"{i}.",
                [left, right],
                key=f"mbti16_{i}"
            )
            answers.append((axis, choice == left))

        if st.button("제출하고 MBTI 확정", use_container_width=True):
            st.session_state.mbti = compute_mbti_from_answers(answers)
            st.success(f"확정된 MBTI: {st.session_state.mbti}")

    st.markdown('<div class="bigbtn">', unsafe_allow_html=True)
    if st.button("운세 보기", use_container_width=True):
        st.session_state.stage = "result"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def render_result(dbs):
    name = (st.session_state.name or "").strip()
    birth = st.session_state.birth
    mbti = st.session_state.mbti or "ENFP"

    lny_map = parse_lny_map(dbs["lunar_lny"])
    zodiac_key, zodiac_year = zodiac_by_birth(birth, lny_map)
    zodiac_label = ZODIAC_LABEL_KO.get(zodiac_key, zodiac_key)

    base_seed = stable_seed(str(birth), name, mbti)

    # 1) 띠별 운세
    zodiac_pool = []
    zdb = dbs["zodiac_db"]
    if isinstance(zdb, dict):
        val = zdb.get(zodiac_key)
        if val is None and isinstance(zdb.get("zodiac"), dict):
            val = zdb["zodiac"].get(zodiac_key)

        if isinstance(val, list):
            zodiac_pool = val
        elif isinstance(val, dict):
            for k in ("items", "lines", "pools"):
                vv = val.get(k)
                if isinstance(vv, list):
                    zodiac_pool = vv
                    break

    zodiac_text = pick_one(
        [strip_trailing_index(normalize_zodiac_text(strip_html_like(safe_str(x)))) for x in zodiac_pool if safe_str(x).strip()],
        stable_seed(str(base_seed), "zodiac")
    )

    # 2) MBTI 특징
    mbti_trait = strip_html_like(get_mbti_trait_text(dbs["mbti_db"], mbti))

    # 3) 사주 한마디 (saju_ko.json: elements 기반)
    saju_text = ""
    sdb = dbs["saju_db"]
    if isinstance(sdb, dict) and isinstance(sdb.get("elements"), list) and sdb["elements"]:
        elements = sdb["elements"]
        idx = stable_seed(str(base_seed), "saju_element") % len(elements)
        el = elements[idx]
        pool = []
        if isinstance(el, dict) and isinstance(el.get("pools"), dict) and isinstance(el["pools"].get("overall"), list):
            pool = el["pools"]["overall"]
        saju_text = pick_one([strip_trailing_index(strip_html_like(str(x))) for x in pool if str(x).strip()],
                             stable_seed(str(base_seed), "saju_overall"))
    else:
        pool = []
        if isinstance(sdb, dict) and isinstance(sdb.get("pools"), dict) and isinstance(sdb["pools"].get("saju"), list):
            pool = sdb["pools"]["saju"]
        saju_text = pick_one([strip_trailing_index(strip_html_like(str(x))) for x in pool if str(x).strip()],
                             stable_seed(str(base_seed), "saju"))

    # 4) 오늘/내일 운세 (날짜 seed → 날짜 바뀌면 다른 내용)
    today = date.today()
    tomorrow = today + timedelta(days=1)

    def get_pool_from_fortune_db(fdb, key_name):
        pool = []
        if isinstance(fdb, dict):
            if isinstance(fdb.get("pools"), dict) and isinstance(fdb["pools"].get(key_name), list):
                pool = fdb["pools"][key_name]
            elif isinstance(fdb.get(key_name), list):
                pool = fdb[key_name]
            elif isinstance(fdb.get("lines"), list):
                pool = fdb["lines"]
        elif isinstance(fdb, list):
            pool = fdb
        return [strip_trailing_index(strip_html_like(safe_str(x))) for x in pool if safe_str(x).strip()]

    today_pool = get_pool_from_fortune_db(dbs["fortunes_today"], "today")
    tomorrow_pool = get_pool_from_fortune_db(dbs["fortunes_tomorrow"], "tomorrow")

    today_text = pick_one(today_pool, stable_seed(str(base_seed), str(today), "today"))
    tomorrow_text = pick_one(tomorrow_pool, stable_seed(str(base_seed), str(tomorrow), "tomorrow"))

    # 5) 2026 전체 운세
    year_pool = []
    ydb = dbs["fortunes_year"]
    if isinstance(ydb, dict):
        if isinstance(ydb.get("pools"), dict) and isinstance(ydb["pools"].get("year_all"), list):
            year_pool = ydb["pools"]["year_all"]
        elif isinstance(ydb.get("year_all"), list):
            year_pool = ydb["year_all"]
        elif isinstance(ydb.get("lines"), list):
            year_pool = ydb["lines"]
    elif isinstance(ydb, list):
        year_pool = ydb

    year_text = pick_one(
        [strip_trailing_index(strip_html_like(safe_str(x))) for x in year_pool if safe_str(x).strip()],
        stable_seed(str(base_seed), "year_2026")
    )

    # 비어있으면 명확히 표시(대체/자동생성 금지)
    def ensure_text(val, label):
        if val and str(val).strip():
            return strip_trailing_index(val)
        return f"{label} 데이터를 DB에서 찾지 못했습니다. (data 폴더 JSON 확인)"

    zodiac_text = ensure_text(zodiac_text, "띠 운세")
    mbti_trait = ensure_text(mbti_trait, "MBTI 특징")
    saju_text = ensure_text(saju_text, "사주 한 마디")
    today_text = ensure_text(today_text, "오늘 운세")
    tomorrow_text = ensure_text(tomorrow_text, "내일 운세")
    year_text = ensure_text(year_text, "2026 전체 운세")

    display_name = f"{name}님의" if name else "당신의"
    st.markdown(
        f"""
        <div class="header-hero">
          <p class="hero-title">{display_name} 운세 결과</p>
          <p class="hero-sub">{zodiac_label} · {mbti} · (설 기준 띠년도 {zodiac_year})</p>
          <span class="badge">2026 · {APP_VERSION}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div class='result-card'>", unsafe_allow_html=True)
    st.markdown(f"**🧧 띠 운세**: {zodiac_text}")
    st.markdown(f"**🧠 MBTI 특징**: {mbti_trait}")
    st.markdown(f"**🧾 사주 한 마디**: {saju_text}")
    st.markdown("---")
    st.markdown(f"**🌞 오늘 운세**: {today_text}")
    st.markdown(f"**🌙 내일 운세**: {tomorrow_text}")
    st.markdown("---")
    st.markdown(f"**📅 2026 전체 운세**: {year_text}")
    st.markdown("</div>", unsafe_allow_html=True)

    share_block()
    dananeum_ad_block()
    tarot_ui(dbs["tarot_db"], birth, name, mbti)

    if st.button("입력 화면으로", use_container_width=True):
        st.session_state.stage = "input"
        st.rerun()

    if DEBUG_MODE:
        with st.expander("DB 연결 상태(확인용)"):
            st.write(dbs["paths"])

# =========================================================
# 11) 실행
# =========================================================

    # === CTA: 미니게임하고 커피쿠폰 받기 (2페이지 맨 아래 강조 버튼) ===
    st.markdown('''
    <div style="margin:24px 0 8px 0; text-align:center;">
      <a href="https://incredible-dusk-20d2b5.netlify.app/" target="_blank" style="text-decoration:none;">
        <div style="
          width:100%;
          padding:18px 14px;
          border-radius:18px;
          background: linear-gradient(135deg, #ffd36a, #ff8c2b);
          color:#1a1a1a;
          font-weight:900;
          font-size:1.1rem;
          box-shadow: 0 8px 22px rgba(0,0,0,0.28);
          animation: pulse 1.4s ease-in-out infinite;
        ">
          🎮 미니게임하고 ☕ 커피쿠폰 받기
        </div>
      </a>
    </div>
    <style>
    @keyframes pulse {
      0% { transform: scale(1); }
      50% { transform: scale(1.05); }
      100% { transform: scale(1); }
    }
    </style>
    ''', unsafe_allow_html=True)

try:
    dbs = load_all_dbs()
except Exception as e:
    st.error(str(e))
    st.stop()

if st.session_state.stage == "input":
    render_input(dbs)
else:
    render_result(dbs)