import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from markdownify import markdownify as md
import os

class PDFConverter:
    def __init__(self, tesseract_cmd=None):
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def pdf_to_md(self, pdf_path, md_path, lang='heb'):
        print(lang)
        print("Start converting PDF to md file")
        # Convert PDF to images
        pages = convert_from_path(pdf_path)
        
        all_text = ""
        
        for page in pages:
            text = pytesseract.image_to_string(page, lang=lang)
            all_text += text + "\n\n"
        
        md_text = md(all_text)
        
        with open(md_path, 'w', encoding='utf-8') as md_file:
            md_file.write(md_text)
            
        print(f"End Converted {pdf_path} to {md_path}")
