import json
import time
import hashlib
from datetime import date
from pathlib import Path

import streamlit as st

# =========================
# 설정
# =========================
APP_TITLE = "🔮 2026 띠 + MBTI + 사주 + 오늘/내일 운세"
DB_PATH = Path("data/fortunes_ko.json")  # ✅ 레포 구조: data/fortunes_ko.json

# 미니게임 설정
STOPWATCH_TARGET = 20.26
STOPWATCH_TOLERANCE = 0.08  # ±0.08초 안이면 성공(원하면 조절)

# 구글시트(기억해둔 ID)
DEFAULT_SHEET_ID = "1WvuKXx2if2WvxmQaxkqzFW-BzDEWWma9hZgCr2jJQYY"


# =========================
# 유틸
# =========================
def stable_hash_int(text: str) -> int:
    """파이썬 내장 hash()는 실행마다 바뀌므로, sha256 기반으로 고정 해시."""
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return int(h[:16], 16)


def safe_pick(pool: list, seed: str) -> str:
    if not pool:
        return ""
    idx = stable_hash_int(seed) % len(pool)
    return pool[idx]


def zodiac_from_year(year: int) -> str:
    """
    한국에서 통용되는 12지 띠 계산.
    2008년 = 쥐(자) 기준으로 맞춤.
    """
    animals = ["쥐", "소", "호랑이", "토끼", "용", "뱀", "말", "양", "원숭이", "닭", "개", "돼지"]
    idx = (year - 2008) % 12
    return animals[idx]


def normalize_combo_key(zodiac_korean: str, mbti: str) -> str:
    # DB 콤보 키 형태: "닭_ENFP"
    return f"{zodiac_korean}_{mbti.upper()}"


def load_db() -> dict:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"DB 파일을 찾을 수 없습니다: {DB_PATH.as_posix()}")
    with DB_PATH.open("r", encoding="utf-8") as f:
        db = json.load(f)

    # fortune-db-v1 스키마 최소 검증
    required_top = ["meta", "zodiacs", "combos"]
    missing = [k for k in required_top if k not in db]
    if missing:
        raise ValueError(f"DB 구조 오류: {', '.join(missing)} 키가 없습니다. (올바른 fortunes_ko.json 업로드 필요)")
    if not isinstance(db["combos"], dict):
        raise ValueError("DB 구조 오류: combos 형식이 dict가 아닙니다.")
    return db


def infer_mbti_from_quicktest(answers: dict) -> str:
    """
    answers: {"E": int, "I": int, ...}
    """
    e = answers.get("E", 0)
    i = answers.get("I", 0)
    s = answers.get("S", 0)
    n = answers.get("N", 0)
    t = answers.get("T", 0)
    f = answers.get("F", 0)
    j = answers.get("J", 0)
    p = answers.get("P", 0)

    mbti = ""
    mbti += "E" if e >= i else "I"
    mbti += "S" if s >= n else "N"
    mbti += "T" if t >= f else "F"
    mbti += "J" if j >= p else "P"
    return mbti


def get_combo(db: dict, zodiac_korean: str, mbti: str) -> dict | None:
    key = normalize_combo_key(zodiac_korean, mbti)
    return db["combos"].get(key)


def render_ad():
    st.markdown("---")
    st.subheader("📢 광고: 다나눔렌탈")
    st.markdown(
        """
**정수기 · 안마의자 · 가전 렌탈 상담**  
- 최저가 비교 / 빠른 상담  
- 문의: **1660-2445**  
"""
    )
    st.link_button("다나눔렌탈 바로가기", "https://www.xn--910b51a1r88nu39a.com/")


# =========================
# 구글시트 기록(선택)
# =========================
def append_to_sheet(row: list[str], sheet_id: str = DEFAULT_SHEET_ID) -> tuple[bool, str]:
    """
    Streamlit secrets에 서비스계정이 있으면 기록.
    secrets 예시(필수):
    [gcp_service_account]
    type="service_account"
    project_id="..."
    private_key="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
    client_email="...@....iam.gserviceaccount.com"
    ...
    """
    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except Exception:
        return False, "라이브러리(gspread/google-auth) 설치가 필요합니다. requirements.txt 확인"

    if "gcp_service_account" not in st.secrets:
        return False, "Streamlit secrets에 gcp_service_account가 없습니다."

    try:
        creds = Credentials.from_service_account_info(
            dict(st.secrets["gcp_service_account"]),
            scopes=["https://www.googleapis.com/auth/spreadsheets"],
        )
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(sheet_id)
        ws = sh.sheet1
        ws.append_row(row, value_input_option="USER_ENTERED")
        return True, "기록 완료"
    except Exception as e:
        return False, f"시트 기록 실패: {e}"


# =========================
# MBTI 입력 UI (변화 금지 조건 반영)
# - 직접 선택 OR 모르면 12문항/16문항
# =========================
def mbti_input_section() -> tuple[str | None, dict]:
    st.subheader("🧠 MBTI 입력")

    mode = st.radio(
        "MBTI를 어떻게 입력할까요?",
        ["직접 선택", "모르면 간단 테스트(12문항)", "모르면 간단 테스트(16문항)"],
        horizontal=False,
    )

    if mode == "직접 선택":
        mbti = st.selectbox(
            "MBTI 선택",
            [
                "ISTJ","ISFJ","INFJ","INTJ",
                "ISTP","ISFP","INFP","INTP",
                "ESTP","ESFP","ENFP","ENTP",
                "ESTJ","ESFJ","ENFJ","ENTJ",
            ],
            index=10,  # ENFP 기본
        )
        return mbti, {"mode": mode}

    # 테스트: 각 축(E/I, S/N, T/F, J/P) 당 n문항(12=3문항씩, 16=4문항씩)
    per_axis = 3 if "12" in mode else 4

    st.caption("각 문항에서 더 가까운 쪽을 선택하세요. (아주 간단 버전)")
    scores = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}

    def q(label: str, left_key: str, right_key: str, left_text: str, right_text: str, i: int):
        choice = st.radio(
            label,
            [left_text, right_text],
            key=f"{left_key}{right_key}_{i}",
            horizontal=False,
        )
        if choice == left_text:
            scores[left_key] += 1
        else:
            scores[right_key] += 1

    st.markdown("#### 에너지 방향")
    for i in range(per_axis):
        q(f"{i+1}. 사람들과 함께할 때 에너지가 난다 / 혼자 있을 때 충전된다",
          "E", "I", "E (사람들과 함께)", "I (혼자 있을 때)", i)

    st.markdown("#### 정보 인식")
    for i in range(per_axis):
        q(f"{i+1}. 사실/경험이 중요 / 의미/가능성이 중요",
          "S", "N", "S (사실·경험)", "N (의미·가능성)", i)

    st.markdown("#### 의사결정")
    for i in range(per_axis):
        q(f"{i+1}. 원칙/논리로 판단 / 가치/공감으로 판단",
          "T", "F", "T (원칙·논리)", "F (가치·공감)", i)

    st.markdown("#### 생활양식")
    for i in range(per_axis):
        q(f"{i+1}. 계획/정리 선호 / 유연/즉흥 선호",
          "J", "P", "J (계획·정리)", "P (유연·즉흥)", i)

    mbti = infer_mbti_from_quicktest(scores)
    st.success(f"예상 MBTI: **{mbti}**")
    return mbti, {"mode": mode, "scores": scores}


# =========================
# 미니게임: 스톱워치 20.26초
# =========================
def minigame_section():
    st.subheader("🎮 미니게임: 20.26초 정확히 맞추기")

    if "sw_running" not in st.session_state:
        st.session_state.sw_running = False
        st.session_state.sw_start = None
        st.session_state.sw_last = None
        st.session_state.sw_attempts = 0
        st.session_state.sw_retry_available = False  # 공유로 1회 재도전

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("START", use_container_width=True, disabled=st.session_state.sw_running):
            st.session_state.sw_running = True
            st.session_state.sw_start = time.time()
            st.session_state.sw_last = None

    with col2:
        if st.button("STOP", use_container_width=True, disabled=not st.session_state.sw_running):
            elapsed = time.time() - (st.session_state.sw_start or time.time())
            st.session_state.sw_running = False
            st.session_state.sw_last = elapsed
            st.session_state.sw_attempts += 1

    with col3:
        if st.button("전체 초기화", use_container_width=True):
            st.session_state.sw_running = False
            st.session_state.sw_start = None
            st.session_state.sw_last = None
            st.session_state.sw_attempts = 0
            st.session_state.sw_retry_available = False
            st.rerun()

    if st.session_state.sw_running and st.session_state.sw_start:
        elapsed = time.time() - st.session_state.sw_start
        st.info(f"진행 중… {elapsed:.2f}초")

    if st.session_state.sw_last is not None:
        elapsed = st.session_state.sw_last
        diff = abs(elapsed - STOPWATCH_TARGET)
        st.write(f"기록: **{elapsed:.2f}초** (목표 {STOPWATCH_TARGET:.2f}초, 오차 {diff:.2f}초)")

        success = diff <= STOPWATCH_TOLERANCE
        if success:
            st.success("🎉 성공! (커피쿠폰 응모 가능)")
            with st.form("minigame_success_form"):
                name = st.text_input("이름", value="")
                phone = st.text_input("전화번호", value="", help="예: 010-1234-5678")
                submit = st.form_submit_button("응모하기")
            if submit:
                if not name.strip() or not phone.strip():
                    st.warning("이름/전화번호를 입력해 주세요.")
                else:
                    ok, msg = append_to_sheet(
                        [
                            time.strftime("%Y-%m-%d %H:%M:%S"),
                            "minigame_success",
                            name.strip(),
                            phone.strip(),
                            f"{elapsed:.2f}",
                        ]
                    )
                    if ok:
                        st.success("응모가 접수되었습니다. 감사합니다!")
                    else:
                        st.error(f"응모 저장 실패: {msg}")
        else:
            st.error("아쉽게 실패! 😭")
            # 공유로 1회 재도전 제공 (진짜 공유 기능 대신 버튼으로 처리)
            if not st.session_state.sw_retry_available:
                if st.button("친구에게 공유하기 (1회 재도전)", use_container_width=True):
                    st.session_state.sw_retry_available = True
                    st.info("재도전 1회가 활성화되었습니다. 다시 START 해보세요!")
            else:
                st.warning("재도전 1회가 활성화된 상태입니다.")


# =========================
# 상담/응모 폼(광고 연계)
# =========================
def lead_form_section():
    st.subheader("📝 상담/쿠폰 신청 (다나눔렌탈)")

    with st.form("lead_form"):
        name = st.text_input("이름")
        phone = st.text_input("전화번호")
        product = st.selectbox("관심 상품", ["정수기 렌탈", "안마의자 렌탈", "기타 가전 렌탈"])
        consult = st.radio("상담 요청", ["O", "X"], horizontal=True, index=0)
        coupon = st.radio("커피쿠폰 응모", ["O", "X"], horizontal=True, index=0)

        submitted = st.form_submit_button("제출")
    if submitted:
        if not name.strip() or not phone.strip():
            st.warning("이름/전화번호를 입력해 주세요.")
            return

        consult_yes = consult == "O"
        coupon_yes = coupon == "O"

        # ✅ 조건: 정수기 렌탈 + 상담요청 O + 커피쿠폰 X => 구글시트 입력 금지
        if (product == "정수기 렌탈") and consult_yes and (not coupon_yes):
            st.info("상담 요청은 접수되었지만, 커피쿠폰 응모가 아니므로 구글시트에는 저장하지 않습니다.")
            return

        ok, msg = append_to_sheet(
            [
                time.strftime("%Y-%m-%d %H:%M:%S"),
                "lead",
                name.strip(),
                phone.strip(),
                product,
                consult,
                coupon,
            ]
        )
        if ok:
            st.success("제출 완료! 곧 연락드릴게요.")
        else:
            st.error(f"저장 실패: {msg}")


# =========================
# 운세 렌더
# =========================
def render_fortune(db: dict, name: str, birth: date, mbti: str):
    zodiac_korean = zodiac_from_year(birth.year)

    st.header("결과")
    st.write(f"띠 운세: **{zodiac_korean}**")
    st.write(f"MBTI 특징: **{mbti}**")

    combo = get_combo(db, zodiac_korean, mbti)
    if not combo:
        st.error(f"데이터에 조합 키가 없습니다: {zodiac_korean}_{mbti}")
        st.info("DB의 combos 키(예: 닭_ENFP)와 띠/MBTI 표기가 일치하는지 확인해 주세요.")
        return

    # DB에서 뽑아오는 값들(요청: 같은 생년월일이면 항상 같은 결과)
    seed_base = f"{birth.isoformat()}|{mbti}|{zodiac_korean}"

    def pick_field(field: str) -> str:
        pool = combo.get(field)
        if isinstance(pool, list):
            return safe_pick(pool, seed_base + "|" + field)
        if isinstance(pool, str):
            return pool
        return ""

    st.subheader("사주 한 마디")
    st.write(pick_field("saju_message"))

    st.subheader("오늘 운세")
    st.write(pick_field("today"))

    st.subheader("내일 운세")
    st.write(pick_field("tomorrow"))

    st.subheader("2026 전체 운세")
    st.write(pick_field("year_2026"))

    st.subheader("조합 조언")
    st.write(f"연애운: {pick_field('love')}")
    st.write(f"재물운: {pick_field('money')}")
    st.write(f"일/학업운: {pick_field('work')}")
    st.write(f"건강운: {pick_field('health')}")

    st.subheader("행운 포인트")
    lucky = combo.get("lucky_point", {})
    if isinstance(lucky, dict):
        st.write(
            f"색: {lucky.get('color','')} · 아이템: {lucky.get('item','')} · "
            f"숫자: {lucky.get('number','')} · 방향: {lucky.get('direction','')}"
        )

    st.subheader("오늘의 액션팁")
    st.write(pick_field("action_tip"))

    st.subheader("주의할 점")
    st.write(pick_field("caution"))


# =========================
# SEO 키워드(검색 노출용 텍스트)
# =========================
def seo_keywords_block():
    # 화면을 지저분하게 만들지 않으려고 expander로 처리
    with st.expander("🔎 검색 키워드(SEO)"):
        st.write(
            "키워드: 2026 운세, 띠 운세, MBTI 운세, 사주, 오늘 운세, 내일 운세, "
            "정수기 렌탈, 다나눔렌탈, 커피쿠폰, 미니게임, 스톱워치 20.26초, "
            "무료 운세, 성격 유형 검사, MBTI 12문항, MBTI 16문항, 상담 신청"
        )


# =========================
# 메인
# =========================
def main():
    st.set_page_config(page_title="2026 운세", page_icon="🔮", layout="centered")
    st.title(APP_TITLE)
    st.caption("완전 무료")

    # DB 경로 노출(디버깅용)
    st.caption(f"DB 경로: {DB_PATH.as_posix()}")

    try:
        db = load_db()
    except Exception as e:
        st.error(f"DB 로드/구조 오류: {e}")
        st.stop()

    st.subheader("입력")
    name = st.text_input("이름 (결과에 표시돼요)", value="")
    c1, c2, c3 = st.columns(3)
    with c1:
        year = st.number_input("년", min_value=1900, max_value=2100, value=1982, step=1)
    with c2:
        month = st.number_input("월", min_value=1, max_value=12, value=1, step=1)
    with c3:
        day = st.number_input("일", min_value=1, max_value=31, value=1, step=1)

    # 날짜 검증
    try:
        birth = date(int(year), int(month), int(day))
    except Exception:
        st.warning("생년월일이 올바르지 않아요. (월/일 확인)")
        st.stop()

    mbti, mbti_meta = mbti_input_section()

    st.markdown("---")
    if st.button("결과 보기", use_container_width=True):
        st.session_state["show_result"] = True

    if st.session_state.get("show_result"):
        render_fortune(db, name=name.strip(), birth=birth, mbti=mbti)

        # 광고/폼/미니게임 복구(요청 사항)
        render_ad()
        lead_form_section()
        minigame_section()
        seo_keywords_block()


if __name__ == "__main__":
    main()
