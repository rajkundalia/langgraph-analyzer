"""
LangGraph Multi-Agent Research Paper Analyzer

A demonstration project showcasing LangGraph's capabilities for building
multi-agent workflows with human-in-the-loop approval, state management,
and streaming outputs.
"""

__version__ = "1.0.0"
__author__ = "LangGraph Learning Project"

from .state import State, create_initial_state
from .graph_builder import build_graph
from .utils import load_pdf_text, save_report

__all__ = [
    "State",
    "create_initial_state",
    "build_graph",
    "load_pdf_text",
    "save_report",
]