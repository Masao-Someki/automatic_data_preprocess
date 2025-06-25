import os
from typing import Dict, Union
from collections import defaultdict

ARCHIVE_LIKE_EXTS = {
    '.zip', '.tar', '.gz', '.tgz', '.bz2', '.xz', '.7z', '.rar',
    '.sph', '.arc', '.zst', '.lz4', '.cab', '.rpm', '.img', '.iso',
    '.bin', '.dat'
}

def summarize_tree(path, max_dirs=5, max_files=100):
    def summarize_dir(current_path) -> Dict[str, Union[list, dict]]:
        summary = {}
        try:
            entries = os.scandir(current_path)
        except Exception as e:
            return {"_error": str(e)}

        dirs = []
        files_by_ext = defaultdict(list)
        for entry in sorted(entries, key=lambda e: e.name):
            if entry.name.startswith('.'):
                continue
            if entry.is_dir():
                dirs.append(entry.name)
            else:
                ext = os.path.splitext(entry.name)[1]
                if ext in ARCHIVE_LIKE_EXTS:
                    continue  
                files_by_ext[ext].append(entry.name)

        bulk_exts = {ext for ext, files in files_by_ext.items() if len(files) >= max_files}

        file_summary = {}
        for ext, files in files_by_ext.items():
            tag = "_bulk" if ext in bulk_exts else "_meta"
            display = files[:5]
            if len(files) > 5:
                display.append(f"... and {len(files) - 5} more")
            if tag not in file_summary:
                file_summary[tag] = []
            file_summary[tag].extend(display)

        dir_summaries = {}
        for subdir in dirs[:max_dirs]:
            dir_summaries[subdir] = summarize_dir(os.path.join(current_path, subdir))
        if len(dirs) > max_dirs:
            dir_summaries["_more_dirs"] = f"... and {len(dirs) - max_dirs} more"

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


def get_markdown(download_path):
    tree = summarize_tree(download_path, max_dirs=3, max_files=100)

    tree_output = print_summary_to_string(tree)
    meta_paths = find_all_meta_files(tree, download_path)
    meta_previews = read_meta_files(meta_paths)

    text = f"""## Analyzed directory: {download_path}
**tree**
```
{tree_output}
```"""
    for path, lines in meta_previews:
        text += f"""

**{os.path.relpath(path, download_path)}**
```
{"\n".join(lines)}
```
"""
    return text
