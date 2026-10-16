import streamlit as st
import json
import os
from datetime import datetime

DATA_FILE = "notifications.json"
SMS_LOG_FILE = "sms_log.json"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "campus123"  # simple hardcoded login for demo purposes

st.set_page_config(page_title="Campus Sync", page_icon="📢", layout="wide")


# ---------- Data helpers ----------
def load_json(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def add_notification(title, message, ntype):
    notifications = load_json(DATA_FILE)
    entry = {
        "id": len(notifications) + 1,
        "title": title,
        "message": message,
        "type": ntype,  # "Routine" or "Emergency"
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    notifications.insert(0, entry)  # newest first
    save_json(DATA_FILE, notifications)

    if ntype == "Emergency":
        send_simulated_sms(entry)

    return entry


def send_simulated_sms(entry):
    """
    Simulates sending an SMS blast for emergency notifications.
    In a full production version this would call a real SMS gateway
    (e.g. Africa's Talking, Twilio). For this project it logs the
    'sent' message so the behaviour can be demonstrated and verified.
    """
    sms_log = load_json(SMS_LOG_FILE)
    sms_log.insert(0, {
        "notification_id": entry["id"],
        "message_sent": f"[EMERGENCY] {entry['title']}: {entry['message']}",
        "sent_at": entry["timestamp"],
        "recipients": "All registered student & staff numbers (simulated)",
    })
    save_json(SMS_LOG_FILE, sms_log)


# ---------- UI ----------
st.title("📢 Campus Sync")
st.caption("A unified platform for routine campus announcements and emergency alerts")

page = st.sidebar.radio("Navigate", ["Student View", "Admin Login"])

# ---------------- STUDENT VIEW ----------------
if page == "Student View":
    st.subheader("Campus Notifications")

    notifications = load_json(DATA_FILE)

    if not notifications:
        st.info("No notifications yet. Check back soon.")
    else:
        for n in notifications:
            if n["type"] == "Emergency":
                st.error(f"🚨 **EMERGENCY: {n['title']}**\n\n{n['message']}\n\n*Posted: {n['timestamp']}*")
            else:
                st.info(f"📌 **{n['title']}**\n\n{n['message']}\n\n*Posted: {n['timestamp']}*")

# ---------------- ADMIN VIEW ----------------
elif page == "Admin Login":
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.subheader("Admin Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid credentials.")
        st.caption("Demo credentials — admin / campus123")

    else:
        st.subheader("Admin Dashboard")
        st.success("Logged in as central admin")

        with st.form("post_notification", clear_on_submit=True):
            title = st.text_input("Title")
            message = st.text_area("Message")
            ntype = st.selectbox("Type", ["Routine", "Emergency"])
            submitted = st.form_submit_button("Post Notification")

            if submitted:
                if title and message:
                    add_notification(title, message, ntype)
                    if ntype == "Emergency":
                        st.success("Emergency notification posted and SMS blast simulated.")
                    else:
                        st.success("Notification posted.")
                else:
                    st.warning("Please fill in both title and message.")

        st.divider()
        st.subheader("Posted Notifications")
        notifications = load_json(DATA_FILE)
        st.write(f"Total: {len(notifications)}")
        for n in notifications:
            st.write(f"**[{n['type']}] {n['title']}** — {n['timestamp']}")
            st.caption(n["message"])

        st.divider()
        st.subheader("Simulated SMS Log (Emergency Alerts)")
        sms_log = load_json(SMS_LOG_FILE)
        if sms_log:
            for s in sms_log:
                st.text(f"[{s['sent_at']}] {s['message_sent']}  -> {s['recipients']}")
        else:
            st.caption("No emergency SMS sent yet.")

        if st.button("Log out"):
            st.session_state.logged_in = False
            st.rerun()