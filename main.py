from coordinate import gr, os, threading, time, \
    IMAGE_DIR, SHARE, REALTIME, CHANGESTATUSTIME, \
    VirtualPet, thre_hold


pet = VirtualPet("Bé Mai")

def game_over_controller():
    # 1. Gọi hàm tick gốc của bạn (nhận về đúng 7 giá trị)
    text, img, hunger, happiness, energy, ale, current_audio = pet.tick()

    # 2. KIỂM TRA ĐIỀU KIỆN: Nếu âm thanh trả về là None -> Ẩn 3 nút bấm
    if current_audio is None:
        return (
            "Nước mắt tuôn rơi, Trò chơi kết thúc 😢",
            img, hunger, happiness, energy,
            ale,  # "Gameover.",
            None,  # Không phát âm thanh
            gr.update(visible=False),  # Ẩn nút btn_feed
            gr.update(visible=False),  # Ẩn nút btn_play
            gr.update(visible=False)  # Ẩn nút btn_sleep
        )

    # 3. Nếu vẫn còn âm thanh trong hàng đợi -> Giữ nguyên các nút bấm bình thường
    return (
        text, img, hunger, happiness, energy, ale, current_audio,
        gr.update(visible=True),
        gr.update(visible=True),
        gr.update(visible=True)
    )

def ui_reset_handler():
    # 1. Gọi hàm reset logic của pet để lấy các chỉ số mặc định (7 phần tử)
    text, img, hunger, happiness, energy, ale, audio = pet.reset()

    # 2. Trả về kèm theo lệnh ép hiển thị lại (visible=True) cho 3 nút bấm cứu trợ
    return (
        text, img, hunger, happiness, energy, ale, audio,
        gr.update(visible=True),  # Hiện lại nút Feed
        gr.update(visible=True),  # Hiện lại nút Play
        gr.update(visible=True)  # Hiện lại nút Sleep
    )

with gr.Blocks() as demo:
    gr.Markdown("## Bé ảo 🐾")
    timer = gr.Timer(value=int(CHANGESTATUSTIME))

    output_text = gr.Textbox(label="Trạng thái")
    with gr.Column():
        with gr.Row():
            output_img = gr.Image(label="Hình ảnh bé", value=f"{IMAGE_DIR}{os.sep}base.gif", scale=7)
            with gr.Column():
                with gr.Row(): output_html = gr.HTML(pet.rule, scale=3)
                with gr.Row(): output_alert = gr.Textbox(label="Cảnh báo", lines=3, scale=5)
                with gr.Row(): output_audio = gr.Audio(label="Âm thanh cảnh báo", type="filepath", autoplay=True)  # , visible=False)

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

        with gr.Row():
            btn_reset = gr.Button("🔄 Reset Game", variant="primary", scale=10)

    btn_feed.click(fn=pet.feed, inputs=None, outputs=[output_text, output_img, progress_hunger, progress_happiness, progress_energy])
    btn_play.click(fn=pet.play, inputs=None, outputs=[output_text, output_img, progress_hunger, progress_happiness, progress_energy])
    btn_sleep.click(fn=pet.sleep, inputs=None, outputs=[output_text, output_img, progress_hunger, progress_happiness, progress_energy])

    outputs_list = [output_text, output_img, progress_hunger, progress_happiness, progress_energy, output_alert, output_audio, btn_feed, btn_play, btn_sleep]

    btn_reset.click(fn=ui_reset_handler, inputs=None, outputs=outputs_list)
    demo.load(fn=game_over_controller, inputs=None, outputs=outputs_list)
    timer.tick(fn=game_over_controller, inputs=None, outputs=outputs_list)

demo.launch(
    share=SHARE,
)
