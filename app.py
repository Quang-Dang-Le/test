import streamlit as st
import pandas as pd
import numpy as np
from streamlit_gsheets import GSheetsConnection
import hashlib

# Hàm mã hóa mật khẩu để bảo mật
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

st.title("📚 Học phần Khoa học Dữ liệu Ứng dụng")

# 1. Khởi tạo bộ nhớ tạm (Session State) để giữ trạng thái đăng nhập
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'current_user' not in st.session_state:
    st.session_state['current_user'] = None
if 'user_code' not in st.session_state:
    st.session_state['user_code'] = None

# Kết nối Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)
df_keys = conn.read(worksheet="Sheet1", ttl=0)
# Ép kiểu dữ liệu để tránh lỗi
df_keys['Trang_thai'] = df_keys['Trang_thai'].astype(str)
df_keys['Username'] = df_keys['Username'].astype(str)

# ==========================================
# GIAO DIỆN KHI CHƯA ĐĂNG NHẬP
# ==========================================
if not st.session_state['logged_in']:
    # Chia làm 2 Tab: Đăng nhập và Đăng ký (Kích hoạt)
    tab1, tab2 = st.tabs(["🔑 Đăng nhập", "📝 Kích hoạt sách (Đăng ký)"])

    # --- TAB 1: ĐĂNG NHẬP ---
    with tab1:
        st.subheader("Đăng nhập vào hệ thống")
        login_user = st.text_input("Tên đăng nhập (Username)", key="login_user")
        login_pass = st.text_input("Mật khẩu", type="password", key="login_pass")
        
        if st.button("Đăng nhập"):
            # Mã hóa pass người dùng nhập để so sánh với pass trên Sheets
            hashed_input_pass = hash_password(login_pass)
            
            # Tìm username trong CSDL
            user_row = df_keys[df_keys['Username'] == login_user]
            
            if not user_row.empty:
                correct_password = user_row.iloc[0]['Password']
                if hashed_input_pass == correct_password:
                    # Đăng nhập thành công, lưu thông tin vào Session
                    st.session_state['logged_in'] = True
                    st.session_state['current_user'] = login_user
                    st.session_state['user_code'] = user_row.iloc[0]['Ma_ID']
                    st.rerun() # Tải lại trang để vào màn hình chính
                else:
                    st.error("Sai mật khẩu!")
            else:
                st.error("Tên đăng nhập không tồn tại!")

    # --- TAB 2: KÍCH HOẠT SÁCH MỚI ---
    with tab2:
        st.subheader("Lần đầu sử dụng? Hãy kích hoạt sách")
        reg_code = st.text_input("Mã kích hoạt (Cào lớp bạc ở cuối sách)")
        reg_user = st.text_input("Chọn Tên đăng nhập (Viết liền không dấu)")
        reg_pass = st.text_input("Chọn Mật khẩu", type="password")
        
        if st.button("Kích hoạt tài khoản"):
            if reg_code in df_keys['Ma_ID'].values:
                row_index = df_keys.index[df_keys['Ma_ID'] == reg_code].tolist()[0]
                trang_thai = df_keys.at[row_index, 'Trang_thai']
                
                if pd.isna(trang_thai) or trang_thai == "nan" or trang_thai != "Đã dùng":
                    # Kiểm tra xem username đã có người lấy chưa
                    if reg_user in df_keys['Username'].values and reg_user != "nan":
                        st.warning("Tên đăng nhập này đã có người sử dụng, vui lòng chọn tên khác!")
                    else:
                        # Cập nhật thông tin lên Sheets
                        df_keys.at[row_index, 'Trang_thai'] = "Đã dùng"
                        df_keys.at[row_index, 'Username'] = reg_user
                        df_keys.at[row_index, 'Password'] = hash_password(reg_pass)
                        
                        conn.update(worksheet="Sheet1", data=df_keys)
                        st.success("Kích hoạt thành công! Vui lòng chuyển sang tab Đăng nhập để sử dụng.")
                else:
                    st.error("Mã này đã được kích hoạt trước đó!")
            else:
                st.error("Mã sách không hợp lệ!")

# ==========================================
# GIAO DIỆN KHI ĐÃ ĐĂNG NHẬP THÀNH CÔNG
# ==========================================
else:
    st.success(f"👋 Xin chào, **{st.session_state['current_user']}**!")
    
    st.write("### Nhận dữ liệu thực hành cá nhân")
    st.info("Hệ thống đã nhận diện mã sách của bạn. Dữ liệu dưới đây được sinh ra dành riêng cho bạn.")
    
    # Sinh dữ liệu ngẫu nhiên dựa trên mã ID gốc của người dùng
    np.random.seed(sum(ord(c) for c in st.session_state['user_code']))
    data = {
        "DienTich_m2": np.random.randint(40, 150, 100),
        "GiaBan_TyVND": np.random.uniform(1.5, 8.0, 100)
    }
    df_bai_tap = pd.DataFrame(data)
    csv = df_bai_tap.to_csv(index=False).encode('utf-8')
    
    st.download_button(
        label="📥 Tải file CSV của bạn",
        data=csv,
        file_name=f"dataset_{st.session_state['current_user']}.csv",
        mime='text/csv',
    )
    
    # Nút Đăng xuất
    if st.button("Đăng xuất"):
        st.session_state['logged_in'] = False
        st.session_state['current_user'] = None
        st.session_state['user_code'] = None
        st.rerun()
