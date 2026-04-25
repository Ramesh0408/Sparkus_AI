import streamlit as st
import requests
import uuid
import os
import base64
from datetime import datetime
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder

load_dotenv()

API          = os.getenv("BACKEND_API", "http://localhost:8000")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

st.set_page_config(
    page_title="Sparkus AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap');

:root {
    --bg:        #0a0a0f;
    --bg2:       #0f0f1a;
    --bg3:       #141428;
    --bg4:       #1a1a35;
    --cyan:      #00e5ff;
    --violet:    #7c3aed;
    --pink:      #ec4899;
    --gold:      #f59e0b;
    --red:       #ef4444;
    --txt:       #e2e8f0;
    --txt2:      #94a3b8;
    --txt3:      #475569;
    --border:    rgba(255,255,255,0.07);
    --glow-c:    rgba(0,229,255,0.15);
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background: var(--bg);
    color: var(--txt);
}
* { box-sizing: border-box; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #07070f 0%, #0c0c1e 100%) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] .stButton > button {
    width: 100%; text-align: left;
    background: transparent; border: 1px solid transparent;
    color: var(--txt2); padding: 0.42rem 0.6rem;
    border-radius: 8px; font-size: 0.79rem;
    font-family: 'Inter', sans-serif;
    transition: all 0.18s ease; cursor: pointer;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(124,58,237,0.1);
    border-color: rgba(124,58,237,0.3);
    color: var(--txt);
}
.new-chat-btn > button {
    background: linear-gradient(135deg,rgba(124,58,237,0.25),rgba(0,229,255,0.1)) !important;
    border: 1px solid rgba(124,58,237,0.5) !important;
    color: #c4b5fd !important; font-weight: 600 !important;
    font-size: 0.85rem !important; letter-spacing: 0.05em !important;
}
.new-chat-btn > button:hover {
    background: linear-gradient(135deg,rgba(124,58,237,0.4),rgba(0,229,255,0.15)) !important;
    box-shadow: 0 0 20px rgba(124,58,237,0.25) !important;
}
.active-chat > button {
    background: rgba(124,58,237,0.15) !important;
    border-left: 2px solid var(--violet) !important;
    color: var(--txt) !important;
    border-radius: 0 8px 8px 0 !important;
}
.pinned-chat > button {
    border-left: 2px solid var(--gold) !important;
    color: #fde68a !important;
}
.icon-btn > button {
    width: auto !important; padding: 0.22rem 0.45rem !important;
    font-size: 0.68rem !important; border-radius: 5px !important;
    color: var(--txt3) !important; min-width: 24px !important;
    text-align: center !important;
}
.icon-btn > button:hover { background: rgba(255,255,255,0.07) !important; color: var(--txt) !important; }
.icon-del > button:hover { background: rgba(239,68,68,0.15) !important; color: var(--red) !important; }
.icon-pin-on > button { color: var(--gold) !important; }

/* ── MESSAGES ── */
.chat-wrap {
    max-width: 820px; margin: 0 auto;
    padding: 4rem 1.5rem 18rem;
}
.msg-row { display:flex; gap:12px; margin-bottom:1.6rem; align-items:flex-start; animation: fadeUp .3s ease; }
.msg-row.user { flex-direction: row-reverse; }
@keyframes fadeUp { from{opacity:0;transform:translateY(10px)} to{opacity:1;transform:translateY(0)} }

.avatar {
    width:36px; height:36px; border-radius:9px; flex-shrink:0;
    display:flex; align-items:center; justify-content:center; font-size:0.95rem;
}
.avatar.ai   { background:linear-gradient(135deg,rgba(0,229,255,0.2),rgba(124,58,237,0.2)); border:1px solid rgba(0,229,255,0.3); }
.avatar.user { background:linear-gradient(135deg,rgba(124,58,237,0.3),rgba(236,72,153,0.2)); border:1px solid rgba(124,58,237,0.4); font-size:0.65rem; font-weight:700; color:#c4b5fd; }

.bubble { max-width:74%; padding:.85rem 1.15rem; border-radius:16px; font-size:.91rem; line-height:1.72; word-break:break-word; }
.bubble.ai   { background:var(--bg3); border:1px solid var(--border); border-top-left-radius:3px; }
.bubble.user { background:linear-gradient(135deg,rgba(124,58,237,0.22),rgba(0,229,255,0.1)); border:1px solid rgba(124,58,237,0.3); border-top-right-radius:3px; }
.ts { font-size:.67rem; color:var(--txt3); margin-top:4px; font-family:'JetBrains Mono',monospace; }

/* ── HEADER STRIP ── */
.top-bar {
    position:fixed; top:0; left:0; right:0; height:50px;
    background:linear-gradient(to bottom,rgba(10,10,15,.97) 70%,transparent);
    z-index:50; display:flex; align-items:center;
    padding:0 1.5rem; gap:10px;
    border-bottom:1px solid var(--border);
}

/* ── BOTTOM INPUT BAR ── */
.bottom-wrap {
    position:fixed; bottom:0; left:0; right:0;
    background:linear-gradient(to top,var(--bg) 65%,transparent);
    padding:.6rem 1.5rem 1.4rem; z-index:1000;
}
.input-box {
    max-width:820px; margin:0 auto;
    background:var(--bg2);
    border:1px solid rgba(124,58,237,0.35);
    border-radius:18px; padding:.6rem .8rem .5rem 1.1rem;
    display:flex; align-items:center; gap:8px;
    box-shadow:0 0 40px rgba(124,58,237,0.08), 0 20px 60px rgba(0,0,0,.5);
    transition:border-color .25s, box-shadow .25s;
}
.input-box:focus-within {
    border-color:rgba(124,58,237,0.65);
    box-shadow:0 0 40px rgba(124,58,237,0.18), 0 20px 60px rgba(0,0,0,.5);
}

/* hide default chat input */
[data-testid="stChatInput"] { display:none !important; }

/* text input inside bar */
.stTextInput > label { display:none !important; }
.stTextInput > div, .stTextInput > div > div { border:none !important; background:transparent !important; box-shadow:none !important; }
.stTextInput > div > div > input {
    background:transparent !important; border:none !important;
    color:var(--txt) !important; font-size:.94rem !important;
    font-family:'Inter',sans-serif !important; box-shadow:none !important;
    padding:.4rem 0 !important; caret-color:var(--cyan);
}
.stTextInput > div > div > input::placeholder { color:var(--txt3) !important; }
.stTextInput > div > div > input:focus { outline:none !important; box-shadow:none !important; }

/* send button */
.send-btn > button {
    background:linear-gradient(135deg,var(--violet),#4f46e5) !important;
    color:#fff !important; border:none !important;
    border-radius:10px !important; width:36px !important; height:36px !important;
    padding:0 !important; font-size:1rem !important; font-weight:700 !important;
    box-shadow:0 0 18px rgba(124,58,237,0.4) !important;
    display:flex !important; align-items:center !important; justify-content:center !important;
    flex-shrink:0 !important;
}
.send-btn > button:hover { box-shadow:0 0 28px rgba(124,58,237,0.6) !important; }

/* mic / image icon buttons in bar */
.bar-icon > button {
    background:transparent !important; border:1px solid var(--border) !important;
    color:var(--txt3) !important; border-radius:8px !important;
    width:34px !important; height:34px !important;
    padding:0 !important; font-size:.9rem !important;
    flex-shrink:0 !important;
    transition:all .18s !important;
}
.bar-icon > button:hover {
    background:rgba(124,58,237,0.12) !important;
    border-color:rgba(124,58,237,0.4) !important;
    color:var(--txt) !important;
}
.bar-icon-on > button {
    background:rgba(0,229,255,0.1) !important;
    border-color:rgba(0,229,255,0.4) !important;
    color:var(--cyan) !important;
}

/* file uploader compact */
[data-testid="stFileUploader"] section {
    background:rgba(20,20,40,0.9) !important;
    border:1px dashed rgba(124,58,237,0.4) !important;
    border-radius:10px !important; padding:.4rem !important;
    font-size:.78rem !important;
}
[data-testid="stFileUploader"] label { display:none !important; }

audio { width:100%; margin-top:8px; border-radius:8px; }
hr { border-color:var(--border); margin:.4rem 0; }
::-webkit-scrollbar { width:4px; }
::-webkit-scrollbar-thumb { background:rgba(124,58,237,0.25); border-radius:4px; }

.del-confirm {
    background:rgba(239,68,68,0.08); border:1px solid rgba(239,68,68,0.25);
    border-radius:9px; padding:.5rem .7rem; margin:3px 0;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# ANIMATED BACKGROUND  (Aurora + particles)
# ══════════════════════════════════════════════════════
st.markdown("""
<div style="position:fixed;inset:0;z-index:0;overflow:hidden;pointer-events:none;">
<svg width="100%" height="100%" viewBox="0 0 1440 900" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid slice">
  <defs>
    <radialGradient id="a1" cx="20%" cy="40%" r="55%">
      <stop offset="0%" stop-color="#7c3aed" stop-opacity=".18"/>
      <stop offset="100%" stop-color="#7c3aed" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="a2" cx="80%" cy="60%" r="55%">
      <stop offset="0%" stop-color="#00e5ff" stop-opacity=".12"/>
      <stop offset="100%" stop-color="#00e5ff" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="a3" cx="50%" cy="90%" r="50%">
      <stop offset="0%" stop-color="#ec4899" stop-opacity=".10"/>
      <stop offset="100%" stop-color="#ec4899" stop-opacity="0"/>
    </radialGradient>
    <filter id="blur18"><feGaussianBlur stdDeviation="18"/></filter>
    <filter id="blur6"><feGaussianBlur stdDeviation="6"/></filter>
  </defs>
  <rect width="1440" height="900" fill="#0a0a0f"/>
  <!-- Aurora blobs -->
  <ellipse cx="288" cy="360" rx="420" ry="280" fill="url(#a1)" filter="url(#blur18)">
    <animate attributeName="cx" values="288;340;288" dur="18s" repeatCount="indefinite"/>
    <animate attributeName="cy" values="360;320;360" dur="14s" repeatCount="indefinite"/>
  </ellipse>
  <ellipse cx="1152" cy="540" rx="380" ry="260" fill="url(#a2)" filter="url(#blur18)">
    <animate attributeName="cx" values="1152;1100;1152" dur="20s" repeatCount="indefinite"/>
    <animate attributeName="cy" values="540;580;540" dur="16s" repeatCount="indefinite"/>
  </ellipse>
  <ellipse cx="720" cy="810" rx="500" ry="200" fill="url(#a3)" filter="url(#blur18)">
    <animate attributeName="rx" values="500;460;500" dur="12s" repeatCount="indefinite"/>
  </ellipse>
  <!-- Stars -->
  <g opacity=".6">
    <circle cx="110" cy="55"  r=".9" fill="#e2e8f0"/>
    <circle cx="260" cy="90"  r=".7" fill="#c4b5fd"/>
    <circle cx="430" cy="35"  r="1"  fill="#e2e8f0"/>
    <circle cx="600" cy="70"  r=".8" fill="#93c5fd"/>
    <circle cx="760" cy="22"  r=".9" fill="#e2e8f0"/>
    <circle cx="920" cy="58"  r=".7" fill="#c4b5fd"/>
    <circle cx="1090" cy="42" r="1"  fill="#e2e8f0"/>
    <circle cx="1260" cy="78" r=".8" fill="#93c5fd"/>
    <circle cx="1400" cy="30" r=".9" fill="#e2e8f0"/>
    <circle cx="180"  cy="160" r=".8" fill="#c4b5fd"/>
    <circle cx="380"  cy="140" r="1"  fill="#e2e8f0"/>
    <circle cx="550"  cy="195" r=".7" fill="#93c5fd"/>
    <circle cx="840"  cy="155" r=".9" fill="#e2e8f0"/>
    <circle cx="1000" cy="130" r=".8" fill="#c4b5fd"/>
    <circle cx="1200" cy="170" r="1"  fill="#e2e8f0"/>
    <circle cx="340"  cy="280" r=".8" fill="#c4b5fd"/>
    <circle cx="680"  cy="260" r=".9" fill="#e2e8f0"/>
    <circle cx="1050" cy="290" r=".7" fill="#93c5fd"/>
    <circle cx="1350" cy="245" r="1"  fill="#e2e8f0"/>
  </g>
  <!-- Twinkle -->
  <g filter="url(#blur6)">
    <circle cx="460" cy="85" r="2" fill="#fff" opacity=".8">
      <animate attributeName="opacity" values=".8;.1;.8" dur="3.2s" repeatCount="indefinite"/>
    </circle>
    <circle cx="890" cy="50" r="1.5" fill="#c4b5fd" opacity=".7">
      <animate attributeName="opacity" values=".7;.15;.7" dur="4.8s" repeatCount="indefinite"/>
    </circle>
    <circle cx="1210" cy="120" r="2" fill="#fff" opacity=".6">
      <animate attributeName="opacity" values=".6;.1;.6" dur="2.9s" repeatCount="indefinite"/>
    </circle>
    <circle cx="220" cy="200" r="1.5" fill="#93c5fd" opacity=".7">
      <animate attributeName="opacity" values=".7;.2;.7" dur="5.1s" repeatCount="indefinite"/>
    </circle>
    <circle cx="730" cy="165" r="2" fill="#fff" opacity=".5">
      <animate attributeName="opacity" values=".5;.08;.5" dur="3.7s" repeatCount="indefinite"/>
    </circle>
  </g>
  <!-- Grid lines (subtle) -->
  <g opacity=".025" stroke="#7c3aed" stroke-width=".5">
    <line x1="0" y1="150" x2="1440" y2="150"/>
    <line x1="0" y1="300" x2="1440" y2="300"/>
    <line x1="0" y1="450" x2="1440" y2="450"/>
    <line x1="0" y1="600" x2="1440" y2="600"/>
    <line x1="0" y1="750" x2="1440" y2="750"/>
    <line x1="240" y1="0" x2="240" y2="900"/>
    <line x1="480" y1="0" x2="480" y2="900"/>
    <line x1="720" y1="0" x2="720" y2="900"/>
    <line x1="960" y1="0" x2="960" y2="900"/>
    <line x1="1200" y1="0" x2="1200" y2="900"/>
  </g>
  <!-- Floating orbs -->
  <circle cx="200" cy="700" r="3" fill="#7c3aed" opacity=".4" filter="url(#blur6)">
    <animate attributeName="cy" values="700;660;700" dur="8s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values=".4;.7;.4" dur="8s" repeatCount="indefinite"/>
  </circle>
  <circle cx="1240" cy="650" r="2.5" fill="#00e5ff" opacity=".35" filter="url(#blur6)">
    <animate attributeName="cy" values="650;610;650" dur="10s" repeatCount="indefinite"/>
  </circle>
  <circle cx="720" cy="750" r="2" fill="#ec4899" opacity=".3" filter="url(#blur6)">
    <animate attributeName="cy" values="750;720;750" dur="7s" repeatCount="indefinite"/>
  </circle>
</svg>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# ENTER KEY  (submits on Enter)
# ══════════════════════════════════════════════════════
st.markdown("""
<script>
(function(){
  function bind(){
    document.querySelectorAll('input[data-testid="stTextInput"]').forEach(function(el){
      if(el.dataset._bound) return;
      el.dataset._bound="1";
      el.addEventListener('keydown',function(e){
        if(e.key==='Enter'&&!e.shiftKey&&el.value.trim()!==''){
          e.preventDefault();
          // find and click the send button (↑) once
          var btns = document.querySelectorAll('.stButton button');
          for(var i=0;i<btns.length;i++){
            if(btns[i].textContent.trim()==='↑'){
              btns[i].click();
              break;
            }
          }
        }
      });
    });
  }
  new MutationObserver(bind).observe(document.body,{childList:true,subtree:true});
  [0,300,800,1500,3000].forEach(function(d){setTimeout(bind,d);});
})();
</script>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════
def safe_post(url, **kwargs):
    try:
        return requests.post(url, timeout=30, **kwargs)
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None


def ts():
    return datetime.now().strftime("%H:%M")


def render_message(role, content, audio_path=None):
    cls    = "ai" if role == "assistant" else "user"
    avatar = "✦"  if role == "assistant" else "YOU"
    align  = ""   if cls == "ai" else "text-align:right;"
    st.markdown(f"""
    <div class="msg-row {cls}">
      <div class="avatar {cls}">{avatar}</div>
      <div style="flex:1;min-width:0;">
        <div class="bubble {cls}">{content}</div>
        <div class="ts" style="{align}">{ts()}</div>
      </div>
    </div>""", unsafe_allow_html=True)
    if audio_path and os.path.exists(audio_path):
        with open(audio_path,"rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        ext  = audio_path.split(".")[-1]
        mime = "audio/mpeg" if ext == "mp3" else "audio/wav"
        st.markdown(f'<audio controls><source src="data:{mime};base64,{b64}"></audio>', unsafe_allow_html=True)


def auto_title(user_msg, ai_reply):
    """Generate a short topic-based title via Groq."""
    if not GROQ_API_KEY:
        t = user_msg.strip().replace("\n"," ")
        return t[:30]+("…" if len(t)>30 else "")
    try:
        prompt = (
            f'User: "{user_msg[:200]}"\nAI: "{ai_reply[:200]}"\n\n'
            "Give a short chat title (max 5 words, no quotes, no punctuation at end). "
            "Make it describe the topic. Reply with ONLY the title."
        )
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type":"application/json"},
            json={"model":"llama3-8b-8192","messages":[{"role":"user","content":prompt}],"max_tokens":20,"temperature":.7},
            timeout=8
        )
        if r.status_code == 200:
            title = r.json()["choices"][0]["message"]["content"].strip().strip('"\'')
            return title[:38] if title else "New Session"
    except Exception:
        pass
    t = user_msg.strip().replace("\n"," ")
    return t[:30]+("…" if len(t)>30 else "")


# ══════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════
def new_chat_obj():
    return {"messages":[], "title":"New Session", "pinned":False, "created":datetime.now()}

if "chats" not in st.session_state:
    cid = str(uuid.uuid4())
    st.session_state.chats        = {cid: new_chat_obj()}
    st.session_state.current_chat = cid

if "audio_store"    not in st.session_state: st.session_state.audio_store    = {}
if "show_mic"       not in st.session_state: st.session_state.show_mic       = False
if "show_img"       not in st.session_state: st.session_state.show_img       = False
if "confirm_delete" not in st.session_state: st.session_state.confirm_delete = None
if "pending_input"  not in st.session_state: st.session_state.pending_input  = ""
if "input_key"      not in st.session_state: st.session_state.input_key      = 0
if "last_processed" not in st.session_state: st.session_state.last_processed = ""

def migrate(cid):
    c = st.session_state.chats[cid]
    if isinstance(c, list):
        st.session_state.chats[cid] = {"messages":c,"title":"New Session","pinned":False,"created":datetime.now()}

for _c in list(st.session_state.chats): migrate(_c)

def msgs(cid):  return st.session_state.chats[cid]["messages"]
def title(cid): return st.session_state.chats[cid].get("title","New Session")
def pinned(cid):return st.session_state.chats[cid].get("pinned",False)

def delete_chat(cid):
    all_ids = list(st.session_state.chats.keys())
    remaining = [c for c in all_ids if c != cid]
    del st.session_state.chats[cid]
    st.session_state.audio_store.pop(cid, None)
    st.session_state.confirm_delete = None
    if not remaining:
        ncid = str(uuid.uuid4())
        st.session_state.chats[ncid] = new_chat_obj()
        st.session_state.current_chat = ncid
    elif st.session_state.current_chat == cid:
        st.session_state.current_chat = remaining[-1]


# ══════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════
with st.sidebar:
    # Brand
    st.markdown("""
    <div style="padding:.6rem 0 .9rem;">
      <div style="display:flex;align-items:center;gap:10px;">
        <div style="width:34px;height:34px;border-radius:9px;
          background:linear-gradient(135deg,rgba(124,58,237,.35),rgba(0,229,255,.15));
          border:1px solid rgba(124,58,237,.5);
          display:flex;align-items:center;justify-content:center;font-size:1.1rem;">✦</div>
        <div>
          <div style="font-size:1.05rem;font-weight:700;letter-spacing:.08em;color:#e2e8f0;">SPARKUS AI</div>
          <div style="font-size:.58rem;color:#475569;font-family:'JetBrains Mono',monospace;letter-spacing:.1em;">MULTIMODAL · v1.0</div>
        </div>
      </div>
    </div>
    <hr/>
    """, unsafe_allow_html=True)

    # New chat
    st.markdown('<div class="new-chat-btn">', unsafe_allow_html=True)
    if st.button("＋  New Session", key="new_chat"):
        ncid = str(uuid.uuid4())
        st.session_state.chats[ncid] = new_chat_obj()
        st.session_state.current_chat = ncid
        st.session_state.confirm_delete = None
        st.session_state.last_processed = ""
        st.session_state.input_key += 1
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    all_ids = list(st.session_state.chats.keys())
    pinned_ids   = [c for c in all_ids if  pinned(c)]
    unpinned_ids = [c for c in all_ids if not pinned(c)]

    def chat_row(cid):
        t           = title(cid)
        is_active   = cid == st.session_state.current_chat
        is_del      = st.session_state.confirm_delete == cid
        is_pin      = pinned(cid)

        if is_del:
            st.markdown('<div class="del-confirm">', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:.71rem;color:#ef4444;margin-bottom:5px;">Delete "{t[:22]}"?</div>', unsafe_allow_html=True)
            ca, cb = st.columns(2)
            with ca:
                if st.button("✕ Delete", key=f"yes_{cid}"):
                    delete_chat(cid); st.rerun()
            with cb:
                if st.button("Cancel",  key=f"no_{cid}"):
                    st.session_state.confirm_delete = None; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            return

        row_cls = "active-chat" if is_active else ("pinned-chat" if is_pin else "")
        c1, c2, c3 = st.columns([7, 1.4, 1.4])
        with c1:
            if row_cls: st.markdown(f'<div class="{row_cls}">', unsafe_allow_html=True)
            prefix = "📌 " if is_pin else "  "
            if st.button(f"{prefix}{t}", key=f"sel_{cid}"):
                st.session_state.current_chat = cid
                st.session_state.confirm_delete = None
                st.session_state.last_processed = ""
                st.rerun()
            if row_cls: st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            pin_cls = "icon-btn icon-pin-on" if is_pin else "icon-btn"
            st.markdown(f'<div class="{pin_cls}">', unsafe_allow_html=True)
            star = "★" if is_pin else "☆"
            if st.button(star, key=f"pin_{cid}"):
                st.session_state.chats[cid]["pinned"] = not is_pin; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with c3:
            st.markdown('<div class="icon-btn icon-del">', unsafe_allow_html=True)
            if st.button("✕", key=f"del_{cid}"):
                st.session_state.confirm_delete = cid; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    if pinned_ids:
        st.markdown('<div style="font-size:.58rem;color:#b45309;font-family:JetBrains Mono,monospace;letter-spacing:.1em;text-transform:uppercase;margin:.5rem 0 .25rem;padding-left:4px;">📌 Pinned</div>', unsafe_allow_html=True)
        for c in pinned_ids: chat_row(c)

    st.markdown('<div style="font-size:.58rem;color:#475569;font-family:JetBrains Mono,monospace;letter-spacing:.1em;text-transform:uppercase;margin:.6rem 0 .25rem;padding-left:4px;">Recent</div>', unsafe_allow_html=True)
    for c in reversed(unpinned_ids): chat_row(c)

    st.markdown('<hr/>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:.6rem;color:#334155;font-family:JetBrains Mono,monospace;">Groq · LLaMA 3.3 · BLIP · Whisper</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
# GUARD
# ══════════════════════════════════════════════════════
if st.session_state.current_chat not in st.session_state.chats:
    st.session_state.current_chat = list(st.session_state.chats.keys())[-1]

cid     = st.session_state.current_chat
history = msgs(cid)
audios  = st.session_state.audio_store.get(cid, [])
cur_title = title(cid)


# ══════════════════════════════════════════════════════
# TOP BAR
# ══════════════════════════════════════════════════════
st.markdown(f"""
<div class="top-bar">
  <span style="font-size:1.1rem;color:#7c3aed;">✦</span>
  <span style="font-size:.78rem;font-family:JetBrains Mono,monospace;color:#475569;
    letter-spacing:.04em;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;max-width:500px;">
    {cur_title}
  </span>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
# MESSAGES
# ══════════════════════════════════════════════════════
st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)

if not history:
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
      min-height:52vh;text-align:center;padding:3rem 1rem;">
      <div style="width:70px;height:70px;border-radius:18px;margin-bottom:1.4rem;
        background:linear-gradient(135deg,rgba(124,58,237,.25),rgba(0,229,255,.15));
        border:1px solid rgba(124,58,237,.4);display:flex;align-items:center;
        justify-content:center;font-size:2rem;
        box-shadow:0 0 40px rgba(124,58,237,.2);">✦</div>
      <div style="font-size:2rem;font-weight:700;letter-spacing:.06em;
        background:linear-gradient(135deg,#e2e8f0,#c4b5fd 50%,#00e5ff);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
        background-clip:text;text-transform:uppercase;margin-bottom:.4rem;">
        Sparkus AI
      </div>
      <div style="font-size:.8rem;color:#475569;font-family:JetBrains Mono,monospace;
        letter-spacing:.1em;margin-bottom:2rem;">
        // multimodal intelligence ready //
      </div>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;max-width:520px;">
        <div style="background:rgba(20,20,40,.7);border:1px solid rgba(255,255,255,.06);
          border-radius:12px;padding:.9rem;font-size:.75rem;color:#94a3b8;">
          <div style="font-size:1.1rem;margin-bottom:6px;">⌨️</div>Deep conversation & reasoning
        </div>
        <div style="background:rgba(20,20,40,.7);border:1px solid rgba(255,255,255,.06);
          border-radius:12px;padding:.9rem;font-size:.75rem;color:#94a3b8;">
          <div style="font-size:1.1rem;margin-bottom:6px;">🎙️</div>Voice input with Whisper
        </div>
        <div style="background:rgba(20,20,40,.7);border:1px solid rgba(255,255,255,.06);
          border-radius:12px;padding:.9rem;font-size:.75rem;color:#94a3b8;">
          <div style="font-size:1.1rem;margin-bottom:6px;">🖼️</div>Image analysis via BLIP
        </div>
      </div>
      <div style="margin-top:1.8rem;font-size:.68rem;color:#334155;
        font-family:JetBrains Mono,monospace;">
        Sessions auto-named · Pin chats · Press Enter to send
      </div>
    </div>
    """, unsafe_allow_html=True)

for i, m in enumerate(history):
    render_message(m["role"], m["content"], audios[i] if i < len(audios) else None)

# ── Thinking slot lives here, right after messages, inside chat area ──
thinking_slot = st.empty()

st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
# BOTTOM INPUT BAR  — text | 🎙️ | 🖼️ | ↑
# ══════════════════════════════════════════════════════
st.markdown('<div class="bottom-wrap">', unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="input-box">', unsafe_allow_html=True)

    # Inline panels (mic / image) shown above input when toggled
    mic_audio  = None
    image_file = None

    if st.session_state.show_mic:
        mic_audio = mic_recorder(
            start_prompt="🔴 Tap to speak",
            stop_prompt="⏹ Stop",
            just_once=True,
            use_container_width=False,
            key=f"mic_{cid}"
        )

    if st.session_state.show_img:
        image_file = st.file_uploader(
            "img", type=["png","jpg","jpeg","webp"],
            label_visibility="collapsed", key=f"img_{cid}"
        )

    # ── Main row: text + mic-btn + img-btn + send ──
    col_txt, col_mic, col_img, col_snd = st.columns([10, 0.8, 0.8, 0.8])

    with col_txt:
        user_text = st.text_input(
            "msg", placeholder="Message Sparkus AI…",
            label_visibility="collapsed",
            key=f"txt_{cid}_{st.session_state.input_key}"
        )

    with col_mic:
        mic_cls = "bar-icon-on" if st.session_state.show_mic else "bar-icon"
        st.markdown(f'<div class="{mic_cls}">', unsafe_allow_html=True)
        if st.button("🎙️", key="tog_mic", help="Voice input"):
            st.session_state.show_mic = not st.session_state.show_mic
            st.session_state.show_img = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_img:
        img_cls = "bar-icon-on" if st.session_state.show_img else "bar-icon"
        st.markdown(f'<div class="{img_cls}">', unsafe_allow_html=True)
        if st.button("🖼️", key="tog_img", help="Image input"):
            st.session_state.show_img = not st.session_state.show_img
            st.session_state.show_mic = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_snd:
        st.markdown('<div class="send-btn">', unsafe_allow_html=True)
        send = st.button("↑", key=f"snd_{cid}")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
# PROCESS: TEXT
# ══════════════════════════════════════════════════════
should_send = send and user_text.strip()

if should_send:
    txt = user_text.strip()

    # Guard: don't process the same message twice
    if txt == st.session_state.last_processed:
        st.stop()

    st.session_state.last_processed = txt

    # ── 1. Add to history + clear input ──
    history.append({"role": "user", "content": txt})
    audios.append(None)
    st.session_state.audio_store[cid] = audios
    st.session_state.input_key += 1

    # ── 2. Show thinking dots in the chat area (right after messages) ──
    thinking_slot.markdown("""
    <div class="msg-row ai">
      <div class="avatar ai">✦</div>
      <div>
        <div class="bubble ai" style="display:flex;gap:7px;align-items:center;padding:.75rem 1.1rem;">
          <span style="width:9px;height:9px;border-radius:50%;background:#7c3aed;display:inline-block;animation:tpulse 1.2s infinite 0s;"></span>
          <span style="width:9px;height:9px;border-radius:50%;background:#7c3aed;display:inline-block;animation:tpulse 1.2s infinite .22s;"></span>
          <span style="width:9px;height:9px;border-radius:50%;background:#7c3aed;display:inline-block;animation:tpulse 1.2s infinite .44s;"></span>
        </div>
      </div>
    </div>
    <style>
    @keyframes tpulse{0%,80%,100%{transform:scale(.65);opacity:.3}40%{transform:scale(1.15);opacity:1}}
    </style>
    """, unsafe_allow_html=True)

    # ── 3. Call backend ──
    resp = safe_post(
        f"{API}/assistant/text",
        json={"text": txt, "history": [
            {"role": m["role"], "content": m["content"]}
            for m in history[:-1]
        ]}
    )

    if resp and resp.status_code == 200:
        data  = resp.json()
        reply = data.get("text", "Sorry, no response.")
        audio = data.get("audio")
    else:
        reply = "⚠️ AI service unavailable — start the backend:\n\n`uvicorn app.main_fastapi:app --reload --port 8000`"
        audio = None

    history.append({"role": "assistant", "content": reply})
    audios.append(audio)

    if len(history) == 2:
        st.session_state.chats[cid]["title"] = auto_title(txt, reply)

    st.session_state.audio_store[cid] = audios
    st.rerun()


# ══════════════════════════════════════════════════════
# PROCESS: MIC
# ══════════════════════════════════════════════════════
if mic_audio and mic_audio.get("bytes"):
    last = history[-1]["content"] if history else ""
    if last != "🎤 Sending…":
        history.append({"role":"user","content":"🎤 Sending…"})
        audios.append(None)
        st.session_state.audio_store[cid] = audios

        thinking_slot.markdown("""
        <div class="msg-row ai"><div class="avatar ai">✦</div>
        <div><div class="bubble ai" style="font-size:.82rem;color:#94a3b8;padding:.75rem 1.1rem;">
        🎙️ Transcribing your voice…</div></div></div>
        """, unsafe_allow_html=True)

        resp = safe_post(
            f"{API}/assistant/audio",
            files={"file":("rec.wav", mic_audio["bytes"], "audio/wav")}
        )

        if resp and resp.status_code == 200:
            data       = resp.json()
            reply      = data.get("text","Could not process audio.")
            audio      = data.get("audio")
            transcript = data.get("transcript","")
            if transcript:
                history[-1]["content"] = f'🎤 *"{transcript}"*'
        else:
            reply, audio = "⚠️ Audio processing failed.", None

        history.append({"role":"assistant","content": reply})
        audios.append(audio)
        if len(history) == 2:
            st.session_state.chats[cid]["title"] = auto_title(history[0]["content"], reply)
        st.session_state.audio_store[cid] = audios
        st.session_state.show_mic = False
        st.rerun()


# ══════════════════════════════════════════════════════
# PROCESS: IMAGE
# ══════════════════════════════════════════════════════
if image_file:
    last = history[-1]["content"] if history else ""
    if not last.startswith("<img"):
        history.append({"role":"user","content":"🖼️ Analyzing…"})
        audios.append(None)
        st.session_state.audio_store[cid] = audios

        thinking_slot.markdown("""
        <div class="msg-row ai"><div class="avatar ai">✦</div>
        <div><div class="bubble ai" style="font-size:.82rem;color:#94a3b8;padding:.75rem 1.1rem;">
        🖼️ Analyzing your image…</div></div></div>
        """, unsafe_allow_html=True)

        img_bytes = image_file.read()
        resp = safe_post(
            f"{API}/assistant/image",
            files={"file":(image_file.name, img_bytes, image_file.type)}
        )

        if resp and resp.status_code == 200:
            data  = resp.json()
            reply = data.get("text","Could not analyze image.")
            audio = data.get("audio")
            b64   = base64.b64encode(img_bytes).decode()
            history[-1]["content"] = (
                f'<img src="data:{image_file.type};base64,{b64}" '
                f'style="max-width:280px;border-radius:12px;margin-top:6px;">'
            )
        else:
            reply, audio = "⚠️ Image processing failed.", None

        history.append({"role":"assistant","content": reply})
        audios.append(audio)
        if len(history) == 2:
            st.session_state.chats[cid]["title"] = auto_title("Image uploaded", reply)
        st.session_state.audio_store[cid] = audios
        st.session_state.show_img = False
        st.rerun()