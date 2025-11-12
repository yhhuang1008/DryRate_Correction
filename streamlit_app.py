import streamlit as st
from PIL import Image

st.title("Image Upload and Click Coordinates")

# Upload image
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Click on the image below", use_column_width=True)

    # Initialize session state for clicks
    if "coords" not in st.session_state:
        st.session_state.coords = []

    # Display clickable image
    click = st.image(image, caption="Click to select points", use_column_width=True)

    # Use Streamlit's image click feature
    # (streamlit-image-coordinates is needed)
    from streamlit_image_coordinates import streamlit_image_coordinates

    coords = streamlit_image_coordinates(image)
    if coords and len(st.session_state.coords) < 4:
        st.session_state.coords.append(coords)

    st.write(f"Selected Points: {st.session_state.coords}")
    if len(st.session_state.coords) == 4:
        st.success("You have selected 4 points!")