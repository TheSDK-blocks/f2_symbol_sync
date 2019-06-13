# f2_symbol_sync class 
# Last modification by initentity generator 
#Simple buffer template

import os
import sys
import numpy as np
import scipy.signal as sig

from thesdk import *
from verilog import *
from verilog.testbench import *
from verilog.testbench import testbench as vtb

import signal_generator_802_11n as sg80211n

class f2_symbol_sync(verilog,thesdk):
    #Classfile is required by verilog and vhdl classes to determine paths.
    @property
    def _classfile(self):
        return os.path.dirname(os.path.realpath(__file__)) + "/"+__name__

    def __init__(self,*arg): 
        self.proplist = [ 'Rs' ];    # Properties that can be propagated from parent
        self.Rs =  100e6;            # Sampling frequency
        self.io_iqSamples = IO();    # Pointer for input data
        self._io_syncMetric = IO();   # Pointer for output data
        self.control_write = IO();   # Pointer for control inputs

        #self.Hstf=np.conj(sg80211n.PLPCsyn_short[0:64])
        #self.Hltf=np.conj(sg80211n.PLPCsyn_long[0:16])
        self.Hstf=1
        self.Hltf=1
        self.model='py';             # Can be set externally, but is not propagated
        self.par= False              # By default, no parallel processing
        self.queue= []               # By default, no parallel processing
        if len(arg)>=1:
            parent=arg[0]
            self.copy_propval(parent,self.proplist)
            self.parent =parent;
        self.init()

    def init(self):
        #This gets updated every time you add an iofile
        self.iofile_bundle=Bundle()
        _=verilog_iofile(self,name='io_iqSamples', dir='in')
        _=verilog_iofile(self,name='io_syncMetric')
        self.vlogparameters =dict([('g_Rs',self.Rs)])

        if self.model=='vhdl':
            self.print_log(type='F', msg='VHDL model not yet supported')

    def main(self):
        #matched filtering for short and long sequences and squaring for energy
        #scale according to l2 norm

        #the maximum of this is sum of squares squared
        matchedshort=np.abs(sig.convolve(self.io_iqSamples.Data, self.Hstf, mode='full'))**2
        matchedlong=(np.sum(np.abs(self.Hstf)**2)/np.sum(np.abs(self.Hltf)**2)\
                *np.abs(sig.convolve(self.io_iqSamples.Data, self.Hltf, mode='full')))**2

        #filter for energy filtering (average of 6 samples)
        efil=np.ones((6,1))
        sshort=sig.convolve(matchedshort,efil,mode='full')
        slong=sig.convolve(matchedlong,efil,mode='full')

        #sum of the 4 past spikes with separation of 16 samples
        sfil=np.zeros((65,1))
        sfil[16:65:16]=1
        sspikes_short=sig.convolve(sshort,sfil,mode='full')/np.sum(np.abs(sfil))
        
        #compensate the matched long for the filter delays of the short
        delay=len(sspikes_short)-len(slong)
        slong=np.r_['0',slong, np.zeros((delay,1))]
        out=slong+sspikes_short
        self._spikes_long=slong
        self._spikes_short=sspikes_short
        #out=slong
        #out=sspikes_short

        # Some probably obsolete code, but save it here for a while
        #self.sspikes_short=sspikes_short
        ##find the frame start
        #usercount=0
        ##found=False
        #i=0
        #smaxprev=0
        #indmaxprev=0
        #ch_index=np.zeros((self.Users,1))
        ##ch_index_est=np.zeros((self.Users,1))
        #while usercount< self.Users and i+16<= len(sspikes_sum):
        #    self.print_log({'type':'D', 'msg': "Syncing user %i" %(usercount)})
        #    testwin=(sspikes_sum[i:i+16])
        #    self.print_log({'type':'D', 'msg': "Testwin is %s" %(testwin)})
        #    smax=np.max(testwin)
        #    indmax=i+np.argmax(testwin,axis=0)
        #    
        #    if smax != sspikes_sum[indmax]:
        #        self.print_log({'type':'F', 'msg': "Something wrong with the symbol boundary"})

        #    if smax < 0.85 * smaxprev:
        #        #found = True
        #        smax=smaxprev
        #        indmax=indmaxprev
        #        self.print_log({'type':'I', 'msg': "Found the symbol boundary at sample %i" %(indmax)})
        #        
        #        #this is an estimate of the start of the channel estimation for 
        #        # a user.
        #        ch_index[usercount]=int(indmaxprev)+int(efil.shape[0]/2)
        #        #this is to prevent accidental sync to long sequence of the current/short sequence of the next user. 
        #        smaxprev=0 #reset the spike maximum Value
        #        usercount+=1
        #        #This is suffient jump to avoid incorrect sync
        #        i+=256
        #    else:
        #        smaxprev=smax
        #        indmaxprev=indmax
        #        i+=16
        #
        ##all user sync found. calculate average
        #c=int(np.mean(ch_index-np.arange(self.Users)*(4*(framelen+CPlen))))
        #ch_index=np.arange(self.Users)*4*(framelen+CPlen)+c
        #ch_index.shape=(-1,1)
        #
        ##common sync index calculated from the last channel estimation index
        #sync_index=int(ch_index[-1,0]+2*len(sg80211n.PLPCsyn_long))

        #if self.par:
        #    self.print_log({'type':'D', 'msg': "putting sync_index for RX path %i: %s" %(self.Antennaindex,sync_index)})
        #    self.queue.put(int(sync_index))
        #    self.queue.put(sspikes_short)
        #    self.queue.put(sspikes_sum)

        ##keep the sync indexes as pointers, even though they are not needed outside the dsp
        #self._ch_index=ch_index
        #self._Frame_sync_short.Value=sspikes_short
        #self._Frame_sync_long.Value=sspikes_sum
        #self.print_log({'type':'D','msg': "sync_index is %s" %(sync_index)})
        #self._sync_index.Value=sync_index
        #self.print_log({'type':'I', 'msg': "start of the RX path %i data is at %i" %(self.Antennaindex,self._sync_index.Value)})


        if self.par:
            self.queue.put(out)
        self._io_syncMetric.Data=out

    def run(self,*arg):
        if len(arg)>0:
            self.par=True      #flag for parallel processing
            self.queue=arg[0]  #multiprocessing.queue as the first argument
        if self.model=='py':
            self.main()
        else: 
          self.write_infile()

          if self.model=='sv':
              #These methods are defined in controller.py
              self.control_write.Data.Members['control_write'].adopt(parent=self)

              # Create testbench and execute the simulation
              self.define_testbench()
              self.tb.export(force=True)
              self.write_infile()
              self.run_verilog()
              self.read_outfile()
              del self.iofile_bundle

          elif self.model=='vhdl':
              self.print_log(type='F', msg='VHDL model not yet supported')

    def write_infile(self):
        self.iofile_bundle.Members['io_iqSamples'].data=self.io_iqSamples.Data.reshape(-1,1)
        # This could be a method somewhere
        for name, val in self.iofile_bundle.Members.items():
            if val.dir=='in':
                self.iofile_bundle.Members[name].write()

    def read_outfile(self):
        #Handle the ofiles here as you see the best
        a=self.iofile_bundle.Members['io_syncMetric']
        a.read(dtype='object')
        self._io_syncMetric.Data=a.data
        if self.par:
            self.queue.put(self._io_syncMetric)

        del self.iofile_bundle #Large files should be deleted

    # Testbench definition method
    def define_testbench(self):
        #Initialize testbench
        self.tb=vtb(self)

        # Dut is creted automaticaly, if verilog file for it exists
        self.tb.connectors.update(bundle=self.tb.dut_instance.io_signals.Members)

        #Assign verilog simulation parameters to testbench
        self.tb.parameters=self.vlogparameters

        # Copy iofile simulation parameters to testbench
        for name, val in self.iofile_bundle.Members.items():
            self.tb.parameters.Members.update(val.vlogparam)

        # Define the iofiles of the testbench. '
        # Needed for creating file io routines 
        self.tb.iofiles=self.iofile_bundle

        #Define testbench verilog file
        self.tb.file=self.vlogtbsrc

        # Create TB connectors from the control file
        for connector in self.control_write.Data.Members['control_write'].verilog_connectors:
            self.tb.connectors.Members[connector.name]=connector
            # Connect them to DUT
            try: 
                self.dut.ios.Members[connector.name].connect=connector
            except:
                pass

        ## Start initializations
        #Init the signals connected to the dut input to zero
        for name, val in self.tb.dut_instance.ios.Members.items():
            if val.cls=='input':
                val.connect.init='\'b0'

        # IO file connector definitions
        # Define what signals and in which order and format are read form the files
        # i.e. verilog_connectors of the file
        name='io_syncMetric'
        ionames=[ 'io_syncMetric']
        self.iofile_bundle.Members[name].verilog_connectors=\
                self.tb.connectors.list(names=ionames)
        #for ioname in ionames:
        #    self.tb.connectors.Members[ioname].type='signed'
        self.iofile_bundle.Members[name].verilog_io_condition_append(cond='&& initdone')

        name='io_iqSamples'
        ionames=[]
        ionames+=[ name+'_real', name+'_imag']
        self.iofile_bundle.Members[name].verilog_connectors=\
                self.tb.connectors.list(names=ionames)
        self.iofile_bundle.Members[name].verilog_io_condition='initdone'

        self.tb.generate_contents()


if __name__=="__main__":
    import matplotlib.pyplot as plt
    from  f2_symbol_sync import *
    from  f2_symbol_sync.controller  import controller \
            as f2_symbol_sync_controller
    from signal_generator_802_11n import *
    import pdb
    symbol_length=64
    Rs=20e6
    signal_generator=signal_generator_802_11n()
    signal_generator.Rs=Rs
    signal_generator.Users=1
    signal_generator.Txantennas=1
    bbsigdict_ofdm_sinusoid3={ 
            'mode':'ofdm_sinusoid', 
            'freqs':[1.0e6 , 3e6, 7e6 ], 
            'length':2**14, 
            'BBRs':20e6 
        };

    bbsigdict_802_11n_random_QAM16_OFDM={ 
            'mode':'ofdm_random_802_11n', 
            'QAM':16, 
            'length':2**10,
            'BBRs': 20e6 };
    signal_generator.bbsigdict=bbsigdict_802_11n_random_QAM16_OFDM

    signal_generator.gen_random_802_11n_ofdm()
    scale=np.amax(np.r_[signal_generator._Z.Data[0,:,0].real, \
            signal_generator._Z.Data[0,:,0].imag])
    data=np.round((signal_generator._Z.Data[0,:,0]/scale)\
            .reshape(-1,1)*(2**10-1))
    controller=f2_symbol_sync_controller()
    controller.reset()
    controller.step_time(step=10*controller.step)
    controller.start_datafeed()
    duts=[ f2_symbol_sync() for i in range(2)]
    duts[1].model='sv'
    toplot=[]
    for d in duts:    
        d.Rs=Rs
        d.init()
        d.Hstf=np.conj(signal_generator._PLPCseq_short[0:64])
        d.Hltf=np.conj(signal_generator._PLPCseq_long[0:16])
        #d.interactive_verilog=True
        d.interactive_verilog=False
        d.io_iqSamples.Data=data
        d.control_write=controller.control_write
        d.run()

    print(duts[0].Hltf)

    #Plots start here
    f0=plt.figure(0)
    #x_ref=np.arange(duts[0]._io_syncMetric.Data.shape[0]).reshape(-1,1) 
    #x_ref=np.arange(2000).reshape(-1,1) 
    
    #plt.plot(x_ref,duts[0]._io_syncMetric.Data[0:200,0])
    plt.plot(duts[0]._io_syncMetric.Data[0:700,0])
    #plt.plot(duts[0].io_iqSamples.Data.real[0:2000,0])
    #plt.plot(data.real)
    #plt.xlim(0,63)
    plt.suptitle("Python model")
    plt.xlabel("n")
    plt.ylabel("Value")
    plt.grid()
    plt.show(block=False)
    f0.savefig('python_syncMetric.eps', format='eps', dpi=300);

    f1=plt.figure(1)
    plt.plot(duts[1]._io_syncMetric.Data[0:700,0])
    #plt.plot(x_ref,data.real[offset:offset+64])
    #plt.xlim(0,63)
    plt.suptitle("Verilog model")
    plt.xlabel("Bin")
    plt.ylabel("Symbol")
    plt.grid()
    plt.show(block=False)
    f1.savefig('verilog_syncMetric.eps', format='eps', dpi=300);

    input()

