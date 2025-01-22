from pathlib import Path
import json
import requests

talk_template = """
title: {title}
---
description:

{description}
---
speaker_slugs:

{speaker_slugs}

"""

speaker_template = """
name: {name}
---
talk_title: {talk_title}
---
talk_slug: {talk_slug}
---
bio:
{bio}
---
website_url: {website_url}
---
mastodon_url: {mastodon_url}
---
github_handle: {github_handle}
---
instagram_handle: {instagram_handle}
---
twitter_handle: {twitter_handle}

"""


def load_speakers():
    speakers = {}
    with open("pycascades-2025_speakers.json", "r") as f:
        speakers_json = json.load(f)
        for speaker in speakers_json:
            speakers[speaker["ID"]] = speaker
            speaker["slug"] = "-".join(speaker["Name"].split(" ")).lower()

    return speakers


def load_talks():
    with open("pycascades-2025_sessions.json", "r") as f:
        talks_json = json.load(f)
        return talks_json


def fetch_speaker_image(speaker):
    print(f"Fetching image for {speaker['Name']}")
    url = speaker["Picture"]
    suffix = url.split(".")[-1]
    picture_data = requests.get(url).content

    with open(f"profile.{suffix.lower()}", "wb") as f:
        f.write(picture_data)


def render_speaker(speaker, talk):
    name = speaker["Name"]
    bio = speaker["Biography"] or ""
    talk_title = talk["Proposal title"]
    slug = speaker["slug"]
    website_url = speaker["Website URL"] or ""
    mastodon_url = speaker["Mastodon URL"] or ""
    github_handle = speaker["Github username"] or ""
    if github_handle:
        # Several folks gave us full URLs, all we need are usernames
        github_handle = github_handle.replace("https://github.com/", "")
    instagram_handle = speaker["Instagram username"] or ""
    twitter_handle = speaker["Twitter username"] or ""
    photo_url = speaker["Picture"] or ""
    photo_suffix = photo_url.split(".")[-1].lower()
    talk_slug = talk["slug"]
    print(f"Rendering speaker {name}")
    contents = speaker_template.format(
        name=name,
        bio=bio,
        talk_title=talk_title,
        talk_slug=talk_slug,
        website_url=website_url,
        mastodon_url=mastodon_url,
        github_handle=github_handle,
        instagram_handle=instagram_handle,
        twitter_handle=twitter_handle,
    )

    folder_path = Path("content", "program", "speakers", slug)

    if not folder_path.exists():
        folder_path.mkdir()
    else:
        print(f"Folder {folder_path} already exists")

    file_path = Path(folder_path, "contents.lr")

    if not file_path.exists():
        file_path.write_text(contents)
    else:
        print(f"File {file_path} already exists")

    if photo_url == "":
        print(f"{name} - picture URL is empty")
        return

    picture_path = Path(folder_path, f"profile.{photo_suffix}")

    if not picture_path.exists():
        print(f"Fetching photo for {speaker['Name']} - {photo_url}")
        picture_data = requests.get(photo_url).content
        picture_path.write_bytes(picture_data)
    else:
        print(f"File {picture_path} already exists")


def trim_title(title, char):
    char_index = title.find(char)

    if char_index > -1:
        title = title[:char_index]

    return title.strip()


def render_talk(talk, speakers):
    title = talk["Proposal title"]
    description = talk["Abstract"]
    slug = trim_title(title, ":")
    slug = trim_title(slug, "(")
    slug = trim_title(slug, " – ")
    slug = trim_title(slug, " - ")
    slug = (
        slug.replace("/", "")
        .replace("+", " ")
        .replace("’", "")
        .replace(",", "")
        .replace(".", " ")
        .replace("!", "")
    )
    slug = "-".join(slug.lower().split(" "))
    talk["slug"] = slug
    speaker_slugs = []
    print(f"Rendering talk: {title}")

    for speaker_id in talk["Speaker IDs"]:
        speaker = speakers[speaker_id]
        speaker_slugs.append(speaker["slug"])
        render_speaker(speaker, talk)

    contents = talk_template.format(
        title=title, description=description, speaker_slugs="\n".join(speaker_slugs)
    )
    folder_path = Path("content", "program", "talks", slug)

    if not folder_path.exists():
        folder_path.mkdir()

    file_path = Path(folder_path, "contents.lr")
    file_path.write_text(contents)


def main():
    speakers = load_speakers()
    talks = load_talks()

    for talk in talks:
        render_talk(talk, speakers)


if __name__ == "__main__":
    main()
