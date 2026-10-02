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

The generator uses the MyAnimeList API to read the anime and manga lists associated with your MyAnimeList account.

To use the generator, you need your own MyAnimeList API Client ID.

### 1. Sign in to MyAnimeList

Sign in to the MyAnimeList account whose anime or manga list you want to process.

Your MyAnimeList username will later be added to the Python script.

---

### 2. Open the MyAnimeList API Client Settings

Open the MyAnimeList API client configuration page while signed in to your account.

Create a new API client/application.

The exact wording of the available fields may change over time, but for a personal cover generator you can use a simple non-commercial/personal configuration.

Example values:

```text
App Name:
MyAnimeList Better Cover Generator

App Description:
Personal non-commercial tool for generating MyAnimeList cover CSS using AniList.

App Type / Purpose:
Hobbyist / Personal use

Commercial / Non-Commercial:
Non-commercial
```

If MyAnimeList asks for additional information that is not required for your use case, use appropriate personal/non-commercial values.

---

### 3. Copy Your Client ID

After creating the API client, MyAnimeList will provide a **Client ID**.

The generator only needs this Client ID.

You do not need to add the Client Secret to this script.

Keep your Client Secret private.

---

### 4. Configure the Python Script

Open:

```text
MyAnimeList-AniList-Better-Cover-Generator.py
```

Near the top of the file, find:

```python
MAL_USERNAME = "YOUR_MAL_USERNAME"
MAL_CLIENT_ID = "YOUR_MAL_CLIENT_ID"
```

Replace them with your own values.

Example:

```python
MAL_USERNAME = "ExampleUser"
MAL_CLIENT_ID = "your_client_id_here"
```

`MAL_USERNAME` must be the MyAnimeList username whose lists you want the script to read.

`MAL_CLIENT_ID` must be the Client ID created from your MyAnimeList API application.

---

### 5. Do Not Add Your Client Secret

This script does not require your MyAnimeList Client Secret.

Do not add it to:

```text
MyAnimeList-AniList-Better-Cover-Generator.py
```

Do not upload or commit your Client Secret to GitHub.

The same applies to passwords, private access tokens, API secrets, or other sensitive credentials.

---

### 6. Install the Required Python Package

From a terminal or command prompt opened in the repository directory, run:

```bash
pip install -r requirements.txt
```

Alternatively:

```bash
pip install requests
```

---

### 7. Run the Generator

Run:

```bash
python MyAnimeList-AniList-Better-Cover-Generator.py
```

On some systems, you may need to use:

```bash
python3 MyAnimeList-AniList-Better-Cover-Generator.py
```

The generator will display:

```text
What would you like to generate?

1 - Anime
2 - Manga
3 - Both
```

Choose the list type you want to process.

The generator will then ask:

```text
Generate/update manual cover templates for failed entries?

1 - Yes
2 - No
```

Choose `1` if you want the script to create manual CSS placeholders for entries that could not automatically receive a cover.

Choose `2` if you only want the automatically generated cover CSS and error log.

---

### API Notes

The script uses the MyAnimeList API only to retrieve your anime and manga list entries and their MAL IDs.

Cover images are then requested from AniList using those MAL IDs.

The general process is:

```text
MyAnimeList account
        |
        v
MyAnimeList API
        |
        v
Anime / Manga list + MAL IDs
        |
        v
AniList API
        |
        v
Higher-resolution cover URLs
        |
        v
Generated MyAnimeList CSS
```

The script sends your MyAnimeList Client ID using the API request headers.

Your Client Secret is not required by the generator.

---

### Troubleshooting MyAnimeList API Access

If the script cannot retrieve your MyAnimeList list, check the following:

- `MAL_USERNAME` is spelled correctly.
- `MAL_CLIENT_ID` contains your actual Client ID.
- You did not accidentally paste the Client Secret instead of the Client ID.
- Your MyAnimeList API application still exists and is active.
- Your internet connection is working.
- Your MyAnimeList list is accessible through your account/API configuration.
- The MyAnimeList API is currently available.

If you receive an authentication-related HTTP error, verify your Client ID first.

If MyAnimeList changes its API or developer settings in the future, the setup process may differ slightly from the instructions above.

---

### Security Reminder

Before uploading your own modified version of the script to a public repository, make sure these values have been reset:

```python
MAL_USERNAME = "YOUR_MAL_USERNAME"
MAL_CLIENT_ID = "YOUR_MAL_CLIENT_ID"
```

Never publish:

- your Client Secret
- passwords
- private tokens
- session cookies
- authentication headers
- other private credentials

---
