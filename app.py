from flask import Flask, render_template, Response, jsonify
import driver_sleep_drowsiness_detection as detection

app = Flask(__name__)

camera_running = False

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/start")
def start():
    global camera_running
    camera_running = True
    return "Camera Started"

@app.route("/stop")
def stop():
    global camera_running
    camera_running = False
    return "Camera Stopped"

@app.route("/video_feed")
def video_feed():
    def stream():
        global camera_running
        for frame in detection.generate_frames():
            if not camera_running:
                break
            yield frame

    return Response(stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/status")
def status():
    return jsonify({
        "ear": detection.current_ear,
        "drowsy": detection.drowsy_state
    })

if __name__ == "__main__":
    app.run(debug=True)

