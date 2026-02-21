"""
Translation Module
使用 LLM (GPT-4o / Claude) 進行字幕翻譯
"""

import os
import re
from pathlib import Path
import logging
from openai import OpenAI
from anthropic import Anthropic
from deep_translator import GoogleTranslator
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 生理醫學術語對照表
MEDICAL_TERMS = {
    # 系統
    "神經系統": "nervous system",
    "循環系統": "circulatory system",
    "呼吸系統": "respiratory system",
    "消化系統": "digestive system",
    "泌尿系統": "urinary system",
    "內分泌系統": "endocrine system",
    "生殖系統": "reproductive system",
    "免疫系統": "immune system",
    "肌肉系統": "muscular system",
    "骨骼系統": "skeletal system",
    
    # 器官
    "心臟": "heart",
    "肺臟": "lung",
    "肝臟": "liver",
    "腎臟": "kidney",
    "胃": "stomach",
    "腸道": "intestine",
    "小腸": "small intestine",
    "大腸": "large intestine",
    "胰臟": "pancreas",
    "脾臟": "spleen",
    "膀胱": "bladder",
    
    # 神經系統
    "神經元": "neuron",
    "突觸": "synapse",
    "神經傳導物質": "neurotransmitter",
    "動作電位": "action potential",
    "靜止膜電位": "resting membrane potential",
    "去極化": "depolarization",
    "再極化": "repolarization",
    "中樞神經系統": "central nervous system",
    "周邊神經系統": "peripheral nervous system",
    "自主神經系統": "autonomic nervous system",
    "交感神經": "sympathetic nervous system",
    "副交感神經": "parasympathetic nervous system",
    
    # 內分泌
    "激素": "hormone",
    "荷爾蒙": "hormone",
    "甲狀腺": "thyroid gland",
    "副甲狀腺": "parathyroid gland",
    "腦下垂體": "pituitary gland",
    "腎上腺": "adrenal gland",
    "胰島素": "insulin",
    "升糖素": "glucagon",
    "腎上腺素": "epinephrine",
    "正腎上腺素": "norepinephrine",
    
    # 呼吸系統
    "氣管": "trachea",
    "支氣管": "bronchus",
    "肺泡": "alveolus",
    "橫膈膜": "diaphragm",
    "吸氣": "inspiration",
    "呼氣": "expiration",
    "氣體交換": "gas exchange",
    "肺活量": "vital capacity",
    
    # 循環系統
    "動脈": "artery",
    "靜脈": "vein",
    "微血管": "capillary",
    "紅血球": "red blood cell",
    "白血球": "white blood cell",
    "血小板": "platelet",
    "血漿": "plasma",
    "心搏輸出量": "cardiac output",
    "收縮壓": "systolic pressure",
    "舒張壓": "diastolic pressure",
    
    # 消化系統
    "食道": "esophagus",
    "十二指腸": "duodenum",
    "空腸": "jejunum",
    "迴腸": "ileum",
    "結腸": "colon",
    "直腸": "rectum",
    "膽囊": "gallbladder",
    "胃酸": "gastric acid",
    "消化酶": "digestive enzyme",
    "蠕動": "peristalsis",
    
    # 生殖系統
    "卵巢": "ovary",
    "子宮": "uterus",
    "睪丸": "testis",
    "精子": "sperm",
    "卵子": "ovum",
    "月經週期": "menstrual cycle",
    "排卵": "ovulation",
    "睪固酮": "testosterone",
    "雌激素": "estrogen",
    "黃體素": "progesterone",
    
    # 一般生理學
    "恆定性": "homeostasis",
    "代謝": "metabolism",
    "同化作用": "anabolism",
    "異化作用": "catabolism",
    "細胞": "cell",
    "組織": "tissue",
    "受體": "receptor",
    "酵素": "enzyme",
    "蛋白質": "protein",
    "葡萄糖": "glucose",
    "三磷酸腺苷": "ATP",
    "粒線體": "mitochondria",
}


class SubtitleTranslator:
    def __init__(self, api_provider="google", api_key=None):
        """
        初始化翻譯器
        
        Args:
            api_provider: API 提供者 ("google", "openai" 或 "anthropic")
            api_key: API 金鑰 (若為 None 則從環境變數讀取)
        """
        self.api_provider = api_provider
        
        if api_provider == "google":
            # Google Translate - 完全免費
            self.translator = GoogleTranslator(source='zh-CN', target='en')
            self.model = "Google Translate (Free) - 生理醫學專用"
            logger.info(f"已初始化翻譯器: Google Translate - 完全免費（生理醫學領域優化）")
        elif api_provider == "openai":
            self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
            self.model = "gpt-4o"
            logger.info(f"已初始化翻譯器: {api_provider} - {self.model}")
        elif api_provider == "anthropic":
            self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
            self.model = "claude-3-5-sonnet-20241022"
            logger.info(f"已初始化翻譯器: {api_provider} - {self.model}")
        else:
            raise ValueError(f"不支援的 API 提供者: {api_provider}")
    
    def parse_srt(self, srt_path):
        """解析 SRT 字幕檔案"""
        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 正則表達式解析 SRT 格式
        pattern = re.compile(
            r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\n|\Z)', 
            re.DOTALL
        )
        
        subtitles = []
        for match in pattern.finditer(content):
            subtitles.append({
                'index': int(match.group(1)),
                'start': match.group(2),
                'end': match.group(3),
                'text': match.group(4).strip()
            })
        
        return subtitles
    
    def translate_subtitles(self, srt_path, target_lang="en", output_dir="output/subtitles"):
        """
        翻譯 SRT 字幕檔案
        
        Args:
            srt_path: 原始 SRT 檔案路徑
            target_lang: 目標語言 (en, ja, etc.)
            output_dir: 輸出目錄
            
        Returns:
            translated_srt_path: 翻譯後的 SRT 檔案路徑
        """
        video_name = Path(srt_path).stem.replace('_zh', '')
        os.makedirs(output_dir, exist_ok=True)
        translated_srt_path = os.path.join(output_dir, f"{video_name}_en.srt")
        
        logger.info(f"開始翻譯字幕: {video_name}")
        
        # 解析原始字幕
        subtitles = self.parse_srt(srt_path)
        
        # 批次翻譯
        translated_subtitles = []
        batch_size = 10
        
        for i in range(0, len(subtitles), batch_size):
            batch = subtitles[i:i+batch_size]
            texts = [sub['text'] for sub in batch]
            
            # 翻譯這一批
            translated_texts = self._translate_batch(texts, target_lang)
            
            # 組合結果
            for j, sub in enumerate(batch):
                translated_subtitles.append({
                    'index': sub['index'],
                    'start': sub['start'],
                    'end': sub['end'],
                    'text': translated_texts[j] if j < len(translated_texts) else sub['text']
                })
            
            logger.info(f"已翻譯 {min(i+batch_size, len(subtitles))}/{len(subtitles)} 條字幕")
            
            # 每批次間稍微休息，避免被封鎖
            if i + batch_size < len(subtitles):
                time.sleep(1.0)
        
        # 寫入新的 SRT 檔案
        with open(translated_srt_path, 'w', encoding='utf-8') as f:
            for sub in translated_subtitles:
                f.write(f"{sub['index']}\n")
                f.write(f"{sub['start']} --> {sub['end']}\n")
                f.write(f"{sub['text']}\n\n")
        
        logger.info(f"翻譯完成，已儲存至: {translated_srt_path}")
        return translated_srt_path
    
    def _translate_batch(self, texts, target_lang="en"):
        """使用選定的翻譯服務翻譯一批文本"""
        
        # 如果使用 Google Translate
        if self.api_provider == "google":
            return self._translate_with_google(texts)
        
        # 如果使用 LLM (OpenAI/Anthropic)
        prompt = f"""你是專業的生理學（Physiology）教材翻譯專家，專精於人體生理系統的醫學教育內容。

翻譯領域：生理學教學影片字幕
涵蓋系統：神經、內分泌、呼吸、循環、消化、泌尿、生殖系統

翻譯要求：
1. 使用標準醫學術語（參考 Gray's Anatomy, Guyton Physiology）
2. 保持學術專業語氣，適合大學醫學教育
3. 醫學術語必須精確（如：action potential, homeostasis, neurotransmitter）
4. 翻譯後的長度儘量與原文相近（±10%，用於影片配音同步）
5. 保持教學語境的清晰度和易理解性
6. 每行翻譯結果獨立一行
7. 只輸出翻譯結果，不要加編號或說明

原文字幕（中文）：
{chr(10).join([f"{i+1}. {text}" for i, text in enumerate(texts)])}

請翻譯成英文（每行一個翻譯結果）："""

        try:
            if self.api_provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a professional medical physiology translator."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )
                result = response.choices[0].message.content
            
            else:  # anthropic
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )
                result = response.content[0].text
            
            # 解析結果
            lines = [line.strip() for line in result.split('\n') if line.strip()]
            # 移除編號
            translations = [re.sub(r'^\d+\.\s*', '', line) for line in lines]
            
            return translations[:len(texts)]
        
        except Exception as e:
            logger.error(f"翻譯失敗: {e}")
            return texts  # 失敗時返回原文
    
    def _translate_with_google(self, texts):
        """使用 Google Translate 翻譯（完全免費）+ 生理醫學術語優化 (加速版)"""
        if not texts:
            return []
            
        try:
            # 將 10 條字幕合併為一個字串進行翻譯 (使用雙換行作為更穩定的分隔符)
            separator = "\n\n"
            combined_text = separator.join(texts)
            translated_combined = self.translator.translate(combined_text)
            
            # 分割回多行 (支援多種分行符)
            translated_lines = re.split(r'\n\s*\n', translated_combined.strip())
            
            # 如果行數不對，嘗試單換行分割
            if len(translated_lines) != len(texts):
                translated_lines = translated_combined.strip().split("\n")
            
            # 檢查行數是否匹配
            if len(translated_lines) == len(texts):
                refined_translations = []
                for orig, trans in zip(texts, translated_lines):
                    refined_translations.append(self._refine_medical_terms(orig, trans))
                return refined_translations
            else:
                logger.warning(f"批量翻譯行數不符 ({len(translated_lines)} vs {len(texts)})，改用逐行翻譯...")
        except Exception as e:
            logger.warning(f"批量翻譯失敗: {e}，改用逐行翻譯...")

        # 降級方案：逐行翻譯
        translations = []
        for i, text in enumerate(texts):
            try:
                translated = self.translator.translate(text)
                translated = self._refine_medical_terms(text, translated)
                translations.append(translated)
                if i < len(texts) - 1:
                    time.sleep(0.05)  # 縮短延遲
            except Exception as e:
                logger.warning(f"逐行翻譯失敗: {e}")
                translations.append(text)
        return translations
    
    def _refine_medical_terms(self, original_text, translated_text):
        """
        優化翻譯結果，確保醫學術語準確
        檢查原文中的醫學術語，並在翻譯結果中確保使用正確的專業術語
        """
        refined_text = translated_text
        # 檢查原文中是否包含醫學術語
        for chinese_term, english_term in MEDICAL_TERMS.items():
            if chinese_term in original_text:
                # 如果翻譯結果殘留中文術語，直接替換成英文
                if chinese_term in refined_text:
                    refined_text = refined_text.replace(chinese_term, english_term)

                # 使用正則表達式進行不區分大小寫的替換
                # 處理可能的變化形式
                variations = [
                    english_term,
                    english_term.title(),
                    english_term.upper(),
                    english_term.replace(' ', '-'),
                    english_term.replace(' ', '')
                ]
                
                # 如果翻譯結果中沒有正確的術語，嘗試智能替換
                if not any(var.lower() in refined_text.lower() for var in variations):
                    # 記錄潛在的術語問題
                    logger.debug(f"醫學術語檢查: '{chinese_term}' → 確保使用 '{english_term}'")

        return refined_text


if __name__ == "__main__":
    # 測試用例
    translator = SubtitleTranslator(api_provider="openai")
    translated_file = translator.translate_subtitles("output/subtitles/test_zh.srt")
    print(f"翻譯後的字幕檔案: {translated_file}")
