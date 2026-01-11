"""
Graph Visualization Utilities

This module provides functions to visualize the LangGraph workflow structure.
Understanding the graph structure is crucial for debugging, documentation,
and explaining the workflow to others.

Key Visualization Methods:
1. Mermaid diagram syntax (for interactive visualization)
2. Text-based graph structure display
3. ASCII art representation
4. Execution state tracking
"""

from typing import Any


def visualize_graph(graph: Any) -> None:
    """
    Display the workflow graph structure as Mermaid diagram syntax.

    Mermaid is a text-based diagramming language that can be rendered
    into interactive flowcharts. This function extracts the Mermaid
    syntax from the LangGraph and displays it for user visualization.

    Users can:
    1. Copy the displayed Mermaid syntax
    2. Visit https://mermaid.live
    3. Paste the syntax to see an interactive diagram

    Args:
        graph: Compiled LangGraph StateGraph instance

    Example Output:
        graph TD
            START --> claims_extractor
            claims_extractor --> methodology_analyzer
            methodology_analyzer --> limitations_finder
            ...
    """

    print("\n" + "=" * 70)
    print("WORKFLOW GRAPH (Mermaid Syntax)")
    print("=" * 70)

    try:
        # Get the Mermaid diagram representation from LangGraph
        # This is a built-in method that generates the syntax
        mermaid_syntax = graph.get_graph().draw_mermaid()

        print(mermaid_syntax)
        print("=" * 70)

        print("\n💡 Copy the above to https://mermaid.live to visualize")
        print("   You'll see an interactive flowchart of the workflow!\n")

    except AttributeError:
        # Fallback if draw_mermaid is not available
        print("⚠️  Mermaid visualization not available")
        print("   Graph structure will be shown in text format instead\n")
        print_graph_structure_simple()

    except Exception as e:
        print(f"⚠️  Could not generate graph visualization: {e}")
        print("   Showing simplified structure instead\n")
        print_graph_structure_simple()


def print_graph_structure() -> None:
    """
    Print detailed text representation of the workflow graph.

    This provides a comprehensive view of:
    - All nodes (agents) in the workflow
    - Edges connecting nodes
    - Conditional routing logic
    - Interrupt points
    - Entry and exit points
    """

    print("\n" + "=" * 70)
    print("📊 WORKFLOW STRUCTURE (Detailed)")
    print("=" * 70)

    print("\n🏁 Entry Point:")
    print("   START → claims_extractor")

    print("\n🔄 Sequential Flow:")
    print("   1. claims_extractor      [Extract key claims and hypotheses]")
    print("      ↓")
    print("   2. methodology_analyzer  [Analyze research methods]")
    print("      ↓")
    print("   3. limitations_finder    [Identify study limitations]")
    print("      ↓")
    print("   4. synthesizer           [Create comprehensive report]")
    print("      ↓")
    print("   5. human_review          [⏸️  INTERRUPT - Human approval]")
    print("      ↓")

    print("\n🔀 Conditional Routing:")
    print("   human_review → check_approval()")
    print("      ├─ [approved] → END ✅ (Save report)")
    print("      └─ [rejected] → END ❌ (Discard report)")

    print("\n⏸️  Interrupt Points:")
    print("   • Before: human_review")
    print("     Reason: Pause for human approval decision")

    print("\n💾 State Checkpointing:")
    print("   • Enabled: Yes")
    print("   • Checkpoint: Before human_review")
    print("   • Resume: After approval input provided")

    print("\n🏁 Exit Points:")
    print("   • Approved path: Report saved to file")
    print("   • Rejected path: Workflow ends without saving")

    print("\n" + "=" * 70 + "\n")


def print_graph_structure_simple() -> None:
    """
    Print simplified ASCII representation of the workflow.

    This is a quick, easy-to-read view of the workflow structure
    that fits on a single screen.
    """

    print("\n📊 Workflow Structure:")
    print("\n  START")
    print("    ↓")
    print("  Claims Extractor 🔍")
    print("    ↓")
    print("  Methodology Analyzer 📋")
    print("    ↓")
    print("  Limitations Finder ⚠️")
    print("    ↓")
    print("  Synthesizer 📝")
    print("    ↓")
    print("  Human Review 👤 [⏸️  INTERRUPT]")
    print("    ↓")
    print("  ┌─────────┐")
    print("  │ Approve? │")
    print("  └─────────┘")
    print("    ├─ Yes → END ✅")
    print("    └─ No  → END ❌")
    print()


def print_execution_progress(current_step: str, total_steps: int = 4) -> None:
    """
    Display current execution progress through the workflow.

    Shows where we are in the pipeline and what's completed.

    Args:
        current_step: Name of current node being executed
        total_steps: Total number of analytical steps (default: 4)
    """

    # Map node names to step numbers
    step_map = {
        "claims_extraction": 1,
        "methodology_analysis": 2,
        "limitations_analysis": 3,
        "synthesis_complete": 4,
        "human_review": 5
    }

    step_num = step_map.get(current_step, 0)

    if step_num <= total_steps:
        print(f"\n[Step {step_num}/{total_steps}] ", end="")
    elif current_step == "human_review":
        print("\n[Human Review Phase] ", end="")


def visualize_state_flow(state: dict) -> None:
    """
    Visualize which state fields have been populated.

    This helps understand the progression of data through the workflow
    and debug any missing information.

    Args:
        state: Current workflow state dictionary
    """

    print("\n" + "=" * 70)
    print("STATE FLOW VISUALIZATION")
    print("=" * 70)

    fields = [
        ("paper_text", "📄 Paper Text", "Input"),
        ("paper_title", "📑 Paper Title", "Input"),
        ("claims", "🔍 Claims Analysis", "Agent 1"),
        ("methodology", "📋 Methodology Analysis", "Agent 2"),
        ("limitations", "⚠️  Limitations Analysis", "Agent 3"),
        ("final_report", "📝 Final Report", "Agent 4"),
        ("human_approved", "👤 Human Approval", "Review"),
    ]

    print("\nField Status:")
    for field_name, display_name, source in fields:
        value = state.get(field_name)

        if value is not None:
            # Field is populated
            status = "✅"
            info = f"({len(str(value))} chars)" if isinstance(value, str) else f"({value})"
        else:
            # Field is not yet populated
            status = "⏳"
            info = "(pending)"

        print(f"  {status} {display_name:30} {info:15} [from {source}]")

    print("\n" + "=" * 70 + "\n")


def draw_workflow_ascii_art() -> None:
    """
    Draw a fun ASCII art representation of the workflow.

    Makes documentation and presentations more engaging!
    """

    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║        LangGraph Multi-Agent Paper Analyzer Workflow        ║
    ╚══════════════════════════════════════════════════════════════╝

                            📄 Research Paper
                                   ↓
                        ┌──────────────────────┐
                        │  Claims Extractor 🔍  │
                        │  What does it claim?  │
                        └──────────────────────┘
                                   ↓
                        ┌──────────────────────┐
                        │ Methodology Analyzer  │
                        │    How was it done? 📋 │
                        └──────────────────────┘
                                   ↓
                        ┌──────────────────────┐
                        │  Limitations Finder   │
                        │   What's missing? ⚠️   │
                        └──────────────────────┘
                                   ↓
                        ┌──────────────────────┐
                        │    Synthesizer 📝     │
                        │ Combine everything!  │
                        └──────────────────────┘
                                   ↓
                        ┌──────────────────────┐
                        │   Human Review 👤     │
                        │    [⏸️  INTERRUPT]     │
                        └──────────────────────┘
                                   ↓
                            Approve? (Y/N)
                           ┌──────┴──────┐
                           ↓             ↓
                      ✅ Approved    ❌ Rejected
                     Save Report    Discard
                           ↓             ↓
                          END           END
    """)


def show_graph_legend() -> None:
    """Display legend explaining graph symbols and notation."""

    print("\n" + "=" * 70)
    print("GRAPH NOTATION LEGEND")
    print("=" * 70)

    print("\nSymbols:")
    print("  →   Sequential edge (direct connection)")
    print("  ↓   Flow direction")
    print("  ┌─  Conditional branch point")
    print("  ⏸️   Interrupt point (pauses execution)")
    print("  ✅  Success path")
    print("  ❌  Rejection path")

    print("\nNode Types:")
    print("  🔍  Analysis Agent (processes data)")
    print("  👤  Human Review (requires human input)")
    print("  🔀  Conditional Router (branches based on state)")

    print("\nState Elements:")
    print("  💾  Checkpointed (saved for resume)")
    print("  📝  Writable (agent can update)")
    print("  👁️   Read-only (for reference)")

    print("\n" + "=" * 70 + "\n")