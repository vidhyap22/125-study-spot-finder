"""
api.py - Flask API server for study space finder
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent / "utils"))

from utils.query import retrieve_ranked_study_spaces, get_available_buildings

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
    try:
        data = request.json or {}

        filters = data.get('filters', {})
        user_id = data.get('user_id')  
        debug = data.get('debug', False)

        if not user_id:
            return jsonify({
                "success": False,
                "error": "user_id is required for personalized ranking"
            }), 400

        # Call new ranking pipeline
        results = retrieve_ranked_study_spaces(
            user_id=user_id,
            filters=filters,
            debug=debug
        )

        return jsonify({
            "success": True,
            "count": len(results),
            "data": results
        })

    except Exception as e:
        print("API ERROR:", e)  
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

"""
@app.route('/api/search', methods=['POST'])
def search_spaces_personal_model():
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON body provided"
            }), 400

        user_id = data.get("user_id")
        filters = data.get("filters")
        debug = data.get("debug", False)

        if not user_id:
            return jsonify({
                "success": False,
                "error": "user_id is required"
            }), 400

        if not isinstance(filters, dict):
            return jsonify({
                "success": False,
                "error": "filters must be a JSON object"
            }), 400


        print("Received filters:", filters)

        return jsonify({
            "success": True,
            "received_filters": filters
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
"""

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "success": True,
        "message": "API is running"
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)