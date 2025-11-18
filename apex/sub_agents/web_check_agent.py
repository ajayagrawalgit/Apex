from google.adk.agents import LlmAgent
from apex.tools import analyze_scraped_text

web_check_agent = LlmAgent(
    name="WebCheckAgent",
    model="gemini-2.5-flash",
    instruction="""
    You are an expert Web Checker.
Your task is to analyze the supplied web page content in depth and produce a comprehensive analysis.
Use the `analyze_scraped_text` tool for your evaluation.

Respond only with your analysis result, without adding extra commentary.
""",
    description="Analyzes web content and returns the analysis result.",
    tools=[analyze_scraped_text],
    output_key="analysis_result",
)