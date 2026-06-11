"""
SmartRoom Flask Backend
=======================
Run:
  pip install flask flask-socketio flask-cors flask-mail python-dotenv eventlet
  python app.py
"""

import os
import logging
from datetime import datetime
from collections import deque
from functools import wraps

from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from flask_mail import Mail, Message
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "smartroom-secret-2026")

CORS(app, resources={r"/api/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# ── Mail Config ───────────────────────────────────────────────────────────────
app.config["MAIL_SERVER"]         = os.getenv("MAIL_SERVER",  "smtp.gmail.com")
app.config["MAIL_PORT"]           = int(os.getenv("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"]        = True
app.config["MAIL_USERNAME"]       = os.getenv("MAIL_USERNAME", "")
app.config["MAIL_PASSWORD"]       = os.getenv("MAIL_PASSWORD", "")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_USERNAME", "")
mail = Mail(app)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ── In-Memory State ───────────────────────────────────────────────────────────
device_state = {
    "light": {"state": False, "updated_at": None, "updated_by": "system"},
    "fan":   {"speed": 0,     "updated_at": None, "updated_by": "system"},
    "sos":   {"triggered": False, "triggered_at": None, "triggered_by": None},
    "esp32": {"online": False, "last_seen": None, "ip_address": None, "firmware_version": "1.0.0"},
    "server": {"started_at": datetime.utcnow().isoformat() + "Z", "version": "1.0.0"}
}

action_logs = deque(maxlen=100)
connected_clients = 0

# ── Helpers ───────────────────────────────────────────────────────────────────
def now_iso():
    return datetime.utcnow().isoformat() + "Z"

def log_action(action, details=None, source="web"):
    entry = {"timestamp": now_iso(), "action": action, "details": details or {}, "source": source}
    action_logs.appendleft(entry)
    logger.info(f"[{source}] {action} | {details}")
    return entry

def broadcast_state(event="state_update"):
    socketio.emit(event, {"state": device_state, "timestamp": now_iso()})

def api_response(data=None, message="OK", status=200, error=None):
    resp = {"success": status < 400, "message": message}
    if data  is not None: resp["data"]  = data
    if error is not None: resp["error"] = error
    return jsonify(resp), status

def require_json(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not request.is_json:
            return api_response(message="Content-Type must be application/json", status=415)
        return f(*args, **kwargs)
    return decorated

# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health():
    return jsonify({"status": "ok", "time": now_iso()}), 200

# ── Status ────────────────────────────────────────────────────────────────────
@app.route("/api/status", methods=["GET"])
def get_status():
    return api_response(data={"devices": device_state, "clients_connected": connected_clients, "log_count": len(action_logs)})

# ── Light ─────────────────────────────────────────────────────────────────────
@app.route("/api/light", methods=["GET"])
def get_light():
    return api_response(data=device_state["light"])

@app.route("/api/light", methods=["POST"])
@require_json
def set_light():
    body   = request.get_json()
    source = body.get("source", "web")

    if "toggle" in body:
        new_state = not device_state["light"]["state"]
    elif "state" in body:
        new_state = bool(body["state"])
    else:
        return api_response(message="Provide 'state' (bool) or 'toggle' (true)", status=400)

    device_state["light"]["state"]      = new_state
    device_state["light"]["updated_at"] = now_iso()
    device_state["light"]["updated_by"] = source

    log_action("LIGHT_" + ("ON" if new_state else "OFF"), {"state": new_state}, source)
    broadcast_state()
    return api_response(data={"light": device_state["light"]}, message=f"Light {'ON' if new_state else 'OFF'}")

# ── Fan ───────────────────────────────────────────────────────────────────────
@app.route("/api/fan", methods=["GET"])
def get_fan():
    return api_response(data=device_state["fan"])

@app.route("/api/fan", methods=["POST"])
@require_json
def set_fan():
    body   = request.get_json()
    source = body.get("source", "web")

    if "speed" not in body:
        return api_response(message="Provide 'speed' (integer 0-5)", status=400)

    try:
        speed = int(body["speed"])
    except (ValueError, TypeError):
        return api_response(message="'speed' must be an integer", status=400)

    if speed < 0 or speed > 5:
        return api_response(message="'speed' must be between 0 and 5", status=400)

    device_state["fan"]["speed"]      = speed
    device_state["fan"]["updated_at"] = now_iso()
    device_state["fan"]["updated_by"] = source

    log_action(f"FAN_{'OFF' if speed == 0 else f'LEVEL_{speed}'}", {"speed": speed}, source)
    broadcast_state()
    return api_response(data={"fan": device_state["fan"]}, message=f"Fan {'OFF' if speed == 0 else f'Level {speed}'}")

# ── SOS ───────────────────────────────────────────────────────────────────────
@app.route("/api/sos", methods=["POST"])
@require_json
def trigger_sos():
    body    = request.get_json()
    trigger = bool(body.get("triggered", True))
    source  = body.get("source", "web")

    device_state["sos"]["triggered"]    = trigger
    device_state["sos"]["triggered_at"] = now_iso() if trigger else None
    device_state["sos"]["triggered_by"] = source if trigger else None

    if trigger:
        log_action("SOS_TRIGGERED", {"source": source}, source)
        broadcast_state("sos_alert")
        _send_sos_email(source)
    else:
        log_action("SOS_RESET", {}, source)
        broadcast_state()

    return api_response(data={"sos": device_state["sos"]}, message="SOS sent!" if trigger else "SOS reset")

def _send_sos_email(source):
    recipient = os.getenv("ALERT_EMAIL", app.config.get("MAIL_USERNAME", ""))
    if not recipient or not app.config["MAIL_USERNAME"]:
        logger.warning("SOS email not sent — MAIL_USERNAME not configured.")
        return
    try:
        msg = Message(
            subject="🚨 SmartRoom SOS ALERT",
            recipients=[recipient],
            html=f"""
            <h2 style="color:#e03e3e">🚨 Emergency SOS Alert</h2>
            <p>An SOS alert was triggered in SmartRoom.</p>
            <p><b>Time:</b> {now_iso()}</p>
            <p><b>Source:</b> {source}</p>
            <p>Please check on the user immediately.</p>
            """
        )
        mail.send(msg)
        logger.info(f"SOS email sent to {recipient}")
    except Exception as e:
        logger.error(f"SOS email failed: {e}")

# ── ESP32 Heartbeat ───────────────────────────────────────────────────────────
@app.route("/api/esp32/heartbeat", methods=["POST"])
@require_json
def esp32_heartbeat():
    body = request.get_json()
    device_state["esp32"]["online"]           = True
    device_state["esp32"]["last_seen"]        = now_iso()
    device_state["esp32"]["ip_address"]       = body.get("ip", request.remote_addr)
    device_state["esp32"]["firmware_version"] = body.get("firmware", "unknown")
    broadcast_state()
    return api_response(
        data={"current_state": {"light": device_state["light"]["state"], "fan": device_state["fan"]["speed"]}},
        message="Heartbeat received"
    )

@app.route("/api/esp32/offline", methods=["POST"])
def esp32_offline():
    device_state["esp32"]["online"]    = False
    device_state["esp32"]["last_seen"] = now_iso()
    log_action("ESP32_OFFLINE", {}, "esp32")
    broadcast_state()
    return api_response(message="ESP32 marked offline")

# ── Contact Form ──────────────────────────────────────────────────────────────
@app.route("/api/contact", methods=["POST"])
@require_json
def contact():
    body    = request.get_json()
    name    = body.get("name",    "").strip()
    email   = body.get("email",   "").strip()
    subject = body.get("subject", "").strip()
    message = body.get("message", "").strip()

    if not all([name, email, subject, message]):
        return api_response(message="All fields are required", status=400)

    recipient = os.getenv("CONTACT_EMAIL", "nithin.ise24@cmrit.ac.in")

    if not app.config["MAIL_USERNAME"]:
        log_action("CONTACT_FORM", {"name": name, "email": email}, "web")
        return api_response(message="Message received (email not configured on server)")

    try:
        msg = Message(
            subject=f"[SmartRoom Contact] {subject}",
            recipients=[recipient],
            reply_to=email,
            html=f"""
            <h3>New message from SmartRoom Contact Form</h3>
            <p><b>Name:</b> {name}</p>
            <p><b>Email:</b> {email}</p>
            <p><b>Subject:</b> {subject}</p>
            <hr>
            <p>{message}</p>
            """
        )
        mail.send(msg)
        log_action("CONTACT_EMAIL_SENT", {"name": name}, "web")
        return api_response(message="Message sent successfully!")
    except Exception as e:
        logger.error(f"Contact email error: {e}")
        return api_response(message="Failed to send email", status=500, error=str(e))

# ── Logs ──────────────────────────────────────────────────────────────────────
@app.route("/api/logs", methods=["GET"])
def get_logs():
    limit = min(int(request.args.get("limit", 20)), 100)
    return api_response(data={"logs": list(action_logs)[:limit], "total": len(action_logs)})

@app.route("/api/logs", methods=["DELETE"])
def clear_logs():
    action_logs.clear()
    return api_response(message="Logs cleared")

# ── WebSocket Events ──────────────────────────────────────────────────────────
@socketio.on("connect")
def on_connect():
    global connected_clients
    connected_clients += 1
    emit("state_update", {"state": device_state, "timestamp": now_iso()})

@socketio.on("disconnect")
def on_disconnect():
    global connected_clients
    connected_clients = max(0, connected_clients - 1)

@socketio.on("ping_server")
def on_ping(data):
    emit("pong_server", {"timestamp": now_iso()})

@socketio.on("client_action")
def on_client_action(data):
    action_type = data.get("type")
    value       = data.get("value")
    source      = data.get("source", "websocket")

    if action_type == "light":
        device_state["light"]["state"]      = bool(value)
        device_state["light"]["updated_at"] = now_iso()
        device_state["light"]["updated_by"] = source
        log_action("LIGHT_" + ("ON" if value else "OFF"), {"state": value}, source)
        broadcast_state()

    elif action_type == "fan":
        speed = max(0, min(5, int(value) if str(value).isdigit() else 0))
        device_state["fan"]["speed"]      = speed
        device_state["fan"]["updated_at"] = now_iso()
        device_state["fan"]["updated_by"] = source
        log_action(f"FAN_{'OFF' if speed==0 else f'LEVEL_{speed}'}", {"speed": speed}, source)
        broadcast_state()

    elif action_type == "sos":
        device_state["sos"]["triggered"]    = True
        device_state["sos"]["triggered_at"] = now_iso()
        device_state["sos"]["triggered_by"] = source
        log_action("SOS_TRIGGERED", {"source": source}, source)
        broadcast_state("sos_alert")
        _send_sos_email(source)

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port  = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "true").lower() == "true"
    logger.info(f"🚀 SmartRoom starting on http://localhost:{port}")
    socketio.run(app, host="0.0.0.0", port=port, debug=debug)
