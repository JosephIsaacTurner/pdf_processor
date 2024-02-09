import os
import fitz 
from PIL import Image
import io
 
def is_uniform_color(image_bytes, num_unique_colors=100, color_variation_threshold=0.40):
    """Function to check if an image is uniform color. 
    We want to avoid extracting images that are just a single color, because they are usually not useful."""
    try:
        image = Image.open(io.BytesIO(image_bytes))
        colors = image.getcolors(maxcolors=image.size[0] * image.size[1])

        if colors:
            # print(f"Number of unique colors: {len(colors)}")
            # display(colors)

            # Check if the number of unique colors is less than 100
            if len(colors) < num_unique_colors:
                return True

            count_of_most_common_color = max(colors, key=lambda x: x[1])[0]
            total_count = sum(count for count, color in colors)

            if total_count == 0:
                return False
            if count_of_most_common_color / total_count > (1 - color_variation_threshold):
                return True
        return False
    except Exception as e:
        # print(f"Error in is_uniform_color: {e}")
        return True

def extract_images(pdf_path, output_folder, min_size=6000):
    """
    Function to extract images from a PDF file using PyMuPDF.
    Does not work for scanned PDFS, but works very well for native PDFs.
    Extracts images that are embedded in the PDF.

    Will exclude images that are less than 6000 bytes in size or are uniform color.
    """

    output_folder = create_output_folder(output_folder)
    extracted_images = []  # List to store paths of extracted images

    try:
        doc = fitz.open(pdf_path)
        for i in range(len(doc)):
            for img in doc.get_page_images(i):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                output_image_path = os.path.join(output_folder, f"image{i}_{xref}.{image_ext}")
                
                # Exclude images that are less than 6000 bytes in size or are uniform color
                if len(image_bytes) > min_size and not is_uniform_color(image_bytes):
                    with open(output_image_path, "wb") as image_file:
                        image_file.write(image_bytes)
                    if os.path.exists(output_image_path):
                        extracted_images.append(output_image_path)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        doc.close()

    # print("extracted {} images from {}".format(len(extracted_images), pdf_path))
    return extracted_images

def extract_text(pdf_path, output_folder):
    """Function to extract text from a PDF file using PyMuPDF.
    Works well for native PDFs, but not for scanned PDFs.
    It does not do OCR. 

    I don't think OCR is necessary for our use case, because we are only interested in extracting text from native PDFs.
    OCR is pointless for native PDFs, because the text is already embedded in the PDF.
    Image extraction only works for native PDFs, because it extracts the images embedded in the PDF.
    So, OCR on scanned PDFs is a dead end unless we can find a way to extract the images from the scanned PDFs as well.

    Maybe later we can convert the PDF to images, slice up the images into smaller images, 
    and then run our model on the smaller images to identify brain images. But, almost all of our PDFs are native PDFs anyway.
    """
    try: 
        with fitz.open(pdf_path) as doc:
            text = ""
            for page in doc:
                text += page.get_text()
        # Write text to .txt file
        with open(os.path.join(output_folder, "text.txt"), "w") as text_file:
            text_file.write(text)
        return output_folder + "/text.txt"
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
def create_output_folder(folder_name):
    """Function to create a folder if it does not exist."""
    if not os.path.exists(folder_name):
        print(f"Creating folder: {folder_name}")
        os.makedirs(folder_name)
    return os.path.abspath(folder_name)
