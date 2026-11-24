/* =========================================
   Customer Feedback Intelligence — Dashboard Charts
   Reads window.dashboardData set by index.html
   ========================================= */

(function () {
    "use strict";

    const data = window.dashboardData;

    if (!data) {
        return;
    }

    // -----------------------------------------
    // Shared chart defaults
    // -----------------------------------------
    Chart.defaults.font.family =
        "'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
    Chart.defaults.font.size = 13;
    Chart.defaults.color = "#4a5568";

    // -----------------------------------------
    // 1. Sentiment Distribution (Doughnut)
    // -----------------------------------------
    const sentimentCanvas = document.getElementById("sentimentChart");
    if (sentimentCanvas) {
        new Chart(sentimentCanvas.getContext("2d"), {
            type: "doughnut",
            data: {
                labels: ["Positive", "Neutral", "Negative"],
                datasets: [{
                    data: [
                        data.sentiment_counts.Positive,
                        data.sentiment_counts.Neutral,
                        data.sentiment_counts.Negative
                    ],
                    backgroundColor: ["#10b981", "#f59e0b", "#ef4444"],
                    borderColor: ["#059669", "#d97706", "#dc2626"],
                    borderWidth: 2,
                    hoverOffset: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                cutout: "62%",
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: {
                            padding: 16,
                            usePointStyle: true,
                            pointStyle: "circle"
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function (ctx) {
                                const total = ctx.dataset.data.reduce(
                                    (a, b) => a + b, 0
                                );
                                const value = ctx.parsed;
                                const pct = total
                                    ? ((value / total) * 100).toFixed(1)
                                    : "0.0";
                                return ` ${ctx.label}: ${value} (${pct}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    // -----------------------------------------
    // 2. Product Sentiment Comparison (Bar)
    // -----------------------------------------
    const productCanvas = document.getElementById("productChart");
    if (productCanvas) {
        const products = data.product_summary;

        new Chart(productCanvas.getContext("2d"), {
            type: "bar",
            data: {
                labels: products.map((p) => p.product),
                datasets: [
                    {
                        label: "Positive",
                        data: products.map((p) => p.positive),
                        backgroundColor: "#10b981",
                        borderColor: "#059669",
                        borderWidth: 1,
                        borderRadius: 4
                    },
                    {
                        label: "Negative",
                        data: products.map((p) => p.negative),
                        backgroundColor: "#ef4444",
                        borderColor: "#dc2626",
                        borderWidth: 1,
                        borderRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: { usePointStyle: true, pointStyle: "circle" }
                    }
                },
                scales: {
                    x: { grid: { display: false } },
                    y: {
                        beginAtZero: true,
                        ticks: { precision: 0 },
                        grid: { color: "#e2e8f0" }
                    }
                }
            }
        });
    }

    // -----------------------------------------
    // 3. Complaint Categories (Horizontal Bar)
    // -----------------------------------------
    const complaintCanvas = document.getElementById("complaintChart");
    if (complaintCanvas) {
        const complaints = data.complaint_summary;

        new Chart(complaintCanvas.getContext("2d"), {
            type: "bar",
            data: {
                labels: complaints.map((c) => c.category),
                datasets: [{
                    label: "Count",
                    data: complaints.map((c) => c.count),
                    backgroundColor: "#3b82f6",
                    borderColor: "#2563eb",
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                indexAxis: "y",
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: { precision: 0 },
                        grid: { color: "#e2e8f0" }
                    },
                    y: { grid: { display: false } }
                }
            }
        });
    }

    // -----------------------------------------
    // 4. Top Keywords (Horizontal Bar)
    // -----------------------------------------
    const keywordCanvas = document.getElementById("keywordChart");
    if (keywordCanvas) {
        const keywords = data.top_keywords;

        new Chart(keywordCanvas.getContext("2d"), {
            type: "bar",
            data: {
                labels: keywords.map((k) => k.keyword),
                datasets: [{
                    label: "Frequency",
                    data: keywords.map((k) => k.count),
                    backgroundColor: "#8b5cf6",
                    borderColor: "#7c3aed",
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                indexAxis: "y",
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: { precision: 0 },
                        grid: { color: "#e2e8f0" }
                    },
                    y: { grid: { display: false } }
                }
            }
        });
    }
})();