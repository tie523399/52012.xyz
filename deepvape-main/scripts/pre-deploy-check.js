#!/usr/bin/env node

/**
 * DeepVape 部署前檢查腳本
 * 確保所有必要的檔案和設定都已準備好
 */

const fs = require('fs');
const path = require('path');

// 顏色輸出
const colors = {
    reset: '\x1b[0m',
    green: '\x1b[32m',
    red: '\x1b[31m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m'
};

const log = {
    success: (msg) => console.log(`${colors.green}✓ ${msg}${colors.reset}`),
    error: (msg) => console.log(`${colors.red}✗ ${msg}${colors.reset}`),
    warning: (msg) => console.log(`${colors.yellow}⚠ ${msg}${colors.reset}`),
    info: (msg) => console.log(`${colors.blue}ℹ ${msg}${colors.reset}`)
};

console.log('\n🔍 DeepVape 部署前檢查\n');

let errors = 0;
let warnings = 0;

// 檢查必要檔案
const requiredFiles = [
    'package.json',
    'server.js',
    'ecosystem.config.js',
    'webpack.config.js',
    'scripts/setup-server.sh',
    'scripts/deploy.sh',
    'scripts/setup-ssl.sh',
    'nginx/deepvape.conf',
    'DEPLOYMENT_GUIDE.md'
];

console.log('📋 檢查必要檔案...');
requiredFiles.forEach(file => {
    const filePath = path.join(__dirname, '..', file);
    if (fs.existsSync(filePath)) {
        log.success(`找到 ${file}`);
    } else {
        log.error(`缺少 ${file}`);
        errors++;
    }
});

// 檢查目錄結構
console.log('\n📁 檢查目錄結構...');
const requiredDirs = [
    'css',
    'js',
    'images',
    'components',
    'pages',
    'scripts',
    'nginx',
    'config'
];

requiredDirs.forEach(dir => {
    const dirPath = path.join(__dirname, '..', dir);
    if (fs.existsSync(dirPath) && fs.statSync(dirPath).isDirectory()) {
        log.success(`目錄 ${dir}/ 存在`);
    } else {
        log.error(`缺少目錄 ${dir}/`);
        errors++;
    }
});

// 檢查 package.json
console.log('\n📦 檢查 package.json...');
try {
    const packageJson = require('../package.json');
    
    // 檢查必要的依賴
    const requiredDeps = ['express', 'cors', 'dotenv'];
    requiredDeps.forEach(dep => {
        if (packageJson.dependencies && packageJson.dependencies[dep]) {
            log.success(`依賴 ${dep} 已定義`);
        } else {
            log.error(`缺少依賴 ${dep}`);
            errors++;
        }
    });
    
    // 檢查腳本
    const requiredScripts = ['start', 'build', 'build:prod'];
    requiredScripts.forEach(script => {
        if (packageJson.scripts && packageJson.scripts[script]) {
            log.success(`腳本 ${script} 已定義`);
        } else {
            log.error(`缺少腳本 ${script}`);
            errors++;
        }
    });
} catch (e) {
    log.error('無法讀取 package.json');
    errors++;
}

// 檢查環境變數範例
console.log('\n🔐 檢查環境變數...');
const envExamplePath = path.join(__dirname, '..', 'config', 'env.production.example');
if (fs.existsSync(envExamplePath)) {
    log.success('找到環境變數範例檔案');
    
    // 檢查重要的環境變數
    const envContent = fs.readFileSync(envExamplePath, 'utf8');
    const requiredEnvVars = [
        'NODE_ENV',
        'PORT',
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_CHAT_ID'
    ];
    
    requiredEnvVars.forEach(envVar => {
        if (envContent.includes(envVar)) {
            log.success(`環境變數 ${envVar} 已定義`);
        } else {
            log.warning(`環境變數 ${envVar} 未在範例中定義`);
            warnings++;
        }
    });
} else {
    log.error('缺少環境變數範例檔案');
    errors++;
}

// 檢查 Git 設定
console.log('\n🔗 檢查 Git 設定...');
const gitPath = path.join(__dirname, '..', '.git');
if (fs.existsSync(gitPath)) {
    log.success('Git 儲存庫已初始化');
} else {
    log.warning('尚未初始化 Git 儲存庫');
    log.info('執行 git init 來初始化');
    warnings++;
}

// 檢查構建檔案
console.log('\n🏗️ 檢查構建系統...');
const distPath = path.join(__dirname, '..', 'dist');
if (fs.existsSync(distPath)) {
    log.success('找到 dist 目錄');
    log.info('記得在部署前執行 npm run build:prod');
} else {
    log.warning('尚未建置（dist 目錄不存在）');
    log.info('執行 npm run build:prod 來建置');
    warnings++;
}

// 檢查 Node.js 版本
console.log('\n🟢 檢查 Node.js 版本...');
const nodeVersion = process.version;
const majorVersion = parseInt(nodeVersion.split('.')[0].substring(1));
if (majorVersion >= 16) {
    log.success(`Node.js 版本 ${nodeVersion} 符合需求`);
} else {
    log.error(`Node.js 版本 ${nodeVersion} 過舊，需要 16.x 或更高`);
    errors++;
}

// 總結
console.log('\n' + '='.repeat(50));
console.log('📊 檢查結果總結');
console.log('='.repeat(50));

if (errors === 0 && warnings === 0) {
    console.log(`${colors.green}✅ 所有檢查通過！專案已準備好部署。${colors.reset}`);
} else {
    if (errors > 0) {
        console.log(`${colors.red}❌ 發現 ${errors} 個錯誤${colors.reset}`);
    }
    if (warnings > 0) {
        console.log(`${colors.yellow}⚠️  發現 ${warnings} 個警告${colors.reset}`);
    }
    console.log('\n請修正錯誤後再進行部署。');
}

console.log('\n下一步：');
console.log('1. 執行 npm run deploy:prepare 來準備部署');
console.log('2. 將程式碼推送到 GitHub');
console.log('3. 按照 DEPLOYMENT_GUIDE.md 進行部署\n');

process.exit(errors > 0 ? 1 : 0); 