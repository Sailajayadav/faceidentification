import face_recognition
import cv2
import os
# Set the working directory to the script's location
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Load Haar cascade for face detection
face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

directory_path = 'database/'  # Folder containing known faces
known_encodings = []
known_names = []

# Check if known faces folder exists
if not os.path.exists(directory_path):
    print(f"Error: The folder '{directory_path}' does not exist.")
    exit(1)

# Load known faces
for filename in os.listdir(directory_path):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
        person_name = os.path.splitext(filename)[0]
        file_path = os.path.join(directory_path, filename)
        try:
            image = face_recognition.load_image_file(file_path)
            encoding = face_recognition.face_encodings(image)[0]
            known_encodings.append(encoding)
            known_names.append(person_name)
            print(f"Loaded face encoding for: {person_name}")
        except IndexError:
            print(f'Face not detected in the image: {file_path}')

# Webcam live recognition
print("Starting live webcam recognition... Press 'q' to quit.")
cap = cv2.VideoCapture(0)

font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 0.7
font_color = (255, 255, 255)
thickness = 2

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to access webcam.")
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_encodings, face_encoding)
        name = "Unknown"

        for i in range(len(matches)):
            if matches[i]:
                name = known_names[i]
                break

        # Draw box and label
        cv2.rectangle(frame, (left, top), (right, bottom), (127, 0, 255), 2)
        cv2.rectangle(frame, (left, top - 25), (right, top), (0, 0, 0), -1)
        cv2.putText(frame, name, (left + 6, top - 6), font, font_scale, font_color, thickness)

    cv2.imshow("Webcam - Face Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
