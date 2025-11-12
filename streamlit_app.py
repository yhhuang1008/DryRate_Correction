import streamlit as st
from PIL import Image, ImageDraw
from streamlit_image_coordinates import streamlit_image_coordinates

st.title("Drying Analysis")

# Assume corrected image and scaling info are already available
# For demo, we simulate corrected image as blank canvas
width, height = 600, 400
corrected_image = Image.new("RGB", (width, height), "white")

# Ask user for scaling info
user_input = st.text_input("Enter [y_min, y_max, x_min, x_max]:", "[28, 36, 7, 507]")
y_min, y_max, x_min, x_max = eval(user_input)

# Initialize session state
if "horizontal_points" not in st.session_state:
    st.session_state.horizontal_points = []
if "linear_points" not in st.session_state:
    st.session_state.linear_points = []

# Step 1: Click two points for horizontal line
st.write("Click two points for horizontal line (y = constant)")
img_h = corrected_image.copy()
draw_h = ImageDraw.Draw(img_h)
for pt in st.session_state.horizontal_points:
    draw_h.ellipse((pt["x"]-4, pt["y"]-4, pt["x"]+4, pt["y"]+4), fill="blue", outline="black")

click_h = streamlit_image_coordinates(img_h)
if click_h and len(st.session_state.horizontal_points) < 2:
    st.session_state.horizontal_points.append(click_h)

st.write(f"Horizontal Points: {st.session_state.horizontal_points}")

# Compute horizontal line real-world y
if len(st.session_state.horizontal_points) == 2:
    avg_y_pixel = (st.session_state.horizontal_points[0]["y"] + st.session_state.horizontal_points[1]["y"]) / 2
    real_y_const = y_max - (avg_y_pixel / height) * (y_max - y_min)
    st.success(f"Horizontal line: y = {real_y_const:.2f}")

# Step 2: Click two points for linear line
if len(st.session_state.horizontal_points) == 2:
    st.write("Now click two points for linear line (y = a*x + b)")
    img_l = corrected_image.copy()
    draw_l = ImageDraw.Draw(img_l)
    for pt in st.session_state.linear_points:
        draw_l.ellipse((pt["x"]-4, pt["y"]-4, pt["x"]+4, pt["y"]+4), fill="red", outline="black")

    click_l = streamlit_image_coordinates(img_l)
    if click_l and len(st.session_state.linear_points) < 2:
        st.session_state.linear_points.append(click_l)

    st.write(f"Linear Points: {st.session_state.linear_points}")

# Compute linear line and intersection
if len(st.session_state.linear_points) == 2 and len(st.session_state.horizontal_points) == 2:
    # Convert linear points to real-world coords
    img_width, img_height = corrected_image.size
    p1 = st.session_state.linear_points[0]
    p2 = st.session_state.linear_points[1]

    x1_real = x_min + (p1["x"] / img_width) * (x_max - x_min)
    y1_real = y_max - (p1["y"] / img_height) * (y_max - y_min)
    x2_real = x_min + (p2["x"] / img_width) * (x_max - x_min)
    y2_real = y_max - (p2["y"] / img_height) * (y_max - y_min)

    # Compute slope and intercept
    a = (y2_real - y1_real) / (x2_real - x1_real)
    b = y1_real - a * x1_real

    # Intersection with horizontal line
    x_intersect = (real_y_const - b) / a
    y_intersect = real_y_const

    drying_time = x_intersect - 20
    drying_rate = 720 / drying_time

    st.success(f"Intersection: X = {x_intersect:.2f}, Y = {y_intersect:.2f}")
    st.write(f"Drying time = {drying_time:.2f} s")
    st.write(f"Drying rate = {drying_rate:.2f} ml/h")