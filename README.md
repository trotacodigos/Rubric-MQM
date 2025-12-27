<p align="center">
    <img src="data/images/logo.png" alt="Comparison" style="width:40%; height:auto;">
</p>


**Rubric-MQM** is a **rubric-driven automatic post-editing (APE) framework**
for machine translation outputs,
built on span-level error diagnosis using large language models.

# ✺ Features
Given a source sentence and its translation (optionally with a reference),
Rubric-MQM uses a large language model to:

- detect translation errors at the **span level**
- classify each error using **MQM-style categories**
- assign severity scores
- generate **targeted post-edited suggestions**

While Rubric-MQM primarily operates as an **APE system**,
it remains fully compatible with **LLM-as-Judge pipelines** by producing
structured span-level error labels, severities, and judgment outputs
that can be reused for evaluation-oriented analysis.

# 🗞️ News
- **Dec 26, 2025 — v2.0 released**  
  Rubric-MQM has been refactored from an *LLM-as-Judge evaluation metric*  
  into a **fully functional APE engine**,  
  featuring JSONL-driven prompts, environment-based API key management,  
  and a simplified `git clone → run` workflow.

- **July 28–30, 2025 — ACL 2025**  
  The original LLM-as-Judge framework of Rubric-MQM was presented at  
  the Annual Meeting of the Association for Computational Linguistics (ACL 2025).

- **May 26, 2025 - v1.0 released**   
  Rubric-MQM has been suggested as an LLM-as-judge metric in Machine Translation.


# ✺ Quick Start

### ➡ Set your OpenAI API key
```bash
export OPENAI_API_KEY=sk-xxxx
# or
export OPENAI_API_KEYS=sk-key1,sk-key2
```

### ➡ Configuration
- `--mode`: Choose which mode to run — APE or LLM-as-Judge
- `--config`: Baseline selection and decoding parameters are fully configurable via YAML.

#### APE vs. Judge ⁉️
- **APE mode (--mode ape)**
: Returns post-edited text suitable for direct integration into MT pipelines.

- **Judge mode (--mode judge)**
: Produces LLM-as-Judge compatible outputs (error categories, severities, scores),
enabling reuse in existing evaluation workflows and prior experiments.

```bash
# Automatic Post-Editing
python -m metric.run \
  --input data/sample.csv \
  --mode ape \
  --output data/v2/ape_out.jsonl \
  --config metric/config/default.yaml \
  --workers 2

# LLM-as-Judge compatible evaluation
python -m metric.run \
  --input data/sample.csv \
  --mode judge \
  --output data/v2/judge_out.jsonl \
  --config metric/config/default.yaml \
  --workers 2
```

### ➡ Prepare your data
Input data must be provided as a CSV file. The required columns for all modes are:
- src_lang
- tgt_lang
- src_text
- target

The rest items are optional.

|||||||
|-|-|-|-|-|-|
|src_lang|tgt_lang|src_text|**target**|ref_text|domain|
|...|...|...|...|...|...|


# ✺ Sample Outputs
Output data can be either a JSONL or CSV file.

|||
|-|-|
|Chinese Source|综合韩国“朝鲜新闻”等报导，金正恩、李雪主夫妇7日带著女儿金主爱出席晚宴的官方合照中，金主爱不仅罕见坐在父母正中间C位，在隔日晚间建军节第75周年阅兵仪式上，她还与金正恩一起登上主席台。|
|English Translation|In the official photo of Kim Jong-un and his wife Ri Sol Ju at a dinner party with their daughter Kim Jong-un, Kim Jong-un not only rarely sits in the middle C of their parents, but also sits on the podium with Kim Jong-un at the 75th anniversary military parade the next evening.|
|🤖 Judge|"Kim Jong-un" - mistranslation - 80|
||"Kim Jong-un" - inconsistency - 63|
||"C位" - untranslated text - 65|
||"their parents" - mistranslation - 78|
||"sits on the podium with Kim Jong-un" - inconsistency - 70|
|(score)|-291 (or -2.91)|
|🤖 APE|In the official photo of Kim Jong-un and Ri Sol Ju at a dinner party with their daughter Kim Joo-ae, Kim Joo-ae is not only rarely sitting in the middle C of their parents, but also stood on the rostrum with Kim Jong-un at the 75th anniversary military parade the next evening.|


# ✺ What Rubric-MQM Provides

- **Span-level error detection** — pinpointing exact erroneous segments  
- **MQM-style classification** — standardized error categories  
- **Post-editing suggestions** — minimal, localized fixes (not rewrites)  
- **Reference-optional** — works with or without gold references  
- **Multilingual & few-shot ready** — JSONL-based prompt and ICL design  
- **Batch post-editing** — scalable processing for real-world MT outputs  
- **PromptCUE integration** — structured error profiling without heuristics
- **LLM-as-Judge compatible outputs** — structured error labels and scores
  that can be directly consumed by existing evaluation pipelines

It improves upon [GEMBA-MQM (Kocmi & Federmann, 2023)](https://github.com/MicrosoftTranslator/GEMBA) by addressing newly discovered issues such as:

- Overuse of _MISTRANSLATION_ and _MAJOR_ labels  
- Systematic failure of _NO-ERROR_ cases  
- Spurious category generation

<figure>
    <img src="data/images/compare.png", alt="GEMBA vs. Rubric", width="500">
    <figcaption>Figure 1: Six advantages of Rubric-MQM, addressing existing challenges of GEMBA-MQM.
    'Major' and Mistranslation indicate precision, while 'No-error' refers to recall score.
</figure>

### 
Furthermore, when assessing reference translations, RubricMQM demonstrates a markedly enhanced correlation, highlighting its robustness when applied to high-performing models (Figure 2). Figure 3 also presents a novel evaluation insight, indicating that RubricMQM is capable of providing a new system-level result (in this case, for _Reference A_).

<p align="center">
    <img src="data/images/correlation.png" alt="Comparison" style="width:40%; height:auto;">
    &nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp
    <img src="data/images/new_result.png" alt="New Finding" style="width:40%; height:auto;">
</p>
<p align="center">
    Figure 2: Segment-level correlations to DA-SQM.
    &nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp
    Figure 3. System-level score of "Reference A" (-716.54).
</p>

# ✺ Directory Structure

```
Rubric-MQM/
├── metric/
│   ├── core/
│   │   └── engine.py          # Shared core engine (LLM call + parsing)
│   │
│   ├── modules/
│   │   ├── ape.py             # Automatic Post-Editing (APE) interface
│   │   └── judge.py           # LLM-as-Judge compatible interface
│   │
│   ├── prompt/
│   │   ├── templates.jsonl    # Prompt instructions
│   │   ├── icl_examples.jsonl # Few-shot ICL examples
│   │   └── fewshot.py         # Message construction logic
│   │
│   ├── parser/
│   │   └── parse.py           # Response parsing & normalization
│   │
│   ├── utils/
│   │   └── utils.py           # Shared utilities
│   │
│   ├── config/
│   │   └── default.yaml       # Default runtime configuration
│   │
│   ├── run.py                 # CLI entry point (APE / Judge switch)
│   └── __init__.py
│
├── data/
│   ├── sample.csv             # Example input data
|   ├── v1/                    # Dataset for v1.0
│   └── v2/                    # Dataset for v2.0
│
├── requirements.txt
├── README.md
└── LICENSE
```


# ✺ Citation
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
```


# License

MIT License (see [`LICENSE`](LICENSE))
