async function uploadAndAnalyze(event) {
    event.preventDefault();

    const fileInput = document.getElementById('fileInput');
    const statusEl = document.getElementById('status');
    const file = fileInput.files[0];

    if (!file) {
        statusEl.textContent = 'Please select a file';
        return;
    }

    statusEl.textContent = 'Analyzing... This may take a moment.';

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('http://127.0.0.1:8000/analyze', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.error) {
            statusEl.textContent = `Error: ${result.error}`;
            return;
        }

        statusEl.textContent = 'Analysis complete!';
        renderDashboard(result); // Corrected function name

    } catch (error) {
        console.error(error);
        statusEl.textContent = `Failed: ${error.message}`;
    }
}

function renderDashboard(data) {
    const dashboard = document.getElementById('dashboard');
    const chartsContainer = document.getElementById('charts-container');

    // Show the dashboard
    dashboard.style.display = 'block';
    chartsContainer.innerHTML = ''; // Clear old charts

    // 1. Update Big Number KPIs
    if (data.kpis) {
        document.getElementById('total-rev').innerText =
            "$" + parseFloat(data.kpis.total_revenue).toLocaleString(undefined, { minimumFractionDigits: 2 });
        document.getElementById('total-rows').innerText =
            data.kpis.row_count.toLocaleString();
    }
    if (data.ai_analysis) {
        const listContainer = document.getElementById('ai-insights-list');
        const paragraphContainer = document.getElementById('ai-paragraph');

        // Clear previous
        listContainer.innerHTML = '';

        // Render Bullet Points
        const ul = document.createElement('ul');
        data.ai_analysis.short_insights.forEach(insight => {
            const li = document.createElement('li');
            li.textContent = insight;
            ul.appendChild(li);
        });
        listContainer.appendChild(ul);

        // Render Paragraph
        paragraphContainer.textContent = data.ai_analysis.paragraph;
    }
    // 2. Loop through charts
    if (data.charts) {
        Object.keys(data.charts).forEach(chartType => {
            const chartData = data.charts[chartType];

            // Create container for canvas
            const div = document.createElement('div');
            div.className = 'chart-box';

            // Add title
            const title = document.createElement('h3');
            title.textContent = chartData.title;
            div.appendChild(title);

            const canvas = document.createElement('canvas');
            div.appendChild(canvas);
            chartsContainer.appendChild(div);

            const ctx = canvas.getContext('2d');

            if (chartType === 'waterfall') {
                renderWaterfall(ctx, chartData);
            } else {
                renderStandardChart(ctx, chartType, chartData);
            }
        });
    }
}

// Added this function which was missing
function renderStandardChart(ctx, type, data) {
    // Chart.js types: 'bar_chart' -> 'bar', 'line_chart' -> 'line'
    const cleanType = type.replace('_chart', '');

    new Chart(ctx, {
        type: cleanType,
        data: {
            labels: data.labels,
            datasets: [{
                label: data.title,
                data: data.values,
                backgroundColor: '#3498db',
                borderColor: '#2980b9',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            }
        }
    });
}

function renderWaterfall(ctx, data) {
    let runningTotal = 0;
    const floatingData = data.values.map((v) => {
        let start = runningTotal;
        runningTotal += v;
        return [start, runningTotal];
    });

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Cash Flow',
                data: floatingData,
                backgroundColor: data.values.map(v => v >= 0 ? '#2ecc71' : '#e74c3c')
            }]
        },
        options: {
            responsive: true,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: (context) => {
                            const val = data.values[context.dataIndex];
                            return `Impact: ${val.toLocaleString()}`;
                        }
                    }
                }
            }
        }
    });
}