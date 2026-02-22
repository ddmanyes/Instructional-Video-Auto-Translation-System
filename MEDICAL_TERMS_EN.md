# Medical Terminology Glossary (Physiology)

This project includes a comprehensive mapping of professional medical terms to ensure high accuracy during translation.

## 📚 Systems Covered

### 1. Nervous System
- neuron (神經元)
- synapse (突觸)
- neurotransmitter (神經傳導物質)
- action potential (動作電位)
- resting membrane potential (靜止膜電位)
- depolarization (去極化)
- repolarization (再極化)
- central nervous system (中樞神經系統)
- peripheral nervous system (周邊神經系統)
- autonomic nervous system (自主神經系統)
- sympathetic nervous system (交感神經)
- parasympathetic nervous system (副交感神經)

### 2. Endocrine System
- hormone (激素/荷爾蒙)
- thyroid gland (甲狀腺)
- parathyroid gland (副甲狀腺)
- pituitary gland (腦下垂體)
- adrenal gland (腎上腺)
- insulin (胰島素)
- glucagon (升糖素)
- epinephrine (腎上腺素)
- norepinephrine (正腎上腺素)

### 3. Respiratory System
- trachea (氣管)
- bronchus (支氣管)
- alveolus (肺泡)
- diaphragm (橫膈膜)
- inspiration (吸氣)
- expiration (呼氣)
- gas exchange (氣體交換)
- vital capacity (肺活量)

### 4. Circulatory System
- heart (心臟)
- artery (動脈)
- vein (靜脈)
- capillary (微血管)
- red blood cell (紅血球)
- white blood cell (白血球)
- platelet (血小板)
- plasma (血漿)
- cardiac output (心搏輸出量)
- systolic pressure (收縮壓)
- diastolic pressure (舒張壓)

### 5. Digestive System
- esophagus (食道)
- stomach (胃)
- duodenum (十二指腸)
- jejunum (空腸)
- ileum (迴腸)
- colon (結腸)
- rectum (直腸)
- liver (肝臟)
- pancreas (胰臟)
- gallbladder (膽囊)
- gastric acid (胃酸)
- digestive enzyme (消化酶)
- peristalsis (蠕動)

### 6. Reproductive System
- ovary (卵巢)
- uterus (子宮)
- testis (睪丸)
- sperm (精子)
- ovum (卵子)
- menstrual cycle (月經週期)
- ovulation (排卵)
- testosterone (睪固酮)
- estrogen (雌激素)
- progesterone (黃體素)

### 7. Urinary System
- kidney (腎臟)
- bladder (膀胱)

### 8. Fundamental Physiological Concepts
- homeostasis (恆定性)
- metabolism (代謝)
- anabolism (同化作用)
- catabolism (異化作用)
- cell (細胞)
- tissue (組織)
- receptor (受體)
- enzyme (酵素)
- protein (蛋白質)
- glucose (葡萄糖)
- ATP (三磷酸腺苷)
- mitochondria (粒線體)

## 🎯 Translation Optimization Engine

### Google Translate Mode
1.  **Initial Translation**: Uses Google Translate for the first pass.
2.  **Terminology Optimization**: Scans the text for medical terms and enforces the correct standardized mapping.
3.  **Trace Logging**: Logs all terminology substitutions for debugging.

### AI Mode (GPT-4o/Claude)
Uses specialized prompts for medical education:
- Identified specifically as a "Physiology Instructional Translation".
- Requires standard medical terminology (Ref: Gray's Anatomy, Guyton Physiology).
- Maintains an academic and formal tone.
- Considers timing constraints for dubbing.

## 📝 How to Add New Terms

If you find errors in specific terms, add them to the `MEDICAL_TERMS` dictionary in `modules/translator.py`:

```python
MEDICAL_TERMS = {
    # ... existing terms ...
    "Your term in Chinese": "Corresponding English Term",
}
```

## 📖 Reference Resources

This glossary is based on the following authorities:
- Gray's Anatomy
- Guyton and Hall Textbook of Medical Physiology
- Medical Subject Headings (MeSH)

---
**Updated**: February 22, 2026
