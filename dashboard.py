import streamlit as st
import pandas as pd
import os
import shutil
from PIL import Image
import subprocess

# =========================
# CONFIG
# =========================
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "svecw"

LOG_FILE = "logs/log.csv"
IMG_DIR = "logs/intruder_images"
DATASET_DIR = "dataset/authorized"

st.set_page_config(
    page_title="AI Intrusion Control Panel",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# MODERN CYBER CSS
# =========================
st.markdown("""
<style>

/* ===== GLOBAL TEXT COLOR FIX ===== */
html, body, [class*="css"]  {
    color: white !important;
}

/* App Background */
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #111827 !important;
    border-right: 1px solid #2d3748;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

/* Input Labels */
label, .stTextInput label, .stFileUploader label {
    color: white !important;
}

/* Radio & Selectbox */
div[role="radiogroup"] label,
div[data-baseweb="select"] *,
div[data-baseweb="select"] span {
    color: white !important;
}

/* Dataframe text */
[data-testid="stDataFrame"] * {
    color: white !important;
}

/* Main Title */
.main-title {
    font-size: 34px;
    font-weight: 700;
    background: linear-gradient(90deg, #00c6ff, #0072ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 20px;
}

/* Section Title */
.section-title {
    font-size: 22px;
    font-weight: 600;
    margin-top: 30px;
    margin-bottom: 15px;
    color: #00c6ff;
}

/* Card */
.card {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    padding: 25px;
    border-radius: 15px;
    border: 1px solid rgba(255,255,255,0.1);
    margin-bottom: 20px;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #0072ff, #00c6ff);
    color: white !important;
    border-radius: 8px;
    height: 45px;
    font-weight: 600;
    border: none;
    transition: 0.3s;
}

.stButton > button:hover {
    transform: scale(1.05);
    box-shadow: 0px 0px 15px rgba(0,198,255,0.5);
}

/* Metrics */
div[data-testid="metric-container"] {
    background: rgba(255, 255, 255, 0.07);
    padding: 20px;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.1);
    color: white !important;
}

</style>
""", unsafe_allow_html=True)

# =========================
# SESSION INIT
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


# =========================
# LOGIN PAGE
# =========================
def login_page():
    st.markdown("<div class='main-title'>🛡 AI Intrusion Control Panel</div>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid Credentials")

    st.markdown("</div>", unsafe_allow_html=True)


# =========================
# DASHBOARD PAGE
# =========================
def dashboard_page():
    st.markdown("<div class='main-title'>📊 System Overview</div>", unsafe_allow_html=True)

    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)
        total_intrusions = len(df)
    else:
        total_intrusions = 0

    if os.path.exists(DATASET_DIR):
        total_staff = len(os.listdir(DATASET_DIR))
    else:
        total_staff = 0

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Intrusions", total_intrusions)
    col2.metric("Registered Staff", total_staff)
    col3.metric("System Status", "🟢 Active")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>Latest Intruder</div>", unsafe_allow_html=True)

    if os.path.exists(IMG_DIR):
        images = sorted(os.listdir(IMG_DIR))
        if images:
            latest = os.path.join(IMG_DIR, images[-1])
            st.image(Image.open(latest), width=420)
        else:
            st.info("No intrusions recorded yet.")


# =========================
# STAFF PAGE
# =========================
def staff_page():
    st.markdown("<div class='main-title'>👤 Staff Management</div>", unsafe_allow_html=True)

    # Add Staff
    st.markdown("<div class='section-title'>Add Staff</div>", unsafe_allow_html=True)
    person_name = st.text_input("Staff Name")
    uploaded_files = st.file_uploader(
        "Upload Images",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )

    if st.button("Save Staff"):
        if person_name and uploaded_files:
            person_path = os.path.join(DATASET_DIR, person_name)
            os.makedirs(person_path, exist_ok=True)

            for file in uploaded_files:
                with open(os.path.join(person_path, file.name), "wb") as f:
                    f.write(file.getbuffer())

            st.success("Staff Added Successfully")

    st.markdown("---")

    # Delete Staff
    st.markdown("<div class='section-title'>Delete Staff</div>", unsafe_allow_html=True)

    if os.path.exists(DATASET_DIR):
        staff_list = os.listdir(DATASET_DIR)
    else:
        staff_list = []

    if staff_list:
        selected_staff = st.selectbox("Select Staff", staff_list)

        if st.button("Delete Staff"):
            shutil.rmtree(os.path.join(DATASET_DIR, selected_staff))
            st.success("Staff Deleted")
    else:
        st.info("No staff available.")

    st.markdown("---")

    # Regenerate Embeddings
    if st.button("🔄 Regenerate Embeddings"):
        subprocess.run(["python", "generate_embeddings.py"])
        st.success("Embeddings Updated Successfully")


# =========================
# LOGS PAGE
# =========================
def logs_page():
    st.markdown("<div class='main-title'>📜 Intrusion Logs</div>", unsafe_allow_html=True)

    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No logs available.")


# =========================
# MAIN APP FLOW
# =========================
if not st.session_state.logged_in:
    login_page()
else:
    st.sidebar.title("🛡 Security Panel")
    page = st.sidebar.radio("Navigation", ["Dashboard", "Staff", "Logs"])

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    if page == "Dashboard":
        dashboard_page()
    elif page == "Staff":
        staff_page()
    elif page == "Logs":
        logs_page()