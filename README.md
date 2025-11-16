# curseforge-MDK-Install-All-Brute-Force
Multi-threaded mass downloader for ALL Minecraft Forge MDK versions. Features 10 concurrent downloads, progress tracking, auto-resume, and direct Maven repository access bypassing AdFocus redirects. Downloads hundreds of MDKs in minutes. No ads, no redirects, just raw speed. 
# Minecraft Forge MDK Downloader

A Python script that downloads all Minecraft Forge MDK versions automatically.

## What it does

Downloads Forge MDK files directly from Maven repositories without going through AdFocus redirects. Uses multi-threading to download multiple files at once. Doesn't actually "brute-force" things, just have no idea what else to call it, let me know any good names.

## Requirements

- Python 3.7 or higher
- requests library
- beautifulsoup4 library

## Installation

```bash
pip install requests beautifulsoup4
```

## Usage

1: Make the repository your own first on line 14, within the quotes

2: Run the script:

```bash
python forge_mdk_downloader.py
```

Files are downloaded to whatever you set your directory to, but as an example, I put in "C:\Users\UwU\Downloads"

## Features

- Downloads 10 files simultaneously
- Saves progress automatically
- Resumes if interrupted
- Skips already downloaded files
- Organizes files by Minecraft version

## How it works

1. Scrapes version information from files.minecraftforge.net
2. Constructs direct Maven repository URLs
3. Downloads files using ThreadPoolExecutor (10 threads)
4. Saves progress to .download_progress.json
5. Organizes downloads into MC_[version] folders

## Technical details

### URL Pattern

```
https://maven.minecraftforge.net/net/minecraftforge/forge/{MC_VERSION}-{FORGE_VERSION}/forge-{MC_VERSION}-{FORGE_VERSION}-mdk.zip
```

Example:
```
https://maven.minecraftforge.net/net/minecraftforge/forge/1.20.1-47.4.10/forge-1.20.1-47.4.10-mdk.zip
```

### Thread safety

Uses `threading.Lock()` to protect shared statistics and progress data during concurrent operations.

### Progress tracking

Progress is stored in JSON format:
```json
{
  "1.20.1-47.4.10": "completed",
  "1.19.4-45.1.0": "failed"
}
```

## Configuration

Edit these variables in the script:

```python
MDK_DIR = r"C:\Users\willi\Downloads\Java\MDKs"  # Change download location
max_workers=10  # Change number of concurrent downloads
```

## Supported versions

Minecraft 1.1 through 1.21+ (all versions with Forge support)

## Error handling

- HTTP errors (404, 403, etc.) are logged and marked as failed
- Timeouts are caught and marked as failed
- Failed downloads can be retried by running the script again

## Stopping and resuming

Press Ctrl+C to stop. Run the script again to resume from where it stopped.

## Performance

Typical download stats:
- Speed: 8-15 files per second
- Total files: 500+ MDKs
- Total size: 15-20 GB
- Time: 10-30 minutes (depends on connection)

## Common issues

**Missing dependencies:**
```bash
pip install requests beautifulsoup4
```

**Permission errors:**
Run as administrator or change the download directory.

**404 errors:**
Some old versions may not exist on Maven. This is normal.

## License

MIT License

## Disclaimer

This is an unofficial tool. Not affiliated with or endorsed by the Minecraft Forge team.
