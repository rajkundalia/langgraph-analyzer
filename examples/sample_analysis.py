"""
Sample Analysis Example

This file demonstrates how to use the LangGraph multi-agent analyzer
programmatically (not via CLI). Useful for:
- Integration into other Python projects
- Custom workflows
- Batch processing
- Testing and development

Key Concepts Shown:
- Direct graph construction and execution
- Custom state initialization
- Event processing
- State inspection
- Manual approval simulation
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.state import create_initial_state, get_state_summary
from src.graph_builder import build_graph, get_graph_config
from src.utils import load_pdf_text, save_report
from src.visualization import visualize_graph, visualize_state_flow


def example_basic_usage():
    """
    Basic example: Run analysis and auto-approve.

    This shows the minimal code needed to run an analysis.
    """

    print("\n" + "=" * 70)
    print("EXAMPLE 1: Basic Usage with Auto-Approval")
    print("=" * 70 + "\n")

    # Load paper
    pdf_path = "data/papers/sample_paper.pdf"
    paper_text, paper_title = load_pdf_text(pdf_path)

    # Create state
    initial_state = create_initial_state(paper_text, paper_title)

    # Build graph
    graph = build_graph()
    config = get_graph_config("example_1")

    # Run until interrupt
    print("Running agents...")
    for event in graph.stream(initial_state, config):
        pass

    # Auto-approve
    graph.update_state(config, {"human_approved": True})

    # Complete workflow
    final_state = None
    for event in graph.stream(None, config):
        final_state = list(event.values())[0]

    # Save report
    if final_state:
        save_report(final_state["final_report"], paper_title)

    print("\n✅ Example 1 complete!\n")


def example_with_inspection():
    """
    Advanced example: Inspect state at each step.

    Shows how to examine state as it progresses through workflow.
    """

    print("\n" + "=" * 70)
    print("EXAMPLE 2: State Inspection at Each Step")
    print("=" * 70 + "\n")

    # Setup
    pdf_path = "data/papers/sample_paper.pdf"
    paper_text, paper_title = load_pdf_text(pdf_path)
    initial_state = create_initial_state(paper_text, paper_title)

    graph = build_graph()
    config = get_graph_config("example_2")

    # Run and inspect
    print("Running with state inspection...\n")

    for i, event in enumerate(graph.stream(initial_state, config)):
        node_name = list(event.keys())[0]
        state = event[node_name]

        print(f"\n--- After Node: {node_name} ---")
        print(get_state_summary(state))

        # Visualize state progression
        if i == 2:  # After a few nodes
            visualize_state_flow(state)

    # Approve and complete
    graph.update_state(config, {"human_approved": True})

    for event in graph.stream(None, config):
        pass

    print("\n✅ Example 2 complete!\n")


def example_batch_processing():
    """
    Advanced example: Process multiple papers.

    Shows how to analyze multiple papers in sequence.
    """

    print("\n" + "=" * 70)
    print("EXAMPLE 3: Batch Processing Multiple Papers")
    print("=" * 70 + "\n")

    # List of papers to process
    papers = [
        "data/papers/paper1.pdf",
        "data/papers/paper2.pdf",
        "data/papers/paper3.pdf",
    ]

    # Build graph once
    graph = build_graph()

    results = []

    for i, pdf_path in enumerate(papers):
        print(f"\n--- Processing Paper {i + 1}/{len(papers)} ---")

        try:
            # Load paper
            paper_text, paper_title = load_pdf_text(pdf_path)
            initial_state = create_initial_state(paper_text, paper_title)

            # Unique thread ID for each paper
            config = get_graph_config(f"batch_{i}")

            # Run workflow
            for event in graph.stream(initial_state, config):
                pass

            # Auto-approve for batch processing
            graph.update_state(config, {"human_approved": True})

            # Complete
            final_state = None
            for event in graph.stream(None, config):
                final_state = list(event.values())[0]

            # Save
            if final_state:
                output_path = save_report(
                    final_state["final_report"],
                    paper_title
                )
                results.append({
                    "title": paper_title,
                    "status": "success",
                    "path": output_path
                })
            else:
                results.append({
                    "title": paper_title,
                    "status": "failed",
                    "error": "No final state"
                })

        except Exception as e:
            results.append({
                "title": pdf_path,
                "status": "error",
                "error": str(e)
            })

    # Summary
    print("\n" + "=" * 70)
    print("BATCH PROCESSING RESULTS")
    print("=" * 70)

    for result in results:
        status = result['status']
        if status == "success":
            print(f"✅ {result['title']}")
            print(f"   → {result['path']}")
        else:
            print(f"❌ {result['title']}")
            print(f"   → {result.get('error', 'Unknown error')}")

    print("\n✅ Example 3 complete!\n")


def example_custom_agent_workflow():
    """
    Advanced example: Custom workflow with different agents.

    Shows how to modify the graph for custom analysis needs.
    """

    print("\n" + "=" * 70)
    print("EXAMPLE 4: Custom Agent Workflow")
    print("=" * 70 + "\n")

    print("This example would show how to:")
    print("- Add custom agents to the workflow")
    print("- Modify the graph structure")
    print("- Implement different routing logic")
    print("- Create specialized analysis pipelines")

    print("\nSee README for extending the project!")
    print("\n✅ Example 4 concept shown!\n")


def example_with_visualization():
    """
    Example: Generate and display workflow visualizations.
    """

    print("\n" + "=" * 70)
    print("EXAMPLE 5: Graph Visualization")
    print("=" * 70 + "\n")

    graph = build_graph()

    # Show Mermaid diagram
    visualize_graph(graph)

    # Show structure
    from src.visualization import print_graph_structure, draw_workflow_ascii_art
    print_graph_structure()
    draw_workflow_ascii_art()

    print("\n✅ Example 5 complete!\n")


def run_all_examples():
    """Run all example demonstrations."""

    print("\n" + "=" * 70)
    print("LANGGRAPH MULTI-AGENT ANALYZER - EXAMPLES")
    print("=" * 70)

    # Example 5 doesn't require PDFs
    example_with_visualization()

    # Other examples would need actual PDF files
    print("\n📝 Note: Examples 1-4 require PDF files in data/papers/")
    print("   Place sample PDFs there to run full examples.")

    # Uncomment these if you have PDF files:
    # example_basic_usage()
    # example_with_inspection()
    # example_batch_processing()
    # example_custom_agent_workflow()


if __name__ == "__main__":
    # Run all examples
    run_all_examples()

    # Or run individual examples:
    # example_basic_usage()
    # example_with_inspection()
    # example_batch_processing()
    # example_custom_agent_workflow()
    # example_with_visualization()