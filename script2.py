import streamlit as st
import datetime
import pandas as pd
import sqlite3
import time
import base64
import hashlib
import os

# ─────────────────────────────────────────────────────────────────────────
# ✅ FIX #10: "Remember Me" cookie so login survives session drops.
# Streamlit's st.session_state lives only as long as the browser's live
# WebSocket connection. If the tab goes idle/background (phone lock, tab
# switch, weak network), the connection can drop and reconnect as a BRAND
# NEW session -> session_state resets -> user gets bounced back to login.
# A browser cookie survives that reconnect, so we use one to silently
# restore the login instead of forcing the person to type email+password
# again every time they come back to the tab.
# pip install streamlit-cookies-controller
# ─────────────────────────────────────────────────────────────────────────
try:
    from streamlit_cookies_controller import CookieController
    cookies = CookieController()
    COOKIES_AVAILABLE = True
except ImportError:
    COOKIES_AVAILABLE = False
    st.warning("⚠️ Install `streamlit-cookies-controller` to stay logged in across reconnects: pip install streamlit-cookies-controller", icon="⚠️")

st.set_page_config(
    page_title="PCAS VIRTUAL OFFICE v2",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────────────────────────────────
# ✅ FIX #1: Real-time refresh WITHOUT the infinite sleep+rerun loop.
# The old `time.sleep(0.5); st.rerun()` at the bottom of the script caused
# every connected user to hammer the server in a tight loop -> CPU 100%,
# crashes on Streamlit Cloud, and dropped clicks. This uses a proper
# timed refresh instead. Run: pip install streamlit-autorefresh
# ─────────────────────────────────────────────────────────────────────────
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=4000, key="office_live_refresh")
except ImportError:
    st.warning("⚠️ Install `streamlit-autorefresh` for live updates: pip install streamlit-autorefresh", icon="⚠️")

st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
}
.header-mild-box {
    background-color: #ebf5fb !important; border: 1px solid #d6eaf8 !important;
    border-radius: 12px !important; padding: 12px 18px !important; margin-bottom: 20px !important;
}
.main-title { font-size: 28px !important; font-weight: 800 !important; color: #1a365d !important; }
.dept-box { border-radius: 8px; padding: 10px; margin: 8px 0; text-align: center; font-weight: bold; color: #fff; font-size: 14px; }
.bg-manager    { background-color: #2c3e50; }
.bg-chemical   { background-color: #16a085; }
.bg-mechanical { background-color: #2980b9; }
.bg-electrical { background-color: #d35400; }
.bg-acc-manager{ background-color: #8e44ad; }
.bg-sales      { background-color: #27ae60; }
.bg-accountant { background-color: #c0392b; }
.status-online  { background-color: #e8f8f5; border-left: 5px solid #2ecc71; border-radius: 6px; padding: 8px; text-align: center; }
.status-busy    { background-color: #fce4d6; border-left: 5px solid #e74c3c; border-radius: 6px; padding: 8px; text-align: center; }
.status-break   { background-color: #fef9e7; border-left: 5px solid #f1c40f; border-radius: 6px; padding: 8px; text-align: center; }
.status-wfh     { background-color: #ebf5fb; border-left: 5px solid #3498db; border-radius: 6px; padding: 8px; text-align: center; }
.status-offline { background-color: #f4f6f7; border-left: 5px solid #95a5a6; border-radius: 6px; padding: 8px; text-align: center; }
.desk-title  { font-size: 11px; font-weight: bold; color: #2c3e50; margin-bottom: 4px; }
.metric-card { background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 12px; text-align: center; }
.notice-box  { background-color: #fff3cd; border: 1px solid #ffeba2; border-left: 6px solid #ffc107; border-radius: 6px; padding: 12px; margin-bottom: 15px; }
.chat-bubble-me {
    background: linear-gradient(135deg, #dcf8c6, #c8f0a8);
    border-radius: 18px 18px 4px 18px; padding: 10px 14px;
    margin: 6px 0 6px 15%; text-align: right;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1); font-size: 15px;
}
.chat-bubble-other {
    background: #ffffff; border-radius: 18px 18px 18px 4px;
    padding: 10px 14px; margin: 4px 0; text-align: left;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1); border: 1px solid #eee;
    font-size: 15px; flex: 1;
}
.chat-time   { font-size: 10px; color: #999; margin-top: 3px; }
.chat-sender { font-size: 11px; color: #075e54; font-weight: bold; margin-bottom: 3px; }
.unread-badge { background: #e74c3c; color: white; border-radius: 50%; padding: 2px 7px; font-size: 11px; font-weight: bold; }
.allocation-dark-box {
    background-color: #4a235a !important; border-radius: 10px !important;
    padding: 12px !important; text-align: center !important; color: #fff !important;
    font-size: 16px !important; font-weight: bold !important; margin-bottom: 15px !important;
}
.groupboard-dark-box {
    background-color: #1a5276 !important; border-radius: 10px !important;
    padding: 12px !important; text-align: center !important; color: #fff !important;
    font-size: 16px !important; font-weight: bold !important;
    margin-bottom: 12px !important; margin-top: 15px !important;
}
.photo-panel-box {
    background: #eaf4fb; border: 1px solid #aed6f1;
    border-radius: 12px; padding: 20px; text-align: center;
}
.avatar-ring {
    border-radius: 50%; object-fit: cover;
    border: 3px solid white;
    box-shadow: 0 3px 10px rgba(0,0,0,0.2);
    display: block; margin: auto;
}
</style>
""", unsafe_allow_html=True)

# =========================================================================
# ✅ FIX #3: Secrets instead of hardcoded plaintext passwords in source.
# Create a file `.streamlit/secrets.toml` (and add it to .gitignore so it
# is NEVER pushed to GitHub) with:
#   OFFICE_PASSWORD = "PCAS@2026"
#   ADMIN_EXTRACT_PASSWORD = "ADMIN@PCAS"
#   ALLOWED_DOMAIN = "@pcas-cert.com"
# If secrets.toml is missing, these defaults are used so the app still
# runs locally in PyCharm without extra setup.
# =========================================================================
def get_secret(key, default):
    try:
        return st.secrets[key]
    except Exception:
        return default

OFFICE_PASSWORD        = get_secret("OFFICE_PASSWORD", "PCAS@2026")
ADMIN_EXTRACT_PASSWORD = get_secret("ADMIN_EXTRACT_PASSWORD", "ADMIN@PCAS")
ALLOWED_DOMAIN         = get_secret("ALLOWED_DOMAIN", "@pcas-cert.com")

DB_PATH           = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pcas_office.db")
HEARTBEAT_TIMEOUT = 12
MAX_FILE_SIZE_MB  = 5
QUICK_EMOJIS      = ["👍","❤️","😂","😮","🙏","🔥","✅","👏"]
AVATAR_COLORS = [
    "#e74c3c","#e67e22","#f39c12","#27ae60","#16a085",
    "#2980b9","#8e44ad","#c0392b","#d35400","#1a5276",
    "#117a65","#1d8348","#7d6608","#6e2f8f","#1f618d"
]

def get_dubai_time():
    return datetime.datetime.utcnow() + datetime.timedelta(hours=4)

def get_avatar_color(name):
    idx = int(hashlib.md5(name.encode()).hexdigest(), 16) % len(AVATAR_COLORS)
    return AVATAR_COLORS[idx]

def get_initials(name):
    parts = name.strip().split()
    return (parts[0][0]+parts[1][0]).upper() if len(parts) >= 2 else parts[0][:2].upper()

def get_avatar_html(username, size=50):
    photo = get_profile_photo(username)
    if photo:
        return (f'<img src="data:image/jpeg;base64,{photo}" '
                f'class="avatar-ring" width="{size}" height="{size}" '
                f'style="width:{size}px;height:{size}px;">')
    color    = get_avatar_color(username)
    initials = get_initials(username)
    fs       = max(11, size // 3)
    return (f'<div style="width:{size}px;height:{size}px;border-radius:50%;'
            f'background:{color};color:#fff;display:flex;align-items:center;'
            f'justify-content:center;font-size:{fs}px;font-weight:900;'
            f'margin:auto;border:3px solid white;'
            f'box-shadow:0 3px 10px rgba(0,0,0,0.2);">{initials}</div>')

# =========================================================================
# ✅ FIX #2: SQLite concurrency hardening.
# Every connection now uses a 30s busy timeout + WAL journal mode, so
# multiple staff checking in / chatting at the same moment no longer
# throws "database is locked" errors.
# =========================================================================
def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=30000;")
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("PRAGMA table_info(desks)")
    cols = [r[1] for r in c.fetchall()]
    if cols and "desk_id" not in cols:
        c.execute("DROP TABLE IF EXISTS desks")
    c.execute('''CREATE TABLE IF NOT EXISTS desks (
        desk_id INTEGER PRIMARY KEY,
        name TEXT DEFAULT '🪑 Empty',
        status TEXT DEFAULT 'Offline',
        checkin_time TEXT DEFAULT '-',
        last_heartbeat REAL DEFAULT 0)''')
    c.execute("SELECT COUNT(*) FROM desks")
    if c.fetchone()[0] == 0:
        for i in range(1, 23):
            c.execute("INSERT INTO desks VALUES (?,?,?,?,?)", (i, '🪑 Empty', 'Offline', '-', 0))
    try: c.execute("ALTER TABLE desks ADD COLUMN last_heartbeat REAL DEFAULT 0")
    except Exception: pass

    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        staff_name TEXT, date TEXT, desk TEXT,
        checkin_time TEXT, checkout_time TEXT DEFAULT 'Active In Office', status TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS group_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT, message TEXT, timestamp TEXT,
        file_data TEXT, file_name TEXT, file_type TEXT)''')
    for col in ["file_data", "file_name", "file_type"]:
        try: c.execute(f"ALTER TABLE group_messages ADD COLUMN {col} TEXT")
        except Exception: pass

    c.execute('''CREATE TABLE IF NOT EXISTS private_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT, receiver TEXT, message TEXT, timestamp TEXT,
        is_read INTEGER DEFAULT 0,
        file_data TEXT, file_name TEXT, file_type TEXT)''')
    for col in ["file_data", "file_name", "file_type"]:
        try: c.execute(f"ALTER TABLE private_messages ADD COLUMN {col} TEXT")
        except Exception: pass

    c.execute('''CREATE TABLE IF NOT EXISTS notice (
        id INTEGER PRIMARY KEY, text TEXT, posted_by TEXT)''')
    c.execute("SELECT COUNT(*) FROM notice")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO notice VALUES (1,'Welcome to PCAS Virtual Office v2.0!','Admin')")

    c.execute('''CREATE TABLE IF NOT EXISTS profiles (
        username TEXT PRIMARY KEY, photo_data TEXT)''')

    conn.commit(); conn.close()

init_db()

# =========================================================================
# DB HELPERS
# =========================================================================
def get_all_desks():
    conn = get_db()
    df = pd.read_sql("SELECT * FROM desks ORDER BY desk_id", conn)
    conn.close(); return df

def update_desk(desk_id, name, status, checkin_time):
    conn = get_db()
    conn.execute(
        "UPDATE desks SET name=?,status=?,checkin_time=?,last_heartbeat=? WHERE desk_id=?",
        (name, status, checkin_time, time.time(), desk_id))
    conn.commit(); conn.close()

def clear_desk(desk_id):
    conn = get_db()
    conn.execute(
        "UPDATE desks SET name='🪑 Empty',status='Offline',checkin_time='-',last_heartbeat=0 WHERE desk_id=?",
        (desk_id,))
    conn.commit(); conn.close()

def clear_user_desk(name):
    conn = get_db()
    conn.execute(
        "UPDATE desks SET name='🪑 Empty',status='Offline',checkin_time='-',last_heartbeat=0 WHERE name=?",
        (name,))
    conn.commit(); conn.close()

def update_heartbeat(name):
    conn = get_db()
    conn.execute("UPDATE desks SET last_heartbeat=? WHERE name=?", (time.time(), name))
    conn.commit(); conn.close()

def cleanup_disconnected():
    ts = time.time() - HEARTBEAT_TIMEOUT
    conn = get_db()
    cur = conn.execute(
        "SELECT name FROM desks WHERE name!='🪑 Empty' AND last_heartbeat<? AND last_heartbeat!=0",
        (ts,))
    for (user,) in cur.fetchall():
        conn.execute(
            "UPDATE attendance SET checkout_time=? WHERE staff_name=? AND checkout_time='Active In Office'",
            (get_dubai_time().strftime("%I:%M %p") + " (Disconnected)", user))
        conn.execute(
            "UPDATE desks SET name='🪑 Empty',status='Offline',checkin_time='-',last_heartbeat=0 WHERE name=?",
            (user,))
    conn.commit(); conn.close()

def add_attendance(staff_name, desk, checkin_time, status):
    conn = get_db()
    conn.execute(
        "INSERT INTO attendance (staff_name,date,desk,checkin_time,status) VALUES (?,?,?,?,?)",
        (staff_name, str(get_dubai_time().date()), desk, checkin_time, status))
    conn.commit(); conn.close()

def checkout_attendance(staff_name, checkout_time):
    conn = get_db()
    conn.execute(
        "UPDATE attendance SET checkout_time=? WHERE staff_name=? AND checkout_time='Active In Office'",
        (checkout_time, staff_name))
    conn.commit(); conn.close()

def get_attendance_df():
    conn = get_db()
    df = pd.read_sql("""
        SELECT staff_name as 'Staff Name', date as 'Date', desk as 'Desk',
               checkin_time as 'Check-In Time', checkout_time as 'Check-Out Time', status as 'Status'
        FROM attendance ORDER BY id DESC""", conn)
    conn.close(); return df

def save_profile_photo(username, photo_bytes):
    conn = get_db()
    conn.execute(
        "INSERT OR REPLACE INTO profiles (username, photo_data) VALUES (?,?)",
        (username, base64.b64encode(photo_bytes).decode("utf-8")))
    conn.commit(); conn.close()

def get_profile_photo(username):
    conn = get_db()
    cur = conn.execute("SELECT photo_data FROM profiles WHERE username=?", (username,))
    row = cur.fetchone(); conn.close()
    return row[0] if row else None

def file_to_base64(b): return base64.b64encode(b).decode("utf-8")

def render_file(file_data, file_name, file_type):
    if file_data and file_name:
        raw = base64.b64decode(file_data)
        if file_type and file_type.startswith("image"):
            st.image(raw, width=200, caption=file_name)
        else:
            st.download_button(f"📎 {file_name}", data=raw, file_name=file_name,
                               key=f"dl_{file_name}_{file_data[:6]}")

def render_chat_messages(msgs, my_name, is_group=False):
    for row in msgs:
        sender = row[0]
        if is_group:
            message = row[1] if row[1] else ""
            ts      = row[2] if row[2] else ""
            fd      = row[3] if len(row) > 3 else None
            fn      = row[4] if len(row) > 4 else None
            ft      = row[5] if len(row) > 5 else None
        else:
            message = row[2] if row[2] else ""
            ts      = row[3] if row[3] else ""
            fd      = row[4] if len(row) > 4 else None
            fn      = row[5] if len(row) > 5 else None
            ft      = row[6] if len(row) > 6 else None
        if sender == my_name:
            st.markdown(
                f'<div class="chat-bubble-me">{message}'
                f'<div class="chat-time" style="text-align:right;">🕒 {ts}</div></div>',
                unsafe_allow_html=True)
        else:
            av = get_avatar_html(sender, 34)
            st.markdown(
                f'<div style="display:flex;align-items:flex-start;gap:8px;margin:4px 10% 4px 0;">'
                f'<div style="flex-shrink:0;margin-top:2px;">{av}</div>'
                f'<div class="chat-bubble-other">'
                f'<div class="chat-sender">{sender}</div>{message}'
                f'<div class="chat-time">🕒 {ts}</div></div></div>',
                unsafe_allow_html=True)
        if fd: render_file(fd, fn, ft)

def send_group_message(sender, message, fd=None, fn=None, ft=None):
    conn = get_db()
    conn.execute(
        "INSERT INTO group_messages (sender,message,timestamp,file_data,file_name,file_type) VALUES (?,?,?,?,?,?)",
        (sender, message or "", get_dubai_time().strftime("%H:%M"), fd, fn, ft))
    conn.commit(); conn.close()

def get_group_messages(limit=50):
    conn = get_db()
    cur = conn.execute(
        "SELECT sender,message,timestamp,file_data,file_name,file_type FROM group_messages ORDER BY id DESC LIMIT ?",
        (limit,))
    msgs = cur.fetchall(); conn.close(); return list(reversed(msgs))

def send_private_message(sender, receiver, message, fd=None, fn=None, ft=None):
    conn = get_db()
    conn.execute(
        "INSERT INTO private_messages (sender,receiver,message,timestamp,file_data,file_name,file_type) VALUES (?,?,?,?,?,?,?)",
        (sender, receiver, message or "", get_dubai_time().strftime("%H:%M"), fd, fn, ft))
    conn.commit(); conn.close()

def get_private_messages(u1, u2, limit=50):
    conn = get_db()
    cur = conn.execute("""
        SELECT sender,receiver,message,timestamp,file_data,file_name,file_type
        FROM private_messages
        WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?)
        ORDER BY id DESC LIMIT ?""", (u1, u2, u2, u1, limit))
    msgs = cur.fetchall(); conn.close(); return list(reversed(msgs))

def get_unread_count(receiver, sender):
    conn = get_db()
    cur = conn.execute(
        "SELECT COUNT(*) FROM private_messages WHERE receiver=? AND sender=? AND is_read=0",
        (receiver, sender))
    n = cur.fetchone()[0]; conn.close(); return n

def mark_as_read(receiver, sender):
    conn = get_db()
    conn.execute(
        "UPDATE private_messages SET is_read=1 WHERE receiver=? AND sender=?",
        (receiver, sender))
    conn.commit(); conn.close()

def get_notice():
    conn = get_db()
    cur = conn.execute("SELECT text,posted_by FROM notice WHERE id=1")
    row = cur.fetchone(); conn.close()
    return {"text": row[0], "by": row[1]}

def update_notice(text, posted_by):
    conn = get_db()
    conn.execute("UPDATE notice SET text=?,posted_by=? WHERE id=1", (text, posted_by))
    conn.commit(); conn.close()

# =========================================================================
# SESSION STATE
# =========================================================================
defaults = {
    "logged_in": False,
    "username": "",
    "user_email": "",
    "chat_with": None,
    "show_photo_panel": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ✅ FIX #10 (cont.): if session_state was reset by a reconnect, but a
# valid "remember me" cookie still exists, silently restore the login
# instead of showing the login page again.
if not st.session_state.logged_in and COOKIES_AVAILABLE:
    cookie_email = cookies.get("pcas_email")
    cookie_name  = cookies.get("pcas_name")
    if cookie_email and cookie_name and cookie_email.endswith(ALLOWED_DOMAIN):
        st.session_state.logged_in  = True
        st.session_state.username   = cookie_name
        st.session_state.user_email = cookie_email

# =========================================================================
# LOGIN PAGE
# =========================================================================
if not st.session_state.logged_in:
    st.write("")
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        with st.form("login_form"):
            if os.path.exists("pcas_logo.png"):
                st.image("pcas_logo.png", width=120)
            st.markdown('<h3 style="color:#1a365d;">PCAS Secure Login Gate</h3>', unsafe_allow_html=True)
            em = st.text_input("Office Email:", placeholder="username@pcas-cert.com").strip().lower()
            pw = st.text_input("Passcode:", type="password", placeholder="••••••••")
            if st.form_submit_button("Verify & Enter Office 🚀", use_container_width=True):
                if not em:
                    st.error("Enter your email!")
                # ✅ FIX #7: endswith() instead of substring `in` check so
                # "user@pcas-cert.com.evil.com" can no longer sneak past.
                elif not em.endswith(ALLOWED_DOMAIN):
                    st.error("❌ Use @pcas-cert.com email only!")
                elif pw != OFFICE_PASSWORD:
                    st.error("❌ Wrong passcode!")
                else:
                    uname = em.split("@")[0].replace(".", " ").title()
                    st.session_state.logged_in  = True
                    st.session_state.username   = uname
                    st.session_state.user_email = em
                    if COOKIES_AVAILABLE:
                        cookies.set("pcas_email", em)
                        cookies.set("pcas_name", uname)
                    st.rerun()
    st.stop()

my_name = st.session_state.username

# =========================================================================
# MAIN APP STARTS HERE
# =========================================================================
update_heartbeat(my_name)
cleanup_disconnected()

# ── HEADER ───────────────────────────────────────────────────────────────
st.markdown('<div class="header-mild-box">', unsafe_allow_html=True)
cl, ct = st.columns([0.08, 0.92])
with cl:
    if os.path.exists("pcas_logo.png"):
        st.image("pcas_logo.png", width=60)
with ct:
    st.markdown('<h1 class="main-title">PCAS VIRTUAL OFFICE v2.0</h1>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

now_dt = get_dubai_time()

# ✅ FIX #9: fetch desks ONCE per rerun and reuse everywhere below,
# instead of calling get_all_desks() three separate times.
desks_df = get_all_desks()

h1, h2, h3, h4 = st.columns([2, 1, 0.8, 0.8])
with h1:
    st.write(f"📅 {now_dt.strftime('%B %d, %Y')} | 🕒 Dubai: {now_dt.strftime('%I:%M %p')}")
with h2:
    hu = desks_df[desks_df["name"] != "🪑 Empty"]["name"].tolist()
    total_unread = sum(get_unread_count(my_name, u) for u in hu if u != my_name)
    if total_unread > 0:
        st.markdown(f'📬 **Inbox** <span class="unread-badge">{total_unread}</span>', unsafe_allow_html=True)
with h3:
    if st.button("📸 My Photo", use_container_width=True):
        st.session_state.show_photo_panel = not st.session_state.show_photo_panel
with h4:
    if st.button("🚪 Logout", use_container_width=True):
        checkout_attendance(my_name, get_dubai_time().strftime("%I:%M %p"))
        clear_user_desk(my_name)
        st.session_state.logged_in = False
        st.session_state.username  = ""
        if COOKIES_AVAILABLE:
            cookies.remove("pcas_email")
            cookies.remove("pcas_name")
        st.rerun()

# ── PHOTO PANEL ──────────────────────────────────────────────────────────
if st.session_state.show_photo_panel:
    st.markdown("---")
    _, pm, _ = st.columns([1, 1.2, 1])
    with pm:
        st.markdown('<div class="photo-panel-box">', unsafe_allow_html=True)
        st.markdown("### 📸 My Profile Photo")
        st.markdown(f'<div style="margin:12px auto;">{get_avatar_html(my_name, size=90)}</div>', unsafe_allow_html=True)
        st.markdown(f'<p style="color:#555;font-weight:bold;">{my_name}</p>', unsafe_allow_html=True)
        new_photo = st.file_uploader("📁 Choose photo (PNG / JPG, max 5MB):", type=["png", "jpg", "jpeg"], key="change_ph")
        if new_photo:
            # ✅ FIX #6: file size guard before saving to DB.
            if new_photo.size > MAX_FILE_SIZE_MB * 1024 * 1024:
                st.error(f"❌ File too large! Max {MAX_FILE_SIZE_MB} MB allowed.")
            else:
                st.markdown("**Preview:**")
                st.image(new_photo, width=110)
                new_photo.seek(0)
                pp1, pp2 = st.columns(2)
                with pp1:
                    if st.button("💾 Save Photo", use_container_width=True, type="primary"):
                        new_photo.seek(0)
                        save_profile_photo(my_name, new_photo.read())
                        st.session_state.show_photo_panel = False
                        st.success("✅ Photo updated!")
                        st.rerun()
                with pp2:
                    if st.button("❌ Cancel", use_container_width=True):
                        st.session_state.show_photo_panel = False; st.rerun()
        else:
            if st.button("❌ Close", use_container_width=True):
                st.session_state.show_photo_panel = False; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")

# ── NOTICE ───────────────────────────────────────────────────────────────
notice = get_notice()
st.markdown(
    f'<div class="notice-box">📢 <b>NOTICE:</b> "{notice["text"]}" '
    f'<span style="float:right;color:#666;font-size:11px;">— {notice["by"]}</span></div>',
    unsafe_allow_html=True)

# ── STATS ────────────────────────────────────────────────────────────────
oc  = len(desks_df[desks_df["status"].str.contains("Online", na=False)])
bc  = len(desks_df[desks_df["status"].str.contains("Busy",   na=False)])
brc = len(desks_df[desks_df["status"].str.contains("Break",  na=False)])
wc  = len(desks_df[desks_df["status"].str.contains("WFH",    na=False)])
ac  = len(desks_df[desks_df["name"] != "🪑 Empty"])

m1, m2, m3, m4, m5 = st.columns(5)
m1.markdown(f'<div class="metric-card"><b style="color:#2ecc71;">🟢 Online</b><h3>{oc}</h3></div>', unsafe_allow_html=True)
m2.markdown(f'<div class="metric-card"><b style="color:#e74c3c;">🔴 Busy</b><h3>{bc}</h3></div>', unsafe_allow_html=True)
m3.markdown(f'<div class="metric-card"><b style="color:#f1c40f;">🟡 Break</b><h3>{brc}</h3></div>', unsafe_allow_html=True)
m4.markdown(f'<div class="metric-card"><b style="color:#3498db;">🔵 WFH</b><h3>{wc}</h3></div>', unsafe_allow_html=True)
m5.markdown(f'<div class="metric-card"><b style="color:#1a365d;">👥 Active</b><h3>{ac}</h3></div>', unsafe_allow_html=True)
st.markdown("---")

# =========================================================================
# TABS
# =========================================================================
tab_office, tab_chat, tab_admin = st.tabs(["🏢 Office Floor", "💬 Messages", "🛠️ Admin"])

# ─── TAB 1: OFFICE FLOOR ─────────────────────────────────────────────────
with tab_office:
    col_ctrl, col_floor = st.columns([1.1, 1.9])

    with col_ctrl:
        st.markdown('<div class="allocation-dark-box">👤 DESK ALLOCATION</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div style="text-align:center;margin-bottom:10px;">'
            f'{get_avatar_html(my_name, 65)}'
            f'<div style="font-weight:bold;font-size:14px;margin-top:6px;">{my_name}</div>'
            f'</div>', unsafe_allow_html=True)
        st.info(f"**{st.session_state.user_email}**")

        desk_options = []
        for _, row in desks_df.iterrows():
            i = int(row["desk_id"])
            dept = ("Manager"      if 1  <= i <= 3  else
                    "Chemical"     if 4  <= i <= 7  else
                    "Mechanical"   if 8  <= i <= 9  else
                    "Electrical"   if 10 <= i <= 14 else
                    "Acct Manager" if 15 <= i <= 17 else
                    "Sales"        if 18 <= i <= 20 else "Accountant")
            if row["name"] == "🪑 Empty" or row["name"] == my_name:
                desk_options.append(f"Desk {i} ({dept})")

        # ✅ FIX #4: guard against an empty desk_options list (would crash
        # on .split() with "None is not subscriptable" once all 22 desks
        # are occupied by other people).
        if desk_options:
            sel_desk = st.selectbox("Select Desk:", desk_options)
            desk_num = int(sel_desk.split(" ")[1])
        else:
            st.warning("😔 No desks available right now. Please wait for one to free up.")
            desk_num = None

        my_status = st.radio("Status:", ["Online 🟢", "Busy/Meeting 🔴", "On Break 🟡", "WFH 🔵"], horizontal=True)

        b1, b2 = st.columns(2)
        with b1:
            if st.button("🚀 Check-In", use_container_width=True, type="primary", disabled=desk_num is None):
                clear_user_desk(my_name)
                ct_str = get_dubai_time().strftime("%I:%M %p")
                update_desk(desk_num, my_name, my_status, ct_str)
                cs = my_status.replace("🟢", "").replace("🔴", "").replace("🟡", "").replace("🔵", "").strip()
                add_attendance(my_name, f"Desk {desk_num}", ct_str, cs)
                st.success("Checked In! ✅"); st.rerun()
        with b2:
            if st.button("🚪 Leave", use_container_width=True):
                checkout_attendance(my_name, get_dubai_time().strftime("%I:%M %p"))
                clear_user_desk(my_name); st.rerun()

        st.markdown("---")
        st.markdown('<div class="groupboard-dark-box">📢 GROUP BOARD</div>', unsafe_allow_html=True)
        st.markdown("**😊 Quick Emoji:**")
        ec = st.columns(len(QUICK_EMOJIS))
        for i, emoji in enumerate(QUICK_EMOJIS):
            with ec[i]:
                if st.button(emoji, key=f"gemoji_{i}", use_container_width=True):
                    send_group_message(my_name, emoji); st.rerun()

        with st.form("group_form", clear_on_submit=True):
            g_msg  = st.text_input("✏️ Message everyone:", placeholder="Type a message...")
            g_file = st.file_uploader(
                f"📎 Attach Image / Doc (max {MAX_FILE_SIZE_MB}MB)",
                type=["png", "jpg", "jpeg", "pdf", "txt", "xlsx", "docx"],
                key="gfile")
            if st.form_submit_button("Send 🌍", use_container_width=True):
                if g_msg or g_file:
                    fd = fn = ft = None
                    blocked = False
                    if g_file:
                        # ✅ FIX #6: size guard for group chat attachments too.
                        if g_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
                            st.error(f"❌ File too large! Max {MAX_FILE_SIZE_MB} MB allowed.")
                            blocked = True
                        else:
                            fd = file_to_base64(g_file.read())
                            fn = g_file.name; ft = g_file.type
                    if not blocked:
                        send_group_message(my_name, g_msg, fd, fn, ft); st.rerun()

        with st.expander("📜 Group Chat", expanded=True):
            render_chat_messages(get_group_messages(30), my_name, is_group=True)

    with col_floor:
        st.subheader("🏢 PCAS Office Floor")
        st.link_button("🚨 JOIN GROUP CALL", "https://meet.google.com/new", type="primary", use_container_width=True)
        st.markdown("---")

        desk_map = {int(r["desk_id"]): r for _, r in desks_df.iterrows()}

        def draw_desks(title, bg, s, e):
            st.markdown(f'<div class="dept-box {bg}">{title}</div>', unsafe_allow_html=True)
            cols = st.columns(e - s + 1)
            for idx, d in enumerate(range(s, e + 1)):
                dd = desk_map[d]
                with cols[idx]:
                    if dd["name"] == "🪑 Empty":
                        st.markdown(
                            f'<div class="status-offline" style="text-align:center;min-height:110px;">'
                            f'<div class="desk-title">Desk {d}</div>'
                            f'<div style="font-size:32px;margin:8px 0;">🪑</div>'
                            f'<span style="font-size:10px;color:#aaa;">Empty</span>'
                            f'</div>', unsafe_allow_html=True)
                    else:
                        ur    = get_unread_count(my_name, dd["name"])
                        badge = f'<span class="unread-badge">{ur}</span>' if ur > 0 else ""
                        st_s  = dd["status"]
                        sc    = ("status-online"  if "Online" in st_s else
                                 "status-busy"    if "Busy"   in st_s else
                                 "status-break"   if "Break"  in st_s else "status-wfh")
                        sicon = ("🟢" if "Online" in st_s else
                                 "🔴" if "Busy"   in st_s else
                                 "🟡" if "Break"  in st_s else "🔵")
                        avatar = get_avatar_html(dd["name"], size=52)
                        st.markdown(
                            f'<div class="{sc}" style="text-align:center;min-height:110px;">'
                            f'<div class="desk-title">Desk {d}</div>'
                            f'<div style="margin:4px auto;">{avatar}</div>'
                            f'<div style="font-size:11px;font-weight:bold;margin-top:3px;">'
                            f'{dd["name"]} {badge}</div>'
                            f'<div style="font-size:10px;color:#555;">{sicon} {st_s}</div>'
                            f'</div>', unsafe_allow_html=True)
                        st.link_button("📞", "https://meet.google.com/new", key=f"call_{d}")
                        if dd["name"] != my_name:
                            if st.button("💬", key=f"chat_{d}", help=f"Chat with {dd['name']}"):
                                st.session_state.chat_with = dd["name"]
                                mark_as_read(my_name, dd["name"]); st.rerun()
                    st.write("")

        draw_desks("💼 MANAGER ROOM (1-3)",     "bg-manager",     1,  3)
        draw_desks("🧪 CHEMICAL TEAM (4-7)",     "bg-chemical",    4,  7)
        draw_desks("🔧 MECHANICAL TEAM (8-9)",   "bg-mechanical",  8,  9)
        draw_desks("⚡ ELECTRICAL TEAM (10-14)", "bg-electrical",  10, 14)
        draw_desks("📊 ACCOUNT MANAGER (15-17)", "bg-acc-manager", 15, 17)
        draw_desks("📈 SALES TEAM (18-20)",      "bg-sales",       18, 20)
        draw_desks("🧮 ACCOUNTANT (21-22)",      "bg-accountant",  21, 22)

# ─── TAB 2: PRIVATE MESSAGES ─────────────────────────────────────────────
with tab_chat:
    st.markdown("### 💬 Private Messages")
    online_users = [r["name"] for _, r in desks_df.iterrows()
                    if r["name"] != "🪑 Empty" and r["name"] != my_name]
    if not online_users:
        st.info("No other staff online right now.")
    else:
        cu, cc = st.columns([1, 2.5])
        with cu:
            st.markdown("**👥 Online Staff:**")
            for user in online_users:
                ur = get_unread_count(my_name, user)
                lb = user + (f" 🔴 {ur}" if ur > 0 else " 🟢")
                if st.button(lb, key=f"sel_{user}", use_container_width=True):
                    st.session_state.chat_with = user
                    mark_as_read(my_name, user); st.rerun()
        with cc:
            target = st.session_state.chat_with
            if target and target in online_users:
                tav = get_avatar_html(target, 42)
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">'
                    f'{tav}<b style="font-size:17px;">{target}</b></div>',
                    unsafe_allow_html=True)
                mark_as_read(my_name, target)
                msgs = get_private_messages(my_name, target)
                if not msgs: st.info("No messages yet. Say hi! 👋")
                render_chat_messages(msgs, my_name, is_group=False)
                st.markdown("---")
                st.markdown("**😊 Quick Emoji:**")
                pec = st.columns(len(QUICK_EMOJIS))
                for i, emoji in enumerate(QUICK_EMOJIS):
                    with pec[i]:
                        if st.button(emoji, key=f"pmemoji_{i}", use_container_width=True):
                            send_private_message(my_name, target, emoji); st.rerun()
                with st.form(f"pm_{target}", clear_on_submit=True):
                    pm_msg  = st.text_input("", placeholder=f"Type to {target}...", label_visibility="collapsed")
                    pm_file = st.file_uploader(
                        f"📎 Attach (max {MAX_FILE_SIZE_MB}MB):",
                        type=["png", "jpg", "jpeg", "pdf", "txt", "xlsx", "docx"],
                        key=f"pmf_{target}")
                    if st.form_submit_button("Send ➤", use_container_width=True):
                        if pm_msg or pm_file:
                            fd = fn = ft = None
                            blocked = False
                            if pm_file:
                                if pm_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
                                    st.error(f"❌ File too large! Max {MAX_FILE_SIZE_MB} MB allowed.")
                                    blocked = True
                                else:
                                    fd = file_to_base64(pm_file.read())
                                    fn = pm_file.name; ft = pm_file.type
                            if not blocked:
                                send_private_message(my_name, target, pm_msg, fd, fn, ft)
                                st.rerun()
            else:
                st.info("👈 Select a staff member to start chatting!")

# ─── TAB 3: ADMIN ────────────────────────────────────────────────────────
with tab_admin:
    st.markdown("### 🛠️ Admin Control Panel")
    ap = st.text_input("Admin Password:", type="password", key="admin_pw")
    if ap == ADMIN_EXTRACT_PASSWORD:
        st.success("🔒 Access Granted!")
        a1, a2 = st.columns(2)
        with a1:
            st.markdown("#### 📢 Notice Board")
            cn = get_notice()
            nn = st.text_area("Announcement:", value=cn["text"])
            if st.button("📢 Broadcast", use_container_width=True):
                update_notice(nn, my_name); st.success("Updated!"); st.rerun()
        with a2:
            st.markdown("#### 🧹 Force Reset Frozen Desks")
            if st.button("🧹 Reset All (except me)", use_container_width=True):
                for _, row in get_all_desks().iterrows():
                    if row["name"] != "🪑 Empty" and row["name"] != my_name:
                        clear_desk(int(row["desk_id"]))
                st.success("Done!"); st.rerun()
        st.markdown("---")
        st.markdown("#### 📥 Attendance Report")
        adf = get_attendance_df()
        if len(adf) > 0:
            csv = adf.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Download CSV", data=csv,
                file_name=f"PCAS_Attendance_{get_dubai_time().strftime('%B_%Y')}.csv",
                mime="text/csv", use_container_width=True)
            st.dataframe(adf, use_container_width=True, hide_index=True)
        else:
            st.warning("No records yet.")
    elif ap:
        st.error("❌ Wrong password!")

# ✅ FIX #1 (cont.): NO manual sleep+rerun here anymore.
# streamlit_autorefresh at the top of the file handles live updates safely.
