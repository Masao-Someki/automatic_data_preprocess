import argparse
import json
from pathlib import Path
import os

from dataset_wizard.src.providers.openai_provider import OpenAIProvider
from dataset_wizard.src.providers.gemini_provider import GeminiProvider
from dataset_wizard.src.utils import load_resource
from dataset_wizard.src.stages.analyze_dir_stage import AnalyzeDirStage
from dataset_wizard.src.stages.define_dataset_stage import DefineDatasetStage
from dataset_wizard.src.stages.define_datasetdict_stage import DefineDatasetDictStage
from dataset_wizard.src.stages.generate_dataset_code_stage import GenerateDatasetCodeStage
from dataset_wizard.src.stages.validate_dataset_info_stage import ValidateDatasetInfoStage
from dataset_wizard.src.stages.validate_dataset_class import ValidateDatasetClassStage
from dataset_wizard.src.stages.generate_dataset_class_stage import GenerateDatasetClassStage

DEFAULT_PROVIDER = "openai"
DEFAULT_MODEL = "o4-mini-2025-04-16"

PROVIDER_REGISTRY = {
    "openai": OpenAIProvider,
    "gemini": GeminiProvider,
}


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def auto_detect_provider() -> str:
    openai_key = os.environ.get("OPENAI_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if openai_key and not gemini_key:
        return "openai"
    elif gemini_key and not openai_key:
        return "gemini"
    else:
        return None  # ambiguous or missing


def save_results(messages, output_dir="dataset", base_filename="result"):
    """
    Save chat messages to both JSON and Markdown formats.

    Args:
        messages (List[dict]): list of {"role": ..., "content": ...} dicts
        output_dir (str): directory to save files in
        base_filename (str): base name (without extension) for saved files
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save as JSON (raw message format)
    json_path = output_dir / f"{base_filename}.json"
    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump(messages, jf, indent=2, ensure_ascii=False)

    # Save as Markdown (human-readable)
    md_path = output_dir / f"{base_filename}.md"
    with open(md_path, "w", encoding="utf-8") as mf:
        for msg in messages:
            role = msg.get("role", "unknown").capitalize()
            content = msg.get("content", "").strip()
            mf.write(f"**{role}**:\n\n{content}\n\n---\n\n")

    print(f"✅ Saved results to:\n  - {json_path}\n  - {md_path}")


def main():
    parser = argparse.ArgumentParser(
        description="CLI tool for chatting with AI via staged prompts."
    )
    parser.add_argument(
        "--provider", default=None, help="Provider name (e.g., openai, gemini)"
    )
    parser.add_argument(
        "--model", default=DEFAULT_MODEL, help="Model name (e.g., gpt-4o, gemini-pro)"
    )
    args = parser.parse_args()

    provider_name = args.provider or auto_detect_provider() or DEFAULT_PROVIDER
    provider_cls = PROVIDER_REGISTRY.get(provider_name)
    if provider_cls is None:
        raise ValueError(f"Unknown provider: {provider_name}")
    provider = provider_cls(model=args.model)

    # Define stages
    stages = [
        AnalyzeDirStage(),
        DefineDatasetStage(),
        DefineDatasetDictStage(),
        ValidateDatasetInfoStage(),
        GenerateDatasetCodeStage(),
        ValidateDatasetClassStage(),
        GenerateDatasetClassStage(),
    ]

    messages = []
    # The very initial system prompt
    messages.append(
        {
            "role": "user",
            "content": load_resource("system_prompt.md"),
        }
    )
    clear_screen()
    for stage in stages:
        messages = stage.run(provider, messages)

    save_results(messages)

if __name__ == "__main__":
    main()
