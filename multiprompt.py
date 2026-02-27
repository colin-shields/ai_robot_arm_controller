"""-------------------------------------------------------------
-- Full CLI to take an image and request Gemini to write code
--   for controlling a Dobot robotic arm.
-- This version sends multiple prompts sequentially to get
--   Gemini to more accurately assess the scene.
-------------------------------------------------------------"""

from google import genai  # pip install google-genai
from PIL import Image  # pip install Pillow
from dotenv import load_dotenv  # pip install python-dotenv
import cv2 as cv  # pip install opencv-python
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

    cap = cv.VideoCapture(1)  # Change this if you have multiple webcams

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


def request_gemini(image: Image, user_prompt):
    width, height = map(str, image.size)
    base_prompts[1] = base_prompts[1].replace('IMGX', width).replace('IMGY', height)
    base_prompts[2] = base_prompts[2].replace('IMGX', width).replace('IMGY', height)

    client = genai.Client(api_key=API_KEY)

    demo_code = client.files.upload(file="python demo.txt")
    lecture_ppt = client.files.upload(file="lecture ppt.txt")

    chat = client.chats.create(
        model=MODEL_NAME
    )

    response1, response2, response3, response4 = None, None, None, None
    try:
        print("0/4")
        response1 = chat.send_message([base_prompts[0], image])
        print("1/4")
        response2 = chat.send_message(base_prompts[1])
        print("2/4")
        response3 = chat.send_message(base_prompts[2])
        print("3/4")
        response4 = chat.send_message([base_prompts[3] + user_prompt, demo_code, lecture_ppt])
        print("4/4")
    except Exception as e:
        print(f"Error with Gemini: {e}")

    client.close()

    return response1, response2, response3, response4


def main():
    print("=== DOBOT-Gemini program CLI ===\n")

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

    # Request the API.
    print("\nSending prompts to Gemini.\nPlease wait...")
    responses = request_gemini(image, user_prompt)
    generated_without_error = True
    print(f"\nResponse finished generating.")

    # Log the responses.
    response_text = ''
    for response in responses:
        if response is not None:
            # Responses initialized to None; if no error, no responses remain None
            try:
                response_text += "\n\n\n" + response.text
            except Exception as e:
                print(f"Error writing response to log: {e}\n{response}")
        else:
            # An error has occurred & a response was not overwritten from None
            generated_without_error = False
            response_text += "\nGEMINI DID NOT GENERATE RESPONSE CORRECTLY"
    response_text += "\n" + user_prompt

    with open(MOST_RECENT_RESPONSE_PATH, 'w') as r:
        # Store the attempt to a file
        r.write(f"TIME: {time.time()}")
        r.write(f"\nMODEL: {MODEL_NAME} (multiprompt.py)")
        r.write(f"\nIMAGE PATH: {image_path}")
        r.write("\n\n=============================================================================")
        r.write(f"\n\nPROMPTS:\n{'/sep'.join(base_prompts) + user_prompt}")
        r.write(f"\n\n============================================================================")
        r.write(f"\n\nRESPONSES:\n{response_text}")

    # Save Generated Code to File.
    if generated_without_error:
        with open(GEMINI_CODE_PATH, 'w') as r:
            lines = responses[-1].text.splitlines()
            r.write('\n'.join(lines[1:-1]))  # remove the ``` code-block formatting
    else:
        print("There was an error generating the response. Please check the \n"
              "log in the responses directory. Exiting...")
        exit()

    # Execute Generated Code.
    choice = input("\n\nExecute the generated code? (y/n): ")
    if choice == 'y':
        runpy.run_path(GEMINI_CODE_PATH)


if __name__ == "__main__":
    TIMESTAMP = int(time.time())
    print(f"Trial: {TIMESTAMP}")
    load_dotenv()

    # Create necessary directories.
    if not os.path.exists("responses"):
        os.makedirs("responses")

    API_KEY = os.getenv("GEMINI_AI_API_KEY")
    MODEL_NAME = "gemini-2.5-flash"
    # MODEL_NAME = "gemini-3-flash-preview"

    with open("multiprompt.txt", 'r') as p:
        base_prompts = p.read().strip().split('/sep')

    with open("python demo.txt", 'r', errors='ignore') as d:
        DEMO_CODE = d.read()

    with open("lecture ppt.txt", 'r', errors='ignore') as l:
        LECTURE_PPT = l.read()

    DEFAULT_IMAGE_PATH = "image.png"
    MOST_RECENT_RESPONSE_PATH = f"responses/response_{TIMESTAMP}.txt"
    GEMINI_CODE_PATH = "code_by_gemini.py"
    SAVE_PICTURE_PATH = f"responses/picture_{TIMESTAMP}.png"

    main()

