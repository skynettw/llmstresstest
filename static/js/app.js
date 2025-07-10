// 全局變量
let currentTestId = null;
let progressInterval = null;
let testResults = [];

// 載入硬體資訊
function loadHardwareInfo() {
    fetch('/api/hardware')
        .then(response => response.json())
        .then(data => {
            displayHardwareInfo(data);
        })
        .catch(error => {
            console.error('載入硬體資訊失敗:', error);
            addLog('載入硬體資訊失敗', 'error');
        });
}

// 顯示硬體資訊
function displayHardwareInfo(hardwareInfo) {
    const container = document.getElementById('hardware-info');
    container.innerHTML = '';
    
    // CPU資訊
    if (hardwareInfo.cpu) {
        const cpuCard = createHardwareCard('CPU', 'bi-cpu', [
            `處理器: ${hardwareInfo.cpu.name || 'N/A'}`,
            `物理核心: ${hardwareInfo.cpu.cores_physical || 'N/A'}`,
            `邏輯核心: ${hardwareInfo.cpu.cores_logical || 'N/A'}`,
            `使用率: ${hardwareInfo.cpu.usage_percent || 'N/A'}%`
        ]);
        container.appendChild(cpuCard);
    }
    
    // 記憶體資訊
    if (hardwareInfo.memory) {
        const memoryCard = createHardwareCard('記憶體', 'bi-memory', [
            `總容量: ${hardwareInfo.memory.total_gb || 'N/A'} GB`,
            `可用: ${hardwareInfo.memory.available_gb || 'N/A'} GB`,
            `已使用: ${hardwareInfo.memory.used_gb || 'N/A'} GB`,
            `使用率: ${hardwareInfo.memory.usage_percent || 'N/A'}%`
        ]);
        container.appendChild(memoryCard);
    }
    
    // GPU資訊
    if (hardwareInfo.gpu && Array.isArray(hardwareInfo.gpu)) {
        hardwareInfo.gpu.forEach((gpu, index) => {
            const gpuCard = createHardwareCard(`GPU ${index + 1}`, 'bi-gpu-card', [
                `名稱: ${gpu.name || 'N/A'}`,
                `記憶體總量: ${gpu.memory_total_mb || 'N/A'} MB`,
                `記憶體使用: ${gpu.memory_used_mb || 'N/A'} MB`,
                `GPU使用率: ${gpu.gpu_usage_percent || 'N/A'}%`
            ]);
            container.appendChild(gpuCard);
        });
    } else if (hardwareInfo.gpu && hardwareInfo.gpu.message) {
        const gpuCard = createHardwareCard('GPU', 'bi-gpu-card', [hardwareInfo.gpu.message]);
        container.appendChild(gpuCard);
    }
    
    // 磁碟資訊
    if (hardwareInfo.disk && Array.isArray(hardwareInfo.disk)) {
        hardwareInfo.disk.forEach((disk, index) => {
            const diskCard = createHardwareCard(`磁碟 ${disk.device}`, 'bi-hdd', [
                `檔案系統: ${disk.file_system || 'N/A'}`,
                `總容量: ${disk.total_gb || 'N/A'} GB`,
                `可用: ${disk.free_gb || 'N/A'} GB`,
                `使用率: ${disk.usage_percent || 'N/A'}%`
            ]);
            container.appendChild(diskCard);
        });
    }
}

// 創建硬體資訊卡片
function createHardwareCard(title, icon, items) {
    const col = document.createElement('div');
    col.className = 'col-md-6 col-lg-4 mb-3';
    
    col.innerHTML = `
        <div class="card hardware-card h-100">
            <div class="card-body">
                <h5 class="card-title">
                    <i class="bi ${icon}"></i> ${title}
                </h5>
                <ul class="list-unstyled mb-0">
                    ${items.map(item => `<li><small>${item}</small></li>`).join('')}
                </ul>
            </div>
        </div>
    `;
    
    return col;
}

// 設置事件監聽器
function setupEventListeners() {
    // 測試表單提交
    document.getElementById('test-form').addEventListener('submit', function(e) {
        e.preventDefault();
        startTest();
    });
    
    // 停止測試按鈕
    document.getElementById('stop-test-btn').addEventListener('click', function() {
        stopTest();
    });
}

// 開始測試
function startTest() {
    const model = document.getElementById('model-select').value;
    const concurrentRequests = parseInt(document.getElementById('concurrent-requests').value);
    const totalRequests = parseInt(document.getElementById('total-requests').value);
    const prompt = document.getElementById('test-prompt').value;
    
    if (!model || !prompt) {
        alert('請填寫所有必要欄位');
        return;
    }
    
    const testConfig = {
        model: model,
        concurrent_requests: concurrentRequests,
        total_requests: totalRequests,
        prompt: prompt
    };
    
    fetch('/api/start_test', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(testConfig)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            currentTestId = data.test_id;
            disableStartButton();
            clearLogs();
            addLog('正在啟動測試...', 'info');
        } else {
            addLog(`啟動測試失敗: ${data.error}`, 'error');
        }
    })
    .catch(error => {
        console.error('啟動測試失敗:', error);
        addLog('啟動測試失敗', 'error');
    });
}

// 停止測試
function stopTest() {
    if (!currentTestId) {
        return;
    }
    
    fetch('/api/stop_test', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({test_id: currentTestId})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            addLog('正在停止測試...', 'warning');
            updateTestStatus('停止中');
        } else {
            addLog(`停止測試失敗: ${data.message}`, 'error');
        }
    })
    .catch(error => {
        console.error('停止測試失敗:', error);
        addLog('停止測試失敗', 'error');
    });
}

// 更新進度
function updateProgress(data) {
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    const completedCount = document.getElementById('completed-count');
    const failedCount = document.getElementById('failed-count');
    
    progressBar.style.width = `${data.progress}%`;
    progressBar.setAttribute('aria-valuenow', data.progress);
    progressText.textContent = `${data.progress.toFixed(1)}%`;
    completedCount.textContent = data.completed;
    failedCount.textContent = data.failed;
    
    // 計算平均回應時間
    if (data.latest_result && data.latest_result.success) {
        testResults.push(data.latest_result);
        const avgTime = testResults.reduce((sum, r) => sum + r.response_time, 0) / testResults.length;
        document.getElementById('avg-response-time').textContent = `${avgTime.toFixed(2)}s`;
        
        // 計算每秒請求數
        const rps = testResults.length / testResults.reduce((sum, r) => sum + r.response_time, 0);
        document.getElementById('requests-per-second').textContent = rps.toFixed(2);
    }
}

// 顯示進度容器
function showProgressContainer() {
    document.getElementById('progress-container').style.display = 'block';
    testResults = [];
}

// 顯示測試結果
function showTestResults(statistics) {
    document.getElementById('test-results').style.display = 'block';
    
    // 填充統計表格
    const tableBody = document.getElementById('statistics-table');
    tableBody.innerHTML = `
        <tr><td>總請求數</td><td>${statistics.total_requests}</td></tr>
        <tr><td>成功請求數</td><td>${statistics.successful_requests}</td></tr>
        <tr><td>失敗請求數</td><td>${statistics.failed_requests}</td></tr>
        <tr><td>成功率</td><td>${statistics.success_rate.toFixed(2)}%</td></tr>
        <tr><td>最小回應時間</td><td>${statistics.response_time_stats.min?.toFixed(2) || 'N/A'}s</td></tr>
        <tr><td>最大回應時間</td><td>${statistics.response_time_stats.max?.toFixed(2) || 'N/A'}s</td></tr>
        <tr><td>平均回應時間</td><td>${statistics.response_time_stats.mean?.toFixed(2) || 'N/A'}s</td></tr>
        <tr><td>中位數回應時間</td><td>${statistics.response_time_stats.median?.toFixed(2) || 'N/A'}s</td></tr>
        <tr><td>每秒請求數</td><td>${statistics.requests_per_second?.toFixed(2) || 'N/A'}</td></tr>
    `;
}

// 更新測試狀態
function updateTestStatus(status) {
    const statusBadge = document.getElementById('test-status');
    statusBadge.textContent = status;
    
    // 根據狀態更改顏色
    statusBadge.className = 'badge status-badge ms-2';
    switch(status) {
        case '運行中':
            statusBadge.classList.add('bg-primary');
            break;
        case '已完成':
            statusBadge.classList.add('bg-success');
            break;
        case '錯誤':
            statusBadge.classList.add('bg-danger');
            break;
        case '停止中':
            statusBadge.classList.add('bg-warning');
            break;
        default:
            statusBadge.classList.add('bg-secondary');
    }
}

// 啟用/禁用開始按鈕
function disableStartButton() {
    document.getElementById('start-test-btn').disabled = true;
    document.getElementById('stop-test-btn').disabled = false;
}

function enableStartButton() {
    document.getElementById('start-test-btn').disabled = false;
    document.getElementById('stop-test-btn').disabled = true;
}

// 日誌功能
function addLog(message, type = 'info') {
    const logContainer = document.getElementById('log-container');
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = document.createElement('div');
    
    let className = '';
    switch(type) {
        case 'success':
            className = 'text-success';
            break;
        case 'error':
            className = 'text-danger';
            break;
        case 'warning':
            className = 'text-warning';
            break;
        case 'info':
        default:
            className = 'text-info';
    }
    
    logEntry.innerHTML = `<span class="text-muted">[${timestamp}]</span> <span class="${className}">${message}</span>`;
    logContainer.appendChild(logEntry);
    logContainer.scrollTop = logContainer.scrollHeight;
}

function clearLogs() {
    document.getElementById('log-container').innerHTML = '';
}

// 重新整理功能
function refreshHardwareInfo() {
    addLog('正在重新載入硬體資訊...', 'info');
    loadHardwareInfo();
}

function refreshModels() {
    addLog('正在重新載入模型列表...', 'info');
    fetch('/api/models')
        .then(response => response.json())
        .then(models => {
            const select = document.getElementById('model-select');
            select.innerHTML = '<option value="">請選擇模型...</option>';
            models.forEach(model => {
                const option = document.createElement('option');
                option.value = model.name;
                option.textContent = model.name;
                select.appendChild(option);
            });
            addLog(`已載入 ${models.length} 個模型`, 'success');
        })
        .catch(error => {
            console.error('載入模型失敗:', error);
            addLog('載入模型失敗', 'error');
        });
}
