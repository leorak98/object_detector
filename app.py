# -*- coding: utf-8 -*-
import cv2

import numpy as np
from flask import Flask, render_template, Response, request
from imutils.video import VideoStream
import imutils
import pyttsx3
from threading import Thread
import logging
import time
from dotenv import dotenv_values,load_dotenv
import json

#coding: utf-8
class Objet:
    def __init__(self,nom,confidence):
        self.nom = nom
        self.confidence = confidence

    def __toString__(self):
        return '{nom:{},confidence:{}}'.format(self.nom,self.confidence)

# logging.basicConfig(level=logging.DEBUG,
# format = '[%(levelname)s](%(threadName)s)%(message)s',)

# Initialisation Flask
app = Flask(__name__)

# configuration pyttsx3
engine=pyttsx3.init()
# VOLUME
volume=engine.getProperty('volume')
# print(volume)
engine.setProperty('volume',1.0)
# VITESSE
vitesse=engine.getProperty('rate')
# print(vitesse)
engine.setProperty('rate',180)
# VOIX
voix=engine.getProperty('voices')
engine.setProperty('voice',voix[0].id)
# --------fin Configuration pyttsx3------------

# Initialisation camera
camera = cv2.VideoCapture(1)  # webcam PC => 0,webcam externe => 1

# Recuperations des classes
classes = None

classes_file = "yolov3_fr.txt"
# classes_file = "yolov3.txt"

with open(classes_file, 'r') as f:
    classes = [line.strip() for line in f.readlines()]

COLORS = np.random.uniform(0, 255, size=(len(classes), 3))

def serialize_float32(obj):
    if isinstance(obj,np.float32):
        return float(obj)
    return obj

def write(label,frame):
    fichier=open("static/data/objets.txt","w")
    fichier.write('rien'if label=='' else label)
    fichier.close
    cv2.imwrite("static/img/result.jpg", frame)

def bg_task():
    while True:
        fichier=open("static/data/objets.txt","r")
        detection=fichier.read()
        if (detection!=''):
            if(detection=='rien'):
                parler('je ne detecte aucun objets')
            else:
                parler('je vois {}'.format(detection))
            fichier=open("static/data/objets.txt","w")
            fichier.write('')
            fichier.close

# Fonction parler
def parler(text):
    logging.debug('Starting')
    engine.say(text)
    engine.runAndWait()
    # time.sleep(2)
    engine.stop()


def get_output_layers(net):
    
    layer_names = net.getLayerNames()
    try:
        output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
    except:
        output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    # print(output_layers)
    return output_layers

def draw_prediction(img, class_id, confidence, x, y, x_plus_w, y_plus_h):

    label = str(classes[class_id])

    color = COLORS[class_id]

    cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), color, 2)

    cv2.putText(img, label+'-'+str(round(confidence*100,2))+'%', (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

def gen_frames():
    while True:
        success, frame = camera.read()
        frame = imutils.resize(frame,width=416)

        if not success:
            break
        else:
            ret,buffer = cv2.imencode('.jpg',frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

def detect_object():
    success, frame = camera.read()
    (Height,Width) = frame.shape[:2]
    label = ''
    resultat = []
    class_ids = []
    confidences = []
    boxes = []
    conf_threshold = 0.5
    nms_threshold = 0.4

    scale = 0.00392
    net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
    # frame = imutils.resize(frame,width=416)
    blob = cv2.dnn.blobFromImage(frame, scale, (416,416), (0,0,0), True, crop=False) 
    net.setInput(blob)
    # outs = net.forward(get_output_layers(net))
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

                objet = Objet(classes[class_id],confidence)

                objet_existant = False
                for obj in resultat:
                    if obj['nom']==objet.nom:
                        obj['nombre'] += 1
                        obj['items'].append({'confidence':objet.confidence})
                        objet_existant = True
                        break

                if not objet_existant:
                    resultat.append({
                        'nom':objet.nom,
                        'nombre':1,
                        'items':[{'confidence':objet.confidence}]
                    })
                print(resultat)
    label = ''
    for objet in resultat:
        nombre = objet['nombre']
        nom = objet['nom']
        if(nom=='Personne'):
            if(nombre==1):
                nom='Une personne'
        label += (str(nombre)if nombre>1 else '') + nom 
        if(len(resultat)>1):
            if(len(resultat)==2):
                label+=' et '
    print(resultat)
    print(len(resultat))

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
        # draw_prediction(frame, class_ids[i], confidences[i], round(x), round(y), round(x+w), round(y+h))
        draw_thread = Thread(target=draw_prediction(frame, class_ids[i], confidences[i], round(x), round(y), round(x+w), round(y+h)),name="DRAW")
        draw_thread.start()

    write_thread = Thread(target=write(label,frame),name="WRITE")
    write_thread.start()
    
    resultat = json.dumps(resultat, default=serialize_float32)
    
    return resultat
    
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/detect')
def detect():
    return detect_object()
    # return Response(detect_object(), mimetype='multipart/x-mixed-replace; boundary=frame')
    # return 'ok'

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

if __name__ == '__main__':
    # app.run(host='192.168.43.208',debug=True)
    # bg_thread = Thread(target=bg_task)
    # bg_thread.start()
    # bg_thread.join()
    print('initialisation...')
    app.run(debug=True)
    # app.run()
