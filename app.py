import streamlit as st
from PIL import Image, ImageDraw
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

# 水楊酸濃度公式
def gray_to_concentration(gray_value):
    return -(gray_value - 182.56) / 3660.7  # 結果是 0~1 的比例

# 分析圖像區塊
def analyze_image_pil(img_pil, block_size=16):
    gray = img_pil.convert("L")
    arr = np.array(gray)
    h, w = arr.shape
    block_data = []  # (x, y, avg_gray, concentration)

    for y in range(0, h - block_size + 1, block_size):
        for x in range(0, w - block_size + 1, block_size):
            block = arr[y:y+block_size, x:x+block_size]
            avg_gray = float(block.mean())
            conc = gray_to_concentration(avg_gray)
            if 0 <= conc <= 1:
                block_data.append((x, y, avg_gray, conc))
    return block_data

# Streamlit 介面
st.title("🔬 水楊酸濃度自動分析工具（Pillow 版本）")
st.write("上傳圖片，我們會自動判斷主要反應區的水楊酸濃度範圍（眾數 ~ 最大值），並繪製分布圖及區塊標註圖")

uploaded_file = st.file_uploader("請選擇一張圖片...", type=["jpg", "jpeg", "png", "bmp"])
if uploaded_file:
    img_pil = Image.open(uploaded_file).convert("RGB")
    st.image(img_pil, caption="上傳的圖片", use_column_width=True)

    blocks = analyze_image_pil(img_pil)
    if blocks:
        conc_list = [round(c, 3) for (_, _, _, c) in blocks]
        most_common_value, _ = Counter(conc_list).most_common(1)[0]
        max_value = max(conc_list)

        # 取範圍內區塊資料
        highlight_blocks = [(x, y, c) for (x, y, _, c) in blocks if most_common_value <= round(c, 3) <= max_value]
        highlight_range = [round(c, 3) for (_, _, _, c) in blocks if most_common_value <= round(c, 3) <= max_value]

        st.success(f"🌟 水楊酸濃度範圍：**{most_common_value:.2%} ~ {max_value:.2%}**，共 {len(highlight_blocks)} 區塊")

        # 直方圖
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.hist(conc_list, bins=30, color='lightgray', edgecolor='black', label='All')
        ax.hist(highlight_range, bins=30, color='green', alpha=0.6, label='Most Common ~ Max')
        ax.set_xlabel('Salicylic Acid Concentration (%)')
        ax.set_ylabel('Block Count')
        ax.set_title('Distribution of Estimated Salicylic Acid Concentration')
        ax.legend()
        st.pyplot(fig)

        # 圖像上框出範圍內區塊
        draw = ImageDraw.Draw(img_pil)
        block_size = 16
        for x, y, c in highlight_blocks:
            draw.rectangle([x, y, x+block_size, y+block_size], outline="green", width=2)

        st.image(img_pil, caption="圈選出眾數~最大值區域", use_column_width=True)
    else:
        st.warning("⚠️ 沒有偵測到有效的水楊酸濃度區塊。")
