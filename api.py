"""
api.py - Flask API server for study space finder
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent / "utils"))

from utils.query import query_study_spaces, get_available_buildings

app = Flask(__name__)
CORS(app)  # Enable CORS for React Native

@app.route('/')
def index():
    return "Study Space Finder API is running."

@app.route('/api/buildings', methods=['GET'])
def get_buildings():
    """Get all available buildings"""
    try:
        buildings = get_available_buildings()
        return jsonify({
            "success": True,
            "data": buildings
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/search', methods=['POST'])
def search_spaces():
    """
    Search for study spaces based on filters
    
    Request body:
    {
        "filters": {
            "capacity_range": "5-10",
            "talking_allowed": true,
            "study_room": false,
            "indoor": true,
            "tech_enhanced": true,
            "has_printer": true,
            "building": "LANGSON"
        },
        "user_location": {
            "latitude": 33.6459,
            "longitude": -117.8443
        },
        "max_distance": 0.5
    }
    """
    try:
        data = request.json
        filters = data.get('filters')
        user_location = data.get('user_location')
        max_distance = data.get('max_distance')
        
        results = query_study_spaces(
            filters=filters,
            user_location=user_location,
            max_distance=max_distance
        )
        
        return jsonify({
            "success": True,
            "count": len(results),
            "data": results
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "success": True,
        "message": "API is running"
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)