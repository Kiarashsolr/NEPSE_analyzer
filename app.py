import openai
from flask import Flask, jsonify, request

app = Flask(__name__)

openai.api_key = os.environ.get('OPENAI_API_KEY')

@app.route('/analyze', methods=['POST'])
def analyze_company():
    data = request.json
    company = data.get('company', 'Apple')  # Default to Apple for testing

    sysPrompt = 'What do you think about {} as a company?'.format(company)

    response = askGPT(sysPrompt)
    
    return jsonify({"analysis": response})

def askGPT(prompt):
    resp = openai.Completion.create(
        model="text-davinci-002",
        prompt=prompt,
        max_tokens=100
    )
    return resp.choices[0].text.strip()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
