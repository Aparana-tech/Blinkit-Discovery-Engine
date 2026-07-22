// Tab Switching Logic
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        // Remove active class from all tabs
        document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
        
        // Add active class to clicked tab
        e.target.classList.add('active');
        const targetId = e.target.getAttribute('data-target');
        document.getElementById(targetId).classList.add('active');
    });
});

// Sidebar Toggle Logic
const sidebar = document.getElementById('sidebar');
const mainContent = document.getElementById('main-content');
const sidebarToggle = document.getElementById('sidebar-toggle');

sidebarToggle.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
    mainContent.classList.toggle('expanded');
    
    if (sidebar.classList.contains('collapsed')) {
        sidebarToggle.innerHTML = '❯';
    } else {
        sidebarToggle.innerHTML = '❮';
    }
});

// Load and Render Data
const DATA_URL = '/data/processed/clusters_2026-07.json';
const REPORT_URL = '/data/insights/report_2026-07.md';

async function initDashboard() {
    try {
        // Load Markdown Report for Executive Briefing
        const reportRes = await fetch(REPORT_URL);
        if (reportRes.ok) {
            const markdown = await reportRes.text();
            document.getElementById('report-container').innerHTML = marked.parse(markdown);
        }

        // Load JSON Clusters
        const response = await fetch(DATA_URL);
        if (!response.ok) throw new Error('Data not found');
        let clusters = await response.json();
        
        // Filter out noise
        clusters = clusters.filter(c => c.cluster_id !== -1);
        clusters.sort((a, b) => b.size - a.size);

        renderDeepDive(clusters);
        renderWhatUsersSay(clusters);
        renderCharts(clusters);
    } catch (e) {
        console.error("Failed to load dashboard data:", e);
    }
}

function renderDeepDive(clusters) {
    const container = document.getElementById('deepdive-list');
    container.innerHTML = '';
    
    clusters.slice(0, 10).forEach((cluster, index) => {
        const div = document.createElement('div');
        div.className = 'deepdive-item';
        div.innerHTML = `
            <div class="deepdive-number">${index + 1}</div>
            <div class="deepdive-content">
                <h3>${cluster.theme_name}</h3>
                <div class="meta">${cluster.size} mentions in discovery-tagged reviews</div>
                <div class="deepdive-quote">
                    <strong>Insight:</strong> ${cluster.actionable_insight}<br><br>
                    <em>"${cluster.best_quote}"</em>
                </div>
                <div class="pill-tag">${cluster.pillar}</div>
            </div>
        `;
        container.appendChild(div);
    });
}

function renderWhatUsersSay(clusters) {
    const container = document.getElementById('insights-grid');
    container.innerHTML = '';

    clusters.forEach(cluster => {
        const div = document.createElement('div');
        div.className = 'q-card';
        div.innerHTML = `
            <h4 style="font-size:1.1rem; color:#fff; margin-bottom:8px;">${cluster.theme_name}</h4>
            <div style="color:var(--text-muted); font-size:0.85rem; margin-bottom:16px;">
                ${cluster.size} mentions <span style="color:var(--accent); margin-left:8px;">+ High Impact</span>
            </div>
            <p style="color:var(--text-muted); font-size:0.9rem; line-height:1.6;">
                Reviewers repeatedly flag issues tied to ${cluster.theme_name.toLowerCase()}. 
                <br><br>${cluster.actionable_insight}
            </p>
        `;
        container.appendChild(div);
    });
}

function renderCharts(clusters) {
    // Simple bar chart of top 5 issues
    const top5 = clusters.slice(0, 5);
    new Chart(document.getElementById('barChart'), {
        type: 'bar',
        data: {
            labels: top5.map(c => c.theme_name),
            datasets: [{
                label: 'Mentions',
                data: top5.map(c => c.size),
                backgroundColor: '#F8CB46',
                hoverBackgroundColor: '#ffe387',
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            onHover: (event, chartElement) => {
                event.native.target.style.cursor = chartElement[0] ? 'pointer' : 'default';
            },
            plugins: { legend: { display: false } },
            scales: {
                y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#a7a7a7' } },
                x: { grid: { display: false }, ticks: { color: '#a7a7a7' } }
            }
        }
    });

    // Pillar pie chart
    const pillarCounts = {};
    clusters.forEach(c => {
        pillarCounts[c.pillar] = (pillarCounts[c.pillar] || 0) + c.size;
    });

    new Chart(document.getElementById('pieChart'), {
        type: 'doughnut',
        data: {
            labels: Object.keys(pillarCounts),
            datasets: [{
                data: Object.values(pillarCounts),
                backgroundColor: ['#F8CB46', '#4CAF50', '#e53e3e', '#3182ce'],
                borderWidth: 0,
                hoverOffset: 15
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            onHover: (event, chartElement) => {
                event.native.target.style.cursor = chartElement[0] ? 'pointer' : 'default';
            },
            plugins: {
                legend: { position: 'bottom', labels: { color: '#a7a7a7' } }
            }
        }
    });
}

// Chatbot Logic
async function sendChatMessage(message) {
    if (!message) return;
    
    const history = document.getElementById('chat-history');
    
    // Add user message
    history.innerHTML += `
        <div class="chat-message user">
            <span class="avatar">👤</span>
            <div class="msg-content">${message}</div>
        </div>
    `;
    
    // Clear input
    document.getElementById('chat-input').value = '';
    history.scrollTop = history.scrollHeight;

    // Add loading state
    const loadingId = 'loading-' + Date.now();
    history.innerHTML += `
        <div class="chat-message system" id="${loadingId}">
            <span class="avatar">🤖</span>
            <div class="msg-content">Thinking...</div>
        </div>
    `;
    history.scrollTop = history.scrollHeight;

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });
        
        const data = await response.json();
        const msgStr = data.response || data.detail || "Error communicating with AI.";
        
        // Remove loading state and add real response
        document.getElementById(loadingId).remove();
        history.innerHTML += `
            <div class="chat-message system">
                <span class="avatar">🤖</span>
                <div class="msg-content">${marked.parse(msgStr)}</div>
            </div>
        `;
        history.scrollTop = history.scrollHeight;
    } catch (e) {
        document.getElementById(loadingId).remove();
        history.innerHTML += `
            <div class="chat-message system">
                <span class="avatar">⚠️</span>
                <div class="msg-content">Server error. Make sure the FastAPI backend is running.</div>
            </div>
        `;
    }
}

document.getElementById('chat-submit').addEventListener('click', () => {
    sendChatMessage(document.getElementById('chat-input').value);
});

document.getElementById('chat-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendChatMessage(e.target.value);
    }
});

function sendPredefined(message) {
    sendChatMessage(message);
}

// Initialize
initDashboard();
