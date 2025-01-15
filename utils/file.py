import fitz  # PyMuPDF
import io
from PIL import Image
import pytesseract
from fastapi import File, UploadFile
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
import os
import shutil
import tempfile
import boto3
from secrets import token_hex
from dotenv import load_dotenv
load_dotenv()

class FileUtils:
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),  
        )
        self.bucket_name = os.environ.get("BUCKET_NAME")
        self.UPLOAD_FOLDER = "uploads/" 
    @staticmethod
    def extract_images_from_page(doc, page):
        images = []
        image_list = page.get_images(full=True)
        for image_index, img in enumerate(page.get_images(full=True)):
            # get the XREF of the image
            xref = img[0]
            # extract the image bytes
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]

            # get the image as a PIL object
            image = Image.open(io.BytesIO(image_bytes))
            images.append(image)
        return images

    # Function to extract text from all images in a PDF page
    @staticmethod
    def extract_text_from_images(images):
        text = ""
        for image in images:
            text += pytesseract.image_to_string(image)
        return text

    # Function to extract text from a PDF, including text in images
    @staticmethod
    def extract_text_from_pdf_with_images(pdf_path):
        # Open the PDF file
        doc = fitz.open(pdf_path)
        total_text = ""

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)

            # Extract text directly from the page
            total_text += page.get_text()

            # Extract images from the page and then extract text from these images
            images = FileUtils.extract_images_from_page(doc, page)
            images_text = FileUtils.extract_text_from_images(images)
            total_text += images_text

        # Remember to close the document when done
        doc.close()
        return total_text
    def upload_file(self,files: UploadFile = File(...)):
        with open(os.path.join(self.UPLOAD_FOLDER, files.filename), "wb") as buffer:
            shutil.copyfileobj(files.file, buffer)
        file_path = os.path.join(self.UPLOAD_FOLDER, files.filename)
        
        extract_text = FileUtils.extract_text_from_pdf_with_images(file_path)
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            temp_file.write(extract_text)
        file_name = f"{token_hex(10)}.txt"
        try:
            self.s3.upload_file(temp_file.name, self.bucket_name, file_name)
        finally:
            os.remove(temp_file.name)
            os.remove(file_path)
        return file_name