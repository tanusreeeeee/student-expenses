"""Hisaab Guru: one site, two modes (Shopkeeper = Khata Guru, Student = SpendWise). No login."""
import streamlit as st
import theme

APP_NAME = "Hisaab Guru"
st.set_page_config(page_title=APP_NAME, page_icon="🪙", layout="wide")
theme.inject()
mode = st.session_state.setdefault("mode", None)

if mode:
    with st.sidebar:
        if st.button("⬅ Switch mode"):
            st.session_state["mode"] = None
            st.rerun()
        st.divider()

try:
    if mode == "shop":
        import shop_mode
        shop_mode.render()
    elif mode == "student":
        import student_mode
        student_mode.render()
    else:
        st.markdown(f'<div class="hg-hero"><h1>{APP_NAME}</h1><p>Har paisa ka hisaab. Pick who you are.</p></div>', unsafe_allow_html=True)
        left, right = st.columns(2, gap="large")
        with left.container(key="card_shop"):
            st.markdown('<div class="hg-bubble">🏪</div>', unsafe_allow_html=True)
            st.markdown("### I run a shop")
            st.write("**Khata Guru**: speak your udhaar in Hindi or English, confirm it, and see who to chase. Runs offline on this laptop.")
            if st.button("Open shopkeeper mode", type="primary", key="go_shop"):
                st.session_state["mode"] = "shop"
                st.rerun()
        with right.container(key="card_student"):
            st.markdown('<div class="hg-bubble">🎓</div>', unsafe_allow_html=True)
            st.markdown("### I am a student")
            st.write("**SpendWise**: track expenses, set a monthly budget, see needs vs wants, and save for goals.")
            if st.button("Open student mode", type="primary", key="go_student"):
                st.session_state["mode"] = "student"
                st.rerun()
except Exception as e:  # never show a raw crash screen
    st.error(f"Something went wrong: {e}")
    st.info("Press 'Switch mode' in the sidebar, or refresh the page.")
