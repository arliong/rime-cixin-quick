# -*- coding: utf-8 -*-
"""
生成《傳統速成》詞組聯想詞典 ms_quick_phrases.dict.yaml
方法：
  1. 從 ms_quick.dict.yaml 建立「單字 -> 速成碼」對照表
  2. 從 RIME 自帶的 essay.txt（繁體詞頻表）取出高頻 2/3 字詞
  3. 把每個詞的每個字換成速成碼，拼接成詞碼；任一字查不到速成碼則捨棄
  4. 輸出獨立詞典，供 ms_quick.schema.yaml 以 dict_import 併入主碼表，
     並由 predictor 做「詞組聯想（聯想字 / shift+數字）」
"""
import os

MS_QUICK = r"D:\download\2c搬迁\rime-ms-quick-master\ms_quick.dict.yaml"
ESSAY   = r"C:\Program Files\Rime\weasel-0.17.4\data\essay.txt"
OUT      = r"C:\Users\Administrator\AppData\Roaming\Rime\ms_quick_phrases.dict.yaml"

TOP2 = 60000      # 取詞頻最高的 2 字詞數量
MIN3_WEIGHT = 2000
TOP3 = 20000      # 取詞頻較高的 3 字詞數量

# 1) 單字 -> 速成碼
charmap = {}
with open(MS_QUICK, encoding="utf-8-sig") as f:
    in_body = False
    for line in f:
        line = line.rstrip("\n")
        if line.strip() == "...":
            in_body = True
            continue
        if not in_body:
            continue
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        ch, code = parts[0], parts[1].strip()
        if len(ch) == 1 and ch not in charmap:
            charmap[ch] = code

print("單字對照表大小:", len(charmap))

# 2) 讀 essay.txt，收集 2/3 字詞與詞頻
bi = []   # (weight, word)
tri = []
with open(ESSAY, encoding="utf-8") as f:
    for line in f:
        line = line.rstrip("\n")
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        w = parts[0]
        try:
            wt = int(parts[1])
        except ValueError:
            continue
        if len(w) == 2:
            bi.append((wt, w))
        elif len(w) == 3 and wt >= MIN3_WEIGHT:
            tri.append((wt, w))

bi.sort(reverse=True)
tri.sort(reverse=True)
bi = bi[:TOP2]
tri = tri[:TOP3]
print("候選 2字詞:", len(bi), " 3字詞:", len(tri))

# 3) 映射成速成詞碼
def to_code(word):
    codes = [charmap.get(c) for c in word]
    if any(c is None for c in codes):
        return None
    return "".join(codes)

seen = set()
entries = []
for wt, w in bi + tri:
    if w in seen:
        continue
    code = to_code(w)
    if code is None:
        continue
    seen.add(w)
    entries.append((w, code))

# 4) 輸出
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write("# encoding: utf-8\n")
    f.write("# 傳統速成 詞組聯想詞典（由 essay.txt 詞頻 + ms_quick 速成碼自動生成）\n")
    f.write("# 生成指令：python build_phrases.py\n")
    f.write("---\n")
    f.write("name: ms_quick_phrases\n")
    f.write('version: "1.0"\n')
    f.write("sort: original\n")
    f.write("use_preset_vocabulary: false\n")
    f.write("---\n")
    for w, code in entries:
        f.write(f"{w}\t{code}\n")

print("已寫出詞組條目:", len(entries))
print("範例：")
for w in ["什麼", "中國", "我們", "你好", "朋友", "時間"]:
    for ww, c in entries:
        if ww == w:
            print("  ", ww, "->", c)
            break
