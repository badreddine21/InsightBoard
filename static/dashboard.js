async function initDashboard() {
    try {
        const response = await fetch('/api/data');
        const data = await response.json();

        // 1. Line Chart: Daily Sales
        const salesCanvas = document.getElementById('salesChart');
        if (salesCanvas) {
            new Chart(salesCanvas, {
                type: 'line',
                data: {
                    labels: data.daily_sales.labels,
                    datasets: [{
                        label: 'Net Amount ($)',
                        data: data.daily_sales.values,
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        fill: true,
                        tension: 0.3
                    }]
                }
            });
        }

        // 2. Bar Chart: Top Products
        const productCanvas = document.getElementById('productChart');
        if (productCanvas) {
            new Chart(productCanvas, {
                type: 'bar',
                data: {
                    labels: data.top_products.labels,
                    datasets: [{
                        label: 'Units Sold',
                        data: data.top_products.values,
                        backgroundColor: '#e74c3c'
                    }]
                },
                options: { indexAxis: 'y' }
            });
        }

        // 3. Doughnut Chart: Cashier Sales
        const cashierCanvas = document.getElementById('cashierChart');
        if (cashierCanvas) {
            new Chart(cashierCanvas, {
                type: 'doughnut',
                data: {
                    labels: data.cashier_sales.labels,
                    datasets: [{
                        data: data.cashier_sales.values,
                        backgroundColor: ['#2ecc71', '#f1c40f', '#9b59b6', '#34495e']
                    }]
                }
            });
        }

        // 4. Bar Chart: Discounts
        const discountCanvas = document.getElementById('discountChart');
        if (discountCanvas) {
            new Chart(discountCanvas, {
                type: 'bar',
                data: {
                    labels: data.discounts.labels,
                    datasets: [{
                        label: 'Total Discount ($)',
                        data: data.discounts.values,
                        backgroundColor: '#95a5a6'
                    }]
                }
            });
        }

        // 5. Bonus table for HR view
        const tableBody = document.getElementById('bonusTableBody');
        if (tableBody && data.bonus_report) {
            tableBody.innerHTML = '';
            data.bonus_report.forEach(emp => {
                const row = `
                    <tr style="border-bottom: 1px solid #eee; height: 40px;">
                        <td>${emp.name}</td>
                        <td>$${Number(emp.total_sales).toLocaleString()}</td>
                        <td style="color: #27ae60; font-weight: bold;">$${Number(emp.bonus).toLocaleString()}</td>
                        <td><button onclick="alert('Bonus approved for ${emp.name}')">Approve</button></td>
                    </tr>`;
                tableBody.innerHTML += row;
            });
        }

        // Boss comment: save locally in browser storage
        const commentInput = document.getElementById('bossComment');
        const commentButton = document.getElementById('bossCommentSubmit');
        if (commentInput) {
            const storageKey = 'insightboard_boss_comment';
            const saved = localStorage.getItem(storageKey);
            if (saved) {
                commentInput.value = saved;
            }

            if (commentButton) {
                commentButton.addEventListener('click', () => {
                    localStorage.setItem(storageKey, commentInput.value || '');
                    alert('Comment saved locally in this browser.');
                });
            }
        }

    } catch (err) {
        console.error("Dashboard failed to load:", err);
    }
}

document.addEventListener('DOMContentLoaded', initDashboard);