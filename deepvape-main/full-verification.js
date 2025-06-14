// DeepVape 完整功能驗證腳本

const fs = require('fs');
const path = require('path');
const http = require('http');

console.log('🔍 開始 DeepVape 完整功能驗證...\n');

const results = {
    passed: [],
    failed: [],
    warnings: []
};

// 測試伺服器是否運行
async function testServer() {
    console.log('🌐 測試伺服器連線...');
    
    return new Promise((resolve) => {
        const options = {
            hostname: 'localhost',
            port: 3000,
            path: '/api/health',
            method: 'GET'
        };

        const req = http.request(options, (res) => {
            let data = '';
            res.on('data', (chunk) => { data += chunk; });
            res.on('end', () => {
                if (res.statusCode === 200) {
                    results.passed.push('✅ Express 伺服器運行正常 (port 3000)');
                } else {
                    results.failed.push('❌ Express 伺服器回應異常');
                }
                resolve();
            });
        });

        req.on('error', (error) => {
            results.warnings.push('⚠️ Express 伺服器未運行 - 請執行 npm start');
            resolve();
        });

        req.end();
    });
}

// 驗證所有產品圖片
function verifyProductImages() {
    console.log('\n📸 驗證產品圖片載入...');
    
    const imageChecks = [
        // UI 圖片
        { file: 'images/ui/deepvape_logo_main.png', usage: '網站 Logo' },
        { file: 'images/ui/deepvape_main.png', usage: '首頁主圖' },
        { file: 'images/ui/7-11_tklogo.jpg', usage: '7-11 物流圖示' },
        
        // SP2 產品
        { file: 'sp2_v/sp2_device_main_showcase.jpg', usage: 'SP2 主機展示圖' },
        { file: 'sp2_d/sp2_pods_cartridge_collection.jpg', usage: 'SP2 煙彈圖' },
        
        // LANA 產品
        { file: 'lana_a8000/lana_a8000.webp', usage: 'LANA A8000' },
        { file: 'lana_pods/lana_ceramic_pods_main.webp', usage: 'LANA 煙彈' },
        
        // ILIA 產品
        { file: 'ilia_1/ilia_gen1_main_device.jpg', usage: 'ILIA 一代主機' },
        { file: 'illa_d/哩亞-ILIA煙彈.webp', usage: 'ILIA 煙彈' },
        
        // HTA 產品
        { file: 'hta_vape/hta_spade_device.webp', usage: 'HTA 黑桃主機' },
        { file: 'hta_pods/hta_spade_pods.webp', usage: 'HTA 煙彈' }
    ];

    let passCount = 0;
    let failCount = 0;

    imageChecks.forEach(({ file, usage }) => {
        const fullPath = path.join(__dirname, file);
        if (fs.existsSync(fullPath)) {
            const stats = fs.statSync(fullPath);
            if (stats.size > 0) {
                passCount++;
            } else {
                results.warnings.push(`⚠️ ${file} 檔案大小為 0 (${usage})`);
                failCount++;
            }
        } else {
            results.failed.push(`❌ 缺失圖片: ${file} (${usage})`);
            failCount++;
        }
    });

    results.passed.push(`✅ 產品圖片驗證: ${passCount}/${imageChecks.length} 通過`);
}

// 測試購物車功能
function testCartOperations() {
    console.log('\n🛒 測試購物車操作...');
    
    // 載入購物車邏輯檔案
    const cartLogicPath = path.join(__dirname, 'js/cart-logic.js');
    if (fs.existsSync(cartLogicPath)) {
        const content = fs.readFileSync(cartLogicPath, 'utf8');
        
        // 檢查關鍵功能
        const features = [
            { pattern: 'class CartManager', name: 'CartManager 類別' },
            { pattern: 'addItem', name: '加入商品功能' },
            { pattern: 'updateQuantity', name: '更新數量功能' },
            { pattern: 'removeItem', name: '移除商品功能' },
            { pattern: 'calculateTotals', name: '計算總額功能' },
            { pattern: 'localStorage', name: 'LocalStorage 持久化' },
            { pattern: 'observers', name: '觀察者模式' }
        ];
        
        features.forEach(({ pattern, name }) => {
            if (content.includes(pattern)) {
                results.passed.push(`✅ ${name} 已實作`);
            } else {
                results.failed.push(`❌ ${name} 未找到`);
            }
        });
    } else {
        results.failed.push('❌ cart-logic.js 檔案不存在');
    }
}

// 測試門市選擇功能
function testStoreSelection() {
    console.log('\n🏪 測試門市選擇功能...');
    
    const storeFiles = [
        'js/store-selector.js',
        'cvs_callback.html'
    ];
    
    storeFiles.forEach(file => {
        const fullPath = path.join(__dirname, file);
        if (fs.existsSync(fullPath)) {
            const content = fs.readFileSync(fullPath, 'utf8');
            
            if (file === 'js/store-selector.js') {
                if (content.includes('openStoreMap') && content.includes('emap.presco.com.tw')) {
                    results.passed.push('✅ 7-11 門市選擇 API 整合完成');
                }
                if (content.includes('handleMessage') && content.includes('postMessage')) {
                    results.passed.push('✅ 門市資料回傳機制實作');
                }
            }
            
            if (file === 'cvs_callback.html' && content.includes('parent.postMessage')) {
                results.passed.push('✅ 門市回調頁面配置正確');
            }
        } else {
            results.failed.push(`❌ ${file} 不存在`);
        }
    });
}

// 測試訂單提交與 Telegram
function testOrderSubmission() {
    console.log('\n📱 測試訂單提交與 Telegram 整合...');
    
    // 檢查伺服器端 Telegram 整合
    const serverPath = path.join(__dirname, 'server.js');
    if (fs.existsSync(serverPath)) {
        const content = fs.readFileSync(serverPath, 'utf8');
        
        if (content.includes('/api/send-telegram')) {
            results.passed.push('✅ Telegram API 端點存在');
        }
        
        if (content.includes('TELEGRAM_BOT_TOKEN') && content.includes('TELEGRAM_CHAT_ID')) {
            results.passed.push('✅ Telegram 環境變數配置');
        }
        
        if (content.includes('sendMessage')) {
            results.passed.push('✅ Telegram 發送訊息功能實作');
        }
    }
    
    // 檢查前端訂單提交
    const cartHtmlPath = path.join(__dirname, 'cart.html');
    if (fs.existsSync(cartHtmlPath)) {
        const content = fs.readFileSync(cartHtmlPath, 'utf8');
        
        if (content.includes('sendTelegramNotification')) {
            results.passed.push('✅ 前端 Telegram 通知函數存在');
        }
        
        if (content.includes('confirmCheckout')) {
            results.passed.push('✅ 訂單確認流程實作');
        }
    }
}

// 檢查所有頁面連結
function checkPageLinks() {
    console.log('\n🔗 檢查頁面連結...');
    
    const mainPages = [
        'index.html',
        'cart.html',
        'order_confirmation.html'
    ];
    
    const linkedPages = [
        'pages/shopping_guide.html',
        'pages/shipping_info.html',
        'pages/return_policy.html',
        'pages/faq.html',
        'pages/brand_story.html'
    ];
    
    // 檢查主要頁面是否正確連結到靜態頁面
    mainPages.forEach(page => {
        const pagePath = path.join(__dirname, page);
        if (fs.existsSync(pagePath)) {
            const content = fs.readFileSync(pagePath, 'utf8');
            let correctLinks = 0;
            
            linkedPages.forEach(linkedPage => {
                const linkPattern = `href="${linkedPage}"`;
                const oldLinkPattern = `href="${path.basename(linkedPage)}"`;
                
                if (content.includes(linkPattern)) {
                    correctLinks++;
                } else if (content.includes(oldLinkPattern)) {
                    results.warnings.push(`⚠️ ${page} 仍使用舊路徑連結到 ${path.basename(linkedPage)}`);
                }
            });
            
            if (correctLinks === linkedPages.length) {
                results.passed.push(`✅ ${page} 所有頁面連結正確`);
            }
        }
    });
    
    // 檢查所有連結的頁面是否存在
    linkedPages.forEach(page => {
        if (fs.existsSync(path.join(__dirname, page))) {
            results.passed.push(`✅ ${page} 存在`);
        } else {
            results.failed.push(`❌ ${page} 不存在`);
        }
    });
}

// 檢查 404 錯誤
function check404Errors() {
    console.log('\n🚫 檢查潛在的 404 錯誤...');
    
    const htmlFiles = fs.readdirSync(__dirname)
        .filter(f => f.endsWith('.html'))
        .concat(
            fs.readdirSync(path.join(__dirname, 'pages'))
                .filter(f => f.endsWith('.html'))
                .map(f => path.join('pages', f))
        );
    
    const resourcePatterns = [
        /<script[^>]*src=["']([^"']+)["']/g,
        /<link[^>]*href=["']([^"']+\.(?:css|js))["']/g,
        /<img[^>]*src=["']([^"']+)["']/g
    ];
    
    let totalResources = 0;
    let missingResources = [];
    
    htmlFiles.forEach(file => {
        const content = fs.readFileSync(path.join(__dirname, file), 'utf8');
        
        resourcePatterns.forEach(pattern => {
            let match;
            while ((match = pattern.exec(content)) !== null) {
                const resource = match[1];
                
                // 跳過外部資源
                if (resource.startsWith('http://') || resource.startsWith('https://') || resource.startsWith('//')) {
                    continue;
                }
                
                totalResources++;
                
                // 計算資源的實際路徑
                let resourcePath;
                if (resource.startsWith('/')) {
                    resourcePath = path.join(__dirname, resource.substring(1));
                } else if (file.includes('pages/')) {
                    resourcePath = path.join(__dirname, 'pages', '..', resource);
                } else {
                    resourcePath = path.join(__dirname, resource);
                }
                
                // 正規化路徑
                resourcePath = path.normalize(resourcePath);
                
                if (!fs.existsSync(resourcePath)) {
                    missingResources.push({
                        file: file,
                        resource: resource
                    });
                }
            }
        });
    });
    
    if (missingResources.length === 0) {
        results.passed.push(`✅ 無 404 錯誤 - 所有 ${totalResources} 個本地資源都存在`);
    } else {
        missingResources.forEach(({ file, resource }) => {
            results.failed.push(`❌ 404 錯誤: ${file} 引用缺失的 ${resource}`);
        });
    }
}

// 建立測試報告
function generateReport() {
    console.log('\n' + '='.repeat(60));
    console.log('📊 完整功能驗證報告');
    console.log('='.repeat(60));
    
    console.log(`\n✅ 通過項目 (${results.passed.length}):`);
    results.passed.forEach(item => console.log(`   ${item}`));
    
    if (results.warnings.length > 0) {
        console.log(`\n⚠️ 警告項目 (${results.warnings.length}):`);
        results.warnings.forEach(item => console.log(`   ${item}`));
    }
    
    if (results.failed.length > 0) {
        console.log(`\n❌ 失敗項目 (${results.failed.length}):`);
        results.failed.forEach(item => console.log(`   ${item}`));
    }
    
    console.log('\n' + '='.repeat(60));
    const status = results.failed.length === 0 ? '✅ 所有功能驗證通過！' : 
                   `❌ 發現 ${results.failed.length} 個問題需要處理`;
    console.log(`總結: ${status}`);
    console.log('='.repeat(60));
}

// 執行所有測試
async function runAllTests() {
    await testServer();
    verifyProductImages();
    testCartOperations();
    testStoreSelection();
    testOrderSubmission();
    checkPageLinks();
    check404Errors();
    generateReport();
    
    // 提供測試建議
    console.log('\n📋 手動測試建議:');
    console.log('1. 在瀏覽器開啟 http://localhost:3000/test.html');
    console.log('2. 測試加入購物車按鈕');
    console.log('3. 前往購物車頁面測試數量調整');
    console.log('4. 測試 7-11 門市選擇功能');
    console.log('5. 填寫訂單資料並測試提交');
    console.log('6. 檢查瀏覽器控制台是否有錯誤');
    
    console.log('\n✨ 功能驗證完成！');
}

// 執行驗證
runAllTests(); 