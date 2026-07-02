#!/usr/bin/env python3
import re
import sys
from pathlib import Path


CHANGE_SECTIONS = {"ADDED", "MODIFIED", "REMOVED"}


def usage():
    print("Usage: python scripts/validate_specs.py <feature-spec-dir>", file=sys.stderr)


def relative(path):
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return path.name


def read_text(path, errors):
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append((relative(path), f"could not read file: {exc}"))
    except UnicodeDecodeError as exc:
        errors.append((relative(path), f"could not decode file as UTF-8: {exc}"))
    return None


def section_body(markdown, heading):
    match = re.search(rf"^##\s+{re.escape(heading)}\s*$", markdown, re.MULTILINE)
    if not match:
        return None
    next_heading = re.search(r"^##\s+", markdown[match.end() :], re.MULTILINE)
    end = match.end() + next_heading.start() if next_heading else len(markdown)
    return markdown[match.end() : end].strip()


def count_scenarios(body):
    state = None
    count = 0
    for match in re.finditer(r"\b(GIVEN|WHEN|THEN)\b", body):
        keyword = match.group(1)
        if keyword == "GIVEN":
            state = "GIVEN"
        elif keyword == "WHEN" and state == "GIVEN":
            state = "WHEN"
        elif keyword == "THEN" and state == "WHEN":
            count += 1
            state = None
    return count


def metadata_fields(body):
    fields = set()
    for field in ("Was", "Now", "Reason"):
        if re.search(rf"^\s*\*\*{field}:\*\*", body, re.MULTILINE):
            fields.add(field)
    return fields


def normalized_behavior_name(name):
    return name.strip().lower()


def parse_delta(text):
    sections = {section: [] for section in CHANGE_SECTIONS}
    present_sections = set()
    current_section = None
    current_behavior = None

    def finish_behavior():
        if current_section and current_behavior:
            sections[current_section].append(current_behavior)

    for line in text.splitlines():
        section_match = re.match(r"^##\s+(ADDED|MODIFIED|REMOVED)\s*$", line.strip())
        if section_match:
            finish_behavior()
            current_section = section_match.group(1)
            present_sections.add(current_section)
            current_behavior = None
            continue

        behavior_match = re.match(r"^###\s+(.+?)\s*$", line.strip())
        if behavior_match and current_section:
            finish_behavior()
            current_behavior = {"name": behavior_match.group(1), "body": []}
            continue

        if current_behavior:
            current_behavior["body"].append(line)

    finish_behavior()
    return present_sections, sections


def validate_feature_dir(feature_dir):
    errors = []
    scenario_count = 0
    modified_behaviors = {}
    removed_behaviors = {}

    proposal = feature_dir / "proposal.md"
    if not proposal.exists():
        errors.append((relative(proposal), "proposal.md is missing"))
    else:
        proposal_text = read_text(proposal, errors)
        if proposal_text is not None:
            for heading in ("Intent", "Scope"):
                body = section_body(proposal_text, heading)
                if body is None or not body.strip():
                    errors.append((relative(proposal), f"{heading} section is empty"))

    design = feature_dir / "design.md"
    if not design.exists():
        errors.append((relative(design), "design.md is missing"))
    else:
        design_text = read_text(design, errors)
        if design_text is not None and not design_text.strip():
            errors.append((relative(design), "design.md is empty"))

    specs_dir = feature_dir / "specs"
    delta_files = sorted(specs_dir.glob("*-delta.md")) if specs_dir.is_dir() else []
    if not delta_files:
        errors.append((relative(specs_dir), "no delta specs were found"))

    for delta_file in delta_files:
        text = read_text(delta_file, errors)
        if text is None:
            continue
        present_sections, sections = parse_delta(text)
        if not present_sections:
            errors.append((relative(delta_file), "delta file has no change sections"))
            continue

        for behavior in sections["ADDED"]:
            body = "\n".join(behavior["body"])
            behavior_scenarios = count_scenarios(body)
            if behavior_scenarios == 0:
                errors.append(
                    (
                        relative(delta_file),
                        f"{behavior['name']} scenario is incomplete",
                    )
                )
            scenario_count += behavior_scenarios

        for behavior in sections["MODIFIED"]:
            body = "\n".join(behavior["body"])
            modified_behaviors.setdefault(
                normalized_behavior_name(behavior["name"]),
                (behavior["name"], relative(delta_file)),
            )
            fields = metadata_fields(body)
            for field in ("Was", "Now", "Reason"):
                if field not in fields:
                    errors.append(
                        (
                            relative(delta_file),
                            f"{behavior['name']} missing {field} field",
                        )
                    )
            behavior_scenarios = count_scenarios(body)
            if behavior_scenarios == 0:
                errors.append(
                    (
                        relative(delta_file),
                        f"{behavior['name']} scenario is incomplete",
                    )
                )
            scenario_count += behavior_scenarios

        for behavior in sections["REMOVED"]:
            body = "\n".join(behavior["body"])
            removed_behaviors.setdefault(
                normalized_behavior_name(behavior["name"]),
                (behavior["name"], relative(delta_file)),
            )
            fields = metadata_fields(body)
            for field in ("Was", "Reason"):
                if field not in fields:
                    errors.append(
                        (
                            relative(delta_file),
                            f"{behavior['name']} missing {field} field",
                        )
                    )

    for behavior_key, (behavior_name, path) in modified_behaviors.items():
        if behavior_key in removed_behaviors:
            errors.append(
                (
                    path,
                    f"{behavior_name} appears in both MODIFIED and REMOVED",
                )
            )

    return errors, len(delta_files), scenario_count


def main(argv):
    if len(argv) != 2:
        usage()
        return 2

    feature_dir = Path(argv[1])
    if (
        not feature_dir.exists()
        or feature_dir.name.endswith("_living")
        or feature_dir.name.endswith("_archive")
    ):
        usage()
        return 2

    errors, delta_count, scenario_count = validate_feature_dir(feature_dir)
    if errors:
        for path, message in errors:
            print(f"ERROR {path}: {message}")
        return 1

    print(f"OK: {delta_count} delta spec(s), {scenario_count} scenario(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
