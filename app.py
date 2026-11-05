import streamlit as st
from PIL import (
    Image, ImageEnhance, ImageFilter,
    ImageDraw, ImageFont, ImageOps
)
import matplotlib.pyplot as plt
from io import BytesIO
from pathlib import Path
from rembg import remove

# =========================
# Page Configuration
# =========================
st.set_page_config(
    page_title="BrightFix | Photo Editor",
    page_icon="📸",
    layout="wide"
)

# =========================
# Custom CSS
# =========================
st.markdown("""
<style>
.stApp {
    background-color: #f4f7fc;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
.bf-header {
    background: linear-gradient(120deg, #123b70, #2878d4);
    padding: 28px;
    border-radius: 16px;
    color: white;
    margin-bottom: 24px;
}
.bf-header h1 {
    color: white;
    margin: 0;
    font-size: 36px;
}
.bf-header p {
    color: #e7f1ff;
    margin: 8px 0 0 0;
}
</style>
""", unsafe_allow_html=True)

# =========================
# Header
# =========================
st.markdown("""
<div class="bf-header">
    <h1>📸 BrightFix</h1>
    <p>Your simple photo editing workspace</p>
</div>
""", unsafe_allow_html=True)

st.write(
    "Upload a photo, edit it, analyze it, "
    "and download your edited image."
)

# =========================
# Reset Function
# =========================
def reset_adjustments():

    defaults = {
        "brightness": 0,
        "contrast": 1.0,
        "saturation": 1.0,
        "sharpness": 1.0,
        "operation": "None",
        "show_name_on_image": False,
        "resize_image": False,
        "maintain_ratio": True,
        "crop_image": False,
        "crop_left": 0,
        "crop_top": 0,
        "crop_right": 500,
        "crop_bottom": 500,
        "threshold": 128,
        "noise_reduction": "None",
        "background_blur": False,
        "blur_strength": 10,
        "watermark_enabled": False,
        "watermark_text": "BrightFix",
        "watermark_position": "Bottom Right",
        "show_comparison": True
    }

    for key, value in defaults.items():
        st.session_state[key] = value


# =========================
# Sidebar
# =========================
st.sidebar.title("🛠️ Editing Studio")

uploaded_file = st.sidebar.file_uploader(
    "📁 Upload an image",
    type=["jpg", "jpeg", "png"],
    key="uploaded_image"
)

# =========================
# Basic Adjustments
# =========================
st.sidebar.divider()
st.sidebar.subheader("🎚️ Basic Adjustments")

brightness = st.sidebar.slider(
    "☀️ Brightness",
    -100, 100, 0,
    key="brightness"
)

contrast = st.sidebar.slider(
    "◐ Contrast",
    0.5, 2.0, 1.0,
    step=0.1,
    key="contrast"
)

saturation = st.sidebar.slider(
    "🌈 Saturation",
    0.0, 2.0, 1.0,
    step=0.1,
    key="saturation"
)

sharpness = st.sidebar.slider(
    "🔍 Sharpness",
    0.0, 3.0, 1.0,
    step=0.1,
    key="sharpness"
)

# =========================
# Image Effects
# =========================
st.sidebar.divider()
st.sidebar.subheader("🎨 Image Effects")

operation = st.sidebar.selectbox(
    "Choose an Effect",
    [
        "None",
        "Grayscale",
        "Sepia",
        "Blur",
        "Sharpen",
        "Negative",
        "Thresholding",
        "Edge Detection",
        "Rotate 90°",
        "Rotate 180°",
        "Rotate 270°",
        "Flip Horizontal",
        "Flip Vertical"
    ],
    key="operation"
)

if operation == "Thresholding":

    threshold = st.sidebar.slider(
        "Threshold Value",
        0, 255, 128,
        key="threshold"
    )

# =========================
# Noise Reduction
# =========================
st.sidebar.divider()
st.sidebar.subheader("✨ Image Enhancement")

noise_reduction = st.sidebar.selectbox(
    "Noise Reduction",
    ["None", "Light", "Medium", "Strong"],
    key="noise_reduction"
)

# =========================
# Background Blur Settings
# =========================
st.sidebar.divider()
st.sidebar.subheader("🌫️ Background Blur")

background_blur = st.sidebar.checkbox(
    "Enable Background Blur",
    key="background_blur"
)

if background_blur:

    blur_strength = st.sidebar.slider(
        "Background Blur Strength",
        min_value=1,
        max_value=30,
        value=10,
        key="blur_strength"
    )

    st.sidebar.caption(
        "Keeps the foreground sharp and blurs the background."
    )

# =========================
# Image Crop
# =========================
st.sidebar.divider()
st.sidebar.subheader("✂️ Image Crop")

crop_image = st.sidebar.checkbox(
    "Enable Image Crop",
    key="crop_image"
)

if crop_image:

    st.sidebar.caption(
        "Enter crop boundaries in pixels."
    )

    crop_left = st.sidebar.number_input(
        "Left",
        min_value=0,
        max_value=10000,
        value=0,
        key="crop_left"
    )

    crop_top = st.sidebar.number_input(
        "Top",
        min_value=0,
        max_value=10000,
        value=0,
        key="crop_top"
    )

    crop_right = st.sidebar.number_input(
        "Right",
        min_value=1,
        max_value=10000,
        value=500,
        key="crop_right"
    )

    crop_bottom = st.sidebar.number_input(
        "Bottom",
        min_value=1,
        max_value=10000,
        value=500,
        key="crop_bottom"
    )

# =========================
# Image Resize
# =========================
st.sidebar.divider()
st.sidebar.subheader("📐 Image Resize")

resize_image = st.sidebar.checkbox(
    "Enable Image Resize",
    key="resize_image"
)

if resize_image:

    new_width = st.sidebar.number_input(
        "New Width (px)",
        min_value=1,
        max_value=5000,
        value=800,
        key="new_width"
    )

    new_height = st.sidebar.number_input(
        "New Height (px)",
        min_value=1,
        max_value=5000,
        value=600,
        key="new_height"
    )

    maintain_ratio = st.sidebar.checkbox(
        "Maintain Aspect Ratio",
        value=True,
        key="maintain_ratio"
    )

# =========================
# Watermark
# =========================
st.sidebar.divider()
st.sidebar.subheader("💧 Watermark")

watermark_enabled = st.sidebar.checkbox(
    "Enable Watermark",
    key="watermark_enabled"
)

if watermark_enabled:

    watermark_text = st.sidebar.text_input(
        "Watermark Text",
        key="watermark_text"
    )

    watermark_position = st.sidebar.selectbox(
        "Watermark Position",
        [
            "Top Left",
            "Top Right",
            "Bottom Left",
            "Bottom Right",
            "Center"
        ],
        key="watermark_position"
    )

# =========================
# Other Options
# =========================
st.sidebar.divider()
st.sidebar.subheader("🖼️ Other Options")

show_name_on_image = st.sidebar.checkbox(
    "Write file name on image",
    key="show_name_on_image"
)

show_comparison = st.sidebar.checkbox(
    "Show Before & After Comparison",
    value=True,
    key="show_comparison"
)

# =========================
# Reset Button
# =========================
st.sidebar.divider()

st.sidebar.button(
    "↩️ Reset All",
    on_click=reset_adjustments,
    use_container_width=True
)

# =========================
# Main Application
# =========================
if uploaded_file is not None:

    try:

        # =========================
        # Read Original Image
        # =========================
        opened_image = Image.open(uploaded_file)

        image_format = opened_image.format or "Unknown"

        original = ImageOps.exif_transpose(
            opened_image
        ).convert("RGB")

        file_name = Path(uploaded_file.name).name

        edited = original.copy()

        # =========================
        # Brightness
        # =========================
        brightness_factor = max(
            0,
            1 + brightness / 100
        )

        edited = ImageEnhance.Brightness(
            edited
        ).enhance(brightness_factor)

        # =========================
        # Contrast
        # =========================
        edited = ImageEnhance.Contrast(
            edited
        ).enhance(contrast)

        # =========================
        # Saturation
        # =========================
        edited = ImageEnhance.Color(
            edited
        ).enhance(saturation)

        # =========================
        # Sharpness
        # =========================
        edited = ImageEnhance.Sharpness(
            edited
        ).enhance(sharpness)

        # =========================
        # Image Effects
        # =========================
        if operation == "Grayscale":

            edited = edited.convert("L").convert("RGB")

        elif operation == "Sepia":

            gray = ImageOps.grayscale(edited)

            edited = ImageOps.colorize(
                gray,
                black="#3b2416",
                white="#f4d7a1"
            ).convert("RGB")

        elif operation == "Blur":

            edited = edited.filter(
                ImageFilter.GaussianBlur(radius=2)
            )

        elif operation == "Sharpen":

            edited = edited.filter(
                ImageFilter.SHARPEN
            )

        elif operation == "Negative":

            edited = Image.eval(
                edited,
                lambda pixel: 255 - pixel
            )

        elif operation == "Thresholding":

            gray = edited.convert("L")

            edited = gray.point(
                lambda pixel: 255 if pixel >= threshold else 0
            ).convert("RGB")

        elif operation == "Edge Detection":

            edited = edited.filter(
                ImageFilter.FIND_EDGES
            ).convert("RGB")

        elif operation == "Rotate 90°":

            edited = edited.rotate(90, expand=True)

        elif operation == "Rotate 180°":

            edited = edited.rotate(180, expand=True)

        elif operation == "Rotate 270°":

            edited = edited.rotate(270, expand=True)

        elif operation == "Flip Horizontal":

            edited = edited.transpose(
                Image.Transpose.FLIP_LEFT_RIGHT
            )

        elif operation == "Flip Vertical":

            edited = edited.transpose(
                Image.Transpose.FLIP_TOP_BOTTOM
            )

        # =========================
        # Noise Reduction
        # =========================
        if noise_reduction == "Light":

            edited = edited.filter(
                ImageFilter.MedianFilter(size=3)
            )

        elif noise_reduction == "Medium":

            edited = edited.filter(
                ImageFilter.MedianFilter(size=5)
            )

        elif noise_reduction == "Strong":

            edited = edited.filter(
                ImageFilter.MedianFilter(size=7)
            )

        # =========================
        # Image Crop
        # =========================
        if crop_image:

            img_width, img_height = edited.size

            left = max(
                0, min(int(crop_left), img_width - 1)
            )

            top = max(
                0, min(int(crop_top), img_height - 1)
            )

            right = max(
                1, min(int(crop_right), img_width)
            )

            bottom = max(
                1, min(int(crop_bottom), img_height)
            )

            if right > left and bottom > top:

                edited = edited.crop(
                    (left, top, right, bottom)
                )

            else:

                st.warning(
                    "Invalid crop values. Please check your values."
                )

        # =========================
        # Image Resize
        # =========================
        if resize_image:

            if maintain_ratio:

                original_width, original_height = edited.size

                ratio = min(
                    new_width / original_width,
                    new_height / original_height
                )

                final_width = max(
                    1, int(original_width * ratio)
                )

                final_height = max(
                    1, int(original_height * ratio)
                )

            else:

                final_width = int(new_width)
                final_height = int(new_height)

            edited = edited.resize(
                (final_width, final_height),
                Image.Resampling.LANCZOS
            )

        # =========================
        # AI Background Blur
        # =========================
        if background_blur:

            with st.spinner(
                "AI is separating the foreground and background..."
            ):

                # Create a sharp foreground with transparency
                foreground = remove(
                    edited.convert("RGB")
                ).convert("RGBA")

                # Create blurred background
                blurred_background = edited.filter(
                    ImageFilter.GaussianBlur(
                        radius=blur_strength
                    )
                ).convert("RGBA")

                # Combine sharp foreground and blurred background
                edited = Image.alpha_composite(
                    blurred_background,
                    foreground
                ).convert("RGB")

        # =========================
        # Watermark
        # =========================
        if watermark_enabled and watermark_text.strip():

            watermark_layer = Image.new(
                "RGBA",
                edited.size,
                (0, 0, 0, 0)
            )

            draw = ImageDraw.Draw(watermark_layer)

            font = ImageFont.load_default()

            text_bbox = draw.textbbox(
                (0, 0),
                watermark_text,
                font=font
            )

            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]

            padding = 15

            if watermark_position == "Top Left":

                x, y = padding, padding

            elif watermark_position == "Top Right":

                x = max(
                    padding,
                    edited.width - text_width - padding
                )
                y = padding

            elif watermark_position == "Bottom Left":

                x = padding
                y = max(
                    padding,
                    edited.height - text_height - padding
                )

            elif watermark_position == "Center":

                x = max(
                    0,
                    (edited.width - text_width) // 2
                )
                y = max(
                    0,
                    (edited.height - text_height) // 2
                )

            else:

                x = max(
                    padding,
                    edited.width - text_width - padding
                )

                y = max(
                    padding,
                    edited.height - text_height - padding
                )

            draw.text(
                (x, y),
                watermark_text,
                fill=(255, 255, 255, 170),
                font=font
            )

            edited = Image.alpha_composite(
                edited.convert("RGBA"),
                watermark_layer
            ).convert("RGB")

        # =========================
        # File Name Overlay
        # =========================
        if show_name_on_image:

            draw = ImageDraw.Draw(edited)

            font = ImageFont.load_default()

            text_bbox = draw.textbbox(
                (0, 0),
                file_name,
                font=font
            )

            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]

            padding = 10

            x = 10

            y = max(
                10,
                edited.height - text_height - padding * 2 - 10
            )

            draw.rectangle(
                [
                    x,
                    y,
                    min(
                        edited.width - 1,
                        x + text_width + padding * 2
                    ),
                    min(
                        edited.height - 1,
                        y + text_height + padding * 2
                    )
                ],
                fill="black"
            )

            draw.text(
                (x + padding, y + padding),
                file_name,
                fill="white",
                font=font
            )

        # =========================
        # Image Information
        # =========================
        st.divider()
        st.subheader("🖼️ Image Information")

        st.markdown(
            f"**📁 File Name:** `{file_name}`"
        )

        info1, info2, info3 = st.columns(3)

        with info1:

            st.metric(
                "Original Width",
                f"{original.width} px"
            )

        with info2:

            st.metric(
                "Original Height",
                f"{original.height} px"
            )

        with info3:

            st.metric(
                "Format",
                image_format
            )

        st.metric(
            "File Size",
            f"{uploaded_file.size / 1024:.2f} KB"
        )

        # =========================
        # Edited Dimensions
        # =========================
        st.subheader("📐 Edited Image Dimensions")

        size1, size2 = st.columns(2)

        with size1:

            st.metric(
                "Edited Width",
                f"{edited.width} px"
            )

        with size2:

            st.metric(
                "Edited Height",
                f"{edited.height} px"
            )

        # =========================
        # Before & After Comparison
        # =========================
        st.divider()
        st.subheader("📷 Image Preview")

        if show_comparison:

            col1, col2 = st.columns(2, gap="large")

            with col1:

                st.markdown("### Original Image")

                st.image(
                    original,
                    caption="Original Image",
                    use_container_width=True
                )

            with col2:

                st.markdown("### Edited Image")

                st.image(
                    edited,
                    caption="Edited Image",
                    use_container_width=True
                )

        else:

            st.markdown("### Edited Image")

            st.image(
                edited,
                use_container_width=True
            )

        # =========================
        # Histogram
        # =========================
        st.divider()
        st.subheader("📊 Image Histogram")

        fig, ax = plt.subplots(figsize=(10, 3))

        original_gray = original.convert("L")
        edited_gray = edited.convert("L")

        ax.hist(
            list(original_gray.getdata()),
            bins=256,
            range=(0, 256),
            alpha=0.4,
            label="Original"
        )

        ax.hist(
            list(edited_gray.getdata()),
            bins=256,
            range=(0, 256),
            alpha=0.6,
            label="Edited"
        )

        ax.set_xlabel("Pixel Intensity")
        ax.set_ylabel("Number of Pixels")
        ax.set_title("Original vs Edited Image Histogram")
        ax.set_xlim(0, 255)
        ax.legend()

        fig.tight_layout()

        st.pyplot(fig)
        plt.close(fig)

        # =========================
        # Download
        # =========================
        st.divider()
        st.subheader("💾 Save Your Photo")

        buffer = BytesIO()

        edited.save(
            buffer,
            format="PNG"
        )

        buffer.seek(0)

        download_name = (
            f"{Path(file_name).stem}_edited.png"
        )

        st.download_button(
            label="⬇️ Download Edited Image",
            data=buffer.getvalue(),
            file_name=download_name,
            mime="image/png",
            use_container_width=True
        )

        st.success(
            "Your image has been processed successfully!"
        )

    except Exception as error:

        st.error(
            "Unable to process this image."
        )

        st.caption(
            f"Error details: {error}"
        )

else:

    st.info(
        "👈 Start by uploading a JPG or PNG image "
        "from the sidebar."
    )

    st.markdown("### What you can do with BrightFix")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown("#### ☀️ Adjust")

        st.write(
            "Change brightness, contrast, saturation "
            "and sharpness."
        )

    with col2:

        st.markdown("#### 🎨 Enhance")

        st.write(
            "Apply grayscale, sepia, blur, sharpen, "
            "negative, thresholding and edge detection."
        )

    with col3:

        st.markdown("#### 📊 Analyze")

        st.write(
            "View image information, dimensions "
            "and original vs edited histogram."
        )

    st.markdown("### More Editing Tools")

    st.write(
        "Crop, resize, maintain aspect ratio, "
        "AI background blur, noise reduction and watermark."
    )