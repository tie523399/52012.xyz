/**
 * DeepVape 共享元件庫
 * 整合所有頁面通用的功能和元件
 */

// 全域命名空間
window.DeepVapeComponents = window.DeepVapeComponents || {};

/**
 * 通用 Header 元件
 */
DeepVapeComponents.createHeader = function(options = {}) {
    const defaults = {
        showCart: true,
        showHome: true,
        logoLink: 'index.html',
        cartLink: 'cart.html'
    };
    
    const config = { ...defaults, ...options };
    
    return `
        <header>
            <div class="header-container">
                <div class="logo">
                    <a href="${config.logoLink}" class="logo-button vfx-logo" id="navLogo">
                        <span class="logo-text">DeepVape</span>
                    </a>
                </div>
                <div class="header-actions">
                    ${config.showCart ? `
                    <a href="${config.cartLink}" class="cart-button">
                        <i class="fas fa-shopping-cart"></i>
                        <span class="cart-count">0</span>
                    </a>
                    ` : ''}
                    ${config.showHome ? `
                    <a href="${config.logoLink}" class="back-button">
                        <i class="fas fa-home"></i>
                    </a>
                    ` : ''}
                </div>
            </div>
        </header>
    `;
};

/**
 * 通用 Footer 元件
 */
DeepVapeComponents.createFooter = function() {
    return `
        <footer class="site-footer">
            <div class="footer-content">
                <div class="footer-section">
                    <h4>關於我們</h4>
                    <ul>
                        <li><a href="pages/brand_story.html">品牌故事</a></li>
                        <li><a href="pages/shopping_guide.html">購物指南</a></li>
                        <li><a href="pages/faq.html">常見問題</a></li>
                    </ul>
                </div>
                <div class="footer-section">
                    <h4>產品系列</h4>
                    <ul>
                        <li><a href="index.html#hosts">主機系列</a></li>
                        <li><a href="index.html#pods">煙彈系列</a></li>
                        <li><a href="index.html#disposable">拋棄式系列</a></li>
                    </ul>
                </div>
                <div class="footer-section">
                    <h4>客戶服務</h4>
                    <ul>
                        <li><a href="pages/shipping_info.html">配送說明</a></li>
                        <li><a href="pages/return_policy.html">退換貨政策</a></li>
                        <li><a href="cart.html">購物車</a></li>
                    </ul>
                </div>
                <div class="footer-section">
                    <h4>聯絡我們</h4>
                    <div class="social-links">
                        <a href="#" class="social-link"><i class="fab fa-facebook"></i></a>
                        <a href="#" class="social-link"><i class="fab fa-instagram"></i></a>
                        <a href="#" class="social-link"><i class="fab fa-line"></i></a>
                        <a href="#" class="social-link"><i class="fab fa-telegram"></i></a>
                    </div>
                    <p class="contact-info">
                        <i class="fas fa-envelope"></i> service@52012.xyz<br>
                        <i class="fas fa-phone"></i> 0800-123-456
                    </p>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; ${new Date().getFullYear()} DeepVape. All rights reserved.</p>
                <p class="warning-text">
                    <i class="fas fa-exclamation-triangle"></i>
                    未滿18歲請勿使用本產品
                </p>
            </div>
        </footer>
    `;
};

/**
 * VFX Logo 效果初始化
 */
DeepVapeComponents.initVFXLogo = function() {
    const logos = document.querySelectorAll('.vfx-logo');
    
    logos.forEach(logo => {
        // 添加發光效果
        logo.addEventListener('mouseenter', function() {
            this.style.textShadow = '0 0 20px #1afe49, 0 0 40px #1afe49';
        });
        
        logo.addEventListener('mouseleave', function() {
            this.style.textShadow = '0 0 10px #1afe49';
        });
        
        // 初始發光
        logo.style.textShadow = '0 0 10px #1afe49';
        logo.style.transition = 'all 0.3s ease';
    });
};

/**
 * Pulse Button 動畫效果
 */
DeepVapeComponents.initPulseButtons = function() {
    const pulseButtons = document.querySelectorAll('.pulse-button');
    
    pulseButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // 創建漣漪效果
            const ripple = document.createElement('span');
            ripple.classList.add('ripple');
            
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            
            this.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    });
};

/**
 * 購物車數量更新
 */
DeepVapeComponents.updateCartCount = function() {
    const cart = JSON.parse(localStorage.getItem('cart') || '[]');
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    
    const cartCounts = document.querySelectorAll('.cart-count');
    cartCounts.forEach(count => {
        count.textContent = totalItems;
        count.style.display = totalItems > 0 ? 'inline-block' : 'none';
    });
};

/**
 * 共享的圖片懶加載功能
 */
DeepVapeComponents.initLazyLoading = function() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.add('lazy-loaded');
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
};

/**
 * 共享的滾動動畫
 */
DeepVapeComponents.initScrollAnimations = function() {
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    
    const animationObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
            }
        });
    }, { threshold: 0.1 });
    
    animatedElements.forEach(el => animationObserver.observe(el));
};

/**
 * 產品卡片元件
 */
DeepVapeComponents.createProductCard = function(product) {
    return `
        <div class="product-card" data-product-id="${product.id}">
            <div class="product-image-container">
                <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 300'%3E%3Crect width='400' height='300' fill='%23f0f0f0'/%3E%3C/svg%3E" 
                     data-src="${product.image}" 
                     alt="${product.name}" 
                     class="product-image"
                     loading="lazy">
                ${product.badge ? `<span class="product-badge">${product.badge}</span>` : ''}
            </div>
            <div class="product-info">
                <h3 class="product-name">${product.name}</h3>
                <p class="product-description">${product.description}</p>
                <div class="product-price">NT$ ${product.price}</div>
                <button class="pulse-button add-to-cart-btn" 
                        data-product-id="${product.id}"
                        data-product-name="${product.name}"
                        data-product-price="${product.price}"
                        data-product-image="${product.image}">
                    <i class="fas fa-shopping-cart"></i> 加入購物車
                </button>
            </div>
        </div>
    `;
};

/**
 * 通用的加入購物車功能
 */
DeepVapeComponents.addToCart = function(productData) {
    let cart = JSON.parse(localStorage.getItem('cart') || '[]');
    
    const existingIndex = cart.findIndex(item => 
        item.id === productData.id && 
        (!productData.color || item.color === productData.color) &&
        (!productData.flavor || item.flavor === productData.flavor)
    );
    
    if (existingIndex > -1) {
        cart[existingIndex].quantity += productData.quantity || 1;
    } else {
        cart.push({
            ...productData,
            quantity: productData.quantity || 1
        });
    }
    
    localStorage.setItem('cart', JSON.stringify(cart));
    DeepVapeComponents.updateCartCount();
    
    // 顯示成功訊息
    DeepVapeComponents.showNotification(`已將 ${productData.name} 加入購物車！`, 'success');
};

/**
 * 通知系統
 */
DeepVapeComponents.showNotification = function(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-info-circle'}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    // 動畫顯示
    setTimeout(() => notification.classList.add('show'), 10);
    
    // 3秒後移除
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
};

/**
 * 初始化所有共享元件
 */
DeepVapeComponents.init = function() {
    // 初始化 VFX 效果
    DeepVapeComponents.initVFXLogo();
    
    // 初始化按鈕動畫
    DeepVapeComponents.initPulseButtons();
    
    // 更新購物車數量
    DeepVapeComponents.updateCartCount();
    
    // 初始化懶加載
    DeepVapeComponents.initLazyLoading();
    
    // 初始化滾動動畫
    DeepVapeComponents.initScrollAnimations();
    
    // 綁定加入購物車按鈕
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('add-to-cart-btn') || 
            e.target.closest('.add-to-cart-btn')) {
            const btn = e.target.classList.contains('add-to-cart-btn') ? 
                        e.target : e.target.closest('.add-to-cart-btn');
            
            const productData = {
                id: btn.dataset.productId,
                name: btn.dataset.productName,
                price: parseFloat(btn.dataset.productPrice),
                image: btn.dataset.productImage
            };
            
            DeepVapeComponents.addToCart(productData);
        }
    });
};

// DOM 載入完成後自動初始化
document.addEventListener('DOMContentLoaded', DeepVapeComponents.init);

// 導出到全域
window.DeepVape = DeepVapeComponents; 