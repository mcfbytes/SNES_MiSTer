-- After FRAMES frames (default 120): print the result block ($0400-$042F) and the screen buffer as hex, then stop.
local n, done = 0, false
local frames = 120
emu.addEventCallback(function()
  n = n + 1
  if done or n < frames then return end
  done = true
  local t = {}
  for a = 0x0400, 0x042F do t[#t + 1] = string.format("%02X", emu.read(a, emu.memType.snesWorkRam)) end
  print("WRAM " .. table.concat(t))
  local buf = emu.getScreenBuffer()
  local s = {}
  for i = 1, #buf do s[i] = string.format("%06X", buf[i] & 0xFFFFFF) end
  print("SCREEN " .. #buf .. " " .. table.concat(s))
  emu.stop(0)
end, emu.eventType.endFrame)
