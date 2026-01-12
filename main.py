#!/usr/bin/env python3
"""
LangGraph Multi-Agent Research Paper Analyzer - Main Entry Point

This is the command-line interface for running the multi-agent paper analysis
workflow. It demonstrates the complete LangGraph pattern including:
- Graph initialization with checkpointing
- Streaming execution with real-time output
- Human-in-the-loop interrupt and approval
- State management across workflow
- Conditional routing based on decisions

Usage:
    python main.py <path_to_pdf>

Example:
    python main.py data/papers/attention_is_all_you_need.pdf
"""

import argparse
import sys
from pathlib import Path

from src.graph_builder import build_graph, get_graph_config
from src.state import create_initial_state
from src.utils import (
    load_pdf_text,
    save_report,
    get_user_approval,
    print_welcome_banner,
    print_completion_summary,
    check_dependencies
)
from src.visualization import (
    visualize_graph,
    print_graph_structure
)


def run_analysis(pdf_path: str, show_visualization: bool = True):
    """
    Run complete paper analysis workflow with human-in-the-loop approval.

    This is the main execution function that orchestrates the entire workflow:
    1. Load PDF and create initial state
    2. Build and visualize graph
    3. Run workflow until human review interrupt
    4. Get human approval decision
    5. Resume workflow to completion
    6. Save report if approved

    Key LangGraph Patterns Demonstrated:
    - Graph compilation with checkpointing
    - Streaming execution (graph.stream)
    - Interrupt handling (pauses at human_review)
    - State updates during execution
    - Resuming from checkpoint
    - Conditional routing (approve/reject paths)

    Args:
        pdf_path: Path to research paper PDF
        show_visualization: Whether to display graph visualization

    Returns:
        None
    """

    print_welcome_banner()

    # Step 1: Load PDF content
    print("📄 Step 1: Loading Paper")
    print("-" * 70)

    try:
        paper_text, paper_title = load_pdf_text(pdf_path)
    except Exception as e:
        print(f"\n❌ Error loading PDF: {e}")
        print("Please check that the file exists and is a valid PDF.\n")
        return

    # Step 2: Initialize state
    print("🔧 Step 2: Initializing Workflow State")
    print("-" * 70)
    initial_state = create_initial_state(paper_text, paper_title)
    print(f"✓ Created initial state for: {paper_title}\n")

    # Step 3: Build graph
    print("🏗️  Step 3: Building LangGraph Workflow")
    print("-" * 70)
    graph = build_graph()

    # Step 4: Visualize graph (optional)
    if show_visualization:
        print("\n📊 Step 4: Workflow Visualization")
        print("-" * 70)
        visualize_graph(graph)
        print_graph_structure()
        # draw_workflow_ascii_art()  # Uncomment for ASCII art

    # Step 5: Create execution config
    # The thread_id identifies this specific workflow instance
    # This allows state to be saved and resumed
    config = get_graph_config(thread_id=f"analysis_{Path(pdf_path).stem}")

    # Step 6: Run workflow until interrupt (human review)
    print("🚀 Step 5: Executing Multi-Agent Analysis")
    print("=" * 70)
    print(f"\n=== Analyzing Paper: \"{paper_title}\" ===\n")

    try:
        # Stream events from graph execution
        # This runs all agents until hitting the human_review interrupt
        for event in graph.stream(initial_state, config):
            # Events contain node outputs
            # In this implementation, agents handle their own printing
            # via streaming LLM calls, so we don't need to process events here

            # For debugging, you could print events:
            # print(f"DEBUG: Event from {list(event.keys())}")
            pass

        # At this point, we've hit the interrupt at human_review
        # The workflow has paused and is waiting for human input

    except Exception as e:
        print(f"\n❌ Error during workflow execution: {e}")
        print("The analysis could not be completed.\n")
        return

    # Step 7: Get human approval
    # The workflow is now paused at the human_review node
    # We need to get the user's approval decision

    print("\n" + "=" * 70)
    print("⏸️  WORKFLOW PAUSED - Human Review Checkpoint")
    print("=" * 70)

    # Get approval from user
    approved = get_user_approval()

    # Step 8: Update state with approval decision
    # This updates the checkpointed state with the human's decision
    # The graph will use this when we resume execution

    try:
        # Get current state from checkpoint
        current_state = graph.get_state(config)

        # Update with approval decision
        graph.update_state(
            config,
            {"human_approved": approved}
        )

        print(f"\n✓ State updated with approval: {approved}")

    except Exception as e:
        print(f"\n❌ Error updating state: {e}")
        return

    # Step 9: Resume workflow to completion
    # Continue execution from the checkpoint with updated state
    # The conditional routing will now direct to the appropriate end state

    print("\n🔄 Resuming workflow...")

    try:
        # Stream from None means "continue from checkpoint"
        # This resumes execution after the interrupt
        final_state = None
        for event in graph.stream(None, config):
            # Get the final state from events
            if event:
                final_state = list(event.values())[0]

        # Step 10: Save report if approved
        if approved and final_state:
            report = final_state.get("final_report", "")
            if report and not report.startswith("[Error"):
                output_path = save_report(report, paper_title)
                print_completion_summary(True, output_path)
            else:
                print("\n⚠️  Warning: No valid report to save")
                print_completion_summary(False)
        else:
            print_completion_summary(False)

    except Exception as e:
        print(f"\n❌ Error completing workflow: {e}")
        return


def main():
    """
    Main CLI entry point.

    Handles command-line arguments and invokes the analysis workflow.
    """

    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)

    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="LangGraph Multi-Agent Research Paper Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py data/papers/attention.pdf
  python main.py research_paper.pdf --no-viz

The analyzer will:
1. Extract text from the PDF
2. Run four AI agents to analyze the paper
3. Pause for your approval of the final report
4. Save the report if you approve it
        """
    )

    parser.add_argument(
        "pdf_path",
        type=str,
        help="Path to research paper PDF file"
    )

    parser.add_argument(
        "--no-viz",
        action="store_true",
        help="Skip graph visualization display"
    )

    args = parser.parse_args()

    # Validate PDF path
    if not Path(args.pdf_path).exists():
        print(f"\n❌ Error: PDF file not found: {args.pdf_path}")
        print("Please provide a valid path to a PDF file.\n")
        sys.exit(1)

    if not args.pdf_path.lower().endswith('.pdf'):
        print(f"\n⚠️  Warning: File does not have .pdf extension: {args.pdf_path}")
        response = input("Continue anyway? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Cancelled.\n")
            sys.exit(0)

    # Run the analysis
    try:
        run_analysis(args.pdf_path, show_visualization=not args.no_viz)
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user")
        print("Exiting...\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()