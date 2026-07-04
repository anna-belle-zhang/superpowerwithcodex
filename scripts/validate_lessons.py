#!/usr/bin/env python3
import re
import sys
from pathlib import Path


REQUIRED_FIELDS = ("Symptom", "Root cause", "Correct approach", "Occurrences", "Level")
VALID_LEVELS = {"lesson", "pattern"}
TAG_PATTERN = re.compile(r"^##\s+\[tag:\s*([a-z0-9]+(?:-[a-z0-9]+)*)\]\s+(.+?)\s*$")
FIELD_PATTERN = re.compile(
    r"^-\s+(Symptom|Root cause|Correct approach|Occurrences|Level):\s*(.*)$",
    re.MULTILINE,
)
OCCURRENCE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}\s+\([^)]+\)$")


def usage():
    print("Usage: python scripts/validate_lessons.py <lessons-file>", file=sys.stderr)


def relative(path):
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return str(path)


def read_text(path, errors):
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append((relative(path), f"could not read file: {exc}"))
    except UnicodeDecodeError as exc:
        errors.append((relative(path), f"could not decode file as UTF-8: {exc}"))
    return None


def parse_entries(text):
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", text, re.MULTILINE))
    entries = []

    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        entries.append(
            {
                "heading": match.group(0).strip(),
                "heading_text": match.group(1).strip(),
                "body": text[match.end() : end],
            }
        )

    return entries


def occurrence_items(value):
    return [item.strip() for item in value.split(",") if item.strip()]


def validate_entry(entry, seen_tags):
    errors = []
    tag_match = TAG_PATTERN.match(entry["heading"])
    if not tag_match:
        errors.append(
            (
                entry["heading"],
                "heading must include [tag: <kebab-case-tag>]",
            )
        )
        return errors, None

    tag = tag_match.group(1)
    if tag in seen_tags:
        errors.append(
            (
                tag,
                f"duplicate tag: {tag}; repeated lessons belong on one entry's Occurrences line",
            )
        )
    seen_tags.add(tag)

    fields = {name: value.strip() for name, value in FIELD_PATTERN.findall(entry["body"])}
    for field in REQUIRED_FIELDS:
        if not fields.get(field):
            errors.append((tag, f"missing required field: {field}"))

    level = fields.get("Level")
    if level and level not in VALID_LEVELS:
        errors.append((tag, "Level must be one of: lesson, pattern"))

    occurrences_value = fields.get("Occurrences")
    if occurrences_value:
        occurrences = occurrence_items(occurrences_value)
        for occurrence in occurrences:
            if not OCCURRENCE_PATTERN.match(occurrence):
                errors.append((tag, f"occurrence missing YYYY-MM-DD date: {occurrence}"))
        if level == "pattern" and len(occurrences) < 2:
            errors.append((tag, "pattern level requires at least 2 occurrences"))

    return errors, tag


def validate_lessons(path):
    errors = []
    text = read_text(path, errors)
    if text is None:
        return errors, 0

    entries = parse_entries(text)
    seen_tags = set()
    valid_entry_count = 0

    for entry in entries:
        entry_errors, tag = validate_entry(entry, seen_tags)
        errors.extend((relative(path), f"{context}: {message}") for context, message in entry_errors)
        if tag:
            valid_entry_count += 1

    return errors, valid_entry_count


def main(argv):
    if len(argv) != 2:
        usage()
        return 2

    path = Path(argv[1])
    if not path.exists():
        print("OK: lessons file not found")
        return 0

    if not path.is_file():
        usage()
        return 2

    errors, entry_count = validate_lessons(path)
    if errors:
        for error_path, message in errors:
            print(f"ERROR {error_path}: {message}")
        return 1

    print(f"OK: {entry_count} lesson entry(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
