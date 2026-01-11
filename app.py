# app.py (v2026.0003)
# - 디자인 큰 틀 유지(그라데이션/카드형)
# - DB는 data/의 JSON만 사용 (자동 생성/ fallback 문구 금지)
# - MBTI/사주/띠 DB 인식 오류 수정
# - 타로: back.png 표시 → 뽑기 클릭 시 흔들림 + 효과음 + 앞면 공개(하루 동안 고정, "하루 1회 가능" 멘트 유지)
# - 타로 클릭 후 화면 위로 튀는 현상 완화(스크롤 위치 복원)

import streamlit as st

# -----------------------------
# Session state defaults
# -----------------------------
if "stage" not in st.session_state:
    st.session_state.stage = "input"

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
APP_VERSION = "v2026.0004"
APP_URL = "https://my-fortune.streamlit.app"
DANANEUM_LANDING_URL = "https://incredible-dusk-20d2b5.netlify.app/"

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

def read_image_b64(path: Path) -> str | None:
    try:
        if not path.exists():
            return None
        b = path.read_bytes()
        # streamlit에서 TypeError 나는 경우(파일이 이미지가 아닌 경우)를 예방: 간단 시그니처 체크
        if len(b) < 12:
            return None
        sig = b[:12]
        # PNG, JPG, WEBP
        if not (sig.startswith(b"\x89PNG") or sig.startswith(b"\xFF\xD8") or sig[0:4] == b"RIFF"):
            # 확실치 않으면 그래도 시도는 하되, 너무 이상하면 None
            pass
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
ZODIAC_EN_TO_KO_INLINE = {
    "rat": "쥐띠", "ox": "소띠", "tiger": "호랑이띠", "rabbit": "토끼띠", "dragon": "용띠", "snake": "뱀띠",
    "horse": "말띠", "goat": "양띠", "monkey": "원숭이띠", "rooster": "닭띠", "dog": "개띠", "pig": "돼지띠",
}

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
    t = text
    # rooster띠 / rooster etc
    for en, ko in ZODIAC_EN_TO_KO_INLINE.items():
        t = re.sub(rf"\b{re.escape(en)}\s*띠\b", ko, t, flags=re.IGNORECASE)
        t = re.sub(rf"\b{re.escape(en)}\b", ko.replace("띠",""), t, flags=re.IGNORECASE)
    return t

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
    # flat map fallback
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
    majors = []
    if isinstance(tarot_db, dict) and isinstance(tarot_db.get("majors"), list):
        majors = tarot_db["majors"]
    elif isinstance(tarot_db, dict) and isinstance(tarot_db.get("cards"), list):
        majors = tarot_db["cards"]
    elif isinstance(tarot_db, list):
        majors = tarot_db

    cleaned = []
    for c in majors:
        if not isinstance(c, dict):
            continue
        name = c.get("name_ko") or c.get("name") or c.get("title") or c.get("card")
        img = c.get("image") or c.get("img") or ""
        # 의미는 upright.summary 우선
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

    seed_int = stable_seed(str(today_), str(user_seed), "tarot")
    r = random.Random(seed_int)
    return r.choice(cleaned)


def tarot_ui(tarot_db: dict, birth: str, name: str, mbti: str):
    """
    - 하루 1회(하루 동안 동일 카드 고정): 날짜 단위로 seed를 고정해서 카드/이미지/해석이 하루 내내 동일
    - "뽑기" 버튼 클릭 시 화면이 위로 튀는 문제 방지: Streamlit rerun 버튼 대신, HTML 내부 버튼으로 처리(리런 없이 애니메이션/사운드/이미지 전환)
    - back.png가 미스테리한 배경음 + 흔들림 → 웅장한 소리 + 앞면 공개
    """
    import base64, random, datetime
    import streamlit.components.v1 as components

    st.subheader("🃏 오늘의 타로카드 (하루 1회 가능)")
    st.caption("뒷면 카드를 보고 **뽑기**를 누르면 오늘의 카드가 공개됩니다. "
               "오늘 하루 동안은 **같은 카드(같은 의미/이미지)**로 고정됩니다.")

    # --- 날짜 기준 고정(seed) ---
    today = datetime.date.today().isoformat()
    ss = st.session_state

    # seed는 (이름/생년월일/mbti/날짜) 기반 → 같은 사용자는 하루 동안 고정, 다음날 바뀜
    base_seed = f"{(name or '').strip()}|{(birth or '').strip()}|{(mbti or '').strip()}|{today}"
    if ss.get("tarot_day") != today or ss.get("tarot_seed") != base_seed:
        ss["tarot_day"] = today
        ss["tarot_seed"] = base_seed
        ss.pop("tarot_pick", None)
        ss.pop("tarot_revealed", None)

    rng = random.Random(base_seed)

    # --- 카드 1장 선택(하루 고정) ---
    if "tarot_pick" not in ss:
        # tarot_db 구조: {"cards":[...]} 또는 {"major":[...], "minor":[...]} 등 다양할 수 있으니 유연하게
        cards = []
        if isinstance(tarot_db, dict):
            if isinstance(tarot_db.get("cards"), list):
                cards = tarot_db["cards"]
            else:
                # flatten: dict 안의 list들을 모으기
                for v in tarot_db.values():
                    if isinstance(v, list):
                        cards.extend(v)
        if not cards:
            st.error("타로 DB(cards)를 찾지 못했습니다. tarot_db_ko.json 구조 확인 필요")
            return
        ss["tarot_pick"] = rng.choice(cards)

    pick = ss["tarot_pick"]

    # --- 이미지 경로/텍스트 추출(다양한 키 대응) ---
    img_rel = pick.get("image") or pick.get("img") or pick.get("path") or ""
    title = pick.get("title") or pick.get("name") or pick.get("card") or "오늘의 카드"
    meaning = pick.get("meaning") or pick.get("desc") or pick.get("description") or ""
    keywords = pick.get("keywords") or pick.get("tags") or []
    if isinstance(keywords, str):
        keywords = [keywords]

    # --- 파일 읽기(이미지/사운드) ---
    back_path = Path("tarot/back.png")
    front_path = Path(img_rel) if img_rel else None

    def _b64_bytes(path: Path) -> str:
        return base64.b64encode(path.read_bytes()).decode("utf-8")

    if not back_path.exists():
        st.error("tarot/back.png 파일을 찾지 못했습니다. 경로: tarot/back.png")
        return
    if not front_path or not front_path.exists():
        st.error(f"타로 앞면 이미지 파일을 찾지 못했습니다: {img_rel} (tarot_db_ko.json의 image/path 확인)")
        return

    back_b64 = _b64_bytes(back_path)
    front_b64 = _b64_bytes(front_path)

    # 사운드 파일은 (사용자 요청대로) assets 폴더 루트에 둔 것으로 가정
    sfx_mystery = Path("assets/mystery.mp3")
    sfx_reveal = Path("assets/reveal.mp3")

    mystery_b64 = _b64_bytes(sfx_mystery) if sfx_mystery.exists() else ""
    reveal_b64 = _b64_bytes(sfx_reveal) if sfx_reveal.exists() else ""

    # --- 카드 UI (리런 없이 JS로 애니메이션/사운드/전환) ---
    # 크기: 모바일에서 보기 좋게 최대 폭 520px, 비율 고정, 공간(높이) 고정 → 레이아웃 점프 최소화
    html = f"""
    <style>
      .tarot-wrap {{
        max-width: 520px; margin: 0 auto;
        user-select: none;
      }}
      .tarot-stage {{
        position: relative;
        width: 100%;
        aspect-ratio: 1 / 1;
        border-radius: 22px;
        overflow: hidden;
        box-shadow: 0 16px 40px rgba(0,0,0,.12);
        background: #111;
      }}
      .tarot-img {{
        width: 100%; height: 100%;
        object-fit: cover;
        display: block;
      }}
      .tarot-front {{
        position:absolute; inset:0;
        opacity:0;
        transform: scale(1.02);
        transition: opacity .45s ease, transform .45s ease;
      }}
      .tarot-back {{
        position:absolute; inset:0;
        opacity:1;
        transition: opacity .25s ease;
      }}
      .tarot-stage.shake .tarot-back {{
        animation: tarot-shake 1.6s ease-in-out infinite;
        filter: brightness(1.02) contrast(1.02);
      }}
      @keyframes tarot-shake {{
        0% {{ transform: translate(0px,0px) rotate(0deg) scale(1); }}
        10% {{ transform: translate(-2px, 1px) rotate(-0.9deg) scale(1.01); }}
        20% {{ transform: translate( 2px,-1px) rotate( 1.1deg) scale(1.01); }}
        30% {{ transform: translate(-3px, 2px) rotate(-1.4deg) scale(1.02); }}
        40% {{ transform: translate( 3px,-2px) rotate( 1.4deg) scale(1.02); }}
        50% {{ transform: translate(-2px, 2px) rotate(-1.0deg) scale(1.015); }}
        60% {{ transform: translate( 2px,-2px) rotate( 1.0deg) scale(1.015); }}
        70% {{ transform: translate(-1px, 1px) rotate(-0.6deg) scale(1.01); }}
        80% {{ transform: translate( 1px,-1px) rotate( 0.6deg) scale(1.01); }}
        90% {{ transform: translate(-1px, 0px) rotate(-0.3deg) scale(1.005); }}
        100% {{ transform: translate(0px,0px) rotate(0deg) scale(1); }}
      }}
      .tarot-controls {{
        display:flex; gap:10px; margin-top: 14px;
      }}
      .tarot-btn {{
        flex:1;
        padding: 14px 14px;
        border-radius: 14px;
        border: 0;
        font-weight: 800;
        font-size: 16px;
        cursor: pointer;
        background: linear-gradient(135deg,#5b56ff,#ff78c8);
        color: white;
        box-shadow: 0 10px 24px rgba(91,86,255,.25);
      }}
      .tarot-btn:disabled {{
        opacity: .55; cursor: not-allowed; box-shadow: none;
      }}
      .tarot-note {{
        margin-top: 12px;
        padding: 14px 14px;
        border-radius: 14px;
        background: rgba(240,242,255,.9);
        border: 1px dashed rgba(80,90,160,.25);
        color: #27305a;
        line-height: 1.5;
        font-size: 14px;
        display:none;
      }}
      .tarot-note.show {{ display:block; }}
      .tarot-title {{
        font-weight: 900;
        font-size: 18px;
        margin-bottom: 8px;
      }}
      .tarot-kws {{
        opacity:.9;
        margin-top: 8px;
      }}
      /* 스크롤 점프 방지: 버튼 클릭 시 현재 위치 고정 */
      html, body {{ scroll-behavior: auto !important; }}
    </style>

    <div class="tarot-wrap" id="tarot-wrap">
      <div class="tarot-stage" id="tarot-stage">
        <div class="tarot-back" id="tarot-back">
          <img class="tarot-img" src="data:image/png;base64,{back_b64}" alt="tarot-back"/>
        </div>
        <div class="tarot-front" id="tarot-front">
          <img class="tarot-img" src="data:image/png;base64,{front_b64}" alt="tarot-front"/>
        </div>
      </div>

      <div class="tarot-controls">
        <button class="tarot-btn" id="tarot-btn">타로카드 뽑기</button>
      </div>

      <div class="tarot-note" id="tarot-note">
        <div class="tarot-title">🃏 {title}</div>
        <div>{meaning}</div>
        {"<div class='tarot-kws'><b>키워드</b>: " + " · ".join([str(k) for k in keywords]) + "</div>" if keywords else ""}
      </div>

      <audio id="aud-mystery" preload="auto" {"src='data:audio/mp3;base64," + mystery_b64 + "'" if mystery_b64 else ""}></audio>
      <audio id="aud-reveal" preload="auto" {"src='data:audio/mp3;base64," + reveal_b64 + "'" if reveal_b64 else ""}></audio>
    </div>

    <script>
      const btn = document.getElementById("tarot-btn");
      const stage = document.getElementById("tarot-stage");
      const front = document.getElementById("tarot-front");
      const note = document.getElementById("tarot-note");
      const audMystery = document.getElementById("aud-mystery");
      const audReveal = document.getElementById("aud-reveal");

      let revealed = false;

      function safePlay(aud) {{
        if (!aud || !aud.src) return;
        try {{
          aud.currentTime = 0;
          const p = aud.play();
          if (p && p.catch) p.catch(()=>{{}});
        }} catch(e) {{}}
      }}

      btn.addEventListener("click", () => {{
        if (revealed) return;

        // 클릭 순간 스크롤 위치를 고정(위로 튀는 느낌 최소화)
        const y = window.scrollY || document.documentElement.scrollTop || 0;
        window.scrollTo(0, y);

        btn.disabled = true;

        // 1) 미스테리 사운드 + 흔들림 시작
        safePlay(audMystery);
        stage.classList.add("shake");

        // 2) 1.8초 후 공개(웅장 사운드 + 앞면)
        setTimeout(() => {{
          stage.classList.remove("shake");
          safePlay(audReveal);
          front.style.opacity = 1;
          front.style.transform = "scale(1)";
          note.classList.add("show");
          revealed = true;
        }}, 1800);
      }});
    </script>
    """

    # components.html height는 카드(정사각) + 버튼 + 설명 영역까지 여유있게
    components.html(html, height=820)
def render_input(dbs):
    """입력 화면"""
    # 기본값
    if "name" not in st.session_state:
        st.session_state.name = ""
    if "birth" not in st.session_state:
        st.session_state.birth = "2005/01/01"
    if "mbti" not in st.session_state:
        st.session_state.mbti = "ENFP"

    st.markdown("## 🔮 2026 운세 생성기")
    st.caption("이름·생년월일·MBTI를 입력하면 결과가 생성됩니다.")

    with st.form("input_form", clear_on_submit=False):
        name = st.text_input("이름", value=st.session_state.name, placeholder="예) 김성흥")
        birth = st.text_input("생년월일", value=st.session_state.birth, placeholder="YYYY/MM/DD")
        mbti_list = [
            "ISTJ","ISFJ","INFJ","INTJ",
            "ISTP","ISFP","INFP","INTP",
            "ESTP","ESFP","ENFP","ENTP",
            "ESTJ","ESFJ","ENFJ","ENTJ",
        ]
        mbti = st.selectbox("MBTI", options=mbti_list, index=mbti_list.index(st.session_state.mbti) if st.session_state.mbti in mbti_list else 10)
        submitted = st.form_submit_button("운세 보기", use_container_width=True)

    if submitted:
        st.session_state.name = (name or "").strip()
        st.session_state.birth = (birth or "").strip()
        st.session_state.mbti = (mbti or "").strip().upper()

        # 결과 화면으로
        st.session_state.stage = "result"
        st.rerun()

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
        # 1) direct key (키 mismatch 방지)
        zinfo = normalize_zodiac_key(zodiac_key)
        zodiac_key_display = zinfo["display"]

        def _lookup(dd: dict, k: str):
            v = dd.get(k)
            if v is None and isinstance(dd.get("zodiac"), dict):
                v = dd["zodiac"].get(k)
            return v

        val = None
        for _k in zinfo["candidates"]:
            val = _lookup(zdb, _k)
            if val is not None:
                break
        if isinstance(val, list):
            zodiac_pool = val
        elif isinstance(val, dict):
            for k in ("items", "lines", "pools"):
                vv = val.get(k)
                if isinstance(vv, list):
                    zodiac_pool = vv
                    break

    zodiac_text = pick_one(
        [normalize_zodiac_text(strip_html_like(safe_str(x))) for x in zodiac_pool if safe_str(x).strip()],
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
        # overall 풀에서 1줄
        pool = []
        if isinstance(el, dict) and isinstance(el.get("pools"), dict) and isinstance(el["pools"].get("overall"), list):
            pool = el["pools"]["overall"]
        saju_text = pick_one([strip_html_like(str(x)) for x in pool if str(x).strip()], stable_seed(str(base_seed), "saju_overall"))
    else:
        # 다른 구조 대비(이전 버전 호환)
        pool = []
        if isinstance(sdb, dict) and isinstance(sdb.get("pools"), dict) and isinstance(sdb["pools"].get("saju"), list):
            pool = sdb["pools"]["saju"]
        saju_text = pick_one([strip_html_like(str(x)) for x in pool if str(x).strip()], stable_seed(str(base_seed), "saju"))

    # 4) 오늘/내일 운세 (날짜 seed)
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
        return [strip_html_like(safe_str(x)) for x in pool if safe_str(x).strip()]

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

    year_text = pick_one([strip_html_like(safe_str(x)) for x in year_pool if safe_str(x).strip()], stable_seed(str(base_seed), "year_2026"))

    # 비어있으면 명확히 표시(생성/대체 금지)
    def ensure_text(val, label):
        if val and str(val).strip():
            return val
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

    with st.expander("DB 연결 상태(확인용)"):
        st.write(dbs["paths"])

# =========================================================
# 2.5) 유틸: 띠 키 정규화 (DB 키 mismatch 방지)
#   - 화면 표시는 한국어(원숭이띠 등)
#   - DB가 한국어/영문/동물명/접미사 유무 등으로 섞여 있어도 최대한 매칭
# =========================================================
def normalize_zodiac_key(raw: str) -> dict:
    """raw에서 가능한 후보 키들을 만들어 반환.
    return: {"display": <한국어표시>, "candidates": [..]}"""
    if not raw:
        return {"display": "", "candidates": []}

    s = str(raw).strip()

    # 접미사 정리
    s_no_tti = s.replace("띠", "").strip()

    # 영문 동물명 → 한글 띠
    en_to_ko = {
        "rat": "쥐", "ox": "소", "tiger": "호랑이", "rabbit": "토끼",
        "dragon": "용", "snake": "뱀", "horse": "말", "goat": "양",
        "monkey": "원숭이", "rooster": "닭", "dog": "개", "pig": "돼지",
    }

    # 혹시 "rooster띠" 같은 케이스
    for en, ko in en_to_ko.items():
        if s_no_tti.lower() == en:
            s_no_tti = ko
            break

    # display는 항상 "OO띠"
    display = s_no_tti + "띠" if s_no_tti else s

    # 후보 키들(우선순위)
    candidates = []
    # 1) 그대로 / 접미사 유무
    candidates += [s, s_no_tti, display]
    # 2) 영문/한글 변환 후보
    #    - 한글이면 영문도 추가
    ko_to_en = {v: k for k, v in en_to_ko.items()}
    base_ko = s_no_tti
    if base_ko in ko_to_en:
        candidates += [ko_to_en[base_ko], ko_to_en[base_ko] + "띠"]
    # 3) 소문자/대문자 변형
    candidates += [c.lower() for c in candidates if isinstance(c, str)]
    candidates += [c.upper() for c in candidates if isinstance(c, str)]

    # 중복 제거(순서 유지)
    seen = set()
    uniq = []
    for c in candidates:
        if not c:
            continue
        if c not in seen:
            seen.add(c)
            uniq.append(c)

    return {"display": display, "candidates": uniq}



# -----------------------------
# Main
# -----------------------------
# 11) 실행
# =========================================================
try:
    dbs = load_all_dbs()
except Exception as e:
    st.error(str(e))
    st.stop()

if st.session_state.stage == "input":
    render_input(dbs)
else:
    render_result(dbs)
# =========================================================
