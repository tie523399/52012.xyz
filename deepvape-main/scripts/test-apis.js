#!/usr/bin/env node

/**
 * DeepVape API 測試腳本
 * 用於測試所有 API 端點是否正常運作
 */

const http = require('http');
const https = require('https');

const API_BASE = process.env.API_BASE || 'http://localhost:3000';
const isHTTPS = API_BASE.startsWith('https');

console.log('🧪 DeepVape API 測試開始...\n');
console.log(`📍 API 基礎 URL: ${API_BASE}\n`);

// 測試資料
const testOrderData = {
    orderId: 'TEST-' + Date.now(),
    orderDate: new Date().toISOString(),
    customer: {
        name: '測試客戶',
        phone: '0912345678'
    },
    store: {
        id: '123456',
        name: '測試門市',
        address: '測試地址'
    },
    items: [
        {
            name: '測試商品',
            quantity: 1,
            price: 100,
            flavor: '測試口味'
        }
    ],
    subtotal: 100,
    shipping: 60,
    total: 160
};

// HTTP 請求輔助函數
function makeRequest(path, options = {}) {
    return new Promise((resolve, reject) => {
        const url = new URL(path, API_BASE);
        const client = isHTTPS ? https : http;
        
        const reqOptions = {
            hostname: url.hostname,
            port: url.port || (isHTTPS ? 443 : 80),
            path: url.pathname + url.search,
            method: options.method || 'GET',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        };
        
        const req = client.request(reqOptions, (res) => {
            let data = '';
            
            res.on('data', (chunk) => {
                data += chunk;
            });
            
            res.on('end', () => {
                try {
                    const parsed = JSON.parse(data);
                    resolve({
                        status: res.statusCode,
                        data: parsed
                    });
                } catch (e) {
                    resolve({
                        status: res.statusCode,
                        data: data
                    });
                }
            });
        });
        
        req.on('error', reject);
        
        if (options.body) {
            req.write(JSON.stringify(options.body));
        }
        
        req.end();
    });
}

// 測試案例
const tests = [
    {
        name: '健康檢查',
        endpoint: '/api/health',
        method: 'GET',
        validate: (res) => res.status === 200 && res.data.status === 'healthy'
    },
    {
        name: '價格資料',
        endpoint: '/api/prices',
        method: 'GET',
        validate: (res) => res.status === 200 && typeof res.data === 'object'
    },
    {
        name: '公告資料',
        endpoint: '/api/announcements',
        method: 'GET',
        validate: (res) => res.status === 200 && Array.isArray(res.data)
    },
    {
        name: 'Telegram 通知（測試）',
        endpoint: '/api/send-telegram',
        method: 'POST',
        body: testOrderData,
        validate: (res) => {
            // 如果沒有設定 Telegram，應該返回錯誤
            if (res.status === 500 && res.data.error === 'Telegram configuration missing') {
                console.log('  ⚠️  Telegram 未設定（這是預期的）');
                return true;
            }
            return res.status === 200 && res.data.success === true;
        }
    }
];

// 執行測試
async function runTests() {
    let passed = 0;
    let failed = 0;
    
    for (const test of tests) {
        process.stdout.write(`📋 測試 ${test.name}... `);
        
        try {
            const result = await makeRequest(test.endpoint, {
                method: test.method,
                body: test.body
            });
            
            if (test.validate(result)) {
                console.log('✅ 通過');
                passed++;
            } else {
                console.log('❌ 失敗');
                console.log(`  回應狀態: ${result.status}`);
                console.log(`  回應資料:`, result.data);
                failed++;
            }
        } catch (error) {
            console.log('❌ 錯誤');
            console.log(`  錯誤訊息: ${error.message}`);
            failed++;
        }
    }
    
    console.log('\n📊 測試結果：');
    console.log(`✅ 通過: ${passed}`);
    console.log(`❌ 失敗: ${failed}`);
    console.log(`📈 總計: ${tests.length}`);
    
    // 額外資訊
    console.log('\n💡 提示：');
    console.log('- 確保伺服器正在運行: npm start');
    console.log('- 設定環境變數: cp env.example .env');
    console.log('- 測試生產環境: API_BASE=https://52012.xyz node scripts/test-apis.js');
    
    process.exit(failed > 0 ? 1 : 0);
}

// 檢查伺服器是否可達
console.log('🔍 檢查伺服器連線...');
makeRequest('/api/health')
    .then(() => {
        console.log('✅ 伺服器連線正常\n');
        runTests();
    })
    .catch((error) => {
        console.log('❌ 無法連線到伺服器');
        console.log(`錯誤: ${error.message}`);
        console.log('\n請確保伺服器正在運行：npm start');
        process.exit(1);
    }); 