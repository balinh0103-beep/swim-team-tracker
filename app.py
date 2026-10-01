import streamlit as st
import pandas as pd
import datetime
import json
import os

# --- TỰ ĐỘNG TẠO CẤU HÌNH GIAO DIỆN TỐI (DARK MODE) VĨNH VIỄN ---
if not os.path.exists(".streamlit"):
    os.makedirs(".streamlit")
config_content = """
[theme]
base="dark"
primaryColor="#0077b6"
backgroundColor="#0e1117"
secondaryBackgroundColor="#161b22"
textColor="#ffffff"
"""
with open(".streamlit/config.toml", "w", encoding="utf-8") as f:
    f.write(config_content.strip())

# Cấu hình trang
st.set_page_config(page_title="Swim Team Pro Tracker", page_icon="🏊‍♂️", layout="wide")

# --- CSS TỐI ƯU HÓA GIAO DIỆN CHUYÊN NGHIỆP ---
BG_IMAGE_URL = "https://images.unsplash.com/photo-1530549387789-4c1017266635?auto=format&fit=crop&w=1920&q=80"

st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(8, 20, 38, 0.92), rgba(8, 20, 38, 0.97)),
                    url('{BG_IMAGE_URL}') no-repeat center center fixed;
        background-size: cover;
    }}
    
    .auth-card {{
        background: rgba(15, 23, 42, 0.90);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        padding: 2.5rem;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.6);
        max-width: 500px;
        margin: 0 auto;
    }}

    .profile-banner {{
        background: rgba(15, 23, 42, 0.88);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 14px;
        padding: 1.5rem;
        display: flex;
        align-items: center;
        gap: 20px;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 20px rgba(0,0,0,0.4);
    }}

    .avatar-img {{
        width: 80px;
        height: 80px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid #00b4d8;
    }}

    h1, h2, h3, h4, h5, h6, p, span, label, div {{
        color: #ffffff !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}

    .stTextInput input, .stSelectbox select, .stNumberInput input, .stTextArea textarea {{
        background-color: rgba(255, 255, 255, 0.08) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
    }}

    .stButton>button {{
        width: 100%;
        background-color: #0077b6 !important;
        color: white !important;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 0.7rem;
        transition: all 0.3s ease;
    }}
    .stButton>button:hover {{
        background-color: #0096c7 !important;
        box-shadow: 0 0 15px rgba(0, 180, 216, 0.7);
    }}
    </style>
""", unsafe_allow_html=True)

# --- QUẢN LÝ DỮ LIỆU FILE & THƯ MỤC UPLOAD ---
USERS_FILE = "users_db.json"
WORKOUTS_FILE = "workouts_db.json"
VIDEOS_FILE = "videos_db.json"
UPLOAD_DIR = "uploaded_avatars"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "admin": {
            "password": "123456", 
            "role": "Admin", 
            "name": "Quản Trị Viên", 
            "class": "Ban Huấn Luyện", 
            "bio": "HLV Trưởng - Đào tạo bơi lội chuyên nghiệp.", 
            "status": "approved",
            "avatar": ""
        }
    }

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

def load_workouts():
    if os.path.exists(WORKOUTS_FILE):
        return pd.read_json(WORKOUTS_FILE, orient="split")
    return pd.DataFrame(columns=[
        "ID", "Ngay", "TenVĐV", "Lop", "KieuBoi", 
        "ThoiGianBoi (phút)", "QuangDuong (m)", "CanNặng (kg)", 
        "CamNhan", "Calorie", "NhanXetCoach"
    ])

def save_workouts(df):
    df.to_json(WORKOUTS_FILE, orient="split", compression="infer", force_ascii=False)

def load_videos():
    if os.path.exists(VIDEOS_FILE):
        with open(VIDEOS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return [
        {"title": "Kỹ thuật bơi Sải (Freestyle) chuẩn quốc tế", "url": "https://www.youtube.com/watch?v=5Q07-HxYVzY", "desc": "Tối ưu hóa nhịp thở và lực quạt tay."},
        {"title": "Kỹ thuật đạp chân và quạt tay bơi Ếch", "url": "https://www.youtube.com/watch?v=123456789", "desc": "Giảm tối đa lực cản của nước."}
    ]

def save_videos(videos):
    with open(VIDEOS_FILE, "w", encoding="utf-8") as f:
        json.dump(videos, f, ensure_ascii=False, indent=4)

if "users_db" not in st.session_state:
    st.session_state["users_db"] = load_users()
if "workouts" not in st.session_state:
    st.session_state["workouts"] = load_workouts()
if "videos_db" not in st.session_state:
    st.session_state["videos_db"] = load_videos()

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["role"] = ""
    st.session_state["user_username"] = ""
    st.session_state["user_name"] = ""

# --- MÀN HÌNH ĐĂNG NHẬP / ĐĂNG KÝ TRUNG TÂM ---
if not st.session_state["logged_in"]:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: white !important;'>SWIM TEAM PERFORMANCE</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #90e0ef !important; margin-bottom: 2rem;'>Hệ thống theo dõi và phân tích hiệu suất bơi lội chuyên nghiệp</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        auth_mode = st.radio("Thao tác", ["Đăng nhập", "Đăng ký thành viên mới"], horizontal=True, label_visibility="collapsed")
        
        st.markdown("<div class='auth-card'>", unsafe_allow_html=True)

        if auth_mode == "Đăng nhập":
            st.markdown("### Đăng nhập hệ thống")
            username_input = st.text_input("Tên đăng nhập")
            password_input = st.text_input("Mật khẩu", type="password")
            
            if st.button("Truy cập hệ thống"):
                users = st.session_state["users_db"]
                if username_input in users:
                    if users[username_input]["password"] == password_input:
                        if users[username_input].get("status") == "approved":
                            st.session_state["logged_in"] = True
                            st.session_state["role"] = users[username_input]["role"]
                            st.session_state["user_username"] = username_input
                            st.session_state["user_name"] = users[username_input]["name"]
                            st.rerun()
                        else:
                            st.warning("Tài khoản đang chờ Ban huấn luyện phê duyệt.")
                    else:
                        st.error("Mật khẩu không chính xác.")
                else:
                    st.error("Tên đăng nhập không tồn tại.")
        else:
            st.markdown("### Đăng ký thành viên")
            new_username = st.text_input("Tên đăng nhập mới")
            new_password = st.text_input("Mật khẩu mới", type="password")
            new_fullname = st.text_input("Họ và tên đầy đủ")
            new_class = st.text_input("Lớp (Ví dụ: 6A1)")
            
            if st.button("Gửi hồ sơ đăng ký"):
                if new_username and new_password and new_fullname:
                    if new_username in st.session_state["users_db"]:
                        st.error("Tên đăng nhập này đã tồn tại.")
                    else:
                        st.session_state["users_db"][new_username] = {
                            "password": new_password,
                            "role": "Swimmer",
                            "name": new_fullname,
                            "class": new_class if new_class else "Chưa phân lớp",
                            "bio": "Vận động viên tiềm năng.",
                            "status": "pending",
                            "avatar": ""
                        }
                        save_users(st.session_state["users_db"])
                        st.success("Đăng ký thành công! Vui lòng chờ phê duyệt.")
                else:
                    st.warning("Vui lòng điền đủ các mục thông tin.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- GIAO DIỆN SAU KHI ĐĂNG NHẬP ---
role = st.session_state["role"]
username = st.session_state["user_username"]
current_user = st.session_state["users_db"][username]
user_name = current_user["name"]
user_avatar = current_user.get("avatar", "")

# Sidebar
st.sidebar.markdown(f"**{user_name}**")
st.sidebar.caption(f"Vai trò: {role}")
if st.sidebar.button("Đăng xuất"):
    st.session_state["logged_in"] = False
    st.rerun()

# Banner hồ sơ đầu trang
avatar_display_html = f'<img src="{user_avatar}" class="avatar-img" alt="avatar">' if (user_avatar and os.path.exists(user_avatar)) else f'<div style="width:80px;height:80px;border-radius:50%;background:#0077b6;display:flex;align-items:center;justify-content:center;font-size:32px;font-weight:bold;color:white;border:3px solid #00b4d8;">{user_name[0].upper()}</div>'

st.markdown(f"""
    <div class="profile-banner">
        {avatar_display_html}
        <div>
            <h2 style="margin: 0; color: white;">{user_name}</h2>
            <p style="margin: 4px 0; color: #caf0f8 !important;">Đơn vị / Lớp: <b>{current_user.get('class', 'N/A')}</b> | Vai trò: <b>{role}</b></p>
            <p style="margin: 0; font-size: 13px; color: #90e0ef !important; font-style: italic;">"{current_user.get('bio', 'Đang cập nhật khẩu hiệu...')}"</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# Tabs chức năng
if role == "Admin":
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Dashboard", "Nhập Nhật Ký", "Đánh Giá / Lời Phê", 
        "Quản Lý Thành Viên", "Bảng Xếp Hạng", "Video Kỹ Thuật", "Hồ Sơ Cá Nhân"
    ])
else:
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Dashboard", "Nhập Nhật Ký", "Bảng Xếp Hạng", "Video Kỹ Thuật", "Hồ Sơ Cá Nhân"
    ])

df = st.session_state["workouts"]

# --- TAB 1: DASHBOARD ---
with tab1:
    st.markdown("### Thống kê hiệu suất tập luyện")
    if df.empty:
        st.info("Chưa có dữ liệu tập luyện nào.")
    else:
        if role == "Swimmer":
            current_df = df[df["TenVĐV"] == user_name]
            st.caption(f"Dữ liệu cá nhân: {user_name}")
        else:
            swimmer_list = ["Toàn đội tuyển"] + list(df["TenVĐV"].unique())
            selected_view = st.selectbox("Lựa chọn góc nhìn Dashboard:", swimmer_list)
            if selected_view == "Toàn đội tuyển":
                current_df = df
                st.caption("Tổng hợp toàn bộ đội bơi")
            else:
                current_df = df[df["TenVĐV"] == selected_view]
                st.caption(f"Chi tiết thông số cá nhân: {selected_view}")

        if current_df.empty:
            st.info("Chưa có dữ liệu cho vận động viên này.")
        else:
            col1, col2, col3, col4 = st.columns(4)
            total_hours = current_df["ThoiGianBoi (phút)"].sum() / 60
            total_distance = current_df["QuangDuong (m)"].sum()
            total_calo = current_df["Calorie"].sum()
            avg_rpe = current_df["CamNhan"].astype(int).mean()

            col1.metric("Thời gian", f"{total_hours:.1f}h")
            col2.metric("Quãng đường", f"{total_distance:,.0f}m")
            col3.metric("Năng lượng đốt cháy", f"{total_calo:,.0f} kcal")
            col4.metric("Độ mệt (RPE)", f"{avg_rpe:.1f}/10")

            st.markdown("---")
            st.markdown("#### Biểu đồ quãng đường bơi theo ngày")
            chart_data = current_df.groupby("Ngay")["QuangDuong (m)"].sum()
            st.bar_chart(chart_data)

# --- TAB 2: NHẬP NHẬT KÝ ---
with tab2:
    st.markdown("### Cập nhật buổi tập mới")
    with st.form("workout_form"):
        col_a, col_b = st.columns(2)
        with col_a:
            ngay_tap = st.date_input("Ngày tập", datetime.date.today())
            vđv_input = st.text_input("Vận động viên", value=user_name)
            lop_input = st.text_input("Lớp", value=current_user.get("class", ""))
            kieu_boi = st.selectbox("Kiểu bơi chủ đạo", ["Bơi tự do (Sải)", "Bơi ếch", "Bơi ngửa", "Bơi bướm", "Hỗn hợp"])
        with col_b:
            thoi_gian = st.number_input("Thời gian bơi (phút)", min_value=10, max_value=300, value=60)
            quang_duong = st.number_input("Quãng đường (m)", min_value=100, max_value=10000, value=1500, step=100)
            can_nang = st.number_input("Cân nặng hiện tại (kg)", min_value=20.0, max_value=100.0, value=45.0)
            cam_nhan = st.slider("Cảm nhận độ mệt (RPE 1-10)", 1, 10, 5)

        if st.form_submit_button("Lưu kết quả buổi tập"):
            met_dict = {"Bơi tự do (Sải)": 8.3, "Bơi ếch": 5.3, "Bơi ngửa": 7.0, "Bơi bướm": 11.8, "Hỗn hợp": 8.0}
            met = met_dict.get(kieu_boi, 8.0)
            calorie_burned = (met * 3.5 * can_nang / 200) * thoi_gian

            new_row = {
                "ID": len(df) + 1,
                "Ngay": str(ngay_tap),
                "TenVĐV": vđv_input,
                "Lop": lop_input,
                "KieuBoi": kieu_boi,
                "ThoiGianBoi (phút)": thoi_gian,
                "QuangDuong (m)": quang_duong,
                "CanNặng (kg)": can_nang,
                "CamNhan": cam_nhan,
                "Calorie": round(calorie_burned, 1),
                "NhanXetCoach": "Chưa có nhận xét"
            }
            updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            st.session_state["workouts"] = updated_df
            save_workouts(updated_df)
            st.success(f"Đã ghi nhận thành công! Tiêu thụ {round(calorie_burned, 1)} kcal.")

# --- TÍNH NĂNG ADMIN ---
if role == "Admin":
    with tab3:
        st.markdown("### Quản lý nhật ký và xuất Database")
        if df.empty:
            st.info("Chưa có dữ liệu.")
        else:
            # Dùng định dạng CSV chuẩn, tương thích 100% với Excel mà không cần cài thêm thư viện
            csv_data = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 Tải xuống toàn bộ Database Tập Luyện (.csv mở bằng Excel)",
                data=csv_data,
                file_name=f"SwimTeam_Database_{datetime.date.today()}.csv",
                mime="text/csv"
            )
            st.markdown("---")
            st.dataframe(df, use_container_width=True)
            st.markdown("---")
            row_id = st.number_input("ID buổi tập cần nhận xét", min_value=1, max_value=max(df["ID"]) if not df.empty else 1, step=1)
            feedback_text = st.text_area("Lời phê / Đánh giá của Ban huấn luyện")
            if st.button("Gửi nhận xét"):
                st.session_state["workouts"].loc[st.session_state["workouts"]["ID"] == row_id, "NhanXetCoach"] = feedback_text
                save_workouts(st.session_state["workouts"])
                st.success("Đã lưu nhận xét thành công.")

    with tab4:
        st.markdown("### Phê duyệt thành viên mới")
        pending_users = {k: v for k, v in st.session_state["users_db"].items() if v.get("status") == "pending"}
        if not pending_users:
            st.info("Không có tài khoản nào đang chờ phê duyệt.")
        else:
            for u_key, u_val in pending_users.items():
                col_p1, col_p2, col_p3 = st.columns([2, 2, 1])
                col_p1.text(f"{u_val['name']} ({u_key})")
                col_p2.text(f"Lớp: {u_val.get('class', 'N/A')}")
                if col_p3.button("Phê duyệt", key=f"approve_{u_key}"):
                    st.session_state["users_db"][u_key]["status"] = "approved"
                    save_users(st.session_state["users_db"])
                    st.success(f"Đã duyệt thành công cho {u_val['name']}.")
                    st.rerun()

        st.markdown("---")
        st.markdown("### Phân quyền thành viên chính thức")
        for u_key, u_val in st.session_state["users_db"].items():
            if u_val.get("status") == "approved":
                col_m1, col_m2, col_m3, col_m4 = st.columns([2, 2, 2, 2])
                col_m1.text(u_key)
                col_m2.text(u_val['name'])
                col_m3.text(u_val.get('class', ''))
                current_role_idx = 0 if u_val['role'] == "Admin" else 1
                new_role = col_m4.selectbox("Vai trò", ["Admin", "Swimmer"], index=current_role_idx, key=f"role_{u_key}")
                if new_role != u_val['role']:
                    st.session_state["users_db"][u_key]['role'] = new_role
                    save_users(st.session_state["users_db"])
                    st.success(f"Đã cập nhật vai trò của {u_val['name']}.")
                    st.rerun()
                st.markdown("---")

    with tab5:
        st.markdown("### Bảng xếp hạng thành tích")
        if df.empty:
            st.info("Chưa có dữ liệu.")
        else:
            lb = df.groupby("TenVĐV")[["QuangDuong (m)", "Calorie"]].sum().reset_index()
            lb = lb.sort_values(by="QuangDuong (m)", ascending=False).reset_index(drop=True)
            lb.index = lb.index + 1
            
            csv_lb = lb.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 Tải xuống Bảng Xếp Hạng (.csv mở bằng Excel)",
                data=csv_lb,
                file_name=f"SwimTeam_BangXepHang_{datetime.date.today()}.csv",
                mime="text/csv"
            )
            st.markdown("---")
            st.dataframe(lb, use_container_width=True)

    with tab6:
        st.markdown("### Quản lý video bài giảng")
        with st.form("add_vid_form"):
            v_title = st.text_input("Tiêu đề")
            v_url = st.text_input("Link YouTube")
            v_desc = st.text_area("Mô tả bài giảng")
            if st.form_submit_button("Thêm video"):
                if v_title and v_url:
                    st.session_state["videos_db"].append({"title": v_title, "url": v_url, "desc": v_desc})
                    save_videos(st.session_state["videos_db"])
                    st.success("Thêm bài giảng thành công.")
        st.markdown("---")
        for v in st.session_state["videos_db"]:
            st.markdown(f"**{v['title']}**")
            st.caption(v['desc'])
            st.markdown(f"[Xem bài giảng tại đây]({v['url']})")
            st.markdown("---")

    with tab7:
        st.markdown("### Hồ sơ cá nhân")
        with st.form("admin_profile"):
            new_name = st.text_input("Họ và tên", value=current_user["name"])
            new_class = st.text_input("Đơn vị / Phụ trách", value=current_user.get("class", ""))
            uploaded_file = st.file_uploader("Tải lên ảnh đại diện mới", type=["jpg", "png", "jpeg"])
            new_bio = st.text_area("Tiểu sử", value=current_user.get("bio", ""))
            new_pass = st.text_input("Mật khẩu mới", type="password")
            
            if st.form_submit_button("Cập nhật hồ sơ"):
                avatar_path = current_user.get("avatar", "")
                if uploaded_file is not None:
                    avatar_path = os.path.join(UPLOAD_DIR, f"{username}_{uploaded_file.name}")
                    with open(avatar_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                st.session_state["users_db"][username]["name"] = new_name
                st.session_state["users_db"][username]["class"] = new_class
                st.session_state["users_db"][username]["avatar"] = avatar_path
                st.session_state["users_db"][username]["bio"] = new_bio
                if new_pass:
                    st.session_state["users_db"][username]["password"] = new_pass
                save_users(st.session_state["users_db"])
                st.success("Cập nhật hồ sơ thành công.")
                st.rerun()

# --- TÍNH NĂNG HỌC VIÊN ---
else:
    with tab3:
        st.markdown("### Bảng xếp hạng toàn đội")
        if df.empty:
            st.info("Chưa có dữ liệu.")
        else:
            lb = df.groupby("TenVĐV")[["QuangDuong (m)", "Calorie"]].sum().reset_index()
            lb = lb.sort_values(by="QuangDuong (m)", ascending=False).reset_index(drop=True)
            lb.index = lb.index + 1
            st.dataframe(lb, use_container_width=True)

    with tab4:
        st.markdown("### Thư viện video bài giảng kỹ thuật")
        for v in st.session_state["videos_db"]:
            st.markdown(f"**{v['title']}**")
            st.caption(v['desc'])
            st.markdown(f"[Bấm vào đây để xem]({v['url']})")
            st.markdown("---")

    with tab5:
        st.markdown("### Hồ sơ cá nhân")
        with st.form("user_profile"):
            new_name = st.text_input("Họ và tên", value=current_user["name"])
            new_class = st.text_input("Lớp", value=current_user.get("class", ""))
            uploaded_file = st.file_uploader("Tải lên ảnh đại diện mới", type=["jpg", "png", "jpeg"])
            new_bio = st.text_area("Tiểu sử", value=current_user.get("bio", ""))
            new_pass = st.text_input("Mật khẩu mới", type="password")
            
            if st.form_submit_button("Cập nhật hồ sơ"):
                avatar_path = current_user.get("avatar", "")
                if uploaded_file is not None:
                    avatar_path = os.path.join(UPLOAD_DIR, f"{username}_{uploaded_file.name}")
                    with open(avatar_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                st.session_state["users_db"][username]["name"] = new_name
                st.session_state["users_db"][username]["class"] = new_class
                st.session_state["users_db"][username]["avatar"] = avatar_path
                st.session_state["users_db"][username]["bio"] = new_bio
                if new_pass:
                    st.session_state["users_db"][username]["password"] = new_pass
                save_users(st.session_state["users_db"])
                st.success("Cập nhật hồ sơ thành công.")
                st.rerun()