import streamlit as st
import pandas as pd
import numpy as np
from streamlit_gsheets import GSheetsConnection

st.title("📚 Thực hành Khoa học Dữ liệu Ứng dụng Kinh tế")

# 1. Kết nối với Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Đọc dữ liệu từ Sheet1 vào một DataFrame của Pandas
# (Lưu ý: tham số ttl=0 để nó luôn lấy dữ liệu mới nhất, không dùng bộ nhớ đệm cache)
df_keys = conn.read(worksheet="Sheet1", ttl=0)
# THÊM DÒNG NÀY VÀO NGAY BÊN DƯỚI:
df_keys['Trang_thai'] = df_keys['Trang_thai'].astype(str)
st.write("### Nhập mã định danh")
ma_sinh_vien = st.text_input("Vui lòng cào lớp bạc ở cuối sách và nhập mã vào đây:")

if st.button("Tạo đề bài"):
    # Tìm xem mã sinh viên nhập có nằm trong cột 'Ma_ID' không
    if ma_sinh_vien in df_keys['Ma_ID'].values:
        
        # Lấy vị trí (index) của dòng chứa mã này
        row_index = df_keys.index[df_keys['Ma_ID'] == ma_sinh_vien].tolist()[0]
        trang_thai_hien_tai = df_keys.at[row_index, 'Trang_thai']
        
        if pd.isna(trang_thai_hien_tai) or trang_thai_hien_tai != "Đã dùng":
            st.success("Xác thực thành công! Hệ thống đang sinh dữ liệu cho bạn...")
            
            # --- CHỖ NÀY LÀ LOGIC SINH BÀI TẬP (GIỐNG PHẦN TRƯỚC) ---
            np.random.seed(sum(ord(c) for c in ma_sinh_vien))
            data = {
                "DienTich_m2": np.random.randint(40, 150, 100),
                "GiaBan_TyVND": np.random.uniform(1.5, 8.0, 100)
            }
            df_bai_tap = pd.DataFrame(data)
            csv = df_bai_tap.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📥 Tải file dữ liệu (CSV)",
                data=csv,
                file_name=f'dataset_{ma_sinh_vien}.csv',
                mime='text/csv',
            )
            # --------------------------------------------------------
            
            # 2. CẬP NHẬT TRẠNG THÁI "ĐÃ DÙNG" LÊN GOOGLE SHEETS
            df_keys.at[row_index, 'Trang_thai'] = "Đã dùng"
            # Đẩy cục data mới ghi đè lên Sheet cũ
            conn.update(worksheet="Sheet1", data=df_keys)
            
        else:
            st.warning("Mã này đã được sử dụng bởi một người khác!")
    else:
        st.error("Mã không hợp lệ. Vui lòng kiểm tra lại!")
