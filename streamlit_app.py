# After showing corrected_image and parsing y_min, y_max, x_min, x_max
st.write("Now click two points on the corrected image to define a horizontal line.")

# Initialize second click set
if "line_coords" not in st.session_state:
    st.session_state.line_coords = []

# Draw markers on corrected image
img_line = corrected_image.copy()
draw_line = ImageDraw.Draw(img_line)
for point in st.session_state.line_coords:
    x, y = point["x"], point["y"]
    r = 4
    draw_line.ellipse((x - r, y - r, x + r, y + r), fill="blue", outline="black")

# Clickable corrected image
line_click = streamlit_image_coordinates(img_line)
if line_click and len(st.session_state.line_coords) < 2:
    st.session_state.line_coords.append(line_click)

st.write(f"Line Points: {st.session_state.line_coords}")

if len(st.session_state.line_coords) == 2:
    st.success("Two points selected!")
    # Compute horizontal line y value
    avg_y_pixel = (st.session_state.line_coords[0]["y"] + st.session_state.line_coords[1]["y"]) / 2
    real_y = y_min + (avg_y_pixel / corrected_image.size[1]) * (y_max - y_min)
    st.write(f"Horizontal line corresponds to y = {real_y:.2f} (real-world units)")