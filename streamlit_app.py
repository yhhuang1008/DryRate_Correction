import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.title("Perspective Correction & Intersection Tool")

# ============================
# Upload Image
# ============================
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")  # Ensure proper format
    st.image(image, caption="Uploaded Image", use_column_width=True)
    img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # ============================
    # Collect Points
    # ============================
    st.write("Click 4 points for perspective correction, then 2 for horizontal line, 2 for linear curve.")
    from streamlit_drawable_canvas import st_canvas

    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=3,
        stroke_color="#FF0000",
        background_image=image,  # PIL image works now
        update_streamlit=True,
        height=image.height,
        width=image.width,
        drawing_mode="point",
        key="canvas",
    )

    if canvas_result.json_data is not None:
        points = [(obj["left"], obj["top"]) for obj in canvas_result.json_data["objects"]]
        st.write(f"Points selected: {points}")

        # ============================
        # Axis Range Inputs
        # ============================
        if len(points) >= 4:
            st.subheader("Enter Axis Ranges")
            x_min = st.number_input("X min", value=26.0)
            x_max = st.number_input("X max", value=37.0)
            y_min = st.number_input("Y min", value=0.0)
            y_max = st.number_input("Y max", value=1207.0)

            if st.button("Compute"):
                # Perspective correction
                pts_src = np.array(points[:4], dtype="float32")
                width_top = np.linalg.norm(pts_src[0] - pts_src[1])
                width_bottom = np.linalg.norm(pts_src[2] - pts_src[3])
                height_left = np.linalg.norm(pts_src[0] - pts_src[3])
                height_right = np.linalg.norm(pts_src[1] - pts_src[2])
                width = int(max(width_top, width_bottom))
                height = int(max(height_left, height_right))

                pts_dst = np.array([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]], dtype="float32")
                M = cv2.getPerspectiveTransform(pts_src, pts_dst)
                warped_img = cv2.warpPerspective(img_cv, M, (width, height))

                # Draw intersection if enough points
                if len(points) >= 8:
                    h_points = points[4:6]
                    l_points = points[6:8]

                    def pixel_to_real(x, y):
                        real_x = x_min + (x / width) * (x_max - x_min)
                        real_y = y_max - (y / height) * (y_max - y_min)
                        return real_x, real_y

                    h_real = [pixel_to_real(px, py) for px, py in h_points]
                    l_real = [pixel_to_real(px, py) for px, py in l_points]

                    y_h = (h_real[0][1] + h_real[1][1]) / 2
                    x1, y1 = l_real[0]
                    x2, y2 = l_real[1]
                    a = (y2 - y1) / (x2 - x1)
                    b = y1 - a * x1
                    x_intersect = (y_h - b) / a
                    y_intersect = y_h

                    st.success(f"Intersection: x = {x_intersect:.1f}, y = {y_intersect:.0f}")
                    st.write(f"Drying time: {y_intersect-20:.0f} s")
                    st.write(f"Drying rate: {720/(y_intersect-20):.2f} ml/hr")

                    # Draw lines and intersection point
                    img_display = warped_img.copy()
                    pt1_h = (0, int((height * (y_max - y_h)) / (y_max - y_min)))
                    pt2_h = (width, pt1_h[1])
                    cv2.line(img_display, pt1_h, pt2_h, (255, 0, 0), 2)

                    pt1_l = (0, int((height * (y_max - (a * x_min + b))) / (y_max - y_min)))
                    pt2_l = (width, int((height * (y_max - (a * x_max + b))) / (y_max - y_min)))
                    cv2.line(img_display, pt1_l, pt2_l, (0, 0, 255), 2)

                    px_intersect = int((width * (x_intersect - x_min)) / (x_max - x_min))
                    py_intersect = int((height * (y_max - y_intersect)) / (y_max - y_min))
                    cv2.circle(img_display, (px_intersect, py_intersect), 8, (0, 255, 0), -1)
                    cv2.putText(img_display, f"t={y_intersect:.0f}s", (px_intersect + 10, py_intersect - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

                    st.image(img_display, caption="Result with Intersection", channels="BGR")

                else:
                    st.warning("Please select 8 points (4 for correction, 2 for horizontal, 2 for linear curve).")
                st.image(warped_img, caption="Corrected Image", channels="BGR")