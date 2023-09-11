from flask import Flask, render_template, Response,request, jsonify
from flask_socketio import SocketIO

import time

app = Flask(__name__, template_folder='frontend/pages', static_folder='frontend/static')
socketio = SocketIO(app)


# Function to stream log data
def stream_log_data():
    with open('broadcast.log', 'r') as log_file:
        while True:
            line = log_file.readline()
            if not line:
                time.sleep(0.01)
                continue
            yield f"data: {line}\n\n"
            
@app.route('/login')
def login():    
     return render_template('login.html')
 
@app.route('/signup')
def signup():    
     return render_template('signup.html')
  
@app.route('/stream_log')
def sse_log():
    return Response(stream_log_data(), content_type='text/event-stream')


@app.route('/save_data', methods=['POST'])
def save_data():
    try:
        data = request.json  # Assuming JSON data is sent from the client
        with open('data.txt', 'a') as file:
            if data is not None:
                file.write(f"Username: {data['username']}, Port: {data['port']}\n")
        return jsonify({'message': 'Data saved successfully'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/')
def index():
    try:
        with open('broadcast.log', 'r') as log_file:
            log_contents = log_file.readlines()
    except FileNotFoundError:
        log_contents = []  # Handle if the log file is not found

    return render_template('index.html', broadcast_log=log_contents)


    


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
