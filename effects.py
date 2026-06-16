# effects.py

import cv2
import numpy as np


def overlay_image(frame, overlay, x, y, width=180):
    if overlay is None:
        return frame

    h, w = overlay.shape[:2]

    if w == 0 or h == 0:
        return frame

    ratio = width / w
    new_h = int(h * ratio)

    overlay = cv2.resize(overlay, (width, new_h))

    frame_h, frame_w = frame.shape[:2]

    if x < 0 or y < 0:
        return frame

    if x + width > frame_w or y + new_h > frame_h:
        return frame

    if len(overlay.shape) == 3 and overlay.shape[2] == 4:
        alpha = overlay[:, :, 3] / 255.0
        overlay_rgb = overlay[:, :, :3]
    else:
        alpha = np.ones((new_h, width))
        overlay_rgb = overlay

    for c in range(3):
        frame[y:y + new_h, x:x + width, c] = (
            alpha * overlay_rgb[:, :, c] +
            (1 - alpha) * frame[y:y + new_h, x:x + width, c]
        )

    return frame


def normal_effect(frame):
    return frame


def funny_effect(frame):
    cv2.putText(
        frame,
        "HAHA!",
        (50, 90),
        cv2.FONT_HERSHEY_SIMPLEX,
        2,
        (0, 255, 255),
        4
    )

    return frame


def glitch_effect(frame):
    result = frame.copy()
    h, w = result.shape[:2]

    step = 25

    for y in range(0, h, step):
        shift = 10 if (y // step) % 2 == 0 else -10
        result[y:y + step] = np.roll(result[y:y + step], shift, axis=1)

    cv2.putText(
        result,
        "GLITCH!",
        (50, 90),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.5,
        (255, 255, 255),
        3
    )

    return result


def powerpoint_vanish_effect(frame, background_frame, person_mask, progress):
    """
    Peace out için net anlık kaybolma efekti.
    Blur yok, saydamlık yok.
    Kişi alanı direkt arka planla değiştirilir.
    """

    h, w = frame.shape[:2]

    # Arka plan kaydedilmediyse mevcut frame'i kullanır.
    # En iyi sonuç için kadrajdan çıkıp b tuşuna bas.
    if background_frame is None:
        background_frame = frame.copy()
    else:
        background_frame = cv2.resize(background_frame, (w, h))

    result = frame.copy()

    if person_mask is None:
        return result

    # Maskeyi frame boyutuna getir
    person_mask = cv2.resize(person_mask, (w, h))

    # Daha net kişi maskesi
    # 0.5 yerine 0.35 kullanıyoruz ki saç/omuz gibi bölgeler de silinsin.
    person_area = person_mask > 0.15

    # Maskedeki küçük boşlukları kapat
    kernel = np.ones((9, 9), np.uint8)
    person_area = person_area.astype(np.uint8) * 255

    person_area = cv2.morphologyEx(person_area, cv2.MORPH_CLOSE, kernel)
    person_area = cv2.dilate(person_area, kernel, iterations=3)

    person_area = person_area > 0

    # Kişi olan alanı direkt arka planla değiştir
    result[person_area] = background_frame[person_area]

    return result
   

def apply_effect(frame, effect_name):
    if effect_name == "funny":
        return funny_effect(frame)

    if effect_name == "glitch":
        return glitch_effect(frame)

    if effect_name == "peace_out":
        return powerpoint_vanish_effect(frame)

    return normal_effect(frame)