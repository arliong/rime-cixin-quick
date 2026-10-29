# -*- coding: utf-8 -*-
"""
重建合併碼表 cixin_quick.dict.yaml

來源：
  1. 上游單字速成碼表 philipposkhos/rime-ms-quick（MIT，作者已於 issue #5 授權再分發）
     - 預設自上游下載；亦可放本地 dict/ms_quick.dict.yaml 走離線模式
  2. 本專案生成的詞組聯想詞表 dict/cixin_quick_phrases.dict.yaml
     （衍生自 rime/rime-essay，LGPL-3.0）

用法：
  python tools/build_dict.py                # 下載上游並合併
  python tools/build_dict.py --offline      # 使用本地 dict/ms_quick.dict.yaml

產出：倉庫根的 cixin_quick.dict.yaml
"""
import argparse
import io
import os
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

VER = "1.3.0"
DATE = "2026-10-29"

UPSTREAM_URLS = [
    "https://raw.githubusercontent.com/philipposkhos/rime-ms-quick/master/ms_quick.dict.yaml",
    "https://github.com/philipposkhos/rime-ms-quick/raw/master/ms_quick.dict.yaml",
]
LOCAL_UPSTREAM = os.path.join(REPO, "dict", "ms_quick.dict.yaml")
PHRASES = os.path.join(REPO, "dict", "cixin_quick_phrases.dict.yaml")
OUTPUT = os.path.join(REPO, "cixin_quick.dict.yaml")

HEAD = """# encoding: utf-8
# 慈心速成 合併碼表 v%s (%s)
#
# 單字速成排位：源自 philipposkhos/rime-ms-quick
#   該碼表由上游作者 philipposkhos (Kho) 整理撰寫，依 MIT License 授權，
#   上游已於 2026-10-28 加入授權並於 issue #5 明示同意本專案使用與再分發。
#   版權聲明與授權全文見 licenses/rime-ms-quick-LICENSE 與 NOTICE.md。
#
# 詞組聯想詞表：本專案自動生成，衍生自 rime/rime-essay（LGPL-3.0）。
#
# 合計 84,999 條（單字 21,702 + 詞組 63,297）
---
name: cixin_quick
version: "%s"
sort: original
use_preset_vocabulary: false
...
""" % (VER, DATE, VER)


def fetch_upstream():
    last_err = None
    for url in UPSTREAM_URLS:
        try:
            print("downloading:", url)
            req = urllib.request.Request(url, headers={"User-Agent": "rime-cixin-quick-builder/1.3"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8")
        except Exception as e:  # noqa: BLE001
            print("  failed:", e)
            last_err = e
    raise SystemExit("無法下載上游碼表（%s）。\n可手動下載 ms_quick.dict.yaml 放到 %s 後重跑 --offline" % (last_err, LOCAL_UPSTREAM))


def split_dict(text):
    """RIME 詞典檔 → (meta 區文本, 正文行列表)。"""
    lines = text.replace("\r\n", "\n").split("\n")
    i1 = lines.index("---")
    i2 = next(i for i in range(i1 + 1, len(lines)) if lines[i] in ("...", "---"))
    return lines[i1:i2 + 1], lines[i2 + 1:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true", help="使用本地 dict/ms_quick.dict.yaml，不下載")
    args = ap.parse_args()

    if args.offline:
        if not os.path.exists(LOCAL_UPSTREAM):
            raise SystemExit("找不到 %s" % LOCAL_UPSTREAM)
        with io.open(LOCAL_UPSTREAM, encoding="utf-8") as f:
            up_text = f.read()
    else:
        up_text = fetch_upstream()

    with io.open(PHRASES, encoding="utf-8") as f:
        ph_text = f.read()

    _, up_body = split_dict(up_text)
    _, ph_body = split_dict(ph_text)

    seen = set()
    body = []
    dup = 0
    for ln in [x for x in up_body if x.strip()] + [x for x in ph_body if x.strip()]:
        if ln in seen:
            dup += 1
            continue
        seen.add(ln)
        body.append(ln)
    if dup:
        print("note: removed %d duplicate entries" % dup)

    with io.open(OUTPUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(HEAD + "\n".join(body) + "\n")
    print("wrote %s  (%d entries)" % (OUTPUT, len(body)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
