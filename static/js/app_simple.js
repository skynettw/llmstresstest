// 全局變量
let currentTestId = null;
let progressInterval = null;
let testResults = [];

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
});

// 重新載入硬體資訊
function loadHardwareInfo() {
    fetch('/api/hardware')
        .then(response => response.json())
        .then(data => {
            displayHardwareInfo(data);
            addLog('硬體資訊已更新', 'success');
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
    
    // 系統資訊
    if (hardwareInfo.system) {
        const systemCard = createHardwareCard('系統', 'bi-pc-display', [
            `作業系統: ${hardwareInfo.system.system || 'N/A'} ${hardwareInfo.system.release || ''}`,
            `架構: ${hardwareInfo.system.machine || 'N/A'}`,
            `Python版本: ${hardwareInfo.system.python_version || 'N/A'}`,
            `開機時間: ${hardwareInfo.system.boot_time || 'N/A'}`
        ]);
        container.appendChild(systemCard);
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
    console.log('Setting up event listeners...');

    // 測試表單提交
    const form = document.getElementById('test-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            console.log('Form submit event triggered');
            e.preventDefault();
            startTest(e);
            return false;
        });
        console.log('Form submit listener added');
    } else {
        console.error('Form element not found');
    }

    // 開始測試按鈕
    const startBtn = document.getElementById('start-test-btn');
    if (startBtn) {
        startBtn.addEventListener('click', function(e) {
            console.log('Start button clicked');
            e.preventDefault();
            startTest(e);
            return false;
        });
        console.log('Start button listener added');
    } else {
        console.error('Start button element not found');
    }

    // 停止測試按鈕
    const stopBtn = document.getElementById('stop-test-btn');
    if (stopBtn) {
        stopBtn.addEventListener('click', function(e) {
            console.log('Stop button clicked');
            e.preventDefault();
            stopTest();
            return false;
        });
        console.log('Stop button listener added');
    } else {
        console.error('Stop button element not found');
    }

    console.log('Event listeners setup complete');
}

// 開始測試
function startTest(event) {
    console.log('startTest function called');

    // 防止表單提交導致頁面重新載入
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }

    const model = document.getElementById('model-select').value;
    const concurrentRequests = parseInt(document.getElementById('concurrent-requests').value);
    const totalRequests = parseInt(document.getElementById('total-requests').value);
    const prompt = document.getElementById('test-prompt').value;

    console.log('Form values:', { model, concurrentRequests, totalRequests, prompt });

    if (!model || !prompt) {
        alert('請填寫所有必要欄位');
        console.log('Validation failed: missing model or prompt');
        return false;
    }

    // 立即更新按鈕狀態
    disableStartButton();
    clearLogs();
    addLog('正在啟動測試...', 'info');
    showProgressContainer();

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
            addLog(`測試已開始 (ID: ${data.test_id})`, 'success');
            startProgressPolling();
        } else {
            addLog(`啟動測試失敗: ${data.error}`, 'error');
            enableStartButton(); // 恢復按鈕狀態
        }
    })
    .catch(error => {
        console.error('啟動測試失敗:', error);
        addLog('啟動測試失敗', 'error');
        enableStartButton(); // 恢復按鈕狀態
    });

    return false; // 防止表單提交
}

// 停止測試
function stopTest() {
    if (!currentTestId) {
        return;
    }

    // 更新停止按鈕狀態
    const stopBtn = document.getElementById('stop-test-btn');
    stopBtn.disabled = true;
    stopBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> 停止中...';

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
            // 恢復停止按鈕狀態
            stopBtn.disabled = false;
            stopBtn.innerHTML = '<i class="bi bi-stop-circle"></i> 停止測試';
        }
    })
    .catch(error => {
        console.error('停止測試失敗:', error);
        addLog('停止測試失敗', 'error');
        // 恢復停止按鈕狀態
        stopBtn.disabled = false;
        stopBtn.innerHTML = '<i class="bi bi-stop-circle"></i> 停止測試';
    });
}

// 開始進度輪詢
function startProgressPolling() {
    if (progressInterval) {
        clearInterval(progressInterval);
    }
    
    progressInterval = setInterval(() => {
        if (currentTestId) {
            checkTestProgress();
        }
    }, 1000); // 每秒檢查一次
}

// 停止進度輪詢
function stopProgressPolling() {
    if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
    }
}

// 檢查測試進度
function checkTestProgress() {
    fetch(`/api/test_status/${currentTestId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                addLog(`獲取測試狀態失敗: ${data.error}`, 'error');
                stopProgressPolling();
                enableStartButton();
                return;
            }
            
            updateProgress(data);
            
            if (data.status === 'completed') {
                addLog('測試完成！', 'success');
                updateTestStatus('已完成');
                if (data.statistics) {
                    showTestResults(data.statistics);
                }
                stopProgressPolling();
                enableStartButton();
            } else if (data.status === 'error') {
                addLog(`測試錯誤: ${data.error || '未知錯誤'}`, 'error');
                updateTestStatus('錯誤');
                stopProgressPolling();
                enableStartButton();
            } else if (data.status === 'stopped') {
                addLog('測試已停止', 'warning');
                updateTestStatus('已停止');
                stopProgressPolling();
                enableStartButton();
            }
        })
        .catch(error => {
            console.error('檢查測試進度失敗:', error);
            addLog('檢查測試進度失敗', 'error');
        });
}

// 更新進度
function updateProgress(data) {
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    const completedCount = document.getElementById('completed-count');
    const failedCount = document.getElementById('failed-count');
    
    const progress = data.progress || 0;
    progressBar.style.width = `${progress}%`;
    progressBar.setAttribute('aria-valuenow', progress);
    progressText.textContent = `${progress.toFixed(1)}%`;
    completedCount.textContent = data.completed_requests || 0;
    failedCount.textContent = data.failed_requests || 0;
    
    // 計算平均回應時間
    if (data.current_results && data.current_results.length > 0) {
        const successfulResults = data.current_results.filter(r => r.success);
        if (successfulResults.length > 0) {
            const avgTime = successfulResults.reduce((sum, r) => sum + r.response_time, 0) / successfulResults.length;
            document.getElementById('avg-response-time').textContent = `${avgTime.toFixed(2)}s`;
            
            // 計算每秒請求數
            const totalTime = successfulResults.reduce((sum, r) => sum + r.response_time, 0);
            const rps = totalTime > 0 ? successfulResults.length / totalTime : 0;
            document.getElementById('requests-per-second').textContent = rps.toFixed(2);
        }
    }
    
    // 更新狀態
    if (data.status) {
        updateTestStatus(getStatusDisplayName(data.status));
    }
}

// 獲取狀態顯示名稱
function getStatusDisplayName(status) {
    const statusMap = {
        'starting': '啟動中',
        'running': '運行中',
        'completed': '已完成',
        'error': '錯誤',
        'stopping': '停止中',
        'stopped': '已停止'
    };
    return statusMap[status] || status;
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
        <tr><td>總請求數</td><td>${statistics.total_requests || 0}</td></tr>
        <tr><td>成功請求數</td><td>${statistics.successful_requests || 0}</td></tr>
        <tr><td>失敗請求數</td><td>${statistics.failed_requests || 0}</td></tr>
        <tr><td>成功率</td><td>${(statistics.success_rate || 0).toFixed(2)}%</td></tr>
        <tr><td>最小回應時間</td><td>${statistics.response_time_stats?.min?.toFixed(2) || 'N/A'}s</td></tr>
        <tr><td>最大回應時間</td><td>${statistics.response_time_stats?.max?.toFixed(2) || 'N/A'}s</td></tr>
        <tr><td>平均回應時間</td><td>${statistics.response_time_stats?.mean?.toFixed(2) || 'N/A'}s</td></tr>
        <tr><td>中位數回應時間</td><td>${statistics.response_time_stats?.median?.toFixed(2) || 'N/A'}s</td></tr>
        <tr><td>標準差</td><td>${statistics.response_time_stats?.std_dev?.toFixed(2) || 'N/A'}s</td></tr>
        <tr><td>每秒請求數</td><td>${(statistics.requests_per_second || 0).toFixed(2)}</td></tr>
    `;

    // 載入圖表
    loadTestCharts();
}

// 更新測試狀態
function updateTestStatus(status) {
    const statusBadge = document.getElementById('test-status');
    statusBadge.textContent = status;
    
    // 根據狀態更改顏色
    statusBadge.className = 'badge status-badge ms-2';
    switch(status) {
        case '運行中':
        case '啟動中':
            statusBadge.classList.add('bg-primary');
            break;
        case '已完成':
            statusBadge.classList.add('bg-success');
            break;
        case '錯誤':
            statusBadge.classList.add('bg-danger');
            break;
        case '停止中':
        case '已停止':
            statusBadge.classList.add('bg-warning');
            break;
        default:
            statusBadge.classList.add('bg-secondary');
    }
}

// 啟用/禁用測試控制項
function disableStartButton() {
    const startBtn = document.getElementById('start-test-btn');
    const stopBtn = document.getElementById('stop-test-btn');

    // 禁用開始按鈕並更改文字
    startBtn.disabled = true;
    startBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> 測試中...';

    // 啟用停止按鈕
    stopBtn.disabled = false;

    // 禁用表單控制項，防止測試期間修改配置
    document.getElementById('model-select').disabled = true;
    document.getElementById('concurrent-requests').disabled = true;
    document.getElementById('total-requests').disabled = true;
    document.getElementById('test-prompt').disabled = true;
}

function enableStartButton() {
    const startBtn = document.getElementById('start-test-btn');
    const stopBtn = document.getElementById('stop-test-btn');

    // 恢復開始按鈕
    startBtn.disabled = false;
    startBtn.innerHTML = '<i class="bi bi-play-circle"></i> 開始測試';

    // 禁用停止按鈕並恢復文字
    stopBtn.disabled = true;
    stopBtn.innerHTML = '<i class="bi bi-stop-circle"></i> 停止測試';

    // 重新啟用表單控制項
    document.getElementById('model-select').disabled = false;
    document.getElementById('concurrent-requests').disabled = false;
    document.getElementById('total-requests').disabled = false;
    document.getElementById('test-prompt').disabled = false;

    currentTestId = null;
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

// 載入測試圖表
function loadTestCharts() {
    if (!currentTestId) {
        console.error('No current test ID available for charts');
        return;
    }

    addLog('正在載入圖表...', 'info');

    // 顯示載入指示器
    showChartLoadingIndicators();

    fetch(`/api/test_charts/${currentTestId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('載入圖表失敗:', data.error);
                addLog(`載入圖表失敗: ${data.error}`, 'error');
                showChartErrorMessage(data.error);
                return;
            }

            // 顯示圖表
            displayCharts(data);
            addLog('圖表載入完成', 'success');
        })
        .catch(error => {
            console.error('載入圖表失敗:', error);
            addLog('載入圖表失敗', 'error');
            showChartErrorMessage('載入圖表時發生錯誤');
        });
}

// 顯示圖表載入指示器
function showChartLoadingIndicators() {
    const chartIds = ['response-time-histogram', 'success-rate-pie', 'response-time-timeline', 'response-time-box'];

    chartIds.forEach(id => {
        const container = document.getElementById(id);
        if (container) {
            container.innerHTML = `
                <div class="chart-loading">
                    <div class="spinner-border text-primary me-2" role="status">
                        <span class="visually-hidden">載入中...</span>
                    </div>
                    載入圖表中...
                </div>
            `;
        }
    });
}

// 顯示圖表錯誤訊息
function showChartErrorMessage(message) {
    const chartIds = ['response-time-histogram', 'success-rate-pie', 'response-time-timeline', 'response-time-box'];

    chartIds.forEach(id => {
        const container = document.getElementById(id);
        if (container) {
            container.innerHTML = `
                <div class="chart-loading text-danger">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    ${message}
                </div>
            `;
        }
    });
}

// 顯示圖表
function displayCharts(chartsData) {
    console.log('Displaying charts:', chartsData);

    // 回應時間分布直方圖
    if (chartsData.response_time_histogram) {
        try {
            const histogramData = JSON.parse(chartsData.response_time_histogram);
            Plotly.newPlot('response-time-histogram', histogramData.data, histogramData.layout, {
                responsive: true,
                displayModeBar: true,
                modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
            });
        } catch (error) {
            console.error('Error displaying histogram:', error);
        }
    }

    // 成功率餅圖
    if (chartsData.success_rate_pie) {
        try {
            const pieData = JSON.parse(chartsData.success_rate_pie);
            Plotly.newPlot('success-rate-pie', pieData.data, pieData.layout, {
                responsive: true,
                displayModeBar: true,
                modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
            });
        } catch (error) {
            console.error('Error displaying pie chart:', error);
        }
    }

    // 回應時間趨勢圖
    if (chartsData.response_time_timeline) {
        try {
            const timelineData = JSON.parse(chartsData.response_time_timeline);
            Plotly.newPlot('response-time-timeline', timelineData.data, timelineData.layout, {
                responsive: true,
                displayModeBar: true,
                modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
            });
        } catch (error) {
            console.error('Error displaying timeline:', error);
        }
    }

    // 回應時間統計箱線圖
    if (chartsData.response_time_box) {
        try {
            const boxData = JSON.parse(chartsData.response_time_box);
            Plotly.newPlot('response-time-box', boxData.data, boxData.layout, {
                responsive: true,
                displayModeBar: true,
                modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
            });
        } catch (error) {
            console.error('Error displaying box plot:', error);
        }
    }
}
