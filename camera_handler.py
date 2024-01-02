import cv2
from keras.models import load_model
from keras.preprocessing.image import img_to_array
from CTkMessagebox import CTkMessagebox
import tkinter as tk
import numpy as np
import requests
from PIL import Image, ImageTk
import io

class CameraHandler:
    def __init__(self, app):
        self.app = app
        self.camera_enabled = False
        self.camera = None
        self.cap = None
        self.is_window_open = False
        self.face_detected = False
        self.detected_emotion = None
        self.emotion_frames_threshold = 30
        self.emotion_window = None
        self.emotion_frames_count = 0

    def toggle_camera(self):
        self.camera_enabled = not self.camera_enabled
        if self.camera_enabled:
            self.camera = cv2.VideoCapture(0)
            self.cap = self.camera
            self.open_camera_for_eyes()
        else:
            if self.camera is not None:
                self.camera.release()

    def open_camera(self):
        self.emotion_window = tk.Toplevel(self.app.root)
        self.emotion_window.title("Emotion Detection")

        def close_emotion_window():
            self.emotion_window.destroy()

        close_button = tk.Button(self.emotion_window, text="Close Emotion Detection", command=close_emotion_window)
        close_button.pack(padx=10, pady=10)
        
        face_classifier = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        if face_classifier.empty():
            CTkMessagebox(title="Error", message="Unable to load the face cascade classifier.", icon="cancel")
            return

        emotion_classifier = load_model('model.h5')
        emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']

        cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read()
            labels = []
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_classifier.detectMultiScale(gray)

            if len(faces) > 0:
                faces = sorted(faces, key=lambda x: x[2] * x[3], reverse=True)
                (x, y, w, h) = faces[0]

                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
                roi_gray = gray[y:y + h, x:x + w]
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
                    self.emotion_frames_count += 1

                    if self.emotion_frames_count >= self.emotion_frames_threshold:
                        cap.release()
                        cv2.destroyAllWindows()
                        self.emotion_frames_count = 0
                        print(self.detected_emotion)
                        self.app.ui.generate_image_from_emotion(self.detected_emotion)
                        break

                    self.face_detected = True
                else:
                    cv2.putText(frame, 'No Faces', (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    self.emotion_frames_count = 0

            cv2.imshow('Emotion Detector', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def open_camera_for_eyes(self):
        self.cap = cv2.VideoCapture(0)

        eye_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        if eye_cascade.empty():
            print("Error: Unable to load the eye cascade classifier.")
            return

        emotion_classifier = load_model('model.h5')
        emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']

        while self.camera_enabled:
            ret, frame = self.cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            eyes = eye_cascade.detectMultiScale(
                gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))

            if len(eyes) > 0:
                if not self.is_window_open:
                    cv2.namedWindow("Eyes Detected", cv2.WINDOW_NORMAL)
                    self.is_window_open = True
                cv2.imshow("Eyes Detected", frame)

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
                        self.emotion_frames_count += 1

                        if self.emotion_frames_count >= self.emotion_frames_threshold:
                            self.cap.release()
                            cv2.destroyAllWindows()
                            self.emotion_frames_count = 0
                            print(self.detected_emotion)
                            self.app.ui.updated_image = False
                            self.app.ui.generate_display_image_Deep_AI(self.detected_emotion)
                            break

                        self.face_detected = True
                    else:
                        cv2.putText(frame, 'No Faces', (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        self.emotion_frames_count = 0
            elif self.is_window_open:
                cv2.destroyWindow("Eyes Detected")
                self.is_window_open = False

            key = cv2.waitKey(1)
            if key == 27:
                break

        self.cap.release()
        cv2.destroyAllWindows()

    def display_image(self, category):
        try:
        # Make a request to the Unsplash API to get a random image
            url = f"https://api.unsplash.com/photos/random?query={category}&orientation=landscape&client_id=1n7sSMtCh8Hs_MrBOjhQ1SygTDA-BJ550UdX3rwLYZQ"
            data = requests.get(url).json()
            img_data = requests.get(data["urls"]["regular"]).content

            # Get the canvas size
            canvas_width = self.app.ui.canvas.winfo_width()
            canvas_height = self.app.ui.canvas.winfo_height()

            # Resize the image to match the canvas size
            photo = ImageTk.PhotoImage(Image.open(io.BytesIO(img_data)).resize((canvas_width, canvas_height), resample=Image.LANCZOS))
            self.app.ui.canvas.image = photo
            self.app.ui.canvas.create_image(0, 0, anchor="nw", image=self.app.ui.canvas.image)

        except Exception as e:
            # Handle the error and display an error message in a pop-up
            error_message = f"An error occurred: {str(e)}"
            CTkMessagebox(title="Error", message=error_message, icon="cancel")


    def generate_image_from_emotion(self, emotion):
        # ... (code for image generation)
        pass

