import streamlit as st
from PIL import Image, ImageDraw
from streamlit_image_coordinates import streamlit_image_coordinates

st.title("Image Upload and Click Coordinates")

# Upload image
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Load and resize image to width = 800 px
    st.write("Click on the four corners of a known grid to perform a perspective transform.")
    image = Image.open(uploaded_file)
    display_width = 600
    w_percent = display_width / float(image.size[0])
    new_height = int(float(image.size[1]) * w_percent)
    image = image.resize((display_width, new_height))

    # Initialize session state for clicks
    if "coords" not in st.session_state:
        st.session_state.coords = []

    # Draw markers on a copy of the image
    img_with_points = image.copy()
    draw = ImageDraw.Draw(img_with_points)
    for point in st.session_state.coords:
        x, y = point["x"], point["y"]
        r = 8  # radius of marker
        draw.ellipse((x - r, y - r, x + r, y + r), fill="red", outline="black")

    # Display clickable image
    coords = streamlit_image_coordinates(img_with_points)

    # Record up to 4 clicks
    if coords and len(st.session_state.coords) < 4:
        st.session_state.coords.append(coords)

    # Show selected points
    st.write(f"Selected Points: {st.session_state.coords}")

    # Success message when 4 points are selected
    if len(st.session_state.coords) == 4:
        st.success("You have selected 4 points!")

    # Reset button
    if st.button("Reset Points"):
        st.session_state.coords = []