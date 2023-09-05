from flask import Flask, render_template,Response
import time

app = Flask(__name__,template_folder='frontend/pages',static_folder='frontend/static')

def stream_log_data():
    
        with open('broadcast.log', 'r') as log_file:
            while True:
                message = log_file.readline()
                if message != "":
                    yield f"data: {message}\n\n"
                    
                time.sleep(0.01)


@app.route('/stream_log')
def sse_log():
    return Response(stream_log_data(), content_type='text/event-stream')    

@app.route('/')
def index():
    # Read the contents of the broadcast_log file
    with open('broadcast.log', 'r') as log_file:
        log_contents = log_file.read()

    # Pass the log contents as a context variable to the template
    return render_template('index.html', broadcast_log=log_contents)

    

if __name__ == "__main__":
    app.run(debug=True)
    
