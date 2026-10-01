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

1. 安裝 [小狼毫 Weasel](https://rime.im/)；
2. 從本頁 [Releases](../../releases) 下載 `cixin-quick-vX.Y.Z-full.zip`；
3. 解壓，把所有檔案複製到 `%APPDATA%\Rime\`（用戶資料夾，可由
   開始選單「【小狼毫】用戶資料夾」打開）；
4. 「【小狼毫】輸入法設定」勾選「**慈心速成**」，點「重新部署」；
5. 若單字候選異常，確認資料夾內有從上游取得的 `ms_quick` 單字碼表
   （安裝腳本會自動處理，手動安裝見下方「源碼安裝」）。

### 源碼安裝（不含上游碼表）

```text
git clone https://github.com/<你的用戶名>/rime-cixin-quick
cd rime-cixin-quick
python tools/install_user.py        # 自動從上游下載單字碼表並合併、部署
```

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
