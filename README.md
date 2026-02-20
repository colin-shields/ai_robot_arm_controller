## Usage
Clone repository:
```commandline
git clone https://github.com/colin-shields/ai_robot_arm_controller.git
```

Initialize venv and install required packages:
```commandline
pip install -r requirements.txt
```
The API for connecting the the DOBOT robotic arm is included in the clone (not installed) for convenience.

Obtain a [Gemini API key](https://aistudio.google.com/app/apikey). Create a .env file and paste your key into it:
```env
GEMINI_AI_API_KEY=your_key_here
```

Connect DOBOT and webcam to your PC.

Run `four_corners.py` and place a half-sheet of letter paper to align with the corners the robot traces.

Run `main.py` and follow the directions in the CLI. If you have multiple webcams, you may need to increase the parameter of cv.VideoCapture() in line 35.


## Project Structure
- `main.py` - Runs the program, including capturing an image, prompting Gemini, logging the results, and running the generated code.
- `four_corners.py` - Moves robots to the centerline and four corners of the workspace.
- `prompt.txt` - The base prompt that is sent to Gemini, informing it of the workspace area and general instructions. A simpler user prompt is taken in `main.py` and appended to the base prompt.
- `responses/` - Each time `main.py` is run, a log of the prompt used and Gemini's response is created, timestamped, and stored in this directory.
- `suction_off.py` - Occasionally, the code Gemini generates leaves the vacuum pump on. Running this file will turn it back off.
- `lecture ppt.txt` and `python demo.txt` - Demo files that are sent to Gemini to inform it of how to control the robot.
- `dobot_api/` - The API used to control the robot, provided by the manufacturer.
- `test_images/` - A collection of images that can be used to test Gemini without setting up the webcam or robot.
