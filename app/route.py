# route.py
from flask import Flask, jsonify, render_template, request
from scrape import get_availability

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/availability')
def availability():
    month = request.args.get('month', 'next')  # 'next' by default
    month_offset = 1 if month == 'next' else 0
    available_dates = get_availability(month_offset)
    return jsonify({"dates": available_dates})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
