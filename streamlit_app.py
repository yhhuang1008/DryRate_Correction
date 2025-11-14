import streamlit as st
from PIL import Image, ImageDraw
from streamlit_image_coordinates import streamlit_image_coordinates
import numpy as np
import cv2

st.title("Drying Analysis with Perspective Correction")

# Upload image
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.write("Double click four corners of the grid (Order: Top-Left, Top-Right, Bottom-Right, Bottom-Left)")
    image = Image.open(uploaded_file)

    # Resize for display
    display_width = 600
    w_percent = display_width / float(image.size[0])
    new_height = int(float(image.size[1]) * w_percent)
    image = image.resize((display_width, new_height))

    # Initialize session state
    if "coords" not in st.session_state:
        st.session_state.coords = []
    if "analysis_points" not in st.session_state:
        st.session_state.analysis_points = []

    # Draw markers for 4 corners
    img_with_points = image.copy()
    draw = ImageDraw.Draw(img_with_points)
    for pt in st.session_state.coords:
        draw.ellipse((pt["x"]-4, pt["y"]-4, pt["x"]+4, pt["y"]+4), fill="red", outline="black")

    # Clickable image for corners
    click = streamlit_image_coordinates(img_with_points)
    if click and len(st.session_state.coords) < 4:
        st.session_state.coords.append(click)

    st.write(f"Selected Corners: {st.session_state.coords}")

    if st.button("Reset All"):
        st.session_state.coords = []
        st.session_state.analysis_points = []
        if "corrected_image" in st.session_state:
            del st.session_state.corrected_image

    # Perspective correction after 4 points
    if len(st.session_state.coords) == 4 and "corrected_image" not in st.session_state:
        st.success("Corners selected!")
        user_input = st.text_input("Enter [upper_y, lower_y, left_x, right_x]:", "[36, 28, 7, 507]")

        if st.button("Perform Correction"):
            try:
                upper_y, lower_y, left_x, right_x = eval(user_input)

                # Original points
                src_pts = np.array([[p["x"], p["y"]] for p in st.session_state.coords], dtype=np.float32)
                width, height = 600, 400
                dst_pts = np.array([[0, 0], [width, 0], [width, height], [0, height]], dtype=np.float32)

                img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
                warped = cv2.warpPerspective(img_cv, matrix, (width, height))

                corrected_image = Image.fromarray(cv2.cvtColor(warped, cv2.COLOR_BGR2RGB))
                st.session_state.corrected_image = corrected_image
                st.session_state.scaling_info = (upper_y, lower_y, left_x, right_x)

            except Exception as e:
                st.error(f"Error: {e}")

# ✅ Combined analysis step
if "corrected_image" in st.session_state:
    upper_y, lower_y, left_x, right_x = st.session_state.scaling_info
    img_width, img_height = st.session_state.corrected_image.size

    st.write("Double click 4 points on the corrected image:")
    st.write("Order: First 2 for horizontal line, Next 2 for linear line")

    # Draw points on image
    img_combined = st.session_state.corrected_image.copy()
    draw_combined = ImageDraw.Draw(img_combined)
    colors = ["blue", "blue", "red", "red"]  # First two blue, next two red
    for i, pt in enumerate(st.session_state.analysis_points):
        draw_combined.ellipse((pt["x"]-4, pt["y"]-4, pt["x"]+4, pt["y"]+4), fill=colors[i], outline="black")

    click_combined = streamlit_image_coordinates(img_combined)
    if click_combined and len(st.session_state.analysis_points) < 4:
        st.session_state.analysis_points.append(click_combined)

    # Compute after 4 points
    if len(st.session_state.analysis_points) == 4:
        # Horizontal line (first two points)
        p_h1, p_h2 = st.session_state.analysis_points[:2]
        avg_y_pixel = (p_h1["y"] + p_h2["y"]) / 2
        real_y_const = upper_y - (avg_y_pixel / img_height) * (upper_y - lower_y)

        # Linear line (next two points)
        p_l1, p_l2 = st.session_state.analysis_points[2:]
        x1_real = left_x + (p_l1["x"] / img_width) * (right_x - left_x)
        y1_real = upper_y - (p_l1["y"] / img_height) * (upper_y - lower_y)
        x2_real = left_x + (p_l2["x"] / img_width) * (right_x - left_x)
        y2_real = upper_y - (p_l2["y"] / img_height) * (upper_y - lower_y)

        # Compute line equation
        a = (y2_real - y1_real) / (x2_real - x1_real)
        b = y1_real - a * x1_real

        # Intersection
        x_intersect = (real_y_const - b) / a
        y_intersect = real_y_const

        drying_time = x_intersect - 20
        drying_rate = 720 / drying_time

        st.success(f"Horizontal line: y = {real_y_const:.2f}")
        st.success(f"Intersection: X = {x_intersect:.2f}, Y = {y_intersect:.2f}")
        st.write(f"Drying time = {drying_time:.2f} s")
        st.write(f"Drying rate = {drying_rate:.2f} ml/h")

        # ✅ NEW FEATURE: Display linear equation and allow user input for y
        st.subheader("Linear Fit and Custom Calculation")
        st.write(f"Linear equation: y = {a:.4f}x + {b:.4f}")

        user_y = st.number_input("Enter a Y value to calculate X, Drying Time, and Rate:", value=real_y_const)
        if st.button("Calculate from Y"):
            x_from_y = (user_y - b) / a
            drying_time_custom = x_from_y - 20
            drying_rate_custom = 720 / drying_time_custom
            st.success(f"For y = {user_y:.2f}: X = {x_from_y:.2f}")
            st.write(f"Drying time = {drying_time_custom:.2f} s")
            st.write(f"Drying rate = {drying_rate_custom:.2f} ml/h")

    if st.button("Reset Analysis Points"):
        st.session_state.analysis_points = []