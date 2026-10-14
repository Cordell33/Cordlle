"""Prepare the approved October puzzle without releasing it before midnight."""

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import time

RELEASE_AT = datetime(2026, 10, 15, 4, tzinfo=timezone.utc)
RELEASE_END = RELEASE_AT + timedelta(days=1)

QUESTIONS = [
    "The letter formed by a two-finger gesture associated with victory and peace",
    "The opposite of the answer to question 4",
    "An abbreviation for base 16 in math and computer science, or a word for a magical curse",
    "A road sign that tells drivers to come to a complete halt",
    "A species or subspecies that is significantly smaller than its counterparts, or the primary term associated with the Bambenga, Bambuti, and Batwa peoples",
    "'Rapper's Delight', 'Straight Outta Compton', 'Juicy', and 'Lose Yourself' are examples of this musical genre",
    "In the cartoon 'Tom and Jerry', what specifically is Spike?",
    "The capital of the only country that is also a continent",
    "",
]
ANSWERS = [list(answer) for answer in [
    "V", "GO", "HEX", "STOP", "PYGMY", "HIPHOP", "BULLDOG", "CANBERRA", "YESTERDAY"
]]
PREVIOUS_HASHES = {
    "questions": "f3a5c0f8ce4882b6b07f344714afd0b17007c9953f3685cab92e4c12ec3e5203",
    "correctAnswers": "8000639a10fc66cf91af2bf33de94fdfd67b16b38df26ab22689b55af6196274",
}


def replacement(name, rows):
    lines = []
    for index, row in enumerate(rows):
        suffix = "," if index < len(rows) - 1 else ""
        if index == len(rows) - 1:
            suffix += (" // final row has no visible question text" if name == "questions"
                       else " // final CORDLLE word")
        lines.append("      " + json.dumps(row, ensure_ascii=False) + suffix)
    return "    const " + name + " = [\n" + "\n".join(lines) + "\n    ];"


def prepare(document):
    if len(QUESTIONS) != 9 or QUESTIONS[-1] != "":
        raise ValueError("Expected eight clues and an empty final clue")
    if [len(row) for row in ANSWERS] != list(range(1, 10)):
        raise ValueError("Answers must fit the nine pyramid rows")
    for name, rows in [("questions", QUESTIONS), ("correctAnswers", ANSWERS)]:
        pattern = re.compile(r"^    const " + name + r" = \[.*?^    \];", re.M | re.S)
        matches = list(pattern.finditer(document))
        if len(matches) != 1:
            raise ValueError(f"Expected exactly one {name} declaration")
        previous = matches[0].group(0)
        updated = replacement(name, rows)
        if previous != updated and hashlib.sha256(previous.encode()).hexdigest() != PREVIOUS_HASHES[name]:
            raise ValueError(f"{name} changed since preparation; refusing to overwrite it")
        document = pattern.sub(lambda _: updated, document, count=1)
    return document


def is_release_window(now):
    return RELEASE_AT <= now < RELEASE_END


def wait_until_release():
    now = datetime.now(timezone.utc)
    # A late yearly cron or an accidental early manual run must not publish.
    if now < RELEASE_AT - timedelta(minutes=20) or now >= RELEASE_END:
        print("due=false")
        return
    while now < RELEASE_AT:
        time.sleep(min(30, (RELEASE_AT - now).total_seconds()))
        now = datetime.now(timezone.utc)
    print("due=" + str(is_release_window(now)).lower())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["check", "apply", "wait"])
    parser.add_argument("--file", type=Path, default=Path("index.html"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.operation == "wait":
        wait_until_release()
        return
    updated = prepare(args.file.read_text())
    if args.operation == "apply":
        if not is_release_window(datetime.now(timezone.utc)):
            raise SystemExit("Release is restricted to October 15, 2026, Eastern time")
        args.file.write_text(updated)
        print("October puzzle applied")
    else:
        if args.output:
            args.output.write_text(updated)
        print("Approved puzzle validated; live index.html unchanged")


if __name__ == "__main__":
    main()
