// DeepVape 購物車管理系統 - 觀察者模式架構

class CartManager {
    constructor() {
        this.cart = this.loadCart();
        this.observers = [];
        this.version = '2.0.0';
        this.storageKey = 'deepvape_cart';
        this.init();
    }

    // === 觀察者模式實現 ===
    subscribe(observer) {
        this.observers.push(observer);
        return () => {
            this.observers = this.observers.filter(obs => obs !== observer);
        };
    }

    notify(event, data) {
        this.observers.forEach(observer => {
            if (typeof observer === 'function') {
                observer({ event, data });
            } else if (observer[event]) {
                observer[event](data);
            }
        });
    }

    // === 核心購物車操作 ===
    addItem(product) {
        if (!product || !product.id) {
            console.error('Invalid product data');
            return false;
        }

        // 建立唯一識別碼（包含變體）
        const uniqueId = this.generateUniqueId(product);
        
        // 檢查是否已存在
        const existingIndex = this.cart.findIndex(item => 
            this.generateUniqueId(item) === uniqueId
        );

        if (existingIndex >= 0) {
            // 更新數量
            this.cart[existingIndex].quantity += (product.quantity || 1);
            this.notify('itemUpdated', {
                item: this.cart[existingIndex],
                index: existingIndex
            });
        } else {
            // 新增項目
            const newItem = {
                ...product,
                quantity: product.quantity || 1,
                uniqueId: uniqueId,
                addedAt: new Date().toISOString()
            };
            this.cart.push(newItem);
            this.notify('itemAdded', { item: newItem });
        }

        this.persist();
        this.notify('cartChanged', { cart: this.cart });
        return true;
    }

    updateQuantity(index, newQuantity) {
        // 邊界檢查
        if (index < 0 || index >= this.cart.length) {
            console.error('Invalid cart index');
            return false;
        }

        newQuantity = parseInt(newQuantity);
        if (isNaN(newQuantity) || newQuantity < 0) {
            console.error('Invalid quantity');
            return false;
        }

        if (newQuantity === 0) {
            return this.removeItem(index);
        }

        // 更新數量
        const oldQuantity = this.cart[index].quantity;
        this.cart[index].quantity = newQuantity;
        
        // 持久化並通知
        this.persist();
        this.notify('quantityChanged', {
            index,
            item: this.cart[index],
            oldQuantity,
            newQuantity
        });
        this.notify('cartChanged', { cart: this.cart });
        
        return true;
    }

    removeItem(index) {
        // 安全移除檢查
        if (index < 0 || index >= this.cart.length) {
            console.error('Invalid cart index');
            return false;
        }

        const removedItem = this.cart.splice(index, 1)[0];
        
        // 更新儲存
        this.persist();
        
        // 廣播變更
        this.notify('itemRemoved', { item: removedItem, index });
        this.notify('cartChanged', { cart: this.cart });
        
        return true;
    }

    calculateTotals() {
        const subtotal = this.cart.reduce((sum, item) => {
            const price = parseFloat(item.price) || 0;
            const quantity = parseInt(item.quantity) || 0;
            return sum + (price * quantity);
        }, 0);

        // 運費邏輯（可根據需求調整）
        const freeShippingThreshold = 1000;
        const shippingFee = 60;
        const shipping = subtotal >= freeShippingThreshold ? 0 : shippingFee;
        
        const total = subtotal + shipping;

        // 回傳結構化資料
        return {
            subtotal: Math.round(subtotal * 100) / 100,
            shipping: shipping,
            total: Math.round(total * 100) / 100,
            itemCount: this.cart.reduce((sum, item) => sum + item.quantity, 0),
            isFreeShipping: shipping === 0,
            freeShippingThreshold: freeShippingThreshold
        };
    }

    // === 持久化策略 ===
    persist() {
        try {
            const data = {
                version: this.version,
                items: this.cart,
                lastModified: new Date().toISOString()
            };
            
            // 智能儲存策略 - 壓縮大型購物車
            const serialized = JSON.stringify(data);
            if (serialized.length > 5000) {
                // 簡化資料結構
                data.items = this.cart.map(item => ({
                    id: item.id,
                    name: item.name,
                    price: item.price,
                    quantity: item.quantity,
                    image: item.image,
                    flavor: item.flavor,
                    color: item.color,
                    uniqueId: item.uniqueId
                }));
            }
            
            localStorage.setItem(this.storageKey, JSON.stringify(data));
            return true;
        } catch (error) {
            console.error('Failed to persist cart:', error);
            this.notify('persistError', { error });
            return false;
        }
    }

    loadCart() {
        try {
            const stored = localStorage.getItem(this.storageKey);
            if (!stored) return [];
            
            const data = JSON.parse(stored);
            
            // 版本控制 - 處理舊版本資料
            if (!data.version || data.version < this.version) {
                return this.migrateCart(data);
            }
            
            return data.items || [];
        } catch (error) {
            console.error('Failed to load cart:', error);
            return [];
        }
    }

    // === 輔助方法 ===
    generateUniqueId(product) {
        const parts = [product.id];
        if (product.flavor) parts.push(product.flavor);
        if (product.color) parts.push(product.color);
        if (product.variant) parts.push(product.variant);
        return parts.join('_');
    }

    migrateCart(oldData) {
        // 處理舊版本購物車資料
        if (Array.isArray(oldData)) {
            return oldData;
        }
        return oldData.items || [];
    }

    clearCart() {
        this.cart = [];
        this.persist();
        this.notify('cartCleared', {});
        this.notify('cartChanged', { cart: this.cart });
    }

    getItem(index) {
        return this.cart[index] || null;
    }

    getCart() {
        return [...this.cart]; // 返回副本避免直接修改
    }

    getItemCount() {
        return this.cart.reduce((sum, item) => sum + item.quantity, 0);
    }

    // === UI 輔助方法 ===
    formatCurrency(amount) {
        return `NT$ ${amount.toLocaleString('zh-TW')}`;
    }

    validateProduct(product) {
        const required = ['id', 'name', 'price'];
        return required.every(field => product[field] !== undefined);
    }

    // === 初始化 ===
    init() {
        // 監聽其他頁籤的購物車變更
        window.addEventListener('storage', (e) => {
            if (e.key === this.storageKey) {
                this.cart = this.loadCart();
                this.notify('cartSynced', { cart: this.cart });
                this.notify('cartChanged', { cart: this.cart });
            }
        });

        // 定期清理過期項目（30天）
        this.cleanupOldItems();
    }

    cleanupOldItems() {
        const thirtyDaysAgo = new Date();
        thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
        
        const cleaned = this.cart.filter(item => {
            if (!item.addedAt) return true;
            return new Date(item.addedAt) > thirtyDaysAgo;
        });

        if (cleaned.length < this.cart.length) {
            this.cart = cleaned;
            this.persist();
            this.notify('cartCleaned', { 
                removed: this.cart.length - cleaned.length 
            });
        }
    }
}

// === 購物車 UI 控制器 ===
class CartUIController {
    constructor(cartManager) {
        this.cartManager = cartManager;
        this.elements = {};
        this.init();
    }

    init() {
        this.cacheElements();
        this.bindEvents();
        this.subscribeToCart();
        this.render();
    }

    cacheElements() {
        this.elements = {
            cartItems: document.getElementById('cart-items'),
            cartCount: document.querySelectorAll('.cart-count'),
            subtotal: document.getElementById('subtotal'),
            shipping: document.getElementById('shipping'),
            total: document.getElementById('total'),
            emptyMessage: document.getElementById('empty-cart-message'),
            checkoutBtn: document.getElementById('checkout-btn')
        };
    }

    bindEvents() {
        // 結帳按鈕
        if (this.elements.checkoutBtn) {
            this.elements.checkoutBtn.addEventListener('click', () => {
                this.handleCheckout();
            });
        }

        // 全域購物車按鈕點擊
        document.addEventListener('click', (e) => {
            if (e.target.matches('.add-to-cart')) {
                e.preventDefault();
                this.handleAddToCart(e.target);
            }
        });
    }

    subscribeToCart() {
        this.cartManager.subscribe({
            cartChanged: () => this.render(),
            itemAdded: (data) => this.showNotification('商品已加入購物車', 'success'),
            itemRemoved: (data) => this.showNotification('商品已移除', 'info'),
            quantityChanged: (data) => this.updateItemDisplay(data.index)
        });
    }

    render() {
        this.renderCartItems();
        this.updateTotals();
        this.updateCartCount();
    }

    renderCartItems() {
        const container = this.elements.cartItems;
        if (!container) return;

        const cart = this.cartManager.getCart();
        
        if (cart.length === 0) {
            container.innerHTML = `
                <div class="empty-cart text-center py-5">
                    <i class="fas fa-shopping-cart fa-4x text-muted mb-4"></i>
                    <h3>購物車是空的</h3>
                    <p class="text-muted">趕快去選購您喜歡的商品吧！</p>
                    <a href="/" class="btn btn-primary mt-3">繼續購物</a>
                </div>
            `;
            return;
        }

        container.innerHTML = cart.map((item, index) => `
            <div class="cart-item" data-index="${index}">
                <div class="row align-items-center">
                    <div class="col-md-2 col-sm-3">
                        <img src="${item.image}" alt="${item.name}" class="img-fluid rounded">
                    </div>
                    <div class="col-md-4 col-sm-9">
                        <h5 class="mb-1">${item.name}</h5>
                        ${item.flavor ? `<small class="text-muted">口味：${item.flavor}</small><br>` : ''}
                        ${item.color ? `<small class="text-muted">顏色：${item.color}</small>` : ''}
                    </div>
                    <div class="col-md-2 col-sm-4 mt-2 mt-md-0">
                        <span class="text-muted">單價</span><br>
                        <strong>${this.cartManager.formatCurrency(item.price)}</strong>
                    </div>
                    <div class="col-md-2 col-sm-4 mt-2 mt-md-0">
                        <label class="text-muted mb-1">數量</label>
                        <div class="quantity-control d-flex align-items-center">
                            <button class="btn btn-sm btn-outline-secondary" onclick="cartUI.changeQuantity(${index}, -1)">
                                <i class="fas fa-minus"></i>
                            </button>
                            <input type="number" class="form-control mx-2 text-center" 
                                   value="${item.quantity}" 
                                   onchange="cartUI.updateQuantity(${index}, this.value)"
                                   style="width: 60px;">
                            <button class="btn btn-sm btn-outline-secondary" onclick="cartUI.changeQuantity(${index}, 1)">
                                <i class="fas fa-plus"></i>
                            </button>
                        </div>
                    </div>
                    <div class="col-md-2 col-sm-4 mt-2 mt-md-0 text-end">
                        <span class="text-muted">小計</span><br>
                        <strong>${this.cartManager.formatCurrency(item.price * item.quantity)}</strong><br>
                        <button class="btn btn-sm btn-link text-danger p-0 mt-1" onclick="cartUI.removeItem(${index})">
                            <i class="fas fa-trash"></i> 移除
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    updateTotals() {
        const totals = this.cartManager.calculateTotals();
        
        if (this.elements.subtotal) {
            this.elements.subtotal.textContent = this.cartManager.formatCurrency(totals.subtotal);
        }
        
        if (this.elements.shipping) {
            this.elements.shipping.textContent = totals.isFreeShipping ? 
                '免運費' : this.cartManager.formatCurrency(totals.shipping);
        }
        
        if (this.elements.total) {
            this.elements.total.textContent = this.cartManager.formatCurrency(totals.total);
        }

        // 更新運費提示
        if (!totals.isFreeShipping && totals.subtotal > 0) {
            const remaining = totals.freeShippingThreshold - totals.subtotal;
            if (remaining > 0 && remaining < 500) {
                this.showNotification(
                    `再消費 ${this.cartManager.formatCurrency(remaining)} 即可享免運費！`,
                    'info'
                );
            }
        }
    }

    updateCartCount() {
        const count = this.cartManager.getItemCount();
        this.elements.cartCount.forEach(el => {
            el.textContent = count;
            el.style.display = count > 0 ? 'inline-block' : 'none';
        });
    }

    // === 事件處理 ===
    changeQuantity(index, delta) {
        const item = this.cartManager.getItem(index);
        if (item) {
            this.cartManager.updateQuantity(index, item.quantity + delta);
        }
    }

    updateQuantity(index, value) {
        this.cartManager.updateQuantity(index, value);
    }

    removeItem(index) {
        if (confirm('確定要移除此商品嗎？')) {
            this.cartManager.removeItem(index);
        }
    }

    updateItemDisplay(index) {
        // 部分更新單一項目（優化性能）
        const item = this.cartManager.getItem(index);
        if (!item) return;

        const itemElement = this.elements.cartItems.querySelector(`[data-index="${index}"]`);
        if (itemElement) {
            const quantityInput = itemElement.querySelector('input[type="number"]');
            const subtotalElement = itemElement.querySelector('.col-md-2:last-child strong');
            
            if (quantityInput) quantityInput.value = item.quantity;
            if (subtotalElement) {
                subtotalElement.textContent = this.cartManager.formatCurrency(item.price * item.quantity);
            }
        }
    }

    handleAddToCart(button) {
        const productData = {
            id: button.dataset.productId,
            name: button.dataset.productName,
            price: parseFloat(button.dataset.productPrice),
            image: button.dataset.productImage,
            flavor: button.dataset.productFlavor,
            color: button.dataset.productColor,
            quantity: parseInt(button.dataset.quantity) || 1
        };

        if (this.cartManager.validateProduct(productData)) {
            this.cartManager.addItem(productData);
        } else {
            this.showNotification('商品資料不完整', 'error');
        }
    }

    async handleCheckout() {
        const cart = this.cartManager.getCart();
        if (cart.length === 0) {
            this.showNotification('購物車是空的！', 'warning');
            return;
        }

        // 檢查門市選擇
        if (window.storeSelector && !window.storeSelector.getSelectedStore()) {
            this.showNotification('請先選擇取貨門市！', 'warning');
            document.getElementById('selectStoreBtn')?.focus();
            return;
        }

        // 這裡可以加入更多結帳邏輯
        this.showNotification('準備結帳...', 'info');
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} notification-toast`;
        notification.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-${this.getIcon(type)} me-2"></i>
                <span>${message}</span>
            </div>
        `;
        
        // 添加樣式
        notification.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            animation: slideIn 0.3s ease;
        `;

        document.body.appendChild(notification);

        // 自動移除
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    getIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
}

// === 全域初始化 ===
let cartManager, cartUI;

document.addEventListener('DOMContentLoaded', () => {
    // 初始化購物車管理器
    cartManager = new CartManager();
    
    // 初始化 UI 控制器（僅在購物車頁面）
    if (document.getElementById('cart-items')) {
        cartUI = new CartUIController(cartManager);
    }
    
    // 匯出到全域
    window.cartManager = cartManager;
    window.cartUI = cartUI;
});

// === 匯出模組 ===
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CartManager, CartUIController };
} 