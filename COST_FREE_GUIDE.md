# 完全免費使用指南 💯

本專案現在可以**完全免費**使用！無需任何 API 金鑰或付費服務。

## ✅ 免費功能清單

| 功能 | 使用技術 | 成本 |
|------|---------|------|
| 語音轉文字 (ASR) | Faster-Whisper (本地) | **免費** |
| 字幕翻譯 | Google Translate API | **免費** |
| 語音合成 (TTS) | Coqui XTTS-v2 (本地/克隆) 或 Edge TTS | **免費** |
| 影音合成 | FFmpeg (本地無損拉伸) | **免費** |

## 🚀 快速開始（免費版）

### 1. 安裝依賴
```powershell
pip install -r requirements.txt
choco install ffmpeg
```

### 2. 確認配置
檢查 `config.py` 中的翻譯設定：
```python
TRANSLATION_CONFIG = {
    "api_provider": "google",  # 使用免費的 Google Translate
    ...
}
```

### 3. 開始處理
```powershell
python main.py --batch
```

就這麼簡單！無需任何 API 金鑰。

## 📊 Google Translate vs 付費 AI 對比

| 特性 | Google Translate (免費) | GPT-4o/Claude (付費) |
|------|------------------------|---------------------|
| **成本** | 完全免費 | $0.3-1.5 per video |
| **速度** | 快速 | 較慢 |
| **一般翻譯** | ⭐⭐⭐⭐ 優秀 | ⭐⭐⭐⭐⭐ 卓越 |
| **醫學術語** | ⭐⭐⭐ 良好 | ⭐⭐⭐⭐⭐ 專業 |
| **自然度** | ⭐⭐⭐ 良好 | ⭐⭐⭐⭐⭐ 極自然 |
| **使用限制** | 無（有速率限制） | 需要 API 金鑰和餘額 |

## 💡 建議使用場景

### 使用免費 Google Translate 當：
- ✅ 日常教學影片翻譯
- ✅ 預算有限
- ✅ 需要快速處理
- ✅ 翻譯品質要求中等

### 升級到付費 AI 當：
- 🎯 需要最高品質的醫學術語翻譯
- 🎯 對自然語感要求極高
- 🎯 處理重要的學術內容
- 🎯 預算充足

## ⚙️ 切換翻譯方式

### 改用 Google Translate（免費）
在 `config.py` 中：
```python
TRANSLATION_CONFIG = {
    "api_provider": "google",
}
```

### 改用 OpenAI GPT-4o（付費）
```python
TRANSLATION_CONFIG = {
    "api_provider": "openai",
}
```
並設定環境變數：
```powershell
$env:OPENAI_API_KEY="sk-your-key"
```

### 改用 Anthropic Claude（付費）
```python
TRANSLATION_CONFIG = {
    "api_provider": "anthropic",
}
```
並設定環境變數：
```powershell
$env:ANTHROPIC_API_KEY="sk-ant-your-key"
```

## 🔧 優化免費版品質

### 1. 後處理醫學術語
可以建立專業術語對照表：
```python
# 在 translator.py 中添加術語替換
medical_terms = {
    "神經系統": "nervous system",
    "循環系統": "circulatory system",
    # ... 更多術語
}
```

### 2. 批次大小調整
```python
TRANSLATION_CONFIG = {
    "batch_size": 10,  # 減少可提高穩定性
}
```

### 3. 手動校正重要術語
翻譯完成後，可以在 `output/subtitles/*_en.srt` 中手動修正關鍵術語。

## ❓ 常見問題

### Q: Google Translate 會不會被限制？
**A:** 理論上有速率限制，但一般使用不會觸發。程式已加入延遲機制。

### Q: 翻譯品質夠用嗎？
**A:** 對於一般教學內容，Google Translate 已經相當優秀。如需最高品質，可考慮混合使用。

### Q: 可以離線使用嗎？
**A:** Google Translate 需要網路。如需完全離線，可改用 Argos Translate（需要額外配置）。

### Q: 處理 15 個影片需要多久？
**A:** 約 2-4 小時（取決於影片長度和電腦性能），完全免費！

## 🎉 總結

使用預設配置（Google Translate），本專案：
- ✅ **完全免費**
- ✅ 無需 API 金鑰
- ✅ 翻譯品質優秀
- ✅ 處理速度快
- ✅ 適合大多數使用場景

開始享受免費的影片翻譯服務吧！🚀

---
**更新日期**: 2026年2月6日
