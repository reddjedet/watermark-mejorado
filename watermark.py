import os
from PIL import Image, ImageDraw, ImageFont

def add_watermark_overlay(input_image_path, output_image_path, watermark_text, color_choice):
    """
    Agrega una marca de agua de texto y líneas a una imagen.
    El color se define por la elección del usuario. El texto está centrado, ligeramente rotado, y se muestra sin recortes.
    """
    try:
        input_image = Image.open(input_image_path).convert("RGBA")
        width, height = input_image.size
        
        # Determinar el color de la marca de agua basado en la elección
        if color_choice == '1':
            text_color = (22, 22, 29, 128) # MODIFICAR
            line_color = (22, 22, 29, 10) # MODIFICAR
        else:
            text_color = (233, 233, 226, 108) # MODIFICAR
            line_color = (233, 233, 226, 10) # MODIFICAR

        # 1. Crear una capa de superposición para las líneas
        lines_overlay = Image.new("RGBA", input_image.size, (255, 255, 255, 0))
        lines_draw = ImageDraw.Draw(lines_overlay)
        
        line_width = int(height * 0.008)
        line_spacing = int(height * 0.05)
        for i in range(0, width + height, line_spacing):
            lines_draw.line([(0, height - i), (i, height)], fill=line_color, width=line_width)

        # 2. Crear una capa de superposición para el texto
        text_overlay = Image.new("RGBA", input_image.size, (255, 255, 255, 0))
        
        try:
            # A: Escalar el tamaño de la fuente
            font_size = 1
            temp_draw = ImageDraw.Draw(Image.new("RGBA", (1, 1))) 
            
            while True:
                font = ImageFont.truetype("arial.ttf", font_size)
                text_width = temp_draw.textlength(watermark_text.split('\n')[0], font=font)
                if text_width > int(width * 0.5):
                    break
                font_size += 1
        except IOError:
            print("Fuente 'arial.ttf' no encontrada. Usando la fuente predeterminada.")
            font = ImageFont.load_default()
            # En este caso, el font size es fijo, pero el texto se ajusta
            text_width = font.getbbox(watermark_text)[2] - font.getbbox(watermark_text)[0]
        
        # B: Calcular el tamaño de la capa de texto con compensación para las letras que descienden
        # Usamos el atributo 'descent' para fuentes FreeType (truetype)
        # y calculamos un 'descent' fijo para la fuente por defecto.
        try:
            descent = font.getdescent()
        except AttributeError:
            # Si el método no existe (fuente por defecto), usa un valor aproximado
            descent = 10 
        
        text_bbox = font.getbbox(watermark_text)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        padding = int(max(text_width, text_height) * 0.2)
        
        text_layer = Image.new("RGBA", (text_width + padding, text_height + descent + padding), (0, 0, 0, 0))
        text_draw_temp = ImageDraw.Draw(text_layer)
        
        text_draw_temp.text((padding // 2, padding // 2 + descent), watermark_text, fill=text_color, font=font)
        
        # C: Rotar el texto
        rotated_text_layer = text_layer.rotate(5, expand=1)

        # D: Centrar la capa de texto rotada en la imagen principal
        center_x_overlay = (text_overlay.width - rotated_text_layer.width) // 2
        center_y_overlay = (text_overlay.height - rotated_text_layer.height) // 2
        
        text_overlay.paste(rotated_text_layer, (center_x_overlay, center_y_overlay), rotated_text_layer)

        # 3. Combinar las capas una por una para evitar la superposición de colores
        watermarked_image = Image.alpha_composite(input_image, lines_overlay)
        final_image = Image.alpha_composite(watermarked_image, text_overlay)

        final_image.save(output_image_path)
        print(f"Marca de agua agregada a '{input_image_path}'. Guardado como '{output_image_path}'")

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de imagen en la ruta '{input_image_path}'.")
    except Exception as e:
        print(f"Ocurrió un error inesperado al procesar '{input_image_path}': {e}")

# ---
### **Ejemplo de uso**


input_folder = "Assets"
output_folder = "Assets/watermarkeadas"
watermark_text = "TEXTO UNO\ntexto dos"

print("Elige el estilo de la marca de agua:")
print("1: Oscuro")
print("2: Claro")
color_choice = input("Ingresa tu opción (1 o 2): ")

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

if os.path.exists(input_folder):
    for file in os.listdir(input_folder):
        if file.endswith((".jpg", ".png", ".jpeg")):
            input_path = os.path.join(input_folder, file)
            output_filename = f"watermarked_{os.path.splitext(file)[0]}.png"
            output_path = os.path.join(output_folder, output_filename)
            
            add_watermark_overlay(input_path, output_path, watermark_text, color_choice)
else:
    print(f"Error: La carpeta '{input_folder}' no existe. Crea la carpeta y agrega tus imágenes.")
