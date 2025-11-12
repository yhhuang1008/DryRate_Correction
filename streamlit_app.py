import streamlit as st
from PIL import Image
from streamlit_image_coordinates import streamlit_image_coordinates

st.title("Image Upload and Click Coordinates")

# Upload image
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)

    # Initialize session state for clicks
    if "coords" not in st.session_state:
        st.session_state.coords = []

    # Display clickable image (only once)
    coords = streamlit_image_coordinates(image)

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