from pathlib import Path


def setup_download_directory():
    download_dir = Path(__file__).resolve().parent.parent / "downloads"
    download_dir.mkdir(parents=True, exist_ok=True)
    print(f"Download directory set up at: {download_dir}")
