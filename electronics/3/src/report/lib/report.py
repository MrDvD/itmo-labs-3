from pathlib import Path
import tempfile
from typing import Any, Dict
import urllib.request
import urllib.error

class ReportFiller:
    @staticmethod
    def get_api_url(cfg: Dict[str, Any], endpoint_key: str) -> str:
        return f"http://{cfg['api']['host']}:{cfg['api']['port']}{cfg['api']['prefix']}{cfg['api'][endpoint_key]}"

    @staticmethod
    def generate_images(url: str) -> None:
        with urllib.request.urlopen(urllib.request.Request(url)) as response:
            response.read()
    
    @staticmethod
    def get_schemas_paths(
        context: Dict[str, Any],
        url: str,
    ) -> Dict[str, Any]:
        tmpdir = Path(tempfile.mkdtemp(prefix="schemas_")).resolve()
        paths = list()

        for n in (1, 2, 3):
            img_url = f"{url.rstrip('/')}/{n}"
            try:
                with urllib.request.urlopen(img_url) as resp:
                    path = tmpdir / f"schema{n}.png"
                    path.write_bytes(resp.read())
                    paths.append(str(path))
            except urllib.error.HTTPError:
                print(f"Failed to download schema {n} from {img_url}.")
                continue

        new_context = context.copy()
        new_context["schemas_paths"] = paths
        print(paths)
        return new_context