import streamlit as st
from datetime import datetime, timedelta
import hashlib

# (언어 번역 부분은 이전과 동일하게 유지 - 생략해서 코드 짧게)
# 실제로는 translations, zodiacs, mbtis, daily_messages 딕셔너리 그대로 넣어줘

# ────────────────────────────────────────────────
#                  간단한 3개 언어 설정 (예시)
# ────────────────────────────────────────────────
if "lang" not in st.session_state:
    st.session_state.lang = "ko"

t = {
    "ko": {
        "title": "🌟 2026 띠 + MBTI + 사주 운세 🌟",
        "birth": "### 생년월일 입력",
        "year": "년", "month": "월", "day": "일",
        "next_btn": "✅ 생년월일 다 적었어! 다음으로 →",
        "mbti_mode": "MBTI 어떻게 할까?",
        "direct": "직접 입력",
        "test": "상세 테스트 (16문제)",
        "test_start": "상세 테스트 시작! 😊",
        "fortune_btn": "🔮 2026년 운세 보기!",
        "reset": "처음부터 다시 하기",
        "daily_title": "🌞 오늘 & 내일의 운세",
        "today": "오늘", "tomorrow": "내일",
        "best_combo": "최고 조합!"
    },
    # en, zh도 필요하면 추가
}[st.session_state.lang]

st.title(t["title"])

# 생년월일 입력
st.write(t["birth"])
col1, col2, col3 = st.columns(3)
year = col1.number_input(t["year"], 1900, 2030, 2005, step=1)
month = col2.number_input(t["month"], 1, 12, 1, step=1)
day = col3.number_input(t["day"], 1, 31, 1, step=1)

# 생년월일 입력 완료 버튼
if st.button(t["next_btn"], type="primary", use_container_width=True):
    st.session_state["birth_done"] = True
    st.balloons()
    st.success("좋아! 이제 MBTI를 선택해보자~ ↓↓↓")
    st.rerun()

# MBTI 선택 단계 (생년월일 입력 후에만 보임)
if st.session_state.get("birth_done", False):
    if "mbti" not in st.session_state:
        st.session_state.mbti = None

    if st.session_state.mbti is None:
        st.write(t["mbti_mode"])
        choice = st.radio("선택", [t["direct"], t["test"]])

        if choice == t["direct"]:
            mbti_direct = st.selectbox("MBTI 골라봐!", [
                "INTJ", "INTP", "ENTJ", "ENTP",
                "INFJ", "INFP", "ENFJ", "ENFP",
                "ISTJ", "ISFJ", "ESTJ", "ESFJ",
                "ISTP", "ISFP", "ESTP", "ESFP"
            ])
            if st.button("이걸로 결정!"):
                st.session_state.mbti = mbti_direct
                st.rerun()

        else:  # 상세 테스트
            st.write(t["test_start"])

            # 4가지 축점수 초기화
            if "scores" not in st.session_state:
                st.session_state.scores = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}

            # 문제 리스트 (16문제 - 간단 버전)
            questions = [
                ("1. 사람 많은 곳에서 에너지 충전됨?", "E", "I"),
                ("2. 새로운 사람 만나는 게 즐거움?", "E", "I"),
                ("3. 세세한 사실 기억 잘함?", "S", "N"),
                ("4. 큰 그림/미래 가능성 더 중요?", "S", "N"),
                ("5. 논리와 사실로 판단함?", "T", "F"),
                ("6. 사람들의 감정 먼저 고려함?", "T", "F"),
                ("7. 계획 세우고 따라가는 걸 좋아함?", "J", "P"),
                ("8. 유연하게 상황에 맞춰가는 걸 좋아함?", "J", "P"),
                # 9~16문제도 비슷하게 추가 (간단히 8개만 넣음)
                ("9. 혼자 있을 때 더 편안함?", "E", "I"),
                ("10. 상상력/아이디어 떠올리는 게 좋음?", "S", "N"),
                ("11. 옳고 그름이 명확해야 함?", "T", "F"),
                ("12. 다른 사람 기분 맞춰주는 게 중요?", "T", "F"),
                ("13. 일정표/할 일 목록 좋아함?", "J", "P"),
                ("14. 즉흥적인 결정이 재미있음?", "J", "P"),
                ("15. 친구들과 자주 어울림?", "E", "I"),
                ("16. 창의적인 활동 즐김?", "S", "N")
            ]

            for i, (q, yes_type, no_type) in enumerate(questions, 1):
                st.subheader(f"문제 {i}: {q}")
                answer = st.radio(f"Q{i}", ["네!", "아니요~"], key=f"q{i}")
                if answer == "네!":
                    st.session_state.scores[yes_type] += 1
                else:
                    st.session_state.scores[no_type] += 1

            if st.button("테스트 완료! 결과 보기"):
                # 결과 계산
                ei = "E" if st.session_state.scores["E"] >= st.session_state.scores["I"] else "I"
                sn = "S" if st.session_state.scores["S"] >= st.session_state.scores["N"] else "N"
                tf = "T" if st.session_state.scores["T"] >= st.session_state.scores["F"] else "F"
                jp = "J" if st.session_state.scores["J"] >= st.session_state.scores["P"] else "P"

                st.session_state.mbti = ei + sn + tf + jp
                st.success(f"당신의 MBTI는... **{st.session_state.mbti}** 입니다! 🎉")
                st.rerun()

# ────────────────────────────────────────────────
#                    결과 화면
# ────────────────────────────────────────────────
if st.session_state.get("mbti"):
    st.markdown("---")
    st.subheader("🎉 결과 나왔어요!")
    st.write(f"**MBTI**: {st.session_state.mbti}")

    if st.button(t["fortune_btn"], type="primary", use_container_width=True):
        st.balloons()
        st.success("2026년 운세 준비 완료! ✨")
        
        # 오늘/내일 운세 (간단 예시)
        st.subheader(t["daily_title"])
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"{t['today']}")
            st.write("에너지 충만한 하루! 🔥")
        with col2:
            st.info(f"{t['tomorrow']}")
            st.write("조금 차분히 준비하는 날 😌")

    if st.button(t["reset"]):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

st.caption("재미로만 봐주세요~ 😊")
