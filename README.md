<div align="center">
  <picture>
    <source srcset="https://github.com/XiaomiMiMo/MiMo-VL/raw/main/figures/Xiaomi_MiMo_darkmode.png?raw=true" media="(prefers-color-scheme: dark)">
    <img src="./figures/logo.png" width="60%" alt="Xiaomi-MiMo-Vl-Miloco" />
  </picture>
</div>

<br/>

<div align="center" style="line-height: 1;">
  <a href="https://huggingface.co/xiaomi-open-source/Xiaomi-MiMo-VL-Miloco" target="_blank">🤗 HuggingFace</a>
  &nbsp;|
  <a href="https://modelscope.cn/models/williamljz" target="_blank">🤖️ ModelScope</a>
  &nbsp;|
 <a href="#gradio-demo">🔥 Gradio Demo</a>
  <br/>
</div>

<br/>


## 🔥🔥🔥 News
* 2025.11.14: We have released the [**MiMo-VL-Miloco-7B**](https://huggingface.co/xiaomi-open-source/Xiaomi-MiMo-VL-Miloco) and [**MiMo-VL-Miloco-7B-GGUF**](https://huggingface.co/williamljz/test2_gguf). Enjoy it!



## Introduction

Welcome to MiMo-VL-Miloco-7B — the first open-source multimodal model built to actually understand what’s happening at home!

### 🤗 Why you’ll love it:
- Built on MiMo-VL-7B: a rock-solid vision–language backbone with reliable video understanding and instruction-following.
- Home-savvy by design: it spots everyday activities (esports, workouts, watching TV, reading, and more) and reads common hand gestures like the V sign, thumbs-up, open palm, OK, and even the shaka hand sign.
- Base skills intact: with a mix training strategy of SFT and RL, we boost home-scene smarts while keeping the model’s generality and transferability in great shape.

### 🌟 Training recipe:

We use a carefully tuned two-stage pipeline to nail home-scene skills without sacrificing general abilities.

#### Stage 1: Supervised Fine-Tuning (SFT)

This stage focuses on boosting the model’s core capabilities in home scenarios. Even with a limited training set, we strike a good balance between sample-efficient learning and fast inference:

- Chain-of-thought supervision: we add chain of reasoning so the model learns structured knowledge about home scenarios.
- Token-budget-aware reasoning: training with “budgeted” reasoning encourages concise, straight-to-the-point answers at inference.

#### Stage 2: Reinforcement Learning (RL)

Building on fine-tuning, this stage introduces GRPO-based reinforcement learning to enhance the model’s overall performance:

- Efficient Training Data: we employed the Time-R1 data strategy (accepted at NeurIPS 2025) to build efficient training datasets across multiple domains.
- Keep-it-general: specialize for home tasks while preserving broad understanding and language generation.

In short: MiMo-VL-Miloco-7B is your friendly, sharp-eyed model roommate—great at recognizing what’s going on around the house, and still ready for the wider world.

### 😉 Model Recomendation

Both versions of the MiMo-VL-Miloco-7B model are now open-sourced:  
- #### [**MiMo-VL-Miloco-7B**](https://huggingface.co/xiaomi-open-source/Xiaomi-MiMo-VL-Miloco)
  - Recommended for most users to experience and utilize.  
- #### [**MiMo-VL-Miloco-7B-GGUF**](https://huggingface.co/williamljz/test2_gguf)
  - This is the mixed-precision quantized version of MiMo-VL-Miloco-7B. It is recommended for evaluation and use in compute-constrained environments.

## Performance

### Evaluation of Home-Scenario Capabilities (F1 Score)
<div align="center">
  <picture>
    <img src="figures/radar.png" width="90%" alt="Accuracy & Recall" />
  </picture>
</div>

### Results of general capability evaluations
<div align="center">
  <picture>
    <img src="figures/results.png" width="90%" alt="Accuracy & Recall" />
  </picture>
</div>


## Deployment

### Thinking Control

We follow the same approach as MiMo-VL. Users can control the thinking mode by appending ```/no_think``` to queries:

- Thinking mode (default):
  ```bash
  "Explain the relationships between the objects in the image and infer the likely next action."
  ```
- Non-thinking mode:
  ``` bash
  "Transcribe the handwritten note exactly as shown. /no_think"
  ```

### Gradio Demo
- Installation

```bash
pip install -r requirements.txt
```

- Deployment

```bash
cd demo
CKPT_PATH="checkpoint_path" python app.py
```


### Mode Switching
In the interface, you can click Smart Home mode to switch to the home scenario mode.
<div align="center">
  <picture>
    <img src="figures/gradio_demo.png" width="90%" alt="Accuracy & Recall" />
  </picture>
</div>