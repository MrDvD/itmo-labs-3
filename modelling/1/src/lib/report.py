from typing import Dict, List, Optional, Callable, Tuple
from jinja2 import Template
import matplotlib.pyplot as plt

class ReportFiller:
  def __init__(self, context: Dict[str, str]):
    self.context: Dict[str, str] = context