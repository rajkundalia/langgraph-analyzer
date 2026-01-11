"""
Agent modules for research paper analysis.

Each agent specializes in a specific aspect of paper analysis:
- Claims Extractor: Identifies key claims and hypotheses
- Methodology Analyzer: Evaluates research methods
- Limitations Finder: Identifies weaknesses and limitations
- Synthesizer: Combines analyses into comprehensive report
"""

from .claims_extractor import claims_extractor_agent
from .methodology_analyzer import methodology_analyzer_agent
from .limitations_finder import limitations_finder_agent
from .synthesizer import synthesizer_agent

__all__ = [
    "claims_extractor_agent",
    "methodology_analyzer_agent",
    "limitations_finder_agent",
    "synthesizer_agent",
]
