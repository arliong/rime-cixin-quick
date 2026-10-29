# NOTICE — 第三方內容歸屬與授權說明

本專案（慈心速成 / cixin_quick）包含以下第三方來源內容，在此逐項說明。

## 1. 單字速成碼表（上游，已獲 MIT 授權）

- 來源：<https://github.com/philipposkhos/rime-ms-quick>（`ms_quick.dict.yaml`）
- 內容：按 Windows 10 版微軟速成錄入的單字排位碼表
  （上游檔案 21,705 行，其中 3 行為完全重複，去重後 21,702 條），含香港增補字符集。
- 授權狀態：**已獲上游作者明示授權**。上游於 2026-10-28 為該倉庫加入
  MIT License（commit `540288d`），並在
  [issue #5](https://github.com/philipposkhos/rime-ms-quick/issues/5) 明確回覆：

  > 倉庫已加上 MIT License。ms_quick.dict.yaml 是我自己整理的碼表，可依 MIT
  > 條款使用、修改及再分發，包括用於 rime-cixin-quick。

- 本專案的處理方式：整包內的 `cixin_quick.dict.yaml` 即為上游單字碼表與本專案
  詞組表的合併產物；上游單字部分依 MIT 條款再分發，其版權聲明與授權全文
  見下方 `licenses/rime-ms-quick-LICENSE`。

上游項目定位為「沒有聯想字」的傳統速成方案；本專案的聯想功能是在獨立倉庫中
實現的新功能，與上游的設計方向不同。

### 上游版權聲明（MIT 條款要求保留）

```text
MIT License

Copyright (c) 2026 philipposkhos (Kho)

The "Software" in this license is the original work of the copyright holder
in this repository:

- ms_quick.dict.yaml
- ms_quick.schema.yaml
- Android/3.1.3/trime.custom.yaml
- Android/3.3/ms_quick.trime.yaml
- Android/3.3/ms_quick.custom.yaml
- README.md

Files under opencc/ and Android/opencc/ are derived from OpenCC and stay
under the Apache License, Version 2.0. They are not part of the Software.
See NOTICE and licenses/Apache-2.0.txt.
```

（MIT 授權全文見 `licenses/rime-ms-quick-LICENSE`；上游授權說明見其
[NOTICE](https://github.com/philipposkhos/rime-ms-quick/blob/master/NOTICE)。）

> ⚠️ 上游 MIT 涵蓋範圍**不含** `opencc/` 與 `Android/opencc/`（維持 Apache-2.0）。
> 本專案**未**引入、改動或再分發任何 OpenCC 檔案；方案中的簡繁轉換沿用
> 小狼毫／RIME 內建的 OpenCC 設定。

## 2. 詞組聯想詞表（本專案生成，衍生自 LGPL-3.0 數據）

- 內容：`cixin_quick.dict.yaml` 中的詞組部分（63,297 條，由 `tools/` 下
  腳本自動生成：以單字速成碼對照表 + RIME 官方【八股文】詞頻表取高頻詞）。
- 數據來源：[rime/rime-essay](https://github.com/rime/rime-essay)（essay.txt），
  **GNU Lesser General Public License v3.0 (LGPL-3.0)**。
- 本衍生詞表按 LGPL-3.0 條款再分發，來源與生成方法如上，生成腳本隨倉庫提供。

## 3. RIME 框架與小狼毫

- 本方案運行於 [RIME｜中州韻輸入法引擎](https://rime.im/)（BSD-3-Clause），
  Windows 前端為 [Weasel｜小狼毫](https://github.com/rime/weasel)（GPL-3.0）。
- 設定中引用的小狼毫自帶 `stroke.dict.yaml`（筆畫反查詞典）版權歸 RIME 項目。

## 4. 商標與輸入法方案

- 「速成」「簡易」輸入法方案本身為第三方（如微軟等）之方法與排位慣例，
  碼表數據僅描述該排位事實；本專案不主張對該輸入法方法本身的所有權。
