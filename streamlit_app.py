# ✅ Analysis steps after correction
if "corrected_image" in st.session_state:
    upper_y, lower_y, left_x, right_x = st.session_state.scaling_info
    img_width, img_height = st.session_state.corrected_image.size

    st.write("Double click 4 points on the corrected image:")
    st.write("Order: First 2 for horizontal line, Next 2 for linear line")

    # Initialize combined points
    if "analysis_points" not in st.session_state:
        st.session_state.analysis_points = []

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

    if st.button("Reset Analysis Points"):
        st.session_state.analysis_points = []