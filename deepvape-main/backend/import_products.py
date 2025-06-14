#!/usr/bin/env python3
"""
導入現有產品數據到後台數據庫
"""

from app import app, db, Category, Product
import json

def import_products():
    """導入產品數據"""
    with app.app_context():
        # 清空現有數據
        Product.query.delete()
        
        # 獲取分類
        hosts_category = Category.query.filter_by(slug='hosts').first()
        pods_category = Category.query.filter_by(slug='pods').first()
        disposable_category = Category.query.filter_by(slug='disposable').first()
        
        # 主機系列產品
        host_products = [
            {
                'name': 'SP2 一代主機',
                'description': '智能溫控系統，7W~8W功率，400mAH電池，16種顏色選擇',
                'price': 600,
                'stock_quantity': 50,
                'category_id': hosts_category.id,
                'main_image': 'sp2_v/SP2主機-SP2S主機圖.jpg',
                'is_active': True,
                'is_featured': True,
                'badge_type': 'hot',
                'badge_text': '目前最火',
                'specifications': json.dumps({
                    '功率': '7W~8W',
                    '電池容量': '400mAH',
                    '充電方式': 'TYPE-C',
                    '顏色選擇': '16種',
                    '特色功能': '智能溫控系統'
                }, ensure_ascii=False),
                'variants': json.dumps([
                    {'name': '顏色', 'value': '黑色,白色,紅色,藍色,綠色,粉色,紫色,橙色,黃色,灰色,金色,銀色,玫瑰金,香檳金,深藍,墨綠'}
                ], ensure_ascii=False),
                'meta_title': 'SP2 一代主機 - 智能溫控電子煙',
                'meta_description': 'SP2 一代主機，配備智能溫控系統，7W~8W功率，400mAH電池，16種顏色可選'
            },
            {
                'name': 'ILIA 一代主機',
                'description': '經典設計，穩定可靠，新手首選，9種顏色選擇',
                'price': 600,
                'stock_quantity': 45,
                'category_id': hosts_category.id,
                'main_image': 'ilia_1/★柒★【ILIA】哩啞-一代主機.jpg',
                'is_active': True,
                'is_featured': False,
                'badge_type': 'safe',
                'badge_text': '安心選擇',
                'specifications': json.dumps({
                    '功率': '7W~8W',
                    '電池容量': '450mAH',
                    '充電方式': 'TYPE-C',
                    '顏色選擇': '9種',
                    '特色': '經典設計，穩定可靠'
                }, ensure_ascii=False),
                'variants': json.dumps([
                    {'name': '顏色', 'value': '黑色,白色,紅色,藍色,綠色,粉色,紫色,橙色,黃色'}
                ], ensure_ascii=False),
                'meta_title': 'ILIA 一代主機 - 經典穩定電子煙',
                'meta_description': 'ILIA 一代主機，經典設計，穩定可靠，新手首選，9種顏色可選'
            },
            {
                'name': 'ILIA 皮革主機',
                'description': '奢華質感，手工皮革包覆，限量發售，6種皮革顏色',
                'price': 900,
                'stock_quantity': 20,
                'category_id': hosts_category.id,
                'main_image': 'ilia_L/ILIA主機-皮革圖.jpg',
                'is_active': True,
                'is_featured': True,
                'badge_type': 'new',
                'badge_text': '新品',
                'specifications': json.dumps({
                    '功率': '8W~10W',
                    '電池容量': '400mAH',
                    '充電方式': 'TYPE-C',
                    '外觀': '手工皮革包覆',
                    '特色功能': '智能電量顯示'
                }, ensure_ascii=False),
                'variants': json.dumps([
                    {'name': '皮革顏色', 'value': '經典黑,咖啡棕,深藍,酒紅,墨綠,奶茶色'}
                ], ensure_ascii=False),
                'meta_title': 'ILIA 皮革主機 - 奢華手工皮革電子煙',
                'meta_description': 'ILIA 皮革主機，奢華質感，手工皮革包覆，限量發售'
            },
            {
                'name': 'ILIA 哩亞布紋主機',
                'description': '時尚布紋外觀、8W~10W功率調節、400mAh電池，8種顏色選擇',
                'price': 750,
                'stock_quantity': 30,
                'category_id': hosts_category.id,
                'main_image': 'ilia_Bu/布紋款哩亞主機-ILIA電子煙主機-換彈式霧化桿.png',
                'is_active': True,
                'is_featured': False,
                'badge_type': 'new',
                'badge_text': '布紋設計',
                'specifications': json.dumps({
                    '功率': '8W~10W',
                    '電池容量': '400mAh',
                    '充電方式': 'TYPE-C',
                    '外觀': '時尚布紋設計',
                    '顏色選擇': '8種'
                }, ensure_ascii=False),
                'variants': json.dumps([
                    {'name': '顏色', 'value': '墨黑色,墨藍色,哩亞灰,哩亞粉,哩亞紅,哩亞藍,哩亞黃,布紋藍'}
                ], ensure_ascii=False),
                'meta_title': 'ILIA 哩亞布紋主機 - 時尚布紋電子煙',
                'meta_description': 'ILIA 哩亞布紋主機，時尚布紋外觀，8W~10W功率調節'
            },
            {
                'name': 'HTA 黑桃主機',
                'description': '一代二代通用、350mAH電池、CP值極高',
                'price': 280,
                'stock_quantity': 60,
                'category_id': hosts_category.id,
                'main_image': 'hta_vape/HTA_c6c0aa3c-79d3-4484-a99c-6fe03e67cb54.webp',
                'is_active': True,
                'is_featured': False,
                'badge_type': 'hot',
                'badge_text': '頂級品牌',
                'specifications': json.dumps({
                    '電池容量': '350mAH',
                    '兼容性': '一代二代通用',
                    '特色': 'CP值極高',
                    '品牌': 'HTA 黑桃'
                }, ensure_ascii=False),
                'variants': json.dumps([
                    {'name': '顏色', 'value': '黑色,白色,紅色,藍色'}
                ], ensure_ascii=False),
                'meta_title': 'HTA 黑桃主機 - 高CP值電子煙',
                'meta_description': 'HTA 黑桃主機，一代二代通用，350mAH電池，CP值極高'
            }
        ]
        
        # 煙彈系列產品
        pod_products = [
            {
                'name': 'ILIA 發光煙彈',
                'description': '透明外殼、炫彩發光、25種口味、3顆裝，3%尼古丁含量',
                'price': 300,
                'stock_quantity': 100,
                'category_id': pods_category.id,
                'main_image': 'illa_d/哩亞-ILIA煙彈.webp',
                'is_active': True,
                'is_featured': True,
                'badge_type': 'hot',
                'badge_text': '發光設計',
                'specifications': json.dumps({
                    '容量': '2.5ml',
                    '包裝': '3顆裝',
                    '尼古丁含量': '3%',
                    '特色': '透明外殼發光設計',
                    '口味數量': '25種'
                }, ensure_ascii=False),
                'variants': json.dumps([
                    {'name': '口味', 'value': '傾心草莓,冰釀藍莓,零度可樂,雪碧,芬達,蘋果,西瓜,哈密瓜,荔枝,芒果,鳳梨,葡萄,櫻桃,水蜜桃,奇異果,檸檬,薄荷,綠茶,烏龍茶,咖啡,香草,巧克力,牛奶,優格,蜂蜜'}
                ], ensure_ascii=False),
                'meta_title': 'ILIA 發光煙彈 - 炫彩發光25種口味',
                'meta_description': 'ILIA 發光煙彈，透明外殼炫彩發光，25種口味選擇，3顆裝'
            },
            {
                'name': 'SP2 煙彈',
                'description': '32種豐富口味、2.0ML容量、3%尼古丁含量、一盒三入',
                'price': 350,
                'stock_quantity': 80,
                'category_id': pods_category.id,
                'main_image': 'sp2_d/S__24518868.jpg',
                'is_active': True,
                'is_featured': False,
                'badge_type': 'new',
                'badge_text': '32種口味',
                'specifications': json.dumps({
                    '容量': '2.0ML',
                    '包裝': '一盒三入',
                    '尼古丁含量': '3%',
                    '口味數量': '32種',
                    '兼容性': 'SP2主機專用'
                }, ensure_ascii=False),
                'variants': json.dumps([
                    {'name': '口味', 'value': '草莓,藍莓,西瓜,哈密瓜,蘋果,葡萄,櫻桃,水蜜桃,芒果,鳳梨,荔枝,奇異果,檸檬,柳橙,薄荷,綠茶,烏龍茶,咖啡,香草,巧克力,牛奶,優格,蜂蜜,可樂,雪碧,芬達,能量飲料,威士忌,伏特加,琴酒,龍舌蘭,白蘭地'}
                ], ensure_ascii=False),
                'meta_title': 'SP2 煙彈 - 32種豐富口味選擇',
                'meta_description': 'SP2 煙彈，32種豐富口味，2.0ML容量，一盒三入'
            }
        ]
        
        # 拋棄式系列產品
        disposable_products = [
            {
                'name': 'ILIA 拋棄式四代',
                'description': '6500口大容量、13ML煙油、650mAh電池、TYPE-C充電、21種口味',
                'price': 280,
                'original_price': 300,
                'stock_quantity': 120,
                'category_id': disposable_category.id,
                'main_image': 'ilia_a_4/-哩亞拋棄式-1000x1000.jpg.webp',
                'is_active': True,
                'is_featured': True,
                'badge_type': 'hot',
                'badge_text': '大容量',
                'specifications': json.dumps({
                    '口數': '6500口',
                    '煙油容量': '13ML',
                    '電池容量': '650mAh',
                    '充電方式': 'TYPE-C',
                    '霧化器': 'Mesh 0.8Ω',
                    '口味數量': '21種'
                }, ensure_ascii=False),
                'variants': json.dumps([
                    {'name': '口味', 'value': '草莓,藍莓,西瓜,哈密瓜,蘋果,葡萄,櫻桃,水蜜桃,芒果,鳳梨,荔枝,奇異果,檸檬,薄荷,綠茶,咖啡,香草,巧克力,可樂,雪碧,能量飲料'}
                ], ensure_ascii=False),
                'meta_title': 'ILIA 拋棄式四代 - 6500口大容量',
                'meta_description': 'ILIA 拋棄式四代，6500口大容量，13ML煙油，TYPE-C充電'
            }
        ]
        
        # 添加所有產品
        all_products = host_products + pod_products + disposable_products
        
        for product_data in all_products:
            product = Product(**product_data)
            db.session.add(product)
        
        db.session.commit()
        print(f"✅ 成功導入 {len(all_products)} 個產品")
        
        # 顯示導入的產品
        products = Product.query.all()
        for product in products:
            print(f"- {product.name} (NT$ {product.price}) - {product.category.name}")

if __name__ == '__main__':
    import_products() 