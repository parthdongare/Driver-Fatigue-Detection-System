# For realtime testing of yawn detection model

import cv2
import mediapipe as mp
import numpy as np
#Face Mesh
 
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten, Dropout


# Define the model architecture
model = Sequential([
    Flatten(input_shape=(478,3)),
    Dense(64, activation='relu',),
    Dense(16, activation='relu'),
    Dense(1, activation='sigmoid')
])
model.load_weights("DrowsinessDetector.h5")
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh( max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6)
# cap = cv2.VideoCapture(0)
buffer = [0]*30
def drowsinessDetector(frame):
    # _,frame = cap.read()
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = face_mesh.process(img)
    if(result.multi_face_landmarks!=None):
        # Convert mesh to numpy array and save
        mesh = np.array([[p.x, p.y, p.z] for face in result.multi_face_landmarks for p in face.landmark])
        mean = np.mean(mesh, axis=0)
        std = np.std(mesh, axis=0)
        mesh_normalized = (mesh - mean) / std
        p = model.predict(np.array([mesh_normalized]),verbose=0)
        # print(p)
        buffer.append(p[0][0])
        buffer.pop(0)
        meanResult = sum(buffer)/30
        # if(meanResult>0.1):
            # print("Drowsy"+str(meanResult*100)+"%")
        cv2.rectangle(frame,(0,300),(50,300-int(p[0][0]*300)),(255-int(p[0][0]*255),0,int(p[0][0]*255)),50)
        # print(p[0][0])
        return (frame, p[0][0])
        # else:
            # print("Not Drowsy"+str(meanResult*100)+"%")
    # cv2.imshow(".",frame)

        # if(p[0][0]>p[0][1]):
        #     print("Yawning"+str(p[0][0]*100)+"%")
        # if(p[0][3]>p[0][2]):
        #     print("Closed Eyes"+str(p[0][2]*100)+"%")
    # cv2.waitKey(1)