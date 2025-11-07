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
app.config['MAIL_USE_SSL'] = os.getenv("MAIL_USE_SSL", "false").lower() == "true"
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
    
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)