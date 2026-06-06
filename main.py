import gradio as gr

class VirtualPet:
    def __init__(self, name):
        self.name = name
        self.hunger = 50
        self.happiness = 50
        self.energy = 50

    def feed(self):
        self.hunger = max(0, self.hunger - 10)
        self.happiness = min(100, self.happiness + 5)
        return f"{self.name} đang ăn 🍖", "images/eat.png", self.hunger, self.happiness, self.energy

    def play(self):
        self.happiness = min(100, self.happiness + 10)
        self.energy = max(0, self.energy - 5)
        return f"{self.name} đang chơi 🎾", "images/play.png", self.hunger, self.happiness, self.energy

    def sleep(self):
        self.energy = min(100, self.energy + 15)
        self.hunger = min(100, self.hunger + 5)
        return f"{self.name} đang ngủ 😴", "images/sleep.png", self.hunger, self.happiness, self.energy


pet = VirtualPet("Mèo Con")

with gr.Blocks() as demo:
    gr.Markdown("## Thú cưng ảo 🐾")

    output_text = gr.Textbox(label="Trạng thái")
    output_img = gr.Image(label="Hình ảnh thú cưng")

    progress_hunger = gr.Slider(0, 100, value=pet.hunger, label="Đói")
    progress_happiness = gr.Slider(0, 100, value=pet.happiness, label="Vui vẻ")
    progress_energy = gr.Slider(0, 100, value=pet.energy, label="Năng lượng")

    btn_feed = gr.Button("Feed")
    btn_play = gr.Button("Play")
    btn_sleep = gr.Button("Sleep")

    btn_feed.click(fn=pet.feed, inputs=None, outputs=[output_text, output_img, progress_hunger, progress_happiness, progress_energy])
    btn_play.click(fn=pet.play, inputs=None, outputs=[output_text, output_img, progress_hunger, progress_happiness, progress_energy])
    btn_sleep.click(fn=pet.sleep, inputs=None, outputs=[output_text, output_img, progress_hunger, progress_happiness, progress_energy])

demo.launch(
    # share=True,
)
