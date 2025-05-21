from tkinter import filedialog
import face_recognition
import cv2
import os

# Use OpenCV's internal Haar cascade path
face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

directory_path = 'database/'  # Folder containing known faces
faces_dict = {}
count = 0

# Load known faces
for filename in os.listdir(directory_path):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
        person_name = os.path.splitext(filename)[0]
        file_path = os.path.join(directory_path, filename)
        faces_dict[person_name] = file_path

# Ask user to select an image
file_path = filedialog.askopenfilename()
while not file_path:
    file_path = filedialog.askopenfilename()

# Load selected image
live = cv2.imread(file_path)
gray = cv2.cvtColor(live, cv2.COLOR_BGR2GRAY)
faces = face_classifier.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

# Text styling
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 1
font_color = (255, 255, 255)
thickness = 2

# Process each known face
for (name, known_image_path) in faces_dict.items():
    known_image = face_recognition.load_image_file(known_image_path)
    try:
        known_encoding = face_recognition.face_encodings(known_image)[0]
    except IndexError:
        print(f'Face not detected in the image: {known_image_path}')
        continue

    if len(faces) == 0:
        print("No faces found in the live image.")
        break

    # Compare detected faces
    for (x, y, w, h) in faces:
        face = live[y:y+h, x:x+w]
        cv2.imwrite('temp_face.jpg', face)
        face_to_check = face_recognition.load_image_file('temp_face.jpg')
        try:
            unknown_encoding = face_recognition.face_encodings(face_to_check)[0]
            if os.path.exists('temp_face.jpg'):
                os.remove('temp_face.jpg')
        except IndexError:
            print('Face not detected in the selected region.')
            continue

        try:
            match = face_recognition.compare_faces([known_encoding], unknown_encoding)[0]
            if match:
                count += 1
                cv2.rectangle(live, (x, y), (x + w, y + h), (127, 0, 255), 2)

                # Draw label with background
                text_size = cv2.getTextSize(name, font, font_scale, thickness)[0]
                bg_x = x
                bg_y = y - text_size[1] - 10
                cv2.rectangle(live, (bg_x, bg_y), (bg_x + text_size[0], bg_y + text_size[1] + 5), (0, 0, 0), -1)
                cv2.putText(live, name, (x, y - 10), font, font_scale, font_color, thickness)
        except Exception as e:
            print(f'Error comparing faces: {e}')

# Summary
if count == 0:
    print("No face was recognized.")
elif count == 1:
    print("1 face was recognized.")
else:
    print(f'{count} faces were recognized.')

# Save and display the result
cv2.imwrite("result.jpg", live)
print("Result saved as result.jpg")
