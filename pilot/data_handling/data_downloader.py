import requests
import os

def download_and_move_files():
    """
    Downloads and moves files to the 'data' directory.
    """
    # Create the 'data' directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')

    # List of file URLs to download
    urls = [
        "https://trddev.com/hackathon-2025/barber-motorsports-park.zip",
        "https://trddev.com/hackathon-2025/circuit-of-the-americas.zip",
        "https://trddev.com/hackathon-2025/indianapolis.zip",
        "https://trddev.com/hackathon-2025/road-america.zip",
        "https://trddev.com/hackathon-2025/sebring.zip",
        "https://trddev.com/hackathon-2025/sonoma.zip",
        "https://trddev.com/hackathon-2025/virginia-international-raceway.zip"
    ]

    # Download each file and save it to the 'data' directory
    for url in urls:
        filename = os.path.join('data', os.path.basename(url))
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"Downloaded {filename}")

if __name__ == '__main__':
    download_and_move_files()
