# Save as test_mcp_client.py
import subprocess
import json
import sys

def call_mcp_server(method, name, arguments):
    request = {
        "jsonrpc": "2.0",
        "method": method,
        "params": {
            "name": name,
            "arguments": arguments
        },
        "id": 1
    }
    
    # Launch the server as a subprocess
    proc = subprocess.Popen(
        ["python", "-m", "openalex-mcp-server.main"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Send the request
    print(f"Sending request: {json.dumps(request)}")
    proc.stdin.write(json.dumps(request) + "\n")
    proc.stdin.flush()
    
    # Read and parse the response
    response_line = proc.stdout.readline().strip()
    proc.terminate()  # Clean up the process
    
    try:
        response = json.loads(response_line)
        return response
    except json.JSONDecodeError:
        print(f"Failed to decode response: {response_line}")
        return None

# Test searching for papers
print("Testing search_papers...")
result = call_mcp_server("tool", "search_papers", {"query": "quantum computing", "limit": 3})
print(json.dumps(result, indent=2))

# Test getting a specific paper
print("\nTesting get_paper...")
result = call_mcp_server("tool", "get_paper", {"paper_id": "W2741809807"})
print(json.dumps(result, indent=2))
