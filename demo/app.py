# Copyright (C) 2025 Xiaomi Corporation
# This software may be used and distributed according to the terms of the Xiaomi Miloco License Agreement.

# modified from https://github.com/XiaomiMiMo/MiMo-VL/blob/main/demo/app.py
import os
import gradio as gr
from infer import MiMoVLMilocoInfer

infer = MiMoVLMilocoInfer(model_path=os.environ.get('CKPT_PATH'))

label_translations = {
    "gr_chatinterface_ofl": {
        "English": "Chatbot",
        "中文": "对话界面"
    },
    "gr_chatinterface_ol": {
        "English": "Chatbot",
        "中文": "对话界面"
    },
    "gr_tab_ol": {
        "English": "Online",
        "中文": "在线模式"
    },
    "gr_tab_ofl": {
        "English": "Offline",
        "中文": "离线模式"
    },
    "gr_temperature": {
        "English": "Temperature",
        "中文": "温度系数"
    },
    "gr_webcam_image": {
        "English": "🤳 Open Webcam",
        "中文": "🤳 打开摄像头"
    },
    "gr_webcam_images": {
        "English": "📹 Recorded Frames",
        "中文": "📹 录制的视频帧"
    },
    "gr_chatinterface_ofl.textbox.placeholder": {
        "English": "Ask me anything. You can also drop in images and .mp4 videos.",
        "中文": "有什么想问的？支持上传图片和.mp4视频。"
    },
    "gr_chatinterface_ol.textbox.placeholder": {
        "English": "Ask me anything...",
        "中文": "有什么想问的？"
    },
    "gr_home_mode": {
        "English": "🏠 Smart Home Mode",
        "中文": "🏠 智能家居模式"
    },
    "gr_clear_btn": {
        "English": "🗑️ Clear All",
        "中文": "🗑️ 清空对话"
    },
    "gr_settings_title": {
        "English": "⚙️ Settings",
        "中文": "⚙️ 设置"
    }
}



def offline_chat(gr_inputs: dict, gr_history: list, infer_history: list, temperature: float, home_mode: bool, reset_flag: bool, lang: str):
    if reset_flag:
        infer_history = []
        first_yield = True
    else:
        first_yield = False
    
    for response_text, new_infer_history in infer(inputs=gr_inputs, history=infer_history, temperature=temperature, home_mode=home_mode, lang=lang):
        if response_text.startswith('<think>') and '</think>' not in response_text:
            # generating reasoning, streaming display
            reasoning_text = response_text.lstrip('<think>')
            response_message = [{
                "role": "assistant",
                "content": reasoning_text,
                'metadata': {'title': '🤔 Thinking'}
            }]
            if first_yield:
                yield response_message, new_infer_history, False
                first_yield = False
            else:
                yield response_message, new_infer_history, False
        elif '<think>' in response_text and '</think>' in response_text:
            # reasoning generated, response starts
            reasoning_text, response_text2 = response_text.split('</think>', 1)
            reasoning_text = reasoning_text.lstrip('<think>')
            response_message = [{
                "role": "assistant",
                "content": reasoning_text,
                'metadata': {'title': '🤔 Thinking'}
            }, {
                "role": "assistant",
                "content": response_text2
            }]
            if first_yield:
                yield response_message, new_infer_history, False
                first_yield = False
            else:
                yield response_message, new_infer_history, False
        else:
            # only response left
            response_message = [{
                "role": "assistant",
                "content": response_text
            }]
            if first_yield:
                yield response_message, new_infer_history, False
                first_yield = False
            else:
                yield response_message, new_infer_history, False


def online_record_chat(text: str, gr_history: list, gr_webcam_images: list, gr_counter: int, infer_history: list, temperature: float, home_mode: bool, reset_flag: bool, lang: str):
    if not gr_webcam_images:
        gr_webcam_images = []
    gr_webcam_images = gr_webcam_images[gr_counter:]
    inputs = {'text': text, 'files': [webp for webp, _ in gr_webcam_images]}
    
    yield f'received {len(gr_webcam_images)} new frames, processing...', gr_counter + len(gr_webcam_images), infer_history, False
    
    for response_message, new_infer_history, new_reset_flag in offline_chat(inputs, gr_history, infer_history, temperature, home_mode, reset_flag, lang):
        yield response_message, gr.skip(), new_infer_history, new_reset_flag


custom_css = """
.settings-container {
    background: linear-gradient(135deg, #FCA12E 0%, #FF6900 100%);
    padding: 0px;
    border-radius: 15px;
    margin-top: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.settings-title {
    color: white;
    font-size: 1.2em;
    font-weight: bold;
    margin-bottom: 15px;
    text-align: center;
}

.control-item {
    background: rgba(255, 255, 255, 0.95);
    padding: 15px;
    border-radius: 10px;
    margin: 8px 0;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-container {
    background: linear-gradient(135deg, #FCA12E 0%, #FF6900 100%);
    padding: 30px;
    border-radius: 15px;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.header-title {
    color: white;
    font-size: 2.5em;
    font-weight: bold;
    text-align: center;
    margin: 0;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
}

.header-subtitle {
    color: rgba(255, 255, 255, 0.9);
    font-size: 1.1em;
    text-align: center;
    margin-top: 10px;
}
"""
# 🏠 
with gr.Blocks(css=custom_css, theme=gr.themes.Soft(primary_hue=gr.themes.colors.orange)) as demo:
    
    with gr.Column(elem_classes="header-container"):
        gr.HTML("""
            <div class="header-title">🏠 Xiaomi MiMo-VL-Miloco</div> 
        """)

    with gr.Column():
        with gr.Row():
            gr_lang_selector = gr.Dropdown(
                choices=["English", "中文"],
                value="English",
                label="🌐 Language / 语言",
                interactive=True,
                min_width=200,
                scale=0
            )

            gr_lang_state = gr.State("English")

        with gr.Tabs():
            # ==================== Offline Tab ====================
            with gr.Tab("📁 Offline", elem_id="tab_offline") as gr_tab_ofl:
                gr_infer_history_ofl = gr.State([])
                gr_reset_flag_ofl = gr.State(False)
                gr_temperature_hidden_ofl = gr.Slider(
                    minimum=0.0, maximum=2.0, step=0.1, value=1.0, interactive=True, visible=False
                )
                gr_home_mode_hidden_ofl = gr.State(value=False)
                
                gr_chatinterface_ofl = gr.ChatInterface(
                    fn=offline_chat,
                    type="messages",
                    multimodal=True,
                    chatbot=gr.Chatbot(
                        height=600, show_copy_button=True, avatar_images=(None, "🤖"), bubble_full_width=False
                    ),
                    textbox=gr.MultimodalTextbox(
                        file_count="multiple", file_types=["image", ".mp4"], sources=["upload"], stop_btn=True,
                        placeholder=label_translations['gr_chatinterface_ofl.textbox.placeholder']['English'],
                    ),
                    additional_inputs=[
                        gr_infer_history_ofl,
                        gr_temperature_hidden_ofl,
                        gr_home_mode_hidden_ofl,
                        gr_reset_flag_ofl,
                        gr_lang_state 
                    ],
                    additional_outputs=[
                        gr_infer_history_ofl,
                        gr_reset_flag_ofl
                    ],
                )
                
                with gr.Group(elem_classes="settings-container"):
                    gr.HTML("""<div class="settings-title">⚙️ Settings</div>""")
                    
                    with gr.Row():
                        with gr.Column(scale=1):
                            gr_home_mode_ofl = gr.Checkbox(
                                label=label_translations['gr_home_mode']['English'],
                                value=False,
                                interactive=True,
                                elem_classes="control-item"
                            )
                        
                        with gr.Column(scale=2):
                            gr_temperature_ofl = gr.Slider(
                                minimum=0.0,
                                maximum=2.0,
                                step=0.1,
                                value=0.4,
                                label=label_translations['gr_temperature']['English'],
                                interactive=True,
                                elem_classes="control-item"
                            )
                        
                        with gr.Column(scale=1):
                            gr_clear_btn_ofl = gr.Button(
                                value=label_translations['gr_clear_btn']['English'],
                                variant="stop",
                                size="lg",
                                elem_classes="control-item"
                            )
                
                gr_temperature_ofl.change(
                    lambda x: x,
                    inputs=gr_temperature_ofl,
                    outputs=gr_temperature_hidden_ofl
                )
                
                def on_home_mode_change_ofl(home_mode):
                    return [], home_mode, True
                
                gr_home_mode_ofl.change(
                    fn=on_home_mode_change_ofl,
                    inputs=[gr_home_mode_ofl],
                    outputs=[
                        gr_infer_history_ofl, 
                        gr_home_mode_hidden_ofl,
                        gr_reset_flag_ofl
                    ]
                ).then(
                    fn=lambda: [],
                    outputs=[gr_chatinterface_ofl.chatbot]
                )
                
                def clear_all_ofl():
                    return [], True
                
                gr_clear_btn_ofl.click(
                    fn=clear_all_ofl,
                    outputs=[gr_infer_history_ofl, gr_reset_flag_ofl]
                ).then(
                    fn=lambda: [],
                    outputs=[gr_chatinterface_ofl.chatbot]
                )

            # ==================== Online Tab ====================
            with gr.Tab("📹 Online", elem_id="tab_online") as gr_tab_ol:
                gr_infer_history_ol = gr.State([])
                gr_reset_flag_ol = gr.State(False)
                gr_temperature_hidden_ol = gr.Slider(
                    minimum=0.0, maximum=2.0, step=0.1, value=1.0, interactive=True, visible=False
                )
                gr_home_mode_hidden_ol = gr.State(value=False)

                with gr.Row():
                    with gr.Column(scale=1):
                    
                        with gr.Group():
                            gr.Markdown("### 📷 Camera Control")
                            gr_webcam_image = gr.Image(
                                label=label_translations['gr_webcam_image']['English'],
                                sources="webcam",
                                height=300,
                                type='filepath'
                            )
                            gr_webcam_images = gr.Gallery(
                                label=label_translations['gr_webcam_images']['English'],
                                show_label=True,
                                format='webp',
                                columns=2,
                                height=300,
                                preview=True,
                                interactive=False
                            )
                            gr_counter = gr.Number(value=0, visible=False)
                            
                    with gr.Column(scale=2):
                        gr_chatinterface_ol = gr.ChatInterface(
                            fn=online_record_chat,
                            type="messages",
                            multimodal=False,
                            chatbot=gr.Chatbot(
                                height=600, show_copy_button=True, avatar_images=(None, "🤖"), bubble_full_width=False
                            ),
                            textbox=gr.Textbox(
                                placeholder=label_translations['gr_chatinterface_ol.textbox.placeholder']['English'],
                                submit_btn=True, stop_btn=True
                            ),
                            additional_inputs=[
                                gr_webcam_images,
                                gr_counter,
                                gr_infer_history_ol,
                                gr_temperature_hidden_ol,
                                gr_home_mode_hidden_ol,
                                gr_reset_flag_ol,
                                gr_lang_state  
                            ],
                            additional_outputs=[
                                gr_counter,
                                gr_infer_history_ol,
                                gr_reset_flag_ol
                            ],
                        )
                
                def cache_webcam(recorded_image: str, recorded_images: list):
                    if not recorded_images:
                        recorded_images = []
                    return recorded_images + [recorded_image]
                
                gr_webcam_image.stream(
                    fn=cache_webcam,
                    inputs=[gr_webcam_image, gr_webcam_images],
                    outputs=[gr_webcam_images],
                    stream_every=1,
                    concurrency_limit=30,
                )
                
                with gr.Group(elem_classes="settings-container"):
                    gr.HTML("""<div class="settings-title">⚙️ Settings</div>""")
                    
                    with gr.Row():
                        with gr.Column(scale=1):
                            gr_home_mode_ol = gr.Checkbox(
                                label=label_translations['gr_home_mode']['English'],
                                value=False,
                                interactive=True,
                                elem_classes="control-item"
                            )
                        
                        with gr.Column(scale=2):
                            gr_temperature_ol = gr.Slider(
                                minimum=0.0,
                                maximum=2.0,
                                step=0.1,
                                value=0.4,
                                label=label_translations['gr_temperature']['English'],
                                interactive=True,
                                elem_classes="control-item"
                            )
                        
                        with gr.Column(scale=1):
                            gr_clear_btn_ol = gr.Button(
                                value=label_translations['gr_clear_btn']['English'],
                                variant="stop",
                                size="lg",
                                elem_classes="control-item"
                            )
                
                gr_temperature_ol.change(
                    lambda x: x,
                    inputs=gr_temperature_ol,
                    outputs=gr_temperature_hidden_ol
                )
                
                def on_home_mode_change_ol(home_mode):
                    return [], 0, [], home_mode, True
                
                gr_home_mode_ol.change(
                    fn=on_home_mode_change_ol,
                    inputs=[gr_home_mode_ol],
                    outputs=[
                        gr_infer_history_ol, 
                        gr_counter,
                        gr_webcam_images,
                        gr_home_mode_hidden_ol,
                        gr_reset_flag_ol
                    ]
                ).then(
                    fn=lambda: [],
                    outputs=[gr_chatinterface_ol.chatbot]
                )
                
                def clear_all_online():
                    return [], 0, [], True
                
                gr_clear_btn_ol.click(
                    fn=clear_all_online,
                    outputs=[
                        gr_infer_history_ol, 
                        gr_counter,
                        gr_webcam_images,
                        gr_reset_flag_ol
                    ]
                ).then(
                    fn=lambda: [],
                    outputs=[gr_chatinterface_ol.chatbot]
                )
                
 
    gr.HTML("""
        <div style="text-align: center; margin-top: 20px; padding: 20px; background: #f5f5f5; border-radius: 10px;">
            <p style="color: #666; margin: 0;">
                💡 <strong>Tips:</strong> Upload images/videos in Offline mode or use webcam in Online mode
            </p>
        </div>
    """)
    
    def update_lang(lang: str):
       
        settings_title = label_translations['gr_settings_title'][lang]
        tips_text = "💡 <strong>提示:</strong> 离线模式支持上传图片/视频，在线模式支持摄像头" if lang == "中文" else "💡 <strong>Tips:</strong> Upload images/videos in Offline mode or use webcam in Online mode"
        
       
        return (
            lang, 
            gr.update(placeholder=label_translations['gr_chatinterface_ofl.textbox.placeholder'][lang]),
            gr.update(placeholder=label_translations['gr_chatinterface_ol.textbox.placeholder'][lang]),
            gr.update(label=("📁 " + label_translations['gr_tab_ofl'][lang])),
            gr.update(label=("📹 " + label_translations['gr_tab_ol'][lang])),
            gr.update(label=label_translations['gr_temperature'][lang]),
            gr.update(label=label_translations['gr_temperature'][lang]),
            gr.update(label=label_translations['gr_webcam_image'][lang]),
            gr.update(label=label_translations['gr_webcam_images'][lang]),
            gr.update(label=label_translations['gr_home_mode'][lang]),
            gr.update(label=label_translations['gr_home_mode'][lang]),
            gr.update(value=label_translations['gr_clear_btn'][lang]),
            gr.update(value=label_translations['gr_clear_btn'][lang]),
        )
    
    gr_lang_selector.change(
        fn=update_lang,
        inputs=[gr_lang_selector],
        outputs=[
            gr_lang_state,
            gr_chatinterface_ofl.textbox,
            gr_chatinterface_ol.textbox,
            gr_tab_ofl,
            gr_tab_ol,
            gr_temperature_ofl,
            gr_temperature_ol,
            gr_webcam_image,
            gr_webcam_images,
            gr_home_mode_ofl,
            gr_home_mode_ol,
            gr_clear_btn_ofl,
            gr_clear_btn_ol,
        ]
    )

demo.queue(default_concurrency_limit=100, max_size=100).launch(
    share=True,
    max_threads=100,
    ssr_mode=False,
    server_port=7869
)
