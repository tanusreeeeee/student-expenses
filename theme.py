"""Soft, rounded design system. Edit the values in T to re-skin the whole app."""
import streamlit as st

T = dict(
    primary="#6B5CE7", tint="#EEEBFD", peach="#F2B8A2", bg="#FAF7F4", surface="#FFFFFF",
    text="#2B2A33", muted="#7A7785", border="#ECE7E1",
    r_sm="12px", r_md="16px", r_lg="28px", r_full="9999px",
    sh1="0 1px 3px rgba(107,92,231,0.06)", sh2="0 6px 20px rgba(107,92,231,0.10)",
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
html, body, .stApp, button, input, textarea, [data-baseweb] {
  font-family: 'DM Sans', ui-rounded, -apple-system, 'Segoe UI', system-ui, sans-serif !important; }
.stApp { background: %(bg)s; color: %(text)s; }
[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 48px; padding-bottom: 64px; max-width: 1100px; }
h1, h2, h3 { font-weight: 700 !important; letter-spacing: -0.02em; color: %(text)s; }
h1 { font-size: 40px !important; } h2 { font-size: 24px !important; } h3 { font-size: 20px !important; }
p, label, li, .stMarkdown { color: %(text)s; }
[data-testid="stCaptionContainer"], small { color: %(muted)s !important; }
hr { border: none; height: 1px; background: %(border)s; margin: 24px 0; }

/* sidebar */
[data-testid="stSidebar"] { background: %(surface)s; border-right: 1px solid %(border)s;
  border-radius: 0 %(r_lg)s %(r_lg)s 0; box-shadow: %(sh1)s; }
[data-testid="stSidebar"] .block-container, [data-testid="stSidebarContent"] { padding-top: 24px; }

/* buttons: soft pills */
.stButton > button, [data-testid^="stBaseButton"] {
  border-radius: %(r_full)s !important; min-height: 48px; padding: 0 24px; font-weight: 500;
  border: 1px solid %(border)s; background: %(surface)s; color: %(text)s;
  box-shadow: %(sh1)s; transition: transform .18s ease, box-shadow .18s ease; }
.stButton > button:hover, [data-testid^="stBaseButton"]:hover {
  transform: scale(1.02); box-shadow: %(sh2)s; border-color: %(primary)s; color: %(primary)s; }
[data-testid="stBaseButton-primary"], .stButton > button[kind="primary"] {
  background: %(primary)s !important; border-color: %(primary)s !important; color: #fff !important; }
[data-testid="stBaseButton-primary"]:hover, .stButton > button[kind="primary"]:hover { color: #fff !important; }

/* inputs */
[data-baseweb="input"], [data-baseweb="textarea"], [data-baseweb="select"] > div {
  border-radius: %(r_md)s !important; background: %(surface)s !important;
  border: 1px solid %(border)s !important; box-shadow: %(sh1)s; }
[data-baseweb="input"] { min-height: 48px; }
[data-baseweb="input"] > div, [data-baseweb="textarea"] > div { background: transparent !important; }
[data-baseweb="input"]:focus-within, [data-baseweb="textarea"]:focus-within,
[data-baseweb="select"]:focus-within > div { border: 2px solid %(primary)s !important; }
[data-testid="stAudioInput"] > div { border-radius: %(r_lg)s !important; background: %(surface)s;
  border: 1px solid %(border)s; box-shadow: %(sh1)s; }

/* tabs as pills */
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] { display: none !important; }
[data-baseweb="tab-list"] { gap: 8px; background: transparent; padding: 4px 0 16px; }
button[role="tab"] { border-radius: %(r_full)s !important; padding: 8px 20px !important;
  background: transparent; color: %(muted)s; font-weight: 500; transition: background .18s ease; }
button[role="tab"]:hover { background: %(tint)s; color: %(primary)s; }
button[role="tab"][aria-selected="true"] { background: %(tint)s; color: %(primary)s; }

/* cards: keyed containers, metrics, expanders */
[class*="st-key-card"], [data-testid="stMetric"], [data-testid="stExpander"] {
  background: %(surface)s; border: 1px solid %(border)s !important; border-radius: %(r_lg)s !important;
  box-shadow: %(sh2)s; padding: 24px; }
[data-testid="stExpander"] { padding: 8px 16px; box-shadow: %(sh1)s; }
[data-testid="stExpander"] details, [data-testid="stExpander"] summary { border: none !important; }
[data-testid="stMetricValue"] { color: %(primary)s; font-weight: 700; }

/* alerts, tables, progress */
[data-testid="stAlert"] { border-radius: %(r_md)s !important; border: none !important; box-shadow: %(sh1)s; }
[data-testid="stDataFrame"], [data-testid="stDataEditor"] { border-radius: %(r_md)s; overflow: hidden;
  border: 1px solid %(border)s; box-shadow: %(sh1)s; }
[data-testid="stProgress"] > div > div { border-radius: %(r_full)s !important; }
[data-testid="stProgress"] > div > div > div { border-radius: %(r_full)s !important; background: %(primary)s; }

/* landing */
.hg-hero { text-align: center; padding: 24px 0 32px; }
.hg-hero h1 { margin-bottom: 8px; } .hg-hero p { color: %(muted)s; font-size: 16px; margin: 0; }
.hg-bubble { width: 56px; height: 56px; border-radius: %(r_full)s; background: %(tint)s;
  display: flex; align-items: center; justify-content: center; font-size: 24px; margin-bottom: 16px; }
</style>
""" % T


def inject():
    st.markdown(CSS, unsafe_allow_html=True)
