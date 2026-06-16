# gesture-project
HandMove - Real-Time Hand Gesture Effects

HandMove is a real-time hand gesture recognition project built with Python, OpenCV, and MediaPipe.

The system detects specific hand gestures through the webcam and triggers custom visual effects and sound effects based on the recognized gesture.

⸻

Features

* Real-time webcam hand tracking
* Hand gesture recognition using MediaPipe
* Custom visual effects for different gestures
* Sound effects triggered by gestures
* Gesture cooldown system to prevent repeated triggering
* Image overlay effects on the camera screen
* Modular Python file structure

⸻

Technologies Used

* Python
* OpenCV
* MediaPipe
* NumPy
* Audio playback library

⸻

Project Structure

handmove/
│
├── main.py              # Main application file
├── gestures.py          # Gesture detection logic
├── effects.py           # Visual effect functions
├── test_camera.py       # Camera test script
├── test_mediapipe.py    # MediaPipe test script
│
├── images/              # Images used for visual effects
├── sounds/              # Sound effects
│
├── README.md
└── .gitignore

⸻

How It Works

The project captures video from the webcam using OpenCV.

MediaPipe is used to detect hand landmarks in real time.

According to the detected hand gesture, the system plays a related sound effect and displays a visual effect on the screen.

Each gesture has its own effect logic. To avoid repeated triggering, the project uses a cooldown mechanism. This means the same gesture will not be triggered again until the current sound and visual effect are completed.

⸻

Installation

First, clone the repository:

git clone https://github.com/beren04/gesture-project.git
cd gesture-project

Create and activate a virtual environment:

python -m venv .venv
source .venv/bin/activate

Install the required libraries:

pip install opencv-python mediapipe numpy

If your project uses an extra library for playing sound, install it as well.

Example:

pip install playsound

or

pip install simpleaudio

⸻

Usage

Run the main project file:

python main.py

Make sure your webcam is connected and accessible.

⸻

Gestures

The project can be customized to detect different hand gestures.
Each gesture can trigger a different sound and visual effect.

Example gesture actions:

* Peace gesture: displays a visual effect and plays a related sound
* Custom hand gesture: triggers a different image and sound effect
* Vanish effect: removes the user from the frame with a sudden visual effect

⸻

Customization

You can add your own images and sounds by placing them inside the related folders:

images/
sounds/

Then update the gesture and effect logic inside:

gestures.py
effects.py
main.py

⸻

Notes

* Good lighting improves hand detection accuracy.
* Keep your hand clearly visible in front of the camera.
* If the camera does not open, check your macOS camera permissions.
* If a gesture triggers repeatedly, adjust the cooldown or effect duration logic.

⸻

Future Improvements

* Add more hand gestures
* Improve gesture accuracy
* Add a better user interface
* Add configurable gesture-effect mappings
* Improve visual effect transitions
* Add support for multiple hands

⸻

Author

Developed by Beren Elitaş.
