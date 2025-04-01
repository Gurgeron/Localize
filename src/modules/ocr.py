#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OCR Module

This module handles text extraction from images using OCR (Optical Character Recognition)
and detects the language of extracted text using langdetect with enhanced context awareness.
"""

import os
import logging
import base64
import json
import numpy as np
import requests
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional, Union, Set
from PIL import Image

# OCR libraries
import easyocr

# Language detection
from langdetect import detect, DetectorFactory, LangDetectException

# Import our modules
from .config_loader import Config

# Set seed for deterministic language detection
DetectorFactory.seed = 0

# Setup logging
logger = logging.getLogger(__name__)

# Dictionary of common hospitality/property management terms that might be mistakenly identified
# These terms are considered valid in the target language regardless of detection
COMMON_HOSPITALITY_TERMS = {
    'fr': {
        # Common French hospitality terms that might be detected as English
        'code de confirmation', 'check-in', 'check-out', 'client', 'réservation', 
        'suite', 'standard', 'confirmation', 'premium', 'deluxe', 'basic',
        'superior', 'service', 'reception', 'wifi', 'breakfast', 'all-inclusive',
        'email', 'login', 'password', 'dashboard', 'menu', 'status', 'ok',
        'application', 'documents', 'contacts', 'filters', 'search', 'calendar',
        'profile', 'settings', 'notifications', 'booking', 'guest', 'room',
        'property', 'amenities', 'rating', 'review', 'payment', 'price',
        'tax', 'total', 'discount', 'promotion', 'cancel', 'refund'
    },
    'en': {
        # English terms that are commonly used without translation
        'check-in', 'check-out', 'booking', 'reservation', 'wifi',
        'suite', 'standard', 'confirmation', 'premium', 'deluxe', 'basic'
    }
}

class OCRProcessor:
    """
    OCRProcessor class for handling text extraction and language detection
    """
    
    def __init__(self):
        """
        Initialize the OCRProcessor
        """
        self.config = Config()
        self.reader = None
        self.target_language = self.config.get('ocr.target_language', 'fr')
        
        # Get language detection settings
        self.check_languages = self.config.get('language_detection.check_languages', ['en'])
        self.min_text_length = self.config.get('language_detection.min_text_length', 4)
        self.min_confidence = self.config.get('language_detection.min_confidence', 0.6)
        
        # Initialize OCR engine based on config
        self._initialize_ocr()
        
        # Load the hospitality term allowlist
        self.allowed_terms = self._load_allowed_terms()
    
    def _load_allowed_terms(self) -> Set[str]:
        """
        Load the allowed terms for the target language
        
        Returns:
            Set[str]: Set of allowed terms in lowercase
        """
        allowed_terms = set()
        
        # Add common terms from our dictionary
        if self.target_language in COMMON_HOSPITALITY_TERMS:
            allowed_terms.update(COMMON_HOSPITALITY_TERMS[self.target_language])
        
        # Add custom terms from config if available
        custom_terms = self.config.get('ocr.allowed_terms', [])
        allowed_terms.update([term.lower() for term in custom_terms])
        
        logger.info(f"Loaded {len(allowed_terms)} allowed terms for language {self.target_language}")
        return allowed_terms
    
    def _initialize_ocr(self) -> None:
        """
        Initialize the OCR engine based on configuration
        """
        ocr_engine = self.config.get('ocr.engine', 'easyocr')
        
        if ocr_engine == 'easyocr':
            logger.info("Initializing EasyOCR engine")
            
            # Get languages for OCR from config
            ocr_languages = self.config.get('ocr.easyocr.languages', ['en', 'fr'])
            use_gpu = self.config.get('ocr.easyocr.gpu', False)
            
            # Initialize EasyOCR reader
            try:
                logger.info(f"Loading EasyOCR with languages: {ocr_languages}")
                self.reader = easyocr.Reader(ocr_languages, gpu=use_gpu)
                logger.info("EasyOCR initialization complete")
            except Exception as e:
                logger.error(f"Error initializing EasyOCR: {e}")
                raise e
        elif ocr_engine == 'google_vision' or ocr_engine == 'google_cloud_vision':
            logger.info("Using Google Cloud Vision API for OCR")
            # No initialization needed for Google Cloud Vision API
            self.reader = None
            
            # Verify API key exists
            api_key = self.config.get('api_keys.google_vision', '')
            if not api_key:
                api_key = os.environ.get('GOOGLE_VISION_API_KEY', '')
                
            if not api_key:
                logger.warning("No Google Cloud Vision API key found. Please set the API key in config or as environment variable.")
                logger.warning("Falling back to EasyOCR.")
                # Fall back to EasyOCR
                ocr_languages = self.config.get('ocr.easyocr.languages', ['en', 'fr'])
                use_gpu = self.config.get('ocr.easyocr.gpu', False)
                self.reader = easyocr.Reader(ocr_languages, gpu=use_gpu)
        else:
            logger.error(f"Unsupported OCR engine: {ocr_engine}")
            raise ValueError(f"Unsupported OCR engine: {ocr_engine}")
    
    def extract_text_from_image(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Extract text from an image
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            List[Dict[str, Any]]: List of dictionaries with text information:
                - text: The extracted text
                - bbox: Bounding box coordinates [x1, y1, x2, y2]
                - confidence: Confidence score for the OCR detection
                - language: Detected language of the text
        """
        ocr_engine = self.config.get('ocr.engine', 'easyocr')
        
        if not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}")
            return []
            
        try:
            logger.info(f"Extracting text from image: {image_path}")
            
            # Get confidence threshold from config
            ocr_confidence_threshold = self.config.get('ocr.confidence_threshold', 0.5)
            
            if ocr_engine == 'easyocr':
                if not self.reader:
                    logger.error("EasyOCR engine not initialized")
                    return []
                    
                # Run OCR on the image
                # EasyOCR returns a list of [bbox, text, confidence]
                result = self.reader.readtext(image_path)
                
                # Convert to standardized format
                text_blocks = []
                for detection in result:
                    bbox, text, confidence = detection
                    
                    # Skip empty or low-confidence detections
                    if not text or confidence < ocr_confidence_threshold:
                        continue
                    
                    # Detect language
                    detected_language = self.detect_language(text)
                    
                    # Add to text blocks
                    text_blocks.append({
                        "text": text.strip(),
                        "bbox": bbox,
                        "confidence": confidence,
                        "language": detected_language or "unknown"
                    })
                
                logger.info(f"Extracted {len(text_blocks)} text blocks from image using EasyOCR")
                return text_blocks
            
            elif ocr_engine == 'google_vision' or ocr_engine == 'google_cloud_vision':
                # Get API key
                api_key = self.config.get('api_keys.google_vision', '')
                if not api_key:
                    api_key = os.environ.get('GOOGLE_VISION_API_KEY', '')
                    
                if not api_key:
                    logger.error("No Google Cloud Vision API key found")
                    return []
                
                # Prepare the image for the API
                with open(image_path, 'rb') as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                
                # API request
                vision_url = "https://vision.googleapis.com/v1/images:annotate"
                headers = {'Content-Type': 'application/json'}
                data = {
                    'requests': [
                        {
                            'image': {
                                'content': encoded_string
                            },
                            'features': [
                                {
                                    'type': 'TEXT_DETECTION'
                                }
                            ]
                        }
                    ]
                }
                
                response = requests.post(
                    f"{vision_url}?key={api_key}",
                    headers=headers,
                    json=data
                )
                
                if response.status_code != 200:
                    logger.error(f"Error from Google Cloud Vision API: {response.text}")
                    return []
                
                # Process response
                response_json = response.json()
                if 'responses' not in response_json or not response_json['responses']:
                    logger.warning("No text detected by Google Cloud Vision API")
                    return []
                
                annotations = response_json['responses'][0]
                if 'textAnnotations' not in annotations or not annotations['textAnnotations']:
                    logger.warning("No text annotations found by Google Cloud Vision API")
                    return []
                
                # Skip the first result which is the entire text
                text_annotations = annotations['textAnnotations'][1:]
                
                # Convert to our standard format
                text_blocks = []
                for annotation in text_annotations:
                    text = annotation.get('description', '').strip()
                    if not text:
                        continue
                    
                    # Extract bounding box vertices
                    vertices = annotation.get('boundingPoly', {}).get('vertices', [])
                    if len(vertices) == 4:
                        bbox = [
                            [vertices[0].get('x', 0), vertices[0].get('y', 0)],  # top-left
                            [vertices[1].get('x', 0), vertices[1].get('y', 0)],  # top-right
                            [vertices[2].get('x', 0), vertices[2].get('y', 0)],  # bottom-right
                            [vertices[3].get('x', 0), vertices[3].get('y', 0)]   # bottom-left
                        ]
                    else:
                        # Default bounding box if vertices are not available
                        bbox = [[0, 0], [0, 0], [0, 0], [0, 0]]
                    
                    # Set a default high confidence since Google doesn't provide one
                    confidence = 0.9
                    
                    # Detect language
                    detected_language = self.detect_language(text)
                    
                    text_blocks.append({
                        "text": text,
                        "bbox": bbox,
                        "confidence": confidence,
                        "language": detected_language or "unknown"
                    })
                
                logger.info(f"Extracted {len(text_blocks)} text blocks from image using Google Cloud Vision API")
                return text_blocks
            
            else:
                logger.error(f"Unsupported OCR engine: {ocr_engine}")
                return []
                
        except Exception as e:
            logger.error(f"Error extracting text from image {image_path}: {e}")
            return []
    
    def detect_language(self, text: str) -> Optional[str]:
        """
        Detect if text is English or French
        
        Args:
            text (str): Text to detect language for
            
        Returns:
            Optional[str]: 'en' for English, 'fr' for French, or None if uncertain
        """
        # Normalize the text for comparison
        normalized_text = text.lower().strip()
        
        # Skip very short text
        if len(normalized_text) < self.min_text_length:
            logger.debug(f"Text too short for language detection: '{text}'")
            return None
        
        # Check if the text is in the allowed terms for French
        if normalized_text in self.allowed_terms:
            logger.debug(f"Text '{text}' is in the allowed French terms list")
            return 'fr'
            
        try:
            # Use langdetect but only accept English or French results
            detected = detect(text)
            if detected == 'en':
                return 'en'
            elif detected == 'fr':
                return 'fr'
            else:
                # For any other language, try to determine if it's more likely English or French
                # This helps reduce false positives from other language detections
                probabilities = DetectorFactory().create().get_probabilities(text)
                en_prob = next((p.prob for p in probabilities if p.lang == 'en'), 0)
                fr_prob = next((p.prob for p in probabilities if p.lang == 'fr'), 0)
                
                if en_prob > fr_prob and en_prob > self.min_confidence:
                    return 'en'
                elif fr_prob > en_prob and fr_prob > self.min_confidence:
                    return 'fr'
                
            return None
            
        except LangDetectException:
            return None
    
    def is_missing_translation(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a text string is missing translation (i.e., it's in English instead of French)
        
        Args:
            text (str): Text to check
            
        Returns:
            Tuple[bool, Optional[str]]: (is_missing_translation, detected_language)
        """
        # Skip short text
        if len(text) < self.min_text_length:
            return False, None
            
        detected_language = self.detect_language(text)
        
        # If language detection failed or detected as French, not missing translation
        if not detected_language or detected_language == 'fr':
            return False, detected_language
            
        # If detected as English, check against allowed terms
        if detected_language == 'en':
            normalized_text = text.lower().strip()
            if normalized_text in self.allowed_terms:
                return False, 'fr'  # Consider it French if it's an allowed term
            return True, 'en'
            
        return False, None
    
    def process_screenshot(self, screenshot_path: str, page_name: str, modal_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Process a screenshot to extract text and detect missing translations
        
        Args:
            screenshot_path (str): Path to the screenshot file
            page_name (str): Name of the page
            modal_name (Optional[str]): Name of the modal, if applicable
            
        Returns:
            List[Dict[str, Any]]: List of dictionaries with information about missing translations:
                - text: The extracted text
                - language: Detected language
                - confidence: Confidence score for the OCR detection
                - bbox: Bounding box coordinates
                - page_name: Name of the page
                - modal_name: Name of the modal, if applicable
                - screenshot_path: Path to the screenshot file
        """
        issues = []
        
        try:
            # Extract text from the screenshot
            text_blocks = self.extract_text_from_image(screenshot_path)
            
            # Check each text block for missing translations
            for block in text_blocks:
                text = block["text"]
                
                # Skip very short text
                if len(text) < self.min_text_length:
                    continue
                
                is_missing, detected_language = self.is_missing_translation(text)
                
                if is_missing:
                    issue_info = {
                        "text": text,
                        "language": detected_language,
                        "confidence": block["confidence"],
                        "bbox": block["bbox"],
                        "page_name": page_name,
                        "modal_name": modal_name,
                        "screenshot_path": screenshot_path,
                        "issue_type": "Missing Translation"
                    }
                    issues.append(issue_info)
                    
                    logger.info(f"Found missing translation on {page_name} {'modal ' + modal_name if modal_name else ''}: '{text}' (detected as {detected_language})")
            
            logger.info(f"Found {len(issues)} missing translations in screenshot {screenshot_path}")
            return issues
            
        except Exception as e:
            logger.error(f"Error processing screenshot {screenshot_path}: {e}")
            return []


# Testing function for direct module execution
def main():
    """Main function for testing the OCR module"""
    processor = OCRProcessor()
    
    # Test with a sample image if provided
    test_image = "test_image.png"
    if os.path.exists(test_image):
        print(f"Testing OCR with image: {test_image}")
        text_blocks = processor.extract_text_from_image(test_image)
        print(f"Extracted {len(text_blocks)} text blocks")
        
        for i, block in enumerate(text_blocks):
            print(f"Block {i+1}: {block['text']} (confidence: {block['confidence']:.2f})")
            is_missing, lang = processor.is_missing_translation(block['text'])
            if is_missing:
                print(f"  - MISSING TRANSLATION: Detected as {lang}")
            else:
                print(f"  - Language: {lang}")
    else:
        print(f"Test image not found: {test_image}")

if __name__ == "__main__":
    main() 