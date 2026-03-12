#!/usr/bin/env python3
"""
CSV to JSON Converter Tool
Extracts Registration No., Contact Name, and Contact Email from CSV
and outputs as JSON format.
"""

from importlib.resources import files
from pathlib import Path
import argparse
import csv
import json
import os
import re
import subprocess

from swmailer.common_data import parse_common_data


CSV_REQUIRED_COLUMNS = ["Registration No.", "Contact Name", "Contact Email"]
RECEIVER_FILE = "receivers.json"
MAIL_FILE = "mail.json"
PKG = files("swmailer")


def sanitize_dir_name(name: str) -> str:
    # allow letters, digits, dot, underscore, dash; convert others to underscore
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", name.strip())
    return safe or "event"


def csv_to_json(csv_file_path: str) -> list[dict]:
    """
    Parse CSV file and extract specific fields into JSON format.
    """
    results = []

    with open(csv_file_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # Check required columns first
        missing = [
            col for col in CSV_REQUIRED_COLUMNS if col not in (reader.fieldnames or [])
        ]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")

        for row in reader:
            entry = {
                "receiver_email": row.get("Contact Email", ""),
                "receiver_name": row.get("Contact Name", ""),
                "id": int(row.get("Registration No.", 0)),
            }
            results.append(entry)

    return results


def mail_config_handle(subject: str) -> dict:
    mail_config = json.loads(
        PKG.joinpath("configs/mail_config.json").read_text(encoding="utf-8")
    )
    mail_config["Subject"] = subject
    return mail_config


def main():
    receiver_data = {"common_data": {}, "unique_data": []}

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "event_url", help="URL of the sciwork event to extract data from"
    )
    parser.add_argument("csv_file_path", help="Path to the KKTIX Attendees CSV file")
    parser.add_argument("-t", "--template", help="Path to the mail template file")
    args = parser.parse_args()

    event_url = args.event_url
    common_data = parse_common_data(event_url)
    unique_data = csv_to_json(args.csv_file_path)

    receiver_data["common_data"] = common_data
    receiver_data["unique_data"] = unique_data

    mail_config = mail_config_handle(common_data["event_name"] + " 活動通知信")

    if args.template:
        template_path = Path(args.template).resolve()
    else:
        template_path = Path(str(PKG.joinpath("templates/scisprint.j2")))

    """ Create Working Directory """
    working_directory_name = sanitize_dir_name(common_data["event_name"])
    Path(working_directory_name).mkdir(exist_ok=True)

    """ Generate Config File """
    with open(Path(working_directory_name, RECEIVER_FILE), "w", encoding="utf-8") as f:
        json.dump(receiver_data, f, ensure_ascii=False, indent=4)

    with open(Path(working_directory_name, MAIL_FILE), "w", encoding="utf-8") as f:
        json.dump(mail_config, f, ensure_ascii=False, indent=4)

    """ Render Mail """
    env = os.environ.copy()
    subprocess.run(
        ["render_mail", template_path, RECEIVER_FILE],
        cwd=Path.cwd().joinpath(working_directory_name),
        env=env,
        check=True,
    )

    """ Send Mail """
    subprocess.run(
        ["send_mail", MAIL_FILE],
        cwd=Path.cwd().joinpath(working_directory_name),
        env=env,
        check=True,
    )


if __name__ == "__main__":
    main()
