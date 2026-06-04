import streamlit as st
import pandas as pd
import numpy as np

# Thiết lập tiêu đề trang web
st.title("📚 Thực hành Khoa học Dữ liệu Ứng dụng Kinh tế")
st.markdown("---")

# 1. Giả lập cơ sở dữ liệu (Database) các mã hợp lệ
danh_sach_ma_hop_le = ["KINHTE2026", "DATA001", "ECON999"]

# 2. Tạo ô nhập liệu cho sinh viên
st.write("### Nhập mã định danh")
ma_sinh_vien = st.text_input("Vui lòng cào lớp bạc ở cuối sách và nhập mã vào đây:")

# 3. Xử lý logic khi bấm nút
if st.button("Tạo đề bài"):
    if ma_sinh_vien in danh_sach_ma_hop_le:
        st.success("Xác thực thành công! Hệ thống đang sinh dữ liệu cho bạn...")
        
        # MẸO HAY: Dùng chính mã của sinh viên làm 'seed' cho hàm random.
        # Như vậy, sinh viên có tải lại web thì bộ số của họ vẫn giữ nguyên, không bị đổi liên tục.
        seed_value = sum(ord(char) for char in ma_sinh_vien)
        np.random.seed(seed_value)
        
        # 4. Sinh bộ dữ liệu ngẫu nhiên (Ví dụ: Bài toán dự báo giá nhà)
        n_samples = 100
        data = {
            "DienTich_m2": np.random.randint(40, 150, n_samples),
            "KhoangCachTrungTam_km": np.random.uniform(1.0, 15.0, n_samples),
            "GiaBan_TyVND": np.random.uniform(1.5, 8.0, n_samples) # Giá ngẫu nhiên
        }
        df = pd.DataFrame(data)
        
        # Hiển thị 5 dòng đầu tiên cho sinh viên xem trước
        st.write(f"**Bộ dữ liệu dành riêng cho mã: {ma_sinh_vien}**")
        st.dataframe(df.head())
        
        # 5. Tạo nút tải file CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Tải file dữ liệu (CSV)",
            data=csv,
            file_name=f'dataset_{ma_sinh_vien}.csv',
            mime='text/csv',
        )
        
    elif ma_sinh_vien != "":
        st.error("Mã không hợp lệ hoặc đã được sử dụng. Vui lòng kiểm tra lại!")
