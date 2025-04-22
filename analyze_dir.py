import os
from typing import Dict, Union

def summarize_tree(path, max_dirs=5, max_files=5, sample_exts={".flac", ".mp3", ".wav", ".m4a"}):
    def summarize_dir(current_path) -> Dict[str, Union[list, dict]]:
        summary = {}
        try:
            entries = os.listdir(current_path)
        except Exception as e:
            return {"_error": str(e)}
        dirs, bulk, meta = [], [], []
        for name in sorted(entries):
            full_path = os.path.join(current_path, name)
            if os.path.isdir(full_path):
                dirs.append(name)
            else:
                ext = os.path.splitext(name)[1]
                if ext in sample_exts:
                    bulk.append(name)
                else:
                    meta.append(name)
        dir_summaries = {}
        for subdir in dirs[:max_dirs]:
            dir_summaries[subdir] = summarize_dir(os.path.join(current_path, subdir))
        if len(dirs) > max_dirs:
            dir_summaries["_more_dirs"] = f"... and {len(dirs) - max_dirs} more"
        file_summary = {}
        if bulk:
            display = bulk[:max_files]
            if len(bulk) > max_files:
                display.append(f"... and {len(bulk) - max_files} more")
            file_summary["_bulk"] = display
        if meta:
            file_summary["_meta"] = meta
        summary.update(dir_summaries)
        summary.update(file_summary)
        return summary
    return summarize_dir(path)

def print_summary_to_string(summary, indent=0) -> str:
    lines = []
    for name, content in summary.items():
        if name == "_bulk":
            for f in content:
                lines.append("    " * indent + f"- [bulk] {f}")
        elif name == "_meta":
            for f in content:
                lines.append("    " * indent + f"- [meta] {f}")
        elif name == "_more_dirs":
            lines.append("    " * indent + content)
        elif name == "_error":
            lines.append("    " * indent + f"- [error] {content}")
        else:
            lines.append("    " * indent + f"{name}/")
            lines.append(print_summary_to_string(content, indent + 1))
    return "\n".join(lines)

def find_all_meta_files(summary, current_path, current_prefix=""):
    results = []
    for key, val in summary.items():
        if key == "_meta":
            for f in val:
                results.append(os.path.join(current_path, f))
        elif isinstance(val, dict):
            new_prefix = os.path.join(current_path, key)
            results.extend(find_all_meta_files(val, new_prefix))
    return results

def read_meta_files(meta_paths, max_lines=5):
    previews = []
    for full_path in meta_paths:
        try:
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = [line.rstrip("\n") for _, line in zip(range(max_lines), f)]
        except Exception as e:
            lines = [f"[Error reading file: {e}]"]
        previews.append((full_path, lines))
    return previews


PATH = "/u/someki1/nvme/espnets/i3d/egs2/europarl/asr1/downloads/v1.1"
tree = summarize_tree(PATH, max_dirs=2, max_files=4)

tree_output = print_summary_to_string(tree)
meta_paths = find_all_meta_files(tree, PATH)
meta_previews = read_meta_files(meta_paths)


print("## output\n")
print("**tree**")
print("```")
print(tree_output)
print("```\n")

for path, lines in meta_previews:
    print(f"**{os.path.relpath(path, PATH)}**")
    print("```")
    print("\n".join(lines))
    print("```")
