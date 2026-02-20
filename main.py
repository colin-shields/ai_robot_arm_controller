"""-------------------------------------------------------------
-- Full CLI to take an image and request Gemini to write code
--   for controlling a Dobot robotic arm.
-------------------------------------------------------------"""

from google import genai        # pip install google-genai
from PIL import Image           # pip install Pillow
from dotenv import load_dotenv  # pip install python-dotenv
import cv2 as cv                # pip install opencv-python
import os
import runpy
import time


def get_image_option():
    image_option = 0
    while not image_option:
        print("Choose how to capture image:\n"
              "1.) Capture with Webcam\n"
              "2.) Choose from File")
        try:
            image_option = int(input("Choose an option (1 or 2): "))
            if image_option != 1 and image_option != 2:
                image_option = 0
                raise ValueError
        except ValueError:
            print("\nInvalid Option.\n")

    return image_option


def capture_from_webcam(image_path):
    image_captured = False

    cap = cv.VideoCapture(0)    # Change this if you have multiple webcams

    if not cap.isOpened():
        print("Error opening camera.")
        raise FileNotFoundError

    while True:
        ret, frame = cap.read()

        if not ret:
            print("End of video stream.")
            break

        cv.imshow("Webcam Stream (q = quit, m = capture)", frame)

        key = cv.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('m'):
            cv.imwrite(image_path, frame)
            image_captured = True
            break

    cap.release()
    cv.destroyAllWindows()

    if not image_captured:
        raise FileNotFoundError


def request_gemini(image, prompt):

    client = genai.Client(api_key=API_KEY)

    contents = [image, prompt, DEMO_CODE, LECTURE_PPT]
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=contents
    )

    return response


def main():
    print("=== DOBOT-Gemini program CLI ===\n")

    # Create necessary directories.
    if not os.path.exists("responses"):
        os.makedirs("responses")

    # Get image.
    image_path = DEFAULT_IMAGE_PATH
    image = None

    image_option = get_image_option()
    match image_option:
        case 1:
            # Capture from webcam.
            try:
                capture_from_webcam(image_path)
                image = Image.open(image_path)
            except FileNotFoundError:
                print("Could not capture image from webcam.")
                exit()

        case 2:
            # Load from file.
            while image is None:
                image_path = input("\nEnter filepath for image: ")
                try:
                    image = Image.open(image_path)
                except FileNotFoundError:
                    print("Could not load image from that path.\n")
    image.save(SAVE_PICTURE_PATH)

    # Get prompt.
    user_prompt = input("\nEnter a prompt: ")
    full_prompt = BASE_PROMPT + user_prompt

    # Request the API.
    print("\nSending prompt to Gemini.\nPlease wait...")
    try:
        response = request_gemini(image, full_prompt)
    except Exception as e:
        print(f"\nAn error occurred with Gemini: {e}")
        exit()
    print(f"\nResponse successfully generated!")

    with open(MOST_RECENT_RESPONSE_PATH, 'w') as r:
        # Store the attempt to a file
        r.write(f"TIME: {time.time()}")
        r.write(f"\nMODEL: {MODEL_NAME}")
        r.write(f"\nIMAGE PATH: {image_path}")
        r.write(f"\n\nPROMPT:\n{full_prompt}")
        r.write(f"\n\nRESPONSE:\n{response.text}")

    # print(f"\nRESPONSE:\n{response.text}\n\nEND OF RESPONSE")     # print the returned response

    # Save Generated Code to File.
    with open(GEMINI_CODE_PATH, 'w') as r:
        lines = response.text.splitlines()
        r.write('\n'.join(lines[1:-1]))     # remove the ``` code-block formatting

    # Execute Generated Code.
    choice = input("\n\nExecute the generated code? (y/n): ")
    if choice == 'y':
        runpy.run_path(GEMINI_CODE_PATH)


if __name__ == "__main__":
    TIMESTAMP = int(time.time())
    print(f"Trial: {TIMESTAMP}")
    load_dotenv()

    API_KEY = os.getenv("GEMINI_AI_API_KEY")
    MODEL_NAME = "gemini-2.5-flash"
    # MODEL_NAME = "gemini-3-flash-preview"

    with open("prompt.txt", 'r') as p:
        BASE_PROMPT = p.read()

    with open("python demo.txt", 'r', errors='ignore') as d:
        DEMO_CODE = d.read()

    with open("lecture ppt.txt", 'r', errors='ignore') as l:
        LECTURE_PPT = l.read()

    DEFAULT_IMAGE_PATH = "image.png"
    MOST_RECENT_RESPONSE_PATH = f"responses/response_{TIMESTAMP}.txt"
    GEMINI_CODE_PATH = "code_by_gemini.py"
    SAVE_PICTURE_PATH = f"responses/picture_{TIMESTAMP}.png"

    main()
