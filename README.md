# 慈心速成（cixin_quick）

RIME／小狼毫的「微軟傳統速成」增強方案：**保留微軟速成原排位**，
補上 XP 時代速成輸入法最令人懷念的**詞組聯想**，以及打不出字時的
**拼音／筆畫雙通道反查**。

> 本專案基於 [philipposkhos/rime-ms-quick](https://github.com/philipposkhos/rime-ms-quick)
> 的單字碼表發展而來。上游定位為「沒有聯想字」的純傳統速成；本專案的方向
> 正好相反——把 XP 式聯想完整搬回 RIME。
>
> **上游已於 2026-10-28 為該倉庫加入 MIT License，並於
> [issue #5](https://github.com/philipposkhos/rime-ms-quick/issues/5)
> 明示授權本專案使用、修改及再分發其單字碼表。**
> 授權與歸屬詳見 [NOTICE.md](NOTICE.md)。

## 功能

### 1. XP 式盲接聯想（Shift+數字接龍）

上屏一字後，直接按 `Shift+1..9` 聯想下一個字，連續按、連續接，
全程不需要看候選欄——與 Windows XP 傳統速成的操作習慣完全一致：

```
輸入 oj → 選 1 上屏「什」
Shift+1 → 麼        Shift+2 → 邡        Shift+3 → 錦
Shift+4 → 麼的      Shift+5 → 麼是      Shift+6 → 麼兒 …
```

- 詞庫約 63,000 條詞組（由 RIME 官方【八股文】高頻詞 + 速成碼自動生成）
- 聯想過程自動防止重複觸發（keyup 過濾 + 去重）
- `Esc` 取消本次聯想提示；繼續正常打字自動回到輸入狀態

### 2. 候選欄可見聯想

上屏一字後，候選欄立即橫向列出該字的聯想詞，可用數字鍵或**鼠標點選**；
不想聯想就繼續打字，互不干擾。

### 3. 打不出字？拼音／筆畫雙通道反查

反查候選會**自動附註該字的速成碼**，邊打邊學：

| 反查 | 操作 | 示例 |
|------|------|------|
| 拼音反查 | `` ` ``（數字 1 左邊的鍵）+ 拼音 | `` ` ``ren → 人 |
| 筆畫反查 | `'` + 筆畫（h橫 s豎 p撇 n捺 z折） | `'`pn → 人 |

> 兩個反查通道所需的 `luna_pinyin` / `stroke` 詞典，已由
> `cixin_quick.schema.yaml` 的 `schema/dependencies` 宣告，
> **部署時會自動編譯**——不必把它們塞進你自己的方案清單。

## 安裝（Windows 小狼毫）

> 三種安裝方式任選其一，皆**無需自行合併碼表**（本倉庫已內含合併後的完整碼表）。

### 方式 A：東風破 plum 一鍵安裝（推薦）

已裝 [小狼毫 Weasel](https://rime.im/) 者，在 Git Bash／WSL 執行：

```bash
bash rime-install arliong/rime-cixin-quick
```

或用小狼毫的「取得更多輸入方案」對話框，輸入同樣的 `arliong/rime-cixin-quick`。
安裝後「重新部署」，再以 `F4` 或托盤選單切到「慈心速成」。

> plum 會把方案**追加**（`"schema_list/+"`）到你的 `default.custom.yaml`，
> 既有的方案清單與其它自訂項都不會被覆蓋。

### 方式 B：整包 zip（免 Python、免聯網）

1. 從本頁 [Releases](../../releases) 下載 `cixin-quick-vX.Y.Z-full.zip`；
2. 解壓，把**包內根級全部文件**複製到 Rime 用戶目錄
   （開始選單 →「【小狼毫】用戶資料夾」，即 `%APPDATA%\Rime\`）；
3. 若你**已有**自訂 `default.custom.yaml`，**不要覆蓋**——把下面一行併入你的
   `patch/schema_list` 即可（不存在則直接用包內那份）：

   ```yaml
   patch:
     "schema_list/+":
       - schema: cixin_quick
   ```

4. 托盤右鍵 → **重新部署**（首次編譯 84,999 條碼表，稍等數秒），`F4` 選「慈心速成」。

### 方式 C：倉庫腳本安裝

```text
python tools/install_user.py
```

腳本會把方案檔、完整碼表與 Lua 組件部署到 `%APPDATA%\Rime\`，
並以「追加」寫法把方案註冊進 `default.custom.yaml`（改動前自動備份 `.bak`）。
選用參數：`--no-register`（不動 `default.custom.yaml`）、`--dry-run`（只看動作）。

## 倉庫結構

```text
cixin_quick.schema.yaml   方案設定（含 schema/dependencies 反查依賴宣告）
cixin_quick.dict.yaml     合併碼表（單字 21,702 + 詞組 63,297 = 84,999 條）
recipe.yaml               東風破 plum 安裝配方
default.custom.yaml       方案註冊輔助（追加寫法，位於 schema/ 供腳本使用）
lua/                      librime-lua 聯想組件
dict/                     詞組聯想詞表（供 tools/build_phrases.py 重建用）
tools/                    安裝與碼表重建腳本
docs/                     開發文檔
```

## 版本

| 版本 | 日期 | 內容 |
|------|------|------|
| v1.0.0 | 2026-09-27 | XP 式盲接聯想（Shift+1..9 接龍） |
| v1.1.0 | 2026-09-27 | 候選欄可見聯想（上屏後橫向列出、可點選） |
| v1.2.0 | 2026-09-28 | 拼音 `` ` `` ＋筆畫 `'` 雙通道反查，附速成碼注釋 |
| v1.3.0 | 2026-10-29 | 獲上游 MIT 授權；整包直發、plum 一鍵安裝；`schema/dependencies` 自動編譯反查詞典 |

變更細節見 [CHANGELOG.md](CHANGELOG.md)。

## 授權

- 本專案原創代碼：[MIT](LICENSE)
- 詞組詞表：衍生自 [rime/rime-essay](https://github.com/rime/rime-essay)（LGPL-3.0）
- 單字碼表：源自 [rime-ms-quick](https://github.com/philipposkhos/rime-ms-quick)，
  **上游已明示授權再分發**（MIT）——授權全文見
  [licenses/rime-ms-quick-LICENSE](licenses/rime-ms-quick-LICENSE)，
  歸屬說明詳見 [NOTICE.md](NOTICE.md)

## 開發文檔

想了解這個方案是怎麼做出來的、以及 librime-lua 組件開發的完整排雷手冊：

- [docs/03-開發歷程.md](docs/03-開發歷程.md) — 從「什!」到完整聯想的 14 輪調試實錄
- [docs/04-踩坑與解法.md](docs/04-踩坑與解法.md) — 按主題分類的坑與解法（模塊加載、鍵碼、librime API、反查、部署）

## 致謝

- [philipposkhos/rime-ms-quick](https://github.com/philipposkhos/rime-ms-quick) — 微軟傳統速成排位碼表，感謝授權
- [RIME｜中州韻輸入法引擎](https://rime.im/) 與 [librime-lua](https://github.com/hchunhui/librime-lua)
- [rime/rime-essay【八股文】](https://github.com/rime/rime-essay) — 詞頻數據
