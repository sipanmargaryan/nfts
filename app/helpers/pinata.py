from typing import Dict

import requests

from app.settings import PINATA_JWT

HEADERS = {
    "Authorization": f"Bearer {PINATA_JWT}",
}


def upload_file_to_pinata(file_bytes, filename: str) -> str:
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    files = {
        "file": (filename, file_bytes),
    }
    response = requests.post(url, headers=HEADERS, files=files)
    response.raise_for_status()
    ipfs_hash = response.json()["IpfsHash"]
    return f"ipfs://{ipfs_hash}"


def upload_json_to_pinata(metadata: Dict) -> str:
    url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"

    payload = {
        "pinataMetadata": {
            "name": f"{metadata.get('company_id')}-{metadata.get('name')}"
        },
        "pinataContent": metadata,
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    ipfs_hash = response.json()["IpfsHash"]
    return f"ipfs://{ipfs_hash}"
