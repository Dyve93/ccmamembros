from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import os
from datetime import datetime

class CardGenerator:
    def __init__(self):
        self.background_path = 'static/background.png'
        self.font_path = 'static/font.ttf'
        
    def generate_card(self, member_data):
        # Abrir imagem de fundo
        img = Image.open(self.background_path)
        
        # Melhorar contraste e brilho
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(0.95)
        
        draw = ImageDraw.Draw(img)
        
        try:
            # Fontes maiores e mais estilizadas
            font_title = ImageFont.truetype(self.font_path, 60)
            font_large = ImageFont.truetype(self.font_path, 48)
            font_medium = ImageFont.truetype(self.font_path, 36)
            font_small = ImageFont.truetype(self.font_path, 30)
        except:
            # Fallback para fontes padrão (aumentei o tamanho)
            font_title = ImageFont.load_default(60)
            font_large = ImageFont.load_default(48)
            font_medium = ImageFont.load_default(36)
            font_small = ImageFont.load_default(30)
        
        # Posições ajustadas para fontes maiores
        positions = {
            'title': (150, 100),
            'name': (150, 180),
            'function': (150, 250),
            'address': (150, 320),
            'birth_date': (150, 390),
            'status': (150, 460),
            'issue_date': (150, 530)
        }
        
        # Adicionar um título
        draw.text(positions['title'], "CREDENCIAL DE MEMBRO", fill=(0, 0, 139), font=font_title)
        
        # Adicionar uma linha decorativa
        draw.line([(150, 170), (img.width - 150, 170)], fill=(0, 0, 139), width=3)
        
        # Textos com cores e sombras
        shadow_offset = 2
        
        # Nome com destaque
        draw.text((positions['name'][0]+shadow_offset, positions['name'][1]+shadow_offset), 
                 f"Nome: {member_data['name']}", fill=(100, 100, 100), font=font_large)
        draw.text(positions['name'], f"Nome: {member_data['name']}", 
                 fill=(0, 0, 139), font=font_large)
        
        # Demais campos
        fields = [
            ('function', f"Função: {member_data['function']}"),
            ('address', f"Endereço: {member_data['address']}"),
            ('birth_date', f"Data Nasc.: {member_data['birth_date']}"),
            ('status', f"Status: {member_data['status']}")
        ]
        
        for field, text in fields:
            draw.text((positions[field][0]+shadow_offset, positions[field][1]+shadow_offset), 
                     text, fill=(100, 100, 100), font=font_medium)
            draw.text(positions[field], text, fill=(0, 0, 0), font=font_medium)
        
        # Data de emissão
        issue_date = datetime.now().strftime("%d/%m/%Y")
        draw.text(positions['issue_date'], f"Emitido em: {issue_date}", 
                fill=(70, 70, 70), font=font_small)
        
        # Adicionar borda decorativa
        border_color = (0, 0, 139)
        border_width = 15
        draw.rectangle([border_width, border_width, img.width-border_width, img.height-border_width], 
                      outline=border_color, width=border_width)
        
        # Salvar a imagem
        card_path = f"temp_card_{member_data['user_id']}.png"
        img.save(card_path, quality=95)
        
        return card_path
