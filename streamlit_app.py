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
    if "horizontal_points" not in st.session_state:
        st.session_state.horizontal_points = []
    if "linear_points" not in st.session_state:
        st.session_state.linear_points = []

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
        st.session_state.horizontal_points = []
        st.session_state.linear_points = []
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

# ✅ Analysis steps after correction
if "corrected_image" in st.session_state:
    upper_y, lower_y, left_x, right_x = st.session_state.scaling_info
    img_width, img_height = st.session_state.corrected_image.size

    # Step 1: Horizontal line
    st.write("Double click two points for horizontal line (y = constant)")
    img_h = st.session_state.corrected_image.copy()
    draw_h = ImageDraw.Draw(img_h)
    for pt in st.session_state.horizontal_points:
        draw_h.ellipse((pt["x"]-4, pt["y"]-4, pt["x"]+4, pt["y"]+4), fill="blue", outline="black")

    click_h = streamlit_image_coordinates(img_h)
    if click_h and len(st.session_state.horizontal_points) < 2:
        st.session_state.horizontal_points.append(click_h)

    if len(st.session_state.horizontal_points) == 2:
        avg_y_pixel = (st.session_state.horizontal_points[0]["y"] + st.session_state.horizontal_points[1]["y"]) / 2
        real_y_const = upper_y - (avg_y_pixel / img_height) * (upper_y - lower_y)
        st.success(f"Horizontal line: y = {real_y_const:.2f}")

    # Step 2: Linear line
    if len(st.session_state.horizontal_points) == 2:
        st.write("Double click two points for linear line (y = a*x + b)")
        img_l = st.session_state.corrected_image.copy()
        draw_l = ImageDraw.Draw(img_l)
        for pt in st.session_state.linear_points:
            draw_l.ellipse((pt["x"]-4, pt["y"]-4, pt["x"]+4, pt["y"]+4), fill="red", outline="black")

        click_l = streamlit_image_coordinates(img_l)
        if click_l and len(st.session_state.linear_points) < 2:
            st.session_state.linear_points.append(click_l)

    # Compute intersection
    if len(st.session_state.linear_points) == 2 and len(st.session_state.horizontal_points) == 2:
        p1, p2 = st.session_state.linear_points
        x1_real = left_x + (p1["x"] / img_width) * (right_x - left_x)
        y1_real = upper_y - (p1["y"] / img_height) * (upper_y - lower_y)
        x2_real = left_x + (p2["x"] / img_width) * (right_x - left_x)
        y2_real = upper_y - (p2["y"] / img_height) * (upper_y - lower_y)

        a = (y2_real - y1_real) / (x2_real - x1_real)
        b = y1_real - a * x1_real

        x_intersect = (real_y_const - b) / a
        y_intersect = real_y_const

        drying_time = x_intersect - 20
        drying_rate = 720 / drying_time

        st.success(f"Intersection: X = {x_intersect:.2f}, Y = {y_intersect:.2f}")
        st.write(f"Drying time = {drying_time:.2f} s")
        st.write(f"Drying rate = {drying_rate:.2f} ml/h")