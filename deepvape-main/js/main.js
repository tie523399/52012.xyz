// DeepVape 主要 JavaScript 檔案
// 移除 import 語句，改為在 HTML 中引入 CSS

// 初始化 AOS 動畫
function initAOS() {
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,
            easing: 'ease-in-out',
            once: true,
            offset: 100
        });
    }
}

// 平滑滾動功能
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// 圖片延遲載入
function initLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));
}

// 產品圖片切換功能
function initProductGallery() {
    const galleryImages = document.querySelectorAll('.gallery-image');
    const mainImage = document.getElementById('mainImage');

    if (galleryImages.length > 0 && mainImage) {
        galleryImages.forEach(img => {
            img.addEventListener('click', function() {
                // 移除所有 active 類別
                galleryImages.forEach(i => i.classList.remove('active'));
                // 添加 active 到當前圖片
                this.classList.add('active');
                // 更換主圖片
                mainImage.src = this.src;
                mainImage.alt = this.alt;
            });
        });
    }
}

// 數量選擇器功能
function initQuantitySelector() {
    const quantityInputs = document.querySelectorAll('.quantity-input');
    
    quantityInputs.forEach(input => {
        const decreaseBtn = input.previousElementSibling;
        const increaseBtn = input.nextElementSibling;
        
        if (decreaseBtn) {
            decreaseBtn.addEventListener('click', () => {
                const currentValue = parseInt(input.value) || 1;
                if (currentValue > 1) {
                    input.value = currentValue - 1;
                    input.dispatchEvent(new Event('change'));
                }
            });
        }
        
        if (increaseBtn) {
            increaseBtn.addEventListener('click', () => {
                const currentValue = parseInt(input.value) || 1;
                input.value = currentValue + 1;
                input.dispatchEvent(new Event('change'));
            });
        }
    });
}

// 載入產品資料
async function loadProducts() {
    try {
        const response = await fetch('/data/prices.json');
        if (!response.ok) throw new Error('無法載入產品資料');
        
        const products = await response.json();
        return products;
    } catch (error) {
        console.error('載入產品失敗：', error);
        return [];
    }
}

// 載入公告資料
async function loadAnnouncements() {
    try {
        const response = await fetch('/data/announcements.json');
        if (!response.ok) throw new Error('無法載入公告資料');
        
        const announcements = await response.json();
        displayAnnouncements(announcements);
    } catch (error) {
        console.error('載入公告失敗：', error);
    }
}

// 顯示公告
function displayAnnouncements(announcements) {
    const announcementContainer = document.getElementById('announcement-container');
    if (!announcementContainer || !announcements.active) return;

    const activeAnnouncements = announcements.items.filter(item => item.active);
    if (activeAnnouncements.length === 0) return;

    const announcement = activeAnnouncements[0];
    announcementContainer.innerHTML = `
        <div class="alert alert-${announcement.type} alert-dismissible fade show" role="alert">
            <strong>${announcement.title}</strong> ${announcement.message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    announcementContainer.style.display = 'block';
}

// 初始化所有功能
function initializeApp() {
    initAOS();
    initSmoothScroll();
    initLazyLoading();
    initProductGallery();
    initQuantitySelector();
    loadAnnouncements();
}

// DOM 載入完成後初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}

// 將函數掛載到全域物件供其他模組使用
window.DeepVapeMain = {
    loadProducts,
    initProductGallery,
    initQuantitySelector,
    initializeApp
}; 