import os
import lib.config as config
from lib.artifacts import ArtifactsFiller
from lib.report import ReportFiller
from typing import Any, Dict

if __name__ == "__main__":
  cfg = config.load('config.yml')
  
  context: Dict[str, Any] = {
    'variant_number': cfg['variant_num'],
  }

  pattern_path = os.path.join(cfg['report_dir'], 'sections', 'algorithms', 'genetic_iteration.j2')
  pics_path = os.path.join(cfg['report_dir'], 'pics')
  os.makedirs(pics_path, exist_ok=True)
  population_diagram_path = os.path.join(pics_path, 'population.pdf')
  colony_diagram_path = os.path.join(pics_path, 'colony.pdf')

  report = ReportFiller(context, cfg['infinity'])
  report.fill_task(1, matrix_1)
  report.fill_task(2, matrix_2)
  report.fill_initial_population(init_population, compute_goal_1)
  report.fill_genetic_descriptive(log_gene[:3], pattern_path)
  report.draw_population_diagram(log_gene, population_diagram_path)
  report.draw_colony_diagram(log_ant, colony_diagram_path)

  artifacts = ArtifactsFiller(context, cfg['report_dir'])
  artifacts.compile_patterns()