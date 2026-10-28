"""
Base64 Image Test for Leaf Disease Detection
===========================================

This script demonstrates how to send base64 image data directly to the detector.
"""

import sys
import base64
from pathlib import Path

# Add the Leaf Disease directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "Leaf Disease"))

from main import LeafDiseaseDetector


def test_with_base64_data(base64_image_string: str):
    """
    Test disease detection with base64 image data

    Args:
        base64_image_string (str): Base64 encoded image data
    """
    detector = LeafDiseaseDetector()
    return detector.analyze_leaf_image_base64(base64_image_string)


def convert_image_to_base64_and_test(image_bytes: bytes):
    """
    Convert image bytes to base64 and test it

    Args:
        image_bytes (bytes): Image data in bytes
    """
    if not image_bytes:
        raise ValueError("No image bytes provided")

    base64_string = base64.b64encode(image_bytes).decode('utf-8')
    return test_with_base64_data(base64_string)


def main():
    """Test with base64 conversion"""
    image_path = Path(__file__).parent / "Media" / "brown-spot-4 (1).jpg"
    convert_image_to_base64_and_test(image_path.read_bytes())


if __name__ == "__main__":
    main()
