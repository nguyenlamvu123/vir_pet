from coordinate import gr, os, threading, time, \
    IMAGE_DIR, SHARE, REALTIME, CHANGESTATUSTIME, \
    VirtualPet, thre_hold


pet = VirtualPet("Mèo Con")

with gr.Blocks() as demo:
    gr.Markdown("## Thú cưng ảo 🐾")
    timer = gr.Timer(value=int(CHANGESTATUSTIME))

    output_text = gr.Textbox(label="Trạng thái")
    with gr.Column():
        with gr.Row():
            output_img = gr.Image(label="Hình ảnh thú cưng", value=f"{IMAGE_DIR}{os.sep}base.gif", scale=7)
            with gr.Column():
                with gr.Row(): output_html = gr.HTML(pet.rule, scale=3)
                with gr.Row(): output_alert = gr.Textbox(label="Cảnh báo", lines=10, scale=3)

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

    outputs_list = [output_text, output_img, progress_hunger, progress_happiness, progress_energy, output_alert]

    demo.load(fn=pet.tick, inputs=None, outputs=outputs_list)
    timer.tick(fn=pet.tick, inputs=None, outputs=outputs_list)

demo.launch(
    share=SHARE,
)
