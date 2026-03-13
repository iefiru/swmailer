# swmailer

swmailer is a toolkit that helps sciwork prepare event notification emails.

## Features
- HTML email template for sciwork events (`templates/*.j2`).
- Example SMTP settings in `configs/mail_config.json`.

## Install

```bash
pip install git+https://github.com/chestercheng/swmailer.git
```

## Usage

```bash
swmail [-h] [-t TEMPLATE] event_url csv_file_path
```

- `event_url` — URL of the sciwork event page
- `csv_file_path` — path to the KKTIX attendees CSV file
- `-t`, `--template` — path to a custom Jinja2 template (optional, defaults to the built-in `templates/scisprint.j2`)

**Example**

```bash
swmail https://sciwork.dev/sprint/2026/03-taipei attendees.csv
```

## Requirements
- `pycontw-mail-handler` and `MarkupSafe` (installed automatically from `pyproject.toml`).
