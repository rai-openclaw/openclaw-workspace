
from flask import Flask, jsonify
app = Flask(__name__, import_name=__name__)

@app.route('/api/usage')
def api_usage():
    return jsonify({
        "apis": {
            "moonshot": {
                "name": "Moonshot",
                "billing_url": "https://platform.moonshot.ai/console"
            }
        }
    })

if __name__ == "__main__":
    app.run(port=8080)
