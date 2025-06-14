/**
 * DeepVape Meta 標籤生成器
 * 為所有頁面添加適當的 SEO 和社交媒體 meta 標籤
 */

class MetaTagsGenerator {
    constructor() {
        this.defaultMeta = {
            // 基本 Meta
            charset: 'UTF-8',
            viewport: 'width=device-width, initial-scale=1.0',
            author: 'DeepVape',
            robots: 'index, follow',
            language: 'zh-TW',
            
            // SEO Meta
            title: 'DeepVape - 台灣領先的電子煙品牌',
            description: '提供高品質電子煙產品，包括 SP2、ILIA、LANA、HTA 等知名品牌。支援 7-11 取貨付款，購物安全方便。',
            keywords: '電子煙,vape,SP2,ILIA,LANA,HTA,主機,煙彈,拋棄式電子煙,台灣電子煙',
            
            // Open Graph
            'og:type': 'website',
            'og:site_name': 'DeepVape',
            'og:locale': 'zh_TW',
            'og:image:width': '1200',
            'og:image:height': '630',
            
            // Twitter Card
            'twitter:card': 'summary_large_image',
            'twitter:site': '@deepvape',
            
            // 其他
            'format-detection': 'telephone=no',
            'theme-color': '#06b6d4'
        };
        
        this.init();
    }

    init() {
        // 如果已經初始化過，不重複執行
        if (document.querySelector('meta[name="meta-generator"]')) {
            return;
        }
        
        // 標記已初始化
        this.addMeta('meta-generator', 'DeepVape Meta Generator');
        
        // 生成基本 meta 標籤
        this.generateBasicMeta();
        
        // 生成頁面特定的 meta 標籤
        this.generatePageSpecificMeta();
        
        // 添加資源提示
        this.addResourceHints();
        
        // 添加結構化數據
        this.addStructuredData();
    }

    generateBasicMeta() {
        // Charset - 確保是第一個
        if (!document.querySelector('meta[charset]')) {
            const charset = document.createElement('meta');
            charset.setAttribute('charset', this.defaultMeta.charset);
            document.head.insertBefore(charset, document.head.firstChild);
        }
        
        // Viewport
        this.addOrUpdateMeta('viewport', this.defaultMeta.viewport);
        
        // 基本 SEO
        this.addOrUpdateMeta('author', this.defaultMeta.author);
        this.addOrUpdateMeta('robots', this.defaultMeta.robots);
        this.addOrUpdateMeta('language', this.defaultMeta.language);
        this.addOrUpdateMeta('format-detection', this.defaultMeta['format-detection']);
        this.addOrUpdateMeta('theme-color', this.defaultMeta['theme-color']);
    }

    generatePageSpecificMeta() {
        const pagePath = window.location.pathname;
        let pageData = {};
        
        // 根據頁面路徑設定特定的 meta 資料
        if (pagePath.includes('sp2_product')) {
            pageData = {
                title: 'SP2 一代主機 - DeepVape',
                description: 'SP2 一代主機搭載智能溫控系統，16 種顏色選擇，400mAH 電池容量，為您帶來穩定順滑的使用體驗。',
                'og:title': 'SP2 一代主機 - 智能溫控電子煙',
                'og:description': '16 種顏色選擇，智能溫控系統，穩定輸出功率 7W-8W',
                'og:image': this.getAbsoluteUrl('sp2_v/sp2_device_main_showcase.jpg')
            };
        } else if (pagePath.includes('lana_pods')) {
            pageData = {
                title: 'LANA 煙彈 - DeepVape',
                description: 'LANA 煙彈採用頂級陶瓷芯霧化技術，12 種口味選擇，2ML 大容量設計，純淨濃郁的口感體驗。',
                'og:title': 'LANA 陶瓷芯煙彈 - 12 種口味',
                'og:description': '頂級陶瓷芯技術，2ML 容量，多種口味選擇',
                'og:image': this.getAbsoluteUrl('lana_pods/lana_ceramic_pods_main.webp')
            };
        } else if (pagePath.includes('cart')) {
            pageData = {
                title: '購物車 - DeepVape',
                description: '查看您的購物車商品，支援 7-11 取貨付款，安全便利的結帳流程。',
                'og:title': '購物車 - DeepVape',
                robots: 'noindex, follow'
            };
        } else {
            // 首頁或其他頁面使用預設值
            pageData = {
                title: this.defaultMeta.title,
                description: this.defaultMeta.description,
                'og:title': this.defaultMeta.title,
                'og:description': this.defaultMeta.description,
                'og:image': this.getAbsoluteUrl('images/ui/deepvape_main.png')
            };
        }
        
        // 更新 title 標籤
        document.title = pageData.title || this.defaultMeta.title;
        
        // 更新 meta 標籤
        this.addOrUpdateMeta('description', pageData.description || this.defaultMeta.description);
        this.addOrUpdateMeta('keywords', pageData.keywords || this.defaultMeta.keywords);
        
        // Open Graph
        this.addOrUpdateMeta('og:title', pageData['og:title'] || pageData.title, 'property');
        this.addOrUpdateMeta('og:description', pageData['og:description'] || pageData.description, 'property');
        this.addOrUpdateMeta('og:url', window.location.href, 'property');
        this.addOrUpdateMeta('og:image', pageData['og:image'] || this.getAbsoluteUrl('images/ui/deepvape_logo_main.png'), 'property');
        this.addOrUpdateMeta('og:type', this.defaultMeta['og:type'], 'property');
        this.addOrUpdateMeta('og:site_name', this.defaultMeta['og:site_name'], 'property');
        this.addOrUpdateMeta('og:locale', this.defaultMeta['og:locale'], 'property');
        
        // Twitter Card
        this.addOrUpdateMeta('twitter:card', this.defaultMeta['twitter:card']);
        this.addOrUpdateMeta('twitter:title', pageData['og:title'] || pageData.title);
        this.addOrUpdateMeta('twitter:description', pageData['og:description'] || pageData.description);
        this.addOrUpdateMeta('twitter:image', pageData['og:image'] || this.getAbsoluteUrl('images/ui/deepvape_logo_main.png'));
        
        // Canonical URL
        this.addOrUpdateLink('canonical', window.location.href);
    }

    addResourceHints() {
        // Preconnect to external domains
        const preconnectDomains = [
            'https://cdn.jsdelivr.net',
            'https://cdnjs.cloudflare.com',
            'https://fonts.googleapis.com',
            'https://fonts.gstatic.com',
            'https://esm.sh'
        ];
        
        preconnectDomains.forEach(domain => {
            this.addLink('preconnect', domain);
            this.addLink('dns-prefetch', domain);
        });
        
        // Prefetch 關鍵資源
        const prefetchResources = [
            'js/cart-logic.js',
            'js/lazy-load.js',
            'css/common-styles.css',
            'images/ui/deepvape_logo_main.png'
        ];
        
        prefetchResources.forEach(resource => {
            this.addLink('prefetch', resource);
        });
        
        // Preload 關鍵字體
        this.addPreloadLink('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&display=swap', 'style');
    }

    addStructuredData() {
        const structuredData = {
            "@context": "https://schema.org",
            "@type": "Store",
            "name": "DeepVape",
            "description": this.defaultMeta.description,
            "url": window.location.origin,
            "logo": this.getAbsoluteUrl('images/ui/deepvape_logo_main.png'),
            "priceRange": "NT$280 - NT$1500",
            "acceptsPayments": ["現金", "信用卡", "7-11取貨付款"],
            "paymentAccepted": "Cash, Credit Card",
            "currenciesAccepted": "TWD",
            "openingHours": "Mo-Fr 09:00-18:00",
            "telephone": "0800-123-456",
            "email": "service@52012.xyz",
            "areaServed": {
                "@type": "Country",
                "name": "Taiwan"
            }
        };
        
        const script = document.createElement('script');
        script.type = 'application/ld+json';
        script.textContent = JSON.stringify(structuredData);
        document.head.appendChild(script);
    }

    // 輔助方法
    addOrUpdateMeta(name, content, attribute = 'name') {
        let meta = document.querySelector(`meta[${attribute}="${name}"]`);
        if (!meta) {
            meta = document.createElement('meta');
            meta.setAttribute(attribute, name);
            document.head.appendChild(meta);
        }
        meta.content = content;
    }

    addMeta(name, content) {
        const meta = document.createElement('meta');
        meta.name = name;
        meta.content = content;
        document.head.appendChild(meta);
    }

    addOrUpdateLink(rel, href) {
        let link = document.querySelector(`link[rel="${rel}"]`);
        if (!link) {
            link = document.createElement('link');
            link.rel = rel;
            document.head.appendChild(link);
        }
        link.href = href;
    }

    addLink(rel, href) {
        // 檢查是否已存在
        if (document.querySelector(`link[rel="${rel}"][href="${href}"]`)) {
            return;
        }
        
        const link = document.createElement('link');
        link.rel = rel;
        link.href = href;
        
        // 對於 preconnect，也加上 crossorigin
        if (rel === 'preconnect') {
            link.crossOrigin = 'anonymous';
        }
        
        document.head.appendChild(link);
    }

    addPreloadLink(href, as) {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.href = href;
        link.as = as;
        
        if (as === 'font') {
            link.crossOrigin = 'anonymous';
        }
        
        document.head.appendChild(link);
    }

    getAbsoluteUrl(path) {
        // 如果已經是絕對 URL，直接返回
        if (path.startsWith('http://') || path.startsWith('https://')) {
            return path;
        }
        
        // 構建絕對 URL
        const baseUrl = window.location.origin;
        return `${baseUrl}/${path.startsWith('/') ? path.slice(1) : path}`;
    }

    // 更新特定的 meta 標籤
    updateMeta(updates) {
        Object.entries(updates).forEach(([key, value]) => {
            if (key === 'title') {
                document.title = value;
            } else if (key.startsWith('og:')) {
                this.addOrUpdateMeta(key, value, 'property');
            } else {
                this.addOrUpdateMeta(key, value);
            }
        });
    }
}

// 自動初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.metaTags = new MetaTagsGenerator();
    });
} else {
    window.metaTags = new MetaTagsGenerator();
}

// 導出
window.MetaTagsGenerator = MetaTagsGenerator; 