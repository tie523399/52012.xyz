const express = require('express');
const cors = require('cors');
const path = require('path');
const https = require('https');
const fs = require('fs');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;
const HOST = process.env.HOST || '0.0.0.0';

// Middleware
app.use(cors({
    origin: process.env.CORS_ORIGINS ? process.env.CORS_ORIGINS.split(',') : '*',
    credentials: true
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// 安全性 headers (生產環境)
if (process.env.NODE_ENV === 'production') {
    app.use((req, res, next) => {
        res.setHeader('X-Content-Type-Options', 'nosniff');
        res.setHeader('X-Frame-Options', 'SAMEORIGIN');
        res.setHeader('X-XSS-Protection', '1; mode=block');
        res.setHeader('Referrer-Policy', 'no-referrer-when-downgrade');
        next();
    });
}

// API 路由應該在靜態檔案之前
const apiRouter = express.Router();

// 載入資料檔案
let pricesData = {};
let announcementsData = [];

try {
    pricesData = JSON.parse(fs.readFileSync(path.join(__dirname, 'data/prices.json'), 'utf8'));
    console.log('✅ 價格資料已載入');
} catch (error) {
    console.error('❌ 無法載入價格資料:', error.message);
}

try {
    announcementsData = JSON.parse(fs.readFileSync(path.join(__dirname, 'data/announcements.json'), 'utf8'));
    console.log('✅ 公告資料已載入');
} catch (error) {
    console.error('❌ 無法載入公告資料:', error.message);
}

// API: 取得價格資料
apiRouter.get('/prices', (req, res) => {
    res.json(pricesData);
});

// API: 取得公告資料
apiRouter.get('/announcements', (req, res) => {
    res.json(announcementsData);
});

// API: 7-11 門市回調處理
apiRouter.post('/711-callback', (req, res) => {
    console.log('收到 7-11 門市選擇回調');
    console.log('POST 資料:', req.body);
    
    // 7-11 API 可能使用的參數名稱
    const storeData = {
        storeId: req.body.CVSStoreID || req.body.storeId || req.body.StoreID,
        storeName: req.body.CVSStoreName || req.body.storeName || req.body.StoreName,
        storeAddress: req.body.CVSAddress || req.body.storeAddress || req.body.Address,
        storePhone: req.body.CVSTelephone || req.body.storePhone || req.body.Telephone,
        storeType: '711',
        timestamp: new Date().toISOString()
    };
    
    console.log('解析後的門市資料:', storeData);
    
    // 回傳 HTML 頁面，包含 JavaScript 來通知父視窗
    const responseHTML = `
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>門市選擇完成</title>
    <style>
        body {
            font-family: 'Noto Sans TC', sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: #f5f5f5;
        }
        .container {
            text-align: center;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .success { color: #4CAF50; }
        .store-info {
            margin: 20px 0;
            text-align: left;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2 class="success">✅ 門市選擇成功！</h2>
        <div class="store-info">
            <p><strong>門市編號：</strong>${storeData.storeId || '未提供'}</p>
            <p><strong>門市名稱：</strong>${storeData.storeName || '未提供'}</p>
            <p><strong>門市地址：</strong>${storeData.storeAddress || '未提供'}</p>
            <p><strong>門市電話：</strong>${storeData.storePhone || '未提供'}</p>
        </div>
        <p>視窗將在 3 秒後自動關閉...</p>
    </div>
    
    <script>
        // 將門市資料傳送給父視窗
        const storeData = ${JSON.stringify(storeData)};
        
        // 嘗試多種方式通知父視窗
        try {
            // 1. 使用 postMessage
            if (window.opener) {
                window.opener.postMessage({
                    type: 'STORE_SELECTED',
                    data: storeData
                }, '*');
            }
            
            // 2. 使用 localStorage（作為備用方案）
            localStorage.setItem('selectedStoreData', JSON.stringify(storeData));
            
            // 3. 如果是在 iframe 中
            if (window.parent !== window) {
                window.parent.postMessage({
                    type: 'STORE_SELECTED',
                    data: storeData
                }, '*');
            }
        } catch (e) {
            console.error('傳送門市資料失敗:', e);
        }
        
        // 3 秒後關閉視窗
        setTimeout(() => {
            window.close();
        }, 3000);
    </script>
</body>
</html>`;
    
    res.send(responseHTML);
});

// API: 發送 Telegram 通知
apiRouter.post('/send-telegram', async (req, res) => {
    console.log('收到 Telegram 通知請求');
    
    const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
    const TELEGRAM_CHAT_ID = process.env.TELEGRAM_CHAT_ID;
    
    if (!TELEGRAM_BOT_TOKEN || !TELEGRAM_CHAT_ID) {
        console.error('Telegram 配置未設定');
        return res.status(500).json({ 
            success: false,
            error: 'Telegram configuration missing' 
        });
    }

    try {
        const orderData = req.body;
        
        // 構建 Telegram 訊息
        const message = `🛒 **新訂單通知**

📋 **訂單編號**: ${orderData.orderId}
📅 **訂單時間**: ${new Date(orderData.orderDate).toLocaleString('zh-TW')}

👤 **客戶資訊**:
• 姓名: ${orderData.customer.name}
• 電話: ${orderData.customer.phone}

🏪 **取貨門市**:
• ${orderData.store.name}
• ${orderData.store.address || '地址未提供'}
• 店號: ${orderData.store.id}

🛍️ **訂購商品**:
${orderData.items.map(item => 
    `• ${item.name} x${item.quantity} - NT$ ${item.price * item.quantity}${item.flavor ? `\n  口味: ${item.flavor}` : ''}${item.color ? `\n  顏色: ${item.color}` : ''}`
).join('\n')}

💰 **金額明細**:
• 商品小計: NT$ ${orderData.subtotal}
• 運費: NT$ ${orderData.shipping}
• **總計: NT$ ${orderData.total}**

請盡快處理此訂單！`;

        // 發送到 Telegram
        const telegramData = JSON.stringify({
            chat_id: TELEGRAM_CHAT_ID,
            text: message,
            parse_mode: 'Markdown'
        });

        const options = {
            hostname: 'api.telegram.org',
            port: 443,
            path: `/bot${TELEGRAM_BOT_TOKEN}/sendMessage`,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': telegramData.length
            }
        };

        const telegramResponse = await new Promise((resolve, reject) => {
            const req = https.request(options, (res) => {
                let data = '';
                
                res.on('data', (chunk) => {
                    data += chunk;
                });
                
                res.on('end', () => {
                    try {
                        const response = JSON.parse(data);
                        resolve({ statusCode: res.statusCode, data: response });
                    } catch (e) {
                        reject(e);
                    }
                });
            });
            
            req.on('error', reject);
            req.write(telegramData);
            req.end();
        });

        if (telegramResponse.statusCode !== 200 || !telegramResponse.data.ok) {
            console.error('Telegram API 錯誤:', telegramResponse.data);
            return res.status(500).json({ 
                success: false,
                error: 'Failed to send Telegram notification',
                details: telegramResponse.data.description 
            });
        }

        console.log('✅ Telegram 通知發送成功');
        res.json({ 
            success: true,
            message: 'Notification sent successfully',
            messageId: telegramResponse.data.result.message_id
        });

    } catch (error) {
        console.error('處理錯誤:', error);
        res.status(500).json({ 
            success: false,
            error: 'Internal server error',
            message: error.message 
        });
    }
});

// API: 健康檢查
apiRouter.get('/health', (req, res) => {
    res.json({ 
        status: 'healthy',
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        environment: process.env.NODE_ENV || 'development',
        version: require('./package.json').version || '1.0.0',
        api: {
            telegram: !!process.env.TELEGRAM_BOT_TOKEN,
            cors: process.env.CORS_ORIGINS || '*'
        }
    });
});

// 掛載 API 路由
app.use('/api', apiRouter);

// 健康檢查（根路徑）
app.get('/health', (req, res) => {
    res.redirect('/api/health');
});

// 靜態檔案服務（在 API 路由之後）
// 生產環境中，Nginx 會處理靜態檔案，但保留此設定作為備用
if (process.env.NODE_ENV !== 'production' || process.env.SERVE_STATIC === 'true') {
    app.use(express.static(path.join(__dirname, 'dist'), {
        maxAge: '1d',
        etag: true
    }));
    
    // SPA 路由處理 - 所有非 API 路由都返回 index.html
    app.get('*', (req, res) => {
        res.sendFile(path.join(__dirname, 'dist', 'index.html'));
    });
} else {
    // 生產環境中，如果請求到達這裡，返回 404
    app.use((req, res) => {
        res.status(404).json({ 
            error: 'Not found',
            message: 'The requested resource was not found on this server.'
        });
    });
}

// 錯誤處理中間件
app.use((err, req, res, next) => {
    console.error('伺服器錯誤:', err);
    res.status(500).json({
        error: 'Internal Server Error',
        message: process.env.NODE_ENV === 'development' ? err.message : 'An error occurred'
    });
});

// 優雅關閉
process.on('SIGTERM', () => {
    console.log('收到 SIGTERM 信號，準備關閉伺服器...');
    server.close(() => {
        console.log('伺服器已關閉');
        process.exit(0);
    });
});

// 啟動伺服器
const server = app.listen(PORT, HOST, () => {
    console.log(`
╔═══════════════════════════════════════════╗
║         DeepVape API Server               ║
╚═══════════════════════════════════════════╝

🚀 伺服器運行在: http://${HOST}:${PORT}
📍 環境: ${process.env.NODE_ENV || 'development'}
🔐 Telegram: ${process.env.TELEGRAM_BOT_TOKEN ? '已配置' : '未配置'}

API 端點:
- GET  /api/health          健康檢查
- GET  /api/prices          取得價格資料
- GET  /api/announcements   取得公告資料
- POST /api/send-telegram   發送 Telegram 通知
- POST /api/711-callback    7-11 門市回調
`);
}); 