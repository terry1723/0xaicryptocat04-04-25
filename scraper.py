import asyncio
from playwright.async_api import async_playwright
import json
import os
from datetime import datetime

async def main():
    print("開始爬取女妖輔助建議策略功能...")
    
    # 創建目錄存儲爬取的數據
    os.makedirs("scraped_data", exist_ok=True)
    
    async with async_playwright() as p:
        # 啟動瀏覽器
        browser = await p.chromium.launch(headless=False)  # 設置為False以便觀察
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()
        
        # 訪問目標網站
        await page.goto("https://crypto-gpt-analyzer-yu6896172.replit.app/strategy-tower")
        print("已加載頁面")
        
        # 等待頁面加載
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(2)  # 額外等待以確保JS加載完成
        
        # 進行登錄 (如果需要)
        if await page.is_visible("text=Login") or await page.is_visible("input[name=username]"):
            print("檢測到登錄頁面，正在登錄...")
            
            # 填寫登錄信息
            await page.fill("input[name=username]", "Terry1723")
            await page.fill("input[name=password]", "26436863")
            await page.click("button:has-text('Login')")
            
            # 等待登錄完成
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(2)
            print("登錄完成")
        
        # 開始收集頁面數據
        print("開始收集頁面數據...")
        
        # 1. 獲取頁面HTML結構
        html_content = await page.content()
        with open("scraped_data/page_structure.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        
        # 2. 獲取CSS樣式
        stylesheets = await page.evaluate("""
            () => {
                let styles = [];
                for (const sheet of document.styleSheets) {
                    try {
                        for (const rule of sheet.cssRules) {
                            styles.push(rule.cssText);
                        }
                    } catch (e) {
                        console.log('無法讀取樣式表');
                    }
                }
                return styles;
            }
        """)
        with open("scraped_data/stylesheets.css", "w", encoding="utf-8") as f:
            f.write("\n".join(stylesheets))
        
        # 3. 識別API端點和請求
        client = await context.new_cdp_session(page)
        await client.send("Network.enable")
        
        # 為了觸發API調用，嘗試使用頁面功能
        print("嘗試與頁面交互以觸發API調用...")
        
        # 假設頁面有選擇貨幣對的功能
        selectors = [
            "select", 
            "input[type='text']", 
            "button:not([type='submit'])", 
            "div[role='button']",
            ".dropdown"
        ]
        
        for selector in selectors:
            elements = await page.query_selector_all(selector)
            for element in elements:
                try:
                    # 嘗試點擊元素
                    await element.click()
                    await asyncio.sleep(0.5)
                    # 如果是輸入框，嘗試輸入內容
                    tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
                    if tag_name == "input":
                        await element.fill("BTC")
                        await asyncio.sleep(0.5)
                    # 嘗試按ESC鍵關閉任何打開的下拉菜單
                    await page.keyboard.press("Escape")
                    await asyncio.sleep(0.5)
                except Exception as e:
                    # 忽略錯誤，繼續下一個元素
                    pass
        
        # 4. 獲取頁面中的所有交互元素
        elements_data = await page.evaluate("""
            () => {
                const getElements = (selector) => {
                    return Array.from(document.querySelectorAll(selector)).map(el => {
                        const rect = el.getBoundingClientRect();
                        return {
                            tag: el.tagName.toLowerCase(),
                            id: el.id,
                            classes: Array.from(el.classList),
                            text: el.innerText,
                            attributes: Array.from(el.attributes).map(attr => ({name: attr.name, value: attr.value})),
                            position: {
                                x: rect.x,
                                y: rect.y,
                                width: rect.width,
                                height: rect.height
                            }
                        };
                    });
                };
                
                return {
                    buttons: getElements('button'),
                    inputs: getElements('input'),
                    selects: getElements('select'),
                    divs: getElements('div[role="button"]'),
                    anchors: getElements('a')
                };
            }
        """)
        
        with open("scraped_data/interactive_elements.json", "w", encoding="utf-8") as f:
            json.dump(elements_data, f, indent=2, ensure_ascii=False)
        
        # 5. 截取頁面截圖
        await page.screenshot(path="scraped_data/page_screenshot.png", full_page=True)
        
        # 6. 嘗試獲取策略數據
        await asyncio.sleep(2)  # 確保頁面完全加載
        
        strategy_data = await page.evaluate("""
            () => {
                // 嘗試在頁面上找到策略相關的數據
                // 這需要根據實際頁面結構調整
                const strategyElements = Array.from(document.querySelectorAll('.strategy-item, .strategy-container, [data-strategy]'));
                
                return strategyElements.map(el => ({
                    text: el.innerText,
                    html: el.innerHTML,
                    classes: Array.from(el.classList)
                }));
            }
        """)
        
        with open("scraped_data/strategy_data.json", "w", encoding="utf-8") as f:
            json.dump(strategy_data, f, indent=2, ensure_ascii=False)
        
        # 7. 獲取所有文本內容
        text_content = await page.evaluate("""
            () => {
                return Array.from(document.querySelectorAll('p, h1, h2, h3, h4, h5, h6, span, div'))
                    .filter(el => el.innerText.trim() !== '')
                    .map(el => ({
                        tag: el.tagName.toLowerCase(),
                        text: el.innerText,
                        classes: Array.from(el.classList)
                    }));
            }
        """)
        
        with open("scraped_data/text_content.json", "w", encoding="utf-8") as f:
            json.dump(text_content, f, indent=2, ensure_ascii=False)
        
        print(f"爬取完成，所有數據已保存到 scraped_data 目錄")
        
        # 關閉瀏覽器
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main()) 