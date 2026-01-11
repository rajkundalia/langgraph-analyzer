"""
Claims Extractor Agent

This agent is the first in the analysis pipeline. Its role is to identify and
extract the key claims, hypotheses, and contributions from the research paper.

Role in Workflow:
- First agent to process the paper after initialization
- Provides foundation for other agents' analysis
- Focuses on WHAT the paper claims to contribute

LangGraph Node Behavior:
- Receives State with paper_text
- Returns State with 'claims' field populated
- Streams output token-by-token for real-time feedback
"""

from langchain_ollama import ChatOllama
from ..state import State


def claims_extractor_agent(state: State) -> State:
    """
    Extract key claims and hypotheses from the research paper.

    This agent analyzes the paper text and identifies 3-5 main claims or
    hypotheses that represent the core contributions of the research. It
    focuses on testable claims and novel contributions.

    Args:
        state: Current workflow state containing paper_text

    Returns:
        Updated state with 'claims' field populated

    State Updates:
        - claims: String with numbered list of identified claims
        - current_step: Updated to "claims_extraction"

    Streaming:
        Outputs results token-by-token to console for real-time feedback
    """

    print("\n" + "=" * 70)
    print("[Step 1/4] Claims Extractor Agent 🔍")
    print("Extracting key claims and hypotheses...")
    print("=" * 70)

    # Initialize LLM with streaming enabled
    # streaming=True allows us to display output in real-time
    llm = ChatOllama(
        model="llama3",
        streaming=True,
        temperature=0.3  # Lower temperature for more focused extraction
    )

    # Construct prompt for claims extraction
    # Specific instructions help the LLM focus on the task
    prompt = f"""You are an expert research analyst specializing in identifying key claims and hypotheses in academic papers.

Analyze the following research paper and extract 3-5 main claims or hypotheses. Focus on:
- Testable claims and assertions
- Novel contributions or findings
- Core arguments the authors make
- Specific results or conclusions claimed

For each claim, provide:
1. A clear, concise statement of the claim
2. A brief 1-2 sentence explanation of why it's significant

Format your response as a numbered list.

Research Paper:
{state['paper_text'][:8000]}

CLAIMS ANALYSIS:"""

    # Stream the response token-by-token
    # This provides immediate feedback and better UX than waiting for full response
    try:
        print("\n🔍 Analyzing claims...\n")

        chunks = []
        for chunk in llm.stream(prompt):
            # Display each token as it arrives
            content = chunk.content if hasattr(chunk, 'content') else str(chunk)
            print(content, end="", flush=True)
            chunks.append(content)

        print("\n")  # Add newline after streaming completes

        # Combine all streamed chunks into final result
        claims = "".join(chunks)

        # Return updated state
        # LangGraph will merge this with existing state
        return {
            **state,
            "claims": claims,
            "current_step": "claims_extraction"
        }

    except Exception as e:
        # Handle errors gracefully
        # In production, you might want to retry or route to error handling node
        error_msg = f"Error in Claims Extractor Agent: {str(e)}"
        print(f"\n❌ {error_msg}\n")

        return {
            **state,
            "claims": f"[Error: Could not extract claims - {str(e)}]",
            "current_step": "claims_extraction_error",
            "error_message": error_msg
        }


def create_claims_prompt(paper_text: str, max_length: int = 8000) -> str:
    """
    Create optimized prompt for claims extraction.

    Helper function to construct the LLM prompt. Separating this allows
    for easier testing and prompt engineering.

    Args:
        paper_text: Full text of research paper
        max_length: Maximum characters to include (prevents token limits)

    Returns:
        Formatted prompt string
    """
    # Truncate paper if too long to fit in context window
    truncated_text = paper_text[:max_length]
    if len(paper_text) > max_length:
        truncated_text += "\n\n[Paper truncated for analysis...]"

    return f"""You are an expert research analyst specializing in identifying key claims and hypotheses in academic papers.

Analyze the following research paper and extract 3-5 main claims or hypotheses.

Focus on:
- Testable claims and assertions
- Novel contributions or findings  
- Core arguments the authors make
- Specific results or conclusions claimed

For each claim, provide:
1. A clear, concise statement of the claim
2. A brief 1-2 sentence explanation of its significance

Format your response as a numbered list.

Research Paper:
{truncated_text}

CLAIMS ANALYSIS:"""