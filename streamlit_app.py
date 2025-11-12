import streamlit as st
from PIL import Image, ImageDraw
from streamlit_image_coordinates import streamlit_image_coordinates
import numpy as np
import cv2

st.title("Image Upload and Perspective Correction")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.write("Double click on the four corners of a known grid to perform a perspective transform.")
    st.write("Order: Top-Left, Top-Right, Bottom-Right, Bottom-Left")
    image = Image.open(uploaded_file)

    # Resize image for display
    display_width = 600
    w_percent = display_width / float(image.size[0])
    new_height = int(float(image.size[1]) * w_percent)
    image = image.resize((display_width, new_height))

    # Initialize session state
    if "coords" not in st.session_state:
        st.session_state.coords = []
    if "line_coords" not in st.session_state:
        st.session_state.line_coords = []

    # Draw markers for first step
    img_with_points = image.copy()
    draw = ImageDraw.Draw(img_with_points)
    for point in st.session_state.coords:
        x, y = point["x"], point["y"]
        r = 4
        draw.ellipse((x - r, y - r, x + r, y + r), fill="red", outline="black")

    # Clickable image for first step
    coords = streamlit_image_coordinates(img_with_points)
    if coords and len(st.session_state.coords) < 4:
        st.session_state.coords.append(coords)

    st.write(f"Selected Points: {st.session_state.coords}")

    if st.button("Reset Points"):
        st.session_state.coords = []
        st.session_state.line_coords = []
        if "corrected_image" in st.session_state:
            del st.session_state.corrected_image

    # Perspective correction
    if len(st.session_state.coords) == 4 and "corrected_image" not in st.session_state:
        st.success("You have selected 4 points!")
        st.write("Next: Enter [y_min, y_max, x_min, x_max] for scaling (not used in correction).")
        user_input = st.text_input("Example: [0, 400, 0, 600]", "[0, 400, 0, 600]")

        if st.button("Perform Perspective Correction"):
            try:
                y_min, y_max, x_min, x_max = eval(user_input)

                src_pts = np.array([[p["x"], p["y"]] for p in st.session_state.coords], dtype=np.float32)
                width, height = 600, 400
                dst_pts = np.array([[0, 0], [width, 0], [width, height], [0, height]], dtype=np.float32)

                img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
                warped = cv2.warpPerspective(img_cv, matrix, (width, height))

                corrected_image = Image.fromarray(cv2.cvtColor(warped, cv2.COLOR_BGR2RGB))
                st.session_state.corrected_image = corrected_image
                st.session_state.scaling_info = (y_min, y_max, x_min, x_max)

            except Exception as e:
                st.error(f"Error: {e}")

# ✅ Display corrected image if available
if "corrected_image" in st.session_state:
    st.image(st.session_state.corrected_image, caption="Perspective Corrected Image", use_column_width=True)
    y_min, y_max, x_min, x_max = st.session_state.scaling_info

    # Second step: click two points
    st.write("Now click two points on the corrected image to define a horizontal line.")
    img_line = st.session_state.corrected_image.copy()
    draw_line = ImageDraw.Draw(img_line)
    for point in st.session_state.line_coords:
        lx, ly = point["x"], point["y"]
        r = 4
        draw_line.ellipse((lx - r, ly - r, lx + r, ly + r), fill="blue", outline="black")

    line_click = streamlit_image_coordinates(img_line)
    if line_click and len(st.session_state.line_coords) < 2:
        st.session_state.line_coords.append(line_click)

    st.write(f"Line Points: {st.session_state.line_coords}")

    if len(st.session_state.line_coords) == 2:
        st.success("Two points selected!")
        avg_y_pixel = (st.session_state.line_coords[0]["y"] + st.session_state.line_coords[1]["y"]) / 2
        img_width, img_height = st.session_state.corrected_image.size

        # Map to real-world coordinates
        real_y = y_min + (avg_y_pixel / img_height) * (y_max - y_min)
        st.write(f"Horizontal line corresponds to y = {real_y:.2f} (real-world units)")