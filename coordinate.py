import gradio as gr
from PIL import Image, ImageSequence
import os, threading, time
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

# Lấy đường dẫn thư mục ảnh
IMAGE_DIR = os.getenv("IMAGE_DIR", "images")
EXT_OF_IMG = os.getenv("EXT_OF_IMG", ".png")
SHARE_ = os.getenv("SHARE", 0)
SHARE = False if int(SHARE_) == 0 else True
REALTIME_ = os.getenv("REALTIME", 0)
REALTIME = False if int(REALTIME_) == 0 else True
CHANGESTATUSTIME = os.getenv("CHANGESTATUSTIME", 10)

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


def thre_hold(hunger, energy, happiness):
    alert = ""
    if hunger > 80:
        alert += "Đói quá đói quá!\n"  # TODO sinh câu văn tương tự  # TODO text to speech
    if energy < 20:
        alert += "mệt quá mệt quá!\n"
    if happiness < 20:
        alert += "buồn quá buồn quá!\n"
    return alert


class VirtualPet:
    def __init__(self, name):
        self.name = name
        self.hunger = 50
        self.happiness = 50
        self.energy = 50
        self.rule = """<ul>
  <li><strong>Feed:</strong> Hunger - 10, Happiness + 5</li>
  <li><strong>Play:</strong> Happiness + 10, Hunger + 10, Energy - 5</li>
  <li><strong>Sleep:</strong> Happiness - 5, Hunger + 5, Energy + 15</li>
</ul>"""
        self.last_update_time = time.time()
        self.tick_speed = 1.5

    def retu(self, activ_name):
        """
        :param activ_name: ("eat", "đang ăn 🍖")
        :return:
        """
        return f"{self.name} {activ_name[1]}", f"{IMAGE_DIR}{os.sep}{activ_name[0]}.gif", self.hunger, self.happiness, self.energy

    def update_status_by_time(self):
        """Hàm tự động tính toán bù trừ chỉ số dựa trên thời gian thực trôi qua"""
        if not REALTIME:
            self.hunger = min(100, self.hunger + 1)
            self.happiness = max(0, self.happiness - 1)
            self.energy = max(0, self.energy - 1)
            return
        current_time = time.time()
        # Tính xem đã bao nhiêu giây trôi qua kể từ lần cập nhật cuối
        elapsed_time = current_time - self.last_update_time

        if elapsed_time >= self.tick_speed:
            # Tính số chu kỳ (ticks) đã trôi qua trong thời gian người dùng rời đi
            num_ticks = int(elapsed_time // self.tick_speed)

            # Trừ bù chỉ số dựa trên số ticks
            self.hunger = min(100, self.hunger + (num_ticks * 3))
            self.happiness = max(0, self.happiness - (num_ticks * 2))
            self.energy = max(0, self.energy - (num_ticks * 2))

            # Cập nhật lại mốc thời gian mới nhất
            self.last_update_time += num_ticks * self.tick_speed

    def tick(self):
        self.update_status_by_time()
        ale = thre_hold(self.hunger, self.energy, self.happiness)
        return f"{self.name} trạng thái hiện tại", f"{IMAGE_DIR}{os.sep}base.png", self.hunger, self.happiness, self.energy, ale

    def feed(self):
        activ_name = ("eat", "đang ăn 🍖", )
        self.hunger = max(0, self.hunger - 10)
        self.happiness = min(100, self.happiness + 5)
        return self.retu(activ_name)

    def play(self):
        activ_name = ("play", "đang chơi 🎾", )
        self.happiness = min(100, self.happiness + 10)
        self.energy = max(0, self.energy - 5)
        self.hunger = min(100, self.hunger + 10)
        return self.retu(activ_name)

    def sleep(self):
        activ_name = ("sleep", "đang ngủ 😴", )
        self.happiness = min(100, self.happiness - 5)
        self.energy = min(100, self.energy + 15)
        self.hunger = min(100, self.hunger + 5)
        return self.retu(activ_name)


if __name__ == "__main__":
    for imgnam in [ina for ina in os.listdir(IMAGE_DIR) if ina.endswith(EXT_OF_IMG)]:
        create_gif(imgnam[: -4], imgnam, )
