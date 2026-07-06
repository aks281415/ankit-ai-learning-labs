"""
Built-in real-time monitoring dashboard.

Serves a beautiful, auto-refreshing HTML dashboard at /dashboard
that visualizes all chatbot metrics — no Grafana needed.
"""

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Career Mentor — Monitoring Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        :root {
            --bg-primary: #0a0e1a;
            --bg-card: #111827;
            --bg-card-hover: #1a2332;
            --border: #1e293b;
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --accent-blue: #3b82f6;
            --accent-purple: #8b5cf6;
            --accent-green: #10b981;
            --accent-orange: #f59e0b;
            --accent-red: #ef4444;
            --accent-cyan: #06b6d4;
            --gradient-blue: linear-gradient(135deg, #3b82f6, #8b5cf6);
            --gradient-green: linear-gradient(135deg, #10b981, #06b6d4);
            --gradient-orange: linear-gradient(135deg, #f59e0b, #ef4444);
            --gradient-purple: linear-gradient(135deg, #8b5cf6, #ec4899);
            --shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
            --shadow-glow-blue: 0 0 30px rgba(59, 130, 246, 0.15);
            --shadow-glow-green: 0 0 30px rgba(16, 185, 129, 0.15);
        }

        body {
            font-family: 'Inter', -apple-system, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* ── Header ──────────────────────────────────── */
        .header {
            background: linear-gradient(180deg, #111827 0%, var(--bg-primary) 100%);
            border-bottom: 1px solid var(--border);
            padding: 1.25rem 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(12px);
        }

        .header-left {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .header-logo {
            width: 36px;
            height: 36px;
            background: var(--gradient-blue);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
        }

        .header h1 {
            font-size: 1.15rem;
            font-weight: 600;
            letter-spacing: -0.01em;
        }

        .header h1 span {
            color: var(--text-muted);
            font-weight: 400;
            margin-left: 0.5rem;
            font-size: 0.85rem;
        }

        .header-right {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .live-dot {
            width: 8px;
            height: 8px;
            background: var(--accent-green);
            border-radius: 50%;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
            50% { opacity: 0.8; box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
        }

        .status-badge {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.2);
            padding: 0.35rem 0.85rem;
            border-radius: 20px;
            font-size: 0.78rem;
            font-weight: 500;
            color: var(--accent-green);
        }

        .uptime {
            font-size: 0.78rem;
            color: var(--text-muted);
        }

        /* ── Main Layout ─────────────────────────────── */
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 1.5rem 2rem 3rem;
        }

        /* ── Stat Cards (Top Row) ────────────────────── */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1rem;
            margin-bottom: 1.5rem;
        }

        .stat-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 1.25rem 1.5rem;
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease;
        }

        .stat-card:hover {
            background: var(--bg-card-hover);
            transform: translateY(-2px);
            box-shadow: var(--shadow);
        }

        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            border-radius: 14px 14px 0 0;
        }

        .stat-card:nth-child(1)::before { background: var(--gradient-blue); }
        .stat-card:nth-child(2)::before { background: var(--gradient-green); }
        .stat-card:nth-child(3)::before { background: var(--gradient-orange); }
        .stat-card:nth-child(4)::before { background: var(--gradient-purple); }

        .stat-label {
            font-size: 0.75rem;
            font-weight: 500;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }

        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            line-height: 1.1;
        }

        .stat-sub {
            font-size: 0.78rem;
            color: var(--text-secondary);
            margin-top: 0.4rem;
        }

        .stat-value.blue { color: var(--accent-blue); }
        .stat-value.green { color: var(--accent-green); }
        .stat-value.orange { color: var(--accent-orange); }
        .stat-value.purple { color: var(--accent-purple); }

        /* ── Section Grid (2 columns) ────────────────── */
        .section-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }

        .section-full {
            grid-column: 1 / -1;
        }

        .card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 1.25rem 1.5rem;
            transition: all 0.3s ease;
        }

        .card:hover {
            box-shadow: var(--shadow);
        }

        .card-title {
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-secondary);
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .card-title .icon { font-size: 1rem; }

        /* ── Latency Bars ────────────────────────────── */
        .latency-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.75rem;
        }

        .latency-item {
            background: rgba(255,255,255,0.03);
            border-radius: 10px;
            padding: 0.85rem 1rem;
            text-align: center;
        }

        .latency-label {
            font-size: 0.7rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.3rem;
        }

        .latency-value {
            font-size: 1.35rem;
            font-weight: 700;
            color: var(--accent-cyan);
        }

        .latency-value.warn { color: var(--accent-orange); }
        .latency-value.bad { color: var(--accent-red); }

        /* ── Token Split Bar ─────────────────────────── */
        .token-bar-container {
            margin-top: 0.75rem;
        }

        .token-bar {
            height: 12px;
            border-radius: 6px;
            overflow: hidden;
            display: flex;
            background: rgba(255,255,255,0.05);
        }

        .token-bar-prompt {
            background: var(--gradient-blue);
            height: 100%;
            transition: width 0.5s ease;
        }

        .token-bar-completion {
            background: var(--gradient-purple);
            height: 100%;
            transition: width 0.5s ease;
        }

        .token-legend {
            display: flex;
            justify-content: space-between;
            margin-top: 0.5rem;
            font-size: 0.75rem;
            color: var(--text-secondary);
        }

        .token-legend .dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 0.3rem;
            vertical-align: middle;
        }

        .dot-prompt { background: var(--accent-blue); }
        .dot-completion { background: var(--accent-purple); }

        .token-stat-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 0.75rem;
            margin-bottom: 0.75rem;
        }

        .token-stat {
            background: rgba(255,255,255,0.03);
            border-radius: 10px;
            padding: 0.75rem 1rem;
        }

        .token-stat-label {
            font-size: 0.7rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .token-stat-value {
            font-size: 1.25rem;
            font-weight: 700;
            margin-top: 0.2rem;
        }

        /* ── Cost Section ────────────────────────────── */
        .cost-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 0.75rem;
        }

        .cost-item {
            background: rgba(255,255,255,0.03);
            border-radius: 10px;
            padding: 0.85rem 1rem;
            text-align: center;
        }

        .cost-label {
            font-size: 0.7rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .cost-value {
            font-size: 1.3rem;
            font-weight: 700;
            color: var(--accent-orange);
            margin-top: 0.2rem;
        }

        /* ── Timeline Chart ──────────────────────────── */
        .chart-container {
            width: 100%;
            height: 180px;
            position: relative;
            margin-top: 0.5rem;
        }

        .chart-bars {
            display: flex;
            align-items: flex-end;
            height: 150px;
            gap: 3px;
            padding-bottom: 25px;
            border-bottom: 1px solid var(--border);
        }

        .chart-bar-group {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 2px;
        }

        .chart-bar {
            width: 100%;
            min-height: 2px;
            border-radius: 3px 3px 0 0;
            background: var(--gradient-blue);
            transition: height 0.5s ease;
            position: relative;
        }

        .chart-bar.error {
            background: var(--accent-red);
        }

        .chart-bar:hover {
            opacity: 0.8;
        }

        .chart-label {
            font-size: 0.6rem;
            color: var(--text-muted);
            position: absolute;
            bottom: 0;
            transform: translateY(18px);
            white-space: nowrap;
        }

        .chart-empty {
            height: 150px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--text-muted);
            font-size: 0.85rem;
        }

        /* ── Error Breakdown ─────────────────────────── */
        .error-list {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        .error-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(239, 68, 68, 0.06);
            border: 1px solid rgba(239, 68, 68, 0.12);
            border-radius: 8px;
            padding: 0.6rem 1rem;
        }

        .error-type {
            font-size: 0.82rem;
            font-weight: 500;
            color: var(--accent-red);
        }

        .error-count {
            font-size: 0.82rem;
            font-weight: 700;
            color: var(--accent-red);
            background: rgba(239, 68, 68, 0.1);
            padding: 0.2rem 0.6rem;
            border-radius: 12px;
        }

        .no-errors {
            text-align: center;
            padding: 1.5rem;
            color: var(--accent-green);
            font-size: 0.85rem;
        }

        /* ── Request Log Table ────────────────────────── */
        .log-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.8rem;
        }

        .log-table th {
            text-align: left;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            font-size: 0.7rem;
            letter-spacing: 0.05em;
            padding: 0.6rem 0.75rem;
            border-bottom: 1px solid var(--border);
        }

        .log-table td {
            padding: 0.55rem 0.75rem;
            border-bottom: 1px solid rgba(255,255,255,0.03);
            color: var(--text-secondary);
            vertical-align: middle;
        }

        .log-table tr:hover td {
            background: rgba(255,255,255,0.02);
        }

        .log-table .msg-col {
            max-width: 280px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .badge {
            display: inline-block;
            padding: 0.15rem 0.5rem;
            border-radius: 10px;
            font-size: 0.68rem;
            font-weight: 600;
            text-transform: uppercase;
        }

        .badge-success {
            color: var(--accent-green);
            background: rgba(16, 185, 129, 0.1);
        }

        .badge-error {
            color: var(--accent-red);
            background: rgba(239, 68, 68, 0.1);
        }

        /* ── Responsive ──────────────────────────────── */
        @media (max-width: 900px) {
            .stats-grid { grid-template-columns: repeat(2, 1fr); }
            .section-grid { grid-template-columns: 1fr; }
            .container { padding: 1rem; }
        }

        @media (max-width: 600px) {
            .stats-grid { grid-template-columns: 1fr; }
            .latency-grid { grid-template-columns: 1fr; }
        }

        /* ── Scrollbar ───────────────────────────────── */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: var(--bg-primary); }
        ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

        /* ── Fade-in Animation ────────────────────────── */
        .fade-in {
            animation: fadeIn 0.4s ease-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>
    <!-- Header -->
    <div class="header">
        <div class="header-left">
            <div class="header-logo">🤖</div>
            <h1>AI Career Mentor <span>Monitoring Dashboard</span></h1>
        </div>
        <div class="header-right">
            <span class="uptime" id="uptime"></span>
            <div class="status-badge">
                <div class="live-dot"></div>
                Live — refreshes every 3s
            </div>
        </div>
    </div>

    <div class="container">
        <!-- Top Stats Row -->
        <div class="stats-grid fade-in">
            <div class="stat-card">
                <div class="stat-label">Total Requests</div>
                <div class="stat-value blue" id="total-requests">0</div>
                <div class="stat-sub"><span id="success-count">0</span> success · <span id="error-count">0</span> errors</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Active Sessions</div>
                <div class="stat-value green" id="active-sessions">0</div>
                <div class="stat-sub">Concurrent conversations</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Cost</div>
                <div class="stat-value orange" id="total-cost">$0.00</div>
                <div class="stat-sub">Avg <span id="avg-cost">$0.00</span>/request</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Error Rate</div>
                <div class="stat-value purple" id="error-rate">0%</div>
                <div class="stat-sub">Failed / Total requests</div>
            </div>
        </div>

        <!-- Row 2: Latency + Tokens -->
        <div class="section-grid fade-in">
            <!-- Latency Card -->
            <div class="card">
                <div class="card-title"><span class="icon">⏱️</span> Response Latency</div>
                <div class="latency-grid">
                    <div class="latency-item">
                        <div class="latency-label">Average</div>
                        <div class="latency-value" id="avg-latency">0s</div>
                    </div>
                    <div class="latency-item">
                        <div class="latency-label">P50 (Median)</div>
                        <div class="latency-value" id="p50-latency">0s</div>
                    </div>
                    <div class="latency-item">
                        <div class="latency-label">P95</div>
                        <div class="latency-value" id="p95-latency">0s</div>
                    </div>
                    <div class="latency-item">
                        <div class="latency-label">P99</div>
                        <div class="latency-value" id="p99-latency">0s</div>
                    </div>
                    <div class="latency-item">
                        <div class="latency-label">Min</div>
                        <div class="latency-value" id="min-latency">0s</div>
                    </div>
                    <div class="latency-item">
                        <div class="latency-label">Max</div>
                        <div class="latency-value" id="max-latency">0s</div>
                    </div>
                </div>
            </div>

            <!-- Token Usage Card -->
            <div class="card">
                <div class="card-title"><span class="icon">🔢</span> Token Usage</div>
                <div class="token-stat-grid">
                    <div class="token-stat">
                        <div class="token-stat-label">Total Tokens</div>
                        <div class="token-stat-value" style="color:var(--accent-cyan)" id="total-tokens">0</div>
                    </div>
                    <div class="token-stat">
                        <div class="token-stat-label">Avg / Request</div>
                        <div class="token-stat-value" style="color:var(--accent-cyan)" id="avg-tokens">0</div>
                    </div>
                </div>
                <div class="token-bar-container">
                    <div class="token-bar">
                        <div class="token-bar-prompt" id="prompt-bar" style="width:50%"></div>
                        <div class="token-bar-completion" id="completion-bar" style="width:50%"></div>
                    </div>
                    <div class="token-legend">
                        <span><span class="dot dot-prompt"></span> Prompt: <strong id="prompt-tokens">0</strong></span>
                        <span><span class="dot dot-completion"></span> Completion: <strong id="completion-tokens">0</strong></span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Row 3: Timeline Chart + Errors -->
        <div class="section-grid fade-in">
            <!-- Timeline Chart -->
            <div class="card">
                <div class="card-title"><span class="icon">📈</span> Request Timeline (per minute)</div>
                <div class="chart-container" id="timeline-chart">
                    <div class="chart-empty">Send some chat requests to see the timeline</div>
                </div>
            </div>

            <!-- Cost + Errors -->
            <div class="card">
                <div class="card-title"><span class="icon">⚠️</span> Error Breakdown</div>
                <div id="error-breakdown">
                    <div class="no-errors">✅ No errors recorded</div>
                </div>
            </div>
        </div>

        <!-- Row 4: Request Log -->
        <div class="card section-full fade-in">
            <div class="card-title"><span class="icon">📋</span> Recent Requests <span style="color:var(--text-muted);font-weight:400;font-size:0.75rem;margin-left:auto;">Last 100</span></div>
            <div style="overflow-x:auto;">
                <table class="log-table" id="log-table">
                    <thead>
                        <tr>
                            <th>Time</th>
                            <th>Session</th>
                            <th>Message</th>
                            <th>Latency</th>
                            <th>Tokens</th>
                            <th>Cost</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody id="log-body">
                        <tr><td colspan="7" style="text-align:center;padding:2rem;color:var(--text-muted)">No requests yet — send a message to /chat</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        // ── Auto-refresh every 3 seconds ────────────────────────
        async function fetchAndUpdate() {
            try {
                const res = await fetch('/api/metrics');
                const d = await res.json();

                // Uptime
                const hrs = Math.floor(d.uptime_seconds / 3600);
                const mins = Math.floor((d.uptime_seconds % 3600) / 60);
                document.getElementById('uptime').textContent = `Uptime: ${hrs}h ${mins}m`;

                // Top stats
                document.getElementById('total-requests').textContent = d.total_requests.toLocaleString();
                document.getElementById('success-count').textContent = d.successful_requests.toLocaleString();
                document.getElementById('error-count').textContent = d.failed_requests.toLocaleString();
                document.getElementById('active-sessions').textContent = d.active_sessions;
                document.getElementById('total-cost').textContent = `$${d.total_cost_usd.toFixed(4)}`;
                document.getElementById('avg-cost').textContent = `$${d.avg_cost_per_request.toFixed(4)}`;
                document.getElementById('error-rate').textContent = `${d.error_rate_pct}%`;

                // Latency
                const latColor = (val) => val > 10 ? 'bad' : val > 5 ? 'warn' : '';
                const setLat = (id, val) => {
                    const el = document.getElementById(id);
                    el.textContent = `${val}s`;
                    el.className = 'latency-value ' + latColor(val);
                };
                setLat('avg-latency', d.avg_latency);
                setLat('p50-latency', d.p50_latency);
                setLat('p95-latency', d.p95_latency);
                setLat('p99-latency', d.p99_latency);
                setLat('min-latency', d.min_latency);
                setLat('max-latency', d.max_latency);

                // Tokens
                document.getElementById('total-tokens').textContent = d.total_tokens.toLocaleString();
                document.getElementById('avg-tokens').textContent = d.avg_tokens_per_request.toLocaleString();
                document.getElementById('prompt-tokens').textContent = d.total_prompt_tokens.toLocaleString();
                document.getElementById('completion-tokens').textContent = d.total_completion_tokens.toLocaleString();

                const totalTk = d.total_prompt_tokens + d.total_completion_tokens;
                const promptPct = totalTk > 0 ? (d.total_prompt_tokens / totalTk * 100) : 50;
                document.getElementById('prompt-bar').style.width = `${promptPct}%`;
                document.getElementById('completion-bar').style.width = `${100 - promptPct}%`;

                // Timeline chart
                renderTimeline(d.timeline);

                // Error breakdown
                renderErrors(d.error_counts, d.failed_requests);

                // Request log
                renderLog(d.recent_requests);

            } catch (err) {
                console.error('Dashboard fetch error:', err);
            }
        }

        function renderTimeline(timeline) {
            const container = document.getElementById('timeline-chart');
            if (!timeline || timeline.length === 0) {
                container.innerHTML = '<div class="chart-empty">Send some chat requests to see the timeline</div>';
                return;
            }

            const maxReq = Math.max(...timeline.map(t => t.requests), 1);
            let html = '<div class="chart-bars">';
            timeline.forEach((t, i) => {
                const height = Math.max((t.requests / maxReq) * 130, 4);
                const errorHeight = t.errors > 0 ? Math.max((t.errors / maxReq) * 130, 3) : 0;
                const showLabel = i % 3 === 0 || i === timeline.length - 1;
                html += `
                    <div class="chart-bar-group" title="${t.time} — ${t.requests} req, ${t.errors} err, ${t.avg_latency}s avg">
                        ${errorHeight > 0 ? `<div class="chart-bar error" style="height:${errorHeight}px"></div>` : ''}
                        <div class="chart-bar" style="height:${height}px">
                            ${showLabel ? `<span class="chart-label">${t.time}</span>` : ''}
                        </div>
                    </div>`;
            });
            html += '</div>';
            container.innerHTML = html;
        }

        function renderErrors(errorCounts, totalErrors) {
            const container = document.getElementById('error-breakdown');
            if (totalErrors === 0) {
                container.innerHTML = '<div class="no-errors">✅ No errors recorded</div>';
                return;
            }
            let html = '<div class="error-list">';
            for (const [type, count] of Object.entries(errorCounts)) {
                html += `
                    <div class="error-item">
                        <span class="error-type">${type}</span>
                        <span class="error-count">${count}</span>
                    </div>`;
            }
            html += '</div>';
            container.innerHTML = html;
        }

        function renderLog(requests) {
            const tbody = document.getElementById('log-body');
            if (!requests || requests.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:2rem;color:var(--text-muted)">No requests yet — send a message to /chat</td></tr>';
                return;
            }
            let html = '';
            requests.forEach(r => {
                const badge = r.status === 'success'
                    ? '<span class="badge badge-success">OK</span>'
                    : `<span class="badge badge-error">${r.error_type || 'ERR'}</span>`;
                html += `
                    <tr>
                        <td>${r.timestamp}</td>
                        <td><code style="color:var(--accent-blue)">${r.session_id}</code></td>
                        <td class="msg-col">${r.message}</td>
                        <td>${r.latency}s</td>
                        <td>${r.tokens.toLocaleString()}</td>
                        <td>${r.cost}</td>
                        <td>${badge}</td>
                    </tr>`;
            });
            tbody.innerHTML = html;
        }

        // Initial fetch + interval
        fetchAndUpdate();
        setInterval(fetchAndUpdate, 3000);
    </script>
</body>
</html>"""
