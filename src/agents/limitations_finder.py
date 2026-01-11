"""
Limitations Finder Agent

This agent is the third in the analysis pipeline. It identifies study limitations,
potential weaknesses, biases, and areas where the research could be strengthened.

Role in Workflow:
- Third agent in sequential pipeline
- Provides critical analysis and constructive critique
- Identifies gaps and potential issues

LangGraph Node Behavior:
- Receives State with paper_text, claims, and methodology
- Returns State with 'limitations' field populated
- Maintains constructive, analytical tone
"""

from langchain_ollama import ChatOllama
from ..state import State


def limitations_finder_agent(state: State) -> State:
    """
    Identify limitations, weaknesses, and potential biases in the research.

    This agent critically examines the research to find:
    - Sample size or data limitations
    - Methodological weaknesses
    - Scope and generalizability issues
    - Potential biases
    - Assumptions and their validity
    - Areas for future improvement

    The critique is constructive and specific, focusing on genuine limitations
    rather than minor issues.

    Args:
        state: Current workflow state with paper_text, claims, and methodology

    Returns:
        Updated state with 'limitations' field populated

    State Updates:
        - limitations: Categorized analysis of research limitations
        - current_step: Updated to "limitations_analysis"
    """

    print("\n" + "=" * 70)
    print("[Step 3/4] Limitations Finder Agent ⚠️")
    print("Identifying limitations and potential weaknesses...")
    print("=" * 70)

    # Initialize LLM
    # The .stream() method used below handles the streaming behavior.
    llm = ChatOllama(
        model="llama3",
        temperature=0.5  # Higher temperature for more critical thinking
    )

    # Provide full context from previous agents
    # This allows the agent to identify limitations in claimed contributions
    # and methodological choices
    context = f"""
Previously Identified Claims:
{state.get('claims', 'N/A')}

Methodology Analysis:
{state.get('methodology', 'N/A')}
"""

    prompt = f"""You are an expert research critic specializing in identifying study limitations and potential weaknesses.

Analyze this research paper and identify significant limitations. Be constructive and specific.

Categorize limitations into:

1. **Sample and Data Limitations**:
   - Sample size issues
   - Data quality or coverage gaps
   - Selection biases

2. **Methodological Limitations**:
   - Weaknesses in experimental design
   - Analytical limitations
   - Validation concerns

3. **Scope and Generalizability**:
   - Limited applicability
   - Context-specific results
   - Narrow focus areas

4. **Assumptions and Constraints**:
   - Underlying assumptions that may not hold
   - Simplifications that affect conclusions
   - Resource or time constraints

5. **Missing Elements**:
   - Important comparisons not made
   - Alternative approaches not considered
   - Future work needed

For each limitation:
- Explain why it's significant
- Assess potential impact on conclusions
- Be specific and constructive

{context}

Research Paper:
{state['paper_text'][:8000]}

LIMITATIONS ANALYSIS:"""

    try:
        print("\n🔍 Analyzing limitations and weaknesses...\n")

        chunks = []
        for chunk in llm.stream(prompt):
            content = chunk.content if hasattr(chunk, 'content') else str(chunk)
            print(content, end="", flush=True)
            chunks.append(content)

        print("\n")

        limitations = "".join(chunks)

        return {
            **state,
            "limitations": limitations,
            "current_step": "limitations_analysis"
        }

    except Exception as e:
        error_msg = f"Error in Limitations Finder Agent: {str(e)}"
        print(f"\n❌ {error_msg}\n")

        return {
            **state,
            "limitations": f"[Error: Could not identify limitations - {str(e)}]",
            "current_step": "limitations_analysis_error",
            "error_message": error_msg
        }