import streamlit as st
from datetime import datetime, timedelta, date
import random
import io
import textwrap
import base64
from PIL import Image, ImageDraw, ImageFont
import streamlit.components.v1 as components
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# =========================
# 기본 설정
# =========================
APP_URL = "https://my-fortune.streamlit.app"   # 너 앱 주소(배포 주소로 맞춰줘)
AD_URL = "https://www.다나눔렌탈.com"

# =========================
# 데이터
# =========================
ZODIAC_LIST_KO = ["쥐띠","소띠","호랑이띠","토끼띠","용띠","뱀띠","말띠","양띠","원숭이띠","닭띠","개띠","돼지띠"]

ZODIAC_EMOJI_KO = {
    "쥐띠":"🐭","소띠":"🐮","호랑이띠":"🐯","토끼띠":"🐰","용띠":"🐲","뱀띠":"🐍",
    "말띠":"🐴","양띠":"🐑","원숭이띠":"🐵","닭띠":"🐔","개띠":"🐶","돼지띠":"🐷"
}
MBTI_EMOJI = {
    "INTJ":"♟️","INTP":"🧩","ENTJ":"👑","ENTP":"🧨",
    "INFJ":"🔮","INFP":"🎨","ENFJ":"🤝","ENFP":"✨",
    "ISTJ":"📏","ISFJ":"🫶","ESTJ":"🧱","ESFJ":"🎉",
    "ISTP":"🔧","ISFP":"🌿","ESTP":"🏎️","ESFP":"🎭"
}

ZODIACS_KO = {
    "쥐띠": "안정 속 새로운 기회! 민첩한 판단으로 성공 잡아요",
    "소띠": "꾸준함의 결실! 안정된 성장과 행복한 가족운",
    "호랑이띠": "대박 띠! 도전과 성공, 리더십 발휘로 큰 성과",
    "토끼띠": "삼재 주의! 신중함으로 변화 대처, 안정 추구",
    "용띠": "운기 상승! 리더십과 승진 기회 많음",
    "뱀띠": "직감과 실속! 예상치 못한 재물운",
    "말띠": "본띠 해! 추진력 강하지만 균형이 핵심",
    "양띠": "대박 띠! 편안함과 최고 돈운, 가정 행복",
    "원숭이띠": "변화와 재능 발휘! 창의력으로 성공",
    "닭띠": "노력 결실! 인정과 승진 가능성 높음",
    "개띠": "대박 띠! 귀인 도움과 네트워킹으로 상승",
    "돼지띠": "여유와 재물 대박! 즐기는 최고의 해"
}

MBTIS_KO = {
    "INTJ": "냉철 전략가", "INTP": "아이디어 천재", "ENTJ": "보스", "ENTP": "토론왕",
    "INFJ": "마음 마스터", "INFP": "감성 예술가", "ENFJ": "모두 선생님", "ENFP": "인간 비타민",
    "ISTJ": "규칙 지킴이", "ISFJ": "세상 따뜻함", "ESTJ": "리더", "ESFJ": "분위기 메이커",
    "ISTP": "고치는 장인", "ISFP": "감성 힐러", "ESTP": "모험왕", "ESFP": "파티 주인공"
}

SAJU_MSGS_KO = [
    "목(木) 기운 강함 → 성장과 발전의 해!",
    "화(火) 기운 강함 → 열정 폭발!",
    "토(土) 기운 강함 → 안정과 재물운",
    "금(金) 기운 강함 → 결단력 좋음!",
    "수(水) 기운 강함 → 지혜와 흐름",
    "오행 균형 → 행복한 한 해",
    "양기 강함 → 도전 성공",
    "음기 강함 → 내면 성찰"
]

DAILY_MSGS_KO = [
    "재물운 좋음! 작은 투자도 이득 봐요",
    "연애운 최고! 고백하거나 데이트 좋음",
    "건강 주의! 과로 피하고 쉬세요",
    "전체운 대박! 좋은 일만 생길 거예요",
    "인간관계 운 좋음! 귀인 만남 가능",
    "학업/일 운 최고! 집중력 최고",
    "여행운 좋음! 갑자기 떠나도 괜찮아요",
    "기분 좋은 하루! 웃음이 가득할 거예요"
]

OVERALL_FORTUNES_KO = [
    "성장과 재물이 함께하는 최고의 해! 대박 기운 가득",
    "안정과 행복이 넘치는 한 해! 가족과 함께하는 기쁨",
    "도전과 성공의 해! 큰 성과를 이룰 거예요",
    "사랑과 인연이 피어나는 로맨틱한 해",
    "변화와 새로운 시작! 창의력이 빛나는 한 해"
]

COMBO_COMMENTS_KO = [
    "{}의 노력과 {}의 따뜻함으로 모두를 이끄는 리더가 될 거예요!",
    "{}의 리더십과 {}의 창의력이 완벽한 시너지!",
    "{}의 직감과 {}의 논리로 무적 조합!",
    "{}의 안정감과 {}의 열정으로 대박 성공!",
    "{}의 유연함과 {}의 결단력으로 모든 일 해결!"
]

LUCKY_COLORS_KO = ["골드", "레드", "블루", "그린", "퍼플"]
LUCKY_ITEMS_KO = ["황금 액세서리", "빨간 지갑", "파란 목걸이", "초록 식물", "보라색 펜"]
TIPS_KO = [
    "새로운 사람 만나는 기회 많아요. 적극적으로!",
    "작은 투자에 집중하세요. 이득 볼 가능성 높음",
    "건강 관리에 신경 쓰세요. 규칙적인 운동 추천",
    "가족/친구와 시간 보내세요. 행복 충전!",
    "창의적인 취미를 시작해보세요. 재능 발휘될 거예요"
]

TAROT_CARDS = {
    "The Fool": "바보 - 새로운 시작, 모험, 순수한 믿음",
    "The Magician": "마법사 - 창조력, 능력 발휘, 집중",
    "The High Priestess": "여사제 - 직감, 신비, 내면의 목소리",
    "The Empress": "여제 - 풍요, 어머니의 사랑, 창작",
    "The Emperor": "황제 - 안정, 권위, 구조",
    "The Hierophant": "교황 - 전통, 스승, 지도",
    "The Lovers": "연인 - 사랑, 조화, 선택",
    "The Chariot": "전차 - 승리, 의지력, 방향",
    "Strength": "힘 - 용기, 인내, 부드러운 통제",
    "The Hermit": "은둔자 - 내면 탐구, 지혜, 고독",
    "Wheel of Fortune": "운명의 수레바퀴 - 변화, 운, 사이클",
    "Justice": "정의 - 공정, 균형, 진실",
    "The Hanged Man": "매달린 사람 - 희생, 새로운 관점, 기다림",
    "Death": "죽음 - 변화, 끝과 시작, 재생",
    "Temperance": "절제 - 균형, 조화, 인내",
    "The Devil": "악마 - 속박, 유혹, 물질주의",
    "The Tower": "탑 - 갑작스러운 변화, 파괴와 재건",
    "The Star": "별 - 희망, 영감, 치유",
    "The Moon": "달 - 불안, 환상, 직감",
    "The Sun": "태양 - 행복, 성공, 긍정 에너지",
    "Judgement": "심판 - 부활, 깨달음, 용서",
    "The World": "세계 - 완성, 성취, 전체성"
}

# =========================
# 유틸: 고정 랜덤(신뢰)
# =========================
def get_zodiac_ko(year: int):
    if not (1900 <= year <= 2030):
        return None
    return ZODIAC_LIST_KO[(year - 4) % 12]

def get_saju_msg(year: int, month: int, day: int):
    return SAJU_MSGS_KO[(year + month + day) % 8]

def daily_fortune(zodiac: str, offset_days: int):
    """오늘/내일은 날짜+띠로 고정"""
    d = datetime.now() + timedelta(days=offset_days)
    seed = int(d.strftime("%Y%m%d")) + ZODIAC_LIST_KO.index(zodiac)
    rng = random.Random(seed)
    return rng.choice(DAILY_MSGS_KO)

def stable_rng(name: str, y: int, m: int, d: int, mbti: str):
    """연간/럭키/팁은 사용자 입력으로 고정"""
    key = f"ko|{name}|{y:04d}-{m:02d}-{d:02d}|{mbti}"
    seed = abs(hash(key)) % (10**9)
    return random.Random(seed)

# =========================
# 공유 이미지 생성(한글 폰트 적용)
# =========================
def load_font(font_path: str, size: int):
    try:
        return ImageFont.truetype(font_path, size)
    except:
        return ImageFont.load_default()

def make_share_image(title_lines, body_lines, footer_text=APP_URL):
    """
def load_font(font_path: str, size: int):
    try:
        return ImageFont.truetype(font_path, size)
    except:
        return ImageFont.load_default()

def _rounded(draw, xy, r, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)

def _shadow_card(base: Image.Image, xy, radius=34, shadow_offset=(0, 14), shadow_blur=18):
    # 간단한 그림자(알파 레이어)
    x1, y1, x2, y2 = xy
    w, h = base.size
    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sx1 = x1 + shadow_offset[0]
    sy1 = y1 + shadow_offset[1]
    sx2 = x2 + shadow_offset[0]
    sy2 = y2 + shadow_offset[1]
    sd.rounded_rectangle((sx1, sy1, sx2, sy2), radius=radius, fill=(0, 0, 0, 85))
    shadow = shadow.filter(ImageFilter.GaussianBlur(shadow_blur))
    base.paste(shadow, (0, 0), shadow)

def _wrap_lines(text, width_chars=26):
    return textwrap.wrap(text, width=width_chars, break_long_words=False)

def make_share_image(title_lines, body_lines, footer_text=APP_URL):
    """
    더 예쁜 공유용 PNG (9:16)
    - 상단: 타이틀/서브타이틀
    - 본문: 섹션 카드(오늘/내일/전체/조합/럭키/팁)
    - 하단: 링크
    """
    from PIL import ImageFilter  # pillow 내장

    W, H = 1080, 1920  # 9:16
    # ---------- 배경 그라데이션 ----------
    bg = Image.new("RGB", (W, H), (245, 240, 255))
    px = bg.load()
    top = (164, 140, 220)   # 보라
    mid = (251, 194, 235)   # 핑크
    bot = (142, 197, 252)   # 하늘
    for y in range(H):
        t = y / (H - 1)
        if t < 0.5:
            k = t / 0.5
            r = int(top[0] * (1-k) + mid[0] * k)
            g = int(top[1] * (1-k) + mid[1] * k)
            b = int(top[2] * (1-k) + mid[2] * k)
        else:
            k = (t - 0.5) / 0.5
            r = int(mid[0] * (1-k) + bot[0] * k)
            g = int(mid[1] * (1-k) + bot[1] * k)
            b = int(mid[2] * (1-k) + bot[2] * k)
        for x in range(W):
            px[x, y] = (r, g, b)

    # 살짝 블러로 부드럽게
    bg = bg.filter(ImageFilter.GaussianBlur(0.8))

    # ---------- 폰트 ----------
    font_path = "NotoSansKR-Regular.ttf"  # 레포 루트에 업로드 필수
    title_f = load_font(font_path, 72)
    sub_f   = load_font(font_path, 46)
    badge_f = load_font(font_path, 34)
    body_f  = load_font(font_path, 40)
    small_f = load_font(font_path, 30)

    draw = ImageDraw.Draw(bg)

    # ---------- 상단 타이틀 ----------
    # 타이틀(중앙)
    y = 90
    t1 = title_lines[0] if title_lines else "⭐ 2026년 운세 ⭐"
    w1 = draw.textlength(t1, font=title_f)
    draw.text(((W - w1) / 2, y), t1, fill=(255, 255, 255), font=title_f)
    # 살짝 글로우 느낌(그림자)
    draw.text(((W - w1) / 2 + 2, y + 2), t1, fill=(0, 0, 0, 55), font=title_f)

    # 서브타이틀(중앙)
    y += 95
    t2 = title_lines[1] if len(title_lines) > 1 else ""
    w2 = draw.textlength(t2, font=sub_f)
    draw.text(((W - w2) / 2, y), t2, fill=(255, 255, 255), font=sub_f)

    # “최고 조합!” 배지
    y += 80
    badge = title_lines[2] if len(title_lines) > 2 else "최고 조합!"
    bw = draw.textlength(badge, font=badge_f)
    pad_x, pad_y = 26, 14
    bx1 = (W - (bw + pad_x*2)) / 2
    by1 = y
    bx2 = bx1 + bw + pad_x*2
    by2 = y + 52
    _rounded(draw, (bx1, by1, bx2, by2), r=26, fill=(255, 255, 255), outline=(255, 255, 255), width=1)
    draw.text((bx1 + pad_x, by1 + 9), badge, fill=(88, 56, 163), font=badge_f)

    # ---------- 메인 카드 ----------
    card_margin = 70
    card_top = 330
    card_bottom = H - 330
    card_xy = (card_margin, card_top, W - card_margin, card_bottom)

    # 그림자 + 카드
    # (그림자)
    shadow = Image.new("RGBA", (W, H), (0,0,0,0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle(
        (card_xy[0] + 6, card_xy[1] + 18, card_xy[2] + 6, card_xy[3] + 18),
        radius=38,
        fill=(0, 0, 0, 70)
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    bg.paste(shadow, (0,0), shadow)

    # 카드 본체(약간 유리 느낌)
    card = Image.new("RGBA", (W, H), (0,0,0,0))
    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle(card_xy, radius=38, fill=(255,255,255,230), outline=(255,255,255,255), width=2)
    # 상단 얇은 그라데이션 라인
    cd.rounded_rectangle((card_xy[0], card_xy[1], card_xy[2], card_xy[1]+10), radius=38, fill=(150,120,220,160))
    bg = Image.alpha_composite(bg.convert("RGBA"), card)
    draw = ImageDraw.Draw(bg)

    # ---------- 본문: 섹션 분리 ----------
    # body_lines는 우리가 만든 문장들: "✨ 띠 운세: ...", "💗 오늘 운세: ..." 등
    # 예쁘게: 키 그룹별로 잘라서 넣기
    def pick(prefix):
        for line in body_lines:
            if line.strip().startswith(prefix):
                return line
        return None

    z1 = pick("✨") or ""
    m1 = pick("🧠") or ""
    s1 = pick("🍀") or ""
    today = pick("💗") or ""
    tom = pick("🌙") or ""
    overall = pick("💝") or ""
    combo = pick("💬") or ""
    lucky = pick("🎨") or ""
    tip = pick("✅") or ""

    sections = [
        ("기본", [z1, m1, s1]),
        ("오늘 · 내일", [today, tom]),
        ("2026 전체", [overall, combo]),
        ("럭키", [lucky, tip]),
    ]

    inner_x = card_xy[0] + 34
    inner_y = card_xy[1] + 28
    inner_w = card_xy[2] - card_xy[0] - 68

    # 섹션 박스 스타일
    box_gap = 18
    box_radius = 26

    def draw_section(title, lines, x, y, w):
        # 박스 높이 계산(대략)
        # 각 줄 래핑해서 줄 수 계산
        content_lines = []
        for ln in lines:
            if not ln:
                continue
            content_lines += _wrap_lines(ln, width_chars=26)
        h = 64 + len(content_lines) * 52 + 10

        # 박스 배경
        _rounded(draw, (x, y, x + w, y + h), r=box_radius, fill=(255, 255, 255, 200), outline=(210, 200, 235, 255), width=2)

        # 섹션 타이틀 pill
        pill_text = title
        pw = draw.textlength(pill_text, font=small_f)
        pill_x1 = x + 18
        pill_y1 = y + 16
        pill_x2 = pill_x1 + pw + 22
        pill_y2 = pill_y1 + 42
        _rounded(draw, (pill_x1, pill_y1, pill_x2, pill_y2), r=18, fill=(124, 58, 237, 230))
        draw.text((pill_x1 + 11, pill_y1 + 7), pill_text, fill=(255, 255, 255), font=small_f)

        # 콘텐츠 텍스트
        ty = y + 66
        for ln in lines:
            if not ln:
                continue
            wrapped = _wrap_lines(ln, width_chars=26)
            for wln in wrapped:
                draw.text((x + 18, ty), wln, fill=(33, 33, 33), font=body_f)
                ty += 52
            ty += 6

        return y + h

    # 2열 레이아웃(모바일 공유이미지에서 가독성 좋음)
    col_w = (inner_w - 18) // 2
    left_x = inner_x
    right_x = inner_x + col_w + 18

    # 위쪽 2개는 2열
    y1 = inner_y
    y2 = inner_y

    # 기본(왼쪽)
    y1_end = draw_section(sections[0][0], sections[0][1], left_x, y1, col_w)
    # 오늘내일(오른쪽)
    y2_end = draw_section(sections[1][0], sections[1][1], right_x, y2, col_w)

    # 아래쪽은 전체 폭 1열(긴 문장 대비)
    y_next = max(y1_end, y2_end) + box_gap
    full_w = inner_w

    y_next = draw_section(sections[2][0], sections[2][1], inner_x, y_next, full_w) + box_gap
    y_next = draw_section(sections[3][0], sections[3][1], inner_x, y_next, full_w)

    # ---------- 하단 푸터 ----------
    ft = footer_text
    fw = draw.textlength(ft, font=small_f)
    draw.text(((W - fw) / 2, H - 250), ft, fill=(255, 255, 255, 230), font=small_f)

    # PNG 출력
    out = io.BytesIO()
    bg.convert("RGB").save(out, format="PNG")
    return out.getvalue()


# =========================
# Streamlit 기본
# =========================
st.set_page_config(page_title="2026년 운세", layout="centered")

# 세션 상태
if "result_shown" not in st.session_state:
    st.session_state.result_shown = False
if "name" not in st.session_state:
    st.session_state.name = ""
if "birthdate" not in st.session_state:
    st.session_state.birthdate = date(2005, 1, 1)
if "mbti" not in st.session_state:
    st.session_state.mbti = "ENFJ"
if "share_png" not in st.session_state:
    st.session_state.share_png = None

# =========================
# 모바일 최적화 + 상단 잘림 해결 CSS
# =========================
st.markdown("""
<style>
header {visibility: hidden;}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

.stApp { background: #efe9ff; }

.block-container {
  padding-top: 10px !important;
  padding-bottom: 30px !important;
  max-width: 720px;
}

.ppt-title {
  font-size: 28px; font-weight: 900; color:#2b2b2b; text-align:center;
  margin: 14px 0 10px;
}
.ppt-subtitle {
  font-size: 20px; font-weight: 900; color:#2b2b2b; text-align:center;
  margin: 4px 0 6px;
}
.ppt-combo {
  font-size: 16px; font-weight: 800; color:#2b2b2b; text-align:center;
  margin: 6px 0 14px;
}

.card {
  background: rgba(255,255,255,0.75);
  border: 1px solid rgba(140,120,200,0.25);
  border-radius: 18px;
  padding: 16px 16px;
  box-shadow: 0 10px 22px rgba(0,0,0,0.08);
  margin: 10px 0 16px;
  text-align: left;
}
.card p { margin: 6px 0; line-height: 1.65; font-size: 14.5px; color:#2b2b2b; }
.kv { font-weight: 900; }
.hr { height: 1px; background: rgba(120,100,180,0.18); margin: 12px 0; }

.ad {
  background: rgba(255,255,255,0.65);
  border: 1px solid rgba(140,120,200,0.22);
  border-radius: 18px;
  padding: 14px 16px;
  box-shadow: 0 10px 22px rgba(0,0,0,0.06);
  margin: 10px 0 18px;
}
.ad-title { font-weight: 900; font-size: 15px; }
.ad-link {
  display: inline-block;
  margin-top: 10px;
  padding: 7px 12px;
  border-radius: 10px;
  border: 1px solid rgba(80,80,180,0.25);
  background: rgba(255,255,255,0.7);
  font-weight: 900;
  color: #2b5bd7;
  text-decoration: none;
}

.tarot-wrap {
  background: rgba(255,255,255,0.6);
  border: 1px solid rgba(140,120,200,0.18);
  border-radius: 16px;
  padding: 14px 16px;
}
.tarot-title { font-weight: 900; color: #7c3aed; margin-bottom: 6px; }
.tarot-cardname { font-weight: 900; font-size: 22px; margin: 0 0 6px; color:#2b2b2b; }
.tarot-meaning { margin: 0; color:#2b2b2b; }

@media (max-width: 480px) {
  .ppt-title { font-size: 24px; margin-top: 12px; }
  .ppt-subtitle { font-size: 18px; }
}
</style>
""", unsafe_allow_html=True)

# =========================
# 입력 화면
# =========================
if not st.session_state.result_shown:
    st.markdown("<div class='ppt-title'>⭐ 2026년 운세 ⭐</div>", unsafe_allow_html=True)

    st.session_state.name = st.text_input("이름 입력 (결과에 표시돼요)", value=st.session_state.name)

    st.session_state.birthdate = st.date_input(
        "생년월일 입력",
        value=st.session_state.birthdate,
        min_value=date(1900, 1, 1),
        max_value=date(2030, 12, 31),
    )

    mbti_mode = st.radio(
        "MBTI는 어떻게 할까요?",
        ["직접 선택(이미 알아요)", "간단 테스트(12문항)"],
        horizontal=True
    )

    if mbti_mode == "직접 선택(이미 알아요)":
        st.session_state.mbti = st.selectbox(
            "MBTI",
            sorted(MBTIS_KO.keys()),
            index=sorted(MBTIS_KO.keys()).index(st.session_state.mbti) if st.session_state.mbti in MBTIS_KO else 0
        )

        if st.button("2026년 운세 보기!", use_container_width=True):
            st.session_state.result_shown = True
            st.session_state.share_png = None
            st.rerun()

    else:
        st.caption("총 12문항(약 30초) — 솔직하게 고르면 더 잘 맞아요 🙂")

        q_ei = [
            ("약속이 갑자기 잡히면?", "좋아! 나가자(E)", "음… 집이 좋아(I)"),
            ("에너지 충전은?", "사람 만나면 충전(E)", "혼자 있어야 충전(I)"),
            ("대화할 때 나는?", "말하면서 정리(E)", "생각 정리 후 말(I)"),
        ]
        q_sn = [
            ("새로운 정보를 볼 때?", "현실/사실 위주(S)", "가능성/의미 위주(N)"),
            ("설명 들을 때 더 편한 건?", "예시·디테일(S)", "전체 그림·핵심(N)"),
            ("아이디어는 보통?", "검증된 방식(S)", "새로운 방식(N)"),
        ]
        q_tf = [
            ("의견 충돌 시 나는?", "논리/원칙(T)", "배려/관계(F)"),
            ("결정 기준은?", "효율/정확(T)", "마음/가치(F)"),
            ("피드백할 때?", "직설적으로(T)", "부드럽게(F)"),
        ]
        q_jp = [
            ("일정 스타일은?", "계획대로(J)", "즉흥적으로(P)"),
            ("마감 앞두면?", "미리 끝냄(J)", "막판 몰아함(P)"),
            ("정리정돈은?", "깔끔하게 유지(J)", "필요할 때만(P)"),
        ]

        ei = sn = tf = jp = 0

        st.subheader("1) 에너지(E/I)")
        for i, (q, a, b) in enumerate(q_ei):
            ans = st.radio(q, [a, b], key=f"ei_{i}")
            if ans == a:
                ei += 1

        st.subheader("2) 인식(S/N)")
        for i, (q, a, b) in enumerate(q_sn):
            ans = st.radio(q, [a, b], key=f"sn_{i}")
            if ans == a:
                sn += 1

        st.subheader("3) 판단(T/F)")
        for i, (q, a, b) in enumerate(q_tf):
            ans = st.radio(q, [a, b], key=f"tf_{i}")
            if ans == a:
                tf += 1

        st.subheader("4) 생활(J/P)")
        for i, (q, a, b) in enumerate(q_jp):
            ans = st.radio(q, [a, b], key=f"jp_{i}")
            if ans == a:
                jp += 1

        if st.button("테스트 결과로 운세 보기!", use_container_width=True):
            mbti = ""
            mbti += "E" if ei >= 2 else "I"
            mbti += "S" if sn >= 2 else "N"
            mbti += "T" if tf >= 2 else "F"
            mbti += "J" if jp >= 2 else "P"
            st.session_state.mbti = mbti

            st.session_state.result_shown = True
            st.session_state.share_png = None
            st.rerun()

# =========================
# 결과 화면
# =========================
if st.session_state.result_shown:
    y = st.session_state.birthdate.year
    m = st.session_state.birthdate.month
    d = st.session_state.birthdate.day
    name = st.session_state.name.strip()
    mbti = st.session_state.mbti

    zodiac = get_zodiac_ko(y)
    if zodiac is None:
        st.error("생년은 1900~2030년 사이로 입력해주세요!")
        st.session_state.result_shown = False
        st.stop()

    zodiac_emoji = ZODIAC_EMOJI_KO.get(zodiac, "")
    mbti_emoji = MBTI_EMOJI.get(mbti, "")
    zodiac_desc = ZODIACS_KO[zodiac]
    mbti_desc = MBTIS_KO.get(mbti, "MBTI")
    saju = get_saju_msg(y, m, d)

    today_msg = daily_fortune(zodiac, 0)
    tomorrow_msg = daily_fortune(zodiac, 1)

    rng = stable_rng(name, y, m, d, mbti)
    overall = rng.choice(OVERALL_FORTUNES_KO)
    combo_comment = rng.choice(COMBO_COMMENTS_KO).format(zodiac, mbti_desc)
    lucky_color = rng.choice(LUCKY_COLORS_KO)
    lucky_item = rng.choice(LUCKY_ITEMS_KO)
    tip = rng.choice(TIPS_KO)

    who = f"{name} · " if name else ""

    st.markdown("<div class='ppt-title'>⭐ 2026년 운세 ⭐</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='ppt-subtitle'>🔮 {who}{zodiac_emoji} {zodiac}  {mbti_emoji} {mbti}</div>", unsafe_allow_html=True)
    st.markdown("<div class='ppt-combo'>최고 조합!</div>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="card">
          <p>✨ <span class="kv">띠 운세</span>: {zodiac_desc}</p>
          <p>🧠 <span class="kv">MBTI 특징</span>: {mbti_desc}</p>
          <p>🍀 <span class="kv">사주 한 마디</span>: {saju}</p>
          <div class="hr"></div>
          <p>💗 <span class="kv">오늘 운세</span>: {today_msg}</p>
          <p>🌙 <span class="kv">내일 운세</span>: {tomorrow_msg}</p>
          <div class="hr"></div>
          <p>💝 <span class="kv">2026 전체 운세</span>: {overall}</p>
          <p>💬 <span class="kv">조합 한 마디</span>: {combo_comment}</p>
          <p>🎨 <span class="kv">럭키 컬러</span>: {lucky_color} &nbsp;&nbsp; 🧿 <span class="kv">럭키 아이템</span>: {lucky_item}</p>
          <p>✅ <span class="kv">팁</span>: {tip}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="ad">
          <div class="ad-title">🔥 정수기 렌탈 대박!</div>
          <div style="margin-top:6px; color:#2b2b2b; font-size:14px; line-height:1.6;">
            제휴카드면 월 0원부터!<br/>
            설치 당일 최대 50만원 지원 + 사은품 듬뿍 ✨
          </div>
          <a class="ad-link" href="{AD_URL}" target="_blank">🔗 다나눔렌탈.com 바로가기</a>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.expander("오늘의 타로 카드 보기", expanded=False):
        tarot_rng = random.Random(abs(hash(f"tarot|{datetime.now().strftime('%Y%m%d')}|{name}|{mbti}")) % (10**9))
        tarot_card = tarot_rng.choice(list(TAROT_CARDS.keys()))
        tarot_meaning = TAROT_CARDS[tarot_card]
        st.markdown(
            f"""
            <div class="tarot-wrap">
              <div class="tarot-title">오늘의 타로 카드</div>
              <div class="tarot-cardname">{tarot_card}</div>
              <p class="tarot-meaning">🪄 {tarot_meaning}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # =========================
    # 공유: 버튼 1번 = 공유 시트(갤러리 공유 화면) 바로 열기
    # =========================
    title_lines = [
        "⭐ 2026년 운세 ⭐",
        f"🔮 {who}{zodiac_emoji} {zodiac}  {mbti_emoji} {mbti}",
        "최고 조합!"
    ]
    body_lines = [
        f"✨ 띠 운세: {zodiac_desc}",
        f"🧠 MBTI 특징: {mbti_desc}",
        f"🍀 사주 한 마디: {saju}",
        "",
        f"💗 오늘 운세: {today_msg}",
        f"🌙 내일 운세: {tomorrow_msg}",
        "",
        f"💝 2026 전체 운세: {overall}",
        f"💬 조합 한 마디: {combo_comment}",
        f"🎨 럭키 컬러: {lucky_color} / 🧿 럭키 아이템: {lucky_item}",
        f"✅ 팁: {tip}",
    ]

    # ✅ 버튼 이름 변경: "친구에게 공유하기"
    if st.button("친구에게 공유하기", use_container_width=True, key="share_open"):
        png_bytes = make_share_image(title_lines, body_lines, footer_text=APP_URL)
        st.session_state.share_png = png_bytes

    # ✅ 버튼을 누른 후: 공유 시트 자동 오픈
    if st.session_state.get("share_png"):
        png_bytes = st.session_state.share_png
        b64 = base64.b64encode(png_bytes).decode("utf-8")

        # 공유 시트 자동 실행 (지원되는 모바일 브라우저에서)
        components.html(f"""
        <script>
          async function b64toBlob(b64Data, contentType='', sliceSize=512) {{
            const byteCharacters = atob(b64Data);
            const byteArrays = [];
            for (let offset = 0; offset < byteCharacters.length; offset += sliceSize) {{
              const slice = byteCharacters.slice(offset, offset + sliceSize);
              const byteNumbers = new Array(slice.length);
              for (let i = 0; i < slice.length; i++) {{
                byteNumbers[i] = slice.charCodeAt(i);
              }}
              const byteArray = new Uint8Array(byteNumbers);
              byteArrays.push(byteArray);
            }}
            return new Blob(byteArrays, {{type: contentType}});
          }}

          (async () => {{
            try {{
              const blob = await b64toBlob("{b64}", "image/png");
              const file = new File([blob], "2026_fortune.png", {{ type: "image/png" }});

              if (navigator.canShare && navigator.canShare({{ files: [file] }})) {{
                await navigator.share({{
                  title: "2026년 운세",
                  text: "내 운세 결과 공유!",
                  files: [file]
                }});
              }} else {{
                alert("이 브라우저는 '공유'를 지원하지 않아요. 아래 '이미지 저장하기'로 저장 후 공유해주세요.");
              }}
            }} catch (e) {{
              alert("공유를 열지 못했어요. 아래 '이미지 저장하기'로 저장 후 공유해주세요.");
            }}
          }})();
        </script>
        """, height=0)

        # 보험(공유 미지원 브라우저 대비): 저장 버튼 제공
        st.download_button(
            "이미지 저장하기(PNG)",
            data=png_bytes,
            file_name="2026_fortune.png",
            mime="image/png",
            use_container_width=True
        )
        st.caption("공유창이 안 뜨면: 저장 → 갤러리에서 공유 버튼(카톡 선택)으로 보내면 돼요.")

    st.markdown(f"<div style='text-align:center; color:#6b6b6b; font-size:12px; margin-top:10px;'>{APP_URL}</div>", unsafe_allow_html=True)

    if st.button("처음부터 다시하기", use_container_width=True, key="reset_btn"):
        st.session_state.result_shown = False
        st.session_state.share_png = None
        st.rerun()
