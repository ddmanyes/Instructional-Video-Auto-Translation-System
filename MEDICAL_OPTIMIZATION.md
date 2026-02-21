# 生理醫學領域優化使用示例

## 🎯 翻譯效果對比

### 原文（中文）
```
神經元在突觸處釋放神經傳導物質，當動作電位到達軸突末端時，
會引發鈣離子內流，促使囊泡與細胞膜融合，釋放神經傳導物質到突觸間隙。
```

### 一般翻譯
```
Neurons release neurotransmitters at synapses, when action potentials reach 
axon terminals, it causes calcium ion influx, promotes vesicle fusion with 
cell membrane, releases neurotransmitters into synaptic cleft.
```

### 本系統優化翻譯（預期）
```
Neurons release neurotransmitters at the synapse. When an action potential 
reaches the axon terminal, it triggers calcium ion influx, which promotes 
vesicle fusion with the cell membrane and releases neurotransmitters into 
the synaptic cleft.
```

## ✨ 關鍵改進

| 中文術語 | 系統翻譯 | 說明 |
|---------|---------|------|
| 神經元 | neuron | 標準醫學術語 |
| 突觸 | synapse | 專業術語，不是 junction |
| 神經傳導物質 | neurotransmitter | 完整術語 |
| 動作電位 | action potential | 生理學標準用語 |
| 軸突 | axon | 神經解剖標準術語 |
| 突觸間隙 | synaptic cleft | 專業術語 |

## 📋 系統涵蓋的課程主題

### ✅ Neurophysiology（神經生理學）
- 神經元結構與功能
- 動作電位機制
- 突觸傳遞
- 感覺與運動系統
- 自主神經系統

### ✅ Endocrine System（內分泌系統）
- 荷爾蒙分泌與調節
- 下視丘-腦垂體軸
- 甲狀腺功能
- 腎上腺功能
- 胰島素與血糖調節

### ✅ Respiratory System（呼吸系統）
- 呼吸力學
- 氣體交換
- 氧氣運輸
- 酸鹼平衡
- 呼吸調節

### ✅ Circulatory System（循環系統）
- 心臟生理
- 血壓調節
- 血液成分
- 心電圖原理
- 血管功能

### ✅ Gastrointestinal System（消化系統）
- 消化酶作用
- 胃腸蠕動
- 營養吸收
- 肝臟功能
- 胰臟分泌

### ✅ Reproductive System（生殖系統）
- 月經週期
- 荷爾蒙調節
- 生育機制
- 性激素作用

## 💡 使用技巧

### 1. 檢查翻譯後的字幕
```powershell
# 搜尋特定專業術語
findstr /i "neuron action potential homeostasis" output\subtitles\*_en.srt
```

### 2. 驗證關鍵概念
翻譯完成後，建議檢查以下關鍵術語是否正確：
- ✅ 細胞層級：neuron, cell membrane, receptor
- ✅ 系統層級：nervous system, cardiovascular system
- ✅ 生理過程：homeostasis, metabolism, action potential
- ✅ 臨床相關：blood pressure, heart rate, pH

### 3. 自訂術語
如果你的課程涉及特殊術語，可在 `modules/translator.py` 添加：

```python
MEDICAL_TERMS = {
    # 現有術語...
    
    # 你的自訂術語
    "特殊蛋白": "specific protein name",
    "特殊機制": "specific mechanism",
}
```

## 🎓 適用課程

本系統已經過優化，特別適合：
- ✅ 大學生理學課程
- ✅ 醫學院基礎醫學
- ✅ 護理學生理課程
- ✅ 研究生進階生理學
- ✅ 專業醫學教育

## 📊 翻譯品質評估

### Google Translate + 術語優化（免費）
- 一般描述：⭐⭐⭐⭐ 優秀
- 醫學術語：⭐⭐⭐⭐ 優秀（100+ 術語保證）
- 複雜概念：⭐⭐⭐ 良好
- 自然流暢度：⭐⭐⭐⭐ 優秀

### GPT-4o/Claude（付費）
- 一般描述：⭐⭐⭐⭐⭐ 卓越
- 醫學術語：⭐⭐⭐⭐⭐ 卓越
- 複雜概念：⭐⭐⭐⭐⭐ 卓越
- 自然流暢度：⭐⭐⭐⭐⭐ 卓越

### 建議選擇
- 💰 預算有限 → Google Translate + 術語優化（完全免費，品質優秀）
- 🎯 重要內容 → GPT-4o（最佳品質，約 $0.5-2/影片）
- 🔬 研究發表 → Claude（最自然的學術語氣）

## 🚀 開始使用

```powershell
# 驗證術語表
python test_medical_terms.py

# 處理單個影片
python main.py --video "video\Neurophysiology-1.mp4"

# 批次處理所有影片
python main.py --batch
```

---
**專為生理醫學教育優化** 🎓  
**100+ 專業術語保證** ✅  
**完全免費使用** 💯
