import streamlit as st
import random
import qrcode
from io import BytesIO
import base64

@st.cache_data
def qr_code(url): 
    img = qrcode.make(url)
    buf = BytesIO()
    img.save(buf, "PNG")
    return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"

@st.cache_data
def get_zodiac(y): 
    z = ["쥐띠","소띠","호랑이띠","토끼띠","용띠","뱀띠","말띠","양띠","원숭이띠","닭띠","개띠","돼지띠"]
    return z[(y-4)%12] if 1900<=y<=2030 else None

Z = {"쥐띠":"🐭 활발·성장, 돈↑","소띠":"🐮 노력 결실","호랑이띠":"🐯 도전 성공, 돈 대박","토끼띠":"🐰 안정·사랑 운","용띠":"🐲 운↑ 리더십","뱀띠":"🐍 실속·직감","말띠":"🐴 새 도전·돈 기회","양띠":"🐑 편안+결혼 운","원숭이띠":"🐵 변화·재능","닭띠":"🐔 노력 결과","개띠":"🐶 친구·돈↑","돼지띠":"🐷 여유·돈 최고"}

M = {"INTJ":"🧠 냉철 전략가","INTP":"💡 아이디어 천재","ENTJ":"👑 보스","ENTP":"⚡ 토론왕","INFJ":"🔮 마음 마스터","INFP":"🎨 감성 예술가","ENFJ":"🤗 모두 선생님","ENFP":"🎉 인간 비타민","ISTJ":"📋 규칙 지킴이","ISFJ":"🛡️ 세상 따뜻함","ESTJ":"📢 리더","ESFJ":"💕 분위기 메이커","ISTP":"🔧 고치는 장인","ISFP":"🌸 감성 힐러","ESTP":"🏄 모험왕","ESFP":"🎭 파티 주인공"}

st.set_page_config(page_title="띠MBTI 운세", layout="centered")
st.title("🌟 2026 띠+MBTI 초궁합 🌟")
st.caption("완전 무료 😄")

app_url = "https://your-app.streamlit.app"  # 배포 후 실제 주소로 변경!
st.markdown("### 📱 QR 코드 스캔!")
st.image(qr_code(app_url), caption="폰으로 찍어보세요")

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

if "mbti" not in st.session_state: st.session_state.mbti = None

if st.session_state.mbti is None:
    c = st.radio("MBTI 선택", ["직접 입력","간단 테스트(4문제)"])
    if c == "직접 입력":
        m = st.selectbox("MBTI",sorted(M))
        if st.button("운세 보기"): st.session_state.mbti = m; st.rerun()
    else:
        q1=st.radio("주말?","친구랑 놀기","혼자 쉬기")
        q2=st.radio("새 물건?","만져보고","상상만")
        q3=st.radio("친구 울 때?","도와줄 방법","먼저 위로")
        q4=st.radio("방 정리?","미리 깔끔","필요할 때")
        if st.button("결과 보기"):
            st.session_state.mbti = ("E"if"친구" in q1 else"I")+("S"if"만져" in q2 else"N")+("T"if"도와줄" in q3 else"F")+("J"if"미리" in q4 else"P")
            st.rerun()

if st.session_state.mbti:
    mbti = st.session_state.mbti
    zodiac = get_zodiac(year)
    if zodiac and st.button("🔮 운세 보기!",use_container_width=True):
        score = random.randint(85,100)
        hit = random.choice(["대박 🔥","좋은 해!","부러움 살 운 💎","인스타 올려 📸"])
        st.success(f"{Z[zodiac][0]} **{zodiac}** + {M[mbti][0]} **{mbti}** 최고!")
        st.metric("운세 점수",f"{score}점","역대급!")
        st.info(f"띠 운세: {Z[zodiac].split(' ',1)[1]}")
        st.info(f"MBTI 특징: {M[mbti].split(' ',1)[1]}")
        st.write(f"**한 마디**: {hit}")
        st.balloons()

        st.markdown("### 📲 공유하기")
        c1,c2,c3,c4 = st.columns(4)
        with c1: st.markdown(f'<a href="https://story.kakao.com/s/share?url={app_url}" target="_blank"><img src="https://developers.kakao.com/assets/img/about/logos/kakaostory/kakaostory-ko.png" width="100%"></a><p>카톡</p>',unsafe_allow_html=True)
        with c2: st.markdown(f'<a href="https://www.instagram.com" target="_blank"><img src="https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png" width="100%"></a><p>인스타</p>',unsafe_allow_html=True)
        with c3: st.markdown(f'<a href="https://www.tiktok.com/share?url={app_url}" target="_blank"><img src="https://sf16-scmcdn-va.ibytedtos.com/goofy/tiktok/web/node/_next/static/images/logo-dark-1e0ed760fa3bc5d3a2f5d9f2f3c3d3d9.svg" width="100%"></a><p>틱톡</p>',unsafe_allow_html=True)
        with c4: st.markdown(f'<a href="https://line.me/R/msg/text/?{zodiac}+{mbti} 운세! {app_url}" target="_blank"><img src="https://scdn.line-apps.com/n/line_add_friends/btn/en.png" width="100%"></a><p>라인</p>',unsafe_allow_html=True)

    if st.button("처음부터 다시"): st.session_state.clear(); st.rerun()

st.caption("재미로만 봐주세요 😊")
