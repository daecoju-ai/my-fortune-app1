import json
import hashlib
import random
from datetime import date, datetime, time
from pathlib import Path

import streamlit as st

# =========================================================
# 고정 설정 (디자인/문구 임의 변경 금지)
# =========================================================
APP_TITLE = "2026년 운세"
TAB_TODAY = "오늘의 운세"
TAB_TOMORROW = "내일의 운세"
TAB_YEAR = "2026년 전체 운세"
TAB_EVENT = "이벤트 스톱워치"

AD_TEXT = "[광고] 정수기 렌탈 제휴카드 적용시 월 렌탈비 0원, 설치당일 최대 현금50만원 + 사은품 증정"
AD_CTA = "무료 상담하기"

# 구글시트 컬럼 고정 (사용자 스크린샷 기준)
SHEET_COLUMNS = ["시간", "이름", "전화번호", "언어", "기록초", "공유여부", "상담신청"]

# 이벤트 고정 문구
EVENT_NOTICE = "커피쿠폰 선착순 지급 / 소진시 조기 종료될 수 있습니다"
EVENT_TARGET = (20.260, 20.269)  # inclusive range
EVENT_SUCCESS_MSG = "성공시 {record:.3f}초 기록. 쿠폰지급을 위해 이름, 전화번호 입력해주세요"
EVENT_FAIL_MSG = "실패시 {record:.3f}초 기록 친구공유시 도전기회 1회추가 또는 정수기렌탈 상담신청 후 커피쿠폰 응모"


# =========================================================
# 파일/DB 로드 유틸
# =========================================================
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def require_file(rel_path: str):
    p = DATA_DIR / rel_path
    if not p.exists():
        raise FileNotFoundError(f"필수 DB 파일을 읽을 수 없습니다: {rel_path}\n에러: [Errno 2] No such file or directory: '{rel_path}'")
    return p


def stable_seed(*parts: str) -> int:
    raw = "|".join(parts).encode("utf-8")
    h = hashlib.sha256(raw).hexdigest()
    return int(h[:16], 16)


def pick_from_list(lst, seed: int):
    if not isinstance(lst, list) or len(lst) == 0:
        raise IndexError("선택 가능한 문장이 비어있습니다.")
    rnd = random.Random(seed)
    return rnd.choice(lst)


# =========================================================
# 띠/MBTI/사주 연결
# =========================================================
ZODIAC_ORDER = ["rat", "ox", "tiger", "rabbit", "dragon", "snake", "horse", "goat", "monkey", "rooster", "dog", "pig"]
ZODIAC_KO = {
    "rat": "쥐",
    "ox": "소",
    "tiger": "호랑이",
    "rabbit": "토끼",
    "dragon": "용",
    "snake": "뱀",
    "horse": "말",
    "goat": "양",
    "monkey": "원숭이",
    "rooster": "닭",
    "dog": "개",
    "pig": "돼지",
}


def parse_birthdate(d: date):
    # Streamlit date_input은 date 객체로 들어옴
    return d


def zodiac_from_birthdate_gregorian(birth: date, lunar_new_year_table):
    """
    한국 기준(음력 설)으로 '띠'를 결정:
    - 해당 연도 음력설 이전에 태어나면 전년도 띠
    - 이후면 해당 연도 띠
    """
    y = birth.year

    # 테이블 구조: { "1920": "1920-02-05", ... } 같은 단순 매핑을 기대
    # (혹시 구조가 다르면 여기만 맞추면 됨)
    if isinstance(lunar_new_year_table, dict) and str(y) in lunar_new_year_table:
        lny_str = lunar_new_year_table[str(y)]
        lny = datetime.strptime(lny_str, "%Y-%m-%d").date()
    else:
        # 테이블이 예상 구조가 아니거나 연도 누락 시: 안전 fallback (양력 기준)
        lny = date(y, 2, 4)

    zodiac_year = y - 1 if birth < lny else y
    idx = zodiac_year % 12
    key = ZODIAC_ORDER[idx]
    return key


def mbti_normalize(s: str) -> str:
    if not s:
        return ""
    s = s.strip().upper()
    # 간단 검증
    if len(s) != 4:
        return ""
    for ch in s:
        if ch not in "EISNTFJP":
            return ""
    return s


# =========================================================
# Google Sheet 연동 (이 프로젝트에서는 "UI/시스템"만 유지)
# - 실제 전송 로직은 기존에 쓰던 방식이 있을 거라 가정
# - 여기서는 "연동 자리"만 유지하고, 데이터 구조 고정이 핵심
# =========================================================
def append_to_sheet_stub(row: dict):
    """
    기존 프로젝트에서 쓰던 구글시트 연동 방식이 있으면
    이 함수 내부만 그 방식으로 교체하면 됨.
    (컬럼은 SHEET_COLUMNS 고정)
    """
    # 현재는 Streamlit Cloud에서 테스트용으로 session_state에만 기록
    st.session_state.setdefault("_local_sheet_rows", [])
    st.session_state["_local_sheet_rows"].append(row)


# =========================================================
# 이벤트 스톱워치 (요구사항 반영)
# - 기록 직접 입력 금지
# - Start 누르면 시작, Stop 누르면 멈춘 화면 + 기록 표시
# - 소수점 3자리, 00.000 형식(분 단위 제거)
# - 시도횟수 차감, 버튼 비활성화
# =========================================================
def fmt_seconds(sec: float) -> str:
    return f"{sec:06.3f}"  # 00.000 형태 (최대 999.999)


def ensure_event_state():
    ss = st.session_state
    ss.setdefault("event_attempts", 1)
    ss.setdefault("event_running", False)
    ss.setdefault("event_start_ts", None)
    ss.setdefault("event_result_sec", None)
    ss.setdefault("event_stopped", False)  # stop 눌러서 결과 고정 상태
    ss.setdefault("event_shared", False)   # 공유로 +1
    ss.setdefault("event_consult", False)  # 상담신청으로 응모
    ss.setdefault("event_name", "")
    ss.setdefault("event_phone", "")


def event_start():
    ss = st.session_state
    if ss["event_attempts"] <= 0:
        return
    if ss["event_running"]:
        return
    ss["event_running"] = True
    ss["event_stopped"] = False
    ss["event_result_sec"] = None
    ss["event_start_ts"] = datetime.utcnow().timestamp()


def event_stop():
    ss = st.session_state
    if not ss["event_running"]:
        return
    now = datetime.utcnow().timestamp()
    elapsed = max(0.0, now - float(ss["event_start_ts"] or now))
    ss["event_running"] = False
    ss["event_stopped"] = True
    ss["event_result_sec"] = elapsed
    ss["event_attempts"] = max(0, ss["event_attempts"] - 1)


def is_success(record: float) -> bool:
    lo, hi = EVENT_TARGET
    return (record >= lo) and (record <= hi)


# =========================================================
# 메인 UI
# =========================================================
def main():
    st.set_page_config(page_title=APP_TITLE, layout="centered")

    # -----------------------------
    # DB 로드 (파일명 고정)
    # -----------------------------
    try:
        fortunes_2026 = load_json(require_file("fortunes_ko_2026.json"))
        fortunes_today = load_json(require_file("fortunes_ko_today.json"))
        fortunes_tomorrow = load_json(require_file("fortunes_ko_tomorrow.json"))
        zodiac_db = load_json(require_file("zodiac_fortunes_ko_2026.json"))
        mbti_db = load_json(require_file("mbti_traits_ko.json"))
        saju_db = load_json(require_file("saju_ko.json"))
        lunar_new_year = load_json(require_file("lunar_new_year_1920_2026.json"))
        # 타로는 "나중에" -> 로드만 (미사용)
        _tarot_db = load_json(require_file("tarot_db_ko.json"))
    except Exception as e:
        # 디자인 건드리지 않고, 기존처럼 상단 에러 박스 형태로만 노출
        st.error(str(e))
        return

    # -----------------------------
    # 헤더
    # -----------------------------
    st.title(APP_TITLE)

    tabs = st.tabs([TAB_TODAY, TAB_TOMORROW, TAB_YEAR, TAB_EVENT])

    # =========================================================
    # 1) 오늘의 운세 (띠 기반: zodiac_fortunes_ko_2026.json 사용)
    # =========================================================
    with tabs[0]:
        st.subheader("띠 선택")

        zodiac_keys = [k for k in ZODIAC_ORDER if k in zodiac_db]
        if len(zodiac_keys) != 12:
            st.error("DB 구조 오류: zodiac DB에 12띠 데이터가 완전하지 않습니다.")
            return

        zodiac_label_list = [f"{ZODIAC_KO[k]}띠" for k in zodiac_keys]
        selected_label = st.selectbox("", zodiac_label_list, index=0)
        selected_key = zodiac_keys[zodiac_label_list.index(selected_label)]

        # 안전 접근 (오류 메시지 고정 스타일)
        try:
            today_list = zodiac_db[selected_key].get("today", [])
            seed = stable_seed("zodiac", "today", selected_key, str(date.today()))
            text = pick_from_list(today_list, seed)
            st.write(text)
        except Exception as e:
            st.error(f"DB 구조 오류: zodiac.{selected_key}.today 경로가 없거나 비어있습니다.\n{e}")
            return

    # =========================================================
    # 2) 내일의 운세 (띠 기반)
    # =========================================================
    with tabs[1]:
        st.subheader("띠 선택")

        zodiac_keys = [k for k in ZODIAC_ORDER if k in zodiac_db]
        zodiac_label_list = [f"{ZODIAC_KO[k]}띠" for k in zodiac_keys]
        selected_label = st.selectbox("", zodiac_label_list, index=0, key="tomorrow_zodiac")
        selected_key = zodiac_keys[zodiac_label_list.index(selected_label)]

        try:
            tomorrow_list = zodiac_db[selected_key].get("tomorrow", [])
            tomorrow_date = date.today().toordinal() + 1
            seed = stable_seed("zodiac", "tomorrow", selected_key, str(tomorrow_date))
            text = pick_from_list(tomorrow_list, seed)
            st.write(text)
        except Exception as e:
            st.error(f"DB 구조 오류: zodiac.{selected_key}.tomorrow 경로가 없거나 비어있습니다.\n{e}")
            return

    # =========================================================
    # 3) 2026년 전체 운세 (일반 풀 + MBTI + 사주 + 띠 연결)
    # =========================================================
    with tabs[2]:
        st.subheader("생년월일 / MBTI")

        # 생년월일: 달력(요구사항 반영)
        birth = st.date_input("생년월일", value=date(2000, 1, 1))

        mbti_in = st.text_input("MBTI (예: ENFP)", value="").strip().upper()
        mbti_type = mbti_normalize(mbti_in)

        # 1) 2026년 전체운세(고정: year_all)
        try:
            year_all = fortunes_2026.get("pools", {}).get("year_all", [])
            seed_year = stable_seed("2026", "year_all", str(birth), mbti_type or "none")
            year_text = pick_from_list(year_all, seed_year)
            st.write(year_text)
        except Exception as e:
            st.error(f"DB 구조 오류: fortunes_ko_2026.pools.year_all 경로가 없거나 비어있습니다.\n{e}")
            return

        # 2) 조언(advice)
        try:
            advice_pool = fortunes_2026.get("pools", {}).get("advice", [])
            seed_adv = stable_seed("2026", "advice", str(birth), mbti_type or "none")
            advice_text = pick_from_list(advice_pool, seed_adv)
            st.subheader("조언")
            st.write(advice_text)
        except Exception as e:
            st.error(f"DB 구조 오류: fortunes_ko_2026.pools.advice 경로가 없거나 비어있습니다.\n{e}")
            return

        # 3) 띠(한국 음력설 기준) + 띠별(2026년)
        try:
            zodiac_key = zodiac_from_birthdate_gregorian(birth, lunar_new_year)
            year_list = zodiac_db[zodiac_key].get("year", [])
            seed_z_year = stable_seed("zodiac", "year", zodiac_key, "2026")
            zodiac_year_text = pick_from_list(year_list, seed_z_year)
            st.subheader("2026년 띠운세")
            st.write(zodiac_year_text)
        except Exception as e:
            st.error(f"DB 구조 오류: zodiac.{zodiac_key}.year 경로가 없거나 비어있습니다.\n{e}")
            return

        # 4) MBTI 해석 (mbti_traits_ko.json 실제 구조 반영: traits[TYPE])
        if mbti_type:
            try:
                traits_map = mbti_db.get("traits", {})
                info = traits_map.get(mbti_type)
                if not info:
                    st.error(f"DB 구조 오류: mbti.traits.{mbti_type} 경로가 없습니다.")
                else:
                    st.subheader("MBTI 요약")
                    # 가능한 키들: keywords / strengths / pitfalls / tip 등 (DB에 맞춰 유연 출력)
                    if isinstance(info, dict):
                        if "summary" in info:
                            st.write(info["summary"])
                        elif "keywords" in info and isinstance(info["keywords"], list):
                            st.write("키워드: " + ", ".join(info["keywords"]))
                        # 길게 나오지 않게 핵심만
                        if "strengths" in info and isinstance(info["strengths"], list) and len(info["strengths"]) > 0:
                            st.write("강점: " + " / ".join(info["strengths"][:3]))
                        if "pitfalls" in info and isinstance(info["pitfalls"], list) and len(info["pitfalls"]) > 0:
                            st.write("주의: " + " / ".join(info["pitfalls"][:3]))
                        if "tip" in info and isinstance(info["tip"], str):
                            st.write("한줄 팁: " + info["tip"])
            except Exception as e:
                st.error(f"DB 구조 오류: mbti DB 처리 중 오류\n{e}")

        # 5) 사주(간단 적용: 오행 안내 DB 출력용)
        # - 정교한 사주 계산은 이후(요구사항대로 DB 기반 확장 가능)
        try:
            elements = saju_db.get("elements", [])
            if isinstance(elements, list) and len(elements) > 0:
                # 생년 기반으로 오행 하나를 '고정 선택'(임시 연결)
                idx = stable_seed("saju", str(birth.year)) % len(elements)
                el = elements[idx]
                st.subheader("사주(오행) 참고")
                if isinstance(el, dict):
                    name = el.get("name_ko", el.get("name", ""))
                    desc = el.get("desc", "")
                    if name:
                        st.write(f"- 오행: {name}")
                    if desc:
                        st.write(desc)
        except Exception as e:
            st.error(f"DB 구조 오류: saju DB 처리 중 오류\n{e}")

        # -----------------------------
        # 광고(고정 문구)
        # -----------------------------
        st.divider()
        st.write(AD_TEXT)
        ad_name = st.text_input("이름", key="ad_name")
        ad_phone = st.text_input("전화번호", key="ad_phone")
        if st.button(AD_CTA):
            row = {
                "시간": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "이름": ad_name.strip(),
                "전화번호": ad_phone.strip(),
                "언어": "ko",
                "기록초": "",
                "공유여부": False,
                "상담신청": "O(정수기 렌탈 상담)",
            }
            append_to_sheet_stub(row)
            st.success("접수되었습니다.")

    # =========================================================
    # 4) 이벤트 스톱워치
    # =========================================================
    with tabs[3]:
        ensure_event_state()
        st.subheader("커피쿠폰 이벤트")
        st.write(EVENT_NOTICE)
        st.write(f"목표 구간: {EVENT_TARGET[0]:.3f} ~ {EVENT_TARGET[1]:.3f}초")
        st.write(f"도전 횟수: {st.session_state['event_attempts']}/1")

        # 표시부(00.000 고정)
        if st.session_state["event_running"]:
            # 실시간 표시 (단, Stop하면 멈춘 화면이 유지되도록 result에 고정)
            now = datetime.utcnow().timestamp()
            elapsed = max(0.0, now - float(st.session_state["event_start_ts"] or now))
            st.markdown(f"### {fmt_seconds(elapsed)}")
        elif st.session_state["event_stopped"] and st.session_state["event_result_sec"] is not None:
            st.markdown(f"### {fmt_seconds(float(st.session_state['event_result_sec']))}")
        else:
            st.markdown("### 00.000")

        col1, col2 = st.columns(2)
        with col1:
            st.button(
                "START",
                on_click=event_start,
                disabled=(st.session_state["event_running"] or st.session_state["event_attempts"] <= 0),
            )
        with col2:
            st.button(
                "STOP",
                on_click=event_stop,
                disabled=(not st.session_state["event_running"]),
            )

        # Stop 후 결과 문구 + 입력폼
        if st.session_state["event_stopped"] and st.session_state["event_result_sec"] is not None:
            record = float(st.session_state["event_result_sec"])
            ok = is_success(record)
            st.divider()

            if ok:
                st.success(EVENT_SUCCESS_MSG.format(record=record))
                st.session_state["event_name"] = st.text_input("이름", value=st.session_state["event_name"])
                st.session_state["event_phone"] = st.text_input("전화번호", value=st.session_state["event_phone"])

                if st.button("쿠폰 지급 신청"):
                    row = {
                        "시간": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "이름": st.session_state["event_name"].strip(),
                        "전화번호": st.session_state["event_phone"].strip(),
                        "언어": "ko",
                        "기록초": f"{record:.3f}",
                        "공유여부": bool(st.session_state.get("event_shared", False)),
                        "상담신청": "O(커피쿠폰 성공)",
                    }
                    append_to_sheet_stub(row)
                    st.success("응모가 접수되었습니다.")
            else:
                st.error(EVENT_FAIL_MSG.format(record=record))

                # 공유/상담으로 기회 추가(요구사항 반영: 공유 시 +1)
                share_col, consult_col = st.columns(2)

                with share_col:
                    # 웹에서 직접 친구공유는 브라우저 제한이 있을 수 있어 "URL 복사"는 유지
                    if st.button("친구에게 공유하기"):
                        st.session_state["event_shared"] = True
                        st.session_state["event_attempts"] = st.session_state["event_attempts"] + 1
                        st.info("공유 처리되었습니다. 도전기회 1회 추가!")

                with consult_col:
                    if st.button("정수기렌탈 상담신청 후 응모"):
                        st.session_state["event_consult"] = True
                        st.info("상담신청 처리되었습니다. 응모가 가능합니다.")

                # 실패 기록도 저장(필요 시)
                if st.button("실패 기록 저장"):
                    row = {
                        "시간": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "이름": "",
                        "전화번호": "",
                        "언어": "ko",
                        "기록초": f"{record:.3f}",
                        "공유여부": bool(st.session_state.get("event_shared", False)),
                        "상담신청": "X(커피쿠폰 실패)",
                    }
                    append_to_sheet_stub(row)
                    st.success("기록이 저장되었습니다.")


if __name__ == "__main__":
    main()
