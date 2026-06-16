# main.py

import cv2
import mediapipe as mp
import time
import os
import subprocess

from gestures import detect_gesture, get_palm_width
from effects import overlay_image, apply_effect, powerpoint_vanish_effect


# -----------------------------
# DOSYA YUKLEME
# -----------------------------

def load_image(path):
    if not os.path.exists(path):
        print(f"Gorsel bulunamadi: {path}")
        return None

    image = cv2.imread(path, cv2.IMREAD_UNCHANGED)

    if image is None:
        print(f"Gorsel okunamadi: {path}")

    return image


def sound_exists(path):
    if not os.path.exists(path):
        print(f"Ses bulunamadi: {path}")
        return None

    return path

def get_sound_duration(path):
    """
    Mac'te afinfo komutu ile ses dosyasının süresini saniye olarak alır.
    Dosya yoksa veya süre okunamazsa varsayılan 2 saniye döner.
    """

    if path is None:
        return 2.0

    try:
        result = subprocess.run(
            ["afinfo", path],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        )

        for line in result.stdout.splitlines():
            if "estimated duration" in line:
                # Örnek satır:
                # estimated duration: 3.210 sec
                duration_text = line.split(":")[1].replace("sec", "").strip()
                return float(duration_text)

    except Exception:
        pass

    return 2.0

# -----------------------------
# SES CALMA
# -----------------------------

current_sound = None


def play_sound(path):
    """
    Mac icin afplay ile ses calar.
    Onceki sesi durdurur, yeni sesi baslatir.
    """

    global current_sound

    if path is None:
        return

    if current_sound is not None:
        current_sound.terminate()
        current_sound = None

    current_sound = subprocess.Popen(
        ["afplay", path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


# -----------------------------
# HAREKET AKSIYONLARI
# -----------------------------

gesture_actions = {
    "nah": {
        "sound": "sounds/nahc.mp3",
        "duration": get_sound_duration("sounds/nahc.mp3"),
        "image": load_image("images/nah.jpeg"),
        "effect": "normal",
        "text": "NAH SANA BAKLAVA"
    },

    "peace": {
        "sound": "sounds/peaceout2.mp3",
        "duration": get_sound_duration("sounds/peaceout2.mp3"),
        "image": load_image("images/peaceout.jpeg"),
        "effect": "vanish",
        "text": "PEACE OUT"
    },

    "open_hand_inside": {
        "sound": "sounds/gusammıc.mp3",
        "duration": get_sound_duration("sounds/gusammıc.mp3"),
        "image": load_image("images/gusammı.jpeg"),
        "effect": "normal",
        "text": "GUSAM MI HOCAM!"
    },

    "open_hand": {
        "sound": "sounds/hello.mp3",
        "duration": get_sound_duration("sounds/hello.mp3"),
        "image": load_image("images/hello.jpeg"),
        "effect": "normal",
        "text": "HELLOOWW!"
    }
}


# -----------------------------
# TETIKLEME AYARLARI
# -----------------------------

last_detected_gesture = None
stable_count = 0
required_stable_frames = 6

last_trigger_time = {}
cooldown = 3.0

last_global_trigger_time = 0
global_cooldown = 1.5

active_action = None
active_action_start_time = 0
effect_duration = 2.0
locked_gesture = None
gesture_released = True

show_debug = True


# -----------------------------
# VANISH EFEKTI ICIN ARKA PLAN
# -----------------------------

background_frame = None
person_mask = None


# -----------------------------
# MEDIAPIPE
# -----------------------------

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Kişi ayırma için MediaPipe Selfie Segmentation
mp_selfie = mp.solutions.selfie_segmentation
selfie_segmentation = mp_selfie.SelfieSegmentation(model_selection=1)


# -----------------------------
# KAMERA
# -----------------------------

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Kamera acilamadi.")
    exit()

window_name = "handmove"

cv2.startWindowThread()
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_name, 960, 720)
cv2.moveWindow(window_name, 100, 100)
cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)


while True:
    ret, frame = cap.read()

    if not ret:
        print("Goruntu alinamadi.")
        break

    frame = cv2.flip(frame, 1)

    frame_h, frame_w, _ = frame.shape

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # -----------------------------
    # KISI MASKESI
    # -----------------------------

    segmentation_result = selfie_segmentation.process(rgb_frame)
    person_mask = segmentation_result.segmentation_mask

    # -----------------------------
    # EL ALGILAMA
    # -----------------------------

    result = hands.process(rgb_frame)

    detected_gesture = None
    stable_gesture = None
    palm_width_value = None

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            landmarks = hand_landmarks.landmark

            detected_gesture = detect_gesture(landmarks)
            palm_width_value = get_palm_width(landmarks)

    current_time = time.time()

    # -----------------------------
    # GESTURE SABITLEME
    # -----------------------------

    if detected_gesture is not None and detected_gesture == last_detected_gesture:
        stable_count += 1
    else:
        stable_count = 0

    last_detected_gesture = detected_gesture

    if stable_count >= required_stable_frames:
        stable_gesture = detected_gesture


    # -----------------------------
    # GESTURE LOCK / TEKRAR TETIKLEME ENGELI
    # -----------------------------

    # Eğer elde artık hareket yoksa veya farklı hareket algılandıysa,
    # eski kilit açılır.
    if locked_gesture is not None:
        if detected_gesture != locked_gesture:
         gesture_released = True
         locked_gesture = None

    # -----------------------------
    # HAREKET TETIKLEME
    # -----------------------------

    if stable_gesture in gesture_actions and gesture_released:
        action = gesture_actions[stable_gesture]

        last_time = last_trigger_time.get(stable_gesture, 0)

        action_finished = (
            active_action is None or
            current_time - active_action_start_time > active_action_duration
        )

        can_trigger = (
            action_finished and
            current_time - last_time > cooldown and
            current_time - last_global_trigger_time > global_cooldown
        )
    
        if can_trigger:
            print(f"Tetiklenen hareket: {stable_gesture}")

            play_sound(action["sound"])

            active_action = action
            active_action_start_time = current_time
            active_action_duration = action["duration"]

            last_trigger_time[stable_gesture] = current_time
            last_global_trigger_time = current_time

            # Bu hareket kilitlensin.
            # Kullanıcı elini bu hareketten çıkarana kadar tekrar tetiklenmesin.
            locked_gesture = stable_gesture
            gesture_released = False

    # -----------------------------
    # AKTIF EFEKT / GORSEL
    # -----------------------------

    if active_action is not None:
        if current_time - active_action_start_time <= active_action_duration:

            elapsed_time = current_time - active_action_start_time
            progress = elapsed_time / active_action_duration
            progress = min(progress, 1.0)

            if active_action["effect"] == "vanish":
                frame = powerpoint_vanish_effect(
                    frame,
                    background_frame,
                    person_mask,
                    progress
                )
            else:
                frame = apply_effect(frame, active_action["effect"])

            if active_action["image"] is not None:
                frame = overlay_image(
                    frame,
                    active_action["image"],
                    frame_w - 230,
                    30,
                    width=200
                )

            cv2.putText(
                frame,
                active_action["text"],
                (30, frame_h - 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

        else:
            active_action = None

    # -----------------------------
    # DEBUG BILGILERI
    # -----------------------------

    if show_debug:
        if detected_gesture is not None:
            cv2.putText(
                frame,
                f"Gesture: {detected_gesture}",
                (30, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2
            )

        if stable_gesture is not None:
            cv2.putText(
                frame,
                f"Stable: {stable_gesture}",
                (30, 75),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

        if palm_width_value is not None:
            cv2.putText(
                frame,
                f"Palm Width: {palm_width_value:.2f}",
                (30, 110),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2
            )

        cv2.putText(
            frame,
            f"Stable Count: {stable_count}",
            (30, 145),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            "b: arka plan kaydet | q: cikis",
            (30, frame_h - 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
        if locked_gesture is not None:
            cv2.putText(
                frame,
                f"Locked: {locked_gesture}",
                (30, 180),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 255),
                2
    )

    cv2.imshow(window_name, frame)

    key = cv2.waitKey(1) & 0xFF

    # Arka planı kaydet
    if key == ord("b"):
        background_frame = frame.copy()
        print("Arka plan kaydedildi.")

    # Çıkış
    if key == ord("q"):
        break


if current_sound is not None:
    current_sound.terminate()

cap.release()
cv2.destroyAllWindows()