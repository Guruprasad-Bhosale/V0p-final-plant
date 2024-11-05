from flask import Flask, request, jsonify, render_template, send_from_directory
import requests
import base64
import os
import logging

# Create the Flask app with the correct template and static folders
app = Flask(__name__, template_folder='.', static_folder='.')

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Load API key from environment variables or set directly here
API_KEY = os.getenv("API_KEY", "asIGc21oESmXngG1uZaoiQAqDjiTJlMYekeGLpnUStn1et1PdY")  # Replace with actual key in production
if not API_KEY:
    raise ValueError("API key for plant.id is not set.")

# Set maximum content length for file uploads (16MB)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Helper function to encode image
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# Helper function to send the plant identification request
def identify_plant(base64_image):
    data = {
        "images": [base64_image],
        "modifiers": ["crops_fast", "similar_images"],
        "plant_language": "en",
        "plant_details": ["common_names", "url", "wiki_description", "taxonomy"]
    }

    headers = {
        "Content-Type": "application/json",
        "Api-Key": API_KEY
    }

    response = requests.post("https://api.plant.id/v2/identify", json=data, headers=headers)
    return response.json()

# Route for home page
@app.route('/')
def home():
    return render_template('index.html')

# Route for about page
@app.route('/about')
def about():
    return render_template('about.html')

# Route for scan page
@app.route('/scan')
def scan():
    return render_template('scan.html')

# API endpoint for identifying plants
@app.route('/api/identify-plant', methods=['POST'])
def api_identify_plant():
    try:
        if 'file' not in request.files:
            app.logger.error("No file part in the request")
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            app.logger.error("No selected file")
            return jsonify({"error": "No selected file"}), 400
        
        if file:
            base64_img = encode_image(file)
            app.logger.info("Sending request to plant.id API")
            result = identify_plant(base64_img)
            
            if result.get('suggestions'):
                plant = result['suggestions'][0]
                name = plant['plant_name']
                common_names = plant['plant_details'].get('common_names', [])
                description = plant['plant_details'].get('wiki_description', {}).get('value', '')
                
                formatted_response = {
                    "images": [base64_img],
                    "name": name,
                    "common_names": common_names,
                    "info": description
                }
                
                app.logger.info(f"Plant identified: {name}")
                return jsonify(formatted_response)
            else:
                app.logger.error("No plant suggestions returned")
                return jsonify({"error": "Unable to identify the plant"}), 404

        app.logger.error("Unexpected error occurred")
        return jsonify({"error": "An unexpected error occurred"}), 500
    
    except requests.RequestException as e:
        app.logger.exception(f"API request failed: {str(e)}")
        return jsonify({"error": "Failed to connect to the plant identification service"}), 503
    except Exception as e:
        app.logger.exception(f"Exception occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

# Route for result page
@app.route('/result')
def result():
    return render_template('result.html')

# Serve static files
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

# Error Handlers
@app.errorhandler(413)
def too_large(e):
    return "File is too large. Maximum size is 16MB.", 413

@app.errorhandler(404)
def not_found(e):
    return "The requested URL was not found on the server.", 404

@app.errorhandler(500)
def internal_error(e):
    return "An internal server error occurred.", 500

if __name__ == '__main__':
    # In production, set debug=False
    app.run(debug=True)