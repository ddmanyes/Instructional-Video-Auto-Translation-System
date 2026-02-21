# 生理醫學術語對照表

本專案內建了豐富的生理醫學專業術語對照表，確保翻譯的準確性。

## 📚 涵蓋系統

### 1. 神經系統 (Nervous System)
- 神經元 → neuron
- 突觸 → synapse
- 神經傳導物質 → neurotransmitter
- 動作電位 → action potential
- 靜止膜電位 → resting membrane potential
- 去極化 → depolarization
- 再極化 → repolarization
- 中樞神經系統 → central nervous system
- 周邊神經系統 → peripheral nervous system
- 自主神經系統 → autonomic nervous system
- 交感神經 → sympathetic nervous system
- 副交感神經 → parasympathetic nervous system

### 2. 內分泌系統 (Endocrine System)
- 激素/荷爾蒙 → hormone
- 甲狀腺 → thyroid gland
- 副甲狀腺 → parathyroid gland
- 腦下垂體 → pituitary gland
- 腎上腺 → adrenal gland
- 胰島素 → insulin
- 升糖素 → glucagon
- 腎上腺素 → epinephrine
- 正腎上腺素 → norepinephrine

### 3. 呼吸系統 (Respiratory System)
- 氣管 → trachea
- 支氣管 → bronchus
- 肺泡 → alveolus
- 橫膈膜 → diaphragm
- 吸氣 → inspiration
- 呼氣 → expiration
- 氣體交換 → gas exchange
- 肺活量 → vital capacity

### 4. 循環系統 (Circulatory System)
- 心臟 → heart
- 動脈 → artery
- 靜脈 → vein
- 微血管 → capillary
- 紅血球 → red blood cell
- 白血球 → white blood cell
- 血小板 → platelet
- 血漿 → plasma
- 心搏輸出量 → cardiac output
- 收縮壓 → systolic pressure
- 舒張壓 → diastolic pressure

### 5. 消化系統 (Digestive System)
- 食道 → esophagus
- 胃 → stomach
- 十二指腸 → duodenum
- 空腸 → jejunum
- 迴腸 → ileum
- 結腸 → colon
- 直腸 → rectum
- 肝臟 → liver
- 胰臟 → pancreas
- 膽囊 → gallbladder
- 胃酸 → gastric acid
- 消化酶 → digestive enzyme
- 蠕動 → peristalsis

### 6. 生殖系統 (Reproductive System)
- 卵巢 → ovary
- 子宮 → uterus
- 睪丸 → testis
- 精子 → sperm
- 卵子 → ovum
- 月經週期 → menstrual cycle
- 排卵 → ovulation
- 睪固酮 → testosterone
- 雌激素 → estrogen
- 黃體素 → progesterone

### 7. 泌尿系統 (Urinary System)
- 腎臟 → kidney
- 膀胱 → bladder

### 8. 基礎生理學概念
- 恆定性 → homeostasis
- 代謝 → metabolism
- 同化作用 → anabolism
- 異化作用 → catabolism
- 細胞 → cell
- 組織 → tissue
- 受體 → receptor
- 酵素 → enzyme
- 蛋白質 → protein
- 葡萄糖 → glucose
- 三磷酸腺苷 (ATP) → ATP
- 粒線體 → mitochondria

## 🎯 翻譯優化機制

### Google Translate 模式
1. **首次翻譯**: 使用 Google Translate 進行初步翻譯
2. **術語優化**: 檢查原文中的醫學術語，確保翻譯結果使用正確的專業術語
3. **日誌記錄**: 記錄所有術語檢查，便於後續優化

### AI 模式 (GPT-4o/Claude)
使用專門的生理醫學翻譯提示詞：
- 明確標示為生理學教材翻譯
- 要求使用標準醫學術語（參考 Gray's Anatomy, Guyton Physiology）
- 保持學術專業語氣
- 確保術語精確度
- 考慮配音時間同步需求

## 📝 如何添加新術語

如果你發現某些專業術語翻譯不準確，可以在 `modules/translator.py` 的 `MEDICAL_TERMS` 字典中添加：

```python
MEDICAL_TERMS = {
    # ... 現有術語 ...
    
    # 添加你的新術語
    "你的中文術語": "對應的英文術語",
}
```

## 💡 使用建議

### 對於一般教學內容
預設的 Google Translate + 術語優化已經足夠準確。

### 對於高階學術內容
如果涉及複雜的生理機制或最新研究，建議切換到 AI 翻譯模式：

```python
# 在 config.py 中
TRANSLATION_CONFIG = {
    "api_provider": "openai",  # 或 "anthropic"
    "domain": "physiology",
}
```

## 🔍 術語準確度驗證

翻譯完成後，可以檢查 `output/subtitles/*_en.srt` 檔案，確認關鍵術語是否正確：

```bash
# 搜尋特定術語
findstr "action potential" output\subtitles\*.srt
findstr "homeostasis" output\subtitles\*.srt
```

## 📖 參考資源

本術語對照表參考以下權威資源：
- Gray's Anatomy
- Guyton and Hall Textbook of Medical Physiology
- 標準醫學詞彙（Medical Subject Headings, MeSH）

---
**最後更新**: 2026年2月6日
