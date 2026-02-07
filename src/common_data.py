#!/usr/bin/env python3
"""
mail handler unique data handler for kktix csv.
"""


def common_data_handle(event_url: str) -> dict:
    common_data = {
        "event_url": "https://sciwork.dev/sprint/2026/01-taipei",
        "event_name": "scisprint Taipei 2026 January",
        "event_date": "2026/01/31",
        "event_time": "10:00 - 17:00",
        "venue": "Happ. 小樹屋｜合歡分館",
        "venue_note": "B303",
        "agenda": [
            "10:00-10:30 報到",
            "10:30-11:00 專案介紹",
            "11:00-12:00 Coding session 1",
            "12:00-13:30 午餐時間 & 小組討論 1",
            "13:30-14:20 Coding session 2",
            "14:20-14:30 小組討論 2",
            "14:30-15:20 Coding session 3",
            "15:20-15:30 小組討論 3",
            "15:30-16:30 最後衝刺",
            "16:30-17:00 活動進度分享 & Closing",
        ],
        "projects": [
            "modmesh",
            "sciwork portal",
            "Cytnx",
            "Pydoc-zhtw",
            "Commitizen-Tools",
        ],
    }

    return common_data
