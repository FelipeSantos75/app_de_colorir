# import re
# import pyperclip

# def svg_to_dart(svg_content):
#     shapes = []
#     # Expressões regulares para encontrar elementos <path> e <circle>
#     path_regex = re.compile(r'<path[^>]*d="([^"]+)"[^>]*>')
#     circle_regex = re.compile(r'<circle[^>]*cx="([^"]+)"[^>]*cy="([^"]+)"[^>]*r="([^"]+)"[^>]*>')

#     # Encontrar todos os elementos <path> e extrair o atributo 'd'
#     paths = path_regex.findall(svg_content)
#     for d in paths:
#         # Remover quebras de linha e espaços extras
#         d_clean = ' '.join(d.strip().split())
#         shape = f"""Shape(
#       path: parseSvgPathData(
#         '{d_clean}',
#       ),
#       color: Colors.white,
#     ),"""
#         shapes.append(shape)

#     # Encontrar todos os elementos <circle> e extrair 'cx', 'cy' e 'r'
#     circles = circle_regex.findall(svg_content)
#     for cx, cy, r in circles:
#         cx = float(cx)
#         cy = float(cy)
#         r = float(r)
#         # Converter o círculo em dados de caminho usando comandos de arco
#         path_data = f'M{cx - r},{cy} A{r},{r} 0 1,0 {cx + r},{cy} A{r},{r} 0 1,0 {cx - r},{cy}'
#         shape = f"""Shape(
#       path: parseSvgPathData(
#         '{path_data}',
#       ),
#       color: Colors.white,
#     ),"""
#         shapes.append(shape)

#     return '\n\n'.join(shapes)

# # Exemplo de uso:
# if __name__ == "__main__":
#     svg_content = '''
#     <svg width="500" height="500" xmlns="http://www.w3.org/2000/svg">
#   <g transform="translate(250,500)">
#     <path d="M 0 0 L 0 -100" stroke="green" stroke-width="2"/>
#     <g transform="translate(0,-100)">
#       <path d="M 0 0 L 0 -80" stroke="green" stroke-width="2"/>
#       <g transform="translate(0,-80) rotate(-30)">
#         <path d="M 0 0 L 0 -60" stroke="green" stroke-width="2"/>
#         <g transform="translate(0,-60) rotate(-30)">
#           <path d="M 0 0 L 0 -40" stroke="green" stroke-width="2"/>
#         </g>
#         <g transform="translate(0,-60) rotate(30)">
#           <path d="M 0 0 L 0 -40" stroke="green" stroke-width="2"/>
#         </g>
#       </g>
#       <g transform="translate(0,-80) rotate(30)">
#         <path d="M 0 0 L 0 -60" stroke="green" stroke-width="2"/>
#         <g transform="translate(0,-60) rotate(-30)">
#           <path d="M 0 0 L 0 -40" stroke="green" stroke-width="2"/>
#         </g>
#         <g transform="translate(0,-60) rotate(30)">
#           <path d="M 0 0 L 0 -40" stroke="green" stroke-width="2"/>
#         </g>
#       </g>
#     </g>
#   </g>
# </svg>
#     '''

#     dart_code = svg_to_dart(svg_content)
#     pyperclip.copy(dart_code)
#     print("O código Dart foi copiado para a área de transferência.")

import re
import pyperclip

def svg_to_dart(svg_content):
    shapes = []
    # Expressões regulares para encontrar elementos <path> e <circle>
    path_regex = re.compile(r'<path[^>]*d="([^"]+)"[^>]*>')
    circle_regex = re.compile(r'<circle[^>]*cx="([^"]+)"[^>]*cy="([^"]+)"[^>]*r="([^"]+)"[^>]*>')

    # Encontrar todos os elementos <path> e extrair o atributo 'd'
    paths = path_regex.findall(svg_content)
    for d in paths:
        # Remover quebras de linha e espaços extras
        d_clean = ' '.join(d.strip().split())
        shape = f"""Shape(
          path: parseSvgPathData(
            '{d_clean}',
          ),
          color: Colors.white,
        ),"""
        shapes.append(shape)

    # Encontrar todos os elementos <circle> e extrair 'cx', 'cy' e 'r'
    circles = circle_regex.findall(svg_content)
    for cx, cy, r in circles:
        cx = float(cx)
        cy = float(cy)
        r = float(r)

        # Converter o círculo em dados de caminho usando curvas de Bézier cúbicas
        # Fórmula para aproximar um círculo com 4 curvas de Bézier
        # Constante para calcular os pontos de controle
        c = r * 0.552284749831

        # Coordenadas dos pontos
        x0 = cx - r
        y0 = cy
        x1 = cx - r
        y1 = cy - c
        x2 = cx - c
        y2 = cy - r
        x3 = cx
        y3 = cy - r
        x4 = cx + c
        y4 = cy - r
        x5 = cx + r
        y5 = cy - c
        x6 = cx + r
        y6 = cy
        x7 = cx + r
        y7 = cy + c
        x8 = cx + c
        y8 = cy + r
        x9 = cx
        y9 = cy + r
        x10 = cx - c
        y10 = cy + r
        x11 = cx - r
        y11 = cy + c

        # Criar o path data usando curvas de Bézier cúbicas (comandos 'C')
        path_data = (
            f'M{x0},{y0} '
            f'C{x1},{y1} {x2},{y2} {x3},{y3} '
            f'C{x4},{y4} {x5},{y5} {x6},{y6} '
            f'C{x7},{y7} {x8},{y8} {x9},{y9} '
            f'C{x10},{y10} {x11},{y11} {x0},{y0} Z'
        )

        # Adicionar o shape à lista
        shape = f"""Shape(
          path: parseSvgPathData(
            '{path_data}',
          ),
          color: Colors.white,
        ),"""
        shapes.append(shape)

    return '\n\n'.join(shapes)

# Exemplo de uso:
if __name__ == "__main__":
    svg_content = '''
    <?xml version="1.0" encoding="utf-8"?>
<!-- Generator: Adobe Illustrator 27.5.0, SVG Export Plug-In . SVG Version: 6.00 Build 0)  -->
<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px"
	 viewBox="0 0 500 500" style="enable-background:new 0 0 500 500;" xml:space="preserve">
<g id="BACKGROUND">
	<rect style="fill:#FFFFFF;" width="500" height="500"/>
</g>
<g id="OBJECTS">
	<g>
		<g>
			<defs>
				<rect id="SVGID_1_" width="500" height="500"/>
			</defs>
			<clipPath id="SVGID_00000128465937127874439250000009739053961940322469_">
				<use xlink:href="#SVGID_1_"  style="overflow:visible;"/>
			</clipPath>
			<g style="clip-path:url(#SVGID_00000128465937127874439250000009739053961940322469_);">
				<g>
					
						<path id="1" style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
						M-15.01,294.65c4.41-25.52,16.06-50.82,37.14-67.32s52.59-22.35,76.62-9.96c15.71,8.1,26.45,22.51,36.62,36.43
						c13.86,18.97,27.72,37.95,41.58,56.92c12.47,17.07,26.64,35.32,47.8,40.81c21.19,5.5,43.16-3.33,63.93-10.09
						c20.77-6.76,45.79-10.95,63.09,1.85c7.28,5.38,13.09,13.67,22.23,14.96c10,1.41,18.83-6.5,23.7-14.86
						c10.81-18.56,10.66-41.35,20.89-60.2c10.02-18.47,30.17-31.69,51.99-34.12c21.82-2.43,44.67,6.01,60.6,20.7
						c-2.9,69.37-5.8,138.75-8.7,208.12C345.2,509.5,162.46,489.37-15.81,463.18C-14.84,409.82-25.55,355.65-15.01,294.65z"/>
					
						<path id="2" style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
						M101.2,306.16c1.03-11.33-0.6-23.2-6.2-32.92c-5.61-9.72-15.55-16.97-26.32-17.35c-7.99-0.28-15.89,3.19-21.89,8.78
						c-10.52,9.8-14.98,26.36-10.66,40.46s17.3,24.82,31.31,25.57S99.67,323.04,101.2,306.16z"/>
					
						<path id="13" style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
						M511.83,314.66c-3.36-5.24-6.79-10.55-11.54-14.71c-4.75-4.16-11.09-7.11-17.54-6.58c-11.42,0.93-18.93,11.92-21.79,22.42
						c-2.86,10.5-2.98,21.83-8.27,31.44c-3.15,5.72-8.2,11.42-6.86,17.75c1.53,7.21,10.49,10.5,18.23,11.12
						c15.6,1.25,32.13-3.71,42.49-14.82C516.92,350.17,522.57,331.38,511.83,314.66z"/>
				</g>
				<g>
					
						<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
						M-48.57,438.56c51.8-29.16,115.2-24.05,172.34-9.22c57.14,14.83,112.52,38.57,171.12,44.66
						c77.08,8.01,153.82-15.07,227.09-41.26c3.15,30.24,1.91,60.97-3.66,90.83c-182.51,1.56-365.03,3.12-547.54,4.69
						c-1.42-14.42-2.84-28.83-4.25-43.25"/>
					<g>
						<ellipse style="fill:none;stroke:#000000;stroke-miterlimit:10;" cx="21.79" cy="436.45" rx="4" ry="2"/>
						<ellipse style="fill:none;stroke:#000000;stroke-miterlimit:10;" cx="38.49" cy="443.45" rx="4" ry="2"/>
						<path style="fill:none;stroke:#000000;stroke-miterlimit:10;" d="M131.631,446.503c0.273-1.07,2.229-1.496,4.37-0.951			s3.655,1.855,3.383,2.925s-2.229,1.496-4.37,0.951S131.358,447.573,131.631,446.503z"/>
						<path style="fill:none;stroke:#000000;stroke-miterlimit:10;" d="M145.929,450.146c0.273-1.07,2.229-1.496,4.37-0.951
							c2.141,0.545,3.655,1.855,3.383,2.925c-0.273,1.07-2.229,1.496-4.37,0.951C147.171,452.526,145.656,451.216,145.929,450.146z"
							/>
						<path style="fill:none;stroke:#000000;stroke-miterlimit:10;" d="M72.896,477.768c0.056-1.103,1.889-1.907,4.096-1.795
							c2.206,0.112,3.95,1.096,3.894,2.199c-0.056,1.103-1.89,1.907-4.096,1.795C74.584,479.856,72.841,478.871,72.896,477.768z"/>
						<path style="fill:none;stroke:#000000;stroke-miterlimit:10;" d="M11.017,491.88c0.045-1.104,1.87-1.926,4.077-1.837
							c2.207,0.089,3.961,1.056,3.916,2.16c-0.045,1.104-1.87,1.926-4.077,1.837C12.726,493.951,10.973,492.984,11.017,491.88z"/>
						<path style="fill:none;stroke:#000000;stroke-miterlimit:10;" d="M181.914,487.255c0.117-1.098,1.993-1.799,4.19-1.564
							c2.197,0.234,3.883,1.315,3.765,2.413c-0.117,1.098-1.993,1.799-4.19,1.564C183.483,489.434,181.797,488.353,181.914,487.255z
							"/>
						<path style="fill:none;stroke:#000000;stroke-miterlimit:10;" d="M277.68,484.543c0.054-1.103,1.887-1.91,4.093-1.802
							c2.206,0.108,3.951,1.09,3.897,2.194c-0.054,1.103-1.887,1.91-4.093,1.802C279.37,486.629,277.626,485.647,277.68,484.543z"/>
						<path style="fill:none;stroke:#000000;stroke-miterlimit:10;" d="M413.496,475.99c2.199-0.216,4.069,0.5,4.177,1.599
							c0.108,1.099-1.586,2.166-3.785,2.382c-2.198,0.216-4.068-0.5-4.177-1.599C409.603,477.273,411.298,476.207,413.496,475.99z"
							/>
						<path style="fill:none;stroke:#000000;stroke-miterlimit:10;" d="M430.423,473.087c2.193-0.265,4.079,0.41,4.211,1.506
							c0.132,1.097-1.538,2.2-3.732,2.465c-2.193,0.265-4.079-0.41-4.211-1.506C426.559,474.455,428.23,473.351,430.423,473.087z"/>
						<path style="fill:none;stroke:#000000;stroke-miterlimit:10;" d="M490.425,454.589c2.193-0.265,4.078,0.41,4.211,1.506
							c0.132,1.097-1.538,2.2-3.732,2.465c-2.193,0.265-4.079-0.41-4.211-1.506C486.561,455.957,488.231,454.854,490.425,454.589z"
							/>
						<path style="fill:none;stroke:#000000;stroke-miterlimit:10;" d="M463.422,485.708c2.193-0.265,4.078,0.41,4.211,1.506
							c0.132,1.097-1.538,2.2-3.732,2.465c-2.193,0.265-4.079-0.41-4.211-1.506C459.559,487.077,461.229,485.973,463.422,485.708z"
							/>
					</g>
				</g>
			</g>
		</g>
	</g>
	<g>
		<g>
			
				<circle style="fill:#FFFFFF;stroke:#000000;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" cx="377.44" cy="288.82" r="16"/>
			<path style="fill:#FFFFFF;stroke:#000000;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="M385.9,285.43
				c0.96-0.67,1.91-1.34,2.87-2c-0.26-0.56-0.55-1.11-0.89-1.63c-2.23-3.36-6.12-5.56-10.16-5.72c-0.79,1.47-1.26,2.5-1.73,3.53
				C380.02,280.22,383.43,281.93,385.9,285.43z"/>
			<path style="fill:#FFFFFF;stroke:#000000;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="M387.4,288.03
				c0.72,1.53,1.33,3.29,1.79,5.35c0.83-2.21,0.99-4.65,0.54-6.97C388.95,286.94,388.18,287.48,387.4,288.03z"/>
		</g>
		<g>
			
				<circle style="fill:#FFFFFF;stroke:#000000;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" cx="166.2" cy="50.33" r="16.4"/>
			<path style="fill:#FFFFFF;stroke:#000000;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="M165.09,41.05
				c-0.41-1.12-0.82-2.25-1.22-3.38c-0.63,0.11-1.25,0.25-1.85,0.45c-3.92,1.31-7.13,4.59-8.36,8.53c1.25,1.17,2.14,1.91,3.04,2.65
				C158.37,45.49,160.97,42.57,165.09,41.05z"/>
			<path style="fill:#FFFFFF;stroke:#000000;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="M168.06,40.26
				c1.71-0.31,3.61-0.44,5.77-0.35c-1.97-1.41-4.34-2.21-6.76-2.39C167.39,38.43,167.73,39.35,168.06,40.26z"/>
		</g>
		<g>
			
				<circle style="fill:#FFFFFF;stroke:#000000;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" cx="354.72" cy="45.27" r="16.4"/>
			<path style="fill:#FFFFFF;stroke:#000000;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="M362.01,39.42
				c0.74-0.94,1.47-1.88,2.22-2.82c-0.42-0.47-0.87-0.93-1.36-1.34c-3.19-2.63-7.66-3.63-11.67-2.58c-0.33,1.68-0.49,2.83-0.65,3.98
				C354.69,36.07,358.54,36.73,362.01,39.42z"/>
			<path style="fill:#FFFFFF;stroke:#000000;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="M364.25,41.52
				c1.17,1.29,2.29,2.83,3.35,4.71c0.16-2.42-0.42-4.86-1.55-7C365.45,39.99,364.85,40.76,364.25,41.52z"/>
		</g>
		
			<circle style="fill:#FFFFFF;stroke:#000000;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" cx="419.29" cy="230.7" r="6.03"/>
		
			<circle style="fill:#FFFFFF;stroke:#000000;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" cx="458.64" cy="43.14" r="6.03"/>
		
			<circle style="fill:#FFFFFF;stroke:#000000;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" cx="243.58" cy="28.36" r="6.03"/>
		
			<circle style="fill:#FFFFFF;stroke:#000000;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" cx="119.28" cy="163.06" r="6.03"/>
		
			<circle style="fill:#FFFFFF;stroke:#000000;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" cx="46.89" cy="183.38" r="6.03"/>
	</g>
	<g>
		<g>
			<g>
				
					<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
					M110.83,83.62c3.63,9.03,12.17,15.26,19.6,21.89c7.43,6.63,14.45,15.14,13.55,24.89c-0.27,2.95-2.22,6.53-5.38,6.34
					c-2.92-0.18-4.18-3.33-5.21-5.86c-3.24-7.93-10.1-13.9-16.48-19.89c-6.38-5.99-12.7-12.69-14.37-21.08
					C105.71,87.77,108.88,85.63,110.83,83.62z"/>
				
					<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
					M69.44,101.88c1.23,8.3-0.51,16.78-1.4,25.18c-0.89,8.4-0.8,17.33,3.66,24.49c1.82,2.92,5.55,5.66,8.73,3.94
					c1.94-1.05,2.72-3.4,2.55-5.49c-0.17-2.08-1.07-4.02-1.7-6.01c-4.28-13.54,4.25-29.4-1.94-42.29
					C76.27,101.9,73.2,102.07,69.44,101.88z"/>
				
					<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
					M98.4,93.59c-0.54,6.69,3.9,12.59,7.8,18.25c3.9,5.66,7.47,12.23,5.11,18.75c-0.68,1.89-2.19,3.9-4.54,4.28
					c-3.33,0.55-5.52-2.37-6.76-4.85c-3.02-6.04-6.04-12.08-9.06-18.12c-2.67-5.34-5.39-11.16-3.05-16.87
					C91.77,94.6,95.64,94.17,98.4,93.59z"/>
				
					<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
					M49.43,98.42c0.11,5.89-2.45,11.53-5.24,16.78c-2.79,5.25-5.92,10.47-7.12,16.26c-1.2,5.79-0.06,12.44,4.53,16.21
					c2.25,1.85,6.26,2.54,7.76,0.03c1.14-1.91,0.01-4.25-0.63-6.35c-2.08-6.77,1.19-13.94,4.29-20.39
					c3.09-6.45,6.13-13.79,3.62-20.42C54.39,99.85,52.16,99.16,49.43,98.42z"/>
			</g>
			<g>
				
					<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
					M34.43,92.39c0,0-4.45,6.54-0.07,10.88c4.38,4.34,22.25,6.36,48.28,0.76s44.93-19.32,43.52-25.5c-1.41-6.18-8.94-4.6-8.94-4.6"
					/>
				
					<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
					M37.77,97.63C23.53,91.3,18.35,72.08,24.09,57.59s19.7-24.34,34.4-29.51c11.64-4.09,24.38-5.74,36.39-2.92
					s23.16,10.47,28.61,21.54c5.45,11.07,4.34,25.5-3.98,34.6"/>
			</g>
			<g>
				<g>
					<circle cx="53.31" cy="75.28" r="4.75"/>
					<circle cx="95.33" cy="65.15" r="4.75"/>
				</g>
				
					<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
					M83.7,68.51c-5.13,2.51-11.4,4.07-17.84,3.73C64.94,92.77,92.05,88.52,83.7,68.51z"/>
			</g>
			<g>
				<path style="fill:#FFFFFF;stroke:#000000;stroke-linecap:round;stroke-miterlimit:10;" d="M75.6,32.75
					c0.82-2.3,6.1-3.37,12.72-2.49c6.61,0.88,12.92,4.32,12.84,7.63c-0.09,3.47-6.47,1.01-13.21-0.38
					C81.41,36.17,74.33,36.31,75.6,32.75z"/>
				<path style="fill:#FFFFFF;stroke:#000000;stroke-linecap:round;stroke-miterlimit:10;" d="M106.17,44.27
					c-0.46-1.9,0.84-3.61,2.8-3.51c2.24,0.11,4,1.48,4.46,3.38c0.46,1.9-0.74,3.77-2.8,3.51C108.67,47.41,106.63,46.17,106.17,44.27
					z"/>
			</g>
		</g>
		<g>
			<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
				M450.06,136.12c-0.86,10.06,2.87,19.71,5.65,29.24s4.54,20.63,0.17,29.32c-1.32,2.63-4.09,5.09-6.27,3.49
				c-2.02-1.48-1.71-4.99-1.49-7.81c0.71-8.85-1.91-17.52-4.18-25.97c-2.27-8.46-4.23-17.56-2.21-26.13
				C444.81,137.68,447.9,137.11,450.06,136.12z"/>
			<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
				M409.88,135.9c-1.98,8.38-6.19,15.67-9.76,23.25c-3.56,7.57-6.59,16.06-5.81,24.73c0.32,3.53,2.1,7.7,5.02,7.43
				c1.79-0.17,3.17-2.07,3.77-4.11c0.6-2.04,0.61-4.26,0.84-6.41c1.56-14.63,13.31-26.03,13.24-40.85
				C414.88,138.8,412.57,137.67,409.88,135.9z"/>
			<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
				M436.35,142.03c-3.4,5.75-3.06,13.31-2.98,20.36c0.08,7.05-0.47,14.78-5.03,19.46c-1.32,1.35-3.25,2.41-5.02,1.57
				c-2.51-1.19-2.67-4.92-2.39-7.77c0.69-6.96,1.37-13.92,2.06-20.88c0.61-6.16,1.4-12.77,5.57-16.73
				C431.39,139.59,434.21,141.16,436.35,142.03z"/>
			<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
				M397.95,123.86c-2.34,6.21-6.45,10.87-10.58,15.02c-4.13,4.14-8.47,8.09-11.69,13.57s-5.13,12.98-3.43,19.13
				c0.83,3.02,3.39,5.67,5.48,3.77c1.59-1.45,1.75-4.44,2.15-6.95c1.3-8.08,6.55-14,11.38-19.25c4.83-5.25,9.99-11.47,10.92-19.61
				C400.88,127.74,399.58,125.95,397.95,123.86z"/>
			<g>
				
					<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
					M390.55,113.29c0,0-6.12,3.38-4.4,8.55c1.72,5.17,15.01,13.89,37.78,19.85c22.77,5.97,43.14,2.68,44.5-2.76
					c1.36-5.44-5.22-7.2-5.22-7.2"/>
				
					<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
					M391.1,118.75c-8.71-10.67-5.13-27.9,5.17-37.04c10.3-9.14,25.25-11.35,38.9-9.56c10.81,1.42,21.52,5.2,29.87,12.21
					s14.09,17.5,13.98,28.4c-0.11,10.9-6.75,21.84-16.94,25.71"/>
			</g>
			<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
				M438.94,114.1c-5.05-0.06-10.62-1.33-15.56-4.18C414.46,125.75,437.54,133.22,438.94,114.1z"/>
			<g>
				<path style="fill:#FFFFFF;stroke:#000000;stroke-linecap:round;stroke-miterlimit:10;" d="M446.81,82.66
					c1.56-1.49,6.16-0.22,11.02,3.11c4.86,3.33,8.47,8.56,7.08,11.14c-1.45,2.7-5.51-1.78-10.27-5.56
					C450.03,87.68,444.39,84.96,446.81,82.66z"/>
				<path style="fill:#FFFFFF;stroke:#000000;stroke-linecap:round;stroke-miterlimit:10;" d="M466.33,103.94
					c0.4-1.68,2.1-2.51,3.61-1.65c1.73,0.98,2.57,2.76,2.17,4.45c-0.4,1.68-2.09,2.67-3.61,1.65
					C467.05,107.41,465.93,105.63,466.33,103.94z"/>
			</g>
			<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
				M415.77,110.68c1.41-2.39,1.1-5.66-0.73-7.75c-1.83-2.08-5.03-2.82-7.58-1.75c-2.55,1.08-4.26,3.89-4.04,6.65"/>
			<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
				M456.89,123.05c1.74-2.16,1.91-5.44,0.41-7.77s-4.57-3.52-7.25-2.83c-2.68,0.69-4.78,3.23-4.96,5.99"/>
		</g>
		<g>
			<g>
				
					<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
					M70.96,404.17c-6.86,3.04-11.55,10.41-11.42,17.91c0.01,0.67,0.06,1.35,0.36,1.95c0.3,0.6,0.89,1.08,1.56,1.07
					c1.25-0.03,1.79-1.55,2.14-2.74c1.7-5.79,6.82-10.42,12.75-11.54C74.67,408.61,72.98,406.41,70.96,404.17z"/>
				
					<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
					M77.62,405.79c-6.19,4.24-9.47,12.33-7.97,19.68c0.13,0.65,0.31,1.32,0.71,1.85s1.08,0.9,1.73,0.77
					c1.22-0.25,1.48-1.85,1.6-3.09c0.62-6,4.81-11.49,10.44-13.67C82.07,409.48,80.02,407.62,77.62,405.79z"/>
			</g>
			<g>
				
					<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
					M122.65,394.52c7.46,0.76,14.22,6.29,16.43,13.46c0.2,0.64,0.36,1.3,0.26,1.96c-0.1,0.66-0.51,1.31-1.15,1.5
					c-1.19,0.36-2.18-0.91-2.89-1.94c-3.42-4.97-9.73-7.78-15.71-7C120.51,399.89,121.42,397.27,122.65,394.52z"/>
				
					<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
					M125.18,386.28c7.44-0.95,15.27,2.92,19.04,9.4c0.33,0.58,0.65,1.19,0.7,1.85s-0.2,1.39-0.78,1.72
					c-1.08,0.62-2.33-0.4-3.25-1.24c-4.45-4.07-11.23-5.39-16.88-3.27C124.31,391.99,124.61,389.24,125.18,386.28z"/>
			</g>
			<g>
				
					<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
					M127.1,374.69c5.04-3.58,8.72-12.16,6.92-17.58c2.75-0.99,3.41-1.6,6.32-2.2c0.39,4.51,0.19,8.82-1.33,13.08
					c-1.5,4.23-3.9,8.33-7.91,11.91C129.41,377.96,128.65,377.41,127.1,374.69z"/>
				
					<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
					M148.05,338.05c-0.99-4.72-3.37-9.28-7.48-11.82c-2-1.24-4.37-2.03-6.7-1.73s-4.59,1.85-5.27,4.1c-0.68,2.25,0.6,5.04,2.89,5.61
					c1.06,0.26,2.54,0.35,2.68,1.43c0.16,1.14-1.46,1.63-2.01,2.64c-0.56,1.03,0.12,2.29,0.93,3.14c0.81,0.84,1.82,1.63,2.05,2.78
					c0.24,1.17-0.57,2.46-1.73,2.75c-1.16,0.29-2.49-0.46-2.82-1.61c-0.17-0.58-0.1-1.2-0.16-1.81c-0.24-2.36-2.75-4.23-5.08-3.77
					c1.61-1.32,0.96-4.25-0.9-5.17c-1.87-0.91-4.26-0.03-5.53,1.61c-1.27,1.64-1.6,3.85-1.45,5.92c0.43,5.9,6.15,14.97,13.72,17.91
					C137.96,362.66,152.19,357.78,148.05,338.05z"/>
			</g>
			<g>
				
					<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
					M67.49,397.85c-6.07,1.19-14.82-2.05-17.51-7.1c-2.61,1.31-3.51,1.37-5.95,3.07c3,3.39,6.26,6.21,10.4,8.05
					c4.11,1.82,8.72,2.91,14.08,2.47C68.26,401.78,68.39,400.85,67.49,397.85z"/>
				
					<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
					M26.5,387.81c-2.74-3.97-4.41-8.84-3.41-13.56c0.48-2.3,1.54-4.56,3.36-6.05c1.82-1.49,4.5-2.06,6.6-1
					c2.1,1.06,3.24,3.91,2.08,5.96c-0.54,0.95-1.49,2.08-0.81,2.93c0.72,0.9,2.18,0.07,3.29,0.36c1.13,0.3,1.58,1.67,1.63,2.83
					c0.05,1.17-0.07,2.44,0.6,3.4c0.69,0.98,2.18,1.28,3.19,0.64c1.01-0.64,1.38-2.12,0.77-3.15c-0.31-0.52-0.8-0.9-1.2-1.36
					c-1.55-1.8-1.17-4.91,0.76-6.28c-2.06,0.26-3.75-2.23-3.12-4.21c0.62-1.98,2.91-3.11,4.97-2.9c2.07,0.21,3.89,1.49,5.29,3.03
					c3.98,4.37,6.62,14.76,3.53,22.28C51.28,397.43,37.95,404.4,26.5,387.81z"/>
			</g>
			<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
				M61.21,397.62c-2.91-17.76,11.45-32.49,29.91-36.71s39.05,5.99,42.58,21.42c3.28,14.32-8.58,23.83-31.15,28.56
				C77.34,416.17,63.64,412.44,61.21,397.62z"/>
			<g>
				<circle cx="79.19" cy="383.26" r="3.76"/>
				<circle cx="110.44" cy="376.11" r="3.76"/>
				
					<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
					M101.98,377.68c-4,1.7-8.46,2.33-13.31,2.54c-1.15,2.95,0.41,6.58,3.27,8.02s6.63,0.66,8.86-1.63
					C103.02,384.32,103.66,380.74,101.98,377.68z"/>
			</g>
		</g>
		<g>
			<g>
				
					<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
					M409.02,436.11c7.12,1.08,13.34,6.72,15.11,13.7c0.16,0.62,0.28,1.27,0.16,1.89c-0.12,0.63-0.55,1.23-1.17,1.39
					c-1.16,0.29-2.05-0.98-2.68-2c-3.04-4.93-8.96-7.93-14.73-7.47C406.71,441.16,407.72,438.7,409.02,436.11z"/>
				
					<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
					M403.26,439.3c6.81,2.36,11.89,9.03,12.37,16.22c0.04,0.64,0.05,1.3-0.19,1.89s-0.77,1.11-1.41,1.15
					c-1.2,0.08-1.83-1.34-2.27-2.45c-2.09-5.4-7.37-9.43-13.13-10.02C400.07,443.85,401.51,441.6,403.26,439.3z"/>
			</g>
			<g>
				
					<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
					M355.12,436.83c-6.69,2.66-11.48,9.55-11.64,16.75c-0.01,0.64,0.01,1.3,0.27,1.88c0.26,0.58,0.82,1.07,1.46,1.09
					c1.2,0.02,1.77-1.42,2.16-2.55c1.85-5.49,6.94-9.75,12.67-10.59C358.5,441.23,356.97,439.06,355.12,436.83z"/>
				
					<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
					M350.61,429.89c-7.12,1.08-13.34,6.71-15.12,13.69c-0.16,0.62-0.28,1.27-0.16,1.89c0.12,0.63,0.55,1.23,1.17,1.39
					c1.16,0.29,2.05-0.98,2.68-2c3.04-4.93,8.96-7.93,14.73-7.46C352.91,434.94,351.91,432.48,350.61,429.89z"/>
			</g>
			<g>
				
					<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
					M351.68,418.06c-5.82-1.2-12.37-7.32-12.88-12.78c-2.8,0.19-3.61-0.09-6.41,0.51c1.4,4.11,3.24,7.82,6.23,10.99
					c2.96,3.14,6.64,5.81,11.56,7.41C350.91,421.83,351.37,421.05,351.68,418.06z"/>
				
					<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
					M319.1,393.95c-0.95-4.54-0.62-9.47,2.01-13.28c1.28-1.86,3.06-3.47,5.22-4.12c2.17-0.64,4.75-0.15,6.22,1.56
					c1.47,1.72,1.42,4.67-0.37,6.05c-0.83,0.64-2.1,1.29-1.81,2.29c0.3,1.06,1.91,0.87,2.78,1.54c0.89,0.68,0.78,2.06,0.4,3.12
					c-0.39,1.06-0.97,2.14-0.73,3.24c0.24,1.12,1.45,1.94,2.58,1.75s2.01-1.37,1.85-2.51c-0.08-0.58-0.38-1.1-0.55-1.65
					c-0.7-2.17,0.79-4.78,3.01-5.28c-1.92-0.54-2.49-3.37-1.2-4.89c1.29-1.52,3.73-1.67,5.48-0.72c1.75,0.95,2.89,2.76,3.56,4.64
					c1.91,5.35,0.38,15.53-5.14,21.04C337.48,411.67,323.09,412.89,319.1,393.95z"/>
			</g>
			<g>
				
					<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
					M410.15,423.45c5.89,0.73,14.06-2.96,16.3-7.97c2.59,1.08,3.45,1.07,5.91,2.54c-2.65,3.45-5.58,6.37-9.42,8.41
					c-3.81,2.02-8.16,3.37-13.33,3.31C409.68,427.26,409.5,426.38,410.15,423.45z"/>
				
					<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
					M448.75,411.07c2.36-3.99,3.63-8.76,2.36-13.22c-0.62-2.17-1.78-4.27-3.63-5.57c-1.85-1.3-4.45-1.67-6.39-0.51
					c-1.94,1.15-2.84,3.96-1.59,5.85c0.58,0.87,1.57,1.89,0.98,2.75c-0.63,0.91-2.09,0.21-3.13,0.57c-1.06,0.36-1.4,1.7-1.38,2.83
					c0.03,1.12,0.23,2.34-0.35,3.3c-0.59,0.98-2,1.38-3.01,0.83c-1.01-0.54-1.46-1.94-0.95-2.97c0.26-0.52,0.71-0.92,1.06-1.39
					c1.36-1.83,0.79-4.78-1.15-5.97c1.99,0.11,3.44-2.39,2.71-4.24c-0.73-1.85-2.99-2.78-4.96-2.44c-1.97,0.34-3.63,1.69-4.86,3.25
					c-3.52,4.46-5.35,14.59-1.89,21.58C425.65,421.96,438.9,427.73,448.75,411.07z"/>
			</g>
			<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
				M416.42,432.71c1.6-17.21-13.15-30.35-31.12-33.16s-37.01,8.36-39.35,23.39c-2.18,13.94,9.82,22.25,31.76,25.26
				C402.21,451.56,415.09,447.06,416.42,432.71z"/>
			<g>
				
					<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
					M375.7,418.38c4.31,1.84,9.19,2.22,14.51,2c1.13,3.78-0.74,8.72-3.94,10.9c-3.2,2.18-7.32,1.54-9.66-1.25
					C374.26,427.24,373.72,422.59,375.7,418.38z"/>
				
					<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
					M358.25,415.05c0.3-2.09,1.83-3.96,3.83-4.66c1.99-0.7,4.36-0.21,5.91,1.24c1.55,1.44,2.2,3.77,1.64,5.81"/>
				
					<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
					M395.94,421.71c0.24-2.1,1.72-4.01,3.7-4.77c1.97-0.76,4.35-0.33,5.94,1.07c1.59,1.4,2.31,3.71,1.8,5.76"/>
			</g>
		</g>
	</g>
	<g>
		<g>
			<g>
				
					<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
					M373.69,215.29c0.03-11.3-5.92-22.45-15.34-28.71c-6.89-4.58-16.06-7.35-19.12-15.04c-2.59-6.51,0.42-13.72,2.72-20.33
					c6.93-19.94,7.21-42.64-1.86-61.7c-9.07-19.06-35.54-32.41-56.24-36.53c-14.18-2.82-25.26-1.85-33.75,1.58
					c-38.76-11.19-87.45,26.56-76.5,70.33c5.92,23.67,1.83,40.82-20.01,58.62c-13.76,11.22-33.7,27.06-25.27,46.13
					c3.76,8.52,14.08,14.53,14.22,23.74c0.09,5.99-4.31,11.04-6.62,16.6c-10.26,24.62,15.89,56.92,54.77,63.69
					c41.31,7.2,87.59,2.49,125.12-18.64c10.15-5.71,21.04-14.08,20.85-25.72c-0.14-8.51-6.29-16.56-4.45-24.87
					c1.23-5.57,5.85-9.79,10.79-12.65s10.41-4.75,15.19-7.88C367.63,237.71,373.65,226.6,373.69,215.29z"/>
			</g>
			<g>
				<path style="fill:none;stroke:#000000;stroke-linecap:round;stroke-miterlimit:10;" d="M298.44,185.03
					c-0.66,6.96-3.15,14.94-2.83,22.7c0.32,7.76,3.43,15.81,9.85,20.2c5.43,3.71,12.96,4.73,16.65,10.19
					c3.02,4.47,2.35,10.43,1.07,15.67c-1.28,5.24-3.06,10.65-1.88,15.92c1.15,5.11,4.91,9.19,7.03,13.98
					c4.2,9.44,1.04,21.59-7.21,27.8"/>
				<path style="fill:none;stroke:#000000;stroke-linecap:round;stroke-miterlimit:10;" d="M244.32,60.29
					c-1.41,13,4.58,26.54,15.14,34.24c9.05,6.6,20.56,8.83,30.25,14.46c16.53,9.61,26.33,29.66,23.75,48.6
					c-0.95,6.99-3.42,13.72-4.06,20.75c-0.64,7.02,0.97,14.86,6.54,19.18c7.9,6.13,19.94,2.72,28.68,7.59
					c8.81,4.9,11.36,17.01,8.42,26.66c-2.93,9.65-9.99,17.39-16.85,24.78"/>
				<path style="fill:none;stroke:#000000;stroke-linecap:round;stroke-miterlimit:10;" d="M253.5,54.2
					c0.62,9.03,8.95,15.8,17.56,18.58c8.62,2.78,17.88,2.74,26.72,4.72c15.33,3.43,29.14,13.21,37.46,26.53
					c8.33,13.32,11.07,30.02,7.44,45.3"/>
				<path style="fill:none;stroke:#000000;stroke-linecap:round;stroke-miterlimit:10;" d="M243.49,60.67
					c-17.01-3.82-35.3,4.63-46.04,18.37c-10.74,13.73-14.69,31.85-14.08,49.27c0.55,15.65,4.26,32.45-3.28,46.17
					c-4.84,8.8-13.54,14.68-21.96,20.16s-17.18,11.23-22.24,19.9c-5.07,8.67-5.08,21.2,2.74,27.51"/>
				<path style="fill:none;stroke:#000000;stroke-linecap:round;stroke-miterlimit:10;" d="M202.39,190.36
					c-2.34,10.71-12.91,17.15-22.21,22.96c-9.3,5.81-19.22,14.08-18.83,25.04c0.27,7.79,5.91,14.72,5.78,22.51
					c-0.12,7.11-4.94,13.14-7.63,19.73c-5.55,13.59-1,30.61,10.59,39.62"/>
				<path style="fill:none;stroke:#000000;stroke-linecap:round;stroke-miterlimit:10;" d="M268.91,209.13
					c-2.19,11.99,4.89,23.64,12.67,33.03s16.86,18.48,19.87,30.29c3.15,12.35-1.12,25.68-8.54,36.04
					c-7.42,10.37-16.96,19.8-27.4,24.7"/>
				<path style="fill:none;stroke:#000000;stroke-linecap:round;stroke-miterlimit:10;" d="M255.37,205.2
					c-3.29,10.54-1.1,22.01,2.39,32.49c3.49,10.48,8.26,20.6,10.23,31.47c4.78,26.34-9.32,55.01-33.1,67.3"/>
			</g>
			<path style="fill:none;stroke:#000000;stroke-linecap:round;stroke-miterlimit:10;" d="M237.36,71.32
				c2.22-7.42,7.61-13.84,14.54-17.31"/>
		</g>
		<g>
			<g>
				
					<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
					M267.06,408.36c4.18,2.15,9.87,0.67,12.47-3.25c2.6-3.92,1.77-9.73-1.83-12.76c5.58-0.47,11.6-1.64,15.28-5.86
					c3.68-4.21,3-12.29-2.35-13.95c4.47,0.3,9.16,0.56,13.23-1.33c4.07-1.88,7.17-6.67,5.59-10.86c-1-2.66-3.56-4.41-6.13-5.63
					c-13.57-6.46-29.86-2.76-43.45,3.64c-13.6,6.41-26.03,15.4-43.5,24.08c5.12,13.27,6.8,27.59,10.44,41.34
					c3.65,13.75,9.82,27.64,21.36,35.96c3.21,2.32,7.67,4.13,10.98,1.96c2.26-1.48,3.17-4.44,2.94-7.13s-1.41-5.19-2.57-7.63
					c4.69-0.41,8.96-3.9,10.29-8.42c1.33-4.51-0.35-9.76-4.06-12.66C271.32,422.54,270.97,412.84,267.06,408.36z"/>
				<g>
					<path style="fill:none;stroke:#000000;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="M292.12,372.95
						c-19.03-4.18-39.63-0.69-56.23,9.51"/>
					<path style="fill:none;stroke:#000000;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="M278.99,392.73
						c-10.27-1.77-20.93-1.31-31.01,1.36"/>
					<path style="fill:none;stroke:#000000;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="M267.81,408.56
						c-7.4-2.69-14.51-6.19-21.16-10.41"/>
					<path style="fill:none;stroke:#000000;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="M266.73,426.66
						c-13.06-4.57-23.98-14.92-29.24-27.72"/>
					<path style="fill:none;stroke:#000000;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="M259.56,447.56
						c-16.34-11.61-27.57-30.16-30.29-50.02"/>
				</g>
			</g>
			<g>
				
					<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
					M167.95,305.17c2.31-24.25,12.89-38.51,26.77-49.02c10.11,7.6,14.17,5.72,28.47,8.03c9.67,7.95,14.58,26.82,13.87,39.13
					c-0.72,12.3-6.95,24.88-9.67,36.92c-10.18,44.89,22.32,46.56,20.74,55.28c-0.58,3.19-4.82,4.37-9.34,3.72
					C180.17,390.73,165.12,334.92,167.95,305.17z"/>
				<g>
					<path style="fill:none;stroke:#000000;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="M169.03,298.3
						c-1.46,3.23,0.47,7.52,3.86,8.57c3.38,1.05,7.41-1.41,8.02-4.9c-1.76,3.8,1.33,8.78,5.49,9.29c4.16,0.52,8.22-3.07,8.65-7.24
						c-1.43,3.92,1.51,8.79,5.65,9.33s8.25-3.39,7.88-7.55"/>
					<path style="fill:none;stroke:#000000;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="M187.41,328.69
						c-0.5,2.65-0.37,5.55,1.05,7.84c1.42,2.3,4.37,3.76,6.92,2.87c2.8-0.98,4.07-4.14,5.01-6.96c-0.44,2.47,0.6,5.14,2.6,6.65
						c1.99,1.51,4.85,1.8,7.11,0.71c3.55-1.71,4.93-6.05,5.32-9.98"/>
					<path style="fill:none;stroke:#000000;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="M203.95,359.45
						c-0.06,1.84-0.12,3.72,0.35,5.5s1.56,3.49,3.23,4.27c2.43,1.13,5.49-0.08,7.05-2.25s1.86-5.04,1.5-7.69
						c0.23,2.62,0.91,5.37,2.79,7.2c1.89,1.83,5.28,2.28,7.07,0.35"/>
					<path style="fill:none;stroke:#000000;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="M191.87,357.46
						c0.14,2.26,0.28,4.58-0.42,6.73s-2.44,4.12-4.69,4.41"/>
					<path style="fill:none;stroke:#000000;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="M214.37,386.97
						c1.66,1.15,3.36,2.33,5.3,2.92c1.94,0.6,4.18,0.54,5.83-0.65c1.76-1.27,2.51-3.66,2.16-5.8c-0.35-2.14-1.66-4.04-3.28-5.48"/>
					<path style="fill:none;stroke:#000000;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="M224.08,307.53
						c-1.95,2.8-1.5,7,0.98,9.33c2.49,2.33,6.71,2.5,9.37,0.37"/>
				</g>
			</g>
			<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
				M197.27,277.62c1.6,5.96,3.36,12.22,7.71,16.6c4.35,4.39,12.17,5.98,16.62,1.7c2.71,2.58,5.85,4.83,9.46,5.84
				c3.6,1,7.73,0.6,10.69-1.7c2.95-2.3,4.34-6.68,2.64-10.01c2.18,1.73,5.67-0.47,6.15-3.22c0.48-2.75-1.01-5.42-2.55-7.74
				c-3.34-5.03-8.03-10.1-14.06-10.21c-1.88-0.03-3.73,0.44-5.55,0.9C218.44,272.32,208.5,274.86,197.27,277.62z"/>
			<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
				M195.93,278.69c-4.41,5.66-10.48,9.79-17.08,11.64c-2.39,0.67-4.99,1.03-7.25,0.02c-2.26-1.02-3.96-3.81-3.16-6.33
				c-1.73,2.4-5.4,2.39-7.47,0.4c-2.07-1.99-2.64-5.38-1.97-8.32s2.39-5.49,4.3-7.72c6.69-7.78,16.35-12.49,26.12-12.73
				C190.74,264.37,193.13,272.89,195.93,278.69z"/>
			<g>
				
					<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
					M309.78,238.7c5.31,0.38,11.77-6.56-0.41-6.7c10-6.38,1.71-9.67-5.83-4.86c2.31-9.19-5.48-6.59-6.79,2.69
					c-20.4,2.8-36.85,2.7-55.75-0.6c-1.76-0.46-3.44-0.91-5.06-1.36c-0.28-4.76,0.55-9.59,1.73-13.88
					c-4.99-1.07-11.96-4.64-16.68-6.99c-1.21,6.85-2.09,11.22-5.06,12.99c-0.57-0.33-1.13-0.68-1.69-1.03
					c-18.77-12.94-31.59-25.67-45.19-44.64c5.84-7.33,2.37-14.77-2.71-6.78c-1.69-8.78-9.78-12.54-7.54-0.89
					c-8.48-8.75-9.08,0.71-5.14,4.3c-9.82-6.38-9.62,2.42-3.21,6c-7.46-0.26-7.82,6.02,5.22,8.87c0,0,18.87,39.05,37.97,54.92
					c-3.81,6.05-7.06,12.7-9.7,19.98c5.87,28.31,19.95,21.93,51.64,13.72c0.21-5.43,0.55-10.94,1.03-16.39
					c24.86,0.92,60.99-10.58,60.99-10.58c11.04,7.51,15.35,2.93,10.03-2.31C314.64,247.36,321.16,241.44,309.78,238.7z"/>
			</g>
			<g>
				<g>
					
						<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
						M196.56,165.86c-0.83-3.5-3.04-6.76-6.22-8.5c-3.18-1.74-7.33-1.78-10.31,0.24c-2.96,2-4.42,5.78-4.08,9.33
						c0.34,3.55,2.32,6.84,4.98,9.25c2.66,2.41,5.99,4.01,9.41,5.13"/>
					
						<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
						M180.62,165.51c4.82-0.82,10.02,2.04,11.91,6.55"/>
				</g>
				<g>
					
						<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
						M285.86,191.66c2.7-2.38,6.38-3.77,9.98-3.36s7.01,2.77,8.28,6.14c1.26,3.34,0.29,7.27-2.04,9.98
						c-2.33,2.71-5.84,4.26-9.41,4.69c-3.57,0.43-7.2-0.18-10.64-1.23"/>
					
						<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
						M299.08,200.57c-3.47-3.45-9.37-4.11-13.51-1.51"/>
				</g>
				
					<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
					M298.18,185.99c-3,3.79-6.3,7.65-9.95,11.57c-1.65,43.34-121.48,12.89-96.95-30.75c-11.86-59.85,14.22-89.54,46.15-96.68
					c-2.41,6.21-2.33,13.73,0.18,20c4.33,10.85,13.91,18.65,23.56,25.24c9.64,6.59,19.96,12.7,27.15,21.91
					C298.84,150.77,300.88,168.82,298.18,185.99z"/>
				<g>
					
						<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
						M244.99,189.66c-6.04,0.3-10.95-0.97-16.49-4.11c-3.22,3.8-3.71,9.91-1.12,13.91c2.59,3.99,7.98,5.45,12.27,3.3
						C243.93,200.61,246.67,195.1,244.99,189.66z"/>
					
						<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
						M226.76,132.7c-2.74-3.24-7.06-5.3-11.32-5.39c-4.26-0.09-8.36,1.79-10.75,4.93"/>
					
						<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
						M271.51,142.49c3.97-1.35,8.53-0.82,12.08,1.41c3.55,2.23,6.01,6.1,6.53,10.26"/>
					<g>
						
							<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
							M221.66,181.17c0.78-4.01-1.27-8.41-4.84-10.39c-3.57-1.98-8.39-1.39-11.37,1.39"/>
						<path style="fill:none;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
							M206.65,171.18c-1.87-0.28-3.51-1.73-4.02-3.56"/>
					</g>
					<g>
						
							<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
							M274.26,192.62c-0.71-4.02-4.2-7.39-8.24-7.96c-4.04-0.57-8.33,1.7-10.12,5.37"/>
						<path style="fill:none;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
							M273.76,190.65c2.08,0.32,4.28-0.34,5.85-1.74"/>
					</g>
				</g>
			</g>
			<path style="fill:#FFFFFF;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;" d="
				M211.65,253.43c-41.38,7.36-16.15-50.85,3.35-11.82C259.86,223.65,246.33,290.06,211.65,253.43z"/>
		</g>
	</g>
</g>
</svg>

    '''

    dart_code = svg_to_dart(svg_content)
    pyperclip.copy(dart_code)
    print("O código Dart foi copiado para a área de transferência.")
