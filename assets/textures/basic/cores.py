from PIL import Image
import os

def create_color_images(colors):
    # Create output directory if it doesn't exist
    if not os.path.exists('color_squares'):
        os.makedirs('color_squares')
    
    # Size of the square image (256x256 pixels)
    size = (256, 256)

    # Create an image for each color
    for color in colors:
        # Create new image with RGB mode
        img = Image.new('RGB', size, color)
        
        # Save the image
        filename = f'assets/textures/basic/{color.replace("#", "")}.png'
        
        img.save(filename)
        print(f'"{filename}",')
    


# Example list of web colors
colors = [
    
    '#FF00FF',  # Magenta
    '#00FFFF',  # Cyan
    '#FFFFFF',  # White
    '#000000',   # Black
    '#FFDFC4',  # Very light skin
   '#F0C8A0',  # Light skin
   '#DEB887',  # Light medium skin
   '#D2956B',  # Medium skin
   '#C68642',  # Medium dark skin
   '#8D5524',  # Dark skin
   '#73452E',  # Very dark skin  
   '#4C3024',  # Deep dark skin
   '#B07C6D',  # Rose beige skin
   '#AA7B6C',  # Native/Indigenous light
   '#8B4513',  # Native/Indigenous medium
   '#6B4423',  # Native/Indigenous dark
   # Tons de Azul
   '#000080',  # Navy Blue
   '#0000FF',  # Blue
   '#1E90FF',  # Dodger Blue 
   '#87CEEB',  # Sky Blue
   
   # Tons de Vermelho
   '#8B0000',  # Dark Red
   '#FF0000',  # Red
   '#DC143C',  # Crimson
   '#FA8072',  # Salmon
   
   # Tons de Amarelo
   '#FFD700',  # Gold Yellow
   '#FFFF00',  # Yellow
   '#F0E68C',  # Khaki
   '#FFFACD',  # Lemon Chiffon
   
   # Tons de Prata
   '#C0C0C0',  # Silver
   '#A9A9A9',  # Dark Gray
   '#D3D3D3',  # Light Gray
   '#DCDCDC',  # Gainsboro
   
   # Tons de Dourado
   '#FFD700',  # Gold
   '#DAA520',  # Goldenrod
   '#B8860B',  # Dark Goldenrod
   '#CD853F',   # Peru

   # Tons de Vermelho (Arco-íris)
   '#8B0000',  # Dark Red
   '#B22222',  # Fire Brick
   '#CD5C5C',  # Indian Red
   '#FF6347',  # Tomato

   # Tons de Laranja (Arco-íris)
   '#FF4500',  # Orange Red
   '#FF8C00',  # Dark Orange
   '#FFA500',  # Orange
   '#FFB347',  # Light Orange

   # Tons de Amarelo (Arco-íris)
   '#FFD700',  # Gold
   '#FFFF00',  # Yellow
   '#FFFFE0',  # Light Yellow
   '#FFFACD',  # Lemon Chiffon

   # Tons de Verde (Arco-íris)
   '#006400',  # Dark Green
   '#008000',  # Green
   '#32CD32',  # Lime Green
   '#90EE90',  # Light Green

   # Tons de Azul (Arco-íris)
   '#00008B',  # Dark Blue
   '#0000FF',  # Blue
   '#1E90FF',  # Dodger Blue
   '#87CEEB',  # Sky Blue

   # Tons de Anil (Arco-íris)
   '#191970',  # Midnight Blue
   '#4169E1',  # Royal Blue
   '#6495ED',  # Cornflower Blue
   '#B0C4DE',  # Light Steel Blue

   # Tons de Violeta (Arco-íris)
   '#4B0082',  # Indigo
   '#8A2BE2',  # Blue Violet
   '#9370DB',  # Medium Purple
   '#DDA0DD',   # Plum
]

# Generate the images
create_color_images(colors)