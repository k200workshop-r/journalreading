"""
臨床文獻 → 院內模板簡報　後端（Flask）
- 前端在瀏覽器擷取 PDF 文字後，POST 純文字到 /api/generate
- 後端呼叫 Claude 產生投影片大綱，再用 python-pptx 套用院內 50 週年模板，回傳 .pptx
"""
import os
import datetime
from flask import Flask, request, send_file, jsonify, send_from_directory

from llm import generate_deck
from pptx_builder import build_deck

app = Flask(__name__, static_folder="static", static_url_path="")
TEMPLATE_PATH = os.environ.get("PPTX_TEMPLATE", "template.pptx")


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/generate", methods=["POST"])
def api_generate():
    data = request.get_json(force=True, silent=True) or {}
    paper_text = (data.get("paperText") or "").strip()
    if len(paper_text) < 200:
        return jsonify({"error": "論文文字過短或未擷取到，請確認是含文字的 PDF。"}), 400

    specialty = data.get("specialty") or "內科部"
    audiences = data.get("audiences") or "住院醫師"
    language = data.get("language") or "中文"
    slide_count = int(data.get("slideCount") or 15)
    deck_style = data.get("deckStyle") or "詳細版"
    focus_note = data.get("focusNote") or ""
    reporter = data.get("reporter") or "__________"

    try:
        deck = generate_deck(paper_text, specialty, audiences, language,
                             slide_count, deck_style, focus_note)
    except Exception as e:
        return jsonify({"error": f"產生大綱失敗：{e}"}), 502

    deck["subtitle"] = f"報告者：{reporter}　|　對象：{audiences}　|　科別：{specialty}"

    try:
        buf = build_deck(deck, TEMPLATE_PATH)
    except Exception as e:
        return jsonify({"error": f"套用模板失敗：{e}"}), 500

    stamp = datetime.datetime.now().strftime("%Y%m%d")
    title = (deck.get("title") or "JournalReading")[:40]
    fname = f"{title}_{stamp}.pptx"
    return send_file(
        buf,
        mimetype="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        as_attachment=True,
        download_name=fname,
    )


@app.route("/healthz")
def healthz():
    return "ok", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
