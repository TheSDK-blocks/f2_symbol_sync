add wave -position insertpoint sim:/tb_f2_symbol_sync/clock
add wave sim:/tb_f2_symbol_sync/reset
add wave -radix decimal sim:/tb_f2_symbol_sync/io_iqSamples_real
add wave -radix decimal sim:/tb_f2_symbol_sync/io_iqSamples_imag
add wave sim:/tb_f2_symbol_sync/initdone 
add wave -radix unsigned sim:/tb_f2_symbol_sync/io_shortEnergy
add wave -radix unsigned sim:/tb_f2_symbol_sync/io_longEnergy
add wave -radix unsigned sim:/tb_f2_symbol_sync/io_syncMetric 

run -all

