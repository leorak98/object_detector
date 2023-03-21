import cv2

import numpy as np
from flask import Flask, render_template, Response, request
from imutils.video import VideoStream
import imutils

app = Flask(__name__)

def get_output_layers(net):
    
    layer_names = net.getLayerNames()
    try:
        output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
    except:
        output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    print(output_layers)
    return output_layers

def draw_prediction(img, class_id, confidence, x, y, x_plus_w, y_plus_h):

    label = str(classes[class_id])

    color = COLORS[class_id]

    cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), color, 2)

    cv2.putText(img, label, (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

def gen_frames():
    while True:
        success, frame = camera.read()
        (Height,Width) = frame.shape[:2]
        scale = 0.00392
        frame = imutils.resize(frame,width=400)
        net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")

        if not success:
            break
        else:
            blob = cv2.dnn.blobFromImage(frame, scale, (416,416), (0,0,0), True, crop=False) 
            net.setInput(blob)
            outs = net.forward(get_output_layers(net))

            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    if confidence > 0.5:
                        center_x = int(detection[0] * Width)
                        center_y = int(detection[1] * Height)
                        w = int(detection[2] * Width)
                        h = int(detection[3] * Height)
                        x = center_x - w / 2
                        y = center_y - h / 2
                        class_ids.append(class_id)
                        confidences.append(float(confidence))
                        boxes.append([x, y, w, h])

            indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)
            
            for i in indices:
                try:
                    box = boxes[i]
                except:
                    i = i[0]
                    box = boxes[i]
                
                x = box[0]
                y = box[1]
                w = box[2]
                h = box[3]
                draw_prediction(frame, class_ids[i], confidences[i], round(x), round(y), round(x+w), round(y+h))

            cv2.putText(frame, "Leonardo", (5, 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255,255,0), 2)
            ret,buffer = cv2.imencode('.jpg',frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

camera = cv2.VideoCapture(0)  # webcam PC 0
classes = None
class_ids = []
confidences = []
boxes = []
conf_threshold = 0.5
nms_threshold = 0.4

with open("yolov3.txt", 'r') as f:
    classes = [line.strip() for line in f.readlines()]

COLORS = np.random.uniform(0, 255, size=(len(classes), 3))

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


if __name__ == '__main__':
    # app.run(host='192.168.43.208',debug=True)
    app.run(debug=True)
    # app.run()