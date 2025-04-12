// DOM 元素
document.addEventListener('DOMContentLoaded', () => {
    // 模態框相關元素
    const modal = document.getElementById('signal-modal');
    const closeModalBtn = document.querySelector('.close-modal');
    const modalTriggers = document.querySelectorAll('.view-details');
    
    // 過濾按鈕
    const filterButtons = document.querySelectorAll('.filter-btn');
    
    // 信號卡片
    const signalCards = document.querySelectorAll('.signal-card');
    
    // 通知開關
    const notificationToggle = document.getElementById('notification-toggle');
    
    // 時間範圍選擇
    const timeframeSelect = document.getElementById('timeframe-select');
    
    // 通知容器
    const notificationContainer = document.querySelector('.notification-container');
    
    // 模擬數據 - 實際應用中這些數據應該從API請求獲取
    const mockSignals = [
        {
            id: 1,
            symbol: 'BTC/USDT',
            type: 'bullish',
            price: 68750.42,
            timestamp: new Date().toISOString(),
            confidence: '高',
            strategy: '突破策略',
            source: 'TradingView',
            description: 'BTC/USDT顯示強勁的上升趨勢，價格突破關鍵阻力位。交易量增加，表明買入壓力較大。MACD指標顯示看漲交叉。相對強弱指數(RSI)處於上升趨勢，但尚未達到超買水平。',
            targets: [
                { level: 1, price: 69500, probability: '高' },
                { level: 2, price: 71000, probability: '中' },
                { level: 3, price: 73000, probability: '低' }
            ],
            stopLoss: 67200
        },
        {
            id: 2,
            symbol: 'ETH/USDT',
            type: 'bullish',
            price: 3456.75,
            timestamp: new Date().toISOString(),
            confidence: '中',
            strategy: '均線交叉',
            source: 'TradingView',
            description: 'ETH/USDT的5日均線剛剛突破20日均線，形成看漲交叉。交易量適中但穩定。價格正在接近主要阻力位，需要觀察是否能夠突破。',
            targets: [
                { level: 1, price: 3550, probability: '高' },
                { level: 2, price: 3650, probability: '中' },
                { level: 3, price: 3800, probability: '低' }
            ],
            stopLoss: 3300
        },
        {
            id: 3,
            symbol: 'SOL/USDT',
            type: 'bearish',
            price: 148.32,
            timestamp: new Date().toISOString(),
            confidence: '中',
            strategy: '頭肩頂形態',
            source: 'Crypto-GPT',
            description: 'SOL/USDT形成了明顯的頭肩頂形態，並且價格跌破了頸線。交易量在下跌期間有所增加，顯示賣壓增強。MACD指標顯示負面趨勢。',
            targets: [
                { level: 1, price: 142, probability: '高' },
                { level: 2, price: 135, probability: '中' },
                { level: 3, price: 125, probability: '低' }
            ],
            stopLoss: 155
        },
        {
            id: 4,
            symbol: 'XRP/USDT',
            type: 'bearish',
            price: 0.5628,
            timestamp: new Date().toISOString(),
            confidence: '高',
            strategy: '支撐位被破',
            source: 'Crypto-GPT',
            description: 'XRP/USDT價格跌破關鍵支撐位0.58，且成交量大幅增加。相對強弱指數(RSI)顯示下跌趨勢，並未達到超賣狀態。多個技術指標顯示繼續下跌的可能性較高。',
            targets: [
                { level: 1, price: 0.54, probability: '高' },
                { level: 2, price: 0.52, probability: '中' },
                { level: 3, price: 0.49, probability: '低' }
            ],
            stopLoss: 0.59
        }
    ];
    
    // 打開模態框並顯示信號詳情
    function openModal(signalId) {
        // 在實際應用中，這裡應該根據signalId請求詳細數據
        const signal = mockSignals.find(s => s.id === parseInt(signalId));
        
        if (signal) {
            // 填充模態框內容
            document.querySelector('.modal-header h2').textContent = `${signal.symbol} ${signal.type === 'bullish' ? '看漲' : '看跌'}信號`;
            
            let modalContent = `
                <div class="signal-details">
                    <div class="detail-item">
                        <span class="detail-label">當前價格:</span>
                        <span class="detail-value">$${signal.price}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">信號時間:</span>
                        <span class="detail-value">${new Date(signal.timestamp).toLocaleString()}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">信心指數:</span>
                        <span class="detail-value">${signal.confidence}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">策略類型:</span>
                        <span class="detail-value">${signal.strategy}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">信號來源:</span>
                        <span class="detail-value">${signal.source}</span>
                    </div>
                </div>
                
                <div class="signal-description">
                    <h3>市場分析</h3>
                    <p>${signal.description}</p>
                </div>
                
                <div class="price-targets">
                    <h3>價格目標</h3>
                    <ul>
            `;
            
            signal.targets.forEach(target => {
                modalContent += `
                    <li>
                        <span class="target-level">目標 ${target.level}:</span>
                        <span class="target-price">$${target.price}</span>
                        <span class="target-probability">(${target.probability}概率)</span>
                    </li>
                `;
            });
            
            modalContent += `
                    </ul>
                </div>
                
                <div class="risk-management">
                    <h3>風險管理</h3>
                    <div class="detail-item">
                        <span class="detail-label">建議止損:</span>
                        <span class="detail-value">$${signal.stopLoss}</span>
                    </div>
                </div>
            `;
            
            document.querySelector('.modal-body').innerHTML = modalContent;
            
            // 顯示模態框
            modal.classList.add('active');
        }
    }
    
    // 關閉模態框
    function closeModal() {
        modal.classList.remove('active');
    }
    
    // 過濾信號
    function filterSignals(filterType) {
        // 移除所有按鈕的active類
        filterButtons.forEach(btn => btn.classList.remove('active'));
        
        // 為當前點擊的按鈕添加active類
        this.classList.add('active');
        
        // 過濾顯示信號卡片
        signalCards.forEach(card => {
            if (filterType === 'all') {
                card.style.display = 'block';
            } else if (card.classList.contains(filterType)) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }
    
    // 顯示通知
    function showNotification(message, type = 'info') {
        // 創建通知元素
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-message">${message}</div>
            <div class="notification-close">&times;</div>
        `;
        
        // 添加到通知容器
        notificationContainer.appendChild(notification);
        
        // 設置自動關閉
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 5000);
        
        // 添加關閉按鈕功能
        notification.querySelector('.notification-close').addEventListener('click', function() {
            notification.style.opacity = '0';
            setTimeout(() => {
                notification.remove();
            }, 300);
        });
    }
    
    // 添加事件監聽器
    
    // 模態框事件
    if (modalTriggers) {
        modalTriggers.forEach(trigger => {
            trigger.addEventListener('click', function() {
                const signalId = this.getAttribute('data-signal-id');
                openModal(signalId);
            });
        });
    }
    
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', closeModal);
    }
    
    // 點擊模態框外部關閉
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            closeModal();
        }
    });
    
    // 過濾按鈕事件
    if (filterButtons) {
        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                const filterType = this.getAttribute('data-filter');
                filterSignals.call(this, filterType);
            });
        });
    }
    
    // 通知開關事件
    if (notificationToggle) {
        notificationToggle.addEventListener('change', function() {
            if (this.checked) {
                showNotification('通知已啟用', 'success');
            } else {
                showNotification('通知已停用', 'info');
            }
        });
    }
    
    // 時間範圍選擇事件
    if (timeframeSelect) {
        timeframeSelect.addEventListener('change', function() {
            const selectedTimeframe = this.value;
            showNotification(`已切換到${selectedTimeframe}時間範圍`, 'info');
            // 這裡可以添加代碼來根據選擇的時間範圍重新獲取信號
        });
    }
    
    // 模擬創建信號卡片的函數
    function createSignalCards() {
        const signalsContainer = document.querySelector('.signals-container');
        
        if (!signalsContainer) {
            return;
        }
        
        // 清空現有內容
        signalsContainer.innerHTML = '';
        
        // 使用模擬數據創建卡片
        mockSignals.forEach(signal => {
            const card = document.createElement('div');
            card.className = `signal-card ${signal.type}`;
            
            card.innerHTML = `
                <div class="signal-header">
                    <div class="signal-symbol">${signal.symbol}</div>
                    <div class="signal-type ${signal.type}">${signal.type === 'bullish' ? '看漲' : '看跌'}</div>
                </div>
                <div class="signal-body">
                    <div class="signal-info">
                        <div class="signal-info-item">
                            <div class="signal-info-label">當前價格</div>
                            <div class="signal-info-value">$${signal.price}</div>
                        </div>
                        <div class="signal-info-item">
                            <div class="signal-info-label">信心指數</div>
                            <div class="signal-info-value">${signal.confidence}</div>
                        </div>
                        <div class="signal-info-item">
                            <div class="signal-info-label">策略</div>
                            <div class="signal-info-value">${signal.strategy}</div>
                        </div>
                    </div>
                    <div class="signal-actions">
                        <button class="btn btn-secondary view-details" data-signal-id="${signal.id}">查看詳情</button>
                        <button class="btn btn-primary confirm-signal">確認信號</button>
                    </div>
                </div>
            `;
            
            signalsContainer.appendChild(card);
            
            // 為新卡片添加事件監聽器
            card.querySelector('.view-details').addEventListener('click', function() {
                const signalId = this.getAttribute('data-signal-id');
                openModal(signalId);
            });
            
            card.querySelector('.confirm-signal').addEventListener('click', function() {
                showNotification(`已確認 ${signal.symbol} ${signal.type === 'bullish' ? '看漲' : '看跌'}信號`, 'success');
            });
        });
    }
    
    // 初始化信號卡片
    createSignalCards();
    
    // 更新統計數據的函數
    function updateStatistics() {
        const totalSignals = mockSignals.length;
        const bullishSignals = mockSignals.filter(s => s.type === 'bullish').length;
        const bearishSignals = mockSignals.filter(s => s.type === 'bearish').length;
        const winRate = 68; // 模擬勝率數據
        
        // 更新DOM元素
        const statElements = {
            'active-signals': totalSignals,
            'bullish-signals': bullishSignals,
            'bearish-signals': bearishSignals,
            'win-rate': `${winRate}%`
        };
        
        for (const [id, value] of Object.entries(statElements)) {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        }
    }
    
    // 初始化統計數據
    updateStatistics();
    
    // 模擬每30秒定時更新數據（實際應用中應使用WebSocket或輪詢API）
    setInterval(() => {
        // 隨機更新一些數據
        mockSignals.forEach(signal => {
            // 隨機價格波動
            const priceChange = (Math.random() - 0.5) * 2 * (signal.price * 0.005);
            signal.price = parseFloat((signal.price + priceChange).toFixed(signal.price < 1 ? 4 : 2));
            
            // 更新時間戳
            signal.timestamp = new Date().toISOString();
        });
        
        // 刷新UI
        createSignalCards();
        updateStatistics();
        
        // 根據通知開關決定是否顯示更新通知
        if (notificationToggle && notificationToggle.checked) {
            showNotification('信號數據已更新', 'info');
        }
    }, 30000);
}); 