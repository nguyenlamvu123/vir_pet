import gradio as gr
from PIL import Image, ImageSequence
import os, threading, time
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

# Lấy đường dẫn thư mục ảnh
IMAGE_DIR = os.getenv("IMAGE_DIR", "images")
EXT_OF_IMG = os.getenv("EXT_OF_IMG", ".png")

offsets = [(-5, 0), (5, 0), (0, -5), (0, 5), (0, 0), (-10, 0), (10, 0), (0, -10), (0, 10), (0, 0), ]


def create_gif(gif_name, *list_of_path):
    """
    :param list_of_path: ["eat.png", "play", "sleep", ]
    :param gif_name: str
    :return:
    """
    if len(list_of_path) == 1:
        activ_name = list_of_path[0]
        if not activ_name.endswith(EXT_OF_IMG):
            activ_name += EXT_OF_IMG
        img = Image.open(f"{IMAGE_DIR}{os.sep}{activ_name}")
        frames = []
        for dx, dy in offsets:
            # Tạo nền trắng cùng kích thước
            frame = Image.new("RGBA", img.size, (255, 255, 255, 0))
            # Dán ảnh vào vị trí lệch
            frame.paste(img, (dx, dy))
            frames.append(frame)
    else:
        frames = [Image.open(im) for im in list_of_path]
    if not gif_name.endswith(".gif"):
        gif_name += ".gif"
    frames[0].save(
        f"{IMAGE_DIR}{os.sep}{gif_name}",
        save_all=True,
        append_images=frames[1:],
        duration=500,   # thời gian mỗi frame (ms)
        loop=0          # 0 = lặp vô hạn
    )

if __name__ == "__main__":
    for imgnam in [ina for ina in os.listdir(IMAGE_DIR) if ina.endswith(EXT_OF_IMG)]:
        create_gif(imgnam[: -4], imgnam, )
