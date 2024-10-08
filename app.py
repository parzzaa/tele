from flask import Flask, request, jsonify, render_template, redirect, url_for
import requests
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Replace these with your bot token and chat IDs
BOT_TOKEN = '7293431359:AAH3QLzmiod9Lf1SQ0bkqgHzk1rMxVLqqOQ'  # Fetch from environment
CHAT_ID_A = '101883112'
CHAT_ID_B = '109566532'
CHAT_ID_C = '85607859'

# In-memory storage for form submissions and reviews
forms = {}

# Helper function to send Telegram messages
def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'  # Allows clickable links in Telegram messages
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raises an error for bad responses
    except requests.exceptions.RequestException as e:
        print(f"مشکلی در ارسال پیام به این آیدی به وجود آمده است {chat_id}: {e}")
        return {"خطا": "عدم ارسال پیام"}
    return response.json()

# Dashboard for all reviewers to see the history of forms
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', forms=forms)

# Route to handle form submission (submitted by 'd')
@app.route('/submit', methods=['POST'])
def submit_form():
    form_data = request.json  # Extract submitted form data

    form_id = len(forms) + 1  # Simple form ID generation

    # Store the form with the form data and initial review stage
    forms[form_id] = {
        'data': form_data,
        'stage': 'a',  # Starts with reviewer 'a'
        'review_comments': [],
        'status': 'Pending'
    }

    # Send review link to reviewer 'a'
    review_link = f"https://tele-f3f3.onrender.com/review_form/{form_id}"  # Update with your app's URL
    send_telegram_message(CHAT_ID_A, f"درخواست پرداخت جدیدی به ثبت رسیده است.\n\n[مشاهده درخواست]({review_link})")

    return jsonify({"پیام": "فرم ثبت شد وبرای خانوم عبدی جهت بازبینی ارسال شده است", "مرحله بعد": "مرضیه عبدی"})

# Route to render the review form for reviewers
@app.route('/review_form/<int:form_id>', methods=['GET'])
def review_form(form_id):
    if form_id not in forms:
        return "درخواست پرداخت یافت نشد", 404

    form = forms[form_id]
    return render_template('review.html', form=form, form_id=form_id)

# Route to handle review decision (accept/reject + comment)
@app.route('/submit_review/<int:form_id>', methods=['POST'])
def submit_review(form_id):
    if form_id not in forms:
        return "درخواست پرداخت یافت نشد", 404

    form = forms[form_id]
    decision = request.form['decision']  # Either 'accept' or 'reject'
    comment = request.form.get('comment', '')  # Optional comment

    # Save the comment and decision
    form['review_comments'].append({
        'stage': form['stage'],
        'decision': decision,
        'comment': comment
    })

    # Move to the next stage or complete the process
    if form['stage'] == 'a' and decision == 'accept':
        form['stage'] = 'b'
        review_link = f"https://tele-f3f3.onrender.com/review_form/{form_id}"  # Update with your app's URL
        send_telegram_message(CHAT_ID_B, f"دستور پرداخت توسط خانوم مرضیه عبدی تایید شد. [مشاهده درخواست]({review_link})")
    elif form['stage'] == 'b' and decision == 'accept':
        form['stage'] = 'c'
        review_link = f"https://tele-f3f3.onrender.com/review_form/{form_id}"  # Update with your app's URL
        send_telegram_message(CHAT_ID_C, f"دستور پرداخت توسط امین صالحی تایید شد. [مشاهده درخواست]({review_link})")
    elif form['stage'] == 'c' and decision == 'accept':
        form['status'] = 'Approved'
        form['stage'] = 'completed'
        send_telegram_message(CHAT_ID_A, "درخواست از جانب تمامی افراد تایید شده است")
        send_telegram_message(CHAT_ID_B, "درخواست از جانب تمامی افراد تایید شده است")
    elif decision == 'reject':
        form['status'] = 'Rejected'
        form['stage'] = 'completed'
        return jsonify({"message": f"درخواست از جانب ایشان رد شده است {form['stage']}"})

    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
