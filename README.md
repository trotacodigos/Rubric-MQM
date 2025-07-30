# Rubric-MQM

**LLM-as-Judge for High-End Machine Translation Evaluation**

---

## About

**RUBRIC-MQM** is a modular, span-level MT evaluation framework that uses **LLMs to detect MQM-style translation errors** and compute **rubric-based scores (0–100)** at the span level. It improves upon [GEMBA-MQM (Kocmi & Federmann, 2023)](https://github.com/MicrosoftTranslator/GEMBA) by addressing newly discovered issues such as:

- Overuse of _MISTRANSLATION_ and _MAJOR_ labels  
- Systematic failure of _NO-ERROR_ cases  
- Spurious category generation

<figure>
    <img src="data/images/compare.png", alt="GEMBA vs. Rubric", width="500">
    <figcaption>Figure 1: Six advantages of Rubric-MQM, addressing existing challenges of GEMBA-MQM. 'Major' and Mistranslation indicate precision, while 'No-error' refers to recall score.
</figure>

### 
Furthermore, when assessing reference translations, RubricMQM demonstrates a markedly enhanced correlation, highlighting its robustness when applied to high-performing models (Figure 2). Figure 3 also presents a novel evaluation insight, indicating that RubricMQM is capable of providing a new system-level result (in this case, for _Reference A_).

<p align="center">
    <img src="data/images/correlation.png" alt="Comparison" style="width:50%; height:auto;">
</p>
<p align="center">
    Figure 2: Segment-level correlations to DA-SQM.
</p>

<p align="center">
    <img src="data/images/new_result.png" alt="New Finding" style="width:50%; height:auto;">
</p>
<p align="center">
    Figure 3. System-level score of "Reference A" (-716.54).
</p>


---

## Core Capabilities

- **Span-level labeling** — Error classification with span localization  
- **Rubric scoring** — Numerical quality estimation (1–100) based on prompt-based scoring criteria  
- **Reference-optional** — Works with or without gold references  
- **Multilingual & few-shot friendly** — Adaptable prompts for non-English use cases  
- **Batch processing** — Scales across datasets via CLI or pipeline  
- **Easy application of PromptCUE** — Our meta-evaluation strategy that frames evaluation as a classification task, enabling error profiling without error detection heuristics.

---

## Installation

```bash
git clone https://github.com/trotacodigos/Rubric-MQM.git
cd Rubric-MQM

# Create a new virtual environment and install
pip install -r requirements.txt
pip install -e .
```
  
---

## Quick Start

### 1. Python Implementation
```python
# Check if the version of openai >= 1.0
import openai
print(openai.__version__)

from rubric_mqm.worker import run_rmqm_eval

# Introduce your keys
your_api_keys = [key1, key2, ...]

# Run evaluation
run_rmqm_eval("data/sample.csv",
              "data/out.csv",
              "data/error.jsonl",
               api_keys=your_api_keys,
               model="gpt-4.1-mini")

```

---

### 2. CLI Implementation
Create an .env file and save your OpenAI API keys. Make sure they’re comma-separated without space.
```bash
OPENAI_API_KEYS=sk-key1,sk-key2,sk-key3...
```

Then, test the module with sample data.
```bash
rubric_mqm -d data/sample.csv \
           -o data/out.csv \
           -e data/error.jsonl \
           -m "gpt-4.1-mini" \
           -p  # Enable PromptCUE mode
```

### Sample Instance

|||
|-|-|
|Chinese Source|综合韩国“朝鲜新闻”等报导，金正恩、李雪主夫妇7日带著女儿金主爱出席晚宴的官方合照中，金主爱不仅罕见坐在父母正中间C位，在隔日晚间建军节第75周年阅兵仪式上，她还与金正恩一起登上主席台。|
|English Translation|In the official photo of Kim Jong-un and his wife Ri Sol Ju at a dinner party with their daughter Kim Jong-un, Kim Jong-un not only rarely sits in the middle C of their parents, but also sits on the podium with Kim Jong-un at the 75th anniversary military parade the next evening.|
|RubricMQM Review|"Kim Jong-un" - mistranslation - 80|
||"Kim Jong-un" - inconsistency - 63|
||"C位" - untranslated text - 65|
||"their parents" - mistranslation - 78|
||"sits on the podium with Kim Jong-un" - inconsistency - 70|
|Score|-291 (or -2.91)|


The answers are organized in the given format:
```python
"{'cat_pred': ['mistranslation', 'inconsistency', 'mistranslation', 'inconsistency'], 'sev_pred': [80, 63, 78, 70], 'score': -2.91}"
```
---

## Directory Structure

```
Rubric_MQM/
├── rubric_mqm/
│   ├── slot_scenarios/        # Prebuilt prompt variations
│   ├── worker.py              # CLI entrypoint for evaluation
│   ├── prompt.py              # Prompt logic and rubric templates
│   ├── promptcue.py           # PromptCUE mode
│   ├── call_api.py
│
├── rmqm_parser/               # Output parsing utilities
│
├── data/                      # Input/output examples
│
├── requirements.txt
├ ...
│
└── README.md
```

---

## 🔖 Citation
Check our paper [here](https://aclanthology.org/2025.acl-industry.12/)!

```bibtex
@inproceedings{kim-2025-rubric,
    title = "{RUBRIC}-{MQM} : Span-Level {LLM}-as-judge in Machine Translation For High-End Models",
    author = "Kim, Ahrii",
    editor = "Rehm, Georg  and
      Li, Yunyao",
    booktitle = "Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 6: Industry Track)",
    month = jul,
    year = "2025",
    address = "Vienna, Austria",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2025.acl-industry.12/",
    pages = "147--165",
    ISBN = "979-8-89176-288-6",
    abstract = "Referred to as $\textit{LLM-as-judge}$, a generative large language model (LLM) has demonstrated considerable efficacy as an evaluator in various tasks, including Machine Translation (LAJ-MT) by predicting scores or identifying error types for individual sentences. However, its dependability in practical application has yet to be demonstrated, as there is only an $\textit{approximated match}$ due to the task{'}s open-ended nature. To address this problem, we introduce a straightforward and novel meta-evaluation strategy $\textbf{PromptCUE}$ and evaluate cutting-edge LAJ-MT models such as GEMBA-MQM. We identify their fundamental deficits, including certain label biases and the inability to assess near-perfect translations.To improve reliability, we investigate more trustworthy and less biased models using multidimensional prompt engineering. Our findings indicate that the combination of span-level error quantification and a rubric-style prompt tailored to the characteristics of LLMs has efficiently addressed the majority of the challenges current LAJ-MT models face. Furthermore, it demonstrates a considerably enhanced alignment with human values. Accordingly, we present $\textbf{Rubric-MQM}$, the LAJ-MT for high-end models and an updated version of GEMBA-MQM."
}

@article{kim2025dr100,
  author       = {Ahrii Kim},
  title        = {{DR-100: Rubric-Based LLM-as-Judge in Machine Translation Via a Simple Meta-Evaluation Framework}},
  journal      = {TechRxiv},
  year         = {2025},
  month        = {April},
  day          = {28},
  doi          = {10.36227/techrxiv.174584742.28568002/v1},
  url          = {https://doi.org/10.36227/techrxiv.174584742.28568002/v1},
  note         = {Preprint}
}
```

---

## 📄 License

MIT License (see [`LICENSE`](LICENSE))
