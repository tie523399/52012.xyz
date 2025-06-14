/**
 * DeepVape VFX.js 共享效果元件
 * 整合所有頁面的 VFX.js 故障效果
 */

// VFX.js Logo效果類別
class LogoButtonEffect {
    constructor(button) {
        this.initVFX(button);
    }

    initVFX(button) {
        // 檢查 VFX.js 是否已載入（需要在 HTML 中引入）
        if (typeof VFX !== 'undefined') {
            try {
                this.vfx = new VFX();
                
                // 滑鼠懸停效果
                button.addEventListener("mouseenter", () => {
                    this.vfx.add(button, { 
                        shader: "glitch", 
                        overflow: 50,
                        uniforms: {
                            uTime: 0,
                            uIntensity: 0.3
                        }
                    });
                });

                button.addEventListener("mouseleave", () => {
                    this.vfx.remove(button);
                });

                // 點擊效果
                button.addEventListener("click", () => {
                    console.log("DeepVape Logo clicked!");
                    
                    // 點擊反饋動畫
                    button.style.transform = "skewX(-10deg) scale(0.95)";
                    setTimeout(() => {
                        button.style.transform = "skewX(-10deg) scale(1)";
                    }, 150);
                });

                // 添加無障礙支援
                this.addAccessibility(button);
                
            } catch (error) {
                console.warn("VFX.js 效果初始化失敗，使用備用樣式", error);
                this.applyFallbackStyles(button);
            }
        } else {
            // VFX.js 未載入，使用備用樣式
            console.info("VFX.js 未載入，使用 CSS 動畫效果");
            this.applyFallbackStyles(button);
        }
    }

    addAccessibility(button) {
        button.setAttribute("tabindex", "0");
        button.setAttribute("role", "button");
        button.setAttribute("aria-label", "DeepVape 主頁連結");
        
        // 鍵盤支援
        button.addEventListener("keydown", (e) => {
            if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                button.click();
            }
        });
    }

    applyFallbackStyles(button) {
        // 如果 VFX.js 載入失敗，使用 CSS 動畫作為備用
        button.style.transition = "all 0.3s ease";
        
        button.addEventListener("mouseenter", () => {
            button.style.transform = "skewX(-10deg) scale(1.05)";
            button.style.filter = "hue-rotate(10deg) brightness(1.2)";
        });

        button.addEventListener("mouseleave", () => {
            button.style.transform = "skewX(-10deg) scale(1)";
            button.style.filter = "none";
        });

        // 點擊效果
        button.addEventListener("click", () => {
            console.log("DeepVape Logo clicked!");
            
            // 點擊反饋動畫
            button.style.transform = "skewX(-10deg) scale(0.95)";
            setTimeout(() => {
                button.style.transform = "skewX(-10deg) scale(1)";
            }, 150);
        });
    }
}

// 初始化函數
function initializeVFXEffects() {
    // 尋找所有需要 VFX 效果的元素
    const logoButtons = document.querySelectorAll('#navLogo, .logo-button, .vfx-logo');
    
    logoButtons.forEach(button => {
        new LogoButtonEffect(button);
    });

    // 添加全域樣式
    if (!document.getElementById('vfx-styles')) {
        const style = document.createElement('style');
        style.id = 'vfx-styles';
        style.textContent = `
            .logo-button, .vfx-logo {
                cursor: pointer;
                display: inline-block;
            }
            
            /* 故障效果動畫 */
            @keyframes glitch {
                0%, 100% { transform: translate(0); }
                20% { transform: translate(-2px, 2px); }
                40% { transform: translate(-2px, -2px); }
                60% { transform: translate(2px, 2px); }
                80% { transform: translate(2px, -2px); }
            }
            
            .vfx-logo:hover {
                animation: glitch 0.3s infinite;
            }
            
            @media (prefers-reduced-motion: reduce) {
                .logo-button, .vfx-logo {
                    animation: none !important;
                    transition: none !important;
                }
            }
        `;
        document.head.appendChild(style);
    }
}

// 自動初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeVFXEffects);
} else {
    initializeVFXEffects();
}

// 掛載到全域物件供需要手動初始化的頁面使用
window.VFXEffects = {
    LogoButtonEffect: LogoButtonEffect,
    initializeVFXEffects: initializeVFXEffects
}; 