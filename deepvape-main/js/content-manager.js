// 內容管理系統 - 動態載入公告和價格
class ContentManager {
    constructor() {
        this.announcements = [];
        this.prices = {};
        this.init();
    }

    async init() {
        try {
            await Promise.all([
                this.loadAnnouncements(),
                this.loadPrices()
            ]);
            this.updateUI();
        } catch (error) {
            console.error('內容載入失敗:', error);
        }
    }

    // 載入公告數據
    async loadAnnouncements() {
        try {
            const response = await fetch('/data/announcements.json');
            const data = await response.json();
            this.announcements = data.announcements.filter(announcement => {
                if (!announcement.active) return false;
                
                const now = new Date();
                const startDate = announcement.startDate ? new Date(announcement.startDate) : null;
                const endDate = announcement.endDate ? new Date(announcement.endDate) : null;
                
                if (startDate && now < startDate) return false;
                if (endDate && now > endDate) return false;
                
                return true;
            });
        } catch (error) {
            console.error('載入公告失敗:', error);
            this.announcements = [];
        }
    }

    // 載入價格數據
    async loadPrices() {
        try {
            const response = await fetch('/data/prices.json');
            const data = await response.json();
            this.prices = {};
            data.products.forEach(product => {
                this.prices[product.id] = product;
            });
        } catch (error) {
            console.error('載入價格失敗:', error);
            this.prices = {};
        }
    }

    // 更新 UI
    updateUI() {
        this.updateAnnouncements();
        this.updatePrices();
    }

    // 更新公告顯示
    updateAnnouncements() {
        const announcementElement = document.getElementById('announcement');
        const announcementText = document.getElementById('announcementText');
        
        if (!announcementElement || !announcementText) return;

        if (this.announcements.length > 0) {
            // 顯示最高優先級的公告
            const sortedAnnouncements = this.announcements.sort((a, b) => {
                const priorityOrder = { 'high': 3, 'medium': 2, 'low': 1 };
                return priorityOrder[b.priority] - priorityOrder[a.priority];
            });

            const currentAnnouncement = sortedAnnouncements[0];
            announcementText.textContent = currentAnnouncement.text;
            
            // 設置優先級樣式
            announcementElement.className = `announcement priority-${currentAnnouncement.priority}`;
            announcementElement.style.display = 'block';

            // 如果有多個公告，可以輪播顯示
            if (sortedAnnouncements.length > 1) {
                this.startAnnouncementRotation(sortedAnnouncements);
            }
        } else {
            announcementElement.style.display = 'none';
        }
    }

    // 公告輪播
    startAnnouncementRotation(announcements) {
        let currentIndex = 0;
        const announcementText = document.getElementById('announcementText');
        const announcementElement = document.getElementById('announcement');

        setInterval(() => {
            currentIndex = (currentIndex + 1) % announcements.length;
            const announcement = announcements[currentIndex];
            
            announcementText.textContent = announcement.text;
            announcementElement.className = `announcement priority-${announcement.priority}`;
        }, 5000); // 每5秒切換一次
    }

    // 更新價格顯示
    updatePrices() {
        // 更新所有產品價格
        Object.keys(this.prices).forEach(productId => {
            const product = this.prices[productId];
            const priceElements = document.querySelectorAll(`[data-product-id="${productId}"] .product-price`);
            
            priceElements.forEach(element => {
                if (product.originalPrice && product.originalPrice > product.price) {
                    element.innerHTML = `
                        NT$ ${product.price}
                        <small>NT$ ${product.originalPrice}</small>
                    `;
                } else {
                    element.textContent = `NT$ ${product.price}`;
                }
            });

            // 更新折扣標籤
            if (product.discount) {
                const discountElements = document.querySelectorAll(`[data-product-id="${productId}"] .discount-badge`);
                discountElements.forEach(element => {
                    element.textContent = product.discount;
                    element.style.display = 'inline-block';
                });
            }
        });
    }

    // 獲取產品價格
    getPrice(productId) {
        return this.prices[productId]?.price || 0;
    }

    // 獲取當前公告
    getCurrentAnnouncements() {
        return this.announcements;
    }
}

// 全域實例
window.contentManager = new ContentManager();

// 關閉公告功能
function closeAnnouncement() {
    const announcementElement = document.getElementById('announcement');
    if (announcementElement) {
        announcementElement.style.display = 'none';
        // 保存用戶關閉狀態到 localStorage
        localStorage.setItem('announcementClosed', 'true');
    }
}

// 檢查用戶是否已關閉公告
function checkAnnouncementStatus() {
    const isClosed = localStorage.getItem('announcementClosed');
    if (isClosed === 'true') {
        const announcementElement = document.getElementById('announcement');
        if (announcementElement) {
            announcementElement.style.display = 'none';
        }
    }
}

// 頁面載入時檢查公告狀態
document.addEventListener('DOMContentLoaded', checkAnnouncementStatus); 