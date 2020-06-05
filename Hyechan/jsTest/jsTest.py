from flask import Flask, request, render_template, url_for

app = Flask(__name__)

@app.route('/')
def test_page():
    return render_template('js-test-page.html', idNum = 0)
