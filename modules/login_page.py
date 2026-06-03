# modules/login_page.py
"""
MedChain — 3D Login Page
Uses the exact working auth pattern from the reference file,
but injects the full 3D visual design (particles, canvas, HUD, cube)
as CSS/HTML layers directly into Streamlit — no iframe, no query params.
Forms are native Streamlit — they WORK.
"""

import streamlit as st
from auth.auth import login_user, register_user
from utils.session_manager import set_user
from utils.constants import BLOOD_GROUPS, ROLE_PATIENT

# ─────────────────────────────────────────────────────────────
#  1. FULL 3D CSS  (exact design from login_page.html)
# ─────────────────────────────────────────────────────────────
_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Rajdhani:wght@300;400;500;600;700&family=Share+Tech+Mono&display=swap');

/* ── Hide Streamlit chrome ── */
#MainMenu,footer,header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
.stDeployButton{ visibility:hidden!important;display:none!important; }
section[data-testid="stSidebar"]{ display:none!important; }
.stApp{ background:#020810!important; }
[data-testid="stAppViewBlockContainer"]{
    padding-top:0!important;padding-bottom:0!important;
    max-width:100%!important;
}
[data-testid="stForm"]{
    background:transparent!important;
    border:none!important;
    padding:0!important;
}

/* ── Variables ── */
:root{
  --cyan:#00f5ff;--cyan2:#00bcd4;--green:#00ff88;
  --dark:#020810;--card:#070e1a;
  --border:rgba(0,245,255,0.15);--border2:rgba(0,245,255,0.35);
  --text:#b0c4d8;--white:#e8f4f8;
}

/* ── Background canvas placeholder ── */
#mc-bg-wrap{
    position:fixed;inset:0;z-index:0;pointer-events:none;
    background:#020810;
    background-image:
      repeating-linear-gradient(60deg,transparent,transparent 30px,rgba(0,245,255,0.025) 30px,rgba(0,245,255,0.025) 31px),
      repeating-linear-gradient(120deg,transparent,transparent 30px,rgba(0,245,255,0.025) 30px,rgba(0,245,255,0.025) 31px);
}
#mc-bg-wrap::before{
    content:'';position:absolute;inset:0;
    background:
      radial-gradient(ellipse 60% 50% at 20% 60%,rgba(0,245,255,0.06) 0%,transparent 60%),
      radial-gradient(ellipse 50% 60% at 80% 30%,rgba(0,180,216,0.04) 0%,transparent 55%);
    animation:glowShift 10s ease infinite alternate;
}
@keyframes glowShift{from{opacity:.6}to{opacity:1}}

/* Scanlines */
#mc-bg-wrap::after{
    content:'';position:absolute;inset:0;
    background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,0.03) 2px,rgba(0,0,0,0.03) 4px);
}

/* ── Floating particles ── */
.mc-p{
    position:fixed;border-radius:50%;pointer-events:none;z-index:1;opacity:0;
    animation:floatP linear infinite;
}
@keyframes floatP{
    0%{opacity:0;transform:translateY(100vh) translateX(0)}
    8%{opacity:.7}90%{opacity:.3}
    100%{opacity:0;transform:translateY(-10vh) translateX(var(--dx,0px))}
}

/* ── Pulse rings ── */
.mc-ring{
    position:fixed;top:50%;left:50%;
    transform:translate(-50%,-50%) scale(0);
    border-radius:50%;border:1px solid rgba(0,245,255,0.25);
    pointer-events:none;z-index:1;
    animation:ringPulse 8s ease-out infinite;
}
.mc-ring:nth-child(2){animation-delay:2.7s}
.mc-ring:nth-child(3){animation-delay:5.4s}
@keyframes ringPulse{
    0%{width:0;height:0;opacity:.8}
    100%{width:180vmax;height:180vmax;opacity:0}
}

/* ── HUD corners ── */
.mc-hud{
    position:fixed;z-index:5;
    font-family:'Share Tech Mono',monospace;font-size:9px;
    color:rgba(0,245,255,0.3);letter-spacing:1px;pointer-events:none;
    line-height:1.6;
}
.mc-hud-tl{top:18px;left:18px}
.mc-hud-tr{top:18px;right:18px;text-align:right}
.mc-hud-bl{bottom:18px;left:18px}
.mc-hud-br{bottom:18px;right:18px;text-align:right}
.mc-blink{animation:blinkAnim 2s step-end infinite}
@keyframes blinkAnim{0%,100%{opacity:1}50%{opacity:0}}

/* ── 3D Spinning cube ── */
.mc-cube-wrap{
    position:fixed;right:5%;top:50%;transform:translateY(-50%);
    perspective:600px;z-index:3;pointer-events:none;
    animation:cubeDrift 8s ease-in-out infinite;
}
@keyframes cubeDrift{0%,100%{transform:translateY(-50%)}50%{transform:translateY(calc(-50% - 18px))}}
.mc-cube{
    width:110px;height:110px;transform-style:preserve-3d;
    animation:spinCube 12s linear infinite;
}
@keyframes spinCube{from{transform:rotateX(20deg) rotateY(0)}to{transform:rotateX(20deg) rotateY(360deg)}}
.mc-face{
    position:absolute;width:110px;height:110px;
    border:1px solid rgba(0,245,255,0.25);background:rgba(0,245,255,0.02);
    display:flex;align-items:center;justify-content:center;
    font-family:'Share Tech Mono',monospace;font-size:8px;
    color:rgba(0,245,255,0.35);letter-spacing:1px;
}
.mc-face-inner{width:78%;height:78%;border:1px solid rgba(0,245,255,0.15);display:flex;align-items:center;justify-content:center}
.mc-face.f{transform:translateZ(55px)}
.mc-face.b{transform:rotateY(180deg) translateZ(55px)}
.mc-face.l{transform:rotateY(-90deg) translateZ(55px)}
.mc-face.r{transform:rotateY(90deg) translateZ(55px)}
.mc-face.t{transform:rotateX(90deg) translateZ(55px)}
.mc-face.bt{transform:rotateX(-90deg) translateZ(55px)}

/* ── Circuit SVG ── */
.mc-circuit{
    position:fixed;left:0;top:0;width:220px;height:100%;
    z-index:2;pointer-events:none;opacity:0.35;
}

/* ── Brand header ── */
#mc-brand{text-align:center;padding:28px 0 18px;animation:fadeDown .8s ease both}
@keyframes fadeDown{from{opacity:0;transform:translateY(-14px)}to{opacity:1;transform:translateY(0)}}
#mc-brand-icon{
    font-size:2.2rem;display:inline-block;
    animation:spinSlow 12s linear infinite;
    filter:drop-shadow(0 0 12px var(--cyan));margin-bottom:8px;
}
@keyframes spinSlow{to{transform:rotate(360deg)}}
#mc-brand-title{
    font-family:'Orbitron',sans-serif;font-size:2.4rem;font-weight:900;
    letter-spacing:4px;line-height:1;
    background:linear-gradient(135deg,var(--cyan) 0%,var(--green) 60%,var(--cyan) 100%);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
    filter:drop-shadow(0 0 18px rgba(0,245,255,0.4));margin-bottom:4px;
}
#mc-brand-sub{
    font-family:'Share Tech Mono',monospace;font-size:10px;letter-spacing:5px;
    color:var(--cyan2);text-transform:uppercase;display:block;
}

/* ── The auth card ── */
#mc-card{
    position:relative;z-index:10;
    background:rgba(7,14,26,0.92);
    border:1px solid var(--border);
    border-radius:18px;
    backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);
    box-shadow:0 0 0 1px rgba(0,245,255,0.04),0 32px 80px rgba(0,0,0,.7),0 0 80px rgba(0,245,255,0.04);
    overflow:hidden;
    animation:riseCard .9s cubic-bezier(.22,1,.36,1) .1s both;
    margin:0 auto;max-width:460px;
}
@keyframes riseCard{
    from{opacity:0;transform:translateY(32px) scale(.97)}
    to{opacity:1;transform:translateY(0) scale(1)}
}
#mc-card::before{
    content:'';position:absolute;top:-1px;left:-1px;
    width:60px;height:60px;
    border-top:2px solid var(--cyan);border-left:2px solid var(--cyan);
    border-radius:18px 0 0 0;z-index:1;pointer-events:none;
}
#mc-card::after{
    content:'';position:absolute;bottom:-1px;right:-1px;
    width:60px;height:60px;
    border-bottom:2px solid var(--cyan);border-right:2px solid var(--cyan);
    border-radius:0 0 18px 0;z-index:1;pointer-events:none;
}
#mc-glow{
    position:absolute;top:-80px;left:50%;transform:translateX(-50%);
    width:260px;height:260px;pointer-events:none;
    background:radial-gradient(circle,rgba(0,245,255,0.07) 0%,transparent 70%);
    animation:glowPulse 4s ease-in-out infinite;
}
@keyframes glowPulse{0%,100%{opacity:.5;transform:translateX(-50%) scale(1)}50%{opacity:1;transform:translateX(-50%) scale(1.2)}}

#mc-inner{padding:28px 32px 24px}

/* ── Card footer ── */
#mc-foot{
    display:flex;align-items:center;justify-content:space-between;
    padding:10px 32px;border-top:1px solid rgba(0,245,255,0.1);
    font-family:'Share Tech Mono',monospace;font-size:9px;
    color:rgba(0,245,255,0.25);letter-spacing:1px;
}
.mc-live{width:5px;height:5px;border-radius:50%;background:var(--cyan);
    box-shadow:0 0 5px var(--cyan);display:inline-block;
    animation:blinkAnim 2s ease infinite;margin-right:6px}

/* ── Tabs override ── */
[data-testid="stTabs"]>div:first-child{
    border-bottom:1px solid rgba(0,245,255,0.15)!important;
    gap:0!important;margin-bottom:20px!important;
}
[data-testid="stTabs"] button[role="tab"]{
    font-family:'Rajdhani',sans-serif!important;font-size:.85rem!important;
    font-weight:700!important;letter-spacing:2px!important;text-transform:uppercase!important;
    color:rgba(176,196,216,0.45)!important;border-radius:0!important;
    padding:12px 20px!important;border:none!important;background:transparent!important;
    transition:color .2s!important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"]{
    color:var(--cyan)!important;
    border-bottom:2px solid var(--cyan)!important;
    box-shadow:0 0 14px rgba(0,245,255,0.2)!important;
}
[data-testid="stTabContent"]{padding-top:4px!important}

/* ── Inputs ── */
.stTextInput>div>div>input,.stTextInput>label+div>div>input{
    background:rgba(0,245,255,0.04)!important;
    border:1px solid rgba(0,245,255,0.18)!important;
    border-radius:10px!important;color:var(--white)!important;
    font-family:'Rajdhani',sans-serif!important;font-size:.95rem!important;
    padding:11px 14px!important;caret-color:var(--cyan)!important;
    transition:border-color .25s,box-shadow .25s!important;
}
.stTextInput>div>div>input:focus{
    border-color:rgba(0,245,255,0.55)!important;
    background:rgba(0,245,255,0.07)!important;
    box-shadow:0 0 0 3px rgba(0,245,255,0.1),0 0 20px rgba(0,245,255,0.07)!important;
}
.stTextInput>div>div>input::placeholder{color:rgba(176,196,216,0.2)!important}
.stTextInput label,.stNumberInput label,.stSelectbox>label{
    font-family:'Share Tech Mono',monospace!important;font-size:.62rem!important;
    letter-spacing:.18em!important;text-transform:uppercase!important;color:#5d8a90!important;
}
.stNumberInput input{
    background:rgba(0,245,255,0.04)!important;
    border:1px solid rgba(0,245,255,0.18)!important;
    border-radius:10px!important;color:var(--white)!important;
}
.stSelectbox>div>div{
    background:rgba(0,245,255,0.04)!important;
    border:1px solid rgba(0,245,255,0.18)!important;
    border-radius:10px!important;color:var(--white)!important;
}

/* ── Submit button ── */
[data-testid="stFormSubmitButton"]>button{
    background:linear-gradient(135deg,var(--cyan) 0%,#00a89f 100%)!important;
    color:var(--dark)!important;border:none!important;border-radius:10px!important;
    font-family:'Orbitron',sans-serif!important;font-size:.8rem!important;
    font-weight:700!important;letter-spacing:3px!important;text-transform:uppercase!important;
    padding:13px!important;width:100%!important;
    box-shadow:0 4px 24px rgba(0,245,255,0.3)!important;
    transition:transform .15s,box-shadow .15s!important;
}
[data-testid="stFormSubmitButton"]>button:hover{
    transform:translateY(-2px)!important;
    box-shadow:0 8px 32px rgba(0,245,255,0.5)!important;
}

/* ── Alerts ── */
[data-testid="stAlert"]{border-radius:8px!important;font-family:'Share Tech Mono',monospace!important;font-size:.72rem!important;}

/* ── Demo creds box ── */
.mc-demo{
    background:rgba(0,245,255,0.03);border:1px solid rgba(0,245,255,0.1);
    border-radius:10px;padding:14px 16px;
    font-family:'Share Tech Mono',monospace;font-size:.68rem;
    color:#5d8a90;line-height:2;margin-top:4px;
}
.mc-demo strong{color:var(--cyan);letter-spacing:.12em;display:block;margin-bottom:2px;text-transform:uppercase}
.mc-demo code{background:rgba(0,245,255,0.12);border-radius:4px;padding:1px 6px;color:#7ffffd}

/* ── Section mono label ── */
.mc-sec{font-family:'Share Tech Mono',monospace;font-size:.58rem;
    letter-spacing:.2em;text-transform:uppercase;color:#2e5560;margin:10px 0 -2px}

/* ── Divider ── */
hr,[data-testid="stDivider"]{border-color:rgba(0,245,255,0.12)!important}

/* ── Scrollbar ── */
::-webkit-scrollbar{width:4px}
::-webkit-scrollbar-track{background:#020810}
::-webkit-scrollbar-thumb{background:rgba(0,245,255,0.25);border-radius:4px}
</style>
"""

# ─────────────────────────────────────────────────────────────
#  2. BACKGROUND LAYERS HTML  (fixed, z-index 0–3)
# ─────────────────────────────────────────────────────────────
_BG = """
<div id="mc-bg-wrap"></div>

<!-- Pulse rings -->
<div class="mc-ring"></div>
<div class="mc-ring"></div>
<div class="mc-ring"></div>

<!-- Particles -->
<div class="mc-p" style="width:3px;height:3px;left:8%;bottom:-10px;animation-duration:11s;animation-delay:-2s;background:#00f5ff;box-shadow:0 0 6px #00f5ff;--dx:30px"></div>
<div class="mc-p" style="width:2px;height:2px;left:15%;bottom:-10px;animation-duration:14s;animation-delay:-5s;background:#00ff88;box-shadow:0 0 5px #00ff88;--dx:-20px"></div>
<div class="mc-p" style="width:4px;height:4px;left:24%;bottom:-10px;animation-duration:9s;animation-delay:-1s;background:#00f5ff;box-shadow:0 0 8px #00f5ff;--dx:50px"></div>
<div class="mc-p" style="width:2px;height:2px;left:33%;bottom:-10px;animation-duration:13s;animation-delay:-7s;background:#00ff88;box-shadow:0 0 5px #00ff88;--dx:-40px"></div>
<div class="mc-p" style="width:3px;height:3px;left:44%;bottom:-10px;animation-duration:10s;animation-delay:-3s;background:#00f5ff;box-shadow:0 0 6px #00f5ff;--dx:20px"></div>
<div class="mc-p" style="width:2px;height:2px;left:52%;bottom:-10px;animation-duration:16s;animation-delay:-9s;background:#00ff88;box-shadow:0 0 5px #00ff88;--dx:-60px"></div>
<div class="mc-p" style="width:5px;height:5px;left:61%;bottom:-10px;animation-duration:12s;animation-delay:-4s;background:#00f5ff;box-shadow:0 0 10px #00f5ff;--dx:40px"></div>
<div class="mc-p" style="width:2px;height:2px;left:70%;bottom:-10px;animation-duration:8s;animation-delay:-6s;background:#00ff88;box-shadow:0 0 5px #00ff88;--dx:-30px"></div>
<div class="mc-p" style="width:3px;height:3px;left:79%;bottom:-10px;animation-duration:15s;animation-delay:-2s;background:#00f5ff;box-shadow:0 0 6px #00f5ff;--dx:25px"></div>
<div class="mc-p" style="width:2px;height:2px;left:88%;bottom:-10px;animation-duration:11s;animation-delay:-8s;background:#00ff88;box-shadow:0 0 5px #00ff88;--dx:-45px"></div>
<div class="mc-p" style="width:4px;height:4px;left:5%;bottom:-10px;animation-duration:13s;animation-delay:-11s;background:#00f5ff;box-shadow:0 0 8px #00f5ff;opacity:.6;--dx:60px"></div>
<div class="mc-p" style="width:2px;height:2px;left:37%;bottom:-10px;animation-duration:10s;animation-delay:0s;background:#00ff88;box-shadow:0 0 5px #00ff88;opacity:.7;--dx:-20px"></div>
<div class="mc-p" style="width:3px;height:3px;left:66%;bottom:-10px;animation-duration:9s;animation-delay:-3s;background:#00f5ff;box-shadow:0 0 6px #00f5ff;opacity:.6;--dx:35px"></div>
<div class="mc-p" style="width:2px;height:2px;left:83%;bottom:-10px;animation-duration:17s;animation-delay:-9s;background:#00ff88;box-shadow:0 0 5px #00ff88;opacity:.5;--dx:-55px"></div>
<div class="mc-p" style="width:5px;height:5px;left:47%;bottom:-10px;animation-duration:20s;animation-delay:-16s;background:#00f5ff;box-shadow:0 0 10px #00f5ff;opacity:.3;--dx:10px"></div>

<!-- HUD Corners -->
<div class="mc-hud mc-hud-tl">
SYS://MEDCHAIN-EMR<br>VER: 1.0.0-SECURE<br><span class="mc-blink">● ONLINE</span>
</div>
<div class="mc-hud mc-hud-tr">
BLOCKCHAIN: ACTIVE<br>NODES: 1/1<br>ENCRYPT: AES-256-GCM
</div>
<div class="mc-hud mc-hud-bl">HIPAA COMPLIANT<br>ISO 27001 READY</div>
<div class="mc-hud mc-hud-br" id="mc-clock">UTC: --:--:--<br>SESSION: NULL</div>

<!-- 3D Cube -->
<div class="mc-cube-wrap">
  <div class="mc-cube">
    <div class="mc-face f"><div class="mc-face-inner">SECURE</div></div>
    <div class="mc-face b"><div class="mc-face-inner">CHAIN</div></div>
    <div class="mc-face l"><div class="mc-face-inner">HEALTH</div></div>
    <div class="mc-face r"><div class="mc-face-inner">DATA</div></div>
    <div class="mc-face t"><div class="mc-face-inner">SHA-256</div></div>
    <div class="mc-face bt"><div class="mc-face-inner">AES-GCM</div></div>
  </div>
</div>

<!-- Circuit SVG -->
<svg class="mc-circuit" viewBox="0 0 250 800" xmlns="http://www.w3.org/2000/svg">
  <g stroke="#00f5ff" fill="none" stroke-width="0.8" opacity="0.5">
    <path d="M20 0 L20 100 L80 160 L80 250 L140 310 L140 400"/>
    <path d="M60 0 L60 80 L120 140 L120 300 L180 360 L180 500 L240 560"/>
    <circle cx="80" cy="160" r="4" fill="rgba(0,245,255,0.3)"/>
    <circle cx="140" cy="310" r="3" fill="rgba(0,245,255,0.3)"/>
    <circle cx="120" cy="300" r="4" fill="rgba(0,245,255,0.3)"/>
    <circle cx="180" cy="500" r="3" fill="rgba(0,245,255,0.2)"/>
    <path d="M20 500 L20 600 L100 680 L100 800"/>
    <path d="M80 400 L80 480 L160 560 L160 700 L220 760"/>
    <circle cx="80" cy="480" r="4" fill="rgba(0,245,255,0.3)"/>
    <circle cx="160" cy="560" r="3" fill="rgba(0,245,255,0.2)"/>
    <path d="M140 0 L140 60 L200 120"/>
    <path d="M0 300 L40 300 L40 350"/>
    <path d="M0 500 L60 500"/>
    <circle cx="40" cy="300" r="3" fill="rgba(0,245,255,0.4)"/>
  </g>
</svg>

<!-- Live clock script -->
<script>
(function(){
  function tick(){
    var el=document.getElementById('mc-clock');
    if(el){
      var t=new Date().toUTCString().split(' ')[4];
      el.innerHTML='UTC: '+t+'<br>SESSION: '+Math.random().toString(36).substr(2,8).toUpperCase();
    }
  }
  tick(); setInterval(tick,1000);
})();
</script>
"""

# Card open/close wrappers
_CARD_OPEN = """
<div id="mc-brand">
  <div id="mc-brand-icon">⚕</div>
  <div id="mc-brand-title">MedChain</div>
  <span id="mc-brand-sub">Electronic Medical Records &nbsp;·&nbsp; Blockchain Secured</span>
</div>
<div id="mc-card">
<div id="mc-glow"></div>
<div id="mc-inner">
"""

_CARD_CLOSE = """
</div>
<div id="mc-foot">
  <span><span class="mc-live"></span>TLS 1.3 &nbsp;·&nbsp; AES-256-GCM &nbsp;·&nbsp; SHA-256</span>
  <span>EMR v1.0.0 &nbsp;·&nbsp; 2026</span>
</div>
</div>
"""


# ─────────────────────────────────────────────────────────────
#  3. MAIN RENDER FUNCTION
# ─────────────────────────────────────────────────────────────

def render_login_page():
    # Inject CSS
    st.markdown(_CSS, unsafe_allow_html=True)
    # Inject background layers (fixed position, behind everything)
    st.markdown(_BG, unsafe_allow_html=True)

    # Center card with columns
    _, col, _ = st.columns([1, 2.2, 1])

    with col:
        st.markdown(_CARD_OPEN, unsafe_allow_html=True)

        # ── TABS ──────────────────────────────────────────────
        tab_login, tab_register = st.tabs(["  🔐  Sign In  ", "  📝  Register  "])

        # ══════════════════════════════════════════════════════
        #  LOGIN TAB
        # ══════════════════════════════════════════════════════
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

            # ← auth logic OUTSIDE the form (same pattern as working file)
            if submitted:
                if not username or not password:
                    st.error("⚠  Please enter both username and password.")
                else:
                    with st.spinner("Authenticating…"):
                        success, message, user_data = login_user(username.strip(), password)
                    if success and user_data:
                        set_user(
                            user_data["user_id"],
                            user_data["username"],
                            user_data["role"],
                            user_data["token"],
                        )
                        st.success(f"✓  Welcome, {username}! Loading dashboard…")
                        st.rerun()
                    else:
                        st.error(f"⚠  {message}")

            st.divider()

            st.markdown("""
            <div class="mc-demo">
              <strong>// Demo Credentials</strong>
              Admin &nbsp;&rarr;&nbsp; <code>admin</code> &nbsp;/&nbsp; <code>Admin@1234</code><br>
              Doctor&nbsp;&rarr;&nbsp; <code>dr_smith</code> &nbsp;/&nbsp; <code>Doctor@1234</code><br>
              Patient&rarr;&nbsp; <code>patient_john</code> &nbsp;/&nbsp; <code>Patient@1234</code>
            </div>
            """, unsafe_allow_html=True)

        # ══════════════════════════════════════════════════════
        #  REGISTER TAB
        # ══════════════════════════════════════════════════════
        with tab_register:
            with st.form("register_form", clear_on_submit=False):

                st.markdown('<div class="mc-sec">// Account Details</div>',
                            unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    reg_username = st.text_input("Username *", key="rg_user",
                                                  placeholder="your_username")
                with c2:
                    reg_email = st.text_input("Email *", key="rg_email",
                                               placeholder="you@hospital.org")

                c3, c4 = st.columns(2)
                with c3:
                    reg_password = st.text_input("Password *", type="password",
                                                  key="rg_pw1",
                                                  placeholder="Min 8 chars")
                with c4:
                    reg_confirm = st.text_input("Confirm *", type="password",
                                                 key="rg_pw2",
                                                 placeholder="Repeat password")

                st.markdown('<div class="mc-sec">// Role</div>',
                            unsafe_allow_html=True)
                reg_role = st.selectbox(
                    "Account Type *",
                    ["patient", "doctor"],
                    key="rg_role",
                    format_func=lambda x: "👤  Patient" if x == "patient" else "🩺  Doctor",
                )

                if reg_role == ROLE_PATIENT:
                    st.markdown('<div class="mc-sec">// Patient Profile</div>',
                                unsafe_allow_html=True)
                    p1, p2 = st.columns(2)
                    with p1:
                        reg_age   = st.number_input("Age", 0, 150, 25, key="rg_age")
                        reg_blood = st.selectbox("Blood Group", BLOOD_GROUPS, key="rg_blood")
                    with p2:
                        reg_allergies = st.text_input("Allergies",
                                                       placeholder="e.g. Penicillin",
                                                       key="rg_allergy")
                        reg_emergency = st.text_input("Emergency Contact",
                                                       placeholder="+91-XXXXXXXXXX",
                                                       key="rg_emrg")
                else:
                    reg_age, reg_blood, reg_allergies, reg_emergency = 0, "O+", "", ""

                reg_submitted = st.form_submit_button(
                    "Create Account →",
                    type="primary",
                    use_container_width=True,
                )

            # ← auth logic OUTSIDE the form
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

        st.markdown(_CARD_CLOSE, unsafe_allow_html=True)
