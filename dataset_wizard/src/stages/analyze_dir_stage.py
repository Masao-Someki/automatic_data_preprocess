# stages/analyze_dir_stage.py
from pathlib import Path
from typing import List

from dataset_wizard.src.analyze_dir import get_markdown
from dataset_wizard.src.stages.abs_stage import AbsStage
from dataset_wizard.src.utils import run_with_spinner


class AnalyzeDirStage(AbsStage):
    def __init__(self):
        super().__init__(
            id="analyze_dir",
            description="Welcome to the Dataset Directory Analyzer!\n"
            "We'll inspect the dataset folder and summarize its structure for "
            "further processing.",
            final_message="✅ Directory structure analysis complete and saved!",
        )

    def run_body(self, provider, messages: List[dict]) -> bool:
        # Ask user where to save analysis
        while True:
            user_input = self.get_user_input("Please enter the directory path you downloaded your dataset:")
            target_dir = Path(user_input) if user_input else self.default_root

            if target_dir and target_dir.exists() and target_dir.is_dir():
                break
            else:
                print(
                    f"\n❌ The path '{target_dir}' is not a valid directory. "
                    "Please try again.\n"
                )

        # Spinner-style indicator
        summary = run_with_spinner(
            get_markdown,
            (target_dir,),
            "Analyzing directory structure, please wait..."
        )

        # Interact with provider
        text = f"""Here is the structure of the dataset directory:

{summary}
"""
        messages.append(
            {
                "role": "user",
                "content": text,
            }
        )
        return messages
