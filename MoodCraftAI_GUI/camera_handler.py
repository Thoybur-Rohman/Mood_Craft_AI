import cv2
from keras.models import load_model
from keras.preprocessing.image import img_to_array
import tkinter as tk
import numpy as np
from PIL import Image, ImageTk

class CameraHandler:
    def __init__(self, app):
          self.app = app
          self.emotion_frames_threshold = 5

    def open_camera(self):
        emotion_frames_count = 0
        cap = cv2.VideoCapture(0)
        eye_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        emotion_classifier = load_model('model.h5')
        emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']

        if not cap.isOpened():
            return

        while True:
            ret, frame = cap.read()

            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            eyes = eye_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))

            if len(eyes) > 0:
                gray_face = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = eye_cascade.detectMultiScale(gray_face)

                for (x, y, w, h) in faces:
                    roi_gray = gray_face[y:y + h, x:x + w]
                    roi_gray = cv2.resize(roi_gray, (48, 48), interpolation=cv2.INTER_AREA)

                    if np.sum([roi_gray]) != 0:
                        roi = roi_gray.astype('float') / 255.0
                        roi = img_to_array(roi)
                        roi = np.expand_dims(roi, axis=0)

                        prediction = emotion_classifier.predict(roi)[0]
                        label = emotion_labels[prediction.argmax()]
                        label_position = (x, y)
                        cv2.putText(frame, label, label_position, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                        self.detected_emotion = label
                        emotion_frames_count += 1
                        if emotion_frames_count >= self.emotion_frames_threshold:
                            cap.release()
                            cv2.destroyAllWindows()
                            emotion_frames_count = 0
                            self.app.ui.updated_image = False
                            self.app.ui.startgen(self.detected_emotion)
                            break

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()