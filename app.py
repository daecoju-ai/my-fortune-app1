import streamlit as st
import streamlit.components.v1 as components
from datetime import date, datetime, timedelta
import json
import os
import re
import random
import hashlib
from pathlib import Path

# =========================================================
# 0) 기본 설정
# =========================================================
APP_URL = "https://my-fortune.streamlit.app"  # 네 Streamlit 앱 주소로 유지/수정 가능
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
    """
    candidates: ["data/a.json", "data/b.json", ...]
    존재하는 첫 파일을 로드해서 반환.
    없으면 예외(명확하게).
    """
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
# 2) 유틸 - 시드 / 문자열 정리
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

# =========================================================
# 3) 한국 설 기준 띠 계산
# =========================================================
ZODIAC_ORDER = ["rat","ox","tiger","rabbit","dragon","snake","horse","goat","monkey","rooster","dog","pig"]
ZODIAC_LABEL_KO = {
    "rat":"쥐띠","ox":"소띠","tiger":"호랑이띠","rabbit":"토끼띠","dragon":"용띠","snake":"뱀띠",
    "horse":"말띠","goat":"양띠","monkey":"원숭이띠","rooster":"닭띠","dog":"개띠","pig":"돼지띠",
}

def parse_lny_map(lny_json):
    out = {}
    if isinstance(lny_json, dict):
        for y, dstr in lny_json.items():
            try:
                yy = int(str(y))
                parts = str(dstr).split("-")
                out[yy] = date(int(parts[0]), int(parts[1]), int(parts[2]))
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

    mbti = (
        decide("EI","E","I") +
        decide("SN","S","N") +
        decide("TF","T","F") +
        decide("JP","J","P")
    )
    return mbti if mbti in MBTI_TYPES else "ENFP"

# =========================================================
# 5) 친구 공유 버튼
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
# 6) 타로 (요구사항 반영)
#   - "이미 뽑았다" 문구 금지
#   - 하루 동안은 똑같은 카드만 나오게(버튼 여러번 눌러도 동일)
#   - back 이미지 -> 뽑기 시 흔들림 -> 앞면 이미지 1장 표시
# =========================================================
def _list_tarot_front_images() -> list[Path]:
    """
    assets/tarot 아래 모든 png/jpg/webp 이미지(단 back.* 제외) 수집
    """
    root = Path("assets/tarot")
    if not root.exists():
        return []
    imgs = []
    for ext in ("*.png", "*.jpg", "*.jpeg", "*.webp"):
        imgs.extend(root.rglob(ext))
    # back.* 제외
    imgs = [p for p in imgs if p.is_file() and p.stem.lower() != "back"]
    return imgs

def _get_tarot_back_path() -> Path | None:
    candidates = [
        Path("assets/tarot/back.png"),
        Path("assets/tarot/back.jpg"),
        Path("assets/tarot/back.webp"),
        Path("assets/tarot/back.jpeg"),
    ]
    for p in candidates:
        if p.exists():
            return p
    return None

def _normalize_key(s: str) -> str:
    return re.sub(r"[^a-z0-9_]+", "_", (s or "").strip().lower()).strip("_")

def _flatten_tarot_db(tarot_db):
    """
    tarot_db 다양한 형태 방어적으로 평탄화
    반환: list[dict] with keys: key, name, meaning, image(optional)
    """
    cards = []

    if isinstance(tarot_db, dict):
        # {"cards":[...]} or {"the_fool": {...}}
        if isinstance(tarot_db.get("cards"), list):
            raw = tarot_db["cards"]
            for c in raw:
                if isinstance(c, dict):
                    name = c.get("name") or c.get("title") or c.get("card")
                    meaning = c.get("meaning") or c.get("desc") or c.get("text")
                    key = c.get("key") or c.get("id") or c.get("slug")
                    image = c.get("image") or c.get("img")
                    if name and meaning:
                        cards.append({
                            "key": _normalize_key(str(key or name)),
                            "name": strip_html_like(str(name)),
                            "meaning": strip_html_like(str(meaning)),
                            "image": str(image or "").strip(),
                        })
        else:
            for k, v in tarot_db.items():
                if not isinstance(v, dict):
                    continue
                name = v.get("name") or v.get("title") or k
                meaning = v.get("meaning") or v.get("desc") or v.get("text") or v.get("today")
                image = v.get("image") or v.get("img")
                if name and meaning:
                    cards.append({
                        "key": _normalize_key(str(k)),
                        "name": strip_html_like(str(name)),
                        "meaning": strip_html_like(str(meaning)),
                        "image": str(image or "").strip(),
                    })

    elif isinstance(tarot_db, list):
        for c in tarot_db:
            if not isinstance(c, dict):
                continue
            name = c.get("name") or c.get("title") or c.get("card")
            meaning = c.get("meaning") or c.get("desc") or c.get("text") or c.get("today")
            key = c.get("key") or c.get("id") or c.get("slug") or name
            image = c.get("image") or c.get("img")
            if name and meaning:
                cards.append({
                    "key": _normalize_key(str(key)),
                    "name": strip_html_like(str(name)),
                    "meaning": strip_html_like(str(meaning)),
                    "image": str(image or "").strip(),
                })

    return cards

def _resolve_image_from_card(card: dict, all_front_images: list[Path]) -> Path | None:
    """
    card["image"]에 경로/파일명이 들어있으면 우선 매칭.
    없거나 매칭 실패면 None 반환.
    """
    if not card:
        return None
    img = (card.get("image") or "").strip()
    if not img:
        return None

    # 1) 절대/상대 경로로 존재하면 그대로
    p = Path(img)
    if p.exists() and p.is_file():
        return p

    # 2) assets 기준 상대경로로 시도
    p2 = Path("assets") / img
    if p2.exists() and p2.is_file():
        return p2

    # 3) 파일명만 들어있을 경우, 전체 이미지 목록에서 stem/이름 매칭
    target_name = Path(img).name.lower()
    for fp in all_front_images:
        if fp.name.lower() == target_name:
            return fp

    # 4) stem 기준 느슨한 매칭
    tstem = Path(img).stem.lower()
    for fp in all_front_images:
        if fp.stem.lower() == tstem:
            return fp

    return None

def get_tarot_of_day(tarot_db, birth: date, name: str):
    """
    하루 동안 고정:
      - 날짜 + (birth + name) 기반 seed로
      - "카드 의미(DB)" 1개 + "앞면 이미지" 1개를 고정 선택
    """
    today = date.today()
    user_seed = stable_seed(str(birth), (name or "").strip(), "tarot_user")

    # DB 카드 목록
    flattened = _flatten_tarot_db(tarot_db)
    # 이미지 파일 목록
    all_front_images = _list_tarot_front_images()

    seed_int = stable_seed(str(today), str(user_seed), "tarot_of_day")
    r = random.Random(seed_int)

    chosen_card = None
    if flattened:
        chosen_card = r.choice(flattened)

    # 이미지 결정:
    # 1) DB에 image가 있으면 그것 우선
    # 2) 아니면 전체 이미지에서 랜덤 1개 (하루 고정)
    chosen_img = None
    if chosen_card:
        chosen_img = _resolve_image_from_card(chosen_card, all_front_images)

    if chosen_img is None and all_front_images:
        chosen_img = r.choice(all_front_images)

    return chosen_card, chosen_img

def tarot_ui(tarot_db, birth: date, name: str):
    st.markdown("<div class='card tarot-card'>", unsafe_allow_html=True)
    st.markdown("### 🃏 오늘의 타로카드 <span style='font-size:0.95rem;opacity:0.85'>(하루 1회 가능)</span>", unsafe_allow_html=True)

    # 고정 설명(요구사항)
    st.markdown(
        "<div class='soft-box'>"
        "뒷면 카드를 보고, <b>뽑기</b>를 누르면 오늘의 카드가 공개됩니다.<br/>"
        "오늘 하루 동안은 같은 카드(같은 의미/이미지)로 고정됩니다."
        "</div>",
        unsafe_allow_html=True
    )

    back_path = _get_tarot_back_path()

    # 세션
    if "tarot_revealed" not in st.session_state:
        st.session_state.tarot_revealed = False
    if "tarot_clicked_at" not in st.session_state:
        st.session_state.tarot_clicked_at = None

    # 카드(하루 고정) 미리 계산
    chosen_card, chosen_img = get_tarot_of_day(tarot_db, birth, name)

    # 표시 영역
    box = st.empty()

    def render_back(shake: bool = False):
        if back_path and back_path.exists():
            if shake:
                # 흔들림: HTML img로 렌더링 (streamlit image는 class 주기 어렵다)
                b64 = None
                try:
                    import base64
                    b64 = base64.b64encode(back_path.read_bytes()).decode("utf-8")
                except Exception:
                    b64 = None

                if b64:
                    html = f"""
                    <style>
                      .tarot-shake {{
                        width: 100%;
                        border-radius: 18px;
                        overflow: hidden;
                        animation: shake 0.55s ease-in-out 1;
                        transform-origin: center;
                      }}
                      @keyframes shake {{
                        0% {{ transform: rotate(0deg) scale(1); }}
                        15% {{ transform: rotate(-1.8deg) scale(1.01); }}
                        30% {{ transform: rotate(1.8deg) scale(1.01); }}
                        45% {{ transform: rotate(-1.2deg) scale(1.01); }}
                        60% {{ transform: rotate(1.2deg) scale(1.01); }}
                        100% {{ transform: rotate(0deg) scale(1); }}
                      }}
                    </style>
                    <img class="tarot-shake" src="data:image/png;base64,{b64}" />
                    """
                    box.markdown(html, unsafe_allow_html=True)
                    return

            # 기본 back
            box.image(str(back_path), use_container_width=True)
        else:
            box.markdown(
                "<div style='height:220px;border-radius:18px;"
                "background:linear-gradient(135deg,#2b2350,#6b4fd6,#fbc2eb);"
                "display:flex;align-items:center;justify-content:center;"
                "color:white;font-weight:900;font-size:1.2rem;'>TAROT BACK</div>",
                unsafe_allow_html=True
            )

    def render_front():
        # 이미지
        if chosen_img and chosen_img.exists():
            box.image(str(chosen_img), use_container_width=True)
        else:
            # 이미지가 없어도 앱이 죽지 않도록 방어
            box.markdown(
                "<div style='height:220px;border-radius:18px;"
                "background:linear-gradient(135deg,#111827,#374151,#6b7280);"
                "display:flex;align-items:center;justify-content:center;"
                "color:white;font-weight:900;font-size:1.05rem;'>이미지 없음</div>",
                unsafe_allow_html=True
            )

        # 의미
        if not chosen_card:
            st.info("타로 DB에서 카드를 불러오지 못했습니다. (tarot_db_ko.json 확인)")
            return

        cname = chosen_card.get("name", "오늘의 카드")
        cmeaning = chosen_card.get("meaning", "")

        st.markdown(
            f"""
            <div class="reveal">
              <div class="reveal-title">✨ {strip_html_like(str(cname))}</div>
              <div class="reveal-meaning">{strip_html_like(str(cmeaning))}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 상태별 렌더
    if not st.session_state.tarot_revealed:
        render_back(shake=False)
    else:
        # 클릭 직후 0.6초는 흔들림 back 보여주고, 이후 front
        clicked_at = st.session_state.tarot_clicked_at
        if isinstance(clicked_at, float):
            elapsed = (datetime.now().timestamp() - clicked_at)
            if elapsed < 0.6:
                render_back(shake=True)
            else:
                render_front()
        else:
            render_front()

    # 버튼(여러번 눌러도 "같은 카드"만 나오므로 '이미 뽑았어요' 문구가 필요 없음)
    if st.button("타로카드 뽑기", use_container_width=True):
        st.session_state.tarot_revealed = True
        st.session_state.tarot_clicked_at = datetime.now().timestamp()
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 7) 다나눔렌탈 광고
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
    st.markdown("""
    <div class="header-hero">
      <p class="hero-title">🔮 2026 운세 | 띠 + MBTI + 사주 + 오늘/내일 + 타로</p>
      <p class="hero-sub">이름 + 생년월일 + MBTI로 결과가 고정 출력됩니다</p>
      <span class="badge">2026</span>
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
        # 키는 무조건 대문자 기준
        trait = dbs["mbti_db"].get(st.session_state.mbti.upper(), "")
        if trait:
            st.markdown(f"<div class='soft-box'><b>{st.session_state.mbti}</b> · {strip_html_like(safe_str(trait))}</div>", unsafe_allow_html=True)

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
    mbti = (st.session_state.mbti or "ENFP").upper()

    lny_map = parse_lny_map(dbs["lunar_lny"])
    zodiac_key, zodiac_year = zodiac_by_birth(birth, lny_map)
    zodiac_label = ZODIAC_LABEL_KO.get(zodiac_key, zodiac_key)

    base_seed = stable_seed(str(birth), name, mbti)

    # 1) 띠별 운세
    zodiac_pool = []
    zdb = dbs["zodiac_db"]
    if isinstance(zdb, dict):
        val = zdb.get(zodiac_key)
        if isinstance(val, list):
            zodiac_pool = val
        elif isinstance(val, dict):
            if isinstance(val.get("items"), list):
                zodiac_pool = val["items"]
            elif isinstance(val.get("lines"), list):
                zodiac_pool = val["lines"]

    zodiac_text = pick_one([strip_html_like(safe_str(x)) for x in zodiac_pool if safe_str(x).strip()], stable_seed(str(base_seed), "zodiac"))
    # 영어키 섞임 방지: 출력은 무조건 한글 띠 라벨 사용
    if zodiac_text:
        zodiac_text = zodiac_text.replace("rooster", "닭").replace("monkey", "원숭이").replace("rat", "쥐").replace("ox", "소") \
                                 .replace("tiger", "호랑이").replace("rabbit", "토끼").replace("dragon", "용").replace("snake", "뱀") \
                                 .replace("horse", "말").replace("goat", "양").replace("dog", "개").replace("pig", "돼지")

    # 2) MBTI 특징 (대문자 키로 통일)
    mbti_trait = strip_html_like(safe_str(dbs["mbti_db"].get(mbti, "")))

    # 3) 사주 한마디
    saju_pool = []
    sdb = dbs["saju_db"]
    if isinstance(sdb, dict):
        if isinstance(sdb.get("pools"), dict) and isinstance(sdb["pools"].get("saju"), list):
            saju_pool = sdb["pools"]["saju"]
        elif isinstance(sdb.get("saju"), list):
            saju_pool = sdb["saju"]
        elif isinstance(sdb.get("lines"), list):
            saju_pool = sdb["lines"]
    elif isinstance(sdb, list):
        saju_pool = sdb
    saju_text = pick_one([strip_html_like(safe_str(x)) for x in saju_pool if safe_str(x).strip()], stable_seed(str(base_seed), "saju"))

    # 4) 오늘/내일 운세
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

    display_name = f"{name}님" if name else "당신"
    st.markdown(
        f"""
        <div class="header-hero">
          <p class="hero-title">{display_name}의 운세 결과</p>
          <p class="hero-sub">{zodiac_label} · {mbti} · (설 기준 띠년도 {zodiac_year})</p>
          <span class="badge">2026</span>
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

    # ✅ 타로 (에러/문구/고정 로직 수정)
    tarot_ui(dbs["tarot_db"], birth, name)

    if st.button("입력 화면으로", use_container_width=True):
        st.session_state.stage = "input"
        st.rerun()

    with st.expander("DB 연결 상태(확인용)"):
        st.write(dbs["paths"])

# =========================================================
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
