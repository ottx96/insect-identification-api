import requests
import base64
import json

def test_identify_endpoint():
    """Test the insect identification API endpoint"""
    
    # Read and encode a test image
    try:
        with open('images/mistkäfer.jpg', 'rb') as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print("Please place a test image named 'mistkäfer.jpg.jpg' in the project images directory")
        return
    
    # Prepare request data (removed status_message from request)
    request_data = {
        "custom_id": "test_identification_001",
        "image_base64": image_base64
    }
    
    # Make API request
    url = "http://localhost:5000/api/v1/identify"
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, json=request_data, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")

if __name__ == '__main__':
    test_identify_endpoint()