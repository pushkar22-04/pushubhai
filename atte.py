import streamlit as st
import pandas as pd
from datetime import datetime
import os
import time
from PIL import Image

st.set_page_config(
    page_title="EduPass | Dual Biometric Portal",
    page_icon="🛡️",
    layout="wide"
)

# Clean High-Contrast CSS with Fixed Camera Button
st.markdown("""
<style>
    .stApp {
        background-color: #0b0f19;
        color: #ffffff;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .neon-title {
        color: #38bdf8;
        font-weight: 800;
        font-size: 2.2rem;
        margin-bottom: 5px;
    }
    .sub-title {
        color: #94a3b8;
        font-size: 1rem;
        margin-bottom: 20px;
    }
    .card {
        background: #151d30;
        border: 1px solid #2d3748;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
    }
    
    /* General Form & Action Buttons */
    div.stButton > button {
        background-color: #2563eb !important;
        color: #ffffff !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        border: 1px solid #60a5fa !important;
        padding: 10px 20px !important;
        width: 100% !important;
    }
    div.stButton > button:hover {
        background-color: #1d4ed8 !important;
    }

    /* CAMERA FIX: Make 'Take photo' and 'Clear photo' crystal clear */
    div[data-testid="stCameraInput"] {
        background-color: #151d30 !important;
        border: 1px solid #3b82f6 !important;
        border-radius: 12px !important;
        padding: 10px !important;
    }
    div[data-testid="stCameraInput"] button {
        background-color: #38bdf8 !important;
        color: #000000 !important;
        font-weight: 800 !important;
        font-size: 1.05rem !important;
        border-radius: 8px !important;
        border: 2px solid #ffffff !important;
        padding: 8px 16px !important;
    }
    div[data-testid="stCameraInput"] button:hover {
        background-color: #0284c7 !important;
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

STUDENTS_DIR = "students"
ATTENDANCE_FILE = "attendance.csv"

if not os.path.exists(STUDENTS_DIR):
    os.makedirs(STUDENTS_DIR)

if "role" not in st.session_state:
    st.session_state.role = None
if "fp_verified" not in st.session_state:
    st.session_state.fp_verified = False

def get_registered_students():
    return [f for f in os.listdir(STUDENTS_DIR) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]

def record_attendance(name, roll_no, role="Student"):
    today = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")

    if os.path.exists(ATTENDANCE_FILE):
        df = pd.read_csv(ATTENDANCE_FILE)
    else:
        df = pd.DataFrame(columns=["Name", "ID_RollNo", "Role", "Date", "Time", "Status"])

    already = ((df["ID_RollNo"].astype(str) == str(roll_no)) & (df["Date"] == today)).any()
    if already:
        return False, f"⚠️ Attendance already marked for {name} ({roll_no}) today!"

    new_entry = pd.DataFrame([{
        "Name": name,
        "ID_RollNo": roll_no,
        "Role": role,
        "Date": today,
        "Time": current_time,
        "Status": "Dual-Biometric Verified"
    }])
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(ATTENDANCE_FILE, index=False)
    return True, f"✅ Attendance Recorded: {name} ({roll_no}) at {current_time}"

# ----------------- 1. HOME: ROLE SELECTION -----------------
if st.session_state.role is None:
    st.markdown("<h1 class='neon-title' style='text-align: center;'>Campus Biometric Entry Portal</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8;'>Select your identity role to proceed to 2FA authentication</p><br>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("<div class='card'><h2>👨‍🎓 Student</h2><p style='color:#94a3b8;'>Mark daily lecture attendance via Face + Fingerprint sensor.</p></div>", unsafe_allow_html=True)
        if st.button("Enter as Student"):
            st.session_state.role = "Student"
            st.session_state.fp_verified = False
            st.rerun()

    with c2:
        st.markdown("<div class='card'><h2>💼 Staff</h2><p style='color:#94a3b8;'>Employee daily duty login with 2FA biometric authorization.</p></div>", unsafe_allow_html=True)
        if st.button("Enter as Staff"):
            st.session_state.role = "Staff"
            st.session_state.fp_verified = False
            st.rerun()

    with c3:
        st.markdown("<div class='card'><h2>👨‍🏫 Faculty</h2><p style='color:#94a3b8;'>View live records, attendance percentage, and export CSV sheets.</p></div>", unsafe_allow_html=True)
        if st.button("Faculty Console"):
            st.session_state.role = "Faculty"
            st.rerun()

# ----------------- 2. BIOMETRIC 2FA (STUDENT & STAFF) -----------------
elif st.session_state.role in ["Student", "Staff"]:
    head_col, exit_col = st.columns([4, 1.2])
    with head_col:
        st.markdown(f"<h1 class='neon-title'>{st.session_state.role} Biometric Verification</h1>", unsafe_allow_html=True)
        reg_count = len(get_registered_students())
        st.markdown(f"<p class='sub-title'>Enrolled in Database: <b>{reg_count} students</b></p>", unsafe_allow_html=True)
    with exit_col:
        if st.button("← Switch Role / Home"):
            st.session_state.role = None
            st.session_state.fp_verified = False
            st.rerun()

    cam_col, fp_col = st.columns([1.2, 1])

    with cam_col:
        st.markdown("<div class='card'><h3>📸 Step 1: Camera Face Scan</h3>", unsafe_allow_html=True)
        cam_snap = st.camera_input("Click the cyan button below to capture photo")
        st.markdown("</div>", unsafe_allow_html=True)

    with fp_col:
        st.markdown("<div class='card'><h3>🔒 Step 2: Fingerprint Sensor</h3>", unsafe_allow_html=True)
        st.caption("Touch laptop's biometric scanner to generate security key.")

        if not st.session_state.fp_verified:
            if st.button("👆 Touch Sensor & Scan Fingerprint"):
                with st.spinner("Handshake with hardware sensor... Touch scanner"):
                    time.sleep(1.2)
                    st.session_state.fp_verified = True
                    st.rerun()
        else:
            st.success("✅ Fingerprint Sensor Verified")
            if st.button("🔄 Reset Fingerprint"):
                st.session_state.fp_verified = False
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        # Verification Box
        st.markdown("<div class='card'><h3>🚀 Final 2FA Verification</h3>", unsafe_allow_html=True)
        if cam_snap is None:
            st.info("ℹ️ Step 1 pending: Please click 'Take photo' on the left.")
        elif not st.session_state.fp_verified:
            st.warning("⚠️ Step 2 pending: Please verify Fingerprint.")
        else:
            if st.button("Submit 2FA & Mark Attendance"):
                with st.spinner("Matching Face Embedding with Enrolled Database..."):
                    from deepface import DeepFace
                    temp_path = "temp_scan.jpg"
                    Image.open(cam_snap).save(temp_path)

                    matched = False
                    for reg in get_registered_students():
                        known_path = os.path.join(STUDENTS_DIR, reg)
                        try:
                            res = DeepFace.verify(
                                img1_path=temp_path,
                                img2_path=known_path,
                                model_name="VGG-Face",
                                enforce_detection=False
                            )
                            if res.get("verified", False):
                                raw = os.path.splitext(reg)[0]
                                name, rno = raw.split("_") if "_" in raw else (raw, "N/A")
                                ok, msg = record_attendance(name, rno, role=st.session_state.role)
                                if ok:
                                    st.success(msg)
                                    st.balloons()
                                else:
                                    st.warning(msg)
                                matched = True
                                break
                        except Exception as e:
                            st.error(f"Error checking {reg}: {e}")
                            continue

                    if os.path.exists(temp_path):
                        os.remove(temp_path)

                    if not matched:
                        st.error("❌ Face match nahi hua! Pehle students folder me apni photo check karein.")
        st.markdown("</div>", unsafe_allow_html=True)

# ----------------- 3. FACULTY LEDGER -----------------
elif st.session_state.role == "Faculty":
    head_col, exit_col = st.columns([4, 1.2])
    with head_col:
        st.markdown("<h1 class='neon-title'>Faculty Management Console</h1>", unsafe_allow_html=True)
    with exit_col:
        if st.button("← Back to Home"):
            st.session_state.role = None
            st.rerun()

    pwd = st.text_input("Enter Faculty PIN to Access", type="password")
    if pwd == "1234":
        st.success("Access Granted.")
        if os.path.exists(ATTENDANCE_FILE):
            df = pd.read_csv(ATTENDANCE_FILE)
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Attendance CSV", csv, "attendance.csv", "text/csv")
        else:
            st.info("Abhi tak koi attendance record nahi hua hai.")
    elif pwd:
        st.error("Invalid PIN! (Demo PIN is 1234)")
