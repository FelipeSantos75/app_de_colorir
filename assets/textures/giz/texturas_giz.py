from PIL import Image, ImageDraw
import numpy as np
import os

def create_crayon_texture(color, output_path, size=(256, 256), noise_intensity=0.7):
    """
    Cria uma imagem com textura similar a giz de cera e salva no caminho especificado
    """
    # Converter cor hex para RGB
    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)
    
    # Criar imagem base
    img = Image.new('RGB', size, (r, g, b))
    img_array = np.array(img)
    
    # Criar múltiplas camadas de ruído para textura mais pronunciada
    for _ in range(3):  # Aumentamos para 3 camadas de ruído
        noise = np.random.normal(0, 1, size)
        
        # Aplicar o ruído em cada canal RGB
        for i in range(3):
            channel = img_array[:,:,i].astype(float)
            variation = noise * noise_intensity * 50  # Aumentamos para 50
            channel += variation
            channel = np.clip(channel, 0, 255)
            img_array[:,:,i] = channel.astype(np.uint8)
    
    textured_img = Image.fromarray(img_array)
    draw = ImageDraw.Draw(textured_img)
    
    # Adicionar mais linhas e mais grossas para simular estrias do giz
    for _ in range(150):  # Aumentamos para 150 linhas
        x1 = np.random.randint(0, size[0])
        y1 = np.random.randint(0, size[1])
        x2 = x1 + np.random.randint(-30, 30)  # Linhas mais longas
        y2 = y1 + np.random.randint(-30, 30)
        
        # Variação maior na cor das linhas
        stroke_color = (
            int(np.clip(r + np.random.randint(-25, 25), 0, 255)),
            int(np.clip(g + np.random.randint(-25, 25), 0, 255)),
            int(np.clip(b + np.random.randint(-25, 25), 0, 255))
        )
        
        # Linhas mais grossas e com opacidade variável
        width = np.random.randint(1, 3)
        draw.line([(x1, y1), (x2, y2)], fill=stroke_color, width=width)
    
    # Adicionar um pouco de granulação extra
    for _ in range(1000):  # Pontos aleatórios para granulação
        x = np.random.randint(0, size[0])
        y = np.random.randint(0, size[1])
        
        # Pontos com variação de cor mais extrema
        point_color = (
            int(np.clip(r + np.random.randint(-40, 40), 0, 255)),
            int(np.clip(g + np.random.randint(-40, 40), 0, 255)),
            int(np.clip(b + np.random.randint(-40, 40), 0, 255))
        )
        
        draw.point((x, y), fill=point_color)
    
    textured_img.save(output_path)

def create_color_images(colors):
    """
    Cria imagens com textura de giz para cada cor na lista
    """
    for color in colors:
        filename = f'assets/textures/giz/{color.replace("#", "")}.png'
        create_crayon_texture(color, filename)
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
    '#CD853F',  # Peru

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
    '#DDA0DD',  # Plum
]

# Gerar as imagens
create_color_images(colors)