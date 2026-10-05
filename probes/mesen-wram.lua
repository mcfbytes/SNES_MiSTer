-- After 900 frames: print WRAM $0400-$13FF (probe results) and the backdrop colour, then stop.
local n = 0
emu.addEventCallback(function()
  n = n + 1
  if n < 900 then return end
  local t = {}
  for a = 0x0400, 0x13FF do t[#t + 1] = string.format("%02X", emu.read(a, emu.memType.snesWorkRam)) end
  print("WRAM " .. table.concat(t))
  local buf = emu.getScreenBuffer()
  print(string.format("PIX %06X", buf[100 * 256 + 128 + 1] & 0xFFFFFF))
  emu.stop(0)
end, emu.eventType.endFrame)
