add wave -position insertpoint sim:/tb_f2_symbol_sync/clock
add wave sim:/tb_f2_symbol_sync/reset
add wave sim:/tb_f2_symbol_sync/initdone
add wave sim:/tb_f2_symbol_sync/io_resetUsers
add wave sim:/tb_f2_symbol_sync/io_syncSearch
add wave sim:/tb_f2_symbol_sync/io_passThru
add wave -radix unsigned sim:/tb_f2_symbol_sync/io_syncThreshold
add wave -radix decimal sim:/tb_f2_symbol_sync/io_iqSamples_real
add wave -radix decimal sim:/tb_f2_symbol_sync/io_iqSamples_imag
add wave -radix decimal sim:/tb_f2_symbol_sync/io_signalPower
add wave -radix decimal sim:/tb_f2_symbol_sync/io_crossPower_real
add wave -radix decimal sim:/tb_f2_symbol_sync/io_crossPower_imag
add wave -radix unsigned sim:/tb_f2_symbol_sync/io_crossMagnitude
add wave -radix decimal sim:/tb_f2_symbol_sync/io_syncMetric
add wave sim:/tb_f2_symbol_sync/io_frameSync
add wave sim:/tb_f2_symbol_sync/io_symbolSync
add wave -radix unsigned sim:/tb_f2_symbol_sync/io_currentUser
add wave -radix decimal sim:/tb_f2_symbol_sync/io_iqSyncedSamples_real
add wave -radix decimal sim:/tb_f2_symbol_sync/io_iqSyncedSamples_imag

run -all
