#!/usr/bin/env node

/**
 * 域名更新腳本
 * 將所有 52012.xyz/org 引用替換為 52012.xyz
 */

const fs = require('fs');
const path = require('path');

const OLD_DOMAINS = ['52012.xyz', '52012.xyz'];
const NEW_DOMAIN = '52012.xyz';

// 要排除的目錄和檔案
const EXCLUDE_DIRS = ['node_modules', '.git', 'dist', 'archive'];
const EXCLUDE_FILES = ['.jpg', '.png', '.gif', '.webp', '.mp4', '.zip', '.tar'];

let totalReplacements = 0;
let filesUpdated = 0;

/**
 * 遞迴處理目錄
 */
function processDirectory(dir) {
    const items = fs.readdirSync(dir);
    
    items.forEach(item => {
        const fullPath = path.join(dir, item);
        const stat = fs.statSync(fullPath);
        
        if (stat.isDirectory()) {
            if (!EXCLUDE_DIRS.includes(item)) {
                processDirectory(fullPath);
            }
        } else if (stat.isFile()) {
            const ext = path.extname(fullPath).toLowerCase();
            if (!EXCLUDE_FILES.includes(ext)) {
                processFile(fullPath);
            }
        }
    });
}

/**
 * 處理單個檔案
 */
function processFile(filePath) {
    try {
        let content = fs.readFileSync(filePath, 'utf8');
        let modified = false;
        let replacements = 0;
        
        OLD_DOMAINS.forEach(oldDomain => {
            // 替換各種形式的域名
            const patterns = [
                new RegExp(`https?://(www\\.)?${oldDomain.replace('.', '\\.')}`, 'gi'),
                new RegExp(`${oldDomain.replace('.', '\\.')}`, 'gi'),
                new RegExp(`service@${oldDomain.replace('.', '\\.')}`, 'gi')
            ];
            
            patterns.forEach(pattern => {
                const matches = content.match(pattern);
                if (matches) {
                    replacements += matches.length;
                    content = content.replace(pattern, (match) => {
                        if (match.includes('service@')) {
                            return `service@${NEW_DOMAIN}`;
                        } else if (match.includes('https://')) {
                            return `https://${NEW_DOMAIN}`;
                        } else if (match.includes('http://')) {
                            return `http://${NEW_DOMAIN}`;
                        } else if (match.includes('www.')) {
                            return `www.${NEW_DOMAIN}`;
                        } else {
                            return NEW_DOMAIN;
                        }
                    });
                    modified = true;
                }
            });
        });
        
        if (modified) {
            fs.writeFileSync(filePath, content, 'utf8');
            console.log(`✅ 更新 ${path.relative(process.cwd(), filePath)} (${replacements} 處替換)`);
            totalReplacements += replacements;
            filesUpdated++;
        }
    } catch (error) {
        console.error(`❌ 處理 ${filePath} 時發生錯誤: ${error.message}`);
    }
}

// 執行更新
console.log('🔄 開始更新域名...\n');
console.log(`舊域名: ${OLD_DOMAINS.join(', ')}`);
console.log(`新域名: ${NEW_DOMAIN}\n`);

processDirectory(process.cwd());

console.log('\n📊 更新完成！');
console.log(`總共替換: ${totalReplacements} 處`);
console.log(`更新檔案: ${filesUpdated} 個`);

// 特別提醒
console.log('\n⚠️  重要提醒：');
console.log('1. 請更新 DNS 記錄指向您的 VPS IP');
console.log('2. 請在 7-11 系統中更新回調 URL');
console.log('3. 請更新 SSL 證書為新域名');
console.log('4. 請檢查所有第三方服務的域名設定'); 