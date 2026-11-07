const socket = io();
let currentResults = [];

socket.on("finding", (f) => {
    currentResults.push(f);
    appendResultRow(f);
});

socket.on("scan_done", () => {
    document.getElementById("stop-btn").disabled = true;
});

socket.on("baseline_ready", (d) => {
    console.log("Baseline status:", d.status);
});

function saveKeys() {
    const gemini = document.getElementById("gemini-key").value.trim();
    const deepseek = document.getElementById("deepseek-key").value.trim();
    fetch("/api/ai_keys", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({gemini_key: gemini || null, deepseek_key: deepseek || null})
    }).then(r => r.json()).then(d => {
        document.getElementById("ai-status").textContent = "✅ Keys saved";
    });
}

function generateAI() {
    const provider = document.getElementById("ai-provider").value;
    const category = document.getElementById("ai-category").value;
    const count = document.getElementById("ai-count").value;
    const status = document.getElementById("ai-status");
    status.textContent = "⏳ Generating with " + provider + "...";
    fetch("/api/ai_generate", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({provider, category, count: parseInt(count)})
    }).then(r => r.json()).then(data => {
        if (data.error) { status.textContent = "❌ " + data.error; return; }
        status.textContent = "✅ Generated " + data.length + " payloads";
        loadPrompts();
    }).catch(e => status.textContent = "❌ " + e);
}

function loadPrompts() {
    fetch("/api/prompts").then(r => r.json()).then(prompts => {
        const list = document.getElementById("prompt-list");
        list.innerHTML = prompts.map(p => `
            <div class="prompt-item">
                <input type="checkbox" class="prompt-check" value="${p.id}" checked>
                <span class="cat">[${p.category}]</span>
                <span class="${p.category === 'ai_generated' ? 'ai-item' : ''}">${p.name}</span>
            </div>
        `).join("");
    });
}

function startScan() {
    const target = document.getElementById("target").value.trim();
    const template = document.getElementById("template").value;
    const method = document.getElementById("method").value;
    const delay = parseInt(document.getElementById("delay").value) || 400;
    const checked = [...document.querySelectorAll(".prompt-check:checked")].map(c => c.value);
    if (!target || checked.length === 0) { alert("Target and at least one prompt required"); return; }

    document.querySelector("#results-table tbody").innerHTML = "";
    currentResults = [];
    document.getElementById("stop-btn").disabled = false;

    fetch("/api/scan", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            target,
            request_template: template,
            payload_ids: checked,
            method,
            delay,
            capture_baseline: true,
        })
    }).then(r => r.json()).then(d => {
        if (d.error) alert(d.error);
    });
}

function stopScan() {
    document.getElementById("stop-btn").disabled = true;
    window.location.reload();
}

function appendResultRow(f) {
    const tbody = document.querySelector("#results-table tbody");
    const tr = document.createElement("tr");
    const matchClass = f.matched ? "match-yes" : "match-no";
    const secretCount = f.secrets ? f.secrets.length : 0;
    tr.innerHTML = `
        <td>${f.index + 1}</td>
        <td>${f.prompt_name}</td>
        <td>${f.category}</td>
        <td>${f.status}</td>
        <td class="${matchClass}">${f.matched ? "MATCH" : "-"}</td>
        <td>${f.reason || ""}</td>
        <td>${secretCount > 0 ? "🔑 " + secretCount : "-"}</td>
        <td><button onclick="confirmFinding(${f.index})">Wilson Confirm</button></td>
    `;
    tbody.appendChild(tr);
}

function confirmFinding(index) {
    const target = document.getElementById("target").value.trim();
    const template = document.getElementById("template").value;
    fetch(`/api/confirm/${index}`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({target, template, retries: 5, successes: 3})
    }).then(r => r.json()).then(d => {
        const row = document.querySelector(`#results-table tbody tr:nth-child(${index + 1})`);
        if (row) {
            const cell = row.cells[7];
            cell.innerHTML = d.confirmed
                ? `<span class="confirmed">Confirmed (${d.ci.successes}/${d.ci.trials}, CI ${d.ci.wilson_lower}-${d.ci.wilson_upper})</span>`
                : `Not confirmed (${d.ci.successes}/${d.ci.trials})`;
        }
    });
}

function exportReport() {
    const target = document.getElementById("target").value.trim();
    fetch("/api/export", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({target})
    }).then(r => r.blob()).then(blob => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "bloodravenist_report.html";
        a.click();
    });
}

loadPrompts();
