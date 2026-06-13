import gradio as gr
from PIL import Image, ImageSequence
import os, threading, time, cv2, random
import numpy as np
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

# Lấy đường dẫn thư mục ảnh
IMAGE_DIR = os.getenv("IMAGE_DIR", "images")
AUDIO_DIR = os.getenv("AUDIO_DIR", "sound")
EXT_OF_IMG = os.getenv("EXT_OF_IMG", ".png")
SHARE_ = os.getenv("SHARE", 0)
SHARE = False if int(SHARE_) == 0 else True
REALTIME_ = os.getenv("REALTIME", 0)
REALTIME = False if int(REALTIME_) == 0 else True
CHANGESTATUSTIME = os.getenv("CHANGESTATUSTIME", 10)

offsets = [(-5, 0), (5, 0), (0, -5), (0, 5), (0, 0), (-10, 0), (10, 0), (0, -10), (0, 10), (0, 0), ]


def readimg(outna):
    if not outna.endswith(EXT_OF_IMG):
        outna += EXT_OF_IMG
        return cv2.imread(f"{IMAGE_DIR}{os.sep}{outna}")


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


def overlay_items(item_path, num_items=10, min_ratio=0.3, max_ratio=0.4, bg_path="base", activ_name="eat"):
    """- code python ghép đồ dùng (bỏ nền trắng) vào 4 góc của ảnh gốc, lặp lại 4 lần vào các vị trí ngẫu nhiên của ảnh nhưng chồng lấn lên nhau ít nhất (không chèn vào hình vuông cạnh 1/2 chiều rộng ảnh ở nửa trên ảnh)"""
    bg = readimg(bg_path)
    item = readimg(item_path)
    if bg is None or item is None:
        print("Không đọc được ảnh!")
        return

    h_bg, w_bg, _ = bg.shape

    # --- bỏ nền trắng ---
    gray = cv2.cvtColor(item, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    b, g, r = cv2.split(item)
    item_rgba = cv2.merge([b, g, r, mask])

    result = bg.copy()

    # --- vùng cấm: hình vuông cạnh 1/2 chiều rộng ảnh, ở nửa trên ---
    forbidden_size = int(w_bg * 0.5)
    forbidden_xmin = (w_bg - forbidden_size) // 2
    forbidden_xmax = forbidden_xmin + forbidden_size
    forbidden_ymin = 0
    forbidden_ymax = h_bg // 2

    placed_boxes = []

    def place_item(x, y, target_w, target_h, resized):
        rgb = resized[:, :, :3]
        alpha = resized[:, :, 3] / 255.0
        alpha_inv = 1.0 - alpha
        for c in range(3):
            result[y:y+target_h, x:x+target_w, c] = (
                alpha * rgb[:, :, c] +
                alpha_inv * result[y:y+target_h, x:x+target_w, c]
            )
        placed_boxes.append((x, y, x+target_w, y+target_h))

    def resize_item():
        ratio = random.uniform(min_ratio, max_ratio)
        target_w = int(w_bg * ratio)
        target_h = int(item_rgba.shape[0] * (target_w / item_rgba.shape[1]))
        resized = cv2.resize(item_rgba, (target_w, target_h), interpolation=cv2.INTER_AREA)
        return target_w, target_h, resized

    # --- THAY ĐỔI: chèn vào 4 góc ---
    corners = [
        (0, 10),
        # (w_bg, 0),
        # (0, h_bg),
        (w_bg - 10, h_bg)
    ]
    for cx, cy in corners:
        target_w, target_h, resized = resize_item()
        x = max(0, cx - target_w if cx > 0 else 0)
        y = max(0, cy - target_h if cy > 0 else 0)
        place_item(x, y, target_w, target_h, resized)

    # --- THAY ĐỔI: thêm 4 vị trí ngẫu nhiên ---
    if True:  # for _ in range(4):
        target_w, target_h, resized = resize_item()
        for _ in range(100):
            x = random.randint(0, w_bg - target_w)
            y = random.randint(0, h_bg - target_h)

            # kiểm tra vùng cấm
            overlap_forbidden = not (x + target_w < forbidden_xmin or x > forbidden_xmax or
                                     y + target_h < forbidden_ymin or y > forbidden_ymax)
            if overlap_forbidden:
                continue

            # kiểm tra chồng lấn
            new_box = (x, y, x+target_w, y+target_h)
            too_much_overlap = False
            for bx in placed_boxes:
                ixmin = max(new_box[0], bx[0])
                iymin = max(new_box[1], bx[1])
                ixmax = min(new_box[2], bx[2])
                iymax = min(new_box[3], bx[3])
                if ixmin < ixmax and iymin < iymax:
                    inter_area = (ixmax - ixmin) * (iymax - iymin)
                    box_area = (new_box[2]-new_box[0])*(new_box[3]-new_box[1])
                    if inter_area / box_area > 0.2:
                        too_much_overlap = True
                        break
            if too_much_overlap:
                continue

            place_item(x, y, target_w, target_h, resized)
            break

    if not activ_name.endswith(EXT_OF_IMG):
        activ_name += EXT_OF_IMG
    cv2.imwrite(f"{IMAGE_DIR}{os.sep}{activ_name}", result)
    print(f"Đã lưu ảnh kết quả {activ_name}")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def thre_hold(hunger, energy, happiness, audio_queue):
    alert = ""
    aulist = [f"{AUDIO_DIR}{os.sep}base.mp3", ]  # list()  # danh sách tạm khởi tạo với tiếng kêu mặc định
    if hunger > 80:  # nếu đói vượt quá ngưỡng an toàn
        alert += "Đói quá đói quá!\n"  # TODO sinh câu văn tương tự  # TODO text to speech
        aulist.append(f"{AUDIO_DIR}{os.sep}hunger.mp3")  # aulist = f"{AUDIO_DIR}{os.sep}hunger.mp3"  # thêm tiếng kêu đói vào danh sách tạm
    else:  # nếu đói nằm trong ngưỡng an toàn
        audio_queue = [aq for aq in audio_queue if not aq == f"{AUDIO_DIR}{os.sep}hunger.mp3"]  # xóa tất cả tiếng kêu đói trong danh sách
    if energy < 20:  # nếu mệt dưới ngưỡng an toàn
        alert += "mệt quá mệt quá!\n"
        aulist.append(f"{AUDIO_DIR}{os.sep}weak.mp3")  # aulist = f"{AUDIO_DIR}{os.sep}weak.mp3"  #  thêm tiếng kêu mệt vào danh sách tạm
    else:  # nếu mệt nằm trong ngưỡng an toàn
        audio_queue = [aq for aq in audio_queue if not aq == f"{AUDIO_DIR}{os.sep}weak.mp3"]  # xóa tất cả tiếng kêu mệt trong danh sách
    if happiness < 20:  # nếu vui vẻ dưới ngưỡng an toàn
        alert += "buồn quá buồn quá!\n"
        aulist.append(f"{AUDIO_DIR}{os.sep}bore.mp3")  # aulist = f"{AUDIO_DIR}{os.sep}bore.mp3"  #  thêm tiếng kêu buồn vào danh sách tạm
    else:  # nếu buồn nằm trong ngưỡng an toàn
        audio_queue = [aq for aq in audio_queue if not aq == f"{AUDIO_DIR}{os.sep}bore.mp3"]  # xóa tất cả tiếng kêu buồn trong danh sách
    # tham số cuối cùng trả về là danh sách đầu vào đã xóa theo trạng thái đắp thêm danh sách tạm
    return alert, aulist, audio_queue + aulist


class VirtualPet:
    def __init__(self, name):
        self.name = name
        self.hunger = 50
        self.happiness = 50
        self.energy = 50
        self.audio_queue: list = []
        self.last_audio = None
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
        ale, audios, self.audio_queue = thre_hold(self.hunger, self.energy, self.happiness, self.audio_queue)

        # if not self.audio_queue:
        self.audio_queue.extend(audios)

        current_audio = None

        if self.audio_queue:
            current_audio = self.audio_queue.pop(0)

        return f"{self.name} trạng thái hiện tại", f"{IMAGE_DIR}{os.sep}base.png", self.hunger, self.happiness, self.energy, ale, current_audio

    def feed(self):
        num = random.randrange(4)
        activ_name = (f"food/eat{num}", "đang ăn 🍖", )
        self.hunger = max(0, self.hunger - 10)
        self.happiness = min(100, self.happiness + 5)
        return self.retu(activ_name)

    def play(self):
        num = random.randrange(4)
        activ_name = (f"play__/play{num}", "đang chơi 🎾", )
        self.happiness = min(100, self.happiness + 10)
        self.energy = max(0, self.energy - 5)
        self.hunger = min(100, self.hunger + 10)
        return self.retu(activ_name)

    def sleep(self):
        num = random.randrange(4)
        activ_name = (f"moon_star/sleep{num}", "đang ngủ 😴", )
        self.happiness = min(100, self.happiness - 5)
        self.energy = min(100, self.energy + 15)
        self.hunger = min(100, self.hunger + 5)
        return self.retu(activ_name)


if __name__ == "__main__":
    create_gif('base', 'base', )
    for activ_name in (('play__/play__', "play__/play", ), ('food/food', "food/eat", ), ('moon_star/moon_star', "moon_star/sleep"), ):
        for so in range(4):
            overlay_items(f'{activ_name[0]}{so}', num_items=8, min_ratio=0.5, max_ratio=0.6, bg_path="base", activ_name=f'{activ_name[1]}{so}')
            create_gif(f'{activ_name[1]}{so}', f'{activ_name[1]}{so}', )
    # for imgnam in [ina for ina in os.listdir(IMAGE_DIR) if ina.endswith(EXT_OF_IMG)]:
    #     create_gif(imgnam[: -4], imgnam, )
