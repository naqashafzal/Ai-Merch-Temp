# src/template_generator.py

import os
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas as pdfcanvas

try:
    from cairosvg import svg2png
    CAIROSVG_AVAILABLE = True
except (ImportError, OSError):
    CAIROSVG_AVAILABLE = False

class TemplateGenerator:
    """Creates merchandise designs (PNGs and PDFs) based on brand assets."""
    def __init__(self, output_dir, domain_name):
        self.output_dir = output_dir
        self.domain_name = domain_name
        os.makedirs(self.output_dir, exist_ok=True)
        try:
            self.font_bold = ImageFont.truetype("arialbd.ttf", 24)
            self.font_regular = ImageFont.truetype("arial.ttf", 18)
        except IOError:
            self.font_bold = ImageFont.load_default()
            self.font_regular = ImageFont.load_default()

    def _prepare_logo(self, logo_path, max_size=(400, 400)):
        """Converts SVG logos to PNG and resizes all logos."""
        if logo_path.lower().endswith('.svg'):
            if CAIROSVG_AVAILABLE:
                prepared_logo_path = os.path.join(os.path.dirname(logo_path), "logo_converted.png")
                svg2png(url=logo_path, write_to=prepared_logo_path, output_width=max_size[0], output_height=max_size[1])
                logo_path = prepared_logo_path
            else:
                print("WARNING: SVG logo found but CairoSVG is not installed. Skipping logo.")
                return Image.new('RGBA', (1, 1), (0,0,0,0)) # Return tiny transparent image
        logo_img = Image.open(logo_path).convert("RGBA")
        logo_img.thumbnail(max_size, Image.Resampling.LANCZOS)
        return logo_img

    def create_mug_template(self, logo_path, primary_color):
        """Generates a coffee mug design."""
        try:
            canvas = Image.new('RGB', (900, 400), color=primary_color)
            logo_img = self._prepare_logo(logo_path, max_size=(300, 300))
            logo_x = (canvas.width - logo_img.width) // 2
            logo_y = (canvas.height - logo_img.height) // 2
            canvas.paste(logo_img, (logo_x, logo_y), logo_img)
            output_path = os.path.join(self.output_dir, "mug_design.png")
            canvas.save(output_path)
            pdf_path = self._create_pdf_output(output_path, "mug_print_ready.pdf")
            return {"design_path": output_path, "pdf_path": pdf_path}
        except Exception as e:
            print(f"Error creating mug template: {e}")
            return None

    def create_business_card_template(self, logo_path, primary_color, accent_color):
        """Generates a business card design."""
        try:
            W, H = 1050, 600
            canvas = Image.new('RGB', (W, H), color="#FFFFFF")
            draw = ImageDraw.Draw(canvas)
            draw.rectangle([(0, 0), (W // 3, H)], fill=primary_color)
            logo_img = self._prepare_logo(logo_path, max_size=(250, 250))
            logo_x, logo_y = ((W // 3) - logo_img.width) // 2, (H // 4) - (logo_img.height // 2)
            canvas.paste(logo_img, (logo_x, logo_y), logo_img)
            text_x, text_color = (W // 3) + 50, "#333333"
            draw.text((text_x, 150), "Your Name", font=self.font_bold, fill=text_color)
            draw.text((text_x, 190), "Job Title / Position", font=self.font_regular, fill=accent_color)
            draw.line([(text_x, 250), (W - 50, 250)], fill="#EEEEEE", width=2)
            draw.text((text_x, 280), "(123) 456-7890", font=self.font_regular, fill=text_color)
            draw.text((text_x, 320), f"hello@{self.domain_name}", font=self.font_regular, fill=text_color)
            draw.text((text_x, 360), self.domain_name, font=self.font_regular, fill=text_color)
            output_path = os.path.join(self.output_dir, "card_design.png")
            canvas.save(output_path)
            pdf_path = self._create_pdf_output(output_path, "card_print_ready.pdf")
            return {"design_path": output_path, "pdf_path": pdf_path}
        except Exception as e:
            print(f"Error creating business card template: {e}")
            return None

    def _create_pdf_output(self, image_path, pdf_filename):
        """Converts a generated PNG design into a PDF."""
        try:
            pdf_path = os.path.join(self.output_dir, pdf_filename)
            img = Image.open(image_path)
            c = pdfcanvas.Canvas(pdf_path, pagesize=img.size)
            c.drawImage(image_path, 0, 0, width=img.width, height=img.height)
            c.save()
            return pdf_path
        except Exception as e:
            print(f"Error creating PDF from {image_path}: {e}")
            return None