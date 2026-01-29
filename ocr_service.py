import streamlit as st
import os
from PIL import Image
import io
from typing import Optional
import base64
import requests
os.environ["GEMINI_API_KEY"] = "AIzaSyAiOpPPYkoYzrD_KIpjnb-7K_mNhMrXCA8"

class OCRService:
    """Service for extracting text from images using Google Gemini API"""

    def __init__(self):
        """Initialize Gemini API client"""
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

        if not self.api_key:
            st.warning("Gemini API key not found. Image OCR will not be available.")

    def extract_text_from_image(self, uploaded_file) -> Optional[str]:
        """
        Extract text from an uploaded image file using OCR

        Args:
            uploaded_file: Streamlit uploaded file object (image)

        Returns:
            Extracted text content or None if extraction fails
        """
        if not self.api_key:
            st.error("Gemini API key not available")
            return None

        try:
            # Read and prepare the image
            image_content = uploaded_file.read()

            # Reset file pointer for potential reuse
            uploaded_file.seek(0)

            # Validate and process image format
            try:
                pil_image = Image.open(io.BytesIO(image_content))
                # Convert to RGB if necessary
                if pil_image.mode in ('RGBA', 'LA', 'P'):
                    pil_image = pil_image.convert('RGB')

                # Save processed image to bytes
                img_byte_arr = io.BytesIO()
                pil_image.save(img_byte_arr, format='JPEG', quality=95)
                image_content = img_byte_arr.getvalue()

            except Exception as e:
                st.error(f"Error processing image: {str(e)}")
                return None

            # Convert image to base64
            image_base64 = base64.b64encode(image_content).decode('utf-8')

            # Create Gemini API request
            headers = {
                "Content-Type": "application/json"
            }

            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": "Extract all text from this image. Return only the extracted text content, without any explanations or formatting."
                            },
                            {
                                "inline_data": {
                                    "mime_type": "image/jpeg",
                                    "data": image_base64
                                }
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 2000
                }
            }

            url = f"{self.base_url}?key={self.api_key}"

            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                response_data = response.json()
                candidates = response_data.get('candidates', [])
                if candidates and 'content' in candidates[0]:
                    parts = candidates[0]['content'].get('parts', [])
                    if parts and 'text' in parts[0]:
                        extracted_text = parts[0]['text'].strip()
                        return extracted_text if extracted_text else None

                st.warning("No text detected in the image. Kindly check manually")
                return None
            else:
                st.error(f"Gemini API error: {response.status_code}")
                return None

        except Exception as e:
            st.error(f"Error during OCR processing: {str(e)}")
            return None

    def extract_text_with_confidence(self, uploaded_file) -> Optional[dict]:
        """
        Extract text with confidence scores using Gemini

        Args:
            uploaded_file: Streamlit uploaded file object (image)

        Returns:
            Dictionary containing extracted text and confidence information
        """
        # Use basic text extraction for now
        text = self.extract_text_from_image(uploaded_file)

        if text:
            return {
                'full_text': text,
                'confidence_score': 1.0  # Gemini generally has high accuracy
            }
        return None

    def preprocess_image_for_ocr(self, uploaded_file):
        """
        Preprocess image to improve OCR accuracy

        Args:
            uploaded_file: Streamlit uploaded file object (image)

        Returns:
            Preprocessed image bytes
        """
        try:
            # Read the image
            image_content = uploaded_file.read()
            uploaded_file.seek(0)

            # Open with PIL
            pil_image = Image.open(io.BytesIO(image_content))

            # Convert to RGB if necessary
            if pil_image.mode not in ('RGB', 'L'):
                pil_image = pil_image.convert('RGB')

            # Enhance image quality for better OCR
            # Resize if image is too small (OCR works better with larger images)
            width, height = pil_image.size
            if width < 1000 or height < 1000:
                # Scale up maintaining aspect ratio
                scale_factor = max(1000 / width, 1000 / height)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Convert to bytes
            img_byte_arr = io.BytesIO()
            pil_image.save(img_byte_arr, format='JPEG', quality=95)

            return img_byte_arr.getvalue()

        except Exception as e:
            st.error(f"Error preprocessing image: {str(e)}")
            # Return original image content as fallback
            uploaded_file.seek(0)
            return uploaded_file.read()

    def validate_api_connection(self) -> bool:
        """
        Validate that the Gemini API connection is working

        Returns:
            True if API is accessible, False otherwise
        """
        if not self.api_key:
            return False

        try:
            # Test with a simple request
            headers = {
                "Content-Type": "application/json"
            }

            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": "Hello, this is a test message."
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "maxOutputTokens": 10
                }
            }

            url = f"{self.base_url}?key={self.api_key}"

            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=10
            )

            return response.status_code == 200

        except Exception:
            return False
