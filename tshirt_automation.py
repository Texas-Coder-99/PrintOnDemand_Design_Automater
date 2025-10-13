import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import textwrap
import csv
import io
import zipfile

st.title("CSV to PNG Image Generator")

# File uploads
csv_file = st.file_uploader("Upload CSV file", type=["csv", "tsv"])
font_file = st.file_uploader("Upload TTF font file", type=["ttf"])

canvas_width = st.number_input("Canvas Width", value=5400)
canvas_height = st.number_input("Canvas Height", value=4500)
canvas_size = (canvas_width, canvas_height)

margin = st.number_input("Margin", value=10)

def calculate_max_lines(canvas_height, font_size, line_spacing=1.2):
    return int(canvas_height / (font_size * line_spacing))

def generate_image(phrase, font_path, canvas_size, margin=10):
    image = Image.new('RGBA', canvas_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    font_size = min(canvas_size) // 10
    line_height = int(font_size * 1.2)
    max_lines = calculate_max_lines(canvas_size[1] - 2 * margin, font_size)

    lines = []
    for part in phrase.split('~'):
        lines.extend(textwrap.wrap(part, width=20))

    lines = lines[:max_lines]

    total_height = len(lines) * line_height
    y_start = (canvas_size[1] - total_height) // 2

    font_file.seek(0)
    font = ImageFont.truetype(io.BytesIO(font_file.read()), font_size)

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        x = (canvas_size[0] - (bbox[2] - bbox[0])) // 2
        draw.text((x, y_start), line, font=font, fill=(0, 0, 0, 255))
        y_start += line_height

    output_buffer = io.BytesIO()
    image.save(output_buffer, format="PNG")
    output_buffer.seek(0)
    return output_buffer

if st.button("Generate Images") and csv_file and font_file:
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        csv_file.seek(0)
        reader = csv.reader(io.TextIOWrapper(csv_file, encoding="utf-8"), delimiter='\t')
        for row in reader:
            if row:
                phrase = row[0]
                img_buffer = generate_image(phrase, font_file, canvas_size, margin)
                zipf.writestr(f"{phrase}.png", img_buffer.read())

    zip_buffer.seek(0)
    st.download_button("Download Images ZIP", data=zip_buffer, file_name="images.zip", mime="application/zip")
