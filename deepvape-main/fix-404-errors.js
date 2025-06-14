// DeepVape 404 錯誤修復腳本

const fs = require('fs');
const path = require('path');

console.log('🔧 開始修復 404 錯誤...\n');

// 1. 修復圖片路徑問題
console.log('🖼️ 修復圖片路徑...');

const fixes = [
    {
        file: 'cart.html',
        from: 'src="7-11_tklogo.jpg"',
        to: 'src="images/ui/7-11_tklogo.jpg"'
    },
    {
        file: 'hta_vape_product.html',
        from: 'logo.png',
        to: 'images/ui/logo.png'
    },
    {
        file: 'index.html',
        from: 'src="deepvape_main.png"',
        to: 'src="images/ui/deepvape_main.png"'
    },
    {
        file: 'lana_pods_product.html',
        from: 'src="deepvape_logo_main.png"',
        to: 'src="images/ui/deepvape_logo_main.png"'
    },
    {
        file: 'order_confirmation.html',
        from: 'src="product_showcase.jpg"',
        to: 'src="images/ui/product_showcase.jpg"'
    }
];

fixes.forEach(({file, from, to}) => {
    const filePath = path.join(__dirname, file);
    if (fs.existsSync(filePath)) {
        let content = fs.readFileSync(filePath, 'utf8');
        if (content.includes(from)) {
            content = content.replace(new RegExp(from, 'g'), to);
            fs.writeFileSync(filePath, content);
            console.log(`✅ 修復 ${file}: ${from} -> ${to}`);
        }
    }
});

// 2. 建立缺失的 SP2 產品圖片（複製現有圖片作為替代）
console.log('\n📁 處理缺失的產品圖片...');

const sp2Images = [
    'sp2_v/sp2_device_galaxy_blue.jpg',
    'sp2_v/sp2_device_samurai_black.jpg', 
    'sp2_v/sp2_device_deep_sea_green.jpg'
];

const sourceSp2Image = path.join(__dirname, 'sp2_v/sp2_device_main_showcase.jpg');

sp2Images.forEach(image => {
    const imagePath = path.join(__dirname, image);
    if (!fs.existsSync(imagePath) && fs.existsSync(sourceSp2Image)) {
        fs.copyFileSync(sourceSp2Image, imagePath);
        console.log(`✅ 建立替代圖片: ${image}`);
    }
});

// 3. 修復 pages 目錄中的路徑問題
console.log('\n🔗 修復 pages 目錄中的路徑...');

const pagesFixes = [
    {
        files: ['pages/brand_story.html', 'pages/shopping_guide.html'],
        from: '../images/ui/deepvape_logo_main.png',
        to: '../images/ui/deepvape_logo_main.png'
    }
];

// 檢查路徑是否正確
const logoPath = path.join(__dirname, 'images/ui/deepvape_logo_main.png');
if (fs.existsSync(logoPath)) {
    console.log('✅ Logo 檔案存在於正確位置');
} else {
    console.log('❌ Logo 檔案不在預期位置，嘗試修復...');
    // 如果檔案在根目錄，移動到正確位置
    const rootLogoPath = path.join(__dirname, 'deepvape_logo_main.png');
    if (fs.existsSync(rootLogoPath)) {
        fs.copyFileSync(rootLogoPath, logoPath);
        console.log('✅ 已複製 logo 到 images/ui 目錄');
    }
}

// 4. 移除模板變數（這些應該由 JavaScript 動態生成）
console.log('\n🧹 處理模板變數...');

const templateVars = [
    '${item.image}',
    '${product.main_image}'
];

const htmlFiles = fs.readdirSync(__dirname)
    .filter(f => f.endsWith('.html'))
    .concat(
        fs.readdirSync(path.join(__dirname, 'pages'))
            .filter(f => f.endsWith('.html'))
            .map(f => path.join('pages', f))
    );

htmlFiles.forEach(file => {
    const filePath = path.join(__dirname, file);
    let content = fs.readFileSync(filePath, 'utf8');
    let modified = false;
    
    templateVars.forEach(templateVar => {
        if (content.includes(`src="${templateVar}"`)) {
            console.log(`ℹ️ ${file} 包含模板變數 ${templateVar} - 這是正常的，將由 JavaScript 處理`);
        }
    });
});

// 5. 建立缺失圖片清單
console.log('\n📋 建議手動處理的圖片：');
const missingImages = [
    'sp2_v/sp2_device_galaxy_blue.jpg - SP2 星河藍',
    'sp2_v/sp2_device_samurai_black.jpg - SP2 武士黑',
    'sp2_v/sp2_device_deep_sea_green.jpg - SP2 深海綠'
];

missingImages.forEach(img => {
    console.log(`  - ${img}`);
});

console.log('\n✨ 修復完成！');
console.log('\n下一步：');
console.log('1. 執行 node full-verification.js 再次驗證');
console.log('2. 確保伺服器運行中：npm start');
console.log('3. 在瀏覽器測試功能'); 