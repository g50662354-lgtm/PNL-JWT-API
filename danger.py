import time
import requests
from flask import Flask, request, jsonify
from danger_ffjwt import guest_to_jwt

app = Flask(__name__)

# Developer credit
DEV_CREDIT = "@PNL_x_SRC"
DEV_TELEGRAM = "t.me/PNL_CODEX"

# ---------- Version Cache ----------
_versions_cache = {
    "ob_version": "OB52",
    "client_version": "1.120.1",
    "last_fetch": 0
}

def get_versions():
    """Fetch latest versions with 1 hour cache"""
    global _versions_cache
    now = time.time()

    if now - _versions_cache["last_fetch"] > 3600:
        try:
            resp = requests.get(
                "https://raw.githubusercontent.com/dangerapix/danger-ffjwt/main/versions.json",
                timeout=3
            )

            if resp.status_code == 200:
                data = resp.json()

                _versions_cache["ob_version"] = data.get("ob_version", "OB52")
                _versions_cache["client_version"] = data.get("client_version", "1.120.1")
                _versions_cache["last_fetch"] = now

        except Exception:
            pass

    return _versions_cache["ob_version"], _versions_cache["client_version"]


# ---------- Add developer header ----------
def add_dev_headers(response):
    response.headers["X-Developer"] = DEV_CREDIT
    return response


# ---------- Token Endpoint ----------
@app.route('/token', methods=['GET'])
def token_converter():

    args = request.args

    if "uid" not in args or "password" not in args:
        return add_dev_headers(jsonify({
            "success": False,
            "error": "Use ?uid=UID&password=PASSWORD",
            "credit": DEV_TELEGRAM
        })), 400

    uid = args.get("uid").strip()
    pwd = args.get("password").strip()

    if not uid or not pwd:
        return add_dev_headers(jsonify({
            "success": False,
            "error": "UID and password cannot be empty",
            "credit": DEV_TELEGRAM
        })), 400

    try:

        ob_ver, client_ver = get_versions()

        result = guest_to_jwt(
            uid,
            pwd,
            ob_version=ob_ver,
            client_version=client_ver
        )

        # Extract JWT token only
        if isinstance(result, dict):
            token = result.get("jwt_token")
        else:
            token = result

        response = jsonify([
            {
                "token": token
            }
        ])

        return add_dev_headers(response)

    except Exception as e:

        return add_dev_headers(jsonify({
            "success": False,
            "error": str(e),
            "credit": DEV_TELEGRAM
        })), 500


# ---------- Health Check ----------
@app.route('/')
def home():
    return jsonify({
        "api": "Free Fire Token API",
        "developer": DEV_TELEGRAM,
        "status": "running"
    })


# ---------- Run Server ----------
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
                )
