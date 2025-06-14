// AWS Lambda function for sending Telegram notifications
exports.handler = async (event) => {
    // 設定 CORS headers
    const headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Content-Type': 'application/json'
    };

    // 處理 OPTIONS 請求（CORS preflight）
    if (event.httpMethod === 'OPTIONS') {
        return {
            statusCode: 200,
            headers,
            body: ''
        };
    }

    // 只允許 POST 請求
    if (event.httpMethod !== 'POST') {
        return {
            statusCode: 405,
            headers,
            body: JSON.stringify({ error: 'Method not allowed' })
        };
    }

    try {
        // 從環境變數獲取敏感資訊
        const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
        const TELEGRAM_CHAT_ID = process.env.TELEGRAM_CHAT_ID;

        if (!TELEGRAM_BOT_TOKEN || !TELEGRAM_CHAT_ID) {
            console.error('Missing Telegram configuration');
            return {
                statusCode: 500,
                headers,
                body: JSON.stringify({ error: 'Telegram configuration missing' })
            };
        }

        // 解析請求內容
        let orderData;
        try {
            orderData = JSON.parse(event.body);
        } catch (parseError) {
            return {
                statusCode: 400,
                headers,
                body: JSON.stringify({ error: 'Invalid request body' })
            };
        }

        // 構建 Telegram 訊息
        const message = `🛒 **新訂單通知**

📋 **訂單編號**: ${orderData.orderId}
📅 **訂單時間**: ${new Date(orderData.orderDate).toLocaleString('zh-TW', { timeZone: 'Asia/Taipei' })}

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

        // 使用 node-fetch 或 AWS SDK 發送請求
        const https = require('https');
        
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

        // 發送請求到 Telegram
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
            console.error('Telegram API error:', telegramResponse.data);
            return {
                statusCode: 500,
                headers,
                body: JSON.stringify({ 
                    error: 'Failed to send Telegram notification',
                    details: telegramResponse.data.description 
                })
            };
        }

        // 成功回應
        return {
            statusCode: 200,
            headers,
            body: JSON.stringify({ 
                success: true,
                message: 'Notification sent successfully',
                messageId: telegramResponse.data.result.message_id
            })
        };

    } catch (error) {
        console.error('Lambda execution error:', error);
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({ 
                error: 'Internal server error',
                message: error.message 
            })
        };
    }
}; 