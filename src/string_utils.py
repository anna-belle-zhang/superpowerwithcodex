import re


def truncate(text, max_len):
    return text[:max_len]


def slugify(text):
    slug = re.sub(r"\s+", "-", text.lower())
    slug = re.sub(r"[^a-z0-9-]", "", slug)
    return re.sub(r"-+", "-", slug)


def count_words(text):
    return len(text.split())
