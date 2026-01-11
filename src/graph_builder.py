"""
LangGraph Workflow Builder with Human-in-the-Loop

This module constructs the multi-agent workflow graph using LangGraph's
StateGraph API. It demonstrates key LangGraph concepts:

1. State Management: TypedDict state flows through all nodes
2. Nodes: Individual agents as processing units
3. Edges: Connections defining workflow sequence
4. Conditional Edges: Branching logic based on state
5. Interrupts: Pause execution for human input
6. Checkpointing: Save and resume workflow state

Graph Structure:
  START → claims_extractor → methodology_analyzer → limitations_finder
       → synthesizer → human_review → [conditional routing] → END

The human_review node creates an interrupt, pausing execution until
the human provides approval/rejection input.
"""

from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .state import State
from .agents.claims_extractor import claims_extractor_agent
from .agents.methodology_analyzer import methodology_analyzer_agent
from .agents.limitations_finder import limitations_finder_agent
from .agents.synthesizer import synthesizer_agent


def human_review_node(state: State) -> State:
    """
    Human-in-the-loop review node.

    This node creates an interrupt in the workflow, pausing execution
    to allow a human reviewer to examine the synthesized report and
    provide approval/rejection feedback.

    Key LangGraph Concept - Interrupts:
    When execution reaches this node, LangGraph will:
    1. Save current state to checkpoint
    2. Return control to the calling code
    3. Wait for human input
    4. Resume execution with updated state

    This enables true human-in-the-loop workflows where AI processing
    can be paused for human judgment and then continued seamlessly.

    Args:
        state: Current workflow state with final_report

    Returns:
        State (unchanged - human input updates state externally)

    Note:
        The actual approval logic happens in the main execution loop.
        This node simply marks the interrupt point.
    """

    print("\n" + "=" * 70)
    print("🔍 HUMAN REVIEW CHECKPOINT")
    print("=" * 70)
    print("\nThe synthesized report is ready for review.")
    print("Workflow execution will pause here for human approval.\n")

    # Display the report for review
    if state.get("final_report"):
        print(state["final_report"])
    else:
        print("⚠️  Warning: No final report found in state")

    print("\n" + "=" * 70)
    print("Waiting for human review decision...")
    print("=" * 70 + "\n")

    # Return state unchanged
    # The interrupt mechanism handles the pause
    # External code will update 'human_approved' field
    return state


def check_approval(state: State) -> Literal["approved", "rejected"]:
    """
    Conditional routing function based on human approval.

    This function determines which path the workflow takes after human review.
    It's called by LangGraph's conditional_edges mechanism to decide the
    next node.

    Key LangGraph Concept - Conditional Edges:
    Conditional edges allow dynamic routing based on state. The function
    returns a string key that maps to the next node in the workflow.

    Current Implementation (Simple):
    - "approved" → END (save report and finish)
    - "rejected" → END (discard report and finish)

    Advanced Extensions:
    You could add more routing options:
    - "needs_revision" → "synthesizer" (loop back for improvements)
    - "needs_clarification" → "human_feedback" (get specific guidance)

    Args:
        state: Current workflow state with human_approved field

    Returns:
        Route key: either "approved" or "rejected"

    Note:
        This function MUST return one of the keys defined in
        the conditional_edges mapping when the graph is built.
    """

    # Check if human approved the report
    approved = state.get("human_approved", False)

    if approved:
        print("\n✅ Report APPROVED - Proceeding to save...")
        return "approved"
    else:
        print("\n❌ Report REJECTED - Ending workflow...")
        return "rejected"


def build_graph() -> StateGraph:
    """
    Build the complete LangGraph workflow with all agents and routing.

    This function constructs the state graph that defines the entire
    multi-agent analysis workflow. It demonstrates the core LangGraph
    pattern of building a graph by:
    1. Creating a StateGraph with state schema
    2. Adding nodes (processing units)
    3. Adding edges (connections)
    4. Adding conditional edges (branching logic)
    5. Setting entry point
    6. Compiling with checkpointer

    Returns:
        Compiled StateGraph ready for execution

    Example Usage:
        graph = build_graph()
        config = {"configurable": {"thread_id": "analysis_1"}}
        for event in graph.stream(initial_state, config):
        ...     # Process events
    """

    # Step 1: Create StateGraph with our state schema
    # The State TypedDict defines what data flows through the graph
    workflow = StateGraph(State)

    # Step 2: Add all agent nodes
    # Each node is a function that takes State and returns updated State
    # Node names should be descriptive and match the graph flow

    workflow.add_node("claims_extractor", claims_extractor_agent)
    print("✓ Added node: claims_extractor")

    workflow.add_node("methodology_analyzer", methodology_analyzer_agent)
    print("✓ Added node: methodology_analyzer")

    workflow.add_node("limitations_finder", limitations_finder_agent)
    print("✓ Added node: limitations_finder")

    workflow.add_node("synthesizer", synthesizer_agent)
    print("✓ Added node: synthesizer")

    workflow.add_node("human_review", human_review_node)
    print("✓ Added node: human_review (interrupt point)")

    # Step 3: Define the workflow sequence with edges
    # add_edge creates direct connections: node_a → node_b
    # These create the linear pipeline through the agents

    workflow.add_edge("claims_extractor", "methodology_analyzer")
    workflow.add_edge("methodology_analyzer", "limitations_finder")
    workflow.add_edge("limitations_finder", "synthesizer")
    workflow.add_edge("synthesizer", "human_review")
    print("✓ Added sequential edges")

    # Step 4: Add conditional routing after human review
    # add_conditional_edges allows branching based on state
    # The check_approval function returns a key that maps to the next step

    workflow.add_conditional_edges(
        "human_review",  # Source node
        check_approval,  # Function that returns routing key
        {
            "approved": END,  # If approved, end successfully
            "rejected": END  # If rejected, end without saving
        }
    )
    print("✓ Added conditional edges for approval routing")

    # Step 5: Set the entry point
    # This defines where execution begins
    workflow.set_entry_point("claims_extractor")
    print("✓ Set entry point: claims_extractor")

    # Step 6: Compile the graph with checkpointer
    # MemorySaver enables state persistence and interrupt functionality
    # This allows the workflow to pause and resume
    checkpointer = MemorySaver()
    compiled_graph = workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=["human_review"]  # Pause before this node
    )
    print("✓ Compiled graph with checkpointing")

    print("\n📊 Graph construction complete!\n")

    return compiled_graph


def build_graph_with_revision() -> StateGraph:
    """
    Advanced version: Build graph with revision loop capability.

    This is an extended version that allows the workflow to loop back
    to the synthesizer if the human requests revisions instead of
    just approving or rejecting.

    Graph Structure with Revisions:
      START → agents... → synthesizer → human_review
                             ↑              ↓
                             └──[revise]────┘
                                    ↓
                                [approved/rejected] → END

    To use this, you would need to:
    1. Add a 'needs_revision' field to State
    2. Update check_approval to return "revise" option
    3. Add revision feedback to guide the synthesizer

    Returns:
        Compiled StateGraph with revision loop
    """

    workflow = StateGraph(State)

    # Add all nodes (same as basic version)
    workflow.add_node("claims_extractor", claims_extractor_agent)
    workflow.add_node("methodology_analyzer", methodology_analyzer_agent)
    workflow.add_node("limitations_finder", limitations_finder_agent)
    workflow.add_node("synthesizer", synthesizer_agent)
    workflow.add_node("human_review", human_review_node)

    # Sequential edges (same as basic)
    workflow.add_edge("claims_extractor", "methodology_analyzer")
    workflow.add_edge("methodology_analyzer", "limitations_finder")
    workflow.add_edge("limitations_finder", "synthesizer")
    workflow.add_edge("synthesizer", "human_review")

    # Extended conditional routing with revision loop
    def check_approval_with_revision(state: State) -> Literal["approved", "rejected", "revise"]:
        """Extended approval check with revision option."""
        if state.get("human_approved"):
            return "approved"
        elif state.get("needs_revision"):
            return "revise"
        else:
            return "rejected"

    workflow.add_conditional_edges(
        "human_review",
        check_approval_with_revision,
        {
            "approved": END,
            "rejected": END,
            "revise": "synthesizer"  # Loop back for revision
        }
    )
    # START point, alternate implementation workflow.add_edge(START, "claims_extractor")
    workflow.set_entry_point("claims_extractor")

    checkpointer = MemorySaver()
    return workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=["human_review"]
    )


# Graph configuration utilities

def get_graph_config(thread_id: str = "default") -> dict:
    """
    Create configuration for graph execution.

    The config dict is required for graph execution with checkpointing.
    The thread_id identifies a specific conversation/workflow instance.

    Args:
        thread_id: Unique identifier for this workflow execution

    Returns:
        Configuration dictionary for graph.stream() or graph.invoke()

    Example:
        config = get_graph_config("paper_analysis_123")
        graph.stream(state, config)
    """
    return {
        "configurable": {
            "thread_id": thread_id
        }
    }


def print_graph_info():
    """Print information about the workflow graph structure."""
    print("\n" + "=" * 70)
    print("LANGGRAPH MULTI-AGENT WORKFLOW")
    print("=" * 70)
    print("\nWorkflow Structure:")
    print("  1. Claims Extractor     → Extract key claims and hypotheses")
    print("  2. Methodology Analyzer → Analyze research methods")
    print("  3. Limitations Finder   → Identify weaknesses and limitations")
    print("  4. Synthesizer          → Create comprehensive report")
    print("  5. Human Review         → [INTERRUPT] Approve or reject")
    print("  6. Conditional Routing  → Save if approved, discard if rejected")
    print("\nKey Features:")
    print("  • State flows through all nodes")
    print("  • Each agent adds its analysis to state")
    print("  • Execution pauses at human review")
    print("  • State is checkpointed for resumption")
    print("  • Conditional routing based on approval")
    print("=" * 70 + "\n")