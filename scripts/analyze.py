import os
import pdfplumber
import PyPDF2
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTImage
import fitz 
from PIL import Image
import io

# This one works, but lower resolution
def extract_images_pdfplumber(pdf_path, output_folder):
    output_folder = create_output_folder(output_folder)

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                print(f"Processing page: {i}")
                im = page.to_image()  # Convert page to an image
                pil_image = im.annotated  # Get the PIL Image object

                for image_index, image in enumerate(page.images):
                    print(f"Image data: {image}")  # Print the image data for debugging
                    bbox = (image["x0"], image["top"], image["x1"], image["bottom"])
                    cropped_im = pil_image.crop(bbox)  # Cropping the image using PIL's crop method
                    output_path = os.path.join(output_folder, f"page_{i}_img_{image_index}.png")
                    cropped_im.save(output_path, "PNG")
                    print(f"Saved image to {output_path}")

    except Exception as e:
        print(f"An error occurred in extract_images_pdfplumber: {e}")
 
# This one works best so far
def extract_images_pymupdf(pdf_path, output_folder):
    output_folder = create_output_folder(output_folder)

    try:
        doc = fitz.open(pdf_path)
        for i in range(len(doc)):
            print(f"Processing page: {i}")
            for img in doc.get_page_images(i):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                output_image_path = os.path.join(output_folder, f"image{i}_{xref}.{image_ext}")
                print(f"Attempting to write image to {output_image_path}")
                with open(output_image_path, "wb") as image_file:
                    image_file.write(image_bytes)
                if os.path.exists(output_image_path):
                    print(f"Image written successfully: {output_image_path}, Size: {os.path.getsize(output_image_path)} bytes")
                else:
                    print(f"Failed to write image: {output_image_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        doc.close()

def create_output_folder(folder_name):
    if not os.path.exists(folder_name):
        print(f"Creating folder: {folder_name}")
        os.makedirs(folder_name)
    return os.path.abspath(folder_name)
