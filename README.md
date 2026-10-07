# 慈心速成（cixin_quick）

RIME／小狼毫的「微軟傳統速成」增強方案：**保留微軟速成原排位**，
補上 XP 時代速成輸入法最令人懷念的**詞組聯想**，以及打不出字時的
**拼音／筆畫雙通道反查**。

> 本專案基於 [philipposkhos/rime-ms-quick](https://github.com/philipposkhos/rime-ms-quick)
> 的單字碼表發展而來。上游定位為「沒有聯想字」的純傳統速成；本專案的方向
> 正好相反——把 XP 式聯想完整搬回 RIME。授權與歸屬詳見 [NOTICE.md](NOTICE.md)。

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

## 安裝（Windows 小狼毫）

> 上游碼表未聲明授權，本專案發佈的皆為 **addon 增件包**（不含上游碼表）；
> full 整包將在上游授權後提供。兩種安裝方式按情況二選一：

### 方式 A：腳本安裝（推薦，自動取得上游碼表）

1. 安裝 [小狼毫 Weasel](https://rime.im/)；
2. 取得本倉庫（下載 zip 解壓，或 `git clone`），在其目錄執行：

```text
python tools/install_user.py        # 自動從上游下載單字碼表並合併、部署
```

3. 「【小狼毫】輸入法設定」勾選「**慈心速成**」，點「重新部署」。

### 方式 B：addon 增件手動安裝（已裝上游方案者）

1. 從本頁 [Releases](../../releases) 下載 `cixin-quick-vX.Y.Z-addon.zip`；
2. 確保上游 [rime-ms-quick](https://github.com/philipposkhos/rime-ms-quick)
   已安裝且部署成功（`ms_quick.schema.yaml` + `ms_quick.dict.yaml` 在 Rime
   用戶目錄，可由開始選單「【小狼毫】用戶資料夾」打開）；
3. 把包內 `lua\` 資料夾整個複製到 Rime 用戶目錄；
4. 編輯 `ms_quick.schema.yaml`，三處 patch（排障見包內 `INSTALL.md`）：

   ```yaml
   # ① engine/processors: 列表最前面加一行
   - lua_processor@*cixin_quick_predict

   # ② engine/translators: 列表最前面加兩行
   - lua_translator@*cixin_quick_predict_tr
   - reverse_lookup_translator@stroke_lookup   # v1.2.0 筆畫反查

   # ③ 檔案末尾追加（v1.2.0 筆畫反查配置）
   stroke_lookup:
     tag: stroke_lookup
     dictionary: stroke
     prefix: "'"
     tips: 〔筆畫反查速成：h一 s丨 p丿 n丶 z乙〕
     enable_completion: true
     preedit_format:
       - "xlit|hspnz|一丨丿丶乙|"
     comment_format:
       - "xlit|abcdefghijklmnopqrstuvwxyz|日月金木水火土竹戈十大中一弓人心手口尸廿山女田難卜符|"

   recognizer:
     import_preset: default
     patterns:
       reverse_lookup: "`[a-z]*$"
       stroke_lookup: "'[hspnz]*$"
   ```

   > 若上游 schema 已有 `recognizer:` 段，只把 `stroke_lookup` 一行併進其
   > `patterns:` 即可，不要重複整段。
5. 「重新部署」，依上方「功能」一節逐項試用。
   
## 版本

| 版本 | 日期 | 內容 |
|------|------|------|
| v1.0.0 | 2026-09-27 | XP 式盲接聯想（Shift+1..9 接龍） |
| v1.1.0 | 2026-09-27 | 候選欄可見聯想（上屏後橫向列出、可點選） |
| v1.2.0 | 2026-09-28 | 拼音 `` ` `` ＋筆畫 `'` 雙通道反查，附速成碼注釋 |

變更細節見 [CHANGELOG.md](CHANGELOG.md)。

## 授權

- 本專案原創代碼：[MIT](LICENSE)
- 詞組詞表：衍生自 [rime/rime-essay](https://github.com/rime/rime-essay)（LGPL-3.0）
- 單字碼表：源自 [rime-ms-quick](https://github.com/philipposkhos/rime-ms-quick)，
  上游未聲明授權，本倉庫不再分發、安裝時自行取得——詳見 [NOTICE.md](NOTICE.md)

## 開發文檔

想了解這個方案是怎麼做出來的、以及 librime-lua 組件開發的完整排雷手冊：

- [docs/03-開發歷程.md](docs/03-開發歷程.md) — 從「什!」到完整聯想的 14 輪調試實錄
- [docs/04-踩坑與解法.md](docs/04-踩坑與解法.md) — 按主題分類的坑與解法（模塊加載、鍵碼、librime API、反查、部署）

## 致謝

- [philipposkhos/rime-ms-quick](https://github.com/philipposkhos/rime-ms-quick) — 微軟傳統速成排位碼表
- [RIME｜中州韻輸入法引擎](https://rime.im/) 與 [librime-lua](https://github.com/hchunhui/librime-lua)
- [rime/rime-essay【八股文】](https://github.com/rime/rime-essay) — 詞頻數據
