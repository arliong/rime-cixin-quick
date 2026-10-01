# NOTICE — 第三方內容歸屬與授權說明

本專案（慈心速成 / cixin_quick）包含以下第三方來源內容，在此逐項說明：

## 1. 單字速成碼表（上游，未聲明授權）

- 來源：<https://github.com/philipposkhos/rime-ms-quick>（`ms_quick.dict.yaml`）
- 內容：按 Windows 10 版微軟速成錄入的單字排位碼表（約 21,000 餘條），含香港增補字符集。
- 授權狀態：**該上游倉庫未包含任何 LICENSE 檔案**。依著作權法預設原則，
  未聲明授權 = 保留所有權利（All Rights Reserved）。
- 本專案的處理方式：
  - 本倉庫**不直接再分發**該單字碼表檔案；
  - 使用者安裝時由安裝腳本／手動步驟**自行從上游倉庫下載**；
  - 本專案已向上游作者提交功能提案與授權請求（回應後將在此處附 issue 連結）；
  - 若取得作者明示授權，將在此處更新狀態。
- 上游項目定位為「沒有聯想字」的傳統速成方案；本專案的聯想功能是在
  獨立倉庫中實現的新功能，與上游的設計方向不同（上游 issue #4 無回應逾一年）。

## 2. 詞組聯想詞表（本專案生成，衍生自 LGPL-3.0 數據）

- 內容：`cixin_quick.dict.yaml` 中的詞組部分（約 63,000 條，由 `tools/` 下
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
