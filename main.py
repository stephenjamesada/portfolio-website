from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/hardware.html')
def hardware():
    return render_template('hardware.html')

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)