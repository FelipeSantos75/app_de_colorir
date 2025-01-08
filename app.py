import tkinter as tk
from tkinter import filedialog
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
from PIL import Image, ImageTk

def select_image():
    file_path = filedialog.askopenfilename(filetypes=[("SVG Files", "*.svg")])
    if file_path:
        global original_image
        original_image = svg2rlg(file_path)
        display_image(original_image)

def colorize_image():
    if original_image:
        colorized_drawing = original_image
        for path in colorized_drawing.contents:
            if path.fillColor:
                path.fillColor = (1, 0, 0, 1)  # Red color (RGB)
        display_image(colorized_drawing)

def display_image(drawing):
    render = renderPM.drawToFile(drawing, 'temp_image.png', fmt='PNG')
    photo = tk.PhotoImage(file='temp_image.png')
    label_image.configure(image=photo)
    label_image.image = photo

# Create the main window
window = tk.Tk()
window.title("SVG Colorizer")

# Create buttons
button_select = tk.Button(window, text="Select Image", command=select_image)
button_select.pack(pady=10)

button_colorize = tk.Button(window, text="Colorize", command=colorize_image)
button_colorize.pack(pady=10)

# Create image display label
label_image = tk.Label(window)
label_image.pack()

# Start the app
window.mainloop()