import os
import pandas as pd
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(BASE_DIR, "..", "data", "all_youtube_comments.xlsx")

PER_PAGE = 20

# --------------------------
# Load data sekali saat server start
# --------------------------
df_master = pd.read_excel(EXCEL_PATH)
if "label" not in df_master.columns:
    df_master["label"] = ""

# Shuffle data sekali saja
df_master = df_master.sample(frac=1, random_state=42).reset_index(drop=True)

# Simpan perubahan sementara di server memory
local_labels = {}  # {index: label}
# --------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get_data")
def get_data():
    page = int(request.args.get("page", 1))
    
    start = (page - 1) * PER_PAGE
    end = start + PER_PAGE

    data = df_master.iloc[start:end].copy()

    # Override dengan local_labels jika ada
    for idx in range(start, end):
        if idx in local_labels:
            data.at[idx, "label"] = local_labels[idx]

    # Tambahkan index asli
    data = data.fillna("").reset_index()
    data = data.rename(columns={"index": "idx"})
    data_list = data.to_dict(orient="records")

    # Hitung stats realtime
    stats_df = df_master.copy()
    for idx, label in local_labels.items():
        stats_df.at[idx, "label"] = label

    stats = {
        "total": len(stats_df),
        "-1": int((stats_df["label"] == -1).sum()),
        "0": int((stats_df["label"] == 0).sum()),
        "1": int((stats_df["label"] == 1).sum()),
    }

    return jsonify({
        "data": data_list,
        "stats": stats
    })


@app.route("/update_label", methods=["POST"])
def update_label():
    payload = request.json

    # Bulk save ke Excel
    if "bulk" in payload:
        for idx_str, label in payload["bulk"].items():
            idx = int(idx_str)
            df_master.at[idx, "label"] = label
        df_master.to_excel(EXCEL_PATH, index=False)
        local_labels.clear()
        return jsonify({"status": "success"})
    
    # Update single label (simpan di memory dulu)
    idx = payload["index"]
    label = payload["label"]
    local_labels[idx] = label
    return jsonify({"status": "success"})


if __name__ == "__main__":
    app.run(debug=True)
