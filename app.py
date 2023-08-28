from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze_company():
    return jsonify({"analysis": "Test successful!"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
