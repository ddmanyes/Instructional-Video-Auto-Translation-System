"""
測試生理醫學術語翻譯功能
"""

from modules.translator import SubtitleTranslator, MEDICAL_TERMS

def test_medical_terms():
    """測試醫學術語對照表"""
    print("="*60)
    print("生理醫學術語對照表測試")
    print("="*60)
    
    # 統計術語數量
    systems = {
        "神經系統": ["神經元", "突觸", "動作電位", "神經傳導物質"],
        "內分泌系統": ["激素", "胰島素", "甲狀腺", "腎上腺"],
        "呼吸系統": ["肺泡", "氣管", "橫膈膜", "氣體交換"],
        "循環系統": ["心臟", "動脈", "靜脈", "心搏輸出量"],
        "消化系統": ["胃酸", "消化酶", "蠕動", "十二指腸"],
        "生殖系統": ["卵巢", "子宮", "精子", "排卵"],
    }
    
    print(f"\n總計 {len(MEDICAL_TERMS)} 個專業術語\n")
    
    for system, terms in systems.items():
        print(f"\n【{system}】")
        for term in terms:
            if term in MEDICAL_TERMS:
                print(f"  ✓ {term:<12} → {MEDICAL_TERMS[term]}")
            else:
                print(f"  ✗ {term:<12} → (未找到)")
    
    print("\n" + "="*60)


def test_translation_sample():
    """測試翻譯功能（示例句子）"""
    print("\n生理醫學翻譯功能測試")
    print("="*60)
    
    # 測試句子（包含多個醫學術語）
    test_sentences = [
        "神經元透過突觸傳遞神經傳導物質",
        "心臟的心搏輸出量會影響血壓",
        "肺泡是進行氣體交換的主要場所",
        "胰島素和升糖素共同調節血糖恆定性",
        "動作電位的產生需要去極化過程",
    ]
    
    print("\n初始化翻譯器（Google Translate + 醫學術語優化）...")
    try:
        translator = SubtitleTranslator(api_provider="google")
        
        print("\n開始翻譯測試句子：\n")
        
        for i, sentence in enumerate(test_sentences, 1):
            print(f"{i}. 原文: {sentence}")
            
            # 翻譯
            translations = translator._translate_batch([sentence])
            
            if translations:
                print(f"   翻譯: {translations[0]}")
                
                # 檢查關鍵術語
                terms_found = []
                for zh_term, en_term in MEDICAL_TERMS.items():
                    if zh_term in sentence and en_term.lower() in translations[0].lower():
                        terms_found.append(f"{zh_term}→{en_term}")
                
                if terms_found:
                    print(f"   ✓ 術語: {', '.join(terms_found)}")
            
            print()
        
        print("="*60)
        print("✅ 翻譯功能測試完成！")
        print("="*60)
    
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        print("\n請確保已安裝 deep-translator:")
        print("  pip install deep-translator")


def test_term_coverage():
    """測試術語涵蓋範圍"""
    print("\n術語涵蓋範圍分析")
    print("="*60)
    
    categories = {
        "系統名稱": ["神經系統", "循環系統", "呼吸系統", "消化系統", "內分泌系統", "生殖系統"],
        "器官": ["心臟", "肺臟", "肝臟", "腎臟", "胃", "腸道"],
        "細胞/組織": ["神經元", "紅血球", "白血球", "細胞", "組織"],
        "生理過程": ["代謝", "恆定性", "氣體交換", "蠕動", "排卵"],
        "化學物質": ["激素", "酵素", "神經傳導物質", "胰島素", "葡萄糖"],
    }
    
    total = 0
    covered = 0
    
    for category, terms in categories.items():
        count = sum(1 for term in terms if term in MEDICAL_TERMS)
        total += len(terms)
        covered += count
        coverage = (count / len(terms)) * 100
        print(f"\n{category}: {count}/{len(terms)} ({coverage:.0f}%)")
        for term in terms:
            status = "✓" if term in MEDICAL_TERMS else "✗"
            print(f"  {status} {term}")
    
    print("\n" + "="*60)
    print(f"總涵蓋率: {covered}/{total} ({(covered/total)*100:.1f}%)")
    print("="*60)


if __name__ == "__main__":
    import sys
    
    print("\n🎓 生理醫學翻譯系統 - 術語測試\n")
    
    # 測試 1: 術語對照表
    test_medical_terms()
    
    # 測試 2: 術語涵蓋範圍
    test_term_coverage()
    
    # 測試 3: 實際翻譯功能（需要網路）
    print("\n是否要測試實際翻譯功能？（需要網路連線）")
    print("按 Enter 繼續，或 Ctrl+C 取消...")
    
    try:
        input()
        test_translation_sample()
    except KeyboardInterrupt:
        print("\n\n已跳過翻譯測試。")
    
    print("\n✨ 所有測試完成！\n")
