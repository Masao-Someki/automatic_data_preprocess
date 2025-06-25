# stages/generate_dataset_class_stage.py
from dataset_wizard.src.stages.abs_stage import AbsStage
from typing import List
from pathlib import Path
from dataset_wizard.src.utils import load_resource
import inquirer

from dataset_wizard.src.utils import run_with_spinner


class ValidateDatasetClassStage(AbsStage):
    def __init__(self):
        super().__init__(
            id="generate_dataset_class",
            description=(
                "Now we will generate the Python class used to load the dataset you created.\n"
                "This class is responsible for reading the saved dataset files and returning structured examples.\n"
            ),
            final_message="✅ Dataset class successfully generated."
        )

    def run_body(self, provider, messages: List[dict]) -> bool:
        save_path = Path("dataset/dataset.py")
        save_path.parent.mkdir(parents=True, exist_ok=True)

        with open("dataset/create_dataset.py", encoding="utf-8") as f:
            reference_code = f.read()

        messages.append({
            "role": "user",
            "content": (
                "Based on the current conversation so far, I want to generate a `dataset.py`.\n"
                "Please check if any important information is missing to generate it correctly.\n"
                "If anything is missing, list what needs to be clarified.\n"
                ""
                "If nothing is missing, reply only with: All required information is available."
                "\n"
                "**Reference code**\n"
                "```\n" + reference_code + "\n```"
            )
        })
        reply = run_with_spinner(
            provider.chat,
            (messages,),
            "Check if we need more information..."
        )

        while True:
            messages.append({"role": provider.assistant_name, "content": reply})
            if "All required information is available" in reply:
                return messages

            user_response = self.get_user_input(reply)
            messages.append({"role": "user", "content": user_response})

            messages.append({
                "role": "user",
                "content": (
                    "Based on the current conversation so far, I want to generate a `dataset.py`.\n"
                    "Please check if any important information is missing to generate it correctly.\n"
                    "If anything is missing, list what needs to be clarified.\n"
                    "If nothing is missing, reply only with: All required information is available."
                )
            })
            reply = provider.chat(messages)
