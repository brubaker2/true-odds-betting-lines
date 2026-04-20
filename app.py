from flask import Flask, jsonify, send_from_directory
import urllib.request
import json
import os

app = Flask(__name__, static_folder='static')

API_KEY = os.environ.get('ODDS_API_KEY')
BASE_URL = 'https://api.the-odds-api.com/v4'


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/api/odds/<sport>')
def get_odds(sport):
    url = (
        f"{BASE_URL}/sports/{sport}/odds/"
        f"?apiKey={API_KEY}"
        f"&regions=us"
        f"&markets=h2h,spreads,totals"
        f"&oddsFormat=american"
        f"&dateFormat=iso"
    )
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            remaining = response.headers.get('x-requests-remaining', 'unknown')
            return jsonify({'data': data, 'remaining': remaining})
    except urllib.error.HTTPError as e:
        body = json.loads(e.read().decode())
        return jsonify({'error': body.get('message', str(e))}), e.code
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
