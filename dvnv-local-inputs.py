#!/usr/bin/env python3
import json
import os
import sys

import yaml


def repo_name_from_url(url):
    cleaned = url.split("?", 1)[0].split("#", 1)[0].removeprefix("git+")

    if cleaned.startswith("github:"):
        cleaned = cleaned.removeprefix("github:")
    elif "github.com/" in cleaned:
        cleaned = cleaned.split("github.com/", 1)[1]

    cleaned = cleaned.rstrip("/").removesuffix(".git")
    cleaned = cleaned.rsplit("/", 1)[-1]
    return cleaned or None


def get_inputs_block(source_label, yaml_text):
    parsed = yaml.safe_load(yaml_text) or {}
    if not isinstance(parsed, dict):
        raise SystemExit(f"expected a top-level mapping in {source_label}")

    inputs_block = parsed.get("inputs", {}) or {}
    if not isinstance(inputs_block, dict):
        raise SystemExit(f"expected `inputs` to be a mapping in {source_label}")

    return inputs_block


def read_input_spec(input_spec):
    if isinstance(input_spec, dict):
        url = input_spec.get("url")
        if isinstance(url, str) and url:
            return url, dict(input_spec)
    elif isinstance(input_spec, str) and input_spec:
        return input_spec, {}
    return None, None


def read_local_repo_names(repo_names_json_path):
    with open(repo_names_json_path, "r", encoding="utf-8") as handle:
        parsed = json.load(handle) or []

    if not isinstance(parsed, list):
        raise SystemExit("expected local repo names JSON to be a list")

    names = set()
    for item in parsed:
        if isinstance(item, str) and item:
            names.add(item)

    return names


def read_repo_sources(repo_sources_json_path):
    with open(repo_sources_json_path, "r", encoding="utf-8") as handle:
        parsed = json.load(handle) or {}

    if not isinstance(parsed, dict):
        raise SystemExit("expected repo sources JSON to be a mapping")

    repo_sources = {}
    for repo_name, yaml_text in parsed.items():
        if isinstance(repo_name, str) and repo_name and isinstance(yaml_text, str):
            repo_sources[repo_name] = yaml_text

    return repo_sources


def add_override(overrides, input_name, copied_spec, source_label):
    existing_spec = overrides.get(input_name)
    if existing_spec is None:
        overrides[input_name] = copied_spec
        return

    if existing_spec != copied_spec:
        raise SystemExit(
            f"conflicting local override for input '{input_name}' while scanning {source_label}"
        )


def main() -> int:
    source_yaml_path, local_repo_names_path, repo_sources_json_path, repos_root, url_scheme = (
        sys.argv[1:6]
    )
    local_repo_names = read_local_repo_names(local_repo_names_path)
    repo_sources = read_repo_sources(repo_sources_json_path)
    url_prefix = "git+file:" if url_scheme == "git+file" else "path:"

    with open(source_yaml_path, "r", encoding="utf-8") as handle:
        source_yaml_text = handle.read()

    overrides = {}
    visited_repo_names = set()
    pending_sources = [("root source", source_yaml_text)]

    while pending_sources:
        source_label, source_yaml_text = pending_sources.pop(0)

        for input_name, input_spec in get_inputs_block(source_label, source_yaml_text).items():
            input_url, copied_spec = read_input_spec(input_spec)

            if input_url is None:
                continue

            repo_name = repo_name_from_url(input_url)
            if not repo_name:
                continue

            # Names are passed from eval-time readDir; do not check os.path.isdir()
            # here because this script runs in a sandboxed build environment.
            if repo_name not in local_repo_names:
                continue

            local_repo_path = os.path.join(repos_root, repo_name)
            copied_spec["url"] = f"{url_prefix}{local_repo_path}"
            add_override(overrides, str(input_name), copied_spec, source_label)

            if repo_name in visited_repo_names:
                continue

            nested_source = repo_sources.get(repo_name)
            if nested_source is None:
                continue

            visited_repo_names.add(repo_name)
            pending_sources.append((f"local repo '{repo_name}'", nested_source))

    if not overrides:
        return 0

    yaml.safe_dump(
        {"inputs": {name: overrides[name] for name in sorted(overrides)}},
        sys.stdout,
        sort_keys=True,
        default_flow_style=False,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
