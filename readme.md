# 🧙 Dataset Wizard

A CLI-based interactive assistant to help you define, configure, and implement custom datasets (e.g., Hugging Face or Lhotse) from raw files such as audio, transcription, and metadata.  
The tool guides you through a **stage-based workflow** to create high-quality, structured datasets step by step — with the help of an LLM (e.g., ChatGPT or Gemini).

---

## ✨ Features

- 📁 **Automatic dataset structure analysis**
- 💬 **LLM-powered requirement discussion**
- ✍️ **Editable stage prompts using your `$EDITOR`**
- 🧠 **Smart suggestions from AI (field layout, splits, formats)**
- 🛠️ **Code generation for dataset creation**
- 🧪 **Dataset class scaffolding**
- 📦 **Hugging Face / Lhotse support**
- 💾 **Logs interaction history as Markdown & JSON**
- 🧱 **Modular stage-based architecture (easy to extend)**

---

## 🏁 Quickstart

### 1. Install the tool

```bash
git clone https://github.com/yourname/dataset-wizard.git
cd dataset-wizard
pip install -e .
````

> This registers a `dataset-wizard` command globally on your system.

---

### 2. Set your API keys

Set one or both of the following environment variables (only one is required):

```bash
export OPENAI_API_KEY=sk-...
# or
export GOOGLE_API_KEY=your-gemini-api-key
```

You can also use `.env` with `python-dotenv`.

---

### 3. Run the wizard

```bash
dataset-wizard
```

The wizard will guide you through several stages:

| Stage ID               | Purpose                                                 |
| ---------------------- | ------------------------------------------------------- |
| `analyze_dir`          | Analyze your dataset directory structure                |
| `define_dataset`       | Decide what each sample should contain (audio, text...) |
| `define_datasetdict`   | Configure splits and output path for the DatasetDict    |
| `generate_dataset`     | Generate Python code to create the dataset              |
| `define_dataset_class` | Scaffold a custom Dataset class                         |

---

## 📁 Example Output

* `dataset/create_dataset.py` — generated dataset builder script
* `dataset/dataset.py` — dataset class to load your data
* `results/result.json` — interaction history (raw message objects)
* `results/result.md` — human-readable summary of the conversation

---

## 🧩 Project Structure

```
dataset_wizard/
├── dataset_wizard/
│   ├── cli.py              # Entry point
│   ├── stages/             # All stages (e.g., analyze_dir.py)
│   ├── providers/          # Provider APIs (OpenAI, Gemini, etc.)
│   └── utils/              # Editor, spinner, save utils, etc.
├── prompts/                # User-facing prompts (001-*.md)
├── resources/              # Code templates (HF/Lhotse)
├── results/                # Saved logs (JSON + MD)
├── setup.py
└── README.md
```

---

## 🧠 Extending the Wizard

You can define your own stages by inheriting from `AbsStage`:

```python
class MyCustomStage(AbsStage):
    def run_body(self, provider, messages: List[dict]) -> bool:
        # implement your stage logic
        return True
```

And register them in your `cli.py`'s stage list.

---

## 🗂️ Supported Dataset Backends

| Backend      | Recommended Use Case                                  |
| ------------ | ----------------------------------------------------- |
| Hugging Face | Simple segmented audio datasets with paired text      |
| Lhotse       | Long audio with segment-level extraction requirements |
| Custom       | Specify your own create\_dataset.py as a reference    |

---

## 📜 License

MIT License

---

## 🙏 Acknowledgements

Built with ❤️ by Masao Someki, powered by OpenAI and Google Gemini.
