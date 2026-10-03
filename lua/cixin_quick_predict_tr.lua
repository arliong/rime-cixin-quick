-- 上屏後候選欄可見聯想詞（配合 cixin_quick_predict 的「標記分段」機制）。
-- 機制：處理器在上屏後 set_input("~") 合成標記分段 → 本翻譯器對 input=="~"
--       生成聯想候選（顯示在候選欄；鼠標點選亦可上屏）。
-- 錨定：與處理器一致，commit_notifier 回調裡優先 get_commit_text()（本次提交文本）。
-- 所有外部呼叫皆 pcall 守衛；自包含模組（require 預建索引）。
local M = {}

local MARK = "~"
local MAX_CANDS = 9

-- 預建索引；require 失敗則降為空表（功能降級但不崩潰）
local ok_idx, idx = pcall(require, "cixin_quick_index")
if not (ok_idx and type(idx) == "table") then idx = {} end

-- 載入麵包屑
pcall(function()
  local n = 0
  for _ in pairs(idx) do n = n + 1 end
  log.info("cixin_quick_predict_tr: loaded ok_idx=" .. tostring(ok_idx) .. " heads=" .. tostring(n))
end)

-- 最近一次上屏文字（由 commit_notifier 錨定）
local tr_last = nil

-- UTF-8 拆字（不依賴 utf8 庫）
local function uchars(s)
  local t = {}
  local i = 1
  local n = #s
  while i <= n do
    local b = string.byte(s, i)
    local len = 1
    if b >= 240 then len = 4
    elseif b >= 224 then len = 3
    elseif b >= 192 then len = 2
    end
    t[#t + 1] = string.sub(s, i, i + len - 1)
    i = i + len
  end
  return t
end

-- 去掉已上屏前綴，只回傳續接部分
local function tail_of(word, committed)
  if not committed or #committed == 0 then return word end
  local wc, cc = uchars(word), uchars(committed)
  if #wc < #cc then return "" end
  for i = 1, #cc do if wc[i] ~= cc[i] then return word end end
  return table.concat(wc, "", #cc + 1)
end

-- 錨定本次提交文本（與處理器同一語義，保證候選欄與盲接一致）
function M.init(env)
  local ok, ctx = pcall(function() return env.engine.context end)
  if not ok or not ctx then return end
  local ok2, notifier = pcall(function() return ctx.commit_notifier end)
  if not ok2 or not notifier then return end
  pcall(function()
    notifier:connect(function(c)
      pcall(function()
        local t = nil
        local ok_g, gt = pcall(function() return c:get_commit_text() end)
        if ok_g and gt and #gt > 0 then t = gt end
        if not t then
          local h = c.commit_history
          if h then
            local ok3, lt = pcall(function() return h:latest_text() end)
            if ok3 and lt and #lt > 0 then t = lt end
          end
        end
        if t then tr_last = t end
      end)
    end)
  end)
end

-- 翻譯：input=="~"（聯想標記分段）→ 以最近上屏字開頭的詞組續接部分為候選
function M.func(input, seg, env)
  if input ~= MARK then return end
  local committed = tr_last
  if not committed or #committed == 0 then return end

  local chars = uchars(committed)
  local last = chars[#chars]
  local list = idx[last]
  if not list then return end

  local count = 0
  for _, word in ipairs(list) do
    if count >= MAX_CANDS then break end
    local tail = tail_of(word, committed)
    if tail and #tail > 0 then
      count = count + 1
      pcall(function()
        yield(Candidate("predict", seg.start, seg._end, tail, "〔" .. word .. "〕"))
      end)
    end
  end
end

return M
