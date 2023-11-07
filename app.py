from flask_cors import CORS
import csv, re, os
import openai
from duckduckgo_search import ddg_news
from flask import Flask, request, jsonify

app = Flask(__name__)
CORS(app)

# Set the OpenAI API key based on environment
if os.environ.get('FLASK_ENV') == 'development':
    openai.api_key = 'YOUR_LOCAL_API_KEY'  # Replace with your local API key
else:
    openai.api_key = os.environ.get('OPENAI_API_KEY')
    
    
@app.route('/nyucs', methods=['POST'])
def nyucs_route():
    # Get the JSON data sent to the route
    data = request.json

    # Your processing here - appending "hello" to the input
    if data:
        response_data = {k: f"{v} hello" for k, v in data.items()}
    else:
        response_data = {"response": "hello"}

    # Return the modified data as JSON
    return jsonify({"response": response_data})



@app.route('/analyze', methods=['POST'])
def analyze_company():
    # Getting inputs from the request
    data = request.json
    company = data.get('company')
    model_version = 'gpt-3.5-turbo' if data.get('model_choice') == 'yes' else 'gpt-4'
    num_headlines = int(data.get('num_headlines', 10))
    temp = float(data.get('temperature', 0.3))

    # Construct the prompt for GPT
    sysPrompt = 'You are a financial advisor. When the user gives you a headline, ' \
                'respond with a number between -1.0 and 1.0, signifying whether the ' \
                'headline is extremely negative (-1.0), neutral (0.0), or extremely ' \
                'positive (1.0) for the stock value of {}.'.format(company)

    # Collect headlines from DDG News
    r = ddg_news(company, safesearch='Off', time='d')
    headlines = [res['title'] for res in r[:num_headlines]]

    scores = []
    total_score = 0

    for headline in headlines:
        score = float(re.findall(r'-?\d+\.\d+', askGPT(sysPrompt, headline, model_version, temp))[0])
        scores.append(score)
        total_score += score

    mean_score = total_score / len(scores)

    # Create a professional financial analysis based on the mean score
    analysis = "Based on the recent news headlines, the sentiment towards the stock value of {} is ".format(company)
    if mean_score > 0.5:
        analysis += "very positive."
    elif mean_score > 0:
        analysis += "slightly positive."
    elif mean_score == 0:
        analysis += "neutral."
    elif mean_score > -0.5:
        analysis += "slightly negative."
    else:
        analysis += "very negative."

    return jsonify({"analysis": analysis})


def askGPT(sysPrompt, headline, model_version, temp):
    resp = openai.ChatCompletion.create(
        model=model_version,
        temperature=temp,
        messages=[{'role': 'system', 'content': sysPrompt}, {'role': 'user', 'content': headline}]
    )
    return resp['choices'][0]['message']['content']


if __name__ == "__main__":
    if os.environ.get('FLASK_ENV') == 'development':
        app.run(host='127.0.0.1', port=5000)
    else:
        app.run(host='0.0.0.0', port=80)