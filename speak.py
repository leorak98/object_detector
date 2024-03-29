import pyttsx3
from threading import Thread
from dotenv import dotenv_values,load_dotenv
import time

local = 'fr'
if(load_dotenv()):
    env = dotenv_values('.env')
    local = env['LOCAL']

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
if(local=='fr'):
    voice=0
elif(local=='en'):
    voice=1
voix=engine.getProperty('voices')
engine.setProperty('voice',voix[voice].id)

# Fonction parler
def parler(text):
    engine.say(text)
    engine.runAndWait()
    engine.stop()
print('initialisation ...')
time.sleep(2)
print('initialisation terminée ...')
while True:
    fichier=open("static/data/objets.txt","r")
    detection=fichier.read()
    if (detection!=''):
        if(detection=='rien'):
            parler('je ne detecte aucune objets')
        else:
            parler('je vois environ {}'.format(detection))
        fichier=open("static/data/objets.txt","w")
        fichier.write('')
        fichier.close