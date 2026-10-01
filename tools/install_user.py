# -*- coding: utf-8 -*-
"""
慈心速成 一鍵安裝腳本（乾淨安裝 / 方案 A）

本倉庫依授權原則【不再分發】上游單字碼表（見 NOTICE.md）。
本腳本會：
  1. 從上游 GitHub 下載 ms_quick.dict.yaml（單字碼表）；
  2. 與本倉庫的詞組聯想表合併生成 cixin_quick.dict.yaml；
  3. 把 schema、lua、合併詞典部署到 %APPDATA%\\Rime\\；
  4. 提示如何在用戶配置中註冊方案。

用法：
  python install_user.py            # 完整安裝（含下載上游碼表）
  python install_user.py --offline  # 離線模式：自行放置 ms_quick.dict.yaml 到當前目錄

需要：Python 3.8+；部署後請在小狼毫中「重新部署」。
"""
import argparse
import io
import os
import shutil
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
RIME_USER = os.path.join(os.environ.get("APPDATA", ""), "Rime")

UPSTREAM_URLS = [
    # 上游 master 的單字碼表（該文件版權歸上游作者，僅下載使用、不再分發）
    "https://raw.githubusercontent.com/philipposkhos/rime-ms-quick/master/ms_quick.dict.yaml",
    "https://github.com/philipposkhos/rime-ms-quick/raw/master/ms_quick.dict.yaml",
]
LOCAL_FALLBACK = "ms_quick.dict.yaml"   # --offline 模式：放到本腳本同目錄


def fetch_upstream() -> str:
    last_err = None
    for url in UPSTREAM_URLS:
        try:
            print("downloading:", url)
            req = urllib.request.Request(url, headers={"User-Agent": "rime-cixin-quick-installer/1.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            return data.decode("utf-8")
        except Exception as e:  # noqa: BLE001
            print("  failed:", e)
            last_err = e
    raise SystemExit(
        "無法下載上游碼表（%s）。\n"
        "可手動從 https://github.com/philipposkhos/rime-ms-quick 下載\n"
        "ms_quick.dict.yaml 放到本腳本目錄後，執行： python install_user.py --offline" % last_err
    )


def split_dict(text: str):
    """RIME 詞典檔 → (meta 區文本, 正文行列表)。meta = 第一個 --- 到 ... 之間。"""
    lines = text.replace("\r\n", "\n").split("\n")
    i1 = lines.index("---")
    i2 = lines.index("...", i1)
    return lines[i1:i2 + 1], lines[i2 + 1:]


def build_merged(upstream_text: str, phrases_text: str) -> str:
    up_meta, up_body = split_dict(upstream_text)
    ph_meta, ph_body = split_dict(phrases_text)
    head = [
        "# encoding: utf-8",
        "# 慈心速成 合併碼表：單字速成排位（源自 philipposkhos/rime-ms-quick，由",
        "#   install_user.py 自上游下載合併）＋ 詞組聯想詞表（本項目自動生成，",
        "#   衍生自 rime/rime-essay，LGPL-3.0）。生成：python tools/install_user.py",
        "---",
        "name: cixin_quick",
        'version: "1.2.0"',
        "sort: original",
        "use_preset_vocabulary: false",
        "...",
        "",
    ]
    return "\n".join(head + [ln for ln in up_body if ln.strip()] + [ln for ln in ph_body if ln.strip()]) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true", help="使用本地的 ms_quick.dict.yaml，不下載")
    args = ap.parse_args()

    if args.offline:
        src = os.path.join(HERE, LOCAL_FALLBACK)
        if not os.path.exists(src):
            raise SystemExit("找不到 %s，請先從上游下載放置" % src)
        upstream_text = io.open(src, encoding="utf-8").read()
    else:
        upstream_text = fetch_upstream()

    ph_path = os.path.join(REPO, "dict", "cixin_quick_phrases.dict.yaml")
    phrases_text = io.open(ph_path, encoding="utf-8").read()

    merged = build_merged(upstream_text, phrases_text)
    print("merged entries ok, chars:", len(merged))

    os.makedirs(RIME_USER, exist_ok=True)
    shutil.copy(os.path.join(REPO, "schema", "cixin_quick.schema.yaml"), RIME_USER)
    shutil.copy(os.path.join(REPO, "schema", "default.custom.yaml"), RIME_USER)
    for f in os.listdir(os.path.join(REPO, "lua")):
        shutil.copy(os.path.join(REPO, "lua", f), RIME_USER)
    out_dict = os.path.join(RIME_USER, "cixin_quick.dict.yaml")
    io.open(out_dict, "w", encoding="utf-8", newline="\n").write(merged)
    print("deployed to:", RIME_USER)

    print(
        "\n完成。接下來：\n"
        "  1. 打開「【小狼毫】輸入法設定」（開始選單）；\n"
        "  2. 勾選「慈心速成」，點「重新部署」；\n"
        "  3. 若 default.custom.yaml 已有自己的配置，請手動把 - {schema: cixin_quick}\n"
        "     加進 schema_list，而不要用本倉庫的 default.custom.yaml 覆蓋。\n"
    )


if __name__ == "__main__":
    main()
