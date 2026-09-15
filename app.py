import sqlite3
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import folium
from streamlit_folium import st_folium
from user_guide import render_guide

# 1. PAGE CONFIG & STYLING
st.set_page_config(page_title="AEGIS AI - Secure Shield", layout="wide", page_icon="🛡️")

try:
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# 2. DATABASE INITIALIZATION
conn = sqlite3.connect("safety_logs_v2.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS active_users (
        username TEXT PRIMARY KEY,
        role TEXT,
        lat REAL,
        lon REAL,
        threat_status TEXT,
        last_active TEXT
    )
""")
conn.commit()

# Default Seed Users
cursor.execute("INSERT OR IGNORE INTO active_users VALUES ('admin', 'Admin', 21.1702, 72.8311, 'SAFE', ?)", (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),))
cursor.execute("INSERT OR IGNORE INTO active_users VALUES ('operator_01', 'User', 21.1900, 72.8100, 'SAFE', ?)", (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),))
conn.commit()

# 3. AUTHENTICATION
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.session_state["role"] = None

if not st.session_state["authenticated"]:
    st.markdown("<h1>🛡️ AEGIS AI - SECURE PORTAL</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        username = st.text_input("Username").strip()
        password = st.text_input("Password", type="password").strip()
        if st.button("LOG IN", use_container_width=True):
            if username == "admin" and password == "admin123":
                st.session_state.update({"authenticated": True, "username": "admin", "role": "Admin"})
                st.rerun()
            else:
                # Dynamic User Authentication Check/Registration
                user_rec = cursor.execute("SELECT role FROM active_users WHERE username=?", (username,)).fetchone()
                if user_rec or password == "user123":
                    if not user_rec:
                        cursor.execute("INSERT INTO active_users VALUES (?, 'User', 21.1702, 72.8311, 'SAFE', ?)", 
                                       (username, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                        conn.commit()
                    st.session_state.update({"authenticated": True, "username": username, "role": "User"})
                    st.rerun()
                else:
                    st.error("Invalid Credentials!")
    st.stop()

# 4. SIDEBAR NAVIGATION
st.sidebar.markdown(f"### 👤 Logged User: `{st.session_state['username']}`")
if st.sidebar.button("Logout"):
    st.session_state["authenticated"] = False
    st.rerun()

st.sidebar.markdown("---")
menu = ["📍 My Live GPS & SOS", "📖 User Guide / Manual"]
if st.session_state["role"] == "Admin":
    menu.insert(0, "👑 Master Admin Control (All Users)")

choice = st.sidebar.radio("Navigation", menu)

# ==========================================
# MODULE 1: ADMIN MASTER CONTROL (SABKA DATA)
# ==========================================
if choice == "👑 Master Admin Control (All Users)":
    st.title("👑 Master Command Center - Complete Fleet Visibility")
    
    df_users = pd.read_sql_query("SELECT * FROM active_users", conn)
    threats = df_users[df_users['threat_status'].str.contains("SOS|DANGER|CRITICAL", case=False, na=False)]
    
    if not threats.empty:
        for _, row in threats.iterrows():
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #ef4444, #991b1b); padding: 15px; border-radius: 10px; color: white; font-weight: bold; margin-bottom: 12px;">
                🚨 CRITICAL EMERGENCY ALERT: User '{row['username']}'<br>
                Coordinates: Lat {row['lat']} | Lon {row['lon']} | Time: {row['last_active']}
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown("### 📊 Live Status Database (All System Users)")
    st.dataframe(df_users, use_container_width=True)

    st.markdown("### 🗺️ Master Fleet Map")
    m_all = folium.Map(location=[21.1702, 72.8311], zoom_start=12, tiles="CartoDB dark_matter")
    for _, u in df_users.iterrows():
        color = "red" if "SOS" in u['threat_status'] else "blue"
        folium.Marker(
            [u['lat'], u['lon']], 
            popup=f"<b>User: {u['username']}</b><br>Status: {u['threat_status']}<br>Time: {u['last_active']}",
            tooltip=f"{u['username']} ({u['threat_status']})",
            icon=folium.Icon(color=color, icon="info-sign")
        ).add_to(m_all)
    st_folium(m_all, width="100%", height=450)

# ==========================================
# MODULE 2: USER PRIVATE DASHBOARD (SIRF MERA DATA)
# ==========================================
elif choice == "📍 My Live GPS & SOS":
    current_u = st.session_state["username"]
    st.title(f"📍 Private Console - {current_u}")
    
    c_map, c_control = st.columns([2, 1])
    
    # Query ONLY the logged-in user's data
    user_data = cursor.execute("SELECT lat, lon, threat_status, last_active FROM active_users WHERE username=?", (current_u,)).fetchone()
    u_lat = user_data[0] if user_data else 21.1702
    u_lon = user_data[1] if user_data else 72.8311
    u_status = user_data[2] if user_data else "SAFE"
    u_time = user_data[3] if user_data else datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with c_control:
        st.markdown("### 🔒 Personal Dispatch Controls")
        st.info(f"My Status: **{u_status}**\nLast Sync: `{u_time}`")

        loc_html = """
        <script>
        function getLocation() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(showPosition);
            }
        }
        function showPosition(position) {
            alert("Location Detected:\\nLat: " + position.coords.latitude + "\\nLon: " + position.coords.longitude);
        }
        </script>
        <button onclick="getLocation()" style="background-color: #00F2FE; color: #0F172A; padding: 10px 18px; border: none; border-radius: 8px; font-weight: bold; width: 100%; cursor: pointer;">
            🎯 Detect My GPS Location
        </button>
        """
        components.html(loc_html, height=55)

        st.markdown("---")
        manual_lat = st.number_input("My Latitude", value=float(u_lat), format="%.6f")
        manual_lon = st.number_input("My Longitude", value=float(u_lon), format="%.6f")
        
        if st.button("📍 Update My Coordinates"):
            now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("UPDATE active_users SET lat=?, lon=?, last_active=? WHERE username=?", 
                           (manual_lat, manual_lon, now_time, current_u))
            conn.commit()
            st.success("Your coordinates have been updated.")
            st.rerun()

        st.markdown("---")
        if st.button("🚨 TRIGGER MY SOS", type="primary"):
            now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("UPDATE active_users SET threat_status='CRITICAL SOS DANGER', last_active=? WHERE username=?", 
                           (now_time, current_u))
            conn.commit()
            st.error("EMERGENCY BROADCAST TRANSMITTED TO ADMIN!")
            st.rerun()

        if st.button("✅ Set Status to SAFE"):
            now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("UPDATE active_users SET threat_status='SAFE', last_active=? WHERE username=?", 
                           (now_time, current_u))
            conn.commit()
            st.success("Status set to SAFE.")
            st.rerun()

    with c_map:
        st.markdown("### 🗺️ My Isolated Location Map")
        # Render map showing ONLY the current logged-in user
        m_single = folium.Map(location=[u_lat, u_lon], zoom_start=14, tiles="CartoDB dark_matter")
        color = "red" if "SOS" in u_status else "blue"
        folium.Marker(
            [u_lat, u_lon], 
            popup=f"<b>My Unit: {current_u}</b><br>Status: {u_status}<br>Time: {u_time}",
            tooltip=f"{current_u} (My Unit)",
            icon=folium.Icon(color=color, icon="user")
        ).add_to(m_single)
            
        st_folium(m_single, width="100%", height=500)

# ==========================================
# MODULE 3: USER GUIDE
# ==========================================
elif choice == "📖 User Guide / Manual":
    render_guide()