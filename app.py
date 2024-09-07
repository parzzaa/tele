from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Example route for testingheroku --version
@app.route('/')
def home():
    return render_template('index.html')  # Serves the HTML form

@app.route('/submit', methods=['POST'])
def submit_form():
    data = request.json
    print(f"Received form data: {data}")
    return jsonify({"status": "Form submitted!"})

@app.route('/review/<stage>', methods=['POST'])
def review_form(stage):
    decision = request.json['decision']
    print(f"Stage {stage} decision: {decision}")
    return jsonify({"nextStage": "next_stage"} if stage != 'c' else {"nextStage": None})

if __name__ == '__main__':
    app.run(debug=True)
