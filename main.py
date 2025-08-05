from flask import Flask, render_template, request, abort, url_for, redirect, flash
from email_validator import validate_email, EmailNotValidError
from config import SECRET_KEY
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/hardware')
def hardware():
    return render_template('hardware.html')

@app.route('/projects')
def projects():
    return render_template('projects.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.errorhandler(400)
def bad_request(e):
    return render_template('400.html'), 400

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.route('/subscribe', methods=['GET'])
def subscribe():
    return render_template('subscribe.html')

@app.route('/subscribe', methods=['POST'])
def subscribe_form():
    raw_email = request.form.get('email', '').strip()

    try:
        valid = validate_email(raw_email)
        email = valid.email.lower()
        filepath = 'subscribers.json'
    
    except EmailNotValidError:
        flash("Invalid email address.", "error")
        return redirect(url_for('subscribe_form'))

    try:
        with open(filepath, 'r') as f:
            subscribers = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        subscribers = []
    
    if email in subscribers:
        flash("You're already subscribed!", "info")
        return redirect(url_for('subscribe_form'))
    
    subscribers.append(email)

    with open(filepath, 'w') as f:
        json.dump(subscribers, f, indent=2)

    flash("Thank you for subscribing!", "success")
    return redirect(url_for('subscribe_form'))
    
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)