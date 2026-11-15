import os
import common.config as config
from lib.artifacts import ArtifactsFiller
from typing import Any, Dict

from report.lib.report import ReportFiller

if __name__ == "__main__":
    cfg = config.load('config.yml')

    pics_path = os.path.join(cfg['report']['dir'], 'pics')
    os.makedirs(pics_path, exist_ok=True)

    context: Dict[str, Any] = {
        'variant_number': cfg['variant_num'],
    }

    ReportFiller.generate_images(
        ReportFiller.get_api_url(cfg, 'generate_images_endpoint')
    )

    context = ReportFiller.get_schemas_paths(
        context,
        ReportFiller.get_api_url(cfg, 'schemas_endpoint'),
    )

    artifacts = ArtifactsFiller(context, [cfg['report']['dir']])
    artifacts.compile_patterns()