from PIL import Image, ImageDraw
import numpy as np
import colorsys

def get_contrast_color(r, g, b):
    """Retorna uma cor contrastante baseada na cor de entrada"""
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    if brightness < 128:
        # Para cores escuras, retorna uma versão mais clara
        return (min(r + 100, 255), min(g + 100, 255), min(b + 100, 255))
    else:
        # Para cores claras, retorna uma versão mais escura
        return (max(r - 50, 0), max(g - 50, 0), max(b - 50, 0))

def create_pencil_texture(color, output_path, size=(256, 256)):
    """
    Cria uma imagem com textura de lápis com marcas diagonais visíveis
    """
    # Converter cor hex para RGB
    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)
    
    # Criar imagem base
    img = Image.new('RGB', size, (r, g, b))
    draw = ImageDraw.Draw(img)
    
    # Obter cor para as marcas
    stroke_color = get_contrast_color(r, g, b)
    
    # Parâmetros do padrão
    spacing = 10  # Espaçamento entre linhas
    line_length = 20  # Comprimento das linhas
    
    # Criar padrão diagonal principal (45 graus)
    for i in range(-size[1], size[0] + size[1], spacing):
        start_x = i
        start_y = 0
        
        while start_y < size[1]:
            end_x = start_x + line_length
            end_y = start_y + line_length
            
            if 0 <= start_x < size[0]:
                draw.line(
                    [(start_x, start_y), (end_x, end_y)],
                    fill=stroke_color,
                    width=2
                )
            
            start_x += spacing
            start_y += spacing
    
    # Criar padrão diagonal secundário (135 graus)
    for i in range(-size[1], size[0] + size[1], spacing * 3):
        start_x = i
        start_y = 0
        
        while start_y < size[1]:
            end_x = start_x - line_length
            end_y = start_y + line_length
            
            if 0 <= start_x < size[0]:
                draw.line(
                    [(start_x, start_y), (end_x, end_y)],
                    fill=stroke_color,
                    width=2
                )
            
            start_x -= spacing
            start_y += spacing
    
    # Adicionar pontos aleatórios para textura
    for _ in range(1000):
        x = np.random.randint(0, size[0])
        y = np.random.randint(0, size[1])
        draw.point((x, y), fill=stroke_color)
    
    img.save(output_path)

def create_color_images(colors):
    """
    Cria imagens com textura de lápis para cada cor na lista
    """
    for color in colors:
        filename = f'assets/textures/pencil/{color.replace("#", "")}.png'
        create_pencil_texture(color, filename)
        print(f'"{filename}",')

# Lista de cores
colors = [
    '#FF00FF',  # Magenta
    '#00FFFF',  # Cyan
    '#FFFFFF',  # White
    '#000000',  # Black
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
    '#000080',  # Navy Blue
    '#0000FF',  # Blue
    '#1E90FF',  # Dodger Blue 
    '#87CEEB',  # Sky Blue
    '#8B0000',  # Dark Red
    '#FF0000',  # Red
    '#DC143C',  # Crimson
    '#FA8072',  # Salmon
    '#FFD700',  # Gold Yellow
    '#FFFF00',  # Yellow
    '#F0E68C',  # Khaki
    '#FFFACD',  # Lemon Chiffon
    '#C0C0C0',  # Silver
    '#A9A9A9',  # Dark Gray
    '#D3D3D3',  # Light Gray
    '#DCDCDC',  # Gainsboro
    '#FFD700',  # Gold
    '#DAA520',  # Goldenrod
    '#B8860B',  # Dark Goldenrod
    '#CD853F',  # Peru
    '#B22222',  # Fire Brick
    '#CD5C5C',  # Indian Red
    '#FF6347',  # Tomato
    '#FF4500',  # Orange Red
    '#FF8C00',  # Dark Orange
    '#FFA500',  # Orange
    '#FFB347',  # Light Orange
    '#FFFFE0',  # Light Yellow
    '#FFFACD',  # Lemon Chiffon
    '#006400',  # Dark Green
    '#008000',  # Green
    '#32CD32',  # Lime Green
    '#90EE90',  # Light Green
    '#00008B',  # Dark Blue
    '#0000FF',  # Blue
    '#1E90FF',  # Dodger Blue
    '#87CEEB',  # Sky Blue
    '#191970',  # Midnight Blue
    '#4169E1',  # Royal Blue
    '#6495ED',  # Cornflower Blue
    '#B0C4DE',  # Light Steel Blue
    '#4B0082',  # Indigo
    '#8A2BE2',  # Blue Violet
    '#9370DB',  # Medium Purple
    '#DDA0DD',  # Plum
]

# Gerar as imagens
create_color_images(colors)