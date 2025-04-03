# CryptoAnalyzer - 加密貨幣分析平台

一個整合多種技術分析策略和多重資料源的加密貨幣分析工具。

## 功能

* 支持多種加密貨幣的技術分析 (BTC, ETH, SOL, BNB, XRP, ADA 等)
* 多時間框架分析 (15分鐘, 1小時, 4小時, 1天, 1週)
* 整合 SMC 和 SNR 策略
* 多種數據來源備份機制 (Coincap, CoinMarketCap, Bitget, Coinbase)
* AI 輔助市場分析

## 使用方法

1. 從側邊欄選擇加密貨幣
2. 選擇時間框架
3. 點擊「開始分析」按鈕
4. 查看技術分析結果和 AI 建議

## 部署

本應用基於 Streamlit 開發，可以在本地運行或部署到 Streamlit Cloud。

### 本地運行

```bash
pip install -r requirements.txt
streamlit run app.py
``` 