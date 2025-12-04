from pathlib import Path
import zipfile
import sys

import requests
from tqdm import tqdm

sys.path.insert(0, Path(__file__).parent.__str__())
sys.path.insert(0, (Path(__file__).parent / "ci").__str__())

from ci.install import get_dotnet_platform_tag

repo = "MaaXYZ/MaaFramework"
ghproxy = "https://gh-proxy.natsuu.top/"


def get_release_info(repo, pre_release=False):
    api_url = f"https://api.github.com/repos/{repo}/releases"
    print(f"Fetching release info from {api_url}")
    response = requests.get(api_url)
    response.raise_for_status()
    releases = response.json()
    if pre_release:
        return releases[0]  # Return the latest pre-release
    else:
        for release in releases:
            if not release.get("prerelease", False):
                return release  # Return the latest stable release
    return None


def download_file(url, dest_path):
    print(f"Downloading from {url} to {dest_path}")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(dest_path, "wb") as out_file:
        for chunk in tqdm(response.iter_content(chunk_size=8192)):
            out_file.write(chunk)


def main():
    release_info = get_release_info(repo, pre_release=False)
    if not release_info:
        print("No release found.")
        return

    assets = release_info.get("assets", [])
    if not assets:
        print("No assets found in the latest release.")
        return

    # Download the first asset as an example
    tag = get_dotnet_platform_tag()
    asset = next((a for a in assets if tag in a["name"]), None)
    download_url = ghproxy + asset["browser_download_url"]
    dest_path = asset["name"]

    print(f"Downloading {asset['name']} from {download_url}...")
    download_file(download_url, dest_path)
    print("Download completed.")

    print(f"Extracting {dest_path}...")
    with zipfile.ZipFile(dest_path, "r") as zip_ref:
        extract_path = Path("deps")
        zip_ref.extractall(extract_path)
        print(f"Extracted to {extract_path}.")

    Path(dest_path).unlink()  # Remove the zip file after extraction


if __name__ == "__main__":
    main()
