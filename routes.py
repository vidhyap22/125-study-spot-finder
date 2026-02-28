# routes.py
from flask import Blueprint, jsonify, request
from automation import updater_service


bp = Blueprint("update_routes", __name__)

@bp.post("/api/update/start")
def api_start_update():
    body = request.get_json(silent=True) or {}
    interval_sec = int(body.get("interval_sec", 300))
    run_immediately = bool(body.get("run_immediately", True))

    try:
        st = updater_service.start(interval_sec=interval_sec, run_immediately=run_immediately)
        return jsonify({"success": True, "status": st})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@bp.post("/api/update/stop")
def api_stop_update():
    st = updater_service.stop()
    return jsonify({"success": True, "status": st})


@bp.get("/api/update/status")
def api_update_status():
    return jsonify({"success": True, "status": updater_service.status()})