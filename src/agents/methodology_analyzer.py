"""
Methodology Analyzer Agent

This agent is the second in the analysis pipeline. It analyzes the research
methodology, experimental design, data sources, and analytical approach used
in the paper.

Role in Workflow:
- Second agent in sequential pipeline
- Focuses on HOW the research was conducted
- Evaluates rigor and reproducibility

LangGraph Node Behavior:
- Receives State with paper_text and claims
- Returns State with 'methodology' field populated
- Streams output for real-time progress feedback
"""

from langchain_ollama import ChatOllama
from ..state import State


def methodology_analyzer_agent(state: State) -> State:
    """
    Analyze the research methodology and experimental approach.

    This agent examines how the research was conducted, including:
    - Research design and methodology type
    - Data sources and sample characteristics
    - Analytical techniques and tools used
    - Experimental setup and procedures
    - Evaluation metrics and validation approaches

    Args:
        state: Current workflow state with paper_text and claims

    Returns:
        Updated state with 'methodology' field populated

    State Updates:
        - methodology: Structured analysis of research methods
        - current_step: Updated to "methodology_analysis"
    """

    print("\n" + "=" * 70)
    print("[Step 2/4] Methodology Analyzer Agent 📋")
    print("Analyzing research methodology and approach...")
    print("=" * 70)

    # Initialize LLM
    # The .stream() method used below handles the streaming behavior.
    llm = ChatOllama(
        model="llama3",
        temperature=0.4  # Slightly higher for more detailed analysis
    )

    # Include claims in context to provide continuity
    # This helps the agent understand what was being tested
    claims_context = f"\n\nPreviously Identified Claims:\n{state.get('claims', 'N/A')}"

    prompt = f"""You are an expert research methodologist specializing in evaluating experimental design and analytical approaches.

Analyze the methodology of this research paper. Provide a structured analysis covering:

1. **Research Design**: What type of study is this? (experimental, observational, computational, theoretical, etc.)

2. **Data Sources**: 
   - What data was used?
   - Sample size and characteristics
   - Data collection methods

3. **Methods and Techniques**:
   - Specific algorithms, models, or analytical techniques
   - Tools and software used
   - Statistical or computational approaches

4. **Experimental Setup**:
   - How were experiments designed?
   - Control conditions and variables
   - Validation and testing procedures

5. **Evaluation Metrics**:
   - How were results measured?
   - What metrics determined success?

6. **Reproducibility**:
   - Is there enough detail to reproduce the work?
   - Are methods clearly described?

{claims_context}

Research Paper:
{state['paper_text'][:8000]}

METHODOLOGY ANALYSIS:"""

    try:
        print("\n📊 Evaluating research methods...\n")

        chunks = []
        for chunk in llm.stream(prompt):
            content = chunk.content if hasattr(chunk, 'content') else str(chunk)
            print(content, end="", flush=True)
            chunks.append(content)

        print("\n")

        methodology = "".join(chunks)

        return {
            **state,
            "methodology": methodology,
            "current_step": "methodology_analysis"
        }

    except Exception as e:
        error_msg = f"Error in Methodology Analyzer Agent: {str(e)}"
        print(f"\n❌ {error_msg}\n")

        return {
            **state,
            "methodology": f"[Error: Could not analyze methodology - {str(e)}]",
            "current_step": "methodology_analysis_error",
            "error_message": error_msg
        }