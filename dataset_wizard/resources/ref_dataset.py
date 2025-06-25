import numpy as np
from lhotse import CutSet
from torch.utils.data import Dataset
from datasets import load_from_disk, Audio



class HuggingfaceDataset(Dataset):
    def __init__(self, data_dir='data/', split=None):
        dataset_dict = load_from_disk(data_dir)

        if split:
            if split in dataset_dict:
                self.dataset = dataset_dict[split]
            else:
                raise ValueError(f"Split '{split}' not found in dataset.")
        else:
            self.dataset = dataset_dict
            
        self.dataset = self.dataset.cast_column("audio", Audio())

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        item = self.dataset[idx]
        example = {
            "speech": item["audio"]["array"].astype(np.float32),
            "text": item["text"]
        }
        return example
    
    def get_text(self, idx):
        item = self.dataset[idx]
        return item["text"]



class LhotseDataset(Dataset):
    def __init__(self, data_dir="data", split=None):
        if split is None:
            raise ValueError("STDataset requires a split name (e.g., 'dev', 'train')")
        path = f"{data_dir}/{split}.jsonl.gz"
        self.cuts = CutSet.from_file(path)

        self.iso_code = {
            "de": "deu",
            "fr": "fra",
            "it": "ita",
        }

    def __len__(self):
        return len(self.cuts)

    def __getitem__(self, idx):
        cut = self.cuts[idx]
        audio = cut.load_audio()[0]
        supervision = cut.supervisions[0]
        custom = supervision.custom

        src_lang = custom['src_lang']
        tgt_lang = custom['tgt_lang']
        src_text = supervision.text.lower()
        tgt_text = custom[f"text.{tgt_lang}"].lower()

        example = {
            "speech": audio.astype(np.float32),
            "text": f'<{self.iso_code[src_lang]}><st_{self.iso_code[tgt_lang]}>'
            + f'<notimestamps> {tgt_text}',
            "text_ctc": src_text,
            "text_prev": "<na>",
        }
        return example

    def get_text(self, idx):
        cut = self.cuts[idx]
        supervision = cut.supervisions[0]
        custom = supervision.custom
        tgt_lang = custom['tgt_lang']
        return custom[f"text.{tgt_lang}"].lower()

