# stages/abs_stage.py
from abc import ABC, abstractmethod
from typing import List
import os
import tempfile
import subprocess

def comment_lines(text: str) -> str:
        return "\n".join(f"# {line}" if not line.strip().startswith("#") else line for line in text.splitlines())

class AbsStage(ABC):
    def __init__(self, id: str, description: str = "", final_message: str = ""):
        self.id = id
        self.description = description
        self.final_message = final_message

    def display_intro(self):
        if self.description:
            print(f"=== Stage: {self.id} ===\n{self.description}\n")

    def display_outro(self):
        if self.final_message:
            print(f"\n{self.final_message}\n")

    def get_user_input(self, initial_text: str) -> str:
        """
        Prompt user for input. Options:
        - 'y': accept default text as-is
        - 'e': open editor to modify text
        - Enter: prompt again

        Returns:
            str: the edited text with comment lines stripped
        """
        print(initial_text)
        print("\nEdit options:")
        print("  [y] Accept default text")
        print("  [e] Edit using your default editor")
        print("  [Enter] Prompt again")
        while True:
            user_choice = input("Your choice (y/e/any text): ").strip().lower()

            if user_choice == "y":
                return "y"
            elif user_choice == "":
                continue
            elif user_choice == "e":
                editor = os.environ.get("EDITOR", "vi")
                with tempfile.NamedTemporaryFile(suffix=".tmp", mode="w+", delete=False) as tf:
                    tf.write(comment_lines(initial_text))
                    tf.flush()
                    tf_path = tf.name

                subprocess.call([editor, tf_path])

                with open(tf_path, "r", encoding="utf-8") as tf:
                    edited_text = tf.read()

                os.unlink(tf_path)
                filtered_text = "\n".join(
                    line for line in edited_text.splitlines()
                    if not line.strip().startswith("#")
                )
                return filtered_text.strip()

            else:
                return user_choice

    @abstractmethod
    def run_body(self, provider, messages: List[dict]) -> bool:
        """
        Execute the core logic of the stage.

        Returns:
            bool: True if the tool should proceed to the next stage, False otherwise.
        """
        pass

    def run(self, provider, messages: List[dict]) -> bool:
        """
        Run the full stage including intro, body, and outro.

        Returns:
            bool: Whether to proceed to the next stage.
        """
        self.display_intro()
        should_continue = self.run_body(provider, messages)
        self.display_outro()
        return should_continue
