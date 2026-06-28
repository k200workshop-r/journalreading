# 臨床文獻 → 院內模板簡報

住院醫師上傳論文 PDF → 選科別與設定 → AI 依「該科評讀要點」整理重點 →
直接套用院內 **50 週年模板底版** 產生 PowerPoint（.pptx）下載。

每一頁都由模板的版面配置建立，所以**每份簡報都是同一個院內底版**；
張數不受 NotebookLM 限制；API 金鑰放在伺服器端，安全。

## 檔案

| 檔案 | 用途 |
|------|------|
| `app.py` | Flask 後端：首頁 + `/api/generate` |
| `llm.py` | 呼叫 Claude，依科別產生投影片大綱（含 16 科要點對照表） |
| `pptx_builder.py` | 用 python-pptx 把大綱套到院內模板 |
| `static/index.html` | 前端（大地色系；瀏覽器端擷取 PDF 文字） |
| `template.pptx` | **院內 50 週年模板**（已內含；要換版型時直接替換這個檔） |
| `requirements.txt` / `render.yaml` | 部署設定 |

## 本機測試

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python app.py            # 開 http://localhost:5000
```

## 部署到 Render

1. 把這個資料夾推到一個 GitHub repo。
2. Render → New → **Web Service** → 連到該 repo（會自動讀 `render.yaml`）。
3. 部署後到該服務的 **Environment** 分頁，新增環境變數
   `ANTHROPIC_API_KEY` = 你的 Anthropic 金鑰（Render 後台填，不要寫進程式或 git）。
4. 完成。網址即可給住院醫師使用。

> 也可部署到其他支援 Python 的平台；Netlify 純前端不適合（需 Python 後端跑 python-pptx）。

## 要調整的地方

- **換模板版型**：替換 `template.pptx` 即可。若新模板的版面配置順序不同，
  到 `pptx_builder.py` 調 `LAYOUT_TITLE` / `LAYOUT_CONTENT`（目前：封面=0、內頁=2）。
- **改科別要點**：編輯 `llm.py` 的 `SPECIALTY_POINTS`。
- **每頁項目上限**：`pptx_builder.py` 的 `MAX_BULLETS_PER_SLIDE`（預設 6，超過自動分頁）。

## 備註

- 需使用「含可選取文字」的 PDF；掃描影像檔需先 OCR。
- 論文文字在瀏覽器端擷取後才送出，PDF 本身不會上傳。
