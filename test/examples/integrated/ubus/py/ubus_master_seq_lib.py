#//----------------------------------------------------------------------
#//   Copyright 2007-2010 Mentor Graphics Corporation
#//   Copyright 2007-2010 Cadence Design Systems, Inc.
#//   Copyright 2010 Synopsys, Inc.
#//   Copyright 2019 Tuomas Poikela
#//   All Rights Reserved Worldwide
#//
#//   Licensed under the Apache License, Version 2.0 (the
#//   "License"); you may not use this file except in
#//   compliance with the License.  You may obtain a copy of
#//   the License at
#//
#//       http://www.apache.org/licenses/LICENSE-2.0
#//
#//   Unless required by applicable law or agreed to in
#//   writing, software distributed under the License is
#//   distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
#//   CONDITIONS OF ANY KIND, either express or implied.  See
#//   the License for the specific language governing
#//   permissions and limitations under the License.
#//----------------------------------------------------------------------

from uvm.seq import UVMSequence
from uvm.macros.uvm_object_defines import uvm_object_utils
from uvm.macros.uvm_message_defines import uvm_info
from uvm.macros.uvm_sequence_defines import uvm_do_with
from uvm.base import sv, UVM_HIGH
from ubus_transfer import ubus_transfer, READ, WRITE

#//------------------------------------------------------------------------------
#//
#// SEQUENCE: ubus_base_sequence
#//
#//------------------------------------------------------------------------------

#// This sequence raises/drops objections in the pre/post_body so that root
#// sequences raise objections but subsequences do not.

class ubus_base_sequence(UVMSequence):

    def __init__(self, name="ubus_base_seq"):
        UVMSequence.__init__(self, name)
        self.set_automatic_phase_objection(1)
        self.req = ubus_transfer()
        self.rsp = ubus_transfer()

#//------------------------------------------------------------------------------
#//
#// SEQUENCE: read_byte
#//
#//------------------------------------------------------------------------------


class read_byte_seq(ubus_base_sequence):

    def __init__(self, name="read_byte_seq"):
        ubus_base_sequence.__init__(self, name)
        self.start_addr = 0
        self.rand('start_addr', range((1 << 12) - 1))
        self.transmit_delay = 0

    #  constraint transmit_del_ct { (transmit_del <= 10); }


    async def body(self):
        self.req.data = [1234]
        self.req.addr = self.start_addr
        self.req.read_write = READ
        self.req.size = 1
        self.req.error_pos = 1000
        self.req.transmit_delay = self.transmit_delay
        await uvm_do_with(self, self.req, lambda addr: addr == self.start_addr)
        #      { req.addr == start_addr
        #        req.read_write == READ
        #        req.size == 1
        #        req.error_pos == 1000
        #        req.transmit_delay == transmit_del; } )
        rsp = []
        await self.get_response(rsp)
        self.rsp = rsp[0]
        uvm_info(self.get_name(),
            sv.sformatf("%s read : addr = `x{}, data[0] = `x{}",
                self.get_sequence_path(), self.rsp.addr, self.rsp.data[0]),
            UVM_HIGH)


uvm_object_utils(read_byte_seq)


#//------------------------------------------------------------------------------
#//
#// SEQUENCE: read_half_word_seq
#//
#//------------------------------------------------------------------------------
#
#class read_half_word_seq extends ubus_base_sequence
#
#  function new(string name="read_half_word_seq")
#    super.new(name)
#  endfunction
#
#  `uvm_object_utils(read_half_word_seq)
#
#  rand bit [15:0] start_addr
#  rand int unsigned transmit_del = 0
#  constraint transmit_del_ct { (transmit_del <= 10); }
#
#  virtual task body()
#    `uvm_do_with(req,
#      { req.addr == start_addr
#        req.read_write == READ
#        req.size == 2
#        req.error_pos == 1000
#        req.transmit_delay == transmit_del; } )
#    get_response(rsp)
#    `uvm_info(get_type_name(),
#      $sformatf("%s read : addr = `x%0h, data[0] = `x%0h, data[1] = `x%0h",
#      get_sequence_path(), rsp.addr, rsp.data[0], rsp.data[1]), UVM_HIGH)
#  endtask
#
#endclass : read_half_word_seq
#
#
#//------------------------------------------------------------------------------
#//
#// SEQUENCE: read_word_seq
#//
#//------------------------------------------------------------------------------
#
#class read_word_seq extends ubus_base_sequence
#
#  function new(string name="read_word_seq")
#    super.new(name)
#  endfunction
#
#  `uvm_object_utils(read_word_seq)
#
#  rand bit [15:0] start_addr
#  rand int unsigned transmit_del = 0
#  constraint transmit_del_ct { (transmit_del <= 10); }
#
#  virtual task body()
#    `uvm_do_with(req,
#      { req.addr == start_addr
#        req.read_write == READ
#        req.size == 4
#        req.error_pos == 1000
#        req.transmit_delay == transmit_del; } )
#    get_response(rsp)
#    `uvm_info(get_type_name(),
#      $sformatf("%s read : addr = `x%0h, data[0] = `x%0h, \
#      data[1] = `x%0h, data[2] = `x%0h, data[3] = `x%0h",
#      get_sequence_path(), rsp.addr, rsp.data[0], rsp.data[1],
#      rsp.data[2], rsp.data[3]), UVM_HIGH)
#  endtask
#
#endclass : read_word_seq
#
#
#//------------------------------------------------------------------------------
#//
#// SEQUENCE: read_double_word_seq
#//
#//------------------------------------------------------------------------------
#
#class read_double_word_seq extends ubus_base_sequence
#
#  function new(string name="read_double_word_seq")
#    super.new(name)
#  endfunction
#
#  `uvm_object_utils(read_double_word_seq)
#
#  rand bit [15:0] start_addr
#  rand int unsigned transmit_del = 0
#  constraint transmit_del_ct { (transmit_del <= 10); }
#
#  virtual task body()
#    `uvm_do_with(req,
#      { req.addr == start_addr
#        req.read_write == READ
#        req.size == 8
#        req.error_pos == 1000
#        req.transmit_delay == transmit_del; } )
#    get_response(rsp)
#    `uvm_info(get_type_name(),
#      $sformatf("%s read : addr = `x%0h, data[0] = `x%0h, \
#      data[1] = `x%0h, data[2] = `x%0h, data[3] = `x%0h, data[4] = `x%0h, \
#      data[5] = `x%0h, data[6] = `x%0h, data[7] = `x%0h",
#      get_sequence_path(), rsp.addr, rsp.data[0], rsp.data[1], rsp.data[2],
#      rsp.data[3], rsp.data[4], rsp.data[5], rsp.data[6], rsp.data[7]),
#      UVM_HIGH)
#  endtask
#
#endclass : read_double_word_seq
#
#
#//------------------------------------------------------------------------------
#//
#// SEQUENCE: write_byte_seq
#//
#//------------------------------------------------------------------------------

class write_byte_seq(ubus_base_sequence):

    last_data = None

    def __init__(self, name="write_byte_seq"):
        ubus_base_sequence.__init__(self, name)
        self.start_addr = 0
        self.rand('start_addr', range(1 << 16))
        self.data0 = 0
        self.transmit_delay = 0

    #  constraint transmit_del_ct { (transmit_del <= 10); }


    async def body(self):
        req = ubus_transfer()
        req.data.append(self.data0)
        req.addr = self.start_addr
        req.size = 1
        req.error_pos = 1000
        req.read_write = WRITE
        req.transmit_delay = self.transmit_delay
        await uvm_do_with(self, req, lambda addr: addr == self.start_addr,
            lambda read_write: read_write == WRITE,
            lambda data: data[0] == self.data0)
        #      { req.addr == start_addr
        #        req.read_write == WRITE
        #        req.size == 1
        #        req.data[0] == data0
        #        req.error_pos == 1000
        #        req.transmit_delay == transmit_del; } )
        uvm_info(self.get_type_name(),
            sv.sformatf("%s wrote : addr = `x%0h, data[0] = `x%0h",
            self.get_sequence_path(), req.addr, req.data[0]), UVM_HIGH)
        write_byte_seq.last_data = req.data[0]


uvm_object_utils(write_byte_seq)


#//------------------------------------------------------------------------------
#//
#// SEQUENCE: write_half_word_seq
#//
#//------------------------------------------------------------------------------
#
#class write_half_word_seq extends ubus_base_sequence
#
#  function new(string name="write_half_word_seq")
#    super.new(name)
#  endfunction
#
#  `uvm_object_utils(write_half_word_seq)
#
#  rand bit [15:0] start_addr
#  rand bit [7:0] data0
#  rand bit [7:0] data1
#  rand int unsigned transmit_del = 0
#  constraint transmit_del_ct { transmit_del <= 10; }
#
#  virtual task body()
#    `uvm_do_with(req,
#      { req.addr == start_addr;
#        req.read_write == WRITE
#        req.size == 2;
#        req.data[0] == data0; req.data[1] == data1
#        req.error_pos == 1000;
#        req.transmit_delay == transmit_del; } )
#    `uvm_info(get_type_name(),
#      $sformatf("%s wrote : addr = `x%0h, data[0] = `x%0h, data[1] = `x%0h",
#      get_sequence_path(), req.addr, req.data[0], req.data[1]), UVM_HIGH)
#  endtask
#
#endclass : write_half_word_seq
#
#
#//------------------------------------------------------------------------------
#//
#// SEQUENCE: write_word_seq
#//
#//------------------------------------------------------------------------------
#
#class write_word_seq extends ubus_base_sequence
#
#  function new(string name="write_word_seq")
#    super.new(name)
#  endfunction
#
#  `uvm_object_utils(write_word_seq)
#
#  rand bit [15:0] start_addr
#  rand bit [7:0] data0; rand bit [7:0] data1
#  rand bit [7:0] data2; rand bit [7:0] data3
#  rand int unsigned transmit_del = 0
#  constraint transmit_del_ct { (transmit_del <= 10); }
#
#  virtual task body()
#    `uvm_do_with(req,
#      { req.addr == start_addr
#        req.read_write == WRITE
#        req.size == 4
#         req.data[0] == data0; req.data[1] == data1
#         req.data[2] == data2; req.data[3] == data3
#        req.error_pos == 1000
#        req.transmit_delay == transmit_del; } )
#    `uvm_info(get_type_name(),
#      $sformatf("%s wrote : addr = `x%0h, data[0] = `x%0h, \
#      data[1] = `x%0h, data[2] = `x%0h, data[3] = `x%0h",
#      get_sequence_path(), req.addr, req.data[0],
#      req.data[1], req.data[2], req.data[3]),
#      UVM_HIGH)
#  endtask
#
#endclass : write_word_seq
#
#
#//------------------------------------------------------------------------------
#//
#// SEQUENCE: write_double_word_seq
#//
#//------------------------------------------------------------------------------
#
#class write_double_word_seq extends ubus_base_sequence
#
#  function new(string name="write_double_word_seq")
#    super.new(name)
#  endfunction
#
#  `uvm_object_utils(write_double_word_seq)
#
#  rand bit [15:0] start_addr
#  rand bit [7:0] data0; rand bit [7:0] data1
#  rand bit [7:0] data2; rand bit [7:0] data3
#  rand bit [7:0] data4; rand bit [7:0] data5
#  rand bit [7:0] data6; rand bit [7:0] data7
#  rand int unsigned transmit_del = 0
#  constraint transmit_del_ct { (transmit_del <= 10); }
#
#  virtual task body()
#    `uvm_do_with(req,
#      { req.addr == start_addr
#        req.read_write == WRITE
#        req.size == 8
#         req.data[0] == data0; req.data[1] == data1
#         req.data[2] == data2; req.data[3] == data3
#         req.data[4] == data4; req.data[5] == data5
#         req.data[6] == data6; req.data[7] == data7
#        req.error_pos == 1000
#        req.transmit_delay == transmit_del; } )
#    `uvm_info(get_type_name(),
#      $sformatf("Writing  %s : addr = `x%0h, data[0] = `x%0h, \
#      data[1] = `x%0h, data[2] = `x%0h, data[3] = `x%0h, data[4] = `x%0h, \
#      data[5] = `x%0h, data[6] = `x%0h, data[7] = `x%0h",
#      get_sequence_path(), req.addr, req.data[0], req.data[1], req.data[2],
#      req.data[3], req.data[4], req.data[5], req.data[6], req.data[7]),
#      UVM_HIGH)
#  endtask
#
#endclass : write_double_word_seq
#
#
