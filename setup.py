from setuptools import setup, find_packages

setup(
    name="dataset-wizard",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai",
        "google-generativeai",
        "rich",
    ],
    entry_points={
        "console_scripts": [
            "dataset-wizard=dataset_wizard.cli:main", 
        ],
    },
    include_package_data=True,
    description="CLI assistant for building Hugging Face or Lhotse datasets",
)
