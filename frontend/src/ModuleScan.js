import React, { useState } from "react";

function ModuleScan({ moduleName, tenantId, token }) {
  const [scanResult, setScanResult] = useState(null);
  const [scanLoading, setScanLoading] = useState(false);

  const handleScan = async () => {
    setScanLoading(true);
    let url = "";
    let body = {};
    if (moduleName === "nmap") {
      url = "/modules/nmap/scan";
      body = { targets: ["scanme.nmap.org"], options: "-A" };
    } else if (moduleName === "semgrep") {
      url = "/modules/semgrep/scan";
      body = { target: "./src", rules: "auto" };
    }
    const res = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Tenant-ID": tenantId,
        "Authorization": `Bearer ${token}`,
      },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    setScanResult(data);
    setScanLoading(false);
  };

  return (
    <div style={{ marginTop: 20 }}>
      <button disabled={scanLoading} onClick={handleScan}>
        Run {moduleName} Scan
      </button>
      {scanResult && (
        <pre style={{ background: "#eee", padding: 10 }}>
          {JSON.stringify(scanResult, null, 2)}
        </pre>
      )}
    </div>
  );
}

export default ModuleScan;
