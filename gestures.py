# gestures.py


def fingers_status(landmarks):
    """
    El landmark noktalarına göre parmakların açık/kapalı durumunu döndürür.

    True  = parmak açık
    False = parmak kapalı
    """

    # MediaPipe'ta y değeri küçüldükçe nokta yukarı çıkar.
    index_up = landmarks[8].y < landmarks[6].y
    middle_up = landmarks[12].y < landmarks[10].y
    ring_up = landmarks[16].y < landmarks[14].y
    pinky_up = landmarks[20].y < landmarks[18].y

    # Baş parmak sağ/sol ele göre değiştiği için sadece yaklaşık kontrol.
    thumb_open = abs(landmarks[4].x - landmarks[3].x) > 0.04

    return {
        "thumb": thumb_open,
        "index": index_up,
        "middle": middle_up,
        "ring": ring_up,
        "pinky": pinky_up
    }


def get_palm_width(landmarks):
    """
    Elin kameraya göre ne kadar geniş göründüğünü hesaplar.

    landmarks[5]  = işaret parmağı kök noktası
    landmarks[17] = serçe parmağı kök noktası
    """

    index_mcp = landmarks[5]
    pinky_mcp = landmarks[17]

    return abs(index_mcp.x - pinky_mcp.x)


def is_open_hand(fingers):
    """
    Dört ana parmak açıksa açık el kabul edilir.
    Baş parmak bu kontrolde şart değil.
    """

    return (
        fingers["index"] and
        fingers["middle"] and
        fingers["ring"] and
        fingers["pinky"]
    )


def is_palm_facing_camera(landmarks):
    """
    Avuç içi kameraya dönük açık el kontrolü.
    Palm width büyükse el kameraya daha düz bakıyor kabul edilir.
    """

    palm_width = get_palm_width(landmarks)

    return palm_width > 0.12


def is_palm_turned_inside(landmarks):
    """
    Avuç içi içe/yan dönük açık el kontrolü.
    Palm width küçükse el yan/içe dönük kabul edilir.
    """

    palm_width = get_palm_width(landmarks)

    return palm_width <= 0.12


def is_finger_closed(landmarks, tip_id, pip_id):
    """
    Parmağın kapalı olup olmadığını kontrol eder.

    tip_id = parmak ucu noktası
    pip_id = parmağın orta eklem noktası

    MediaPipe'ta y değeri büyüdükçe nokta aşağı iner.
    Parmak ucu, orta eklemden daha aşağıdaysa parmak kapalı kabul edilir.
    """

    return landmarks[tip_id].y > landmarks[pip_id].y


def is_nah_gesture(landmarks):
    """
    Gerçek nah hareketine yakın kontrol.

    Mantık:
    - İşaret, orta, yüzük ve serçe parmak kapalı olacak.
    - Baş parmak işaret ve orta parmak kök noktaları arasında/çevresinde görünecek.
    """

    thumb_tip = landmarks[4]

    index_mcp = landmarks[5]
    middle_mcp = landmarks[9]

    # Parmaklar kapalı mı?
    index_closed = is_finger_closed(landmarks, 8, 6)
    middle_closed = is_finger_closed(landmarks, 12, 10)
    ring_closed = is_finger_closed(landmarks, 16, 14)
    pinky_closed = is_finger_closed(landmarks, 20, 18)

    fingers_closed = (
        index_closed and
        middle_closed and
        ring_closed and
        pinky_closed
    )

    # Baş parmak işaret ve orta parmak kök noktalarının x aralığına yakın mı?
    min_x = min(index_mcp.x, middle_mcp.x)
    max_x = max(index_mcp.x, middle_mcp.x)

    thumb_between_index_middle = (
        min_x - 0.12 <= thumb_tip.x <= max_x + 0.12
    )

    # Baş parmak yumruğun çok altında kalmasın.
    # landmarks[13] = yüzük parmağı kök noktası
    thumb_visible_in_fist = thumb_tip.y < landmarks[13].y

    return fingers_closed and thumb_between_index_middle and thumb_visible_in_fist


def detect_gesture(landmarks):
    """
    Algılanan el hareketinin adını döndürür.

    Dönebilecek değerler:
    - nah
    - peace
    - open_hand_inside
    - open_hand
    - None
    """

    fingers = fingers_status(landmarks)

    index = fingers["index"]
    middle = fingers["middle"]
    ring = fingers["ring"]
    pinky = fingers["pinky"]

    # 1. Nah hareketi
    # Yumruk kapalı + baş parmak işaret/orta parmak arasından çıkıyor.
    if is_nah_gesture(landmarks):
        return "nah"

    # 2. Peace out hareketi
    # İşaret + orta açık, yüzük + serçe kapalı.
    if index and middle and not ring and not pinky:
        return "peace"

    # 3. Avuç içi içe/yan dönük açık el
    # Gusam mı hocam hareketi için.
    if is_open_hand(fingers) and is_palm_turned_inside(landmarks):
        return "open_hand_inside"

    # 4. Normal açık el
    # Avuç içi kameraya dönük açık el.
    if is_open_hand(fingers) and is_palm_facing_camera(landmarks):
        return "open_hand"

    return None