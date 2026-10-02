# MyAnimeList AniList Better Cover Generator

Generate higher-resolution MyAnimeList anime and manga cover CSS using AniList.

This Python script reads your MyAnimeList anime and/or manga list, matches entries using their MAL IDs through the AniList API, and generates CSS rules that can be used to replace the default MyAnimeList cover images.

---

## Features

- Anime list support
- Manga list support
- Generate Anime, Manga, or both
- Uses MyAnimeList IDs for matching
- Fetches AniList `extraLarge` covers when available
- Falls back to AniList `large` covers
- Batch processing
- AniList rate-limit handling
- Retry handling for temporary network and server errors
- Automatically isolates problematic entries when a batch fails
- Resumes from already generated CSS files
- Saves successful covers immediately
- Separate error logs
- Optional manual CSS templates for failed entries
- Existing manually edited cover URLs are preserved

---

## Requirements

- Python 3
- A MyAnimeList account
- A MyAnimeList API Client ID
- Internet connection

Install the required Python package with:

```bash
pip install -r requirements.txt
```

or:

```bash
pip install requests
```

---

## MyAnimeList API Setup

The generator uses the MyAnimeList API to read your anime and manga lists.

You need your own MyAnimeList API Client ID.

Create a MyAnimeList API client from your MyAnimeList account and copy the generated **Client ID**.

Then open:

```text
MyAnimeList-AniList-Better-Cover-Generator.py
```

and edit:

```python
MAL_USERNAME = "YOUR_MAL_USERNAME"
MAL_CLIENT_ID = "YOUR_MAL_CLIENT_ID"
```

Example:

```python
MAL_USERNAME = "ExampleUser"
MAL_CLIENT_ID = "your_client_id_here"
```

### Security

Only the MyAnimeList Client ID is required by this script.

Do not add your Client Secret to the script.

Do not commit passwords, private tokens, API secrets, or other sensitive credentials to GitHub.

---
