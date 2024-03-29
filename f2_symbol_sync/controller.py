# Written by Marko kosunen, Marko.kosunen@aalto.fi 20190509
# The right way to do the unit controls is to write a controller class here
import os

import numpy as np
from thesdk import *
from verilog import *
from verilog.module import *

from signal_generator_802_11n import PLPCsyn_long

class controller(verilog,thesdk):
    @property
    def _classfile(self):
        return os.path.dirname(os.path.realpath(__file__)) + "/"+__name__

    def __init__(self,*arg):
        self.proplist = [ 'Rs', 'symbol_length', 'Users' ];    #properties that can be propagated from parent
        self.Rs = 160e6;                   # Sampling frequency
        self.step=int(1/(self.Rs*1e-12))   #Time increment for control
        self.Users = 16;                   # Number of users
        self.symbol_length  = 64;          # OFDM symbol length
        self.time=0
        self.control_write = IO()
        self.control_write.Data = Bundle()
        self.control_read = IO()
        self.control_read.Data = Bundle()
        #self.reference_sequence=np.array(PLPCsyn_long).reshape(-1,1).astype(complex)
        self.model='py';             #can be set externally, but is not propagated
        self.par= False              #By default, no parallel processing
        self.queue= []               #By default, no parallel processing

        if len(arg)>=1:
            parent=arg[0]
            self.copy_propval(parent,self.proplist)
            self.parent =parent;


        # We now where the verilog file is.
        # Let's read in the file to have IOs defined
        self.dut=verilog_module(file=self.entitypath +
                '/../f2_symbol_sync/sv/f2_symbol_sync.sv')

        # Define the signal connectors associeted with this
        # controller
        # These are signals of tb driving several targets
        # Not present in DUT
        self.connectors=verilog_connector_bundle()

        if len(arg)>=1:
            parent=arg[0]
            self.copy_propval(parent,self.proplist)
            self.parent =parent;

        #These are signals not in dut
        self.newsigs_write=[
                 'initdone',
                ]

        # Selected signals controlled with this file with init values
        # These are tuples defining name init value pair
        self.signallist_write=[
            ('reset', 1),
            ('initdone',0),
            ('io_resetUsers',0),
            ('io_syncSearch',0),
            ('io_passThru',0),
            ('io_frameThreshold',128),
        ]

        #These are signals not in dut
        self.newsigs_read=[
                ]
        self.signallist_read=[
        ]
        #for user in range(self.Users):
        #   self.signallist_read+= [ ('io_estimate_out_%s_real' %(user),0)  ,
        #           ('io_estimate_out_%s_imag' %(user) ,0)]

        self.init()

    def init(self):
        self._vlogparameters =dict([('Rs',self.Rs)])
        # This gets interesting
        # IO is a file data stucture
        iofiles_write=[
                'control_write'
                ]
        for name in iofiles_write:
            self.control_write.Data.Members[name]=verilog_iofile(self,name=name,
                    dir='in',iotype='ctrl')

        self.define_control()

    #Redefines teh control sequence to zero
    def reset_control_sequence(self):
        f=self.control_write.Data.Members['control_write']
        self.time=0
        f.data= np.array([])
        f.set_control_data(init=0) # Initialize to zeros at time 0


    # First we start to control Verilog simulations with
    # This controller. I.e we pass the IOfile definition
    def step_time(self,**kwargs):
        self.time+=kwargs.get('step',self.step)

    def define_control(self):
        # This is a bit complex way of passing the data,
        # But eventually we pass only the data , not the file
        # Definition. File should be created in the testbench
        scansigs_write=[]
        for name, val in self.signallist_write:
            # We manipulate connectors as verilog_iofile operate on those
            if name in self.newsigs_write:
                self.connectors.new(name=name, cls='reg')
            else:
                self.connectors.Members[name]=self.dut.io_signals.Members[name]
                self.connectors.Members[name].init=''
            scansigs_write.append(name)

        f=self.control_write.Data.Members['control_write']
        f.verilog_connectors=self.connectors.list(names=scansigs_write)
        f.set_control_data(init=0) # Initialize to zeros at time 0

    def reset(self):
        #start defining the file
        f=self.control_write.Data.Members['control_write']
        for name in [ 'reset', ]:
            f.set_control_data(time=self.time,name=name,val=1)

        # After awhile, switch off reset
        self.step_time(step=15*self.step)

        for name in [ 'reset', ]:
            f.set_control_data(time=self.time,name=name,val=0)

    def start_datafeed(self):
        f=self.control_write.Data.Members['control_write']
        for name in [ 'initdone', ]:
            f.set_control_data(time=self.time,name=name,val=1)
        self.step_time()

    def set_resetUsers(self):
        f=self.control_write.Data.Members['control_write']
        for name in [ 'io_resetUsers', ]:
            f.set_control_data(time=self.time,name=name,val=1)
        self.step_time()

    def reset_resetUsers(self):
        f=self.control_write.Data.Members['control_write']
        for name in [ 'io_resetUsers', ]:
            f.set_control_data(time=self.time,name=name,val=0)
        self.step_time()

    def set_syncSearch(self):
        f=self.control_write.Data.Members['control_write']
        for name in [ 'io_syncSearch', ]:
            f.set_control_data(time=self.time,name=name,val=1)
        self.step_time()

    def reset_syncSearch(self):
        f=self.control_write.Data.Members['control_write']
        for name in [ 'io_syncSearch', ]:
            f.set_control_data(time=self.time,name=name,val=0)
        self.step_time()

    def set_passThru(self):
        f=self.control_write.Data.Members['control_write']
        for name in [ 'io_passThru', ]:
            f.set_control_data(time=self.time,name=name,val=1)
        self.step_time()

    def reset_passThru(self):
        f=self.control_write.Data.Members['control_write']
        for name in [ 'io_passThru', ]:
            f.set_control_data(time=self.time,name=name,val=0)
        self.step_time()

    def set_frameThreshold(self):
        f=self.control_write.Data.Members['control_write']
        for name in [ 'io_frameThreshold', ]:
            f.set_control_data(time=self.time,name=name,val=100)
        self.step_time()
