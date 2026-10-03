-- 傳統速成 上屏後「詞組聯想」（XP 式：Shift+數字 接龍 + 候選欄可見聯想）
-- 機制：
--   A. 上屏一字後，commit_notifier 只置 pending_mark（librime 1.13 的 Commit()
--      是先回調後 Clear()，回調裡設 input 會被清）；由 update_notifier 回調
--      （Clear() 之後）用 push_input("~") 合成「標記分段」，讓 lua_translator
--      把聯想詞顯示在候選欄（可見預覽；鼠標點選亦可選詞）。
--      注意：librime-lua 的 Context 沒有 set_input 方法（那是 input 屬性 setter）。
--   B. Shift+1..9 盲接仍是主機制（鍵碼兼容移位符號與直數字兩形態）。
--   C. 標記態按鍵語義：Esc=取消聯想；字母/普通數字/空格/標點=清標記放行恢復打字；
--      純 Shift 放行不動標記（避免 Shift+數字 期間候選欄閃爍）。
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

local MARK = "~"  -- 聯想標記分段（不會被 speller alphabet 吸收，punct_segmentor 接手）

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
-- 聯想標記態：notifier set_input 後為 true，清除後復位
local marking = false
-- 待推標記：commit_notifier 裡置位（librime 1.13 的 Commit() 是
-- 「先觸發 commit_notifier、後 Clear()」，回調裡設 input 會被清掉），
-- 由 update_notifier 回調（Clear() 之後觸發）消費：push_input("~") 合成標記分段。
-- update_notifier 槽序：Engine 先（對空 input 的 Compose 跑完）、本模組後，
-- 故嵌套 Compose("~") 不會被外層覆蓋。標誌冪等，重複連線（切方案）也安全。
local pending_mark = false

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

-- 判斷「以最近上屏字開頭」是否有聯想詞（無則不推標記，避免空候選欄）
local function has_predict(committed)
  if not committed or #committed == 0 then return false end
  local chars = uchars(committed)
  local list = idx[chars[#chars]]
  if not list or #list == 0 then return false end
  for _, word in ipairs(list) do
    local tail = tail_of(word, committed)
    if tail and #tail > 0 then return true end
  end
  return false
end

-- 註冊 notifiers：
--   commit_notifier → 錨定本次提交文字 + 置 pending_mark（不設 input，會被 Clear 清掉）
--   update_notifier → Clear() 之後觸發，消費 pending_mark：push_input("~") 合成標記分段
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
          pending_mark = true
          pcall(function() log.info("cixin_quick_predict: commit anchored [" .. tostring(t) .. "] pending mark") end)
        end)
      end)
    end)
  end
  local ok_u, updater = pcall(function() return ctx.update_notifier end)
  if ok_u and updater then
    pcall(function()
      updater:connect(function(c)
        pcall(function()
          if not pending_mark then return end
          pending_mark = false
          if marking then return end
          local comp = false
          pcall(function() comp = c:is_composing() end)
          if not comp and has_predict(last_committed) then
            c:push_input(MARK)  -- librime-lua 無 set_input 方法（那是 input 屬性 setter）
            marking = true
            pcall(function() log.info("cixin_quick_predict: mark pushed after commit [" .. tostring(last_committed) .. "]") end)
          end
        end)
      end)
    end)
  end
  pcall(function() log.info("cixin_quick_predict: notifiers wired commit=" .. tostring(ok2 and notifier ~= nil) .. " update=" .. tostring(ok_u and updater ~= nil)) end)
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

  -- 同步標記態：composition 已被外部清空時復位
  local composing = false
  pcall(function() composing = ctx:is_composing() end)
  if marking and not composing then marking = false end

  -- ② Shift+數字 判定（兩形態）
  local n = nil
  local ok_sh, shifted = pcall(function() return key:shift() end)
  if ok_sh and shifted then n = DIGIT_MAP[key.keycode] end

  -- ③ 聯想標記態的按鍵語義
  if marking then
    if n then
      -- Shift+數字：走接龍主邏輯（下方）
    elseif key.keycode == 0xFF1B then            -- Esc：取消聯想
      pcall(function() ctx:clear() end)
      marking = false
      pcall(function() log.info("cixin_quick_predict: mark cleared (esc)") end)
      return 1
    elseif key.keycode == 0xFFE1 or key.keycode == 0xFFE2 then
      return 2                                    -- 純 Shift：放行，不動標記（避免候選欄閃爍）
    else                                          -- 字母/普通數字/空格/標點/回車：
      pcall(function() ctx:clear() end)           -- 清標記放行，恢復正常打字
      marking = false
      pcall(function() log.info("cixin_quick_predict: mark cleared (key 0x" .. string.format("%x", key.keycode) .. ")") end)
      return 2
    end
  end

  if not n then return 2 end
  -- 真打字（非標記態的組字）時不攔截；標記態（marking）繼續走接龍
  if ctx:is_composing() and not marking then return 2 end

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
