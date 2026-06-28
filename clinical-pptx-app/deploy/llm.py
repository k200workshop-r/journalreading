"""呼叫 Anthropic API，把論文文字 + 科別/設定 轉成投影片大綱（deck JSON）。"""
import os
import json
import requests

API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-6"

SPECIALTY_POINTS = {
    "內科部": [
        "運用實證醫學於疾病診斷與治療決策之能力。",
        "更新心臟內科、感染科、新陳代謝科、腎臟內科、過敏免疫風濕科、消化內科、胸腔內科、血液腫瘤科等次專科新知識。",
        "分析 RCT、Meta-analysis 及 Clinical Guideline。",
        "比較不同治療策略之成效與安全性。",
        "培養研究設計與統計判讀能力。",
        "將研究結果轉換為臨床照護決策。",
        "批判性文獻分析能力。",
    ],
    "外科部": [
        "評估新手術技術之適用性與安全性。",
        "建立病人安全及品質改善觀念。",
        "評析手術結果與併發症研究。",
        "學習 ERAS、微創技術及機器手臂手術新知識。",
        "強化術前風險評估及術後照護能力需求。",
    ],
    "皮膚科": [
        "了解國際最新治療指引更新狀況。",
        "培養病理與臨床整合能力及知識。",
        "評估新藥及生物製劑之療效與安全性。",
        "分析各種皮膚症狀與病灶的治療新知。",
        "強化皮膚病理判讀能力。",
        "評估長期追蹤與預後研究。",
    ],
    "耳鼻喉科": [
        "提升耳鼻喉科與跨科部手術整合與決策能力。",
        "評估新型手術技術及治療方式。",
        "頭頸癌治療策略、最新狀況與新知。",
        "評估耳科及鼻竇手術相關成果及研究報告。",
        "（若剛好有需要）學習睡眠醫學相關之研究。",
        "最新頭頸癌疾病診斷、治療及相關預後方式。",
    ],
    "泌尿科": [
        "泌尿系統疾病診治之實證能力。",
        "分析泌尿腫瘤與治療相關之研究及微創手術新知。",
        "評估新型機械手臂或機械手臂之手術成果，並強化手術品質改善。",
        "更新尿路結石等泌尿常見症狀（例如：排尿障礙、勃起障礙等）之治療策略。",
    ],
    "放射腫瘤科": [
        "了解腫瘤放射治療與跨團隊癌症照護最新證據。",
        "評估放療技術與臨床結果。",
        "分析 IMRT、VMAT、SBRT 研究。",
        "評估免疫治療與放療整合策略。",
        "學習治療毒性與生活品質之研究。",
    ],
    "安寧緩和科": [
        "了解以病人為中心之緩和醫療實證照護能力。",
        "學習疼痛控制新知。",
        "探討預立醫療決定及 ACP 相關之研究。",
        "分析生命末期照護品質指標。",
    ],
    "影像醫學部": [
        "了解影像診斷與醫學影像創新應用能力。",
        "評估 MRI、CT、超音波新機器與新技術。",
        "分析 AI 影像輔助診斷研究。",
        "強化影像與病理對照能力範圍。",
    ],
    "復健醫學部": [
        "提升功能恢復與生活品質改善之實證能力。",
        "分析神經復健相關之研究。",
        "評估肌肉骨骼超音波之應用與新型機種。",
        "分析機器人與智慧復健技術相關研究之優缺點或顯著性。",
    ],
    "婦產科": [
        "了解婦女健康與週產期照護之實證能力。",
        "分析高危險妊娠研究。",
        "評估微創婦科手術成果、了解達文西手臂技術之新知。",
        "更新生殖醫學及不孕症治療之策略及研究。",
    ],
    "小兒科": [
        "了解兒童照護與發展醫學之實證照護能力。",
        "分析疫苗與感染症狀之相關研究。",
        "更新兒童慢性疾病管理策略。",
        "評估兒童發展相關研究。",
        "探討兒童腫瘤、兒童癌症之治療流程與術後評估的新知與相關研究。",
    ],
    "神經外科": [
        "分析腦瘤與脊椎手術相關之研究。",
        "評估導航及機器人手臂之手術新型技術及當前技術。",
        "神經重症照護策略指引。",
        "評估術後病人預後研究。",
    ],
    "神經內科": [
        "神經疾病最新治療策略。",
        "分析各種神經內科症狀之相關研究細節。",
        "評估神經退化疾病新療法、藥物治療。",
        "神經影像與生物標記之應用。",
    ],
    "急診醫學科": [
        "最新創傷與重症醫學之研究。",
        "分析急診流程改善之相關研究與制度。",
        "評估 POCUS 及 AI 可應用及急重症場域發展之可能性。",
        "培養快速判讀證據能力。",
        "分析急重症病人即時決策與處置能力。",
    ],
    "骨科部": [
        "了解骨骼肌肉疾病治療與手術品質。",
        "評估每項手術之成效與併發症。",
        "分析關節置換研究相關之探討與預後可能性。",
        "更新運動醫學與創傷治療策略之應對。",
        "評估新型植入物與技術之預後狀況及可能的排斥反應。",
    ],
    "家庭醫學科": [
        "著重預防醫學與健康促進。",
        "評估慢性病管理研究。",
        "分析、篩檢健康促進之成效。",
        "探討社區整合照護模式。",
    ],
}

LANG_RULE = {
    "中文": "全部用繁體中文。",
    "English": "Write everything in English.",
    "中英對照": "每個項目先繁體中文，再附精簡英文。",
}


def _lang_rule(language):
    return LANG_RULE.get(language, LANG_RULE["中文"])


def build_prompt(paper_text, specialty, audiences, language, slide_count, deck_style, focus_note):
    pts = SPECIALTY_POINTS.get(specialty)
    pts_block = ""
    if pts:
        pts_block = "\n\n【此科別必整理的評讀要點】請以下列要點為核心優先涵蓋（論文未涉及者略過、不要杜撰）：\n" + \
            "\n".join("- " + p for p in pts)
    content_n = max(3, int(slide_count) - 1)  # 扣掉標題頁
    style_hint = "每頁資訊較完整、可單獨閱讀。" if deck_style == "詳細版" else "每頁只放關鍵 talking points、精簡。"
    focus = f"\n使用者特別希望著重：{focus_note}。" if focus_note else ""
    return f"""你是嚴謹的醫學教育與臨床文獻分析助手，正在協助「{specialty}」的住院醫師把一篇論文/期刊做成 Journal Reading 投影片，供 {audiences} 教學使用。

請以「{specialty}」的臨床視角閱讀下方論文全文，整理成一份投影片大綱。{focus}{pts_block}

要求：
- 語言：{_lang_rule(language)}
- 風格：{style_hint}
- 內容頁數請約 {content_n} 頁（不含標題頁）。建議第一頁為「大綱」，接著依序：研究背景與臨床問題、研究方法、主要結果與關鍵數據、對「{specialty}」臨床決策的意義、教學討論要點、研究限制與結論。
- 每頁 3–6 個重點，每點一句話、精準可信，用自己的話、不要照抄整段原文。
- 教學討論要點請符合「{audiences}」的程度。

只回傳一個 JSON 物件（不要 markdown、不要前後說明）：
{{
  "title": "論文標題（找不到就用簡短主題）",
  "slides": [
    {{"title": "大綱", "bullets": ["...", "..."]}},
    {{"title": "研究背景與臨床問題", "bullets": ["...", "..."]}}
  ]
}}

=== 論文全文（擷取自 PDF）===
{paper_text[:45000]}"""


def _extract_json(text):
    text = text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(text)
    except Exception:
        s, e = text.find("{"), text.rfind("}")
        if s >= 0 and e > s:
            return json.loads(text[s:e + 1])
        raise


def generate_deck(paper_text, specialty, audiences, language, slide_count, deck_style, focus_note):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("伺服器未設定 ANTHROPIC_API_KEY 環境變數。")
    prompt = build_prompt(paper_text, specialty, audiences, language, slide_count, deck_style, focus_note)
    resp = requests.post(
        API_URL,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={"model": MODEL, "max_tokens": 8000,
              "messages": [{"role": "user", "content": prompt}]},
        timeout=180,
    )
    resp.raise_for_status()
    data = resp.json()
    text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
    deck = _extract_json(text)
    deck.setdefault("title", "Journal Reading")
    deck.setdefault("slides", [])
    return deck
