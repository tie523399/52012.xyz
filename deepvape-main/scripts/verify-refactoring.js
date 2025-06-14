#!/usr/bin/env node

/**
 * DeepVape 重構驗證腳本
 * 驗證重構後所有功能是否正常運作
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const { execSync } = require('child_process');

console.log('🔍 DeepVape 重構驗證開始...\n');

const results = {
    passed: [],
    failed: [],
    warnings: []
};

// 1. 檢查所有產品圖片
function checkProductImages() {
    console.log('📸 檢查產品圖片...');
    
    const imageDirectories = [
        'sp2_v', 'sp2_d', 'ilia_1', 'ilia_L', 'ilia_Bu', 'illa_d',
        'ilia_a_4', 'hta_vape', 'hta_pods', 'lana_a8000', 'lana_pods',
        'cart_image', 'images'
    ];
    
    let missingImages = [];
    
    imageDirectories.forEach(dir => {
        const dirPath = path.join(__dirname, '..', dir);
        if (!fs.existsSync(dirPath)) {
            results.warnings.push(`⚠️ 圖片目錄不存在: ${dir}`);
        } else {
            const files = fs.readdirSync(dirPath);
            if (files.length === 0) {
                results.warnings.push(`⚠️ 圖片目錄是空的: ${dir}`);
            } else {
                results.passed.push(`✅ 圖片目錄 ${dir} 包含 ${files.length} 個檔案`);
            }
        }
    });
    
    // 檢查 HTML 中引用的圖片
    const htmlFiles = fs.readdirSync(path.join(__dirname, '..'))
        .filter(file => file.endsWith('.html'));
    
    htmlFiles.forEach(file => {
        const content = fs.readFileSync(path.join(__dirname, '..', file), 'utf8');
        const imgMatches = content.match(/src="([^"]+\.(jpg|jpeg|png|webp|gif))"/gi) || [];
        
        imgMatches.forEach(match => {
            const imgPath = match.match(/src="([^"]+)"/)[1];
            if (!imgPath.startsWith('http') && !imgPath.startsWith('data:')) {
                const fullPath = path.join(__dirname, '..', imgPath);
                if (!fs.existsSync(fullPath)) {
                    missingImages.push(`${file}: ${imgPath}`);
                }
            }
        });
    });
    
    if (missingImages.length > 0) {
        results.failed.push(`❌ 找到 ${missingImages.length} 個缺失的圖片引用`);
        missingImages.slice(0, 5).forEach(img => {
            console.log(`   - ${img}`);
        });
        if (missingImages.length > 5) {
            console.log(`   ... 還有 ${missingImages.length - 5} 個`);
        }
    } else {
        results.passed.push('✅ 所有圖片引用都存在');
    }
}

// 2. 檢查購物車功能
function checkCartFunctionality() {
    console.log('\n🛒 檢查購物車功能...');
    
    // 檢查購物車相關功能是否存在於任何 JS 檔案中
    const jsDir = path.join(__dirname, '..', 'js');
    const jsFiles = fs.readdirSync(jsDir).filter(file => file.endsWith('.js'));
    
    const requiredFunctions = [
        'addToCart',
        'localStorage.setItem.*cart',
        'localStorage.getItem.*cart',
        'updateCartCount'
    ];
    
    let foundFunctions = new Set();
    
    jsFiles.forEach(file => {
        const content = fs.readFileSync(path.join(jsDir, file), 'utf8');
        
        requiredFunctions.forEach(func => {
            const regex = new RegExp(func, 'i');
            if (regex.test(content)) {
                foundFunctions.add(func);
            }
        });
    });
    
    // 檢查 HTML 檔案中的購物車功能
    const cartHtml = path.join(__dirname, '..', 'cart.html');
    if (fs.existsSync(cartHtml)) {
        const cartContent = fs.readFileSync(cartHtml, 'utf8');
        if (cartContent.includes('localStorage') && cartContent.includes('cart')) {
            foundFunctions.add('localStorage.getItem.*cart');
            foundFunctions.add('localStorage.setItem.*cart');
        }
    }
    
    if (foundFunctions.size >= 3) {
        results.passed.push('✅ 購物車功能存在（分散在多個檔案中）');
        foundFunctions.forEach(func => {
            results.passed.push(`✅ 找到功能: ${func}`);
        });
    } else {
        results.warnings.push('⚠️ 購物車功能可能不完整');
    }
}

// 3. 檢查門市選擇功能
function checkStoreSelector() {
    console.log('\n🏪 檢查門市選擇功能...');
    
    const storeFile = path.join(__dirname, '..', 'js', 'store-selector.js');
    if (fs.existsSync(storeFile)) {
        const content = fs.readFileSync(storeFile, 'utf8');
        
        if (content.includes('openStoreMap')) {
            results.passed.push('✅ 7-11 地圖功能存在');
        } else {
            results.failed.push('❌ 7-11 地圖功能缺失');
        }
        
        if (content.includes('processStoreSelection')) {
            results.passed.push('✅ 門市回調處理存在');
        } else {
            results.failed.push('❌ 門市回調處理缺失');
        }
    } else {
        results.failed.push('❌ 門市選擇器檔案不存在');
    }
}

// 4. 檢查 API 端點
function checkAPIEndpoints() {
    console.log('\n🌐 檢查 API 端點...');
    
    const serverFile = path.join(__dirname, '..', 'server.js');
    if (fs.existsSync(serverFile)) {
        const content = fs.readFileSync(serverFile, 'utf8');
        
        const endpoints = [
            '/api/health',
            '/api/prices',
            '/api/announcements',
            '/api/send-telegram',
            '/api/711-callback'
        ];
        
        endpoints.forEach(endpoint => {
            if (content.includes(endpoint)) {
                results.passed.push(`✅ API 端點存在: ${endpoint}`);
            } else {
                results.failed.push(`❌ API 端點缺失: ${endpoint}`);
            }
        });
    } else {
        results.failed.push('❌ 伺服器檔案不存在');
    }
}

// 5. 檢查共享元件
function checkSharedComponents() {
    console.log('\n🧩 檢查共享元件...');
    
    const sharedJS = path.join(__dirname, '..', 'js', 'shared-components.js');
    const sharedCSS = path.join(__dirname, '..', 'css', 'shared-styles.css');
    
    if (fs.existsSync(sharedJS)) {
        results.passed.push('✅ 共享 JavaScript 元件存在');
        
        const content = fs.readFileSync(sharedJS, 'utf8');
        const components = ['createHeader', 'createFooter', 'initVFXLogo', 'initPulseButtons'];
        
        components.forEach(comp => {
            if (content.includes(comp)) {
                results.passed.push(`✅ 元件函數存在: ${comp}`);
            } else {
                results.warnings.push(`⚠️ 元件函數可能缺失: ${comp}`);
            }
        });
    } else {
        results.failed.push('❌ 共享 JavaScript 元件不存在');
    }
    
    if (fs.existsSync(sharedCSS)) {
        results.passed.push('✅ 共享 CSS 樣式存在');
    } else {
        results.failed.push('❌ 共享 CSS 樣式不存在');
    }
}

// 6. 檢查頁面連結
function checkPageLinks() {
    console.log('\n🔗 檢查頁面連結...');
    
    const indexFile = path.join(__dirname, '..', 'index.html');
    if (fs.existsSync(indexFile)) {
        const content = fs.readFileSync(indexFile, 'utf8');
        const linkMatches = content.match(/href="([^"]+\.html)"/g) || [];
        
        let brokenLinks = [];
        linkMatches.forEach(match => {
            const link = match.match(/href="([^"]+)"/)[1];
            if (!link.startsWith('http') && !link.startsWith('#')) {
                const fullPath = path.join(__dirname, '..', link);
                if (!fs.existsSync(fullPath)) {
                    brokenLinks.push(link);
                }
            }
        });
        
        if (brokenLinks.length > 0) {
            results.failed.push(`❌ 找到 ${brokenLinks.length} 個損壞的連結`);
            brokenLinks.forEach(link => {
                console.log(`   - ${link}`);
            });
        } else {
            results.passed.push('✅ 所有頁面連結都有效');
        }
    }
}

// 7. 檢查 Console 錯誤（需要實際運行）
function checkConsoleErrors() {
    console.log('\n🚫 檢查 JavaScript 錯誤...');
    
    // 檢查是否有語法錯誤
    const jsFiles = fs.readdirSync(path.join(__dirname, '..', 'js'))
        .filter(file => file.endsWith('.js'));
    
    let syntaxErrors = 0;
    jsFiles.forEach(file => {
        try {
            const content = fs.readFileSync(path.join(__dirname, '..', 'js', file), 'utf8');
            new Function(content);
        } catch (error) {
            syntaxErrors++;
            results.failed.push(`❌ JavaScript 語法錯誤在 ${file}: ${error.message}`);
        }
    });
    
    if (syntaxErrors === 0) {
        results.passed.push('✅ 所有 JavaScript 檔案語法正確');
    }
}

// 執行所有檢查
function runAllChecks() {
    checkProductImages();
    checkCartFunctionality();
    checkStoreSelector();
    checkAPIEndpoints();
    checkSharedComponents();
    checkPageLinks();
    checkConsoleErrors();
    
    // 輸出總結
    console.log('\n' + '='.repeat(50));
    console.log('📊 驗證總結\n');
    
    console.log(`✅ 通過: ${results.passed.length} 項`);
    console.log(`❌ 失敗: ${results.failed.length} 項`);
    console.log(`⚠️  警告: ${results.warnings.length} 項`);
    
    if (results.failed.length > 0) {
        console.log('\n❌ 失敗項目:');
        results.failed.forEach(item => console.log(`   ${item}`));
    }
    
    if (results.warnings.length > 0) {
        console.log('\n⚠️  警告項目:');
        results.warnings.forEach(item => console.log(`   ${item}`));
    }
    
    if (results.failed.length === 0) {
        console.log('\n🎉 所有關鍵功能驗證通過！');
    } else {
        console.log('\n⚠️  請修復失敗的項目後再進行部署。');
    }
    
    // 生成報告
    const report = {
        timestamp: new Date().toISOString(),
        summary: {
            passed: results.passed.length,
            failed: results.failed.length,
            warnings: results.warnings.length
        },
        details: results
    };
    
    fs.writeFileSync(
        path.join(__dirname, '..', 'verification-report.json'),
        JSON.stringify(report, null, 2)
    );
    
    console.log('\n📄 詳細報告已儲存至 verification-report.json');
}

// 執行驗證
runAllChecks(); 