// women_strategy/script.js
document.addEventListener('DOMContentLoaded', function() {
    // 初始化頁面
    initPage();
    
    // 添加事件監聽器
    addEventListeners();
    
    // 模擬實時更新
    startRealTimeUpdates();
});

// 初始化頁面
function initPage() {
    updateStatistics();
    checkForNewSignals();
}

// 添加事件監聽器
function addEventListeners() {
    // 清空警報按鈕
    const clearBtn = document.querySelector('.btn-secondary');
    if (clearBtn) {
        clearBtn.addEventListener('click', clearSignals);
    }
    
    // 為每個信號卡片添加點擊事件
    const signalCards = document.querySelectorAll('.signal-card');
    signalCards.forEach(card => {
        card.addEventListener('click', function() {
            showSignalDetail(this);
        });
    });
}

// 清空所有信號
function clearSignals() {
    const signalsContainer = document.getElementById('signals-container');
    if (signalsContainer) {
        signalsContainer.innerHTML = '<p class="text-center py-8 text-gray-500">沒有活躍的信號</p>';
        
        // 顯示清空成功的通知
        showNotification('所有信號已清空', 'success');
    }
}

// 更新統計數據
function updateStatistics() {
    // 這裡可以加入AJAX請求獲取最新統計數據
    console.log('正在更新統計數據...');
    
    // 模擬統計數據更新
    setTimeout(() => {
        const lastUpdateElem = document.querySelector('.stat-card + p.text-sm.text-gray-400');
        if (lastUpdateElem) {
            const now = new Date();
            const formattedDate = `${now.getFullYear()}/${now.getMonth() + 1}/${now.getDate()} ${formatTime(now)}`;
            lastUpdateElem.textContent = `最後更新時間：${formattedDate}`;
        }
    }, 5000);
}

// 檢查是否有新信號
function checkForNewSignals() {
    // 這裡可以加入AJAX請求獲取最新信號
    console.log('正在檢查新信號...');
    
    // 模擬偶爾出現新信號
    if (Math.random() > 0.7) {
        setTimeout(() => {
            addNewSignal();
        }, 10000);
    }
}

// 添加新信號
function addNewSignal() {
    const signalsContainer = document.getElementById('signals-container');
    if (!signalsContainer) return;
    
    // 創建新的信號卡片
    const newSignal = document.createElement('div');
    newSignal.className = 'signal-card';
    
    // 獲取當前時間
    const now = new Date();
    const formattedDate = `${now.getFullYear()}/${now.getMonth() + 1}/${now.getDate()}`;
    const formattedTime = formatTime(now);
    
    // 隨機選擇幣種
    const coins = ['BTC-USDT', 'ETH-USDT', 'SOL-USDT', 'DOGE-USDT', 'SHIB-USDT', 'ADA-USDT', 'XRP-USDT'];
    const randomCoin = coins[Math.floor(Math.random() * coins.length)];
    
    // 設置信號卡片內容
    newSignal.innerHTML = `
        <div class="flex items-start justify-between mb-3">
            <div>
                <h3 class="signal-header text-lg mb-1">🚨 交易輔助推薦信號 📈</h3>
                <div class="grid grid-cols-2 gap-2 mb-2">
                    <div>
                        <span class="text-gray-400">📅 日期:</span> ${formattedDate}
                    </div>
                    <div>
                        <span class="text-gray-400">⏰ 時間:</span> ${formattedTime}
                    </div>
                    <div>
                        <span class="text-gray-400">💱 幣種:</span> ${randomCoin}
                    </div>
                    <div>
                        <span class="text-gray-400">⏳ 時區:</span> 4h
                    </div>
                </div>
            </div>
            <span class="signal-time">${formattedTime}</span>
        </div>
        <div class="bg-gray-800 p-3 rounded my-3">
            <h4 class="font-semibold text-red-400 mb-2">重要風險警告:</h4>
            <p class="text-sm text-gray-300 mb-2">【風險提示】</p>
            <ul class="text-sm text-gray-300 list-disc pl-5 space-y-1">
                <li>本分析僅供參考，不構成任何投資建議或擔保</li>
                <li>加密貨幣市場波動劇烈，可能導致資金完全損失</li>
                <li>進行任何交易前，請確保您已充分了解相關風險</li>
                <li>交易決策完全由用戶自行負責，平台不承擔任何交易損失責任</li>
                <li>使用槓桿交易將顯著增加風險，不建議新手使用高槓桿</li>
            </ul>
        </div>
        <div class="text-sm text-gray-400">
            <p>⚠️ 系統說明</p>
            <p>此訊號透過每2小時自動掃描產生，UTC時間00, 02, 04, 06, 08, 10, 12, 14, 16, 18, 20, 22點掃描。</p>
        </div>
    `;
    
    // 添加點擊事件
    newSignal.addEventListener('click', function() {
        showSignalDetail(this);
    });
    
    // 插入到容器頂部
    const firstSignal = signalsContainer.firstChild;
    signalsContainer.insertBefore(newSignal, firstSignal);
    
    // 顯示新信號通知
    showNotification(`新的交易信號: ${randomCoin}`, 'info');
    
    // 添加動畫效果
    newSignal.style.opacity = '0';
    newSignal.style.transform = 'translateY(-20px)';
    newSignal.style.transition = 'opacity 0.5s, transform 0.5s';
    
    setTimeout(() => {
        newSignal.style.opacity = '1';
        newSignal.style.transform = 'translateY(0)';
    }, 100);
}

// 顯示信號詳情
function showSignalDetail(signalCard) {
    // 獲取幣種
    const coinElem = signalCard.querySelector('div:nth-child(1) div:nth-child(3) span:nth-child(2)');
    const coin = coinElem ? coinElem.textContent.trim() : '未知幣種';
    
    // 創建模態對話框
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-75';
    modal.innerHTML = `
        <div class="bg-gray-900 rounded-lg w-full max-w-2xl mx-4 overflow-hidden">
            <div class="bg-gradient-to-r from-amber-600 to-amber-800 px-4 py-3 flex justify-between items-center">
                <h2 class="text-xl font-bold">${coin} 詳細分析</h2>
                <button id="close-modal" class="text-white hover:text-gray-300">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
            <div class="p-4">
                <div class="mb-4 pb-4 border-b border-gray-700">
                    <h3 class="text-lg font-semibold mb-2">市場概況</h3>
                    <p class="text-gray-300">目前${coin}處於${Math.random() > 0.5 ? '上升' : '下降'}趨勢，近期交易量${Math.random() > 0.5 ? '增加' : '穩定'}，市場情緒指標為${Math.random() > 0.7 ? '極度恐懼' : Math.random() > 0.4 ? '恐懼' : '中性'}。</p>
                </div>
                <div class="mb-4 pb-4 border-b border-gray-700">
                    <h3 class="text-lg font-semibold mb-2">技術分析</h3>
                    <p class="text-gray-300">MACD顯示${Math.random() > 0.5 ? '多頭' : '空頭'}信號，RSI當前值為${Math.floor(Math.random() * 100)}，${Math.random() > 0.7 ? '已經超買' : Math.random() > 0.3 ? '接近超買' : '處於中性區間'}。</p>
                </div>
                <div class="mb-4 pb-4 border-b border-gray-700">
                    <h3 class="text-lg font-semibold mb-2">鏈上數據</h3>
                    <p class="text-gray-300">大額持有者近期${Math.random() > 0.5 ? '增加' : '減少'}持倉，鏈上活躍地址數${Math.random() > 0.5 ? '上升' : '下降'}，交易所流入資金${Math.random() > 0.5 ? '增加' : '減少'}。</p>
                </div>
                <div class="flex justify-end mt-6">
                    <button class="btn-primary">匯出分析報告</button>
                </div>
            </div>
        </div>
    `;
    
    // 添加到頁面
    document.body.appendChild(modal);
    
    // 點擊關閉按鈕
    document.getElementById('close-modal').addEventListener('click', function() {
        document.body.removeChild(modal);
    });
    
    // 點擊背景關閉模態框
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            document.body.removeChild(modal);
        }
    });
}

// 顯示通知
function showNotification(message, type = 'info') {
    // 創建通知元素
    const notification = document.createElement('div');
    notification.className = `fixed bottom-4 right-4 px-4 py-2 rounded-lg text-white z-50 ${type === 'success' ? 'bg-green-600' : type === 'error' ? 'bg-red-600' : 'bg-blue-600'}`;
    notification.textContent = message;
    
    // 添加到頁面
    document.body.appendChild(notification);
    
    // 設置自動消失
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateY(20px)';
        notification.style.transition = 'opacity 0.5s, transform 0.5s';
        
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 500);
    }, 3000);
}

// 啟動實時更新
function startRealTimeUpdates() {
    // 每隔一段時間檢查新信號
    setInterval(() => {
        checkForNewSignals();
    }, 30000);
    
    // 每隔一段時間更新統計數據
    setInterval(() => {
        updateStatistics();
    }, 300000);
}

// 格式化時間
function formatTime(date) {
    const hours = date.getHours();
    const minutes = date.getMinutes();
    const seconds = date.getSeconds();
    const ampm = hours >= 12 ? '下午' : '上午';
    const formattedHours = hours % 12 || 12;
    
    return `${ampm}${formattedHours}:${minutes < 10 ? '0' + minutes : minutes}:${seconds < 10 ? '0' + seconds : seconds}`;
}

// 模擬交易信號數據
const mockSignals = [
    {
        id: 'signal-001',
        coin: 'BTC-USDT',
        type: 'buy',
        price: 65842.32,
        timestamp: new Date('2024-04-25T08:30:00'),
        timeframe: '4H',
        status: 'active',
        profit: 12.5,
        confidence: 87,
        analysis: '比特幣在近期經歷連續上漲後出現強勁支撐位，突破關鍵阻力位顯示多頭趨勢延續的可能性很高。鏈上數據顯示大戶持續積累，市場情緒轉向偏多。',
        targets: [
            { level: 1, price: 67200, reached: true },
            { level: 2, price: 68500, reached: false },
            { level: 3, price: 70000, reached: false }
        ],
        stopLoss: 63800
    },
    {
        id: 'signal-002',
        coin: 'ETH-USDT',
        type: 'buy',
        price: 3128.75,
        timestamp: new Date('2024-04-25T06:15:00'),
        timeframe: '4H',
        status: 'active',
        profit: 8.2,
        confidence: 82,
        analysis: '以太坊在近期表現強勁，技術指標顯示上漲動能持續。上海升級後質押解鎖並未造成顯著賣壓，相反更多資金參與質押。圖表形態呈現突破三角形整理區間，暗示更高目標價。',
        targets: [
            { level: 1, price: 3250, reached: false },
            { level: 2, price: 3400, reached: false },
            { level: 3, price: 3600, reached: false }
        ],
        stopLoss: 2950
    },
    {
        id: 'signal-003',
        coin: 'SOL-USDT',
        type: 'buy',
        price: 142.68,
        timestamp: new Date('2024-04-24T22:45:00'),
        timeframe: '8H',
        status: 'active',
        profit: 15.3,
        confidence: 85,
        analysis: 'Solana生態系持續強勁發展，連續交易量增加，鏈上活動顯著提升。在近期整體市場調整中表現出相對強勢，顯示買盤力量十足。突破關鍵阻力位後動能加速，預期短期內將測試更高價位。',
        targets: [
            { level: 1, price: 150, reached: true },
            { level: 2, price: 160, reached: false },
            { level: 3, price: 175, reached: false }
        ],
        stopLoss: 132
    },
    {
        id: 'signal-004',
        coin: 'MEME-USDT',
        type: 'buy',
        price: 0.03245,
        timestamp: new Date('2024-04-24T18:20:00'),
        timeframe: '4H',
        status: 'completed',
        profit: 32.7,
        confidence: 78,
        analysis: 'MEME幣種在社交媒體關注度顯著提升，鯨魚錢包大量積累。市場流動性良好，技術突破關鍵阻力位，短期內有望測試歷史高點區域。社區活動升溫，可能促使價格短期內大幅上漲。',
        targets: [
            { level: 1, price: 0.035, reached: true },
            { level: 2, price: 0.040, reached: true },
            { level: 3, price: 0.045, reached: false }
        ],
        stopLoss: 0.029
    },
    {
        id: 'signal-005',
        coin: 'TIA-USDT',
        type: 'buy',
        price: 15.82,
        timestamp: new Date('2024-04-24T14:10:00'),
        timeframe: '8H',
        status: 'completed',
        profit: 18.9,
        confidence: 83,
        analysis: 'Celestia正吸引越來越多的開發者和用戶，鏈上數據顯示活躍度持續攀升。技術分析顯示突破重要阻力位後持續走高，市場情緒轉為強烈看多。項目基本面保持強勁，未來發展前景良好。',
        targets: [
            { level: 1, price: 16.5, reached: true },
            { level: 2, price: 17.2, reached: true },
            { level: 3, price: 18.0, reached: false }
        ],
        stopLoss: 14.9
    }
];

// DOM元素
const signalsContainer = document.getElementById('signals-container');
const clearSignalsBtn = document.getElementById('clear-signals');
const modal = document.getElementById('signal-modal');
const modalTitle = document.getElementById('modal-title');
const modalContent = document.getElementById('modal-content');
const closeModalBtn = document.getElementById('close-modal');
const modalBackdrop = document.getElementById('modal-backdrop');
const notificationContainer = document.getElementById('notification-container');

// 格式化時間函數
function formatDateTime(date) {
    const options = { 
        month: 'numeric', 
        day: 'numeric',
        hour: '2-digit', 
        minute: '2-digit'
    };
    return new Date(date).toLocaleDateString('zh-TW', options);
}

// 時間差異顯示函數
function timeAgo(date) {
    const seconds = Math.floor((new Date() - new Date(date)) / 1000);
    
    let interval = Math.floor(seconds / 31536000);
    if (interval >= 1) {
        return `${interval}年前`;
    }
    
    interval = Math.floor(seconds / 2592000);
    if (interval >= 1) {
        return `${interval}個月前`;
    }
    
    interval = Math.floor(seconds / 86400);
    if (interval >= 1) {
        return `${interval}天前`;
    }
    
    interval = Math.floor(seconds / 3600);
    if (interval >= 1) {
        return `${interval}小時前`;
    }
    
    interval = Math.floor(seconds / 60);
    if (interval >= 1) {
        return `${interval}分鐘前`;
    }
    
    return `${Math.floor(seconds)}秒前`;
}

// 創建信號卡片
function createSignalCard(signal) {
    const card = document.createElement('div');
    card.className = 'signal-card';
    card.dataset.signalId = signal.id;
    
    const statusClass = signal.status === 'active' ? 'text-green-500' : 'text-gray-400';
    const typeClass = signal.type === 'buy' ? 'text-green-500' : 'text-red-500';
    const typeIcon = signal.type === 'buy' ? '📈' : '📉';
    
    card.innerHTML = `
        <div class="flex items-center justify-between mb-2">
            <div class="flex items-center">
                <span class="text-xl mr-2">${typeIcon}</span>
                <div>
                    <h3 class="font-bold ${typeClass}">${signal.coin}</h3>
                    <span class="text-xs ${statusClass}">
                        ${signal.status === 'active' ? '● 活躍中' : '✓ 已完成'}
                    </span>
                </div>
            </div>
            <div class="text-right">
                <div class="text-sm opacity-70">${formatDateTime(signal.timestamp)}</div>
                <div class="text-xs opacity-50">${timeAgo(signal.timestamp)}</div>
            </div>
        </div>
        
        <div class="grid grid-cols-2 gap-4 mb-4 text-sm">
            <div>
                <div class="text-gray-400">入場價</div>
                <div class="font-medium">${signal.price.toLocaleString()}</div>
            </div>
            <div>
                <div class="text-gray-400">時間週期</div>
                <div class="font-medium">${signal.timeframe}</div>
            </div>
            <div>
                <div class="text-gray-400">目前收益</div>
                <div class="font-medium text-green-500">+${signal.profit}%</div>
            </div>
            <div>
                <div class="text-gray-400">信心指數</div>
                <div class="font-medium text-amber-500">${signal.confidence}%</div>
            </div>
        </div>
        
        <div class="flex justify-between items-center">
            <div class="text-xs opacity-70">目標價: ${signal.targets[0].price.toLocaleString()} → ${signal.targets[1].price.toLocaleString()} → ${signal.targets[2].price.toLocaleString()}</div>
            <button class="view-details-btn text-xs px-3 py-1 rounded bg-gray-800 hover:bg-gray-700 transition-colors">
                查看詳情
            </button>
        </div>
    `;
    
    // 添加卡片點擊事件
    card.querySelector('.view-details-btn').addEventListener('click', () => {
        showSignalDetails(signal);
    });
    
    return card;
}

// 顯示信號詳情
function showSignalDetails(signal) {
    modalTitle.textContent = `${signal.coin} 信號詳情`;
    
    const typeClass = signal.type === 'buy' ? 'text-green-500' : 'text-red-500';
    const typeText = signal.type === 'buy' ? '買入信號' : '賣出信號';
    const typeIcon = signal.type === 'buy' ? '📈' : '📉';
    
    modalContent.innerHTML = `
        <div class="flex items-center space-x-2 mb-4">
            <span class="text-lg ${typeClass} font-bold">${typeIcon} ${typeText}</span>
            <span class="text-xs px-2 py-1 rounded-full bg-gray-800">${signal.timeframe}</span>
            <span class="text-xs opacity-70">${formatDateTime(signal.timestamp)}</span>
        </div>
        
        <div class="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
            <div class="bg-gray-800 p-3 rounded">
                <div class="text-sm text-gray-400">入場價</div>
                <div class="font-bold">${signal.price.toLocaleString()}</div>
            </div>
            <div class="bg-gray-800 p-3 rounded">
                <div class="text-sm text-gray-400">止損位</div>
                <div class="font-bold text-red-500">${signal.stopLoss.toLocaleString()}</div>
            </div>
            <div class="bg-gray-800 p-3 rounded">
                <div class="text-sm text-gray-400">當前收益</div>
                <div class="font-bold text-green-500">+${signal.profit}%</div>
            </div>
            <div class="bg-gray-800 p-3 rounded">
                <div class="text-sm text-gray-400">信心指數</div>
                <div class="font-bold text-amber-500">${signal.confidence}%</div>
            </div>
            <div class="bg-gray-800 p-3 rounded">
                <div class="text-sm text-gray-400">當前狀態</div>
                <div class="font-bold ${signal.status === 'active' ? 'text-green-500' : 'text-gray-400'}">
                    ${signal.status === 'active' ? '活躍中' : '已完成'}
                </div>
            </div>
        </div>
        
        <div class="mb-6">
            <h4 class="font-semibold text-amber-500 mb-2">目標價位</h4>
            <div class="space-y-3">
                ${signal.targets.map((target, index) => `
                    <div class="flex items-center">
                        <div class="w-8 h-8 rounded-full ${target.reached ? 'bg-green-900 text-green-400' : 'bg-gray-800 text-gray-400'} flex items-center justify-center mr-3">
                            ${index + 1}
                        </div>
                        <div class="flex-1">
                            <div class="h-2 bg-gray-800 rounded-full">
                                <div class="h-2 rounded-full ${target.reached ? 'bg-gradient-to-r from-green-600 to-green-400' : 'bg-gray-700'}" style="width: ${target.reached ? '100' : '30'}%"></div>
                            </div>
                        </div>
                        <div class="ml-3 font-medium ${target.reached ? 'text-green-500' : 'text-gray-400'}">
                            ${target.price.toLocaleString()}
                            ${target.reached ? '<i class="fas fa-check ml-1"></i>' : ''}
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
        
        <div class="mb-6">
            <h4 class="font-semibold text-amber-500 mb-2">市場分析</h4>
            <p class="bg-gray-800 p-4 rounded text-gray-300 leading-relaxed">${signal.analysis}</p>
        </div>
        
        <div class="bg-gray-800 p-4 rounded mb-4">
            <h4 class="font-semibold text-red-400 mb-2">風險警告</h4>
            <ul class="text-sm text-gray-300 list-disc pl-5 space-y-1">
                <li>本分析僅供參考，不構成任何投資建議或擔保</li>
                <li>加密貨幣市場波動劇烈，可能導致資金完全損失</li>
                <li>進行任何交易前，請確保您已充分了解相關風險</li>
                <li>請嚴格遵守止損位設置，控制風險</li>
            </ul>
        </div>
        
        <div class="flex justify-end">
            <button id="close-detail-btn" class="btn-secondary">關閉</button>
        </div>
    `;
    
    document.getElementById('close-detail-btn').addEventListener('click', hideModal);
    
    modal.classList.remove('hidden');
}

// 隱藏模態框
function hideModal() {
    modal.classList.add('hidden');
}

// 顯示通知
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    
    let bgColor, textColor, icon;
    switch(type) {
        case 'success':
            bgColor = 'bg-green-900 border-green-700';
            textColor = 'text-green-300';
            icon = '<i class="fas fa-check-circle mr-2"></i>';
            break;
        case 'warning':
            bgColor = 'bg-amber-900 border-amber-700';
            textColor = 'text-amber-300';
            icon = '<i class="fas fa-exclamation-triangle mr-2"></i>';
            break;
        case 'error':
            bgColor = 'bg-red-900 border-red-700';
            textColor = 'text-red-300';
            icon = '<i class="fas fa-times-circle mr-2"></i>';
            break;
        default:
            bgColor = 'bg-blue-900 border-blue-700';
            textColor = 'text-blue-300';
            icon = '<i class="fas fa-info-circle mr-2"></i>';
    }
    
    notification.className = `p-4 rounded-lg shadow-lg border ${bgColor} ${textColor} max-w-sm transform transition-all duration-300 translate-x-full opacity-0`;
    notification.innerHTML = `
        <div class="flex items-center">
            ${icon}
            <div>${message}</div>
        </div>
    `;
    
    notificationContainer.appendChild(notification);
    
    // 動畫顯示通知
    setTimeout(() => {
        notification.classList.remove('translate-x-full', 'opacity-0');
    }, 10);
    
    // 自動移除通知
    setTimeout(() => {
        notification.classList.add('translate-x-full', 'opacity-0');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 4000);
}

// 加載信號
function loadSignals() {
    signalsContainer.innerHTML = '';
    
    if (mockSignals.length === 0) {
        signalsContainer.innerHTML = '<p class="text-center py-8 text-gray-500">沒有活躍的信號</p>';
        return;
    }
    
    // 按時間排序信號，最新的在前面
    const sortedSignals = [...mockSignals].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    
    sortedSignals.forEach(signal => {
        signalsContainer.appendChild(createSignalCard(signal));
    });
}

// 清除信號
function clearSignals() {
    const isConfirmed = confirm('確定要清除所有信號嗎？');
    if (isConfirmed) {
        signalsContainer.innerHTML = '<p class="text-center py-8 text-gray-500">沒有活躍的信號</p>';
        showNotification('所有信號已清除', 'success');
    }
}

// 初始化
function init() {
    // 加載信號
    loadSignals();
    
    // 清除按鈕事件
    clearSignalsBtn.addEventListener('click', clearSignals);
    
    // 關閉模態框事件
    closeModalBtn.addEventListener('click', hideModal);
    modalBackdrop.addEventListener('click', hideModal);
    
    // 模擬新信號到達
    setTimeout(() => {
        const newSignal = {
            id: 'signal-006',
            coin: 'APE-USDT',
            type: 'buy',
            price: 1.47,
            timestamp: new Date(),
            timeframe: '4H',
            status: 'active',
            profit: 0,
            confidence: 81,
            analysis: 'ApeCoin近期表現活躍，技術面突破長期下降趨勢線，成交量增加顯示買盤信心增強。社交媒體熱度上升，機構投資者開始關注。',
            targets: [
                { level: 1, price: 1.55, reached: false },
                { level: 2, price: 1.70, reached: false },
                { level: 3, price: 1.85, reached: false }
            ],
            stopLoss: 1.32
        };
        
        mockSignals.unshift(newSignal);
        loadSignals();
        
        showNotification('新交易信號: APE-USDT 買入信號', 'warning');
        
        // 播放通知聲音
        const audio = new Audio('https://assets.mixkit.co/sfx/preview/mixkit-interface-hint-notification-911.mp3');
        audio.play();
    }, 30000);
}

// 頁面加載完成後執行初始化
document.addEventListener('DOMContentLoaded', init); 