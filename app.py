import streamlit as st
import cv2
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from io import BytesIO
from PIL import Image

# 水楊酸濃度公式
def gray_to_concentration(gray_value):
    return -(gray_value - 182.56) / 3660.7  # 結果是 0~1 的比例

# 圖片區塊分析，回傳灰階與濃度的清單 + 座標
def analyze_image(image_array, block_size=16):
    gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    block_data = []  # 存 (x, y, avg_gray, concentration)

    for y in range(0, h - block_size + 1, block_size):
        for x in range(0, w - block_size + 1, block_size):
            block = gray[y:y+block_size, x:x+block_size]
            avg_gray = np.mean(block)
            conc = gray_to_concentration(avg_gray)

            if 0 <= conc <= 1:
                block_data.append((x, y, avg_gray, conc))

    return block_data

# Streamlit 介面
st.title("🔬 水楊酸濃度自動分析工具")
st.write("上傳圖片，我們會自動判斷主要反應區的水楊酸濃度，繪製分布圖，並在圖片中圈選主要反應區")

uploaded_file = st.file_uploader("請選擇一張圖片...", type=["jpg", "jpeg", "png", "bmp"])

if uploaded_file is not None:
    # 讀入圖片並轉為 OpenCV 格式
    img_pil = Image.open(uploaded_file).convert('RGB')
    img_cv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    st.image(img_pil, caption="上傳的圖片", use_column_width=True)

    # 分析
    block_size = 16
    blocks = analyze_image(img_cv, block_size=block_size)

    if blocks:
        conc_list = [round(conc, 3) for (_, _, _, conc) in blocks]
        counts = Counter(conc_list)
        most_common_value, count = counts.most_common(1)[0]

        st.success(f"🌟 最常出現的水楊酸濃度為：約 **{most_common_value:.2%}**，共 {count} 區塊")

        # 繪製直方圖
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.hist(conc_list, bins=30, color='skyblue', edgecolor='black')
        ax.set_xlabel('Salicylic Acid Concentration (%)')
        ax.set_ylabel('Block Count')
        ax.set_title('Distribution of Estimated Salicylic Acid Concentration')
        st.pyplot(fig)

        # 繪製區塊標註圖
        img_marked = img_cv.copy()
        for x, y, gray, conc in blocks:
            if round(conc, 3) == most_common_value:
                cv2.rectangle(img_marked, (x, y), (x + block_size, y + block_size), (0, 255, 0), 2)

        # 顯示標註後圖片
        img_rgb_marked = cv2.cvtColor(img_marked, cv2.COLOR_BGR2RGB)
        st.image(img_rgb_marked, caption="圈選出灰階值（濃度）最常見區域", use_column_width=True)

    else:
        st.warning("⚠️ 沒有偵測到有效的水楊酸濃度區塊。")
