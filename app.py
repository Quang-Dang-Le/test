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
# THAY THẾ PHẦN ÉP KIỂU BẰNG 4 DÒNG SAU:
df_keys['Ma_ID'] = df_keys['Ma_ID'].astype(str)
df_keys['Trang_thai'] = df_keys['Trang_thai'].astype(str)
df_keys['Username'] = df_keys['Username'].astype(str)
df_keys['Password'] = df_keys['Password'].astype(str) # <-- Đây chính là dòng trị dứt điểm lỗi

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
# ==========================================
# GIAO DIỆN KHI ĐÃ ĐĂNG NHẬP THÀNH CÔNG
# ==========================================
else:
    # 1. TẠO THANH MENU BÊN TRÁI (SIDEBAR)
    st.sidebar.success(f"👋 Xin chào, **{st.session_state['current_user']}**!")
    st.sidebar.write("---")
    
    # Định nghĩa các mục trong Menu
    menu = [
        "Cuốn 1: Tiền xử lý dữ liệu (Đã mở)", 
        "Cuốn 2: Machine Learning (Sắp ra mắt)", 
        "💎 Nâng cấp VIP"
    ]
    choice = st.sidebar.radio("📚 KHÔNG GIAN THỰC HÀNH:", menu)
    
    # Nút Đăng xuất đưa vào menu trái cho gọn
    st.sidebar.write("---")
    if st.sidebar.button("Đăng xuất"):
        st.session_state['logged_in'] = False
        st.session_state['current_user'] = None
        st.session_state['user_code'] = None
        st.rerun()

    # 2. KHÔNG GIAN LÀM VIỆC CHÍNH (DỰA VÀO MENU ĐƯỢC CHỌN)
    
    # --- MODULE CUỐN 1 (TẬP TRUNG XÂY DỰNG NGAY) ---
    if choice == "Cuốn 1: Tiền xử lý dữ liệu (Đã mở)":
        st.header("🛠️ Kỹ thuật Tiền xử lý Dữ liệu")
        st.info("Hệ thống đã nhận diện mã của bạn. Hãy tải bộ dữ liệu thô dưới đây và thực hành làm sạch.")
        
        # (Ví dụ: Sinh dữ liệu hồ sơ tín dụng có lỗi nhập liệu và dòng trống)
        np.random.seed(sum(ord(c) for c in st.session_state['user_code']))
        data = {
            "Thu_Nhap_TrieuVND": np.random.randint(10, 200, 100).astype(float),
            "Diem_Tin_Dung": np.random.randint(300, 850, 100).astype(float)
        }
        df_bai_tap = pd.DataFrame(data)
        
        # Cố tình đục lỗ (tạo NaN) vào dữ liệu để ép sinh viên phải xử lý
        df_bai_tap.loc[np.random.choice(df_bai_tap.index, 5), 'Thu_Nhap_TrieuVND'] = np.nan
        df_bai_tap.loc[np.random.choice(df_bai_tap.index, 3), 'Diem_Tin_Dung'] = np.nan
        
        csv = df_bai_tap.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Tải file CSV Dữ liệu thô",
            data=csv,
            file_name=f"raw_data_{st.session_state['current_user']}.csv",
            mime='text/csv',
        )
        
        st.write("---")
        st.subheader("📝 Nộp bài chấm điểm tự động")
        st.write("Sau khi xử lý điền khuyết bằng trung vị (median), hãy nhập giá trị trung bình (mean) mới của cột Thu nhập:")
        ket_qua = st.number_input("Nhập kết quả của bạn:", format="%.2f")
        if st.button("Kiểm tra đáp án"):
            # (Phần logic chấm điểm sẽ viết ở đây)
            st.warning("Chức năng chấm điểm đang được hoàn thiện.")
            
    # --- MODULE CUỐN 2 (CHỖ TRỐNG CHỜ SẴN - TẠO SỰ TÒ MÒ) ---
    elif choice == "Cuốn 2: Machine Learning (Sắp ra mắt)":
        st.header("🤖 Mô hình Machine Learning")
        st.warning("🔒 Học phần này đang được xây dựng và sẽ sớm ra mắt!")
        st.write("Dự kiến bạn sẽ được thực hành xây dựng mô hình phân loại rủi ro tín dụng trên tập dữ liệu hàng chục ngàn dòng.")
        
        # Nút thu thập Data để Upsell (Bán chéo)
        if st.button("Đăng ký nhận thông báo và ưu đãi 50% khi ra mắt"):
            st.success("Cám ơn bạn! Chúng tôi sẽ gửi email khi học phần này sẵn sàng.")
            
    # --- MODULE VIP (MỞ RỘNG KINH DOANH SAU NÀY) ---
    elif choice == "💎 Nâng cấp VIP":
        st.header("Mở khóa toàn quyền truy cập")
        st.write("👉 Tải video hướng dẫn giải chi tiết code Python từng bước.")
        st.write("👉 Truy cập kho 50+ bộ dữ liệu tài chính thực tế.")
        st.info("Chức năng thanh toán tự động đang được bảo trì.")
