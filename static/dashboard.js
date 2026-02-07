async function initDashboard() {
    try {
        const response = await fetch('/api/data');
        const data = await response.json();

        // Check if data exists (has actual values)
        const hasData = data.daily_sales && data.daily_sales.labels && data.daily_sales.labels.length > 0;
        
        if (!hasData) {
            // Show empty state
            document.getElementById('emptyState').style.display = 'flex';
            document.getElementById('chartsContainer').style.display = 'none';
            return;
        }
        
        // Hide empty state and show charts
        document.getElementById('emptyState').style.display = 'none';
        document.getElementById('chartsContainer').style.display = 'block';

        // Populate KPI Stats
        populateStats(data);

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

function populateStats(data) {
    // Calculate total revenue
    const totalRevenue = data.daily_sales.values.reduce((sum, val) => sum + val, 0);
    document.getElementById('totalRevenue').textContent = '$' + totalRevenue.toLocaleString(undefined, {maximumFractionDigits: 0});
    
    // Total transactions
    const totalTransactions = data.daily_sales.labels.length;
    document.getElementById('totalTransactions').textContent = totalTransactions;
    
    // Average transaction
    const avgTransaction = totalRevenue / totalTransactions;
    document.getElementById('avgTransaction').textContent = '$' + avgTransaction.toLocaleString(undefined, {maximumFractionDigits: 0});
    
    // Peak day (find the day with highest sales)
    const maxValue = Math.max(...data.daily_sales.values);
    const maxIndex = data.daily_sales.values.indexOf(maxValue);
    const peakDay = data.daily_sales.labels[maxIndex];
    document.getElementById('peakDay').textContent = peakDay;
    document.getElementById('peakValue').textContent = '$' + maxValue.toLocaleString(undefined, {maximumFractionDigits: 0});
    
    // For demo purposes, showing positive changes
    // In a real app, you'd compare with previous period
    document.getElementById('revenueChange').textContent = '+12.5%';
    document.getElementById('transactionsChange').textContent = '+8.3%';
    document.getElementById('avgChange').textContent = '+3.2%';
}

document.addEventListener('DOMContentLoaded', initDashboard);