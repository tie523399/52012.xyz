// DeepVape 共用元件系統

class CommonComponents {
    constructor() {
        this.componentsLoaded = false;
        this.cartCount = 0;
        this.updateCartCount();
    }

    // 創建導航列元件 - 支援多種樣式
    createNavbar(style = 'default') {
        if (style === 'minimal') {
            return this.createMinimalNavbar();
        } else if (style === 'modern') {
            return this.createModernNavbar();
        }
        return this.createDefaultNavbar();
    }

    // 預設導航列（Bootstrap 樣式）
    createDefaultNavbar() {
        return `
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark sticky-top">
            <div class="container-fluid">
                <a class="navbar-brand" href="index.html">
                    <img src="images/ui/deepvape_logo_main.png" alt="深煙電子煙" height="40" class="me-2">
                    DeepVape
                </a>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav ms-auto">
                        <li class="nav-item"><a class="nav-link" href="index.html">首頁</a></li>
                        <li class="nav-item dropdown">
                            <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">產品</a>
                            <ul class="dropdown-menu">
                                <li><a class="dropdown-item" href="sp2_product.html">SP2 主機</a></li>
                                <li><a class="dropdown-item" href="ilia_1_product.html">ILIA 一代</a></li>
                                <li><a class="dropdown-item" href="hta_vape_product.html">HTA 黑桃</a></li>
                                <li><hr class="dropdown-divider"></li>
                                <li><a class="dropdown-item" href="sp2_pods_product.html">SP2 煙彈</a></li>
                                <li><a class="dropdown-item" href="ilia_pods_product.html">ILIA 煙彈</a></li>
                            </ul>
                        </li>
                        <li class="nav-item"><a class="nav-link" href="pages/shopping_guide.html">購物指南</a></li>
                        <li class="nav-item">
                            <a class="nav-link" href="cart.html">
                                <i class="fas fa-shopping-cart"></i> 購物車
                                <span class="badge bg-danger cart-count">${this.cartCount}</span>
                            </a>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>`;
    }

    // 簡約風格導航列（產品頁樣式）
    createMinimalNavbar() {
        return `
        <header>
            <div class="header-container">
                <div class="logo">
                    <a href="index.html" class="logo-button vfx-logo" id="navLogo">
                        <span class="logo-text">DeepVape</span>
                    </a>
                </div>
                <div class="header-actions">
                    <a href="cart.html" class="cart-button">
                        <i class="fas fa-shopping-cart"></i>
                        <span class="cart-count badge">${this.cartCount}</span>
                    </a>
                    <a href="index.html" class="back-button">
                        <i class="fas fa-home"></i>
                    </a>
                </div>
            </div>
        </header>`;
    }

    // 現代風格導航列（深色主題）
    createModernNavbar() {
        return `
        <header class="header" id="navbar">
            <nav class="nav-container">
                <img src="images/ui/deepvape_logo_main.png" alt="深煙電子煙" class="logo vfx-logo">
                <ul class="nav-links">
                    <li><a href="index.html"><i class="fas fa-home"></i> 首頁</a></li>
                    <li><a href="index.html#hosts"><i class="fas fa-microchip"></i> 主機</a></li>
                    <li><a href="index.html#pods"><i class="fas fa-capsules"></i> 煙彈</a></li>
                    <li><a href="index.html#disposable"><i class="fas fa-trash-alt"></i> 拋棄式</a></li>
                    <li>
                        <a href="cart.html">
                            <i class="fas fa-shopping-cart"></i> 購物車
                            <span class="cart-count">${this.cartCount}</span>
                        </a>
                    </li>
                </ul>
            </nav>
        </header>`;
    }

    // 創建頁尾元件 - 支援多種樣式
    createFooter(style = 'default') {
        const currentYear = new Date().getFullYear();
        
        if (style === 'minimal') {
            return `
            <footer class="footer-minimal">
                <div class="container text-center py-3">
                    <p>&copy; ${currentYear} DeepVape. All rights reserved.</p>
                </div>
            </footer>`;
        }

        return `
        <footer class="bg-dark text-white py-5 mt-5">
            <div class="container">
                <div class="row">
                    <div class="col-md-4">
                        <h5>關於 DeepVape</h5>
                        <p>台灣領先的電子煙品牌，提供高品質的電子煙產品和優質的客戶服務。</p>
                        <div class="social-links mt-3">
                            <a href="#" class="text-white me-3"><i class="fab fa-facebook-f"></i></a>
                            <a href="#" class="text-white me-3"><i class="fab fa-instagram"></i></a>
                            <a href="#" class="text-white me-3"><i class="fab fa-line"></i></a>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <h5>快速連結</h5>
                        <ul class="list-unstyled">
                            <li><a href="pages/shopping_guide.html" class="text-white-50">購物指南</a></li>
                            <li><a href="pages/shipping_info.html" class="text-white-50">配送資訊</a></li>
                            <li><a href="pages/return_policy.html" class="text-white-50">退換貨政策</a></li>
                            <li><a href="pages/faq.html" class="text-white-50">常見問題</a></li>
                            <li><a href="pages/brand_story.html" class="text-white-50">品牌故事</a></li>
                        </ul>
                    </div>
                    <div class="col-md-4">
                        <h5>聯絡我們</h5>
                        <p><i class="fas fa-envelope"></i> service@52012.xyz<br>
                           <i class="fas fa-clock"></i> 週一至週五 9:00-18:00<br>
                           <i class="fas fa-phone"></i> 0800-123-456</p>
                        <div class="mt-3">
                            <img src="images/ui/7-11_tklogo.jpg" alt="7-11 取貨" height="40" class="me-2">
                            <span class="text-white-50">支援 7-11 取貨付款</span>
                        </div>
                    </div>
                </div>
                <hr class="my-4">
                <div class="text-center">
                    <p>&copy; ${currentYear} DeepVape. All rights reserved. | 
                       <a href="#" class="text-white-50">隱私政策</a> | 
                       <a href="#" class="text-white-50">使用條款</a>
                    </p>
                    <p class="text-warning small">
                        <i class="fas fa-exclamation-triangle"></i> 
                        本產品僅供 18 歲以上成年人使用
                    </p>
                </div>
            </div>
        </footer>`;
    }

    // 創建產品卡片元件
    createProductCard(product) {
        return `
        <div class="col-md-4 mb-4">
            <div class="card h-100 product-card">
                <div class="card-img-wrapper">
                    <img src="${product.image}" class="card-img-top" alt="${product.name}">
                    ${product.badge ? `<span class="product-badge">${product.badge}</span>` : ''}
                </div>
                <div class="card-body">
                    <h5 class="card-title">${product.name}</h5>
                    <p class="card-text">${product.description}</p>
                    <p class="text-primary fw-bold">NT$ ${product.price}</p>
                    <a href="${product.link}" class="btn btn-primary w-100">查看詳情</a>
                </div>
            </div>
        </div>`;
    }

    // 更新購物車數量
    updateCartCount() {
        const cart = JSON.parse(localStorage.getItem('cart') || '[]');
        this.cartCount = cart.reduce((sum, item) => sum + (item.quantity || 1), 0);
        
        // 更新所有購物車計數元素
        document.querySelectorAll('.cart-count').forEach(el => {
            el.textContent = this.cartCount;
        });
    }

    // 添加滾動效果
    addScrollEffects() {
        const navbar = document.getElementById('navbar');
        if (!navbar) return;

        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    // 載入所有元件到頁面
    loadComponents(options = {}) {
        const {
            navbarStyle = 'default',
            footerStyle = 'default',
            includeVFX = true
        } = options;

        // 載入導航列
        const navbarPlaceholder = document.getElementById('navbar-placeholder');
        if (navbarPlaceholder) {
            navbarPlaceholder.innerHTML = this.createNavbar(navbarStyle);
        }

        // 載入頁尾
        const footerPlaceholder = document.getElementById('footer-placeholder');
        if (footerPlaceholder) {
            footerPlaceholder.innerHTML = this.createFooter(footerStyle);
        }

        // 添加滾動效果
        this.addScrollEffects();

        // 載入 VFX 效果
        if (includeVFX && window.VFXEffects) {
            window.VFXEffects.initializeVFXEffects();
        }

        // 監聽購物車變化
        window.addEventListener('storage', (e) => {
            if (e.key === 'cart') {
                this.updateCartCount();
            }
        });

        this.componentsLoaded = true;
    }

    // 初始化元件系統
    init(options = {}) {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.loadComponents(options));
        } else {
            this.loadComponents(options);
        }
    }
}

// 創建全域實例
window.commonComponents = new CommonComponents();
window.commonComponents.init(); 