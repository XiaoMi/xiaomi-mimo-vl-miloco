# Copyright (C) 2025 Xiaomi Corporation
# This software may be used and distributed according to the terms of the Xiaomi Miloco License Agreement.

# modified from https://github.com/ByteDance-Seed/Seed1.5-VL/blob/main/GradioDemo/infer.py
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration, TextIteratorStreamer
from transformers.generation.stopping_criteria import EosTokenCriteria, StoppingCriteriaList
from qwen_vl_utils import process_vision_info
from threading import Thread
import torch

class MiMoVLMilocoInfer:
    def __init__(self, model_path, device='cuda', torch_dtype=torch.bfloat16, **kwargs):
        self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            model_path, torch_dtype=torch_dtype,  attn_implementation='flash_attention_2', device_map=device,
        )
        self.processor = AutoProcessor.from_pretrained(model_path)
        
        self.system_prompts = {
            "中文": (
                "你是一个智能摄像头助手，专注于分析家庭环境下的视频内容。"
                "你可以识别人物、物体、动作变化以及事件发生顺序，并基于连续的图像序列判断所发生的事件。\n"
                "请你基于我提供的画面内容，准确判断每个场景中发生了什么，并据此回答用户的问题。"
                "你的回答应基于图像事实，避免臆测。\n"
                "我将为你提供一个按时间顺序排列的图像序列（每秒2帧，共6帧）。\n"
                "回复的内容要求以json string格式返回，key值及对应内容如下：\n"
                "1. result: 回答用户提出的问题，确保推理清晰、结论明确，"
                "对于用户判断性问题只可以输出\"是\"或者\"否\";\n"
                "不要返回其他内容。"
            ),
            "English": (
                "You are a smart camera assistant focused on analyzing video content in a home environment."
                "You can identify people, objects, changes in actions, and the sequence of events, and determine what happened based on a continuous sequence of images.\n"
                "Please accurately determine what happened in each scene based on the provided footage and answer the user's questions accordingly."
                "Your answers should be based on factual image content, avoiding speculation.\n"
                "I will provide you with a chronologically ordered image sequence (2 frames per second, 6 frames in total).\n"
                "The response must be returned in json string format, with the following key and corresponding content:\n"
                "1. result: Answer the user's question, ensuring clear reasoning and a definite conclusion. "
                "For user's yes/no questions, you can only output \"Yes\" or \"No\";\n"
                "Do not return any other content."
            )
        }
    
    def __call__(self, inputs: dict, history: list = [], temperature: float = 1.0, home_mode: bool = False, lang: str = "English"):
        messages = self.construct_messages(inputs, home_mode, lang)
        updated_history = history + messages
        
        text = self.processor.apply_chat_template(
            updated_history,
            tokenize=False,
            add_generation_prompt=True
        )
        image_inputs, video_inputs = process_vision_info(updated_history)
        
        model_inputs = self.processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors='pt'
        ).to(self.model.device)
        
        tokenizer = self.processor.tokenizer
        streamer = TextIteratorStreamer(
            tokenizer,
            timeout=20.0,
            skip_prompt=True,
            skip_special_tokens=True
        )
        
        gen_kwargs = {
            'max_new_tokens': 16000,
            'streamer': streamer,
            'stopping_criteria': StoppingCriteriaList([
                EosTokenCriteria(eos_token_id=self.model.config.eos_token_id)
            ]),
            'pad_token_id': self.model.config.eos_token_id,
            **model_inputs
        }
        
        thread = Thread(target=self.model.generate, kwargs=gen_kwargs)
        thread.start()
        
        partial_response = ""
        for new_text in streamer:
            partial_response += new_text
            yield partial_response, updated_history + [{
                'role': 'assistant',
                'content': [{
                    'type': 'text',
                    'text': partial_response
                }]
            }]
    
    def _is_video_file(self, filename):
        video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.mpeg']
        return any(filename.lower().endswith(ext) for ext in video_extensions)
    
    def construct_messages(self, inputs: dict, home_mode: bool = False, lang: str = "English") -> list:
        messages = []
        
        if home_mode:
            system_prompt = self.system_prompts.get(lang, self.system_prompts["English"])
            messages.append({
                "role": "system",
                "content": [{
                    "type": "text",
                    "text": system_prompt
                }]
            })
        
        content = []
        for i, path in enumerate(inputs.get('files', [])):
            if self._is_video_file(path):
                content.append({
                    "type": "video",
                    "video": f'file://{path}'
                })
            else:
                content.append({
                    "type": "image",
                    "image": f'file://{path}'
                })
        
        query = inputs.get('text', '')
        if query:
            content.append({
                "type": "text",
                "text": query,
            })
        
        messages.append({
            "role": "user",
            "content": content,
        })
        
        return messages

