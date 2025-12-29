import streamlit as st
import random

Z = {"쥐띠":"🐭 활발·성장, 돈↑","소띠":"🐮 노력 결실","호랑이띠":"🐯 도전 성공, 돈 대박","토끼띠":"🐰 안정·사랑 운","용띠":"🐲 운↑ 리더십","뱀띠":"🐍 실속·직감","말띠":"🐴 새 도전·돈 기회","양띠":"🐑 편안+결혼 운","원숭이띠":"🐵 변화·재능","닭띠":"🐔 노력 결과","개띠":"🐶 친구·돈↑","돼지띠":"🐷 여유·돈 최고"}

M = {"INTJ":"🧠 냉철 전략가","INTP":"💡 아이디어 천재","ENTJ":"👑 보스","ENTP":"⚡ 토론왕","INFJ":"🔮 마음 마스터","INFP":"🎨 감성 예술가","ENFJ":"🤗 모두 선생님","ENFP":"🎉 인간 비타민","ISTJ":"📋 규칙 지킴이","ISFJ":"🛡️ 세상 따뜻함","ESTJ":"📢 리더","ESFJ":"💕 분위기 메이커","ISTP":"🔧 고치는 장인","ISFP":"🌸 감성 힐러","ESTP":"🏄 모험왕","ESFP":"🎭 파티 주인공"}

def get_zodiac(y): 
    z = ["쥐띠","소띠","호랑이띠","토끼띠","용띠","뱀띠","말띠","양띠","원숭이띠","닭띠","개띠","돼지띠"]
    return z[(y-4)%12] if 1900<=y<=2030 else None

st.set_page_config(page_title="띠MBTI 운세", layout="centered")
st.title("🌟 2026 띠+MBTI 초궁합 🌟")
st.caption("완전 무료 😄")

app_url = "https://my-fortune.streamlit.app"  # 너의 주소!

st.markdown("### 📱 QR 코드 스캔!")
st.image("frame.png", caption="폰으로 찍어보세요")

st.markdown("""
<div style="background:#ffeb3b;padding:15px;border-radius:15px;text-align:center;margin:20px 0;">
  <h3>💳 렌탈 궁금할 때?</h3>
  <p><b>다나눔렌탈</b> 제휴카드 시 <b>월 0원부터</b> + <b>현금 페이백</b>!</p>
  <a href="https://www.다나눔렌탈.com" target="_blank">
    <button style="background:#ff5722;color:white;padding:10px 25px;border:none;border-radius:10px;">🔗 보러가기</button>
  </a>
</div>
""", unsafe_allow_html=True)

year = st.number_input("출생 연도",1900,2030,2005,step=1)

if "mbti" not in st.session_state: 
    st.session_state.mbti = None

if st.session_state.mbti is None:
    c = st.radio("MBTI 어떻게 할까?", ["직접 입력","간단 테스트 (4문제)"], key="mbti_mode")
    if c == "직접 입력":
        m = st.selectbox("너의 MBTI", sorted(M.keys()), key="direct_mbti")
        if st.button("이 MBTI로 운세 보기", key="direct_button"):
            st.session_state.mbti = m
            st.rerun()
    else:
        st.write("4문제만 답해줘!")
        q1 = st.radio("주말에 뭐 하고 싶어?", ("친구들이랑 놀기", "혼자 쉬기"), key="q1")
        q2 = st.radio("새로운 물건 보면?", ("실제로 만져보고 싶음", "상상만 해도 재밌음"), key="q2")
        q3 = st.radio("친구가 울 때?", ("어떻게 도와줄지 생각", "먼저 위로하고 공감"), key="q3")
        q4 = st.radio("방 정리?", ("미리미리 깔끔하게", "필요할 때 대충"), key="q4")
        if st.button("테스트 결과 보기!", key="test_button"):
            ei = "E" if q1 == "친구들이랑 놀기" else "I"
            sn = "S" if q2 == "실제로 만져보고 싶음" else "N"
            tf = "T" if q3 == "어떻게 도와줄지 생각" else "F"
            jp = "J" if q4 == "미리미리 깔끔하게" else "P"
            st.session_state.mbti = ei + sn + tf + jp
            st.rerun()

if st.session_state.mbti:
    mbti = st.session_state.mbti
    zodiac = get_zodiac(year)
    if zodiac:
        if st.button("🔮 2026년 운세 보기!", use_container_width=True, key="fortune_button"):
            score = random.randint(85,100)
            hit = random.choice(["올해 대박 터질 조합 🔥","인생 역전 각 🚀","주변 부러워할 운세 💎","인스타 스토리 터질 준비 📸"])
            st.success(f"{Z[zodiac][0]} **{zodiac}** + {M[mbti][0]} **{mbti}** 조합 완전 미쳤어!!")
            st.metric("운세 점수", f"{score}점", delta="역대급!")
            st.info(f"**띠 운세**: {Z[zodiac].split(' ',1)[1]}")
            st.info(f"**MBTI 특징**: {M[mbti].split(' ',1)[1]}")
            st.write(f"**요약**: {hit}")
            st.balloons()

            st.markdown("### 📲 친구한테 공유하기!")
            col1,col2,col3,col4 = st.columns(4)
            with col1: st.markdown(f'<a href="https://story.kakao.com/s/share?url={app_url}" target="_blank"><img src="https://developers.kakao.com/assets/img/about/logos/kakaostory/kakaostory-ko.png" width="100%"></a><p>카톡</p>', unsafe_allow_html=True)
            with col2: st.markdown(f'<a href="https://www.instagram.com" target="_blank"><img src="https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png" width="100%"></a><p>인스타</p>', unsafe_allow_html=True)
            with col3: st.markdown(f'<a href="https://www.tiktok.com/share?url={app_url}" target="_blank"><img src="https://sf16-scmcdn-va.ibytedtos.com/goofy/tiktok/web/node/_next/static/images/logo-dark-1e0ed760fa3bc5d3a2f5d9f2f3c3d3d9.svg" width="100%"></a><p>틱톡</p>', unsafe_allow_html=True)
            with col4: st.markdown(f'<a href="https://line.me/R/msg/text/?{zodiac}+{mbti} 운세 대박! {app_url}" target="_blank"><img src="https://scdn.line-apps.com/n/line_add_friends/btn/en.png" width="100%"></a><p>라인</p>', unsafe_allow_html=True)

    if st.button("처음부터 다시 하기", key="reset_button"):
        st.session_state.clear()
        st.rerun()

st.caption("재미로만 봐주세요! 친구들이랑 같이 해보세요 😊")
