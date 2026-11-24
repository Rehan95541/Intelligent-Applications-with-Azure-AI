(function () {
    "use strict";
    const data = window.dashboardData;
    if (!data) return;

    Chart.defaults.font.family = "'Inter', 'Segoe UI', sans-serif";
    Chart.defaults.font.size = 13;
    Chart.defaults.color = "#4a5568";

    new Chart(document.getElementById("sentimentChart").getContext("2d"), {
        type: "doughnut",
        data: {
            labels: ["Positive", "Neutral", "Negative"],
            datasets: [{
                data: [data.sentiment_counts.Positive, data.sentiment_counts.Neutral, data.sentiment_counts.Negative],
                backgroundColor: ["#10b981", "#f59e0b", "#ef4444"],
                borderColor: ["#059669", "#d97706", "#dc2626"],
                borderWidth: 2
            }]
        },
        options: { responsive: true, maintainAspectRatio: true, cutout: "62%",
            plugins: { legend: { position: "bottom", labels: { usePointStyle: true, pointStyle: "circle" } } } }
    });

    new Chart(document.getElementById("productChart").getContext("2d"), {
        type: "bar",
        data: {
            labels: data.product_summary.map(p => p.product),
            datasets: [
                { label: "Positive", data: data.product_summary.map(p => p.positive), backgroundColor: "#10b981", borderRadius: 4 },
                { label: "Negative", data: data.product_summary.map(p => p.negative), backgroundColor: "#ef4444", borderRadius: 4 }
            ]
        },
        options: { responsive: true, plugins: { legend: { position: "bottom" } },
            scales: { x: { grid: { display: false } }, y: { beginAtZero: true, ticks: { precision: 0 } } } }
    });

    new Chart(document.getElementById("complaintChart").getContext("2d"), {
        type: "bar",
        data: {
            labels: data.complaint_summary.map(c => c.category),
            datasets: [{ label: "Count", data: data.complaint_summary.map(c => c.count), backgroundColor: "#3b82f6", borderRadius: 4 }]
        },
        options: { responsive: true, indexAxis: "y", plugins: { legend: { display: false } },
            scales: { x: { beginAtZero: true, ticks: { precision: 0 } }, y: { grid: { display: false } } } }
    });

    new Chart(document.getElementById("keywordChart").getContext("2d"), {
        type: "bar",
        data: {
            labels: data.top_keywords.map(k => k.keyword),
            datasets: [{ label: "Frequency", data: data.top_keywords.map(k => k.count), backgroundColor: "#8b5cf6", borderRadius: 4 }]
        },
        options: { responsive: true, indexAxis: "y", plugins: { legend: { display: false } },
            scales: { x: { beginAtZero: true, ticks: { precision: 0 } }, y: { grid: { display: false } } } }
    });
})();