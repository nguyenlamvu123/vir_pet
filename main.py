import gradio as gr

class VirtualPet:
    def __init__(self, name):
        self.name = name
        self.hunger = 50
        self.happiness = 50
        self.energy = 50

    def feed(self):
        self.hunger = max(0, self.hunger - 10)
        self.happiness += 5
        return f"{self.name} đang ăn 🍖. Đói: {self.hunger}, Vui vẻ: {self.happiness}", "images/eat.png", self.hunger, self.happiness, self.energy


    def play(self):
        self.happiness += 10
        self.energy -= 5
        return f"{self.name} đang chơi 🎾. Vui vẻ: {self.happiness}, Năng lượng: {self.energy}", "images/play.png", self.hunger, self.happiness, self.energy


    def sleep(self):
        self.energy += 15
        self.hunger += 5
        return f"{self.name} đang ngủ 😴. Năng lượng: {self.energy}, Đói: {self.hunger}", "images/sleep.png", self.hunger, self.happiness, self.energy


pet = VirtualPet("Mèo Con")

def action(choice):
    if choice == "Feed":
        return pet.feed()
    elif choice == "Play":
        return pet.play()
    elif choice == "Sleep":
        return pet.sleep()

with gr.Blocks() as demo:
    gr.Markdown("## Thú cưng ảo 🐾")
    choice = gr.Radio(["Feed", "Play", "Sleep"], label="Chọn hành động")
    output_text = gr.Textbox(label="Trạng thái")
    output_img = gr.Image(label="Hình ảnh thú cưng")

    progress_hunger = gr.Slider(0, 100, value=pet.hunger, label="Đói")
    progress_happiness = gr.Slider(0, 100, value=pet.happiness, label="Vui vẻ")
    progress_energy = gr.Slider(0, 100, value=pet.energy, label="Năng lượng")

    # Khi tick Radio, hàm sẽ tự chạy

    choice.change(
        fn=action,
        inputs=choice,
        outputs=[output_text, output_img, progress_hunger, progress_happiness, progress_energy]
    )

demo.launch()
