import cv2
import os
from keras.models import load_model
import numpy as np
from pygame import mixer
import time
from drowsinessDetector import drowsinessDetector

mixer.init()
sound = mixer.Sound('alarm.wav')
voice = mixer.Channel(5)





lbl=['Close','Open']

# model = load_model('models/cnncat2.h5')
path = os.getcwd()
cap = cv2.VideoCapture(0)
font = cv2.FONT_HERSHEY_COMPLEX_SMALL
count=0
score=0
thicc=2
rpred=[99]
lpred=[99]
def reset_score():
    global count,score,thicc,rpred,lpred
    count=0
    score=0
    thicc=2
    rpred=[99]
    lpred=[99]
def drowsy_prediction(frame):
    global count,score,thicc,rpred,lpred
    height,width = frame.shape[:2] 

    # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    res = drowsinessDetector(frame)
    if(res):
        frame = res[0]
        prediction = res[1]
        if(prediction!=None):
            if((prediction>0.5) and score<35):
                score=score+1
                cv2.putText(frame,"Closed",(10,height-20), font, 1,(255,255,255),1,cv2.LINE_AA)
            # if(rpred[0]==1 or lpred[0]==1):
            else:
                score=score-1
                cv2.putText(frame,"Open",(10,height-20), font, 1,(255,255,255),1,cv2.LINE_AA)
    
        
    if(score<0):
        score=0   
        voice.stop()
    cv2.putText(frame,'Score:'+str(score),(100,height-20), font, 1,(255,255,255),1,cv2.LINE_AA)
    if(score>8 and not voice.get_busy()):
        #person is feeling sleepy so we beep the alarm
        cv2.imwrite(os.path.join(path,'image.jpg'),frame)
        try:
            voice.play(sound)
            
        except:  # isplaying = False
            pass
        if(thicc<16):
            thicc= thicc+2
        else:
            thicc=thicc-2
            if(thicc<2):
                thicc=2
        cv2.rectangle(frame,(0,0),(width,height),(0,0,255),thicc) 
    return frame,score
