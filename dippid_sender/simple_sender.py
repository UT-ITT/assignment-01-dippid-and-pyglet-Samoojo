import socket
import time
import random
import math

IP = "127.0.0.1"
PORT = 5700

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


isButtonPressed = False
nextActionTime = time.time() + random.randint(5, 10)

while True:
    currentTime = time.time()

    # simulate the user pressing the button randomly
    if not isButtonPressed:
        if currentTime >= nextActionTime:
            print("Sent: Press")
            isButtonPressed = True
            nextActionTime = currentTime + 1
    else:
        if currentTime >= nextActionTime:
            print("Sent: Release")
            isButtonPressed = False
            nextActionTime = currentTime + random.randint(5, 10)

    # send continous stream of button events
    if isButtonPressed:
        sock.sendto(b'{"button_1": 1}', (IP, PORT))
    else:
        sock.sendto(b'{"button_1": 0}', (IP, PORT))

    # simulate continous movement of the phone
    x = math.sin(currentTime)
    y = math.cos(currentTime)
    z = math.sin(currentTime * 0.5)

    # send phone movement
    message = f'{{"accelerometer": ' f'{{"x": {x:.6f}, "y": {y:.6f}, "z": {z:.6f}}}}}'
    sock.sendto(
        message.encode(),
        (IP, PORT),
    )

    time.sleep(0.01)
