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
            data.bonus_report.forEach((emp, index) => {
                const row = `
                    <tr class="hr-row">
                        <td>${emp.name}</td>
                        <td>$${Number(emp.total_sales).toLocaleString()}</td>
                        <td class="bonus-value">$${Number(emp.bonus).toLocaleString()}</td>
                        <td>
                            <select class="status-select" id="status-${index}" onchange="updateBonusStatus(${index}, '${emp.name}')">
                                <option value="approved" class="approved">✓ Approved</option>
                                <option value="not-approved" class="not-approved">✗ Not Approved</option>
                            </select>
                        </td>
                        <td><button class="approve-btn" onclick="approveBonusAlert('${emp.name}')">Approve</button></td>
                    </tr>`;
                tableBody.innerHTML += row;
            });
        }


    } catch (err) {
        console.error("Dashboard failed to load:", err);
    }
}

function updateBonusStatus(index, empName) {
    const selectElement = document.getElementById(`status-${index}`);
    const status = selectElement.value;
    
    if (status === 'approved') {
        selectElement.classList.remove('not-approved');
        selectElement.classList.add('approved');
    } else {
        selectElement.classList.remove('approved');
        selectElement.classList.add('not-approved');
    }
}

function approveBonusAlert(empName) {
    alert(`Bonus approved for ${empName}`);
}

document.addEventListener('DOMContentLoaded', initDashboard);