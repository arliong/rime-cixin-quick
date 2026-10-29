# 更新日誌（Changelog）

所有對外發佈的版本均記錄於此。格式參考 [Keep a Changelog](https://keepachangelog.com/)。

## [v1.3.0] — 2026-10-29

### 新增
- **獲上游 MIT 授權**：上游 [philipposkhos/rime-ms-quick](https://github.com/philipposkhos/rime-ms-quick)
  已於 2026-10-28 為該倉庫加入 MIT License，並於
  [issue #5](https://github.com/philipposkhos/rime-ms-quick/issues/5)
  明示授權本專案使用、修改及再分發其單字碼表。
- **整包直發**：`cixin-quick-v1.3.0-full.zip` 內含合併後的完整碼表
  （單字 21,702 + 詞組 63,297 = 84,999 條），下載解壓即用，無需 Python、無需聯網。
- **東風破 plum 一鍵安裝**：倉庫提供 `recipe.yaml`，
  `bash rime-install arliong/rime-cixin-quick` 即可完成安裝。
- **MIT 合規**：整包與倉庫均附上游授權全文（`licenses/rime-ms-quick-LICENSE`）
  與版權聲明（`NOTICE.md`），滿足 MIT 條款「分發時須保留版權及授權聲明」之要求。

### 變更
- **倉庫改為 RIME 標準根級佈局**：`cixin_quick.schema.yaml`、`cixin_quick.dict.yaml`
  移至倉庫根目錄（plum 的 `install_files` 會保留相對路徑，置於子目錄將無法被 RIME 載入）。
- **方案註冊改為「追加」寫法**：`default.custom.yaml` 與 plum 配方一律採用
  `"schema_list/+"`，不再整段覆蓋使用者的 `schema_list`。
  plum 配方另以 `"patch/+"` 合併進既有的 `patch` 節點，
  使用者既有的方案清單與其它自訂項（menu、switches 等）皆保留。
- **新增 `tools/build_dict.py`**：可由上游碼表 + 詞組詞表重建合併碼表，
  重建過程套用 MIT 標頭，便於複核出處。
- `tools/install_user.py` 改為直接部署倉庫內建的完整碼表（不再聯網下載上游），
  並改以「追加」寫法註冊方案（改動前自動備份 `.bak`）。

### 修復
- **反查詞典缺失**：`luna_pinyin.prism.bin` / `stroke.prism.bin` 過去只有在
  使用者方案清單恰好含 `luna_pinyin` / `stroke` 時才會被編譯，
  否則拼音反查與筆畫反查靜默失效。
  v1.3.0 改由 `cixin_quick.schema.yaml` 宣告 `schema/dependencies: [luna_pinyin, stroke]`，
  部署時自動編譯依賴方案——既修好反查功能，也不必再往使用者方案清單塞額外條目。
- **部署時碼表殘留**：`ms_quick` 舊命名殘留於 schema／lua 的問題已於整包建置時
  加入自動斷言檢查。

## [v1.2.0] — 2026-09-28

### 新增
- **拼音反查**：`` ` ``（數字 1 左鍵）進入拼音反查模式，打全拼或部分拼音
  （`enable_completion`）即可出字；候選自動附註速成碼。
- **筆畫反查**：`'` 進入筆畫反查模式，五鍵 h橫／s豎／p撇／n捺／z折，
  支持打部分筆畫即出候選；同樣附註速成碼。
- 反查候選注釋（comment）自動反查主碼表，顯示每個候選字的速成碼，邊打邊學。

### 修復
- 拼音反查在部分機器上無反應：根因是 `luna_pinyin.prism.bin` 未被編譯
  （上游方案列表不含 luna_pinyin），已在文件中說明處理方式。

## [v1.1.0] — 2026-09-27

### 新增
- **候選欄可見聯想**：上屏一字後，候選欄即時橫向列出聯想詞，
  支持數字鍵選擇與鼠標點選；`Esc` 取消，繼續打字自動隱藏。
- 實現機制：librime 的 `Commit()` 是「先 commit_notifier、後 Clear()」，
  故在 `commit_notifier` 只置標記，於 `update_notifier`（Clear 之後觸發）
  再 `push_input("~")` 合成標記分段，交由 `lua_translator` 生成聯想候選。
- 推標記前先檢查該字有無聯想詞，避免空候選欄殘留。

## [v1.0.0] — 2026-09-27

### 新增
- **XP 式盲接聯想**：上屏一字後按 `Shift+1..9` 依詞頻接龍出下一字，
  可連續按、連續接，全程免看候選欄。
- 預建索引（首字 → 詞組列表，詞頻序），運行時零遍歷、微秒級響應。
- 按鍵語義完整處理：Shift+數字（含移位符號形鍵碼與直數字形鍵碼雙形態）、
  keyup 釋放事件過濾、150ms 同鍵去重、`Esc` 取消、
  字母／數字／空格／標點自動清除聯想狀態並放行。
- 詞組詞庫約 63,000 條，由 rime-essay（LGPL-3.0）高頻詞 + 速成碼自動生成，
  生成腳本隨倉庫提供。
