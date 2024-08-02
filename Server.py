from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/data', methods=['GET'])
def get_data():
    with open('windspeed.txt', 'r') as f:
        windspeed_str = f.read().split(': ')[1]  # Split the string and take the second part
        windspeed = float(windspeed_str)
    with open('temperature.txt', 'r') as f:
        temperature_str = f.read().split(': ')[1]  # Split the string and take the second part
        temperature = float(temperature_str)
    return jsonify({'windspeed': windspeed, 'temperature': temperature})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)