"""
State Schema for LangGraph Multi-Agent Research Paper Analyzer

This module defines the application state that flows through the entire workflow.
In LangGraph, state is the core mechanism for passing information between nodes
(agents). Each node receives the current state and returns an updated state.

Key LangGraph Concepts:
- State is immutable: nodes return new state dictionaries
- State accumulates: each agent adds its analysis to the state
- State enables checkpointing: can save and resume from any point
- TypedDict provides type safety and IDE support
"""

from typing import TypedDict, Optional


class State(TypedDict, total=False):
    """
    Application state schema for the research paper analysis workflow.

    This TypedDict defines all fields that can be present in the state as it
    flows through the multi-agent pipeline. Using TypedDict provides:
    - Type hints for better IDE support
    - Runtime type checking capabilities
    - Clear documentation of state structure

    The 'total=False' parameter means not all fields need to be present initially.
    This is important because state is built up progressively as agents add their
    analysis results.

    State Flow Through Workflow:
    1. START: paper_text, paper_title initialized
    2. Claims Extractor: adds 'claims'
    3. Methodology Analyzer: adds 'methodology'
    4. Limitations Finder: adds 'limitations'
    5. Synthesizer: adds 'final_report'
    6. Human Review: adds 'human_approved'
    """

    # === Input Data ===
    paper_text: str
    """
    Full text content extracted from the research paper PDF.
    This is the source material that all agents analyze.
    Populated at workflow initialization.
    """

    paper_title: str
    """
    Title of the research paper for reference and reporting.
    Used in progress messages and output file naming.
    Populated at workflow initialization.
    """

    # === Agent Analysis Results ===
    claims: Optional[str]
    """
    Key claims and hypotheses extracted by the Claims Extractor Agent.
    Contains 3-5 main contributions or testable claims from the paper.
    Format: Numbered list with brief explanations.
    Populated after: claims_extractor node
    """

    methodology: Optional[str]
    """
    Research methodology analysis by the Methodology Analyzer Agent.
    Describes methods, data sources, experimental design, and approach.
    Format: Structured analysis (Method Type, Data, Analysis Approach).
    Populated after: methodology_analyzer node
    """

    limitations: Optional[str]
    """
    Study limitations and weaknesses identified by the Limitations Finder Agent.
    Constructive critique of potential biases, scope, and methodological issues.
    Format: Categorized list (Sample Size, Methodology, Scope, etc.).
    Populated after: limitations_finder node
    """

    final_report: Optional[str]
    """
    Comprehensive analysis report synthesized by the Synthesizer Agent.
    Combines all agent analyses into coherent executive summary.
    Format: Structured report with sections for claims, methodology,
    limitations, and overall assessment.
    Populated after: synthesizer node
    """

    # === Human-in-the-Loop Fields ===
    human_approved: Optional[bool]
    """
    Human approval decision for the final report.
    - True: Report approved, will be saved
    - False: Report rejected, workflow ends without saving
    - None: Not yet reviewed (default)

    This field enables conditional routing in the workflow:
    - If True: route to END (success)
    - If False: route to END (rejected)

    In more advanced implementations, this could be extended to:
    - 'needs_revision': Loop back to synthesizer
    - 'needs_clarification': Request specific improvements

    Populated after: human_review node (via user input)
    """

    # === Metadata and Tracking ===
    current_step: Optional[str]
    """
    Current workflow step for progress tracking and debugging.
    Updated by each agent to show which node is executing.
    Example values: "claims_extraction", "methodology_analysis", etc.
    Useful for: progress displays, logging, error tracking
    """

    error_message: Optional[str]
    """
    Error message if any agent fails during execution.
    Allows graceful error handling and user notification.
    If present, workflow can route to error handling node.
    """


# === State Update Helper Functions ===

def create_initial_state(paper_text: str, paper_title: str) -> State:
    """
    Create initial state for starting the workflow.

    This helper function initializes the state with input data and sets
    default values for tracking fields. All agent result fields (claims,
    methodology, etc.) are left as None and will be populated during execution.

    Args:
        paper_text: Full text extracted from research paper PDF
        paper_title: Title of the paper for reference

    Returns:
        State dictionary ready for workflow execution

    Example:
        state = create_initial_state(pdf_text, "Attention Is All You Need")
        graph.stream(state, config)
    """
    return State(
        paper_text=paper_text,
        paper_title=paper_title,
        current_step="initialization",
        human_approved=None,
        error_message=None
    )


def merge_state(current_state: State, updates: State) -> State:
    """
    Merge state updates into current state.

    In LangGraph, state updates are typically done by returning a new dictionary
    with updated fields. This helper makes explicit merging easier for complex
    updates or when only certain fields should be modified.

    Args:
        current_state: Current state dictionary
        updates: Dictionary with fields to update

    Returns:
        New state dictionary with updates applied

    Note:
        LangGraph automatically merges returned dictionaries with current state,
        so this helper is optional but can make intent clearer.
    """
    return {**current_state, **updates}


# === State Validation ===

def validate_state_for_synthesis(state: State) -> bool:
    """
    Validate that state contains all required fields for synthesis.

    Before the Synthesizer Agent runs, we need to ensure all previous agents
    completed successfully. This validation prevents synthesis from running
    with incomplete data.

    Args:
        state: Current workflow state

    Returns:
        True if all required fields are present, False otherwise

    Example:
        if not validate_state_for_synthesis(state):
             raise ValueError("Missing required analysis results")
    """
    required_fields = ["claims", "methodology", "limitations"]
    return all(state.get(field) is not None for field in required_fields)


# === State Inspection Utilities ===

def get_state_summary(state: State) -> str:
    """
    Generate human-readable summary of current state.

    Useful for debugging, logging, and displaying progress to users.
    Shows which fields are populated and their approximate sizes.

    Args:
        state: Current workflow state

    Returns:
        Multi-line string summary of state contents
    """
    summary_lines = [
        "=== State Summary ===",
        f"Paper Title: {state.get('paper_title', 'N/A')}",
        f"Current Step: {state.get('current_step', 'N/A')}",
        f"Paper Text: {'Present' if state.get('paper_text') else 'Missing'} "
        f"({len(state.get('paper_text', ''))} chars)",
        f"Claims: {'Present' if state.get('claims') else 'Missing'}",
        f"Methodology: {'Present' if state.get('methodology') else 'Missing'}",
        f"Limitations: {'Present' if state.get('limitations') else 'Missing'}",
        f"Final Report: {'Present' if state.get('final_report') else 'Missing'}",
        f"Human Approved: {state.get('human_approved', 'Pending')}",
    ]

    if state.get('error_message'):
        summary_lines.append(f"⚠️  Error: {state['error_message']}")

    return "\n".join(summary_lines)