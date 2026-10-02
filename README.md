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

## Generated Files

The generator creates separate files for Anime and Manga.

### Anime

```text
mal-anime-covers.css
mal-anime-covers-error.txt
mal-anime-covers-manual.css
```

### Manga

```text
mal-manga-covers.css
mal-manga-covers-error.txt
mal-manga-covers-manual.css
```

### File Purpose

#### Automatic CSS

`mal-anime-covers.css` and `mal-manga-covers.css`

These are the automatically generated cover files.

They contain successful AniList cover matches and can be used directly in your MyAnimeList custom CSS.

Example:

```css
/* Example Anime
   MAL ID: 12345
*/
.data.image .link[href*="/anime/12345/"] {
    background-image: url("https://s4.anilist.co/...") !important;
}
```

#### Error Logs

`mal-anime-covers-error.txt` and `mal-manga-covers-error.txt`

These files contain entries that could not be matched successfully or did not have an available AniList cover.

Example:

```text
MAL ID: 12345 | Title: Example Title | Error: No AniList match
```

Error log entries are not automatically removed.

If an entry fails during one run but later becomes available from AniList, the old error entry may remain in the error log.

This is expected behavior.

#### Manual CSS

`mal-anime-covers-manual.css` and `mal-manga-covers-manual.css`

These files contain optional manual cover templates for failed entries.

They are only created or updated if manual template generation is enabled.

See the **Manual Cover Editing** section below for instructions on adding your own cover URLs.

---

## Resume Behavior

The generator checks the existing automatic CSS file before requesting covers from AniList.

If a MAL ID is already present in:

```text
mal-anime-covers.css
```

or:

```text
mal-manga-covers.css
```

that entry is skipped.

This means the generator can be stopped and restarted without downloading already completed entries again.

Successful covers are saved during processing, so previously completed work is preserved if the program is interrupted.

---

## Using the CSS on MyAnimeList

The generated CSS files are designed to be used with MyAnimeList custom list CSS.

You can either copy the generated CSS directly into your list style or host the CSS file somewhere accessible and import it.

### Automatic Covers

For Anime:

```css
@import url("YOUR-AUTOMATIC-ANIME-CSS-URL");
```

For Manga:

```css
@import url("YOUR-AUTOMATIC-MANGA-CSS-URL");
```

### Manual Overrides

If you use manual cover overrides, import the manual CSS after the automatic CSS.

Anime example:

```css
@import url("YOUR-AUTOMATIC-ANIME-CSS-URL");
@import url("YOUR-MANUAL-ANIME-CSS-URL");
```

Manga example:

```css
@import url("YOUR-AUTOMATIC-MANGA-CSS-URL");
@import url("YOUR-MANUAL-MANGA-CSS-URL");
```

The manual CSS should come after the automatic CSS so your manually selected covers can override automatically generated covers when necessary.

---

## Hosting the Generated CSS

The generated CSS must be available through a direct public URL if you want to use it with `@import`.

You can host the files using GitHub together with a compatible CDN or another service that serves raw CSS files.

For example, if you keep your generated files in a public GitHub repository, you can use a CDN URL that points to the CSS file.

Make sure the URL returns the actual CSS content and not an HTML webpage.

---

## Manual Cover Editing

If manual cover template generation is enabled, failed entries are added to the corresponding manual CSS file.

Example:

```css
/* Example Anime
   MAL ID: 12345
*/
.data.image .link[href*="/anime/12345/"] {
    background-image: url("ADD-MANUAL-COVER-URL-HERE") !important;
}
```

For manga, the generated selector uses `/manga/` instead of `/anime/`.

Replace:

```text
ADD-MANUAL-COVER-URL-HERE
```

with your own direct image URL.

Example:

```css
background-image: url("https://example.com/my-cover.jpg") !important;
```

Do not remove the MAL ID comment if you want the generator to continue recognizing that entry as already present in the manual CSS.

Existing manual entries are not overwritten automatically.

If you have already replaced the placeholder with your own image URL, the generator preserves that manual entry.

Manual placeholder entries are not automatically removed if the same title later becomes available through AniList.

This is expected behavior.

---

## Personal Directory

This repository contains a `personal/` directory.

The files inside this directory are used by the repository owner for their own MyAnimeList lists.

They may include:

- generated anime cover CSS
- generated manga cover CSS
- manual cover overrides
- list-specific CSS
- other personal MyAnimeList customizations

These files are not required to use the generator.

The `personal/` directory is included so the repository owner can keep their own list files in the same repository without mixing them with the reusable public generator.

If you only want to use the generator yourself, you can ignore the entire `personal/` directory.

---

## Repository Structure

```text
MyAnimeList-AniList-Better-Cover-Generator/
│
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
├── MyAnimeList-AniList-Better-Cover-Generator.py
│
└── personal/
    ├── README.md
    ├── mal-anime-covers.css
    ├── mal-anime-covers-manual.css
    ├── mal-manga-covers.css
    └── mal-manga-covers-manual.css
```

The main generator is:

```text
MyAnimeList-AniList-Better-Cover-Generator.py
```

Files inside the `personal/` directory are repository-owner-specific and are not required for normal use.

---

## Notes

This is an unofficial community project.

It is not affiliated with, endorsed by, or maintained by MyAnimeList or AniList.

MyAnimeList and AniList are separate services with their own APIs, availability, terms, and rate limits.

API behavior may change over time.

---

## License

This project is licensed under the MIT License.

See the `LICENSE` file for details.
