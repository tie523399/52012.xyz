/**
 * 7-11 門市選擇功能模組
 * 處理門市地圖選擇、資料回傳和顯示
 */

class StoreSelector {
    constructor() {
        this.selectedStore = null;
        // 使用配置檔案的設定（如果存在）
        this.eshopId = window.SITE_CONFIG?.SEVEN_ELEVEN?.ESHOP_ID || '870';
        this.serviceType = window.SITE_CONFIG?.SEVEN_ELEVEN?.SERVICE_TYPE || '1';
        this.init();
    }

    init() {
        // 監聽來自其他視窗的訊息
        window.addEventListener('message', this.handleMessage.bind(this));
    }

    /**
     * 開啟 7-11 電子地圖選擇門市
     */
    openStoreMap() {
        // 建構回調 URL - 必須是公開可訪問的 URL
        let callbackUrl;
        
        // 檢查環境
        const isProduction = window.location.hostname !== 'localhost' && 
                           window.location.hostname !== '127.0.0.1';
        
        if (isProduction) {
            // 生產環境：使用回調頁面（期望 7-11 會在 URL 中附加參數）
            callbackUrl = window.location.origin + '/cvs_callback.html';
        } else {
            // 開發環境：需要公開 URL
            console.warn('⚠️ 7-11 API 整合 - 開發環境限制');
            console.warn('7-11 無法將資料發送到 localhost');
            
            // 檢查是否有設定開發用的公開 URL
            if (window.SITE_CONFIG?.DEVELOPMENT_CALLBACK_URL) {
                callbackUrl = window.SITE_CONFIG.DEVELOPMENT_CALLBACK_URL;
                console.log('使用開發回調 URL:', callbackUrl);
            } else {
                // 使用測試功能
                console.log('💡 提示：使用 cvs_callback.html 的測試功能進行開發');
                if (confirm('開發環境無法直接使用 7-11 API。\n\n是否開啟測試頁面？')) {
                    window.open('/cvs_callback.html', 'TestStoreSelection', 'width=600,height=700');
                }
                return;
            }
        }
        
        console.log('📍 7-11 回調 URL:', callbackUrl);

        // 構建 7-11 電子地圖 URL
        const mapUrl = 'https://emap.presco.com.tw/c2cemap.ashx' + 
                      '?eshopid=' + this.eshopId +
                      '&servicetype=' + this.serviceType +
                      '&url=' + encodeURIComponent(callbackUrl);

        console.log('🗺️ 開啟 7-11 電子地圖:', mapUrl);

        // 開啟新視窗
        const mapWindow = window.open(
            mapUrl, 
            'SevenElevenStoreMap', 
            'width=1000,height=700,scrollbars=yes,resizable=yes'
        );

        if (!mapWindow) {
            alert('無法開啟門市查詢視窗，請檢查瀏覽器的彈出視窗設定。');
            return;
        }

        // 顯示使用指引
        this.showInstructions();
        
        // 監聽回調結果
        this.waitForCallback();
    }

    /**
     * 等待門市選擇回調
     */
    waitForCallback() {
        // 檢查 localStorage 是否有新的門市資料
        const checkInterval = setInterval(() => {
            const storeData = localStorage.getItem('selectedStoreData');
            if (storeData) {
                try {
                    const store = JSON.parse(storeData);
                    // 確認是最近的資料（5分鐘內）
                    if (store.timestamp) {
                        const timeDiff = Date.now() - new Date(store.timestamp).getTime();
                        if (timeDiff < 5 * 60 * 1000) { // 5分鐘
                            this.processStoreSelection(store);
                            localStorage.removeItem('selectedStoreData');
                            clearInterval(checkInterval);
                        }
                    }
                } catch (e) {
                    console.error('解析門市資料失敗:', e);
                }
            }
        }, 1000);
        
        // 30秒後停止檢查
        setTimeout(() => {
            clearInterval(checkInterval);
        }, 30000);
    }

    /**
     * 顯示使用說明
     */
    showInstructions() {
        const instructions = `📍 7-ELEVEN 門市查詢說明：

1. 在地圖上選擇您要取貨的門市
2. 點擊「確認」按鈕
3. 系統將自動回傳門市資訊

⚠️ 注意事項：
- 請確保允許彈出視窗
- 選擇門市後系統會自動填入資訊`;

        // 使用更友善的提示方式
        if (window.showNotification) {
            window.showNotification(instructions, 'info');
        } else {
            console.log(instructions);
        }
    }

    /**
     * 處理來自其他視窗的訊息
     */
    handleMessage(event) {
        // 驗證訊息來源
        if (!event.data || event.data.type !== 'STORE_SELECTED') {
            return;
        }

        console.log('收到門市選擇訊息:', event.data);
        
        // 處理門市資料
        if (event.data.data) {
            this.processStoreSelection(event.data.data);
        }
    }

    /**
     * 處理門市選擇資料
     */
    processStoreSelection(storeInfo) {
        // 標準化門市資料格式
        this.selectedStore = {
            storeId: storeInfo.storeId,
            storeName: storeInfo.storeName,
            storeAddress: storeInfo.storeAddress,
            storePhone: storeInfo.storePhone,
            storeType: storeInfo.storeType || '711'
        };

        console.log('處理門市資料:', this.selectedStore);

        // 更新顯示
        this.updateStoreDisplay(this.selectedStore);

        // 執行回調
        this.onStoreSelected(this.selectedStore);

        // 儲存到 sessionStorage（供頁面重新載入時使用）
        sessionStorage.setItem('currentSelectedStore', JSON.stringify(this.selectedStore));
    }

    /**
     * 更新門市顯示資訊
     */
    updateStoreDisplay(storeInfo) {
        // 取得顯示元素
        const displayElements = {
            selectedStore: document.getElementById('selectedStore'),
            storeName: document.getElementById('storeName'),
            storeAddress: document.getElementById('storeAddress'),
            storeId: document.getElementById('storeId'),
            storePhone: document.getElementById('storePhone')
        };

        // 更新顯示內容
        if (displayElements.storeName) {
            displayElements.storeName.textContent = `7-ELEVEN ${storeInfo.storeName}`;
        }
        
        if (displayElements.storeAddress) {
            displayElements.storeAddress.textContent = storeInfo.storeAddress || '地址未提供';
        }
        
        if (displayElements.storeId) {
            displayElements.storeId.textContent = `門市代號：${storeInfo.storeId}`;
        }
        
        if (displayElements.storePhone) {
            displayElements.storePhone.textContent = `電話：${storeInfo.storePhone || '未提供'}`;
        }

        // 顯示選擇的門市區塊
        if (displayElements.selectedStore) {
            displayElements.selectedStore.style.display = 'block';
            displayElements.selectedStore.classList.add('show');
        }
    }

    /**
     * 門市選擇完成的回調函數
     * 可以被覆寫以執行自訂邏輯
     */
    onStoreSelected(storeInfo) {
        console.log('門市選擇完成:', storeInfo);
        
        // 顯示成功訊息
        const message = `✅ 已選擇門市：
        
門市代號：${storeInfo.storeId}
門市名稱：${storeInfo.storeName}
門市地址：${storeInfo.storeAddress || '未提供'}
門市電話：${storeInfo.storePhone || '未提供'}`;

        if (window.showNotification) {
            window.showNotification(message, 'success');
        } else {
            alert(message);
        }
    }

    /**
     * 取得選擇的門市資訊
     */
    getSelectedStore() {
        return this.selectedStore;
    }

    /**
     * 清除選擇的門市
     */
    clearSelectedStore() {
        this.selectedStore = null;
        
        // 隱藏顯示區塊
        const selectedStoreElement = document.getElementById('selectedStore');
        if (selectedStoreElement) {
            selectedStoreElement.style.display = 'none';
            selectedStoreElement.classList.remove('show');
        }
        
        // 清除 sessionStorage
        sessionStorage.removeItem('currentSelectedStore');
    }

    /**
     * 手動設定門市資訊
     */
    setStore(storeInfo) {
        this.selectedStore = storeInfo;
        this.updateStoreDisplay(storeInfo);
    }
}

// 建立全域實例
window.storeSelector = new StoreSelector();

// 開發環境輔助函數
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    console.log('🛠️ 開發環境 - 7-11 API 整合提示：');
    console.log('1. 使用 ngrok 建立公開 URL: ngrok http 3000');
    console.log('2. 在 config.js 設定 DEVELOPMENT_CALLBACK_URL');
    console.log('3. 或使用手動輸入門市功能進行測試');
} 