# DeepVape 共享元件使用指南

## 已建立的共享元件

### 1. VFX 效果 (js/vfx-effects.js)
- 自動初始化所有具有 .vfx-logo 或 #navLogo 的元素
- 提供故障效果和無障礙支援
- 包含降級方案（VFX.js 載入失敗時使用 CSS 動畫）

### 2. 共享樣式 (css/common-styles.css)
- CSS 變數定義
- 導航列樣式（支援多種風格）
- 卡片和按鈕樣式
- 響應式設計
- 動畫效果

### 3. 通用元件 (components/common-components.js)
- 支援三種導航列樣式：default, minimal, modern
- 兩種頁尾樣式：default, minimal
- 購物車計數自動更新
- 滾動效果

## 使用方式

### 在新頁面中使用共享元件：

```html
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>頁面標題</title>
    
    <!-- 共享樣式 -->
    <link rel="stylesheet" href="css/common-styles.css">
    
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <!-- 導航列佔位符 -->
    <div id="navbar-placeholder"></div>
    
    <!-- 頁面內容 -->
    <main>
        <!-- 您的內容 -->
    </main>
    
    <!-- 頁尾佔位符 -->
    <div id="footer-placeholder"></div>
    
    <!-- 共享元件 -->
    <script src="components/common-components.js"></script>
    <script src="js/vfx-effects.js"></script>
    
    <script>
        // 初始化共享元件
        commonComponents.init({
            navbarStyle: 'modern',  // 可選: default, minimal, modern
            footerStyle: 'default', // 可選: default, minimal
            includeVFX: true       // 是否包含 VFX 效果
        });
    </script>
</body>
</html>
```

## 優點
1. 減少程式碼重複 (移除了 11 個檔案中的重複 VFX.js 程式碼)
2. 統一的視覺風格
3. 更容易維護和更新
4. 自動的購物車計數同步
5. 內建的無障礙功能

## 已整合的功能

### 重複程式碼移除統計
- 移除 VFX.js 初始化程式碼：11 個檔案
- 整合共享 CSS 樣式：所有產品頁面
- 標準化導航列/頁尾結構：所有頁面

### 效能改進
- 減少重複載入的 JavaScript
- CSS 樣式集中管理
- 更快的頁面載入速度
