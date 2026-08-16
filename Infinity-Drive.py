import os
import time
import numpy as np
import cv2
from PIL import Image, ImageDraw
from tqdm import tqdm

pref = input("Would you like to [1] ENCODE or [2] DECODE a file?: ")

WIDTH = 1280
HEIGHT = 720
DENSITY = 8
FPS = 30
BATCH_FRAMES = 300

if pref == "1":
    input_file = input("What file should I encode? (i.e input.zip): ")
    while str(os.path.isfile(input_file)) != "True":
        print("Oops! File does not exist.")
        input_file = input("What file should I encode?: ")
    file_size = os.path.getsize(input_file)

    video = cv2.VideoWriter("Infinity-Drive.mp4", cv2.VideoWriter_fourcc(*'mp4v'), FPS, (WIDTH, HEIGHT), isColor=False)

    img = Image.new('1', (WIDTH, HEIGHT), "black")
    w_pix = 0
    h_pix = 0
    if len(str(DENSITY)) == 1:
        density_binary = "".join(format(byte, '08b') for byte in str(0).encode('utf-8'))
        for a in range(len(density_binary)):
            if density_binary[a] == "1":
                ImageDraw.Draw(img).rectangle((w_pix, h_pix, w_pix + (WIDTH / 8) - 1, h_pix + (HEIGHT / 2) - 1), fill="white", outline=None, width=1)
            w_pix += (WIDTH / 8)
        w_pix = 0
        h_pix += (HEIGHT / 2)
    for a in range(len(str(DENSITY))):
        density_binary = "".join(format(byte, '08b') for byte in str(DENSITY)[a].encode('utf-8'))
        for b in range(len(density_binary)):
            if str(density_binary)[b] == "1":
                ImageDraw.Draw(img).rectangle((w_pix, h_pix, w_pix + (WIDTH / 8) - 1, h_pix + (HEIGHT / 2) - 1), fill="white", outline=None, width=1)
            w_pix += (WIDTH / 8)
        w_pix = 0
        h_pix += (HEIGHT / 2)
    meta_frame = np.array(img, dtype=np.uint8) * 255
    video.write(meta_frame)
    frames = 1

    print("Generating frames, please be patient...")
    tic = time.perf_counter()

    bytes_per_row = WIDTH // DENSITY
    rows_per_frame = HEIGHT // DENSITY
    bytes_per_frame = (bytes_per_row * rows_per_frame) // 8

    with open(input_file, "rb") as f:
        data = f.read()

    byte_array = np.frombuffer(data, dtype=np.uint8)
    frames_total = -(-len(byte_array) // bytes_per_frame)
    pad_len = frames_total * bytes_per_frame - len(byte_array)
    if pad_len > 0:
        byte_array = np.pad(byte_array, (0, pad_len), constant_values=0)

    with tqdm(total=frames_total, unit=' FP') as pbar:
        for start in range(0, frames_total, BATCH_FRAMES):
            end = min(start + BATCH_FRAMES, frames_total)
            batch_count = end - start
            batch_bytes = byte_array[start * bytes_per_frame:end * bytes_per_frame]

            bits = np.unpackbits(batch_bytes)
            bits = bits.reshape(batch_count, rows_per_frame, bytes_per_row)
            frame_batch = np.repeat(np.repeat(bits, DENSITY, axis=1), DENSITY, axis=2)
            frame_batch = (frame_batch * 255).astype(np.uint8)

            for i in range(batch_count):
                video.write(frame_batch[i])
                frames += 1
            pbar.update(batch_count)

    video.release()
    toc = time.perf_counter()
    print("Generated " + str(frames) + f" frames in {toc - tic:0.4f} seconds.")
    cv2.destroyAllWindows()

elif pref == "2":
    input_file = input("What file should I decode? (i.e Infinity-Drive.mp4): ")
    while str(os.path.isfile(input_file)) != "True":
        print("Oops! File does not exist.")
        input_file = input("What file should I decode?: ")
    cap = cv2.VideoCapture(input_file)

    output_file = input("What should I name the output file? (i.e output.zip): ")
    while str(os.path.exists(output_file)) == "True":
        print("Oops! File already exists.")
        output_file = input("What should I name the output file?: ")

    frames_total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.set(1, 0)
    res, frame = cap.read()
    height, width = frame.shape[:2]

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if frame.ndim == 3 else frame
    image = Image.fromarray(gray)
    binary = ""
    for a in range(2):
        for b in range(8):
            coordinate = (int((width / 8) * b + 2), int((height / 2) * a + 2))
            color = image.getpixel(coordinate)
            binary += "1" if color > 128 else "0"
    density = int(bytes(int(binary[i:i+8], 2) for i in range(0, len(binary), 8)).decode('utf-8'))

    rows_per_frame = height // density
    bytes_per_row = width // density
    remaining = frames_total - 1

    tic = time.perf_counter()

    with open(output_file, "wb") as file:
        with tqdm(total=remaining, unit=' FP') as pbar:
            while True:
                batch = []
                for _ in range(BATCH_FRAMES):
                    res, frame = cap.read()
                    if not res:
                        break
                    g = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if frame.ndim == 3 else frame
                    batch.append(g)
                if not batch:
                    break

                batch_arr = np.stack(batch)
                small = batch_arr[:, ::density, ::density]
                small = small[:, :rows_per_frame, :bytes_per_row]
                bits = (small > 128).astype(np.uint8)
                bits = bits.reshape(bits.shape[0], -1)
                packed = np.packbits(bits, axis=1)
                file.write(packed.tobytes())
                pbar.update(len(batch))

    cap.release()
    toc = time.perf_counter()
    print(f"Decoded in {toc - tic:0.4f} seconds.")
    cv2.destroyAllWindows()