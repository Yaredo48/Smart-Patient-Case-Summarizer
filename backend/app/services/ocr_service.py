import os
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class OCRService:
    """Service for extracting text from images and PDFs using Tesseract OCR."""
    
    def __init__(self):
        self.tesseract_config = '--oem 3 --psm 6'  # LSTM OCR Engine, Assume single uniform block of text
    
    def process_pdf(self, pdf_path: str) -> str:
        """
        Convert PDF to images and extract text using OCR.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text from all pages
        """
        try:
            logger.info(f"Processing PDF: {pdf_path}")
            
            # Convert PDF to images (300 DPI for better OCR accuracy)
            images = convert_from_path(pdf_path, dpi=300)
            
            texts = []
            for page_num, image in enumerate(images, 1):
                logger.info(f"Processing page {page_num}")
                
                # Preprocess image
                processed_image = self._preprocess_image(image)
                
                # Extract text
                text = pytesseract.image_to_string(
                    processed_image,
                    config=self.tesseract_config
                )
                
                texts.append(f"=== Page {page_num} ===\n{text}")
            
            full_text = "\n\n".join(texts)
            logger.info(f"Extracted {len(full_text)} characters from {len(images)} pages")
            
            return full_text
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
            raise
    
    def process_image(self, image_path: str) -> str:
        """
        Extract text from an image file.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted text
        """
        try:
            logger.info(f"Processing image: {image_path}")
            
            # Load and preprocess image
            image = Image.open(image_path)
            processed_image = self._preprocess_image(image)
            
            # Extract text
            text = pytesseract.image_to_string(
                processed_image,
                config=self.tesseract_config
            )
            
            logger.info(f"Extracted {len(text)} characters from image")
            return text
            
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {str(e)}")
            raise
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR accuracy.
        
        Args:
            image: PIL Image object
            
        Returns:
            Preprocessed PIL Image
        """
        # Convert to grayscale
        image = image.convert('L')
        
        # Enhance contrast
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        # Optionally resize if image is too small
        width, height = image.size
        if width < 1000:
            scale_factor = 1000 / width
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return image
    
    def extract_text_from_file(self, file_path: str, file_type: str) -> str:
        """
        Extract text from a file based on its type.
        
        Args:
            file_path: Path to the file
            file_type: Type of file (pdf, jpg, png, etc.)
            
        Returns:
            Extracted text
        """
        file_type = file_type.lower()
        
        if file_type == 'pdf':
            return self.process_pdf(file_path)
        elif file_type in ['jpg', 'jpeg', 'png', 'tiff', 'bmp']:
            return self.process_image(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")


# Singleton instance
ocr_service = OCRService()
