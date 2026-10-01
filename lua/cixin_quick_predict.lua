-- 傳統速成 上屏後「詞組聯想」（XP 式：Shift+數字 接龍 + 候選欄可見聯想）
-- 機制：上屏一字後，commit_notifier 錨定該字 → 查預建索引 → Shift+1..9 續接上屏。
--       本版**候選欄不顯示**聯想詞（盲接），v1.1.0 起才補上可見聯想。
-- 防護：
--   * keyup（按鍵釋放）事件必須放行——否則同一鍵接龍兩次（實測「什麼麼」）；
--     另加 150ms 同鍵去重兜底。
--   * 聯想詞表由預建 lua/cixin_quick_index.lua 提供（require 直接載入）。
--   * 錨定：commit_notifier 回調裡優先 get_commit_text()（本次提交文本，
--     latest_text 此時尚未更新），實現 XP 式連續接龍（什→麼→麼樣…）。
--   * 所有外部呼叫皆 pcall 守衛，異常只放行，絕不崩潰。
-- 模組回傳 table（含 M.func）；librime-lua loader 對 table 讀 .func 欄位。
--   func(key, env) 回傳值：0=kReject, 1=kAccept, 2(其他)=kNoop。
local M = {}

-- 預建索引；require 失敗則降為空表（功能降級但不崩潰）
local ok_idx, idx = pcall(require, "cixin_quick_index")
if not (ok_idx and type(idx) == "table") then idx = {} end

-- 載入麵包屑：寫進 rime.weasel 的 INFO 日誌，用於確認模組已載入
pcall(function()
  local n = 0
  for _ in pairs(idx) do n = n + 1 end
  log.info("cixin_quick_predict: loaded ok_idx=" .. tostring(ok_idx) .. " heads=" .. tostring(n))
end)

-- 最近一次上屏文字（由 commit_notifier 寫入）
local last_committed = nil
-- 上次接龍去重記錄 { clock, n, committed }：150ms 內同鍵同字不重複上屏
local last_hit = nil

-- UTF-8 拆字（兼容各 Lua 版本，不依賴 utf8 庫）
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

-- 去掉已上屏前綴，只回傳續接部分（避免重複字）
local function tail_of(word, committed)
  if not committed or #committed == 0 then return word end
  local wc, cc = uchars(word), uchars(committed)
  if #wc < #cc then return "" end
  for i = 1, #cc do if wc[i] ~= cc[i] then return word end end
  return table.concat(wc, "", #cc + 1)
end

-- 註冊 commit_notifier：上屏後錨定本次提交文字（v1.0 不做候選欄標記分段）
function M.init(env)
  local ok, ctx = pcall(function() return env.engine.context end)
  if not ok or not ctx then return end
  local ok2, notifier = pcall(function() return ctx.commit_notifier end)
  if ok2 and notifier then
    pcall(function()
      notifier:connect(function(c)
        pcall(function()
          -- 錨定本次提交文本：get_commit_text() 在回調時實時正確；
          -- commit_history:latest_text() 此時尚未更新（讀到舊值），只作兜底
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
          if t then last_committed = t end
          pcall(function() log.info("cixin_quick_predict: commit anchored [" .. tostring(t) .. "] pending mark") end)
        end)
      end)
    end)
  end
  pcall(function() log.info("cixin_quick_predict: commit notifier wired") end)
end

-- 從 context 取最近上屏文字（兜底路徑）
local function last_from_ctx(ctx)
  local ok, h = pcall(function() return ctx.commit_history end)
  if not ok or not h then return nil end
  local ok2, t = pcall(function() return h:latest_text() end)
  if ok2 and t and #t > 0 then return t end
  return nil
end

-- Shift+數字 的鍵碼對照：兩種形態都接受（直數字 / 移位符號）
local DIGIT_MAP = {
  [0x31]=1, [0x32]=2, [0x33]=3, [0x34]=4, [0x35]=5, [0x36]=6, [0x37]=7, [0x38]=8, [0x39]=9,  -- 1..9
  [0x21]=1, [0x40]=2, [0x23]=3, [0x24]=4, [0x25]=5, [0x5E]=6, [0x26]=7, [0x2A]=8, [0x28]=9,  -- ! @ # $ % ^ & * (
}

function M.func(key, env)
  -- ① 放行 keyup（按鍵釋放）事件：否則同一鍵會接龍兩次（「什麼麼」實錘）
  local ok_rel, is_rel = pcall(function() return key:release() end)
  if ok_rel and is_rel then return 2 end

  local ctx = env.engine.context

  -- ② Shift+數字 判定（兩形態）
  local n = nil
  local ok_sh, shifted = pcall(function() return key:shift() end)
  if ok_sh and shifted then n = DIGIT_MAP[key.keycode] end

  if not n then return 2 end
  -- 組字中（真打字）不攔截，避免干擾正常組字
  if ctx:is_composing() then return 2 end

  -- 取最近上屏字：notifier 錨定優先，commit_history 兜底
  local committed = last_committed
  if not committed or #committed == 0 then
    committed = last_from_ctx(ctx)
  end
  if not committed or #committed == 0 then
    pcall(function() log.info("cixin_quick_predict: shift+" .. n .. " passed (no commit history)") end)
    return 2
  end

  -- ④ 同鍵去重兜底：150ms 內同 n 同上屏字 → 吃掉按鍵但不重複上屏
  local ok_clk, now = pcall(os.clock)
  if ok_clk and last_hit and last_hit.n == n and last_hit.committed == committed
     and (now - last_hit.clock) < 0.15 then
    return 1
  end

  -- 查「以最後上屏字開頭」的聯想詞清單（按詞頻排列，最常見在前）
  local chars = uchars(committed)
  local last = chars[#chars]
  local list = idx[last]
  if not list or #list < n then
    pcall(function() log.info("cixin_quick_predict: shift+" .. n .. " passed (no predict for [" .. last .. "])") end)
    return 2
  end

  local word = list[n]
  if not word then return 2 end

  local tail = tail_of(word, committed)
  if tail and #tail > 0 then
    pcall(function() env.engine:commit_text(tail) end)  -- 接龍上屏（如「麼」）
    if ok_clk then last_hit = { clock = now, n = n, committed = committed } end
    pcall(function() log.info("cixin_quick_predict: shift+" .. n .. " after [" .. committed .. "] -> " .. tail) end)
    return 1                                            -- 消費此按鍵
  end
  return 2
end

return M
