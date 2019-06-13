add wave -position insertpoint  \
sim:/tb_f2_symbol_sync/clock \
sim:/tb_f2_symbol_sync/reset \
sim:/tb_f2_symbol_sync/io_iqSamples_real \
sim:/tb_f2_symbol_sync/io_iqSamples_imag \
sim:/tb_f2_symbol_sync/initdone \
sim:/tb_f2_symbol_sync/io_syncMetric \

run -all

