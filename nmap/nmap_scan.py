import sys
import json
import subprocess

# Usage: python3 nmap_scan.py '{"targets": ["192.168.1.1"], "options": "-sV"}'

def run_scan(scan_request):
    targets = scan_request.get("targets", [])
    options = scan_request.get("options", "-sV")
    if not targets:
        return {"error": "No targets specified"}
    cmd = ["nmap"] + options.split() + targets
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return {
            "command": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No scan request provided"}))
        sys.exit(1)
    scan_request = json.loads(sys.argv[1])
    result = run_scan(scan_request)
    print(json.dumps(result))
