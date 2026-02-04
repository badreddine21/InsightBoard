async function uploadAndAnalyze(event) {
    event.preventDefault(); // THIS IS CRITICAL - prevents page reload

    const fileInput = document.getElementById('fileInput');
    const statusEl = document.getElementById('status');
    const file = fileInput.files[0];

    if (!file) {
        statusEl.textContent = 'Please select a file';
        return;
    }

    statusEl.textContent = 'Analyzing...';

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
        displayResults(result);

    } catch (error) {
        statusEl.textContent = `Failed: ${error.message}`;
    }
}

function renderDashboard(data) {
    const dashboard = document.getElementById('dashboard');
    dashboard.innerHTML = ''; // Clear old charts

    // 1. Update Big Number KPIs
    document.getElementById('total-rev').innerText = "$" + data.kpis.total_revenue.toLocaleString();
    document.getElementById('total-rows').innerText = data.kpis.row_count.toLocaleString();

    // 2. Loop through recommended charts
    Object.keys(data.charts).forEach(chartType => {
        const chartData = data.charts[chartType];
        const div = document.createElement('div');
        div.className = 'chart-box';
        const canvas = document.createElement('canvas');
        div.appendChild(canvas);
        dashboard.appendChild(div);

        if (chartType === 'waterfall') {
            renderWaterfall(canvas.getContext('2d'), chartData); //
        } else {
            renderStandardChart(canvas.getContext('2d'), chartType, chartData); //
        }
    });
}
function renderWaterfall(ctx, data) {
    let runningTotal = 0;
    const floatingData = data.values.map((v) => {
        let start = runningTotal;
        runningTotal += v;
        return [start, runningTotal]; // [bottom of bar, top of bar]
    });

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: data.title || 'Financial Bridge',
                data: floatingData,
                backgroundColor: data.values.map(v => v >= 0 ? '#2ecc71' : '#e74c3c')
            }]
        },
        options: {
            plugins: {
                tooltip: {
                    callbacks: {
                        label: (ctx) => `Amount: ${data.values[ctx.dataIndex].toLocaleString()}`
                    }
                }
            }
        }
    });
}