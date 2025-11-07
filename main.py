from flask import Flask, render_template, request, abort, url_for, redirect, flash
from config import SECRET_KEY
from flask_talisman import Talisman
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = SECRET_KEY

csp = {
'default-src': ["'self'"],
'script-src': ["'self'", "'unsafe-inline'"],
'style-src': ["'self'", "'unsafe-inline'"],
'font-src': ["'self'"],
'img-src': ["'self'", "data:"],
}

Talisman(
    app,
    content_security_policy=csp,
    force_https=False,  # Let Render handle HTTPS
    strict_transport_security=False  # Disable HSTS; Render sets this
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
    app.run(port=5000, debug=False)