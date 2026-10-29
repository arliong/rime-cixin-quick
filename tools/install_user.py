# -*- coding: utf-8 -*-
"""
慈心速成 一鍵安裝腳本（v1.3.0）

上游 philipposkhos/rime-ms-quick 已於 2026-10-28 加入 MIT License，
並於 issue #5 明示授權本專案使用、修改及再分發其單字碼表。
因此本倉庫【直接內含】合併後的完整碼表，本腳本不再需要聯網下載上游。

本腳本會：
  1. 把 schema、合併詞典、lua 組件部署到 %APPDATA%\\Rime\\；
  2. 以「追加」寫法把 cixin_quick 註冊進 default.custom.yaml 的 schema_list
     （不覆蓋使用者既有內容；改動前自動備份）。

用法：
  python tools/install_user.py              # 部署 + 註冊方案
  python tools/install_user.py --no-register # 只部署，不動 default.custom.yaml
  python tools/install_user.py --dry-run     # 只顯示將要做的動作

需要：Python 3.8+；部署後請在小狼毫中「重新部署」。
"""
import argparse
import io
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
RIME_USER = os.path.join(os.environ.get("APPDATA", ""), "Rime")

# 需要部署的檔案（相對於倉庫根）
FILES = [
    "cixin_quick.schema.yaml",
    "cixin_quick.dict.yaml",
]
LUA_DIR = "lua"

# 要註冊的方案
# 拼音反查 / 筆畫反查所需的 luna_pinyin、stroke 詞典，
# 已由 cixin_quick.schema.yaml 的 schema/dependencies 自動編譯，
# 不需要（也不建議）把它們塞進使用者的方案清單。
SCHEMAS = ["cixin_quick"]


def log(msg):
    print(msg)


def deploy_files(dry_run=False):
    """把 schema / dict / lua 複製到 Rime 使用者目錄。"""
    os.makedirs(RIME_USER, exist_ok=True)
    for name in FILES:
        src = os.path.join(REPO, name)
        dst = os.path.join(RIME_USER, name)
        if not os.path.exists(src):
            raise SystemExit("缺少 %s（倉庫內容不完整？）" % src)
        if dry_run:
            log("  [dry-run] %s  ->  %s" % (name, dst))
            continue
        shutil.copy(src, dst)
        log("  [部署] %s" % name)

    # ⚠️ Lua 模組必須位於用戶目錄的 lua\\ 子資料夾（require 只搜那裡）
    lua_src = os.path.join(REPO, LUA_DIR)
    lua_dst = os.path.join(RIME_USER, LUA_DIR)
    if not os.path.isdir(lua_src):
        raise SystemExit("缺少 %s" % lua_src)
    if not dry_run:
        os.makedirs(lua_dst, exist_ok=True)
    for f in sorted(os.listdir(lua_src)):
        if not f.endswith(".lua"):
            continue
        if dry_run:
            log("  [dry-run] %s\\%s  ->  %s" % (LUA_DIR, f, lua_dst))
            continue
        shutil.copy(os.path.join(lua_src, f), os.path.join(lua_dst, f))
        log("  [部署] %s\\%s" % (LUA_DIR, f))


def _indent_of(line):
    return len(line) - len(line.lstrip(" "))


def register_schemas(dry_run=False):
    """把 SCHEMAS 以「追加」寫法併入 default.custom.yaml 的 patch/schema_list。

    原則：只做「插入」，不刪、不改既有行；改動前先備份 .bak。
    遇到無法安全解析的寫法（如 __patch / __merge 風格）則不動檔案，改為提示。
    """
    path = os.path.join(RIME_USER, "default.custom.yaml")
    entries = ["- schema: %s" % s for s in SCHEMAS]

    if not os.path.exists(path):
        content = (
            "# encoding: utf-8\n"
            "# 慈心速成 安裝輔助（由 tools/install_user.py 產生）\n"
            "patch:\n"
            '  "schema_list/+":\n'
            + "".join("    %s\n" % e for e in entries)
        )
        if dry_run:
            log("  [dry-run] 將建立 default.custom.yaml")
            return True
        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        log("  [建立] default.custom.yaml")
        return True

    with io.open(path, "r", encoding="utf-8") as f:
        text = f.read()
    lines = text.replace("\r\n", "\n").split("\n")

    # 已註冊過就不動
    if any(re.search(r"schema:\s*%s\s*$" % re.escape(s), l) for l in lines for s in SCHEMAS):
        log("  [跳過] schema_list 已含 cixin_quick")
        return True

    # __patch / __merge 風格無法安全就地編輯 → 不動檔案
    if re.search(r"^(__patch|__merge|__append)\s*:", text, re.M):
        log("  [提示] 偵測到 __patch/__merge 風格設定，為安全起見未修改 default.custom.yaml。")
        log("         請手動在 schema_list 中加入：")
        for e in entries:
            log("           %s" % e)
        return False

    # 找 patch: 底下的 schema_list:
    patch_idx = None
    for i, l in enumerate(lines):
        if re.match(r"^patch\s*:\s*$", l):
            patch_idx = i
            break
    if patch_idx is None:
        # 沒有 patch: 節點 → 整段追加
        if dry_run:
            log("  [dry-run] 將在 default.custom.yaml 末尾追加 patch 節點")
            return True
        backup(path)
        add = ["patch:", '  "schema_list/+":'] + ["    " + e for e in entries]
        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text.rstrip("\n") + "\n" + "\n".join(add) + "\n")
        log("  [更新] default.custom.yaml：已追加 patch/schema_list")
        return True

    # 在 patch: 區塊內找 schema_list:
    list_idx = None
    for i in range(patch_idx + 1, len(lines)):
        l = lines[i]
        if l.strip() and _indent_of(l) == 0:
            break  # 離開 patch: 區塊
        m = re.match(r'^(\s*)"?schema_list"?\s*:\s*$', l)
        if m:
            list_idx = i
            list_indent = len(m.group(1))
            break
    if list_idx is None:
        # patch: 存在但沒有 schema_list → 在 patch: 下插入
        if dry_run:
            log("  [dry-run] 將在 patch: 下插入 schema_list")
            return True
        backup(path)
        ins = ['  "schema_list/+":'] + ["    " + e for e in entries]
        lines[patch_idx + 1:patch_idx + 1] = ins
        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(lines))
        log("  [更新] default.custom.yaml：已插入 patch/schema_list")
        return True

    # 已有 schema_list → 在其列表末尾追加條目
    item_indent = None
    end = len(lines)
    for i in range(list_idx + 1, len(lines)):
        l = lines[i]
        if not l.strip():
            continue
        ind = _indent_of(l)
        if ind <= list_indent:
            end = i
            break
        if item_indent is None and l.lstrip().startswith("- "):
            item_indent = ind
    if item_indent is None:
        item_indent = list_indent + 2
    if dry_run:
        log("  [dry-run] 將在 schema_list 末尾追加 %d 條" % len(entries))
        return True
    backup(path)
    add = [" " * item_indent + e for e in entries]
    lines[end:end] = add
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))
    log("  [更新] default.custom.yaml：schema_list 已追加 %d 條" % len(entries))
    return True


def backup(path):
    bak = path + ".bak"
    shutil.copy(path, bak)
    log("  [備份] %s" % bak)


def main():
    ap = argparse.ArgumentParser(description="慈心速成 一鍵安裝")
    ap.add_argument("--no-register", action="store_true", help="不修改 default.custom.yaml")
    ap.add_argument("--dry-run", action="store_true", help="只顯示動作，不實際寫檔")
    args = ap.parse_args()

    log("== 慈心速成 安裝 ==")
    log("Rime 使用者目錄: %s" % RIME_USER)
    log("-- 部署方案檔案 --")
    deploy_files(dry_run=args.dry_run)

    if not args.no_register:
        log("-- 註冊方案 --")
        register_schemas(dry_run=args.dry_run)

    log(
        "\n完成。接下來：\n"
        "  1. 打開「【小狼毫】輸入法設定」（開始選單）；\n"
        "  2. 勾選「慈心速成」，點「重新部署」；\n"
        "  3. 首次部署需編譯 84,999 條碼表，請稍等數秒。\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
