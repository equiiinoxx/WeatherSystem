// WeatherScope Analytics Platform - Industrial Client Controller

document.addEventListener('DOMContentLoaded', () => {
    // Dynamically resolve API Base URL (Supports Flask :5000 and VS Code Live Server :5500)
    const API_BASE = window.location.port === '5000' ? '' : 'http://127.0.0.1:5000';

    // DOM References - Ingestion
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('csvFileInput');
    const fileSelectedBadge = document.getElementById('fileSelectedBadge');
    const fileNameDisplay = document.getElementById('fileNameDisplay');
    const fileSizeDisplay = document.getElementById('fileSizeDisplay');
    const btnRemoveFile = document.getElementById('btnRemoveFile');
    const btnExecutePipeline = document.getElementById('btnExecutePipeline');
    const btnLoadSample = document.getElementById('btnLoadSample');
    const btnQuickSample = document.getElementById('btnQuickSample');
    const statusAlert = document.getElementById('statusAlert');
    const loadingOverlay = document.getElementById('loadingOverlay');

    // DOM References - Dashboard & Telemetry
    const dashboardResults = document.getElementById('dashboardResults');
    const kpiTotal = document.getElementById('kpiTotal');
    const kpiValid = document.getElementById('kpiValid');
    const kpiInvalid = document.getElementById('kpiInvalid');
    const kpiScore = document.getElementById('kpiScore');
    const quarantineSection = document.getElementById('quarantineSection');
    const quarantineTableBody = document.getElementById('quarantineTableBody');

    // DOM References - Visuals & Tables
    const imgTempChart = document.getElementById('imgTempChart');
    const imgRainChart = document.getElementById('imgRainChart');
    const btnDownloadTemp = document.getElementById('btnDownloadTemp');
    const btnDownloadRain = document.getElementById('btnDownloadRain');
    const summaryTableBody = document.getElementById('summaryTableBody');
    const summarySearchInput = document.getElementById('summarySearchInput');
    const dbExplorerTableBody = document.getElementById('dbExplorerTableBody');
    const btnRefreshExplorer = document.getElementById('btnRefreshExplorer');
    const btnTruncateExplorer = document.getElementById('btnTruncateExplorer');
    const btnPurgeDb = document.getElementById('btnPurgeDb');

    let currentSummaryData = [];
    let selectedFile = null;

    // --- Drag and Drop File Handlers ---
    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            handleFileSelection(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files.length > 0) {
            handleFileSelection(e.target.files[0]);
        }
    });

    function handleFileSelection(file) {
        if (!file.name.toLowerCase().endsWith('.csv')) {
            showAlert('Invalid file format. Please upload a standard .csv weather dataset.', 'error');
            return;
        }
        selectedFile = file;
        fileNameDisplay.textContent = file.name;
        fileSizeDisplay.textContent = `(${(file.size / 1024).toFixed(1)} KB)`;
        fileSelectedBadge.style.display = 'inline-flex';
        showAlert(`File "${file.name}" staged. Ready to run pipeline.`, 'success');
    }

    // Remove / Deselect Staged File
    btnRemoveFile.addEventListener('click', (e) => {
        e.stopPropagation(); // Prevent opening file picker
        clearSelectedFile();
    });

    function clearSelectedFile() {
        selectedFile = null;
        fileInput.value = '';
        fileSelectedBadge.style.display = 'none';
        showAlert('Staged file removed. Please choose or drop a CSV file.', 'info');
    }

    // --- Pipeline Execution ---
    btnExecutePipeline.addEventListener('click', async () => {
        if (!selectedFile) {
            showAlert('Please select or drop a CSV file first.', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('file', selectedFile);

        showLoading(true);
        showAlert('', '');

        try {
            const res = await fetch(`${API_BASE}/api/upload`, {
                method: 'POST',
                body: formData
            });

            const data = await res.json();
            showLoading(false);

            if (data.success) {
                renderTelemetry(data);
                showAlert(`Ingestion pipeline completed! ${data.database_inserted} records transactionally written to MySQL.`, 'success');
            } else {
                showAlert(`Pipeline failure: ${data.error || 'Server rejected dataset.'}`, 'error');
            }
        } catch (err) {
            showLoading(false);
            showAlert(`Network or Backend error: ${err.message}`, 'error');
        }
    });

    // --- Sample Dataset Ingestion ---
    const loadSampleData = async () => {
        showLoading(true);
        showAlert('Streaming bundled meteorological sample dataset...', 'info');

        try {
            const res = await fetch(`${API_BASE}/api/sample`);
            const data = await res.json();
            showLoading(false);

            if (data.success) {
                renderTelemetry(data);
                showAlert(`Sample dataset processed! ${data.database_inserted} valid records written to MySQL.`, 'success');
            } else {
                showAlert(`Failed to load sample dataset: ${data.error}`, 'error');
            }
        } catch (err) {
            showLoading(false);
            showAlert(`Connection error: ${err.message}`, 'error');
        }
    };

    btnLoadSample.addEventListener('click', loadSampleData);
    btnQuickSample.addEventListener('click', loadSampleData);

    // --- Database Truncate Handlers ---
    const handlePurge = async () => {
        if (!confirm('Are you sure you want to delete all records from weather_records in MySQL?')) {
            return;
        }

        showLoading(true);
        try {
            const res = await fetch(`${API_BASE}/api/records/purge`, { method: 'POST' });
            const data = await res.json();
            showLoading(false);

            if (data.success) {
                showAlert('Database table "weather_records" truncated successfully. All records cleared.', 'success');
                fetchDbRecords();
            } else {
                showAlert(`Failed to clear database: ${data.error}`, 'error');
            }
        } catch (err) {
            showLoading(false);
            showAlert(`Error: ${err.message}`, 'error');
        }
    };

    btnPurgeDb.addEventListener('click', handlePurge);
    btnTruncateExplorer.addEventListener('click', handlePurge);
    btnRefreshExplorer.addEventListener('click', () => fetchDbRecords());

    // --- Render Dashboard Telemetry ---
    function renderTelemetry(data) {
        dashboardResults.style.display = 'block';

        // 1. KPI Telemetry
        const report = data.quality_report;
        const total = report.total_records || 0;
        const valid = report.valid_records || 0;
        const invalid = report.invalid_records || 0;
        const score = total > 0 ? ((valid / total) * 100).toFixed(1) : '100';

        kpiTotal.textContent = total;
        kpiValid.textContent = valid;
        kpiInvalid.textContent = invalid;
        kpiScore.textContent = `${score}%`;

        // 2. Quarantine Audit Table
        if (report.issues && report.issues.length > 0) {
            quarantineSection.style.display = 'block';
            quarantineTableBody.innerHTML = '';

            report.issues.forEach(issue => {
                const tr = document.createElement('tr');
                const rawPayload = Object.entries(issue.raw_values || {})
                    .map(([k, v]) => `<strong>${k}:</strong> ${v}`)
                    .join(' | ');

                tr.innerHTML = `
                    <td><strong>Row #${issue.row}</strong></td>
                    <td class="text-red">${issue.reasons.join('<br>')}</td>
                    <td><code>${rawPayload}</code></td>
                `;
                quarantineTableBody.appendChild(tr);
            });
        } else {
            quarantineSection.style.display = 'none';
        }

        // 3. Matplotlib Visuals
        if (data.charts) {
            imgTempChart.src = `data:image/png;base64,${data.charts.temperature}`;
            imgRainChart.src = `data:image/png;base64,${data.charts.rainfall}`;

            setupChartDownload(btnDownloadTemp, data.charts.temperature, 'temperature_trend.png');
            setupChartDownload(btnDownloadRain, data.charts.rainfall, 'rainfall_comparison.png');
        }

        // 4. Monthly Summary Aggregation
        currentSummaryData = data.summary || [];
        renderSummaryTable(currentSummaryData);

        // 5. Query MySQL Database Records
        fetchDbRecords();

        // Smooth scroll to results
        dashboardResults.scrollIntoView({ behavior: 'smooth' });
    }

    // --- Filter Monthly Summary Table ---
    summarySearchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase().trim();
        if (!query) {
            renderSummaryTable(currentSummaryData);
            return;
        }

        const filtered = currentSummaryData.filter(item => 
            item.month.toLowerCase().includes(query) ||
            item.location.toLowerCase().includes(query)
        );
        renderSummaryTable(filtered);
    });

    function renderSummaryTable(rows) {
        summaryTableBody.innerHTML = '';
        if (rows.length === 0) {
            summaryTableBody.innerHTML = '<tr><td colspan="11" style="text-align: center; color: var(--text-muted);">No monthly summary observations found.</td></tr>';
            return;
        }

        rows.forEach(r => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${r.month}</strong></td>
                <td>${r.location}</td>
                <td>${r.days_observed}</td>
                <td>${r.temp_min}</td>
                <td>${r.temp_max}</td>
                <td><strong>${r.temp_avg}</strong></td>
                <td>${r.humidity_min}</td>
                <td>${r.humidity_max}</td>
                <td>${r.humidity_avg}</td>
                <td><strong>${r.rainfall_total}</strong></td>
                <td>${r.rainfall_avg}</td>
            `;
            summaryTableBody.appendChild(tr);
        });
    }

    // --- Fetch MySQL Records Explorer ---
    async function fetchDbRecords() {
        try {
            const res = await fetch(`${API_BASE}/api/records`);
            const data = await res.json();
            if (data.success && data.records) {
                dbExplorerTableBody.innerHTML = '';
                if (data.records.length === 0) {
                    dbExplorerTableBody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--text-muted);">No records currently stored in weather_records table.</td></tr>';
                    return;
                }
                data.records.forEach(r => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>#${r.record_id}</td>
                        <td>${r.observation_date}</td>
                        <td>${r.location}</td>
                        <td>${r.temperature !== null ? `${r.temperature} °C` : '-'}</td>
                        <td>${r.humidity !== null ? `${r.humidity} %` : '-'}</td>
                        <td>${r.rainfall !== null ? `${r.rainfall} mm` : '-'}</td>
                    `;
                    dbExplorerTableBody.appendChild(tr);
                });
            }
        } catch (err) {
            console.error('Failed to query DB explorer:', err);
        }
    }

    // --- Chart Image Downloader ---
    function setupChartDownload(button, base64Data, filename) {
        button.onclick = () => {
            const a = document.createElement('a');
            a.href = `data:image/png;base64,${base64Data}`;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        };
    }

    // --- UI Helpers ---
    function showLoading(isLoading) {
        loadingOverlay.style.display = isLoading ? 'flex' : 'none';
    }

    function showAlert(msg, type) {
        if (!msg) {
            statusAlert.style.display = 'none';
            return;
        }
        statusAlert.textContent = msg;
        statusAlert.className = `alert alert-${type}`;
        statusAlert.style.display = 'block';
    }

    // Initial check on database records
    fetchDbRecords();
});
