from flask import Flask, request, jsonify
import base64
import cv2
import numpy as np
import requests
import logging
from io import BytesIO
from PIL import Image
import khandy
from insectid import InsectDetector, InsectIdentifier

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the insect detection and identification models
detector = InsectDetector()
identifier = InsectIdentifier()

def decode_base64_image(base64_string):
    """Decode base64 string to OpenCV image format"""
    try:
        # Remove data URL prefix if present
        if base64_string.startswith('data:image'):
            base64_string = base64_string.split(',')[1]
        
        # Decode base64 to bytes
        image_bytes = base64.b64decode(base64_string)
        
        # Convert to PIL Image
        pil_image = Image.open(BytesIO(image_bytes))
        
        # Convert PIL to OpenCV format
        opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        return opencv_image
    except Exception as e:
        logger.error(f"Error decoding base64 image: {str(e)}")
        return None

def get_gbif_species_id(latin_name):
    """Get GBIF species ID from Latin name using GBIF API"""

    # GBIF species search API
    url = "https://api.gbif.org/v1/species"
    params = {
        'name': latin_name,
        'offest': 0,
        'limit': 1
    }

    try:    
        # Log the outgoing request
        logger.info(f"GBIF API Request - URL: {url}")
        logger.info(f"GBIF API Request - Parameters: {params}")
        logger.info(f"GBIF API Request - Species: {latin_name}")
        
        response = requests.get(url, params=params, timeout=10)
        
        # Log response status
        logger.info(f"GBIF API Response - Status Code: {response.status_code}")
        logger.info(f"GBIF API Response - Headers: {dict(response.headers)}")
        
        response.raise_for_status()
        
        data = response.json()
        
        # Log response data
        logger.info(f"GBIF API Response - Data: {data}")
        
        if data.get('results') and len(data['results']) > 0:
            species = data['results'][0]
            gbif_id = species.get('key')
            logger.info(f"GBIF API Success - Found species ID {gbif_id} for {latin_name}")
            return gbif_id
        else:
            logger.warning(f"GBIF API Warning - No species found for: {latin_name}")
            logger.warning(f"GBIF API Warning - Response data: {data}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"GBIF API Error - Request failed for {latin_name}: {str(e)}")
        logger.error(f"GBIF API Error - URL: {url}")
        logger.error(f"GBIF API Error - Parameters: {params}")
        return None
    except Exception as e:
        logger.error(f"GBIF API Error - Unexpected error in lookup for {latin_name}: {str(e)}")
        return None

def process_insect_identification(image):
    """Process image for insect identification"""
    try:
        # Resize image if too large (following demo.py pattern)
        if max(image.shape[:2]) > 1280:
            image = khandy.resize_image_long(image, 1280)
        
        # Detect insects in the image
        boxes, confs, classes = detector.detect(image)
        
        identified_insects = []
        
        for box, conf, class_ind in zip(boxes, confs, classes):
            box = box.astype(np.int32)
            box_width = box[2] - box[0]
            box_height = box[3] - box[1]
            
            # Skip small detections (following demo.py pattern)
            if box_width < 30 or box_height < 30:
                continue
            
            # Crop the detected region
            cropped = khandy.crop_or_pad(image, box[0], box[1], box[2], box[3])
            
            # Identify the insect species
            results = identifier.identify(cropped)
            
            if results and len(results) > 0:
                top_result = results[0]
                probability = top_result.get('probability', 0.0)
                latin_name = top_result.get('latin_name', 'Unknown')
                
                # Get GBIF species ID
                gbif_id = get_gbif_species_id(latin_name) if latin_name != 'Unknown' else None
                
                identified_insects.append({
                    'probability': float(probability),  # Convert numpy float32 to Python float
                    'latin_name': latin_name,
                    'gbif_id': gbif_id
                })
        
        return identified_insects
        
    except Exception as e:
        logger.error(f"Error in insect identification: {str(e)}")
        raise

@app.route('/api/v1/identify', methods=['POST'])
def identify_insect():
    """Main endpoint for insect identification"""
    try:
        # Validate request content type
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type must be application/json',
                'status_message': 'Invalid content type'
            }), 400
        
        # Get request data
        data = request.get_json()
        
        # Validate required fields (removed status_message from request)
        required_fields = ['custom_id', 'image_base64']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'Missing required field: {field}',
                    'status_message': 'Missing required fields'
                }), 400
        
        custom_id = data['custom_id']
        image_base64 = data['image_base64']
        
        # Decode base64 image
        image = decode_base64_image(image_base64)
        if image is None:
            return jsonify({
                'error': 'Invalid base64 image data',
                'status_message': 'Failed to decode image'
            }), 400
        
        # Process insect identification
        identified_insects = process_insect_identification(image)
        
        # Check if any insects were identified
        if not identified_insects:
            return jsonify({
                'error': 'No insects detected in the image',
                'status_message': 'No insects found'
            }), 400
        
        # Check confidence threshold (0.10 minimum)
        max_probability = max(insect['probability'] for insect in identified_insects)
        if max_probability < 0.10:
            return jsonify({
                'error': 'Low confidence identification',
                'status_message': 'Low confidence identification'
            }), 400
        
        # Prepare successful response
        response_data = {
            'custom_id': custom_id,
            'identified_insects': identified_insects,
            'status_message': 'Success'
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Unexpected error in identify_insect: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'status_message': 'Processing failed'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)