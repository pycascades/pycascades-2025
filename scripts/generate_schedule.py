#!/usr/bin/env python3
"""
Generate a CSV attachment for the schedule using Pretalx's API
The Pretalx API is documented at https://docs.pretalx.org/en/latest/api/index.html
This script expects the `PRETALX_TOKEN` environment variable to be populated.
"""

import csv
import os
import requests
from pathlib import Path


HEADERS = {"Authorization": f"Token {os.environ.get('PRETALX_TOKEN')}"}
YEAR = "2025"
EVENT_SLUG = f"pycascades-{YEAR}"
CSV_PATH = (
    Path(__file__).parents[1]
    / f"content/program/schedule/pycascades-{YEAR}_schedule.csv"
)


def fetch_schedule():
    print(f"Fetching talks for {EVENT_SLUG}")
    response = requests.get(
        f"https://pretalx.com/api/events/{EVENT_SLUG}/talks/",
        headers=HEADERS,
    )
    response.raise_for_status()
    return response.json()


def write_schedule(schedule):
    with CSV_PATH.open(mode="w", newline="") as file:
        columns = ["id", "title", "speakers", "start_time", "duration", "track"]
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()

        for talk in schedule["results"]:
            data = {
                "id": talk["code"],
                "title": talk["title"],
                "speakers": ", ".join(
                    [speaker["name"] for speaker in talk["speakers"]]
                ),
                "start_time": talk["slot"]["start"]
                if "slot" in talk and talk["slot"]
                else "",
                "duration": talk["duration"],
                "track": talk["track"]["en"]
                if "track" in talk and talk["track"]
                else "",
            }
            writer.writerow(data)


if __name__ == "__main__":
    schedule = fetch_schedule()
    write_schedule(schedule)
    print(f"Schedule written to {CSV_PATH}")
