import streamlit as st
from PIL import Image, ImageDraw
from streamlit_image_coordinates import streamlit_image_coordinates
import numpy as np
import cv2

st.title("Image Upload and Perspective Correction")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.write("Double click on the four corners of a known grid to perform a perspective transform.")
    image = Image.open(uploaded_file)

    # Resize image for display
    display_width = 600
    w_percent = display_width / float(image.size[0])
    new_height = int(float(image.size[1]) * w_percent)
    image = image.resize((display_width, new_height))

    # Initialize session state
    if "coords" not in st.session_state:
        st.session_state.coords = []

    # Draw markers
    img_with_points = image.copy()
    draw = ImageDraw.Draw(img_with_points)
    for point in st.session_state.coords:
        x, y = point["x"], point["y"]
        r = 4
        draw.ellipse((x - r, y - r, x + r, y + r), fill="red", outline="black")

    # Clickable image
    coords = streamlit_image_coordinates(img_with_points)
    if coords and len(st.session_state.coords) < 4:
        st.session_state.coords.append(coords)

    st.write(f"Selected Points: {st.session_state.coords}")

    if st.button("Reset Points"):
        st.session_state.coords = []

    # Perspective correction
    if len(st.session_state.coords) == 4:
        st.success("You have selected 4 points!")
        st.write("Next: Enter [y_min, y_max, x_min, x_max] for scaling (not used in correction).")
        user_input = st.text_input("Example: [0, 400, 0, 600]", "[0, 400, 0, 600]")

        if st.button("Perform Perspective Correction"):
            try:
                # Original points
                src_pts = np.array([[p["x"], p["y"]] for p in st.session_state.coords], dtype=np.float32)

                # Destination rectangle size (auto or fixed)
                width = 600
                height = 400
                dst_pts = np.array([[0, 0],
                                    [width, 0],
                                    [width, height],
                                    [0, height]], dtype=np.float32)

                # Convert PIL to OpenCV
                img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

                # Perspective transform
                matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
                warped = cv2.warpPerspective(img_cv, matrix, (width, height))

                # Convert back to PIL
                corrected_image = Image.fromarray(cv2.cvtColor(warped, cv2.COLOR_BGR2RGB))
                st.image(corrected_image, caption="Perspective Corrected Image", use_column_width=True)

                # Parse user input for later scaling
                y_min, y_max, x_min, x_max = eval(user_input)
                st.write(f"Scaling info: y range = {y_min}-{y_max}, x range = {x_min}-{x_max}")

            except Exception as e:
                st.error(f"Error: {e}")