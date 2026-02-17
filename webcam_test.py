"""
This is a simple script that takes a webcam signal using opencv and sends a capture of it to Google's Gemini chatbot to
analyze it.

-- Controls --
Capture image & send it to Gemini with 'm' (edit the prompt in prompt.txt)
Quit with 'q'
"""
import cv2 as cv                # pip install opencv-python
import numpy as np              # pip install numpy
from PIL import Image           # pip install Pillow
from google import genai        # pip install google-genai
import os
from dotenv import load_dotenv  # pip install python-dotenv
# import threading


def request_gemini(file_path):

    try:
        client = genai.Client(api_key=API_KEY)
    except Exception as e:
        client = None
        print("Error: could not initialize Gemini client.")

    try:
        img = Image.open(file_path)
        print("Sending request to Gemini")
        contents = [img, PROMPT]

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents
        )

        # print(response.text)
        return response.text

    except Exception as e:
        print(e)
        return "An error occurred with Gemini"


def webcam_stuff():
    cap = cv.VideoCapture(1)

    if not cap.isOpened():
        print("error opening camera")
        exit()

    while True:
        ret, frame = cap.read()

        if not ret:
            print("end of stream")
            break

        cv.imshow("video stream", frame)  # replace frame with np.zeros([100, 100]) to hide image

        key = cv.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('m'):
            cv.imwrite("image.png", frame)
            print("IMAGE CAPTURED")
            # thread = threading.Thread(target=request_gemini, args=("image.png"))
            # thread.start()
            print(request_gemini("image.png"))

    cap.release()
    cv.destroyAllWindows()


if __name__ == "__main__":
    load_dotenv()

    # Constants
    API_KEY = os.getenv("GEMINI_AI_API_KEY")
    MODEL_NAME = "gemini-2.5-flash"

    # with open('prompt.txt', 'r') as f:
    #     # To edit the prompt, change the text contained in the prompt.txt file.
    #     PROMPT = f.read()

    PROMPT = "This image contains blocks arranged on a 2D plane. Return the coordinates of the centroid of each block and the color of each block in the format '-[x, y](color)'. Separate each with a new line. Say nothing else."

    webcam_stuff()

