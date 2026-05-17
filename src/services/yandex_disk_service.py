from typing import List, BinaryIO, Tuple
import requests


class YandexDiskServices:
    def __init__(self, token) -> None:
        self.token = token
        self.headers = {"Authorization": f"OAuth {self.token}"}

    def list_root_dirs(self) -> List[Tuple[str, str]]:
        url = "https://cloud-api.yandex.net/v1/disk/resources"
        params = {
            "path": "/",
            "fields": "_embedded.items.name,_embedded.items.path,_embedded.items.type",
        }

        response = requests.get(url, params=params, headers=self.headers)
        response.raise_for_status()

        items = response.json()["_embedded"]["items"]
        folders = [
            (item["name"], item["path"]) for item in items if item["type"] == "dir"
        ]
        return folders

    def upload_file(self, file: BinaryIO, target_dir: str) -> None:
        get_uploader_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        params = {
            "path": target_dir,
            "overwrite": "true"
        }
        response = requests.get(get_uploader_url, params=params, headers=self.headers)
        response.raise_for_status()

        uploader_url = response.json()["href"]
        upload_response = requests.put(uploader_url, data=file)
        upload_response.raise_for_status()
