# Author Names: Joshua Anderson, Becca Casad, Charlie Cathcart, Ahn Nguyen
# Description: Creates a video feed that interprets ASL into text on screen.
#
# Credits:  Bimal-Tech (https://github.com/bimal-tech/AmericanSignLanguage) - Code used for main part of project
#           MediaPipe Facial Detection - https://google.github.io/mediapipe/solutions/face_detection.html

import csv
import copy
import cv2 as cv
import mediapipe as mp
from model import KeyPointClassifier
from app_files import calc_landmark_list, draw_info_text, draw_landmarks, get_args, pre_process_landmark

# Main - Creates camera output with hand and face detection. (Will be split later)
def main():
    args = get_args()

    cap_device = args.device
    cap_width = args.width
    cap_height = args.height

    use_static_image_mode = args.use_static_image_mode
    min_detection_confidence = args.min_detection_confidence
    min_tracking_confidence = args.min_tracking_confidence

    # Imports Capture Device (Camera)
    cap = cv.VideoCapture(cap_device)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, cap_width)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, cap_height)

    # Imports Hand Detection
    mp_drawing = mp.solutions.drawing_utils
    mp_face = mp.solutions.face_detection
    face = mp_face.FaceDetection(
        model_selection=0,
        min_detection_confidence=min_detection_confidence
    )

    # Imports Hand Detection
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=use_static_image_mode,
        max_num_hands=1,
        min_detection_confidence=min_detection_confidence,
        min_tracking_confidence=min_tracking_confidence,
    )

    keypoint_classifier = KeyPointClassifier()

    # Opens Keypoint Classifier Labels
    with open('model/keypoint_classifier/keypoint_classifier_label.csv', encoding='utf-8-sig') as f:
        keypoint_classifier_labels = csv.reader(f)
        keypoint_classifier_labels = [
            row[0] for row in keypoint_classifier_labels
        ]

    while True:
        key = cv.waitKey(10)
        if key == 27:  # ESC
            break

        ret, image = cap.read()
        if not ret:
            break
        image = cv.flip(image, 1) 
        debug_image = copy.deepcopy(image)
        # print(debug_image.shape)
        # cv.imshow("debug_image",debug_image)
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

        # Processes image to detect face and hands.
        image.flags.writeable = False
        results_hands = hands.process(image)
        results_face = face.process(image)
        image.flags.writeable = True

        # Determines if face needs to be drawn.
        if results_face.detections:
            for detection in results_face.detections:
                mp_drawing.draw_detection(debug_image, detection)

        # Determines if hand needs to be drawn.
        if results_hands.multi_hand_landmarks is not None:
            for hand_landmarks, handedness in zip(results_hands.multi_hand_landmarks, results_hands.multi_handedness):
                landmark_list = calc_landmark_list(debug_image, hand_landmarks)
                pre_processed_landmark_list = pre_process_landmark(landmark_list)

                hand_sign_id = keypoint_classifier(pre_processed_landmark_list)

                debug_image = draw_landmarks(debug_image, landmark_list)

                debug_image = draw_info_text(
                    debug_image,
                    handedness,
                    keypoint_classifier_labels[hand_sign_id])

        cv.imshow('Hand Gesture Recognition', debug_image)

    cap.release()
    cv.destroyAllWindows()

# Calling Main
if __name__ == '__main__':
    main()
