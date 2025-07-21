import sys
import json
import subprocess

if len(sys.argv) < 2:
    print(json.dumps({"error": "No input provided"}))
    sys.exit(1)

try:
    scan_input = json.loads(sys.argv[1])
    target = scan_input.get("target", ".")
    rules = scan_input.get("rules", "auto")
    cmd = ["semgrep", "--json", "--config", rules, target]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    output = {
        "command": " ".join(cmd),
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode
    }
    print(json.dumps(output))
except Exception as e:
    print(json.dumps({"error": str(e)}))
    sys.exit(1)
