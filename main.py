from flask import Flask, render_template, request, abort, url_for, redirect, flash
from email_validator import validate_email, EmailNotValidError
from config import SECRET_KEY
from flask_mail import Mail, Message
from flask_talisman import Talisman
import json
import os
import hmac
import hashlib

app = Flask(__name__)

app.config['SECRET_KEY'] = SECRET_KEY

app.config['MAIL_SERVER'] = os.getenv("MAIL_SERVER", 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv("MAIL_PORT", 587))
app.config['MAIL_USE_TLS'] = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
app.config['MAIL_USE_SSL'] = os.getenv("MAIL_USE_SSL", "false").lower() == true"
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_DEFAULT_SENDER", app.config['MAIL_USERNAME'])

GITHUB_SECRET = os.environ.get("GITHUB_WEBHOOK_SECRET", "").encode()

mail = Mail(app)

csp = {
    'default-src': ["'self'"],
    'script-src': ["'self'", "'unsafe-inline'"],
    'style-src': ["'self'"],
    'font-src': ["'self'"],
    'img-src': ["'self'", "data:"],
    'object-src': ["'none'"],
    'base-uri': ["'none'"],
    'form-action': ["'self'"],
    'frame-ancestors': ["'none'"]
}

Talisman(
    app,
    content_security_policy=csp,
    frame_options='DENY',
    x_content_type_options='nosniff',
    strict_transport_security=True,
    strict_transport_security_max_age=31536000,
    strict_transport_security_include_subdomains=True,
    referrer_policy='no-referrer',
    permissions_policy={
        "geolocation": "()",
        "camera": "()",
        "microphone": "()",
        "fullscreen": "()",
        "payment": "()"
    }
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

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

@app.errorhandler(503)
def service_unavailable(e):
    return render_template('503.html'), 503

@app.route('/subscribe', methods=['GET'])
def subscribe():
    return render_template('subscribe.html')

@app.route('/subscribe', methods=['POST'])
def subscribe_form():
    raw_email = request.form.get('email', '').strip()

    try:
        valid = validate_email(raw_email)
        email = valid.email.lower()
        filepath = 'data/subscribers.json'
    
    except EmailNotValidError:
        flash("Invalid email address.", "error")
        return redirect(url_for('subscribe'))

    try:
        with open(filepath, 'r') as f:
            subscribers = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        subscribers = []
    
    if email in subscribers:
        flash("You're already subscribed!", "info")
        return redirect(url_for('subscribe'))
    
    subscribers.append(email)
    
    msg = Message(
        subject="Thanks for subscribing!",
        recipients=[email],
        body="Thanks for subscribing to updates from Stephen Ada's portfolio!"
    )
    mail.send(msg)

    with open(filepath, 'w') as f:
        json.dump(subscribers, f, indent=2)

    flash("Thank you for subscribing!", "success")
    return redirect(url_for('subscribe'))
    
@app.route('/webhook/github', methods=['POST'])
def github_webhook():
    signature = request.headers.get('X-Hub-Signature-256')
    if signature is None:
        print("Missing signature header.")
        abort(403)
    
    try:
        sha_name, signature = signature.split('=')
    except ValueError:
        print("Malformed signature header.")
        abort(403)
    
    if sha_name != 'sha256':
        print("Unsupported hash method: {sha_name}")
        abort(403)

    mac = hmac.new(GITHUB_SECRET, msg=request.data, digestmod=hashlib.sha256)
    if not hmac.compare_digest(mac.hexdigest(), signature):
        print("Invalid signature. Webhook rejected.")
        abort(403)
    
    payload = request.json
    event = request.headers.get('X-GitHub-Event')

    if event != "push":
        return "Ignored event", 200

    if event == 'push':
        try:
            repo = payload["repository"]["full_name"]
            commits = payload["commits"]
            latest_commit = commits[-1]["message"]
            link = payload["compare"]
        except (KeyError, IndexError) as e:
            print(f"Payload missing data: {e}")
            return "Malformed payload", 400

        message = f"""New push to **{repo}**!
        
        Commit: {latest_commit}

        View it: {link}
        """

        filepath = subscribers.json
        try:
            with open(filepath, 'r') as f:
                subscribers = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Subscriber file error: {e}")
            subscribers = []
        
        for email in subscribers:
            msg = Message(
                subject=f"[GitHub] New Push to {repo}",
                sender=app.config['MAIL_USERNAME'],
                recipients=[email]
            )
            msg.body = message
            mail.send(msg)
        
        print(f"Webhook processed: {repo}, notified {len(subscribers)} subscriber(s).")

        return "Webhook received", 200
    
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)