async function initInsights() {
    try {
        const response = await fetch('/api/data');
        const data = await response.json();

        const insightsList = document.getElementById('insightsList');
        if (!insightsList) return;

        const dailyLabels = (data.daily_sales && data.daily_sales.labels) ? data.daily_sales.labels : [];
        const dailyValues = (data.daily_sales && data.daily_sales.values) ? data.daily_sales.values.map(v => Number(v)).filter(v => !Number.isNaN(v)) : [];
        const topProductLabel = (data.top_products && data.top_products.labels && data.top_products.labels[0]) ? data.top_products.labels[0] : null;
        const topProductValue = (data.top_products && data.top_products.values && data.top_products.values[0]) ? Number(data.top_products.values[0]) : null;
        const topCashierLabel = (data.cashier_sales && data.cashier_sales.labels && data.cashier_sales.labels[0]) ? data.cashier_sales.labels[0] : null;
        const topCashierValue = (data.cashier_sales && data.cashier_sales.values && data.cashier_sales.values[0]) ? Number(data.cashier_sales.values[0]) : null;
        const discountLabels = (data.discounts && data.discounts.labels) ? data.discounts.labels : [];
        const discountValues = (data.discounts && data.discounts.values) ? data.discounts.values.map(v => Number(v)).filter(v => !Number.isNaN(v)) : [];

        const insights = [];

        if (dailyValues.length > 0) {
            const totalSales = dailyValues.reduce((a, b) => a + b, 0);
            const avgDaily = totalSales / dailyValues.length;
            const maxDaily = Math.max(...dailyValues);
            const maxIndex = dailyValues.indexOf(maxDaily);
            const bestDayLabel = dailyLabels[maxIndex] || 'N/A';

            insights.push(`Total sales: $${totalSales.toLocaleString(undefined, { maximumFractionDigits: 2 })}`);
            insights.push(`Average daily sales: $${avgDaily.toLocaleString(undefined, { maximumFractionDigits: 2 })}`);
            insights.push(`Best sales day: ${bestDayLabel} ($${maxDaily.toLocaleString(undefined, { maximumFractionDigits: 2 })})`);
        }

        if (topProductLabel) {
            insights.push(`Top product: ${topProductLabel} (${topProductValue?.toLocaleString() || 0} units)`);
        }

        if (topCashierLabel) {
            insights.push(`Top cashier: ${topCashierLabel} ($${topCashierValue?.toLocaleString(undefined, { maximumFractionDigits: 2 }) || 0})`);
        }

        if (discountValues.length > 0) {
            const totalDiscount = discountValues.reduce((a, b) => a + b, 0);
            const maxDiscount = Math.max(...discountValues);
            const maxDiscountIndex = discountValues.indexOf(maxDiscount);
            const maxDiscountProduct = discountLabels[maxDiscountIndex] || 'N/A';
            insights.push(`Total discounts: $${totalDiscount.toLocaleString(undefined, { maximumFractionDigits: 2 })}`);
            insights.push(`Highest discount by product: ${maxDiscountProduct} ($${maxDiscount.toLocaleString(undefined, { maximumFractionDigits: 2 })})`);
        }

        if (insights.length === 0) {
            insightsList.innerHTML = '<li class="insight-item">No insights available.</li>';
        } else {
            insightsList.innerHTML = insights.map(text => `<li class="insight-item">${text}</li>`).join('');
        }
    } catch (err) {
        console.error('Insights failed to load:', err);
    }
}

document.addEventListener('DOMContentLoaded', initInsights);
