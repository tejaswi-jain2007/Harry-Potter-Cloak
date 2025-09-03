from flask import Flask, render_template, Response, request, jsonify
import cv2
import numpy as np

app = Flask(__name__)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

background = None
bg_captured = False
sensitivity = 15
cloak_color = "red"

def capture_background():
    global background, bg_captured
    for i in range(60):
        ret, frame = cap.read()
        if ret:
            background = frame
    if background is not None:
        background = np.flip(background, axis=1)
        bg_captured = True

@app.route('/capture_background', methods=['POST'])
def capture_bg_api():
    capture_background()
    return jsonify({'status': 'success'})

@app.route('/set_sensitivity', methods=['POST'])
def set_sensitivity():
    global sensitivity
    data = request.json
    sens = data.get('sensitivity', 15)
    if 5 <= sens <= 40:
        sensitivity = sens
        return jsonify({"status": "success", "sensitivity": sensitivity})
    else:
        return jsonify({"status": "error", "message": "Sensitivity out of range (5-40)"}), 400

@app.route('/set_cloak_color', methods=['POST'])
def set_cloak_color():
    global cloak_color
    data = request.json
    color = data.get('color', "green")
    if color in ["red", "green", "blue"]:
        cloak_color = color
        return jsonify({"status": "success", "color": cloak_color})
    else:
        return jsonify({"status": "error", "message": "Color must be red, green, or blue."}), 400

def get_hsv_range(color, sensitivity):
    if color == "green":
        lower = np.array([60 - sensitivity, 70, 70])
        upper = np.array([60 + sensitivity, 255, 255])
        return lower, upper
    elif color == "blue":
        lower = np.array([100 - sensitivity, 150, 0])
        upper = np.array([140 + sensitivity, 255, 255])
        return lower, upper
    else: # red
        lower1 = np.array([0, 120, 70])
        upper1 = np.array([sensitivity, 255, 255])
        lower2 = np.array([180 - sensitivity, 120, 70])
        upper2 = np.array([180, 255, 255])
        return (lower1, upper1), (lower2, upper2)

def generate_frames():
    global background, sensitivity, cloak_color, bg_captured

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = np.flip(frame, axis=1)

        if not bg_captured or background is None:
            display_frame = frame
        else:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            if cloak_color == "green" or cloak_color == "blue":
                lower, upper = get_hsv_range(cloak_color, sensitivity)
                mask = cv2.inRange(hsv, lower, upper)
            else:
                (lower1, upper1), (lower2, upper2) = get_hsv_range("red", sensitivity)
                mask1 = cv2.inRange(hsv, lower1, upper1)
                mask2 = cv2.inRange(hsv, lower2, upper2)
                mask = mask1 + mask2

            kernel = np.ones((5,5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
            mask = cv2.dilate(mask, kernel, iterations=2)
            mask = cv2.GaussianBlur(mask, (7, 7), 0)
            mask_inv = cv2.bitwise_not(mask)

            res1 = cv2.bitwise_and(background, background, mask=mask)
            res2 = cv2.bitwise_and(frame, frame, mask=mask_inv)
            display_frame = cv2.addWeighted(res1, 1, res2, 1, 0)

        ret, buffer = cv2.imencode('.jpg', display_frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)
