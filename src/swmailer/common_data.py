#!/usr/bin/env python3
"""
mail handler unique data handler for kktix csv.
"""

from datetime import datetime
from html import unescape
from urllib.request import urlopen
import argparse
import json
import re
import sys

from lxml import html


def _collapse_spaces(text):
    return " ".join(text.split())


def _text_content(element):
    return _collapse_spaces(element.text_content())


def _collect_sections(root):
    sections = {}
    for header in root.xpath("//h2[@id]"):
        section_id = header.get("id")
        fragments = []
        for sibling in header.itersiblings():
            if isinstance(sibling.tag, str) and sibling.tag.lower() == "h2":
                break
            fragments.append(html.tostring(sibling, encoding="unicode"))

        content = "".join(fragments).strip()
        if not content:
            raise ValueError(f"Section {section_id} has no content in HTML dump.")

        sections[section_id] = html.fragment_fromstring(content, create_parent="section")

    return sections


def _extract_list_value(section_node, label):
    for item in section_node.xpath(".//li[strong]"):
        strong_text = _text_content(item.xpath(".//strong")[0])
        if strong_text != label:
            continue
        text = item.text_content()
        match = re.search(rf"^{re.escape(label)}\s*:\s*(.*)$", text, re.S)
        if match:
            value = unescape(_collapse_spaces(match.group(1)))
            if value:
                return value

    raise ValueError(f"Failed to extract {label.lower()} information from HTML dump.")


def _format_event_date(raw_date):
    dt = datetime.strptime(_collapse_spaces(raw_date), "%A, %B %d, %Y")
    return dt.strftime("%Y/%m/%d")


def _clean_event_time(raw_time):
    cleaned = _collapse_spaces(raw_time)
    return cleaned.split("(")[0].strip()


def _extract_agenda(section_node):
    rows = section_node.xpath(
        ".//div[contains(concat(' ', normalize-space(@class), ' '), ' flex-col ') and "
        "contains(concat(' ', normalize-space(@class), ' '), ' lg:flex-row ')]"
    )
    agenda = []

    for row in rows:
        columns = [child for child in row if isinstance(child.tag, str)]
        if len(columns) < 2:
            continue
        time_text = _collapse_spaces(columns[0].text_content())
        desc_text = _collapse_spaces(columns[1].text_content())
        if time_text and desc_text:
            agenda.append(f"{time_text} {desc_text}")

    if not agenda:
        raise ValueError("Failed to parse agenda from HTML dump.")

    return agenda


def _extract_projects(section_node):
    projects = [_text_content(tag) for tag in section_node.xpath(".//h3")]
    if not projects:
        raise ValueError("Failed to parse project list from HTML dump.")
    return projects


def parse_common_data(event_url):
    with urlopen(event_url) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        html_content = response.read().decode(charset)

    dom = html.fromstring(html_content)

    sections = _collect_sections(dom)

    def require(section_id):
        if section_id not in sections:
            raise ValueError(f"Failed to locate section {section_id} in HTML dump.")
        return sections[section_id]

    date_section = require("date")
    raw_date = _extract_list_value(date_section, "Date")
    raw_time = _extract_list_value(date_section, "Time")

    return {
        "event_url": event_url,
        "event_name": _text_content(dom.xpath("//title")[0]).replace("sciwork - ", "", 1),
        "event_date": _format_event_date(raw_date),
        "event_time": _clean_event_time(raw_time),
        "venue": _text_content(require("venue").xpath(".//a")[0]),
        "agenda": _extract_agenda(require("agenda")),
        "projects": _extract_projects(require("project-list")),
    }


def _main():
    parser = argparse.ArgumentParser(description="Dump the common_data section from a sciwork sprint HTML page.")
    parser.add_argument(
        "--event-url",
        required=True,
        help="Event page URL to fetch the sprint HTML from, e.g., https://sciwork.dev/sprint/2026/02-hsinchu",
    )
    args = parser.parse_args()

    try:
        common_data = parse_common_data(args.event_url)
    except ValueError as exc:
        sys.stderr.write(f"{exc}\n")
        return 1

    serialized = json.dumps(common_data, ensure_ascii=False, indent=2)
    sys.stdout.write(serialized)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
