from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

class CardGenerator:
    def __init__(self):
        self.background_path = 'static/background.png'
        self.font_path = 'static/font.ttf'
        
    def generate_card(self, member_data):
        img = Image.open(self.background_path)
        draw = ImageDraw.Draw(img)
        
        try:
            font_large = ImageFont.truetype(self.font_path, 40)
            font_medium = ImageFont.truetype(self.font_path, 30)
            font_small = ImageFont.truetype(self.font_path, 25)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        positions = {
            'name': (150, 200),
            'function': (150, 260),
            'address': (150, 320),
            'birth_date': (150, 380),
            'status': (150, 440),
            'issue_date': (150, 500)
        }
        
        draw.text(positions['name'], f"Nome: {member_data['name']}", fill="black", font=font_large)
        draw.text(positions['function'], f"Função: {member_data['function']}", fill="black", font=font_medium)
        draw.text(positions['address'], f"Endereço: {member_data['address']}", fill="black", font=font_medium)
        draw.text(positions['birth_date'], f"Data Nasc.: {member_data['birth_date']}", fill="black", font=font_medium)
        draw.text(positions['status'], f"Status: {member_data['status']}", fill="black", font=font_medium)
        
        issue_date = datetime.now().strftime("%d/%m/%Y")
        draw.text(positions['issue_date'], f"Emitido em: {issue_date}", fill="black", font=font_small)
        
        card_path = f"temp_card_{member_data['user_id']}.png"
        img.save(card_path)
        
        return card_path