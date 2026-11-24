(function () {
    "use strict";

    const askBtn = document.getElementById("ragAskBtn");
    if (!askBtn) return;

    const questionEl = document.getElementById("ragQuestion");
    const answerArea = document.getElementById("ragAnswerArea");
    const answerText = document.getElementById("ragAnswerText");
    const sourcesList = document.getElementById("ragSourcesList");
    const errorBox = document.getElementById("ragError");
    const thresholdEl = document.getElementById("ragThreshold");
    const thresholdVal = document.getElementById("thresholdValue");
    const backendLabel = document.getElementById("ragBackendLabel");

    if (backendLabel && window.ragBackendName) {
        backendLabel.textContent = window.ragBackendName;
    }

    const savedThreshold = localStorage.getItem("ragThreshold");
    if (savedThreshold !== null) {
        thresholdEl.value = savedThreshold;
        thresholdVal.textContent = parseFloat(savedThreshold).toFixed(2);
    }

    thresholdEl.addEventListener("input", function () {
        thresholdVal.textContent = parseFloat(this.value).toFixed(2);
        localStorage.setItem("ragThreshold", this.value);
    });

    document.querySelectorAll(".chip").forEach(function (chip) {
        chip.addEventListener("click", function () {
            questionEl.value = this.dataset.question;
            questionEl.focus();
        });
    });

    function showError(msg) {
        errorBox.textContent = msg;
        errorBox.style.display = "block";
    }

    function clearError() {
        errorBox.style.display = "none";
    }

    askBtn.addEventListener("click", function () {
        const question = questionEl.value.trim();
        if (!question) {
            showError("Please enter a question.");
            return;
        }
        clearError();
        askBtn.disabled = true;
        askBtn.textContent = "Searching...";

        const payload = {
            question: question,
            filters: {
                product: document.getElementById("ragProductFilter").value,
                sentiment: document.getElementById("ragSentimentFilter").value,
                category: document.getElementById("ragCategoryFilter").value
            },
            top_k: parseInt(document.getElementById("ragTopK").value, 10),
            threshold: parseFloat(thresholdEl.value)
        };

        fetch("/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        })
            .then(r => r.json())
            .then(data => {
                if (data.error) {
                    showError(data.error);
                    return;
                }

                answerText.textContent = data.answer;
                sourcesList.innerHTML = "";

                if (data.sources && data.sources.length) {
                    data.sources.forEach(function (s) {
                        const li = document.createElement("li");
                        li.innerHTML =
                            '<div class="source-meta">' +
                            '<span class="source-product">' + escapeHtml(s.product) + '</span>' +
                            '<span class="source-similarity">sim: ' + s.similarity.toFixed(3) + '</span>' +
                            '<span class="sentiment-badge sentiment-' + s.sentiment.toLowerCase() + '">' + escapeHtml(s.sentiment) + '</span>' +
                            '</div>' +
                            '<div class="source-feedback">' + escapeHtml(s.feedback) + '</div>';
                        sourcesList.appendChild(li);
                    });
                } else {
                    sourcesList.innerHTML = "<li class='muted'>No sources passed the threshold.</li>";
                }

                answerArea.style.display = "block";
            })
            .catch(err => showError("Request failed: " + err.message))
            .finally(function () {
                askBtn.disabled = false;
                askBtn.textContent = "Ask";
            });
    });

    questionEl.addEventListener("keypress", function (e) {
        if (e.key === "Enter") askBtn.click();
    });

    function escapeHtml(s) {
        return String(s || "").replace(/[&<>"']/g, function (c) {
            return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
        });
    }

    const searchInput = document.getElementById("feedbackSearch");
    const sentimentFilter = document.getElementById("feedbackSentimentFilter");
    const productFilter = document.getElementById("feedbackProductFilter");
    const feedbackTable = document.getElementById("feedbackTable");
    const feedbackCount = document.getElementById("feedbackCount");
    const prevBtn = document.getElementById("prevPage");
    const nextBtn = document.getElementById("nextPage");
    const pageInfo = document.getElementById("pageInfo");

    if (feedbackTable) {
        const allRows = Array.from(feedbackTable.querySelectorAll("tbody tr"));
        const PAGE_SIZE = 10;
        let currentPage = 1;
        let filteredRows = allRows.slice();

        function applyFilters() {
            const q = (searchInput?.value || "").toLowerCase();
            const sent = sentimentFilter?.value || "";
            const prod = productFilter?.value || "";

            filteredRows = allRows.filter(function (row) {
                const text = row.textContent.toLowerCase();
                const rowSent = row.dataset.sentiment || "";
                const rowProd = row.dataset.product || "";
                if (q && !text.includes(q)) return false;
                if (sent && rowSent !== sent) return false;
                if (prod && rowProd !== prod) return false;
                return true;
            });

            currentPage = 1;
            renderPage();
        }

        function renderPage() {
            const totalPages = Math.max(1, Math.ceil(filteredRows.length / PAGE_SIZE));
            if (currentPage > totalPages) currentPage = totalPages;
            const start = (currentPage - 1) * PAGE_SIZE;
            const end = start + PAGE_SIZE;

            allRows.forEach(r => (r.style.display = "none"));
            filteredRows.slice(start, end).forEach(r => (r.style.display = ""));

            if (pageInfo) pageInfo.textContent = "Page " + currentPage + " of " + totalPages;
            if (prevBtn) prevBtn.disabled = currentPage <= 1;
            if (nextBtn) nextBtn.disabled = currentPage >= totalPages;
            if (feedbackCount) feedbackCount.textContent = filteredRows.length + " rows";
        }

        if (searchInput) searchInput.addEventListener("input", applyFilters);
        if (sentimentFilter) sentimentFilter.addEventListener("change", applyFilters);
        if (productFilter) productFilter.addEventListener("change", applyFilters);

        if (prevBtn) prevBtn.addEventListener("click", function () {
            if (currentPage > 1) { currentPage--; renderPage(); }
        });
        if (nextBtn) nextBtn.addEventListener("click", function () {
            currentPage++;
            renderPage();
        });

        renderPage();
    }

    document.querySelectorAll("table.sortable").forEach(function (table) {
        const headers = table.querySelectorAll("thead th[data-sort]");
        headers.forEach(function (th) {
            th.style.cursor = "pointer";
            th.title = "Click to sort";
            let dir = 1;
            th.addEventListener("click", function () {
                const tbody = table.querySelector("tbody");
                const rows = Array.from(tbody.querySelectorAll("tr"));
                const idx = Array.from(th.parentNode.children).indexOf(th);
                const isNum = th.dataset.sort === "num";

                rows.sort(function (a, b) {
                    const av = a.children[idx].textContent.trim();
                    const bv = b.children[idx].textContent.trim();
                    if (isNum) {
                        const an = parseFloat(av.replace(/[^0-9.\-]/g, "")) || 0;
                        const bn = parseFloat(bv.replace(/[^0-9.\-]/g, "")) || 0;
                        return (an - bn) * dir;
                    }
                    return av.localeCompare(bv) * dir;
                });

                dir *= -1;
                rows.forEach(r => tbody.appendChild(r));

                headers.forEach(h => h.classList.remove("sort-asc", "sort-desc"));
                th.classList.add(dir === 1 ? "sort-desc" : "sort-asc");
            });
        });
    });

    const uploadForm = document.getElementById("uploadForm");
    const analyzeBtn = document.getElementById("analyzeBtn");
    if (uploadForm && analyzeBtn) {
        uploadForm.addEventListener("submit", function () {
            analyzeBtn.disabled = true;
            analyzeBtn.classList.add("loading");
            analyzeBtn.innerHTML = '<span class="spinner"></span> Analyzing...';
        });
    }

    const fileInput = document.getElementById("file");
    const fileName = document.getElementById("fileName");
    if (fileInput && fileName) {
        fileInput.addEventListener("change", function () {
            fileName.textContent = this.files.length ? this.files[0].name : "No file chosen";
        });
    }
})();