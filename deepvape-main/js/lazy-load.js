/**
 * DeepVape 圖片延遲載入系統
 * 使用 Intersection Observer API 實現高效能的圖片載入
 */

class LazyImageLoader {
    constructor(options = {}) {
        this.options = {
            rootMargin: '50px 0px',
            threshold: 0.01,
            loadingClass: 'lazy-loading',
            loadedClass: 'lazy-loaded',
            errorClass: 'lazy-error',
            ...options
        };
        
        this.imageObserver = null;
        this.init();
    }

    init() {
        // 檢查瀏覽器支援
        if (!('IntersectionObserver' in window)) {
            console.warn('IntersectionObserver not supported, loading all images immediately');
            this.loadAllImages();
            return;
        }

        // 建立觀察器
        this.imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.loadImage(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, {
            rootMargin: this.options.rootMargin,
            threshold: this.options.threshold
        });

        // 開始觀察所有延遲載入的圖片
        this.observeImages();

        // 監聽動態新增的圖片
        this.setupMutationObserver();
    }

    observeImages() {
        const lazyImages = document.querySelectorAll('img[data-src], img[data-lazy]');
        lazyImages.forEach(img => {
            // 添加載入中的樣式
            img.classList.add(this.options.loadingClass);
            
            // 設置預設佔位圖
            if (!img.src) {
                img.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300"%3E%3Crect width="400" height="300" fill="%23f0f0f0"/%3E%3Ctext x="50%25" y="50%25" text-anchor="middle" dy=".3em" fill="%23999" font-family="sans-serif" font-size="20"%3E載入中...%3C/text%3E%3C/svg%3E';
            }
            
            this.imageObserver.observe(img);
        });
    }

    loadImage(img) {
        const src = img.dataset.src || img.dataset.lazy;
        const srcset = img.dataset.srcset;
        
        if (!src) return;

        // 預載圖片
        const tempImg = new Image();
        
        tempImg.onload = () => {
            // 成功載入
            img.src = src;
            if (srcset) {
                img.srcset = srcset;
            }
            
            img.classList.remove(this.options.loadingClass);
            img.classList.add(this.options.loadedClass);
            
            // 淡入效果
            this.fadeIn(img);
            
            // 清理 data 屬性
            delete img.dataset.src;
            delete img.dataset.lazy;
            delete img.dataset.srcset;
            
            // 觸發自定義事件
            img.dispatchEvent(new CustomEvent('lazyloaded', {
                detail: { src }
            }));
        };
        
        tempImg.onerror = () => {
            // 載入失敗
            img.classList.remove(this.options.loadingClass);
            img.classList.add(this.options.errorClass);
            
            // 使用錯誤佔位圖
            img.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300"%3E%3Crect width="400" height="300" fill="%23ffebee"/%3E%3Ctext x="50%25" y="50%25" text-anchor="middle" dy=".3em" fill="%23f44336" font-family="sans-serif" font-size="20"%3E載入失敗%3C/text%3E%3C/svg%3E';
            
            console.error(`Failed to load image: ${src}`);
        };
        
        // 開始載入
        tempImg.src = src;
    }

    fadeIn(img) {
        img.style.opacity = '0';
        img.style.transition = 'opacity 0.3s ease-in-out';
        
        // 強制重繪
        img.offsetHeight;
        
        img.style.opacity = '1';
    }

    setupMutationObserver() {
        // 監聽 DOM 變化，自動處理新增的圖片
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1) { // Element node
                        if (node.tagName === 'IMG' && (node.dataset.src || node.dataset.lazy)) {
                            node.classList.add(this.options.loadingClass);
                            this.imageObserver.observe(node);
                        }
                        
                        // 檢查子元素
                        const lazyImages = node.querySelectorAll?.('img[data-src], img[data-lazy]');
                        lazyImages?.forEach(img => {
                            img.classList.add(this.options.loadingClass);
                            this.imageObserver.observe(img);
                        });
                    }
                });
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    // 降級方案：立即載入所有圖片
    loadAllImages() {
        const lazyImages = document.querySelectorAll('img[data-src], img[data-lazy]');
        lazyImages.forEach(img => {
            const src = img.dataset.src || img.dataset.lazy;
            if (src) {
                img.src = src;
                if (img.dataset.srcset) {
                    img.srcset = img.dataset.srcset;
                }
            }
        });
    }

    // 手動載入特定圖片
    loadImageManually(img) {
        if (this.imageObserver) {
            this.imageObserver.unobserve(img);
        }
        this.loadImage(img);
    }

    // 銷毀觀察器
    destroy() {
        if (this.imageObserver) {
            this.imageObserver.disconnect();
        }
    }
}

// 自動初始化
let lazyLoader;
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        lazyLoader = new LazyImageLoader();
    });
} else {
    lazyLoader = new LazyImageLoader();
}

// 導出給全域使用
window.LazyImageLoader = LazyImageLoader;
window.lazyLoader = lazyLoader; 