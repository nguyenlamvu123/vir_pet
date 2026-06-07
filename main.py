from coordinate import gr, os, threading, time, \
    IMAGE_DIR

class VirtualPet:
    """
    feed: hunger - 10, happiness + 5
    play: happiness + 10, energy - 5
    sleep: happiness - 5, hunger + 5, energy + 15
    """
    def __init__(self, name):
        self.name = name
        self.hunger = 50
        self.happiness = 50
        self.energy = 50

    def retu(self, activ_name):
        """
        :param activ_name: ("eat", "đang ăn 🍖")
        :return:
        """
        return f"{self.name} {activ_name[1]}", f"{IMAGE_DIR}{os.sep}{activ_name[0]}.gif", self.hunger, self.happiness, self.energy

    def tick(self):
        # Mỗi lần tick: hunger +1, happiness -1, energy -1
        self.hunger = min(100, self.hunger + 1)
        self.happiness = max(0, self.happiness - 1)
        self.energy = max(0, self.energy - 1)
        return f"{self.name} trạng thái hiện tại", f"{IMAGE_DIR}{os.sep}base.png", self.hunger, self.happiness, self.energy

    def feed(self):
        activ_name = ("eat", "đang ăn 🍖", )
        self.hunger = max(0, self.hunger - 10)
        self.happiness = min(100, self.happiness + 5)
        return self.retu(activ_name)

    def play(self):
        activ_name = ("play", "đang chơi 🎾", )
        self.happiness = min(100, self.happiness + 10)
        self.energy = max(0, self.energy - 5)
        return self.retu(activ_name)

    def sleep(self):
        activ_name = ("sleep", "đang ngủ 😴", )
        self.happiness = min(100, self.happiness - 5)
        self.energy = min(100, self.energy + 15)
        self.hunger = min(100, self.hunger + 5)
        return self.retu(activ_name)


pet = VirtualPet("Mèo Con")

with gr.Blocks() as demo:
    gr.Markdown("## Thú cưng ảo 🐾")
    timer = gr.Timer(value=10.0)

    output_text = gr.Textbox(label="Trạng thái")
    output_img = gr.Image(label="Hình ảnh thú cưng", value=f"{IMAGE_DIR}{os.sep}base.gif")

    # Tạo ba cột: mỗi cột gồm 1 nút và 1 slider tương ứng
    with gr.Column():
        with gr.Row():
            btn_feed = gr.Button("Feed", scale=2)
            progress_hunger = gr.Slider(0, 100, value=pet.hunger, label="Đói", scale=8)
        with gr.Row():
            btn_play = gr.Button("Play", scale=2)
            progress_happiness = gr.Slider(0, 100, value=pet.happiness, label="Vui vẻ", scale=8)
        with gr.Row():
            btn_sleep = gr.Button("Sleep", scale=2)
            progress_energy = gr.Slider(0, 100, value=pet.energy, label="Năng lượng", scale=8)

    btn_feed.click(fn=pet.feed, inputs=None, outputs=[output_text, output_img, progress_hunger, progress_happiness, progress_energy])
    btn_play.click(fn=pet.play, inputs=None, outputs=[output_text, output_img, progress_hunger, progress_happiness, progress_energy])
    btn_sleep.click(fn=pet.sleep, inputs=None, outputs=[output_text, output_img, progress_hunger, progress_happiness, progress_energy])

    demo.load(
        fn=pet.tick, inputs=None, outputs=[output_text, output_img, progress_hunger, progress_happiness, progress_energy],
    )
    timer.tick(
        fn=pet.tick, inputs=None, outputs=[output_text, output_img, progress_hunger, progress_happiness, progress_energy],
    )

demo.launch(
    # share=True,
)
