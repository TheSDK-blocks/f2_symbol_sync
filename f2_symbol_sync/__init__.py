# f2_symbol_sync class 
# Last modification by initentity generator 
#Simple buffer template

import os
import sys
import numpy as np
import tempfile

from thesdk import *
from verilog import *
from vhdl import *

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
        self._io_synMetric = IO();    # Pointer for output data
        self.Hstf=np.conj(sg80211n._PLPCseq_short[0:64])
        self.Hltf=np.conj(sg80211n._PLPCseq_long[0:16])
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
        _=verilog_iofile(self,name='A', dir='in')
        _=verilog_iofile(self,name='Z')
        self.vlogparameters =dict([('g_Rs',self.Rs)])

        if self.model=='vhdl':
            self.print_log(type='F', msg='VHDL model not yet supported')

    def main(self):
        #matched filtering for short and long sequences and squaring for energy
        #scale according to l2 norm
        framelen=sg80211n.ofdm64dict_noguardband['framelen']
        CPlen=sg80211n.ofdm64dict_noguardband['CPlen']


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
        self._io_synMetric.Data=out

    def run(self,*arg):
        if len(arg)>0:
            self.par=True      #flag for parallel processing
            self.queue=arg[0]  #multiprocessing.queue as the first argument
        if self.model=='py':
            self.main()
        else: 
          self.write_infile()

          if self.model=='sv':
              self.run_verilog()

          elif self.model=='vhdl':
            self.print_log(type='F', msg='VHDL model not yet supported')

          self.read_outfile()

    def write_infile(self):
        self.iofile_bundle.Members['io_iqSamples'].data=self.io_iqSamples.Data.reshape(-1,1)
        # This could be a method somewhere
        for name, val in self.iofile_bundle.Members.items():
            if val.dir=='in':
                self.iofile_bundle.Members[name].write()

    def read_outfile(self):
        #Handle the ofiles here as you see the best
        a=self.iofile_bundle.Members['io_synMetric']
        a.read(dtype='object')
        self._io_synMetric.Data=a.data
        if self.par:
            self.queue.put(self._io_synMetric)

        del self.iofile_bundle #Large files should be deleted


if __name__=="__main__":
    import matplotlib.pyplot as plt
    from  f2_symbol_sync import *
    t=thesdk()
    t.print_log(type='I', msg="This is a testing template. Enjoy")
