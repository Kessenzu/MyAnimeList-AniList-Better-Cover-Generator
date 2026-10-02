import os
import re
import time
from pathlib import Path

import requests


# ============================== #
#           VARIABLES            #
# ------------------------------ #

MAL_USERNAME = "YOUR_MAL_USERNAME"
MAL_CLIENT_ID = "YOUR_MAL_CLIENT_ID"

MAL_API = "https://api.myanimelist.net/v2"
ANILIST_API = "https://graphql.anilist.co"

BATCH_SIZE = 20
REQUEST_DELAY = 2.5
MAX_RETRIES = 5

MANUAL_PLACEHOLDER = "ADD-MANUAL-COVER-URL-HERE"


# ============================== #
#        MEDIA CONFIGS           #
# ------------------------------ #

CONFIGS = {
    "anime": {
        "name": "Anime",
        "mal_endpoint": "animelist",
        "anilist_type": "ANIME",
        "url_type": "anime",

        "output_file": Path(
            "mal-anime-covers.css"
        ),

        "error_file": Path(
            "mal-anime-covers-error.txt"
        ),

        "manual_file": Path(
            "mal-anime-covers-manual.css"
        ),
    },

    "manga": {
        "name": "Manga",
        "mal_endpoint": "mangalist",
        "anilist_type": "MANGA",
        "url_type": "manga",

        "output_file": Path(
            "mal-manga-covers.css"
        ),

        "error_file": Path(
            "mal-manga-covers-error.txt"
        ),

        "manual_file": Path(
            "mal-manga-covers-manual.css"
        ),
    },
}


# ============================== #
#         HTTP SESSION           #
# ------------------------------ #

session = requests.Session()

session.headers.update({
    "User-Agent": (
        "Better-MyAnimeList-Covers/4.0"
    ),
    "Accept": "application/json",
})


# ============================== #
#       HELPER FUNCTIONS         #
# ------------------------------ #

def safe_title(title):
    """
    Makes a media title safe to use
    inside a CSS comment.
    """

    return (
        str(title)
        .replace("*/", "* /")
        .replace("\n", " ")
        .strip()
    )


def clean_text(text):
    """
    Converts multiline text into
    a single clean line.
    """

    return (
        str(text)
        .replace("\n", " ")
        .replace("\r", " ")
        .strip()
    )


def chunked(items, size):
    """
    Splits a list into smaller batches.
    """

    for i in range(
        0,
        len(items),
        size
    ):
        yield items[
            i:i + size
        ]


def anilist_alias(mal_id):
    """
    Converts a MAL ID into a valid
    GraphQL alias.

    Example:
    60636 -> m60636
    """

    return f"m{mal_id}"


# ============================== #
#         CSS HEADERS            #
# ------------------------------ #

def get_auto_css_header(config):
    """
    Creates the header for the
    automatically generated CSS.
    """

    return f"""/*
============================================================
 Better {MAL_USERNAME}'s MyAnimeList {config["name"]} Covers
 Covers Automatically Fetched From AniList
============================================================
*/

"""


def get_manual_css_header(config):
    """
    Creates the header for the
    manually maintained CSS.
    """

    return f"""/*
============================================================
 Better {MAL_USERNAME}'s MyAnimeList {config["name"]} Covers
 Manually Updated Covers
============================================================
*/

"""


# ============================== #
#       EXISTING CSS LOAD        #
# ------------------------------ #

def load_existing_css(config):
    """
    Loads the existing automatic CSS.

    If it does not exist yet,
    a new header is created.
    """

    output_file = config[
        "output_file"
    ]

    if output_file.exists():

        return output_file.read_text(
            encoding="utf-8"
        )

    return get_auto_css_header(
        config
    )


def load_existing_ids(css_content):
    """
    Extracts all MAL IDs already
    present in a CSS file.
    """

    matches = re.findall(
        r"MAL ID:\s*(\d+)",
        css_content
    )

    return {
        int(mal_id)
        for mal_id in matches
    }


# ============================== #
#          CSS SAVING            #
# ------------------------------ #

def save_css(
    config,
    css_content
):
    """
    Safely overwrites the automatic
    CSS file.

    The content is written to a
    temporary file first.
    """

    output_file = config[
        "output_file"
    ]

    temp_file = (
        output_file.with_suffix(
            output_file.suffix
            + ".tmp"
        )
    )

    temp_file.write_text(
        css_content,
        encoding="utf-8"
    )

    os.replace(
        temp_file,
        output_file
    )


# ============================== #
#       ERROR LOG READING        #
# ------------------------------ #

def load_error_entries(config):
    """
    Reads all existing entries from
    the error log.

    Returns:
    {
        MAL_ID: {
            "title": "...",
            "error": "..."
        }
    }
    """

    error_file = config[
        "error_file"
    ]

    entries = {}

    if not error_file.exists():
        return entries

    content = error_file.read_text(
        encoding="utf-8"
    )

    pattern = re.compile(
        r"MAL ID:\s*(\d+)\s*\|\s*"
        r"Title:\s*(.*?)\s*\|\s*"
        r"Error:\s*(.*)"
    )

    for line in content.splitlines():

        match = pattern.fullmatch(
            line.strip()
        )

        if not match:
            continue

        mal_id = int(
            match.group(1)
        )

        entries[mal_id] = {
            "title": match.group(2),
            "error": match.group(3),
        }

    return entries


# ============================== #
#        ERROR LOG SAVING        #
# ------------------------------ #

def save_error(
    config,
    mal_id,
    title,
    error_message,
    error_entries,
    generate_manual
):
    """
    Saves a failed entry immediately.

    The same MAL ID is only written
    once to the error file.
    """

    if mal_id in error_entries:

        if generate_manual:
            ensure_manual_entry(
                config,
                mal_id,
                error_entries[
                    mal_id
                ]["title"]
            )

        return

    error_file = config[
        "error_file"
    ]

    title = clean_text(
        title
    )

    error_message = clean_text(
        error_message
    )

    line = (
        f"MAL ID: {mal_id} | "
        f"Title: {title} | "
        f"Error: {error_message}\n"
    )

    with open(
        error_file,
        "a",
        encoding="utf-8"
    ) as file:

        file.write(
            line
        )

    error_entries[mal_id] = {
        "title": title,
        "error": error_message,
    }

    print(
        f"     -> Error saved: "
        f"{error_file}"
    )

    if generate_manual:

        ensure_manual_entry(
            config,
            mal_id,
            title
        )


# ============================== #
#      MANUAL CSS HANDLING       #
# ------------------------------ #

def load_manual_css(config):
    """
    Loads the existing manual CSS.

    Existing manual URLs are preserved.
    """

    manual_file = config[
        "manual_file"
    ]

    if manual_file.exists():

        return manual_file.read_text(
            encoding="utf-8"
        )

    return get_manual_css_header(
        config
    )


def create_manual_css_block(
    config,
    mal_id,
    title
):
    """
    Creates a manual cover placeholder
    for a failed entry.
    """

    title = safe_title(
        title
    )

    url_type = config[
        "url_type"
    ]

    return f"""/* {title}
   MAL ID: {mal_id}
*/
.data.image .link[href*="/{url_type}/{mal_id}/"] {{
    background-image: url("{MANUAL_PLACEHOLDER}") !important;
}}

"""


def save_manual_css(
    config,
    css_content
):
    """
    Safely overwrites the manual CSS.
    """

    manual_file = config[
        "manual_file"
    ]

    temp_file = (
        manual_file.with_suffix(
            manual_file.suffix
            + ".tmp"
        )
    )

    temp_file.write_text(
        css_content,
        encoding="utf-8"
    )

    os.replace(
        temp_file,
        manual_file
    )


def ensure_manual_entry(
    config,
    mal_id,
    title
):
    """
    Adds a manual placeholder only
    if the MAL ID is not already
    present in the manual CSS.

    Existing manually edited URLs
    are never overwritten.
    """

    css_content = load_manual_css(
        config
    )

    existing_ids = load_existing_ids(
        css_content
    )

    if mal_id in existing_ids:
        return

    block = create_manual_css_block(
        config,
        mal_id,
        title
    )

    css_content = (
        css_content.rstrip()
        + "\n\n"
        + block
    )

    save_manual_css(
        config,
        css_content
    )

    print(
        f"     -> Manual template added: "
        f"{config['manual_file']}"
    )


def sync_manual_css_from_errors(
    config,
    error_entries
):
    """
    Makes sure every existing error
    also has a manual CSS placeholder.
    """

    if not error_entries:
        return

    print()
    print(
        "Synchronizing manual "
        "cover templates..."
    )

    for mal_id, entry in (
        error_entries.items()
    ):

        ensure_manual_entry(
            config,
            mal_id,
            entry["title"]
        )


# ============================== #
#      CSS BLOCK GENERATOR       #
# ------------------------------ #

def create_css_block(
    config,
    mal_id,
    title,
    cover_url
):
    """
    Creates an automatic CSS block
    for one anime or manga entry.
    """

    title = safe_title(
        title
    )

    url_type = config[
        "url_type"
    ]

    return f"""/* {title}
   MAL ID: {mal_id}
*/
.data.image .link[href*="/{url_type}/{mal_id}/"] {{
    background-image: url("{cover_url}") !important;
}}

"""


# ============================== #
#         MAL LIST FETCH         #
# ------------------------------ #

def get_mal_list(config):

    print()
    print("=" * 60)

    print(
        f"FETCHING MAL "
        f"{config['name'].upper()} LIST"
    )

    print("=" * 60)

    endpoint = config[
        "mal_endpoint"
    ]

    url = (
        f"{MAL_API}/users/"
        f"{MAL_USERNAME}/"
        f"{endpoint}"
    )

    headers = {
        "X-MAL-CLIENT-ID":
            MAL_CLIENT_ID
    }

    params = {
        "limit": 1000
    }

    media_list = []

    while url:

        response = session.get(
            url,
            headers=headers,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        for item in data.get(
            "data",
            []
        ):

            node = item.get(
                "node",
                {}
            )

            mal_id = node.get(
                "id"
            )

            title = node.get(
                "title"
            )

            if mal_id is None:
                continue

            media_list.append({
                "id": int(mal_id),
                "title": (
                    title
                    or str(mal_id)
                )
            })

        print(
            f"Loaded: "
            f"{len(media_list)} entries"
        )

        url = (
            data
            .get("paging", {})
            .get("next")
        )

        params = None


    # ============================== #
    #       REMOVE DUPLICATES        #
    # ------------------------------ #

    unique = {}

    for media in media_list:

        unique[
            media["id"]
        ] = media

    media_list = list(
        unique.values()
    )

    print()

    print(
        f"Total unique "
        f"{config['name'].lower()} "
        f"entries: "
        f"{len(media_list)}"
    )

    return media_list


# ============================== #
#       ANILIST QUERY BUILD      #
# ------------------------------ #

def build_anilist_query(
    config,
    batch
):
    """
    Builds one GraphQL query containing
    multiple MAL IDs.
    """

    fields = []

    media_type = config[
        "anilist_type"
    ]

    for media in batch:

        mal_id = media[
            "id"
        ]

        alias = anilist_alias(
            mal_id
        )

        fields.append(
            f"""
            {alias}: Media(
                idMal: {mal_id},
                type: {media_type}
            ) {{
                idMal

                title {{
                    romaji
                    english
                }}

                coverImage {{
                    extraLarge
                    large
                }}
            }}
            """
        )

    return (
        "query {\n"
        + "\n".join(fields)
        + "\n}"
    )


# ============================== #
#      ANILIST BATCH REQUEST     #
# ------------------------------ #

def request_anilist_batch(
    config,
    batch,
    error_entries,
    generate_manual
):
    """
    Fetches one AniList batch.

    If AniList returns 404,
    the batch is recursively split
    until the problematic MAL ID
    is isolated.
    """

    query = build_anilist_query(
        config,
        batch
    )

    retries = 0

    while True:

        try:

            response = session.post(
                ANILIST_API,
                json={
                    "query": query
                },
                timeout=60
            )


            # ============================== #
            #          RATE LIMIT           #
            # ------------------------------ #

            if response.status_code == 429:

                retry_after = (
                    response.headers.get(
                        "Retry-After"
                    )
                )

                try:

                    wait_time = int(
                        retry_after
                    )

                except (
                    TypeError,
                    ValueError
                ):

                    wait_time = 60

                wait_time += 2

                print()
                print(
                    f"[RATE LIMIT] "
                    f"Waiting "
                    f"{wait_time} seconds..."
                )
                print()

                time.sleep(
                    wait_time
                )

                continue


            # ============================== #
            #              404              #
            # ------------------------------ #

            if response.status_code == 404:

                print()

                print(
                    f"[404] Problematic batch: "
                    f"{len(batch)} entries"
                )

                if len(batch) == 1:

                    media = batch[0]

                    print(
                        f"[SKIPPED] "
                        f"MAL ID "
                        f"{media['id']} - "
                        f"{media['title']}"
                    )

                    save_error(
                        config,
                        media["id"],
                        media["title"],
                        (
                            "404 / "
                            "No AniList match"
                        ),
                        error_entries,
                        generate_manual
                    )

                    return {}


                middle = (
                    len(batch) // 2
                )

                left_batch = (
                    batch[:middle]
                )

                right_batch = (
                    batch[middle:]
                )

                print(
                    f"Splitting batch: "
                    f"{len(left_batch)} + "
                    f"{len(right_batch)}"
                )

                left_data = (
                    request_anilist_batch(
                        config,
                        left_batch,
                        error_entries,
                        generate_manual
                    )
                )

                right_data = (
                    request_anilist_batch(
                        config,
                        right_batch,
                        error_entries,
                        generate_manual
                    )
                )

                merged = {}

                merged.update(
                    left_data
                )

                merged.update(
                    right_data
                )

                return merged


            # ============================== #
            #         SERVER ERROR          #
            # ------------------------------ #

            if response.status_code >= 500:

                retries += 1

                if retries > MAX_RETRIES:

                    response.raise_for_status()

                wait_time = (
                    retries * 5
                )

                print()
                print(
                    "[ANILIST SERVER ERROR]"
                )

                print(
                    f"HTTP "
                    f"{response.status_code}"
                )

                print(
                    f"Retrying in "
                    f"{wait_time} seconds..."
                )

                time.sleep(
                    wait_time
                )

                continue


            # ============================== #
            #       OTHER HTTP ERROR        #
            # ------------------------------ #

            if response.status_code >= 400:

                print()

                print(
                    f"[HTTP ERROR] "
                    f"{response.status_code}"
                )

                print(
                    response.text[:1000]
                )

                response.raise_for_status()


            # ============================== #
            #           SUCCESS             #
            # ------------------------------ #

            result = response.json()


            # ============================== #
            #      GRAPHQL WARNINGS         #
            # ------------------------------ #

            if result.get(
                "errors"
            ):

                print()

                print(
                    "[ANILIST GRAPHQL WARNING]"
                )

                for error in result[
                    "errors"
                ]:

                    message = error.get(
                        "message",
                        "Unknown GraphQL error"
                    )

                    print(
                        f"  - {message}"
                    )

                print()


            return (
                result.get(
                    "data"
                )
                or {}
            )


        # ============================== #
        #         NETWORK ERROR          #
        # ------------------------------ #

        except (
            requests.ConnectionError,
            requests.Timeout
        ) as error:

            retries += 1

            if retries > MAX_RETRIES:
                raise

            wait_time = (
                retries * 5
            )

            print()
            print(
                "[NETWORK ERROR]"
            )

            print(
                error
            )

            print(
                f"Retrying in "
                f"{wait_time} seconds..."
            )

            print()

            time.sleep(
                wait_time
            )


# ============================== #
#       BATCH PROCESSING         #
# ------------------------------ #

def process_batch(
    config,
    batch,
    data,
    css_content,
    completed_ids,
    error_entries,
    generate_manual
):
    """
    Processes one AniList batch.

    Every successful cover is
    saved immediately.
    """

    added = 0

    for media in batch:

        mal_id = media[
            "id"
        ]


        # ============================== #
        #       ALREADY COMPLETE        #
        # ------------------------------ #

        if mal_id in completed_ids:
            continue


        alias = anilist_alias(
            mal_id
        )

        anilist_media = data.get(
            alias
        )


        # ============================== #
        #           NO MATCH            #
        # ------------------------------ #

        if not anilist_media:

            print(
                f"[NO MATCH] "
                f"{mal_id} - "
                f"{media['title']}"
            )

            save_error(
                config,
                mal_id,
                media["title"],
                "No AniList match",
                error_entries,
                generate_manual
            )

            continue


        # ============================== #
        #          COVER IMAGE          #
        # ------------------------------ #

        cover_data = (
            anilist_media.get(
                "coverImage"
            )
            or {}
        )

        cover = (
            cover_data.get(
                "extraLarge"
            )
            or
            cover_data.get(
                "large"
            )
        )


        if not cover:

            print(
                f"[NO COVER] "
                f"{mal_id} - "
                f"{media['title']}"
            )

            save_error(
                config,
                mal_id,
                media["title"],
                "No AniList cover",
                error_entries,
                generate_manual
            )

            continue


        # ============================== #
        #             TITLE             #
        # ------------------------------ #

        title = media.get(
            "title"
        )

        if not title:

            titles = (
                anilist_media.get(
                    "title"
                )
                or {}
            )

            title = (
                titles.get(
                    "english"
                )
                or
                titles.get(
                    "romaji"
                )
                or
                str(mal_id)
            )


        # ============================== #
        #          CSS BLOCK            #
        # ------------------------------ #

        block = create_css_block(
            config,
            mal_id,
            title,
            cover
        )

        css_content = (
            css_content.rstrip()
            + "\n\n"
            + block
        )

        completed_ids.add(
            mal_id
        )

        added += 1


        # ============================== #
        #        IMMEDIATE SAVE         #
        # ------------------------------ #

        save_css(
            config,
            css_content
        )

        print(
            f"[OK] "
            f"{mal_id} - "
            f"{title}"
        )

        print(
            f"     CSS saved | "
            f"Total complete: "
            f"{len(completed_ids)}"
        )


    return (
        css_content,
        added
    )


# ============================== #
#        LIST PROCESSING         #
# ------------------------------ #

def process_list(
    config,
    generate_manual
):

    print()
    print()
    print("#" * 60)

    print(
        f"# PROCESSING "
        f"{config['name'].upper()}"
    )

    print("#" * 60)


    # ============================== #
    #       LOAD EXISTING CSS       #
    # ------------------------------ #

    css_content = load_existing_css(
        config
    )

    completed_ids = load_existing_ids(
        css_content
    )


    # ============================== #
    #      LOAD EXISTING ERRORS     #
    # ------------------------------ #

    error_entries = (
        load_error_entries(
            config
        )
    )


    print()

    print(
        f"Existing covers: "
        f"{len(completed_ids)}"
    )

    print(
        f"Logged errors: "
        f"{len(error_entries)}"
    )


    # ============================== #
    #    SYNC OLD MANUAL ERRORS     #
    # ------------------------------ #

    if generate_manual:

        sync_manual_css_from_errors(
            config,
            error_entries
        )


    # ============================== #
    #         FETCH MAL LIST        #
    # ------------------------------ #

    media_list = get_mal_list(
        config
    )


    # ============================== #
    #      FILTER COMPLETED IDS     #
    # ------------------------------ #

    remaining = [
        media
        for media in media_list
        if media["id"]
        not in completed_ids
    ]


    print()
    print("-" * 60)

    print(
        f"Full {config['name']} list: "
        f"{len(media_list)}"
    )

    print(
        f"Already complete: "
        f"{len(completed_ids)}"
    )

    print(
        f"Remaining: "
        f"{len(remaining)}"
    )

    print(
        f"Previously logged errors: "
        f"{len(error_entries)}"
    )

    print("-" * 60)


    # ============================== #
    #         NOTHING TO DO         #
    # ------------------------------ #

    if not remaining:

        print()
        print("=" * 60)

        print(
            f"ALL "
            f"{config['name'].upper()} "
            f"COVERS ARE COMPLETE"
        )

        print("=" * 60)

        return


    # ============================== #
    #            BATCHES            #
    # ------------------------------ #

    batches = list(
        chunked(
            remaining,
            BATCH_SIZE
        )
    )

    total_batches = len(
        batches
    )

    print()

    print(
        f"Total batches: "
        f"{total_batches}"
    )


    # ============================== #
    #        PROCESS BATCHES        #
    # ------------------------------ #

    for batch_number, batch in enumerate(
        batches,
        start=1
    ):

        print()
        print("=" * 60)

        print(
            f"{config['name'].upper()} "
            f"BATCH "
            f"{batch_number}/"
            f"{total_batches}"
        )

        print(
            f"Entries: "
            f"{len(batch)}"
        )

        print("=" * 60)


        data = request_anilist_batch(
            config,
            batch,
            error_entries,
            generate_manual
        )


        (
            css_content,
            added
        ) = process_batch(
            config,
            batch,
            data,
            css_content,
            completed_ids,
            error_entries,
            generate_manual
        )


        print()

        print(
            "Batch complete."
        )

        print(
            f"New covers: "
            f"{added}"
        )

        print(
            f"Total complete: "
            f"{len(completed_ids)}"
        )

        print(
            f"Logged errors: "
            f"{len(error_entries)}"
        )


        if batch_number < total_batches:

            time.sleep(
                REQUEST_DELAY
            )


    # ============================== #
    #         LIST COMPLETE         #
    # ------------------------------ #

    print()
    print("=" * 60)

    print(
        f"{config['name'].upper()} "
        f"COMPLETE"
    )

    print("=" * 60)

    print()

    print(
        "Automatic CSS:"
    )

    print(
        config[
            "output_file"
        ].resolve()
    )

    print()

    print(
        "Error log:"
    )

    print(
        config[
            "error_file"
        ].resolve()
    )

    if generate_manual:

        print()

        print(
            "Manual CSS:"
        )

        print(
            config[
                "manual_file"
            ].resolve()
        )

    print()

    print(
        f"Successful covers: "
        f"{len(completed_ids)}"
    )

    print(
        f"Logged errors: "
        f"{len(error_entries)}"
    )


# ============================== #
#             MENU               #
# ------------------------------ #

def show_media_menu():

    print()
    print("=" * 60)
    print("BETTER MYANIMELIST COVERS")
    print("=" * 60)

    print()

    print(
        "What would you like "
        "to generate?"
    )

    print()

    print(
        "1 - Anime"
    )

    print(
        "2 - Manga"
    )

    print(
        "3 - Both"
    )

    print()

    while True:

        choice = input(
            "Selection: "
        ).strip()

        if choice in {
            "1",
            "2",
            "3"
        }:

            return choice

        print(
            "Invalid selection. "
            "Please enter 1, 2, or 3."
        )


def show_manual_menu():

    print()

    print(
        "Generate/update manual "
        "cover templates for failed "
        "entries?"
    )

    print()

    print(
        "1 - Yes"
    )

    print(
        "2 - No"
    )

    print()

    while True:

        choice = input(
            "Selection: "
        ).strip()

        if choice == "1":
            return True

        if choice == "2":
            return False

        print(
            "Invalid selection. "
            "Please enter 1 or 2."
        )


# ============================== #
#             MAIN               #
# ------------------------------ #

def main():

    media_choice = (
        show_media_menu()
    )

    generate_manual = (
        show_manual_menu()
    )


    # ============================== #
    #          ANIME ONLY           #
    # ------------------------------ #

    if media_choice == "1":

        process_list(
            CONFIGS["anime"],
            generate_manual
        )


    # ============================== #
    #          MANGA ONLY           #
    # ------------------------------ #

    elif media_choice == "2":

        process_list(
            CONFIGS["manga"],
            generate_manual
        )


    # ============================== #
    #             BOTH             #
    # ------------------------------ #

    elif media_choice == "3":

        process_list(
            CONFIGS["anime"],
            generate_manual
        )

        print()
        print()
        print("=" * 60)

        print(
            "ANIME COMPLETE - "
            "STARTING MANGA"
        )

        print("=" * 60)

        time.sleep(
            REQUEST_DELAY
        )

        process_list(
            CONFIGS["manga"],
            generate_manual
        )


    # ============================== #
    #         ALL COMPLETE         #
    # ------------------------------ #

    print()
    print()
    print("#" * 60)

    print(
        "# ALL REQUESTED TASKS COMPLETED"
    )

    print("#" * 60)


# ============================== #
#         PROGRAM START          #
# ------------------------------ #

if __name__ == "__main__":

    try:

        main()


    # ============================== #
    #          MANUAL STOP          #
    # ------------------------------ #

    except KeyboardInterrupt:

        print()
        print()

        print("=" * 60)

        print(
            "STOPPED"
        )

        print("=" * 60)

        print()

        print(
            "All successfully processed "
            "covers have already been saved."
        )

        print(
            "All detected errors have also "
            "been saved to the appropriate "
            "error log."
        )


    # ============================== #
    #          FATAL ERROR          #
    # ------------------------------ #

    except Exception as error:

        print()
        print()

        print("=" * 60)

        print(
            "FATAL ERROR"
        )

        print("=" * 60)

        print()

        print(
            repr(error)
        )

        print()

        print(
            "Previously generated CSS, "
            "manual templates, and error "
            "logs have not been lost."
        )