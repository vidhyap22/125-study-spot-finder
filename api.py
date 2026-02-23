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
from personal_model.store_personal_model_data import add_user, delete_bookmarks, store_bookmarks, store_filter_info, store_spot_feedback, store_spot_view, store_study_session

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


@app.route('/api/personal_model/search_filter', methods=['POST'])
def search_filter_todata():
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
        store_filter_info(user_id, filters, debug)
        return jsonify({
            "success": True,
            "received_filters": filters
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    
@app.route('/api/personal_model/study_session', methods=['POST'])
def study_session_todata():
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON body provided"
            }), 400

        user_id = data.get("user_id")
        session = data.get("session")
        debug = data.get("debug", False)
        
        if not user_id:
            return jsonify({
                "success": False,
                "error": "user_id is required"
            }), 400

        if not isinstance(session, dict):
            return jsonify({
                "success": False,
                "error": "session must be a JSON object"
            }), 400

        fields = session.keys()
        if "study_space_id" not in fields or "building_id" not in fields or "started_at" not in fields or "ended_at" not in fields or "start_date" not in fields or "end_date" not in fields:
           return jsonify({
                "success": False,
                "error": "session miss required fields"
            }), 400 

        print("Received session:", session)
        store_study_session(user_id, session, debug)
        return jsonify({
            "success": True,
            "received_session": session
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    
@app.route('/api/personal_model/add_bookmark', methods=['POST'])
def add_bookmarks_todata():
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON body provided"
            }), 400

        user_id = data.get("user_id")
        bookmark = data.get("bookmark")
        debug = data.get("debug", False)
        
        if not user_id:
            return jsonify({
                "success": False,
                "error": "user_id is required"
            }), 400

        if not isinstance(bookmark, dict):
            return jsonify({
                "success": False,
                "error": "bookmark must be a JSON object"
            }), 400

        fields = bookmark.keys()
        if "study_space_id" not in fields or "building_id" not in fields or "created_at" not in fields:
           return jsonify({
                "success": False,
                "error": "bookmark miss required fields"
            }), 400 

        print("Received bookmark:", bookmark)
        store_bookmarks(user_id, bookmark, debug)
        return jsonify({
            "success": True,
            "received_bookmark": bookmark
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/personal_model/delete_bookmark', methods=['POST'])
def delete_bookmarks_todata():
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON body provided"
            }), 400

        user_id = data.get("user_id")
        bookmark = data.get("bookmark")
        debug = data.get("debug", False)
        
        if not user_id:
            return jsonify({
                "success": False,
                "error": "user_id is required"
            }), 400

        if not isinstance(bookmark, dict):
            return jsonify({
                "success": False,
                "error": "bookmark must be a JSON object"
            }), 400

        fields = bookmark.keys()
        if "study_space_id" not in fields:
           return jsonify({
                "success": False,
                "error": "bookmark miss required fields (study_space_id)"
            }), 400 

        print("Received bookmark:", bookmark)
        delete_bookmarks(user_id, bookmark, debug)
        return jsonify({
            "success": True,
            "received_bookmark": bookmark
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/personal_model/spot_view', methods=['POST'])
def spot_view_todata():
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON body provided"
            }), 400

        user_id = data.get("user_id")
        view = data.get("view")
        debug = data.get("debug", False)
        
        if not user_id:
            return jsonify({
                "success": False,
                "error": "user_id is required"
            }), 400

        if not isinstance(view, dict):
            return jsonify({
                "success": False,
                "error": "view must be a JSON object"
            }), 400

        fields = view.keys()
        if "study_space_id" not in fields or "building_id" not in fields or "opened_at" not in fields:
           return jsonify({
                "success": False,
                "error": "view miss required fields"
            }), 400 

        print("Received view:", view)
        store_spot_view(user_id, view, debug)
        return jsonify({
            "success": True,
            "received_view": view
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/personal_model/spot_feedback', methods=['POST'])
def spot_feedback_todata():
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON body provided"
            }), 400

        user_id = data.get("user_id")
        feedback = data.get("feedback")
        debug = data.get("debug", False)
        
        if not user_id:
            return jsonify({
                "success": False,
                "error": "user_id is required"
            }), 400

        if not isinstance(feedback, dict):
            return jsonify({
                "success": False,
                "error": "feedback must be a JSON object"
            }), 400

        fields = feedback.keys()
        if "study_space_id" not in fields or "building_id" not in fields or "rating" not in fields or "updated_at" not in fields:
           return jsonify({
                "success": False,
                "error": "feedback miss required fields"
            }), 400 

        print("Received feedback:", feedback)
        store_spot_feedback(user_id, feedback, debug)
        return jsonify({
            "success": True,
            "received_feedback": feedback
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/personal_model/add_user', methods=['POST'])
def add_user_todata():
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON body provided"
            }), 400

        user_id = data.get("user_id")
        info = data.get("info")
        debug = data.get("debug", False)
        
        if not user_id:
            return jsonify({
                "success": False,
                "error": "user_id is required"
            }), 400

        if not isinstance(info, dict):
            return jsonify({
                "success": False,
                "error": "feedback must be a JSON object"
            }), 400

        fields = info.keys()
        if "created_at" not in fields:
           return jsonify({
                "success": False,
                "error": "feedback miss required fields(created_at)"
            }), 400 

        print("Received user:", user_id)
        add_user(user_id, info, debug)
        return jsonify({
            "success": True,
            "received_user": user_id
        }), 200

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