"""Template for agent prompt used across OpenAlex MCP Server"""

# Goal of the agents/definition
AGENT_NAME_PROMPT=""" You are an AI research assistant tasked with performing abc through the xyz produce output in the format of def.

AVAILABLE TOOLS :
    1. function_1 : Use this tool 
    2. function_2 : Use this tool if 
    3. function_3 : This tool is for ...


WORKFLOW FOR ASSIGNMENT:
    1. STEP 1 : 
        - First, 
        - If, 
        - Then, otherwise

    2. STEP 2 : 
        - Execute, 
        - If,
        - For 

    3. STEP 3 : 


OPTIONAL STEPS : 

STRUCTURE OUTPUT
"""
