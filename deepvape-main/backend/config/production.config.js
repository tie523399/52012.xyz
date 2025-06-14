/**
 * DeepVape 生產環境配置 - 52012.xyz
 */

module.exports = {
    // 伺服器設定
    server: {
        port: process.env.PORT || 3000,
        host: process.env.HOST || '127.0.0.1',
        trustProxy: true
    },
    
    // 域名設定
    domain: {
        main: '52012.xyz',
        frontend: 'https://52012.xyz',
        api: 'https://52012.xyz/api'
    },
    
    // CORS 設定
    cors: {
        origins: [
            'https://52012.xyz',
            'https://www.52012.xyz',
            'http://localhost:3000', // 開發環境
        ],
        methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
        credentials: true,
        maxAge: 86400 // 24 小時
    },
    
    // 安全設定
    security: {
        // 速率限制
        rateLimit: {
            windowMs: 60 * 1000, // 1 分鐘
            max: 100, // 每個 IP 最多 100 個請求
            message: '請求過於頻繁，請稍後再試',
            standardHeaders: true,
            legacyHeaders: false,
            
            // API 特定限制
            api: {
                windowMs: 60 * 1000,
                max: 60
            },
            
            // Telegram 發送限制
            telegram: {
                windowMs: 60 * 1000,
                max: 2 // 每分鐘最多 2 次
            }
        },
        
        // Helmet 配置
        helmet: {
            contentSecurityPolicy: {
                directives: {
                    defaultSrc: ["'self'", 'https:'],
                    styleSrc: ["'self'", 'https:', "'unsafe-inline'"],
                    scriptSrc: ["'self'", 'https:', "'unsafe-inline'", "'unsafe-eval'"],
                    imgSrc: ["'self'", 'https:', 'data:', 'blob:'],
                    connectSrc: ["'self'", 'https:', 'wss:'],
                    fontSrc: ["'self'", 'https:', 'data:'],
                    objectSrc: ["'none'"],
                    mediaSrc: ["'self'"],
                    frameSrc: ["'self'"]
                }
            },
            hsts: {
                maxAge: 63072000,
                includeSubDomains: true,
                preload: true
            }
        },
        
        // Session 配置
        session: {
            secret: process.env.SESSION_SECRET || 'change-this-in-production',
            resave: false,
            saveUninitialized: false,
            cookie: {
                secure: true, // HTTPS only
                httpOnly: true,
                maxAge: 24 * 60 * 60 * 1000, // 24 小時
                sameSite: 'strict'
            }
        }
    },
    
    // 7-11 API 設定
    sevenEleven: {
        callbackUrl: 'https://52012.xyz/api/711-callback',
        apiEndpoint: 'https://api.7-eleven.com.tw/v1',
        apiKey: process.env.SEVEN_ELEVEN_API_KEY,
        apiSecret: process.env.SEVEN_ELEVEN_API_SECRET,
        timeout: 30000 // 30 秒
    },
    
    // Telegram 設定
    telegram: {
        botToken: process.env.TELEGRAM_BOT_TOKEN,
        chatId: process.env.TELEGRAM_CHAT_ID,
        parseMode: 'HTML',
        sendInterval: 1000, // 發送間隔 1 秒
        maxRetries: 3,
        retryDelay: 5000 // 重試延遲 5 秒
    },
    
    // 日誌設定
    logging: {
        level: 'info',
        format: 'combined',
        dir: '/var/log/deepvape',
        maxSize: '20m',
        maxFiles: '14d',
        datePattern: 'YYYY-MM-DD'
    },
    
    // 檔案上傳設定
    upload: {
        maxFileSize: 10 * 1024 * 1024, // 10MB
        allowedTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
        uploadDir: '/var/www/deepvape/uploads',
        tempDir: '/tmp/deepvape-uploads'
    },
    
    // 靜態檔案
    static: {
        dir: '/var/www/deepvape/dist',
        maxAge: 31536000, // 1 年
        index: false,
        dotfiles: 'deny'
    },
    
    // 錯誤處理
    errorHandling: {
        showStack: false,
        logErrors: true,
        returnError: false
    },
    
    // 監控設定
    monitoring: {
        enabled: true,
        metricsPort: 9615,
        healthCheckPath: '/health',
        readinessPath: '/ready'
    },
    
    // 快取設定
    cache: {
        enabled: true,
        ttl: 300, // 5 分鐘
        checkPeriod: 60, // 每分鐘檢查過期
        maxKeys: 1000
    }
}; 