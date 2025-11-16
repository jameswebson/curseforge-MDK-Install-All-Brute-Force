import os
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import json

# Target installation directory
#MAKE THIS YOUR OWN DIRECTORY OR IT WON'T WORK
#ignore my directory, that's an example
MDK_DIR = r"C:\Users\UwU\Downloads"

# Progress tracking file
PROGRESS_FILE = os.path.join(MDK_DIR, ".download_progress.json")

# Create directory if it doesn't exist
Path(MDK_DIR).mkdir(parents=True, exist_ok=True)

# Maven base URL - DIRECT DOWNLOAD, NO ADFOCUS!
MAVEN_BASE = "https://maven.minecraftforge.net/net/minecraftforge/forge"
FORGE_FILES_URL = "https://files.minecraftforge.net/net/minecraftforge/forge"

# Thread-safe counters
lock = threading.Lock()
stats = {
    'downloaded': 0,
    'skipped': 0,
    'failed': 0
}

def load_progress():
    """Load previous download progress"""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_progress(progress_data):
    """Save current download progress"""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress_data, f, indent=2)

def get_all_minecraft_versions():
    """Get all Minecraft versions that have Forge"""
    versions = [
        # Modern versions (1.13+)
        "1.21.4", "1.21.3", "1.21.1", "1.21",
        "1.20.6", "1.20.5", "1.20.4", "1.20.3", "1.20.2", "1.20.1", "1.20",
        "1.19.4", "1.19.3", "1.19.2", "1.19.1", "1.19",
        "1.18.2", "1.18.1", "1.18",
        "1.17.1", "1.17",
        "1.16.5", "1.16.4", "1.16.3", "1.16.2", "1.16.1",
        "1.15.2", "1.15.1", "1.15",
        "1.14.4", "1.14.3", "1.14.2", "1.14.1",
        "1.13.2", "1.13",
        # Legacy versions (pre-1.13)
        "1.12.2", "1.12.1", "1.12",
        "1.11.2", "1.11",
        "1.10.2", "1.10",
        "1.9.4", "1.9",
        "1.8.9", "1.8.8", "1.8",
        "1.7.10", "1.7.2",
        "1.6.4", "1.6.2", "1.6.1",
        "1.5.2", "1.5.1", "1.5",
        "1.4.7", "1.4.6", "1.4.5", "1.4.4", "1.4.2",
        "1.3.2", "1.2.5", "1.1"
    ]
    return versions

def get_forge_versions_from_page(mc_version):
    """Scrape Forge version numbers from the HTML page"""
    url = f"{FORGE_FILES_URL}/index_{mc_version}.html"
    
    try:
        response = requests.get(url, timeout=30)
        
        if response.status_code != 200:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        forge_versions = []
        
        # Find all version numbers in the table
        rows = soup.find_all('tr')
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) > 0:
                version_text = cells[0].get_text(strip=True)
                
                # Match Forge version pattern
                if re.match(r'^\d+\.\d+\.\d+', version_text):
                    forge_versions.append(version_text)
        
        # Alternative: look for download links
        if not forge_versions:
            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href']
                match = re.search(rf'{re.escape(mc_version)}-(\d+\.\d+\.\d+)', href)
                if match:
                    version = match.group(1)
                    if version not in forge_versions:
                        forge_versions.append(version)
        
        return forge_versions
        
    except Exception as e:
        return []

def construct_maven_url(mc_version, forge_version):
    """Construct direct Maven download URL - BYPASSES ADFOCUS"""
    full_version = f"{mc_version}-{forge_version}"
    filename = f"forge-{full_version}-mdk.zip"
    url = f"{MAVEN_BASE}/{full_version}/{filename}"
    return url

def download_file(url, destination):
    """Download a file from URL to destination"""
    try:
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()
        
        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
        
    except:
        return False

def download_mdk_task(mc_version, forge_version, progress_data):
    """Download a specific MDK - designed for threading"""
    version_key = f"{mc_version}-{forge_version}"
    
    # Check if already completed
    if progress_data.get(version_key) == "completed":
        with lock:
            stats['skipped'] += 1
            print(f"⊙ SKIP: {version_key}")
        return "skipped"
    
    # Create subdirectory
    version_dir = os.path.join(MDK_DIR, f"MC_{mc_version}")
    Path(version_dir).mkdir(parents=True, exist_ok=True)
    
    filename = f"forge-{mc_version}-{forge_version}-mdk.zip"
    destination = os.path.join(version_dir, filename)
    
    # Check if file exists
    if os.path.exists(destination):
        with lock:
            stats['skipped'] += 1
            progress_data[version_key] = "completed"
            print(f"⊙ EXISTS: {version_key}")
        return "skipped"
    
    # Construct direct Maven URL
    maven_url = construct_maven_url(mc_version, forge_version)
    
    # Download
    if download_file(maven_url, destination):
        with lock:
            stats['downloaded'] += 1
            progress_data[version_key] = "completed"
            print(f"✓ SUCCESS: {version_key}")
        return "success"
    else:
        with lock:
            stats['failed'] += 1
            progress_data[version_key] = "failed"
            print(f"✗ FAILED: {version_key}")
        return "failed"

def main():
    print("="*70)
    print("Minecraft Forge MDK Mass Downloader")
    print("MAXIMUM SPEED MODE - MULTI-THREADED DOWNLOADS!")
    print("="*70)
    print(f"Target Directory: {MDK_DIR}\n")
    
    # Load previous progress
    print("Loading previous progress...")
    progress_data = load_progress()
    completed_count = sum(1 for v in progress_data.values() if v == "completed")
    print(f"Found {completed_count} previously completed downloads\n")
    
    mc_versions = get_all_minecraft_versions()
    
    # Build complete task list
    print("Building download queue...")
    all_tasks = []
    
    for mc_version in mc_versions:
        print(f"  Scanning MC {mc_version}...", end=' ')
        forge_versions = get_forge_versions_from_page(mc_version)
        if forge_versions:
            print(f"Found {len(forge_versions)} versions")
            for forge_version in forge_versions:
                all_tasks.append((mc_version, forge_version))
        else:
            print("None found")
    
    print(f"\nTotal tasks in queue: {len(all_tasks)}")
    print(f"Starting downloads with 10 concurrent threads...\n")
    print("="*70)
    
    start_time = time.time()
    
    # Multi-threaded downloading - MAX SPEED!
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(download_mdk_task, mc_ver, forge_ver, progress_data): (mc_ver, forge_ver)
            for mc_ver, forge_ver in all_tasks
        }
        
        completed = 0
        for future in as_completed(futures):
            completed += 1
            
            # Save progress every 10 downloads
            if completed % 10 == 0:
                save_progress(progress_data)
                elapsed = time.time() - start_time
                rate = completed / elapsed
                remaining = len(all_tasks) - completed
                eta = remaining / rate if rate > 0 else 0
                
                print(f"\n[{completed}/{len(all_tasks)}] Rate: {rate:.1f}/s | ETA: {eta/60:.1f}m")
    
    # Final save
    save_progress(progress_data)
    
    elapsed = time.time() - start_time
    
    print(f"\n{'='*70}")
    print(f"FINAL SUMMARY:")
    print(f"  ✓ Downloaded: {stats['downloaded']}")
    print(f"  ⊙ Skipped: {stats['skipped']}")
    print(f"  ✗ Failed: {stats['failed']}")
    print(f"  TOTAL: {len(all_tasks)}")
    print(f"  TIME: {elapsed/60:.2f} minutes")
    print(f"  RATE: {len(all_tasks)/elapsed:.2f} files/second")
    print(f"{'='*70}")
    print(f"\nAll MDKs saved to: {MDK_DIR}")
    print("MDKs are organized by Minecraft version in subdirectories")
    print("\n🔥 MAXIMUM SPEED ACHIEVED! 🔥")

if __name__ == "__main__":

    main()
