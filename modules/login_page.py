# modules/login_page.py
"""
MedChain — Beautiful 3D-styled Login & Registration page.

Drop-in replacement for the original render_login_page() in app.py.
Zero extra dependencies — uses only Streamlit + CSS/HTML injection.

To use in app.py, make exactly 2 changes:
  1. Add import:   from modules.login_page import render_login_page
  2. Remove/replace the old render_login_page() function (lines 236-336)
     The call site `render_login_page()` in main() stays identical.
"""

import streamlit as st
import streamlit.components.v1 as components
from auth.auth import login_user, register_user
from utils.session_manager import set_user
from utils.constants import BLOOD_GROUPS, ROLE_PATIENT


# ─────────────────────────────────────────────────────────────────────
#  CSS  — injects directly into the Streamlit page (not an iframe)
# ─────────────────────────────────────────────────────────────────────

_LOGIN_CSS = """
<style>
/* ── Fonts ─────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&display=swap');

/* ── Hide Streamlit chrome on the login page ────────────────────── */
#MainMenu          { visibility: hidden !important; }
footer             { visibility: hidden !important; }
[data-testid="stHeader"]          { display: none !important; }
[data-testid="stToolbar"]         { display: none !important; }
section[data-testid="stSidebar"]  { display: none !important; }
[data-testid="stDecoration"]      { display: none !important; }

/* ── Full-page dark background ──────────────────────────────────── */
.stApp {
    background: #050a12 !important;
    font-family: 'DM Sans', sans-serif !important;
}

[data-testid="stAppViewContainer"] {
    background: transparent !important;
}

[data-testid="stAppViewBlockContainer"] {
    padding-top: 0 !important;
    max-width: 100% !important;
}

/* ── Animated background layer ──────────────────────────────────── */
#mc-scene {
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    overflow: hidden;
}

/* Radial glow clouds */
#mc-scene::before {
    content: '';
    position: absolute;
    inset: 0;
    background:
        radial-gradient(ellipse 55% 45% at 20% 60%, rgba(0,210,200,0.07) 0%, transparent 60%),
        radial-gradient(ellipse 45% 55% at 80% 30%, rgba(0,130,200,0.05) 0%, transparent 55%),
        radial-gradient(ellipse 60% 40% at 50% 90%, rgba(0,200,180,0.04) 0%, transparent 50%);
    animation: glowShift 12s ease infinite alternate;
}
@keyframes glowShift {
    from { opacity: .7; transform: scale(1); }
    to   { opacity: 1;  transform: scale(1.06); }
}

/* Subtle grid */
#mc-scene::after {
    content: '';
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(0,210,200,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,210,200,0.03) 1px, transparent 1px);
    background-size: 48px 48px;
}

/* Vignette */
#mc-vignette {
    position: fixed;
    inset: 0;
    z-index: 1;
    background: radial-gradient(ellipse 75% 75% at 50% 50%,
        transparent 35%, rgba(5,10,18,0.88) 100%);
    pointer-events: none;
}

/* ── Floating particles (CSS-only, no JS) ───────────────────────── */
.mc-dot {
    position: fixed;
    border-radius: 50%;
    background: rgba(0,210,200,0.55);
    box-shadow: 0 0 6px rgba(0,210,200,0.4);
    pointer-events: none;
    z-index: 1;
    animation: floatDot linear infinite;
}
@keyframes floatDot {
    0%   { transform: translateY(0)   scale(1);   opacity: 0; }
    8%   { opacity: 1; }
    90%  { opacity: .4; }
    100% { transform: translateY(-110vh) scale(.4); opacity: 0; }
}

/* Pulse rings */
.mc-ring {
    position: fixed;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%) scale(0);
    border-radius: 50%;
    border: 1px solid rgba(0,210,200,0.35);
    pointer-events: none;
    z-index: 1;
    animation: ringPulse 7s ease-out infinite;
}
.mc-ring:nth-child(2) { animation-delay: 2.3s; }
.mc-ring:nth-child(3) { animation-delay: 4.6s; }
@keyframes ringPulse {
    0%   { width: 0; height: 0; opacity: .7; transform: translate(-50%,-50%) scale(1); }
    100% { width: 170vmax; height: 170vmax; opacity: 0; transform: translate(-50%,-50%) scale(1); }
}

/* ── Layout wrapper ─────────────────────────────────────────────── */
#mc-wrap {
    position: relative;
    z-index: 10;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 32px 16px 48px;
    gap: 24px;
}

/* ── Brand header ───────────────────────────────────────────────── */
#mc-brand {
    text-align: center;
    animation: fadeDown .8s ease both;
}
@keyframes fadeDown {
    from { opacity: 0; transform: translateY(-16px); }
    to   { opacity: 1; transform: translateY(0); }
}
#mc-brand-name {
    font-family: 'Syne', sans-serif;
    font-size: 2.6rem;
    font-weight: 800;
    letter-spacing: -.02em;
    background: linear-gradient(135deg, #00d2c8 0%, #7ffffd 55%, #f5c842 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
}
#mc-brand-sub {
    font-family: 'DM Mono', monospace;
    font-size: .62rem;
    letter-spacing: .22em;
    color: #5d8a90;
    text-transform: uppercase;
    margin-top: 6px;
    display: block;
}
#mc-brand-icon {
    display: inline-block;
    animation: spinSlow 12s linear infinite;
    font-size: 2rem;
    filter: drop-shadow(0 0 10px #00d2c8);
    margin-bottom: 8px;
}
@keyframes spinSlow { to { transform: rotate(360deg); } }

/* ── Card (the column wrapper) ──────────────────────────────────── */
#mc-card {
    width: 460px;
    max-width: 100%;
    background: rgba(8,18,32,0.88);
    border: 1px solid rgba(0,210,200,0.18);
    border-radius: 18px;
    backdrop-filter: blur(28px) saturate(1.4);
    -webkit-backdrop-filter: blur(28px) saturate(1.4);
    box-shadow:
        0 0 0 1px rgba(0,210,200,0.05),
        0 32px 80px rgba(0,0,0,.75),
        inset 0 1px 0 rgba(255,255,255,0.04);
    overflow: hidden;
    animation: riseCard .9s cubic-bezier(.22,1,.36,1) .12s both;
    padding-bottom: 8px;
}
@keyframes riseCard {
    from { opacity: 0; transform: translateY(36px) rotateX(4deg); }
    to   { opacity: 1; transform: translateY(0)    rotateX(0deg); }
}

/* Top glow line */
#mc-card::before {
    content: '';
    display: block;
    height: 2px;
    background: linear-gradient(90deg, transparent 0%, #00d2c8 50%, transparent 100%);
    opacity: .85;
    animation: scanH 3s ease-in-out infinite alternate;
}
@keyframes scanH {
    from { background-position: -100% 0; opacity: .45; }
    to   { background-position:  200% 0; opacity: 1;   }
}

/* ── Card inner padding ─────────────────────────────────────────── */
#mc-inner {
    padding: 28px 32px 8px;
}

/* ── Card footer ────────────────────────────────────────────────── */
#mc-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 32px;
    border-top: 1px solid rgba(0,210,200,0.1);
    margin-top: 4px;
}
#mc-secure {
    display: flex;
    align-items: center;
    gap: 7px;
    font-family: 'DM Mono', monospace;
    font-size: .58rem;
    letter-spacing: .14em;
    color: #2e5560;
    text-transform: uppercase;
}
.mc-dot-live {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #00d2c8;
    box-shadow: 0 0 6px #00d2c8;
    display: inline-block;
    animation: blink 2s ease infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.25} }
#mc-version {
    font-family: 'DM Mono', monospace;
    font-size: .58rem;
    color: #2e5560;
    letter-spacing: .1em;
}

/* ── Streamlit Tabs override ────────────────────────────────────── */
[data-testid="stTabs"] > div:first-child {
    border-bottom: 1px solid rgba(0,210,200,0.15) !important;
    gap: 0 !important;
}
[data-testid="stTabs"] button[role="tab"] {
    font-family: 'Syne', sans-serif !important;
    font-size: .82rem !important;
    font-weight: 700 !important;
    letter-spacing: .08em !important;
    text-transform: uppercase !important;
    color: #5d8a90 !important;
    border-radius: 0 !important;
    padding: 14px 20px !important;
    transition: color .25s !important;
    border: none !important;
    background: transparent !important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #00d2c8 !important;
    border-bottom: 2px solid #00d2c8 !important;
    box-shadow: 0 0 12px rgba(0,210,200,0.25) !important;
}
[data-testid="stTabContent"] {
    padding-top: 24px !important;
}

/* ── Input fields ───────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stTextInput > label + div > div > input {
    background: rgba(0,210,200,0.04) !important;
    border: 1px solid rgba(0,210,200,0.18) !important;
    border-radius: 10px !important;
    color: #d8eef0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: .9rem !important;
    padding: 10px 14px !important;
    transition: border-color .25s, box-shadow .25s !important;
    caret-color: #00d2c8 !important;
}
.stTextInput > div > div > input:focus {
    border-color: rgba(0,210,200,0.55) !important;
    background: rgba(0,210,200,0.07) !important;
    box-shadow: 0 0 0 3px rgba(0,210,200,0.12), 0 0 20px rgba(0,210,200,0.07) !important;
}
.stTextInput > div > div > input::placeholder { color: #2e5560 !important; }
.stTextInput label {
    font-family: 'DM Mono', monospace !important;
    font-size: .65rem !important;
    letter-spacing: .14em !important;
    text-transform: uppercase !important;
    color: #5d8a90 !important;
}

/* ── Number input ───────────────────────────────────────────────── */
.stNumberInput input {
    background: rgba(0,210,200,0.04) !important;
    border: 1px solid rgba(0,210,200,0.18) !important;
    border-radius: 10px !important;
    color: #d8eef0 !important;
}
.stNumberInput label {
    font-family: 'DM Mono', monospace !important;
    font-size: .65rem !important;
    letter-spacing: .14em !important;
    text-transform: uppercase !important;
    color: #5d8a90 !important;
}

/* ── Selectbox ──────────────────────────────────────────────────── */
.stSelectbox > label {
    font-family: 'DM Mono', monospace !important;
    font-size: .65rem !important;
    letter-spacing: .14em !important;
    text-transform: uppercase !important;
    color: #5d8a90 !important;
}
.stSelectbox > div > div {
    background: rgba(0,210,200,0.04) !important;
    border: 1px solid rgba(0,210,200,0.18) !important;
    border-radius: 10px !important;
    color: #d8eef0 !important;
}

/* ── Primary button ─────────────────────────────────────────────── */
[data-testid="stFormSubmitButton"] > button,
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #00d2c8 0%, #00a89f 100%) !important;
    color: #050a12 !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-size: .92rem !important;
    font-weight: 700 !important;
    letter-spacing: .06em !important;
    padding: 12px !important;
    box-shadow: 0 4px 24px rgba(0,210,200,0.35) !important;
    transition: transform .15s, box-shadow .15s !important;
}
[data-testid="stFormSubmitButton"] > button:hover,
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 32px rgba(0,210,200,0.5) !important;
}

/* ── Alerts / notifications ─────────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: 8px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: .78rem !important;
}
[data-testid="stAlert"][data-baseweb="notification"] {
    background: rgba(0,210,200,0.08) !important;
    border: 1px solid rgba(0,210,200,0.3) !important;
    color: #00d2c8 !important;
}

/* Success / error overrides */
div[data-testid="stAlert"] > div[role="alert"] {
    font-family: 'DM Mono', monospace !important;
}

/* ── Section label (mono dividers inside form) ──────────────────── */
.mc-section {
    font-family: 'DM Mono', monospace;
    font-size: .6rem;
    letter-spacing: .22em;
    text-transform: uppercase;
    color: #2e5560;
    margin: 8px 0 -4px;
}

/* ── Divider ────────────────────────────────────────────────────── */
hr, [data-testid="stDivider"] {
    border-color: rgba(0,210,200,0.12) !important;
}

/* ── Demo credentials table ─────────────────────────────────────── */
.mc-demo {
    background: rgba(0,210,200,0.04);
    border: 1px solid rgba(0,210,200,0.12);
    border-radius: 10px;
    padding: 14px 16px;
    font-family: 'DM Mono', monospace;
    font-size: .7rem;
    color: #5d8a90;
    line-height: 1.9;
}
.mc-demo strong {
    color: #00d2c8;
    letter-spacing: .1em;
    display: block;
    margin-bottom: 4px;
    font-size: .62rem;
    text-transform: uppercase;
}
.mc-demo code {
    background: rgba(0,210,200,0.12);
    border-radius: 4px;
    padding: 1px 5px;
    color: #7ffffd;
}

/* ── Streamlit columns used as card wrapper ─────────────────────── */
[data-testid="stHorizontalBlock"] > div:first-child,
[data-testid="stHorizontalBlock"] > div:last-child {
    background: transparent !important;
}

/* ── Form container background ──────────────────────────────────── */
[data-testid="stForm"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}

/* ── Scrollbar ──────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #050a12; }
::-webkit-scrollbar-thumb { background: rgba(0,210,200,0.3); border-radius: 4px; }
</style>
"""

_LOGIN_HTML_LAYERS = """
<!-- Animated background layers (rendered directly in Streamlit page) -->
<div id="mc-scene"></div>
<div id="mc-vignette"></div>

<!-- Pulse rings -->
<div class="mc-ring"></div>
<div class="mc-ring"></div>
<div class="mc-ring"></div>

<!-- Floating particles (20 dots, staggered via inline style) -->
<div class="mc-dot" style="width:3px;height:3px;left:8%;bottom:-20px;animation-duration:11s;animation-delay:-2s;"></div>
<div class="mc-dot" style="width:2px;height:2px;left:15%;bottom:-20px;animation-duration:14s;animation-delay:-5s;"></div>
<div class="mc-dot" style="width:4px;height:4px;left:24%;bottom:-20px;animation-duration:9s; animation-delay:-1s;"></div>
<div class="mc-dot" style="width:2px;height:2px;left:33%;bottom:-20px;animation-duration:13s;animation-delay:-7s;"></div>
<div class="mc-dot" style="width:3px;height:3px;left:44%;bottom:-20px;animation-duration:10s;animation-delay:-3s;"></div>
<div class="mc-dot" style="width:2px;height:2px;left:52%;bottom:-20px;animation-duration:16s;animation-delay:-9s;"></div>
<div class="mc-dot" style="width:5px;height:5px;left:61%;bottom:-20px;animation-duration:12s;animation-delay:-4s;"></div>
<div class="mc-dot" style="width:2px;height:2px;left:70%;bottom:-20px;animation-duration:8s; animation-delay:-6s;"></div>
<div class="mc-dot" style="width:3px;height:3px;left:79%;bottom:-20px;animation-duration:15s;animation-delay:-2s;"></div>
<div class="mc-dot" style="width:2px;height:2px;left:88%;bottom:-20px;animation-duration:11s;animation-delay:-8s;"></div>
<div class="mc-dot" style="width:4px;height:4px;left:5%; bottom:-20px;animation-duration:13s;animation-delay:-11s;opacity:0.6;"></div>
<div class="mc-dot" style="width:2px;height:2px;left:18%;bottom:-20px;animation-duration:18s;animation-delay:-14s;opacity:0.5;"></div>
<div class="mc-dot" style="width:3px;height:3px;left:37%;bottom:-20px;animation-duration:10s;animation-delay:-0s; opacity:0.7;"></div>
<div class="mc-dot" style="width:2px;height:2px;left:55%;bottom:-20px;animation-duration:14s;animation-delay:-12s;opacity:0.4;"></div>
<div class="mc-dot" style="width:4px;height:4px;left:66%;bottom:-20px;animation-duration:9s; animation-delay:-3s; opacity:0.6;"></div>
<div class="mc-dot" style="width:2px;height:2px;left:75%;bottom:-20px;animation-duration:17s;animation-delay:-6s; opacity:0.5;"></div>
<div class="mc-dot" style="width:3px;height:3px;left:83%;bottom:-20px;animation-duration:11s;animation-delay:-9s; opacity:0.7;"></div>
<div class="mc-dot" style="width:2px;height:2px;left:92%;bottom:-20px;animation-duration:13s;animation-delay:-2s; opacity:0.4;"></div>
<div class="mc-dot" style="width:5px;height:5px;left:47%;bottom:-20px;animation-duration:20s;animation-delay:-16s;opacity:0.3;"></div>
<div class="mc-dot" style="width:2px;height:2px;left:29%;bottom:-20px;animation-duration:12s;animation-delay:-10s;opacity:0.6;"></div>

<!-- Brand header -->
<div id="mc-brand">
    <div id="mc-brand-icon">✛</div>
    <div id="mc-brand-name">MedChain</div>
    <span id="mc-brand-sub">EMR System &nbsp;·&nbsp; Blockchain-secured &nbsp;·&nbsp; v1.0.0</span>
</div>
"""

_CARD_OPEN = """
<div id="mc-card">
<div id="mc-inner">
"""

_CARD_CLOSE = """
</div>
<div id="mc-footer">
    <div id="mc-secure">
        <span class="mc-dot-live"></span>
        TLS 1.3 &nbsp;·&nbsp; AES-256 &nbsp;·&nbsp; SHA-3
    </div>
    <span id="mc-version">EMR v1.0.0 &nbsp;·&nbsp; 2026</span>
</div>
</div>
"""


# ─────────────────────────────────────────────────────────────────────
#  Main render function
# ─────────────────────────────────────────────────────────────────────

def render_login_page():
    """
    Render the 3D-styled login & registration page.
    Replaces the original render_login_page() in app.py.
    All auth logic (login_user, register_user, set_user) is unchanged.
    """

    # 1. Inject CSS (runs in Streamlit page context, not an iframe)
    st.markdown(_LOGIN_CSS, unsafe_allow_html=True)

    # 2. Inject animated background layers + brand header
    st.markdown(_LOGIN_HTML_LAYERS, unsafe_allow_html=True)

    # 3. Center the card using columns
    _, col, _ = st.columns([1, 2.2, 1])

    with col:
        # Open card wrapper
        st.markdown(_CARD_OPEN, unsafe_allow_html=True)

        # ── Tabs ────────────────────────────────────────────────────
        tab_login, tab_register = st.tabs(["  🔐  Sign In  ", "  📝  Register  "])

        # ── LOGIN TAB ────────────────────────────────────────────────
        with tab_login:
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input(
                    "Username",
                    placeholder="Enter your username",
                    key="li_user",
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="••••••••••••",
                    key="li_pass",
                )
                submitted = st.form_submit_button(
                    "Access System →",
                    type="primary",
                    use_container_width=True,
                )

            # Handle submit OUTSIDE the form block
            if submitted:
                if not username or not password:
                    st.error("⚠  Please enter both username and password.")
                else:
                    with st.spinner("Authenticating…"):
                        success, message, user_data = login_user(username, password)
                    if success and user_data:
                        set_user(
                            user_data["user_id"],
                            user_data["username"],
                            user_data["role"],
                            user_data["token"],
                        )
                        st.success(f"✓  Welcome back, {username}! Loading dashboard…")
                        st.rerun()
                    else:
                        st.error(f"⚠  {message}")

            st.divider()

            # Demo credentials block
            st.markdown("""
            <div class="mc-demo">
                <strong>// Demo Credentials</strong>
                Admin &nbsp;&nbsp;→&nbsp; <code>admin</code> &nbsp;/&nbsp; <code>Admin@1234</code><br/>
                Doctor&nbsp;→&nbsp; <code>dr_smith</code> &nbsp;/&nbsp; <code>Doctor@1234</code><br/>
                Patient→&nbsp; <code>patient_john</code> &nbsp;/&nbsp; <code>Patient@1234</code>
            </div>
            """, unsafe_allow_html=True)

        # ── REGISTER TAB ─────────────────────────────────────────────
        with tab_register:

            with st.form("register_form", clear_on_submit=False):

                st.markdown('<div class="mc-section">// Account</div>',
                            unsafe_allow_html=True)

                col_a, col_b = st.columns(2)
                with col_a:
                    reg_username = st.text_input("Username *", key="rg_user",
                                                  placeholder="your_username")
                with col_b:
                    reg_email = st.text_input("Email *", key="rg_email",
                                               placeholder="you@hospital.org")

                col_pw1, col_pw2 = st.columns(2)
                with col_pw1:
                    reg_password = st.text_input("Password *", type="password",
                                                  key="rg_pw1",
                                                  placeholder="Min. 8 chars")
                with col_pw2:
                    reg_confirm = st.text_input("Confirm *", type="password",
                                                 key="rg_pw2",
                                                 placeholder="Repeat password")

                st.markdown('<div class="mc-section">// Role</div>',
                            unsafe_allow_html=True)

                reg_role = st.selectbox(
                    "Account Type *",
                    ["patient", "doctor"],
                    key="rg_role",
                )

                # Patient-only fields
                if reg_role == ROLE_PATIENT:
                    st.markdown('<div class="mc-section">// Patient Profile</div>',
                                unsafe_allow_html=True)
                    col_c, col_d = st.columns(2)
                    with col_c:
                        reg_age = st.number_input("Age", min_value=0,
                                                   max_value=150, value=25,
                                                   key="rg_age")
                        reg_blood = st.selectbox("Blood Group", BLOOD_GROUPS,
                                                  key="rg_blood")
                    with col_d:
                        reg_allergies = st.text_input(
                            "Allergies", placeholder="e.g. Penicillin",
                            key="rg_allergy")
                        reg_emergency = st.text_input(
                            "Emergency Contact",
                            placeholder="+91-XXXXXXXXXX",
                            key="rg_emergency")
                else:
                    reg_age, reg_blood = 0, "O+"
                    reg_allergies, reg_emergency = "", ""

                reg_submitted = st.form_submit_button(
                    "Create Account →",
                    type="primary",
                    use_container_width=True,
                )

            # Handle submit OUTSIDE the form block
            if reg_submitted:
                with st.spinner("Creating account…"):
                    success, message = register_user(
                        username=reg_username,
                        email=reg_email,
                        password=reg_password,
                        confirm_password=reg_confirm,
                        role=reg_role,
                        age=reg_age if reg_role == ROLE_PATIENT else 0,
                        blood_group=reg_blood if reg_role == ROLE_PATIENT else "O+",
                        allergies=reg_allergies,
                        emergency_contact=reg_emergency,
                    )
                if success:
                    st.success(f"✓  {message}")
                    st.info("Switch to the Sign In tab to log in.")
                else:
                    st.error(f"⚠  {message}")

        # Close card wrapper
        st.markdown(_CARD_CLOSE, unsafe_allow_html=True)
