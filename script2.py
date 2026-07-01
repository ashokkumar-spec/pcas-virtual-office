import streamlit as st
import datetime
import pandas as pd

# 📱 🏛️ ஆப் பெயர் மற்றும் பிரீமியம் செட்டப்
st.set_page_config(
    page_title="PCAS VIRTUAL OFFICE", 
    page_icon="🛡️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* 📱 💻 மொபைல் மற்றும் கம்ப்யூட்டர் இரண்டிற்கும் ஏத்த குளோபல் ஸ்டைல்ஸ் */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }

    /* 🏛️ 🔵 மெயின் ஹெடருக்கான Mild Color பாக்ஸ் */
    .header-mild-box {
        background-color: #ebf5fb !important;
        border: 1px solid #d6eaf8 !important;
        border-radius: 12px !important;
        padding: 12px 18px !important;
        margin-bottom: 20px !important;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.03) !important;
    }
    
    .main-title {
        font-size: 28px !important;
        font-weight: 800 !important;
        color: #1a365d !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .dept-box {
        border-radius: 8px;
        padding: 10px;
        margin-top: 10px;
        margin-bottom: 10px;
        text-align: center;
        font-weight: bold;
        color: #ffffff;
        font-size: 14px;
    }
    .bg-manager { background-color: #2c3e50; }
    .bg-chemical { background-color: #16a085; }
    .bg-mechanical { background-color: #2980b9; }
    .bg-electrical { background-color: #d35400; }
    .bg-acc-manager { background-color: #8e44ad; }
    .bg-sales { background-color: #27ae60; }
    .bg-accountant { background-color: #c0392b; }

    .status-online { background-color: #e8f8f5; border-left: 5px solid #2ecc71; border-radius: 6px; padding: 10px; text-align: center; box-shadow: 0px 2px 4px rgba(0,0,0,0.05); }
    .status-busy { background-color: #fce4d6; border-left: 5px solid #e74c3c; border-radius: 6px; padding: 10px; text-align: center; box-shadow: 0px 2px 4px rgba(0,0,0,0.05); }
    .status-break { background-color: #fef9e7; border-left: 5px solid #f1c40f; border-radius: 6px; padding: 10px; text-align: center; box-shadow: 0px 2px 4px rgba(0,0,0,0.05); }
    .status-wfh { background-color: #ebf5fb; border-left: 5px solid #3498db; border-radius: 6px; padding: 10px; text-align: center; box-shadow: 0px 2px 4px rgba(0,0,0,0.05); }
    .status-offline { background-color: #f4f6f7; border-left: 5px solid #95a5a6; border-radius: 6px; padding: 10px; text-align: center; }

    .desk-title { font-size: 12px; font-weight: bold; color: #2c3e50; margin-bottom: 3px; }
    .metric-card { background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 12px; text-align: center; box-shadow: 0px 2px 5px rgba(0,0,0,0.05); }
    .notice-box { background-color: #fff3cd; border: 1px solid #ffeba2; border-left: 6px solid #ffc107; border-radius: 6px; padding: 12px; margin-bottom: 15px; font-size: 14px; }

    /* 🎨 சாட் பேக்ரவுண்ட் கண்டெய்னர்கள் */
    .group-chat-container { 
        background-color: #fef9e7 !important; 
        border: none !important; 
        border-radius: 14px !important; 
        padding: 15px !important; 
        margin-top: 12px !important; 
        box-shadow: 0px 4px 12px rgba(0,0,0,0.05) !important; 
    }
    .private-chat-container { 
        background-color: #fbf5f3 !important; 
        border: none !important; 
        border-radius: 14px !important; 
        padding: 15px !important; 
        margin-top: 15px !important; 
        box-shadow: 0px 4px 12px rgba(0,0,0,0.05) !important; 
    }
    
    .group-dark-box { background-color: #b7950b !important; border-radius: 10px !important; padding: 12px !important; text-align: center !important; color: #ffffff !important; font-size: 16px !important; font-weight: bold !important; margin-bottom: 12px !important; }
    .private-dark-box { background-color: #a04000 !important; border-radius: 10px !important; padding: 12px !important; text-align: center !important; color: #ffffff !important; font-size: 16px !important; font-weight: bold !important; margin-bottom: 12px !important; }
    .allocation-dark-box { background-color: #4a235a !important; border-radius: 10px !important; padding: 12px !important; text-align: center !important; color: #ffffff !important; font-size: 16px !important; font-weight: bold !important; margin-bottom: 15px !important; }

    /* மொபைல் ஆப்டிமைசேஷன் */
    @media (max-width: 768px) {
        .main-title { font-size: 22px !important; }
        .header-mild-box { padding: 10px !important; margin-bottom: 15px !important; }
        .stButton > button { width: 100% !important; padding: 12px !important; font-size: 16px !important; }
        [data-testid="stHorizontalBlock"] { flex-direction: column !important; gap: 10px !important; }
        .status-online, .status-busy, .status-break, .status-wfh, .status-offline { margin-bottom: 8px !important; padding: 12px !important; }
    }
</style>
""", unsafe_allow_html=True)

# 🔑 செக்யூரிட்டி பாஸ்கோடு செட்டப்
OFFICE_PASSWORD = "PCAS@2026"
ADMIN_EXTRACT_PASSWORD = "ADMIN@PCAS"

# 🌍 🇦🇪 துபாய் நேரத்தை (Dubai Time - GST) கணக்கிடும் மேஜிக் பங்க்ஷன்
def get_dubai_time():
    # சர்வர் நேரத்துடன் 4 மணிநேரம் கூட்டி துபாய் நேரமாக மாற்றுகிறோம்
    utc_now = datetime.datetime.utcnow()
    dubai_offset = datetime.timedelta(hours=4)
    dubai_now = utc_now + dubai_offset
    return dubai_now

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# 🔒 செக்யூர் லாகின் விண்டோ
if not st.session_state.logged_in:
    st.write("")
    st.write("")
    col_l1, col_l2, col_l3 = st.columns([1, 1.2, 1])
    with col_l2:
        with st.form(key="login_form"):
            st.image("pcas_logo.png", width=120)
            st.markdown('<h3 style="color: #1a365d; font-family: sans-serif; margin-top: -10px;">Secure Login Gate</h3>', unsafe_allow_html=True)
            
            input_user = st.text_input("Enter Your Name:", placeholder="e.g., ashokkumar").strip()
            input_pass = st.text_input("Enter Office Secret Passcode:", type="password", placeholder="••••••••")
            
            login_btn = st.form_submit_button("Verify & Enter Office 🚀", use_container_width=True)
            
            if login_btn:
                if input_user == "":
                    st.error("Please enter your name!")
                elif input_pass == OFFICE_PASSWORD:
                    st.session_state.logged_in = True
                    st.session_state.username = input_user
                    st.success("Access Granted!")
                    st.rerun()
                else:
                    st.error("❌ Incorrect Office Passcode! Access Denied.")
    st.stop()

my_name = st.session_state.username

# 💾 குளோபல் மெமரி சிஸ்டம் (டேட்டாபேஸ்)
@st.cache_resource
def get_global_office_db():
    return {i: {"name": "🪑 Empty", "status": "Offline", "checkin_time": "-"} for i in range(1, 23)}

@st.cache_resource
def get_global_message_db(): return []
@st.cache_resource
def get_global_notice_db(): return {"text": "Welcome to PCAS Virtual Office! Stay Connected.", "by": "Admin"}
@st.cache_resource
def get_global_attendance_log():
    # ஆரம்ப சாம்பிள் டேட்டாக்கள் (இனிமேல் துபாய் நேரப்படி அழகாக விழும்)
    return [
        {"Staff Name": "ashokkumar", "Date": str(get_dubai_time().date()), "Desk": "Desk 1", "Check-In Time": "09:15 AM", "Check-Out Time": "Active In Office", "Status": "Online"},
        {"Staff Name": "Ramesh", "Date": str(get_dubai_time().date()), "Desk": "Desk 4", "Check-In Time": "09:30 AM", "Check-Out Time": "Active In Office", "Status": "Online"}
    ]

office_desks = get_global_office_db()
all_messages = get_global_message_db()
notice_board = get_global_notice_db()
attendance_log = get_global_attendance_log()

if "chat_with_user" not in st.session_state: st.session_state.chat_with_user = None
COMMON_GROUP_MEET_URL = "https://meet.google.com/new"

# 🏛️ லோகோ + பெயர் செட்டப்
st.markdown('<div class="header-mild-box">', unsafe_allow_html=True)
col_logo_native, col_title_native = st.columns([0.08, 0.92])
with col_logo_native: st.image("pcas_logo.png", width=60)
with col_title_native: st.markdown('<h1 class="main-title">PCAS VIRTUAL OFFICE</h1>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# 🏢 மெயின் லேஅவுட் தொடக்கம்
current_dubai_datetime = get_dubai_time()
col_top1, col_top2 = st.columns([2, 1])
with col_top1: st.write(f"📅 Today: {current_dubai_datetime.strftime('%B %d, %Y')} | 🕒 Dubai Live Time: {current_dubai_datetime.strftime('%I:%M %p')}")
with col_top2:
    if st.button("🚪 Logout From Office", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

st.markdown("---")
st.markdown(f'<div class="notice-box">📢 <b>OFFICE NOTICE BOARD:</b> "{notice_board["text"]}" <span style="float:right; color:#666; font-size:11px;">- Posted by {notice_board["by"]}</span></div>', unsafe_allow_html=True)

# 📊 லைவ் ஓவர்வியூ டேஷ்போர்டு
active_staff = []; online_count = 0; busy_count = 0; break_count = 0; wfh_count = 0
for idx, data in office_desks.items():
    if data["name"] != "🪑 Empty":
        active_staff.append(data["name"])
        if "Online" in data["status"]: online_count += 1
        elif "Busy" in data["status"]: busy_count += 1
        elif "Break" in data["status"]: break_count += 1
        elif "WFH" in data["status"]: wfh_count += 1

st.markdown("### 📊 Live Management Overview")
m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
m_col1.markdown(f'<div class="metric-card"><b style="color:#2ecc71; font-size:12px;">🟢 Online Staff</b><h4>{online_count}</h4></div>', unsafe_allow_html=True)
m_col2.markdown(f'<div class="metric-card"><b style="color:#e74c3c; font-size:12px;">🔴 Busy / Meeting</b><h4>{busy_count}</h4></div>', unsafe_allow_html=True)
m_col3.markdown(f'<div class="metric-card"><b style="color:#f1c40f; font-size:12px;">🟡 On Break</b><h4>{break_count}</h4></div>', unsafe_allow_html=True)
m_col4.markdown(f'<div class="metric-card"><b style="color:#3498db; font-size:12px;">🔵 WFH Staff</b><h4>{wfh_count}</h4></div>', unsafe_allow_html=True)
m_col5.markdown(f'<div class="metric-card"><b style="color:#1a365d; font-size:12px;">👥 Total Active</b><h4>{len(active_staff)}</h4></div>', unsafe_allow_html=True)

st.write("")
with st.expander("🛠️ Manager & Admin Control Panel (Notice & Attendance Report)", expanded=False):
    col_adm1, col_adm2 = st.columns([1.5, 1.5])
    with col_adm1:
        st.markdown("##### 📢 Broadcast Notice")
        new_notice = st.text_input("Type new announcement here:", value=notice_board["text"])
        if st.button("📢 Broadcast Notice to Everyone"):
            notice_board["text"] = new_notice
            notice_board["by"] = my_name
            st.success("Notice updated!")
            st.rerun()
            
    with col_adm2:
        st.markdown("##### 📥 Monthly Attendance Report Extractor")
        st.write("Click below to download the complete attendance log of this month as a standard CSV spreadsheet file.")
        
        admin_pass_input = st.text_input(
            "Verification Required: Enter Admin Password to Download", 
            type="password", 
            placeholder="Enter admin code...", 
            key="local_admin_password_field"
        )
        
        if admin_pass_input == ADMIN_EXTRACT_PASSWORD:
            st.success("🔒 Access Granted! Download button unlocked.")
            if len(attendance_log) > 0:
                df_report = pd.DataFrame(attendance_log)
                csv_data = df_report.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Attendance Report (.csv)",
                    data=csv_data,
                    file_name=f"PCAS_Attendance_Report_{get_dubai_time().strftime('%B_%Y')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="local_download_button_trigger"
                )
            else:
                st.warning("No attendance records found yet!")
        elif admin_pass_input != "":
            st.error("❌ Invalid Admin Password! Document locked.")

st.markdown("---")
col_control, col_floor_plan = st.columns([1.1, 1.9])

# இடது பக்கம் கண்ட்ரோல் & சாட் விண்டோ
with col_control:
    st.markdown('<div class="allocation-dark-box">👤 STAFF LOGIN & DESK ALLOCATION</div>', unsafe_allow_html=True)
    st.info(f"Logged in as: **{my_name}**")

    desk_options = []
    for i in range(1, 23):
        if 1 <= i <= 3: dept = "Manager"
        elif 4 <= i <= 7: dept = "Chemical Team"
        elif 8 <= i <= 9: dept = "Mechanical Team"
        elif 10 <= i <= 14: dept = "Electrical Team"
        elif 15 <= i <= 17: dept = "Account Manager"
        elif 18 <= i <= 20: dept = "Sales Team"
        else: dept = "Accountant"

        if office_desks[i]["name"] == "🪑 Empty" or office_desks[i]["name"] == my_name:
            desk_options.append(f"Desk {i} ({dept})")

    selected_desk_str = st.selectbox("Select Your Department Desk:", desk_options)
    desk_num = int(selected_desk_str.split(" ")[1])
    my_status = st.radio("Your Status:", ["Online 🟢", "Busy/Meeting 🔴", "On Break 🟡", "WFH 🔵"], horizontal=True)

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🚀 Occupy Desk & Check-In", use_container_width=True):
            # பழைய சீட்டை காலி செய்தல்
            for i, val in list(office_desks.items()):
                if val["name"] == my_name: office_desks[i] = {"name": "🪑 Empty", "status": "Offline", "checkin_time": "-"}
            
            # துபாய் நேரப்படி செக்-இன் செய்தல்
            dubai_time_str = get_dubai_time().strftime("%I:%M %p")
            office_desks[desk_num] = {"name": my_name, "status": my_status, "checkin_time": dubai_time_str}
            
            # எக்செல் காக இமோஜிகளை நீக்கி சுத்தமான எழுத்துக்களை மட்டும் சேர்க்கிறோம்
            clean_status = my_status.replace("🟢","").replace("🔴","").replace("🟡","").replace("🔵","").strip()
            
            attendance_log.append({
                "Staff Name": my_name,
                "Date": str(get_dubai_time().date()),
                "Desk": f"Desk {desk_num}",
                "Check-In Time": dubai_time_str,
                "Check-Out Time": "Active In Office", # 👈 இன்னும் வெளியேறவில்லை
                "Status": clean_status
            })
            st.success(f"Checked-In successfully at Dubai Time: {dubai_time_str}!")
            st.rerun()
            
    with col_btn2:
        if st.button("🚪 Leave Desk", use_container_width=True):
            checkout_time_str = get_dubai_time().strftime("%I:%M %p")
            
            # மெமரி லாகில் இந்த குறிப்பிட்ட ஸ்டாஃபின் செக்-அவுட் நேரத்தை அப்டேட் செய்தல்
            for row in reversed(attendance_log):
                if row["Staff Name"] == my_name and row["Check-Out Time"] == "Active In Office":
                    row["Check-Out Time"] = checkout_time_str
                    break
            
            # டெஸ்க்கை காலி செய்தல்
            for i, val in list(office_desks.items()):
                if val["name"] == my_name: office_desks[i] = {"name": "🪑 Empty", "status": "Offline", "checkin_time": "-"}
                
            st.success(f"Checked-Out successfully at Dubai Time: {checkout_time_str}!")
            st.rerun()

    st.markdown("---")
    
    # 📢 குரூப் சாட் போர்டு
    st.markdown('<div class="group-chat-container"><div class="group-dark-box">📢 GROUP COMMON BOARD</div>', unsafe_allow_html=True)
    with st.form(key="group_chat_form", clear_on_submit=True):
        group_input = st.text_input("Message to everyone:")
        uploaded_file = st.file_uploader("Share Photo/File 📎", type=["png", "jpg", "jpeg", "pdf", "txt", "xlsx"], key="group_file")
        submit_group = st.form_submit_button("Broadcast 🌍", use_container_width=True)
        if submit_group and (group_input or uploaded_file):
            f_data = uploaded_file.read() if uploaded_file else None
            f_name = uploaded_file.name if uploaded_file else None
            all_messages.append({"sender": my_name, "receiver": "Everyone", "text": group_input, "file": f_data, "file_name": f_name, "time": get_dubai_time().strftime("%H:%M")})
            st.rerun()
    with st.expander("📜 View Group Logs", expanded=True):
        for msg in reversed(all_messages):
            if msg["receiver"] == "Everyone":
                st.markdown(f"`{msg['time']}` **{msg['sender']}**: {msg['text'] if msg['text'] else ''}")
                if msg.get("file") is not None:
                    if msg["file_name"].lower().endswith(('.png', '.jpg', '.jpeg')): st.image(msg["file"], width=200)
                    else: st.download_button(f"📥 Download {msg['file_name']}", data=msg["file"], file_name=msg["file_name"], key=f"g_dl_{msg['time']}")
    st.markdown('</div>', unsafe_allow_html=True)

    # 🔒 பிரைவேட் தனிநபர் சாட் ரூம்
    if st.session_state.chat_with_user:
        target_user = st.session_state.chat_with_user
        if target_user != my_name:
            st.markdown('<div class="private-chat-container"><div class="private-dark-box">🔒 PRIVATE CHAT ROOM</div>', unsafe_allow_html=True)
            with st.form(key=f"p_form_{target_user}", clear_on_submit=True):
                chat_input = st.text_input(f"Write message to {target_user}:")
                if st.form_submit_button("Send Private Message 📤") and chat_input:
                    all_messages.append({"sender": my_name, "receiver": target_user, "text": chat_input, "time": get_dubai_time().strftime("%H:%M")})
                    st.rerun()
            if st.button("❌ Close Private Chat", use_container_width=True):
                st.session_state.chat_with_user = None
                st.rerun()
            for msg in reversed(all_messages):
                if msg["sender"] == my_name and msg["receiver"] == target_user:
                    st.markdown(f"`{msg['time']}` 📤 *To {target_user}:* {msg['text']}")
                elif msg["sender"] == target_user and msg["receiver"] == my_name:
                    st.markdown(f"`{msg['time']}` 📥 *From {target_user}:* **{msg['text']}**")
            st.markdown('</div>', unsafe_allow_html=True)

# வலது பக்கம் டிபார்ட்மென்ட் லேஅவுட் (Floor Plan)
with col_floor_plan:
    st.subheader("📢 PCAS Collaboration Hub")
    st.link_button("🚨 JOIN OFFICE GROUP CALL (ALL ONLINE STAFF)", COMMON_GROUP_MEET_URL, type="primary", use_container_width=True)
    st.markdown("---")

    def draw_desks(title, bg_class, start_idx, end_idx):
        st.markdown(f'<div class="dept-box {bg_class}">{title}</div>', unsafe_allow_html=True)
        cols = st.columns(end_idx - start_idx + 1)
        for idx, d_num in enumerate(range(start_idx, end_idx + 1)):
            d_data = office_desks[d_num]
            with cols[idx]:
                if d_data["name"] == "🪑 Empty":
                    st.markdown(f'<div class="status-offline"><div class="desk-title">Desk {d_num}</div>🪑 Empty</div>', unsafe_allow_html=True)
                else:
                    if "Online" in d_data["status"]: style_class = "status-online"
                    elif "Busy" in d_data["status"]: style_class = "status-busy"
                    elif "Break" in d_data["status"]: style_class = "status-break"
                    else: style_class = "status-wfh"

                    st.markdown(f'<div class="{style_class}"><div class="desk-title">Desk {d_num}</div>👤 <b>{d_data["name"]}</b><br>{d_data["status"]}</div>', unsafe_allow_html=True)
                    st.link_button("🎛️ Call", "https://meet.google.com/new", key=f"lnk_{d_num}")
                    if st.button("💬 Chat", key=f"cb_{d_num}"):
                        st.session_state.chat_with_user = d_data["name"]
                        st.rerun()
        st.write("")

    draw_desks("💼 MANAGER ROOM (Desks 1-3)", "bg-manager", 1, 3)
    draw_desks("🧪 CHEMICAL TEAM (Desks 4-7)", "bg-chemical", 4, 7)
    draw_desks("🔧 MECHANICAL TEAM (Desks 8-9)", "bg-mechanical", 8, 9)
    draw_desks("⚡ ELECTRICAL TEAM (Desks 10-14)", "bg-electrical", 10, 14)
    draw_desks("📊 ACCOUNT MANAGER (Desks 15-17)", "bg-acc-manager", 15, 17)
    draw_desks("📈 SALES TEAM (Desks 18-20)", "bg-sales", 18, 20)
    draw_desks("🧮 ACCOUNTANT (Desks 21-22)", "bg-accountant", 21, 22)
