#//------------------------------------------------------------------------------
#//   Copyright 2007-2011 Mentor Graphics Corporation
#//   Copyright 2007-2010 Cadence Design Systems, Inc.
#//   Copyright 2010 Synopsys, Inc.
#//   Copyright 2019 Tuomas Poikela (tpoikela)
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
#//------------------------------------------------------------------------------
"""
Title: Sequence-Related Functions

Group: Sequence Action Functions

NOTE: Each macro defines `seq_obj` argument, which is `self` argument within
the sequence member functions. `seq_obj` is not present in SystemVerilog UVM
since the context comes from where the macro is used.

These functions are used to start sequences and sequence items on the default
sequencer, `m_sequencer`. This is determined a number of ways.
- the sequencer handle provided in the `UVMSequenceBase.start` method
- the sequencer used by the parent sequence
- the sequencer that was set using the `UVMSequenceItem::set_sequencer` method

"""

import cocotb
from .uvm_message_defines import uvm_warning, uvm_fatal


def uvm_create(seq_obj, SEQ_OR_ITEM, m_sequencer):
    """
    This action creates the item or sequence using the factory.  It intentionally
    does zero processing.  After this action completes, the user can manually set
    values, manipulate rand_mode and constraint_mode, etc.

    Args:
        seq_obj (UVMSequence): Sequence from which the function is called
    """
    return uvm_create_on(seq_obj, SEQ_OR_ITEM, m_sequencer)




async def uvm_do(seq_obj, SEQ_OR_ITEM):
    """
    This macro takes as an argument a uvm_sequence_item variable or object.
    The argument is created using `uvm_create` if necessary,
    then randomized.
    In the case of an item, it is randomized after the call to
    `UVMSequenceBase.start_item()` returns.
    This is called late-randomization.
    In the case of a sequence, the sub-sequence is started using
    `UVMSequenceBase.start_item()` with `call_pre_post` set to 0.
    In the case of an item,
    the item is sent to the driver through the associated sequencer.
    
    For a sequence item, the following are called, in order::
    
       uvm_create(item)
       sequencer.wait_for_grant(prior) (task)
       this.pre_do(1)                  (task)
       item.randomize()
       this.mid_do(item)               (func)
       sequencer.send_request(item)    (func)
       sequencer.wait_for_item_done()  (task)
       this.post_do(item)              (func)
    
    For a sequence, the following are called, in order::
    
       uvm_create(sub_seq)
       sub_seq.randomize()
       sub_seq.pre_start()         (task)
       this.pre_do(0)              (task)
       this.mid_do(sub_seq)        (func)
       await sub_seq.body()              (task)
       this.post_do(sub_seq)       (func)
       sub_seq.post_start()        (task)
   """
    
    await uvm_do_on_pri_with(seq_obj, SEQ_OR_ITEM, seq_obj.m_sequencer, -1, [])


#// MACRO: `uvm_do_pri
#//
#//| `uvm_do_pri(SEQ_OR_ITEM, PRIORITY)
#//
#// This is the same as `uvm_do except that the sequence item or sequence is
#// executed with the priority specified in the argument
#
#`define uvm_do_pri(SEQ_OR_ITEM, PRIORITY) \
#  `uvm_do_on_pri_with(SEQ_OR_ITEM, m_sequencer, PRIORITY, {})


async def uvm_do_with(seq_obj, SEQ_OR_ITEM, *CONSTRAINTS):
    """
    This is the same as `uvm_do except that the constraint block in the 2nd
    argument is applied to the item or sequence in a randomize with statement
    before execution.
    """
    await uvm_do_on_pri_with(seq_obj, SEQ_OR_ITEM, seq_obj.m_sequencer, -1,
            *CONSTRAINTS)


async def uvm_do_pri_with(seq_obj, SEQ_OR_ITEM, PRIORITY, *CONSTRAINTS):
    """
    This is the same as `uvm_do_pri except that the given constraint block is
    applied to the item or sequence in a randomize with statement before
    execution.
    """
    await uvm_do_on_pri_with(seq_obj, SEQ_OR_ITEM, seq_obj.m_sequencer,
            PRIORITY, *CONSTRAINTS)


"""
Group: Sequence on Sequencer Action Macros

These macros are used to start sequences and sequence items on a specific
sequencer. The sequence or item is created and executed on the given
sequencer.
"""


def uvm_create_on(seq_obj, SEQ_OR_ITEM, SEQR):
    """
    This is the same as <`uvm_create> except that it also sets the parent sequence
    to the sequence in which the macro is invoked, and it sets the sequencer to
    the specified ~SEQR~ argument.
    """
    w_ = SEQ_OR_ITEM.get_type()
    if w_ is None:
        uvm_fatal("uvm_create_on",
            "Object {} not registered with factory".format(SEQ_OR_ITEM.get_name()))
        return None
    else:
        return seq_obj.create_item(w_, SEQR, "SEQ_OR_ITEM")


async def uvm_do_on(seq_obj, SEQ_OR_ITEM, SEQR):
    """
    This is the same as <`uvm_do> except that it also sets the parent sequence to
    the sequence in which the macro is invoked, and it sets the sequencer to the
    specified ~SEQR~ argument.
    """
    await uvm_do_on_pri_with(seq_obj, SEQ_OR_ITEM, SEQR, -1, {})


#// MACRO: `uvm_do_on_pri
#//
#//| `uvm_do_on_pri(SEQ_OR_ITEM, SEQR, PRIORITY)
#//
#// This is the same as <`uvm_do_pri> except that it also sets the parent sequence
#// to the sequence in which the macro is invoked, and it sets the sequencer to
#// the specified ~SEQR~ argument.
#
#`define uvm_do_on_pri(SEQ_OR_ITEM, SEQR, PRIORITY) \
#  `uvm_do_on_pri_with(SEQ_OR_ITEM, SEQR, PRIORITY, {})


async def uvm_do_on_with(seq_obj, SEQ_OR_ITEM, SEQR, *CONSTRAINTS):
    """
    This is the same as `uvm_do_with` except that it also sets the parent
    sequence to the sequence in which the macro is invoked, and it sets the
    sequencer to the specified ~SEQR~ argument.
    The user must supply the constraints using lambdas.

    An example call::

        await uvm_do_on_with(self, sys0_seq, None,
            lambda num_blk_seq: num_blk_seq == 10,
            lambda blk_level_delay_ns: blk_level_delay_ns in [10, 20],
        )

    Note that variables used in lambdas must exist, or an exception is thrown
    due to randomization error.
    """
    await uvm_do_on_pri_with(seq_obj, SEQ_OR_ITEM, SEQR, -1,
            *CONSTRAINTS)

#`define uvm_do_on_pri_with(SEQ_OR_ITEM, SEQR, PRIORITY, CONSTRAINTS) \
#  begin \
#  uvm_sequence_base __seq; \
#  `uvm_create_on(SEQ_OR_ITEM, SEQR) \
#  if (!$cast(__seq,SEQ_OR_ITEM)) start_item(SEQ_OR_ITEM, PRIORITY);\
#  if ((__seq == null || !__seq.do_not_randomize) && !SEQ_OR_ITEM.randomize() with CONSTRAINTS ) begin \
#    `uvm_warning("RNDFLD", "Randomization failed in uvm_do_with action") \
#  end\
#  if (!$cast(__seq,SEQ_OR_ITEM)) finish_item(SEQ_OR_ITEM, PRIORITY); \
#  else __seq.start(SEQR, this, PRIORITY, 0); \
#  end
async def uvm_do_on_pri_with(seq_obj, SEQ_OR_ITEM, SEQR, PRIORITY, *CONSTRAINTS):
    """
    This is the same as uvm_do_pri_with except that it also sets the parent
    sequence to the sequence in which the function is invoked, and it sets the
    sequencer to the specified ~SEQR~ argument.

    Args:
        seq_obj (UVMSequence): Sequence context.
        SEQ_OR_ITEM (UVMSequence|UVMSequenceItem): 
        SEQR (UVMSequencer): Runs sequence on this sequencer.
        CONSTRAINTS (constraints): Randomization constraints
    """
    from ..seq.uvm_sequence import UVMSequence
    _seq = uvm_create_on(seq_obj, SEQ_OR_ITEM, SEQR)
    if isinstance(_seq, UVMSequence):
        if SEQ_OR_ITEM.do_not_randomize == 0:
            if SEQ_OR_ITEM.randomize_with(*CONSTRAINTS) is False:
                uvm_warning("RNDFLD", "Randomization failed in uvm_do_with action")
        await SEQ_OR_ITEM.start(SEQR, seq_obj, PRIORITY, 0)
    else:
        # TODO handle constraints
        await seq_obj.start_item(SEQ_OR_ITEM, PRIORITY)
        if SEQ_OR_ITEM.randomize_with(*CONSTRAINTS) is False:
            uvm_warning("RNDFLD", "Randomization failed in uvm_do_with action")
        await seq_obj.finish_item(SEQ_OR_ITEM, PRIORITY)


"""
Group: Sequence Action Functions for Pre-Existing Sequences

These functions are used to start sequences and sequence items that do not
need to be created.
"""

#`define uvm_send(SEQ_OR_ITEM) \
#  `uvm_send_pri(SEQ_OR_ITEM, -1)
async def uvm_send(seq_obj, SEQ_OR_ITEM):
    """
    This function processes the item or sequence that has been created using
    `uvm_create`.  The processing is done without randomization.  Essentially, an
    `uvm_do` without the create or randomization.

    Args:
        seq_obj (UVMSequence): Sequence context.
        SEQ_OR_ITEM (UVMSequence|UVMSequenceItem): 
    """
    await uvm_send_pri(seq_obj, SEQ_OR_ITEM, -1)



#`define uvm_send_pri(SEQ_OR_ITEM, PRIORITY) \
#  begin \
#  uvm_sequence_base __seq; \
#  if (!$cast(__seq,SEQ_OR_ITEM)) begin \
#     start_item(SEQ_OR_ITEM, PRIORITY);\
#     finish_item(SEQ_OR_ITEM, PRIORITY);\
#  end \
#  else __seq.start(__seq.get_sequencer(), this, PRIORITY, 0);\
#  end
async def uvm_send_pri(seq_obj, SEQ_OR_ITEM, PRIORITY):
    """
    This is the same as `uvm_send` except that the sequence item or sequence is
    executed with the priority specified in the argument.

    Args:
        seq_obj (UVMSequence): Sequence context.
        SEQ_OR_ITEM (UVMSequence|UVMSequenceItem): 
        PRIORITY (int): Priority of the sequence
    """
    from ..seq.uvm_sequence import UVMSequence
    _seq = SEQ_OR_ITEM
    if isinstance(_seq, UVMSequence):
        await _seq.start(_seq.get_sequencer(), seq_obj, PRIORITY, 0)
    else:
        await seq_obj.start_item(SEQ_OR_ITEM, PRIORITY)
        await seq_obj.finish_item(SEQ_OR_ITEM, PRIORITY)


#// MACRO: `uvm_rand_send
#//
#//| `uvm_rand_send(SEQ_OR_ITEM)
#//
#// This macro processes the item or sequence that has been already been
#// allocated (possibly with `uvm_create). The processing is done with
#// randomization.  Essentially, an `uvm_do without the create.
#
#`define uvm_rand_send(SEQ_OR_ITEM) \
#  `uvm_rand_send_pri_with(SEQ_OR_ITEM, -1, {})


#// MACRO: `uvm_rand_send_pri
#//
#//| `uvm_rand_send_pri(SEQ_OR_ITEM, PRIORITY)
#//
#// This is the same as `uvm_rand_send except that the sequence item or sequence
#// is executed with the priority specified in the argument.
#
#`define uvm_rand_send_pri(SEQ_OR_ITEM, PRIORITY) \
#  `uvm_rand_send_pri_with(SEQ_OR_ITEM, PRIORITY, {})


#// MACRO: `uvm_rand_send_with
#//
#//| `uvm_rand_send_with(SEQ_OR_ITEM, CONSTRAINTS)
#//
#// This is the same as `uvm_rand_send except that the given constraint block is
#// applied to the item or sequence in a randomize with statement before
#// execution.
#
#`define uvm_rand_send_with(SEQ_OR_ITEM, CONSTRAINTS) \
#  `uvm_rand_send_pri_with(SEQ_OR_ITEM, -1, CONSTRAINTS)


#// MACRO: `uvm_rand_send_pri_with
#//
#//| `uvm_rand_send_pri_with(SEQ_OR_ITEM, PRIORITY, CONSTRAINTS)
#//
#// This is the same as `uvm_rand_send_pri except that the given constraint block
#// is applied to the item or sequence in a randomize with statement before
#// execution.
#
#`define uvm_rand_send_pri_with(SEQ_OR_ITEM, PRIORITY, CONSTRAINTS) \
#  begin \
#  uvm_sequence_base __seq; \
#  if (!$cast(__seq,SEQ_OR_ITEM)) start_item(SEQ_OR_ITEM, PRIORITY);\
#  else __seq.set_item_context(this,SEQ_OR_ITEM.get_sequencer()); \
#  if ((__seq == null || !__seq.do_not_randomize) && !SEQ_OR_ITEM.randomize() with CONSTRAINTS ) begin \
#    `uvm_warning("RNDFLD", "Randomization failed in uvm_rand_send_with action") \
#  end\
#  if (!$cast(__seq,SEQ_OR_ITEM)) finish_item(SEQ_OR_ITEM, PRIORITY);\
#  else __seq.start(__seq.get_sequencer(), this, PRIORITY, 0);\
#  end


#`define uvm_create_seq(UVM_SEQ, SEQR_CONS_IF) \
#  `uvm_create_on(UVM_SEQ, SEQR_CONS_IF.consumer_seqr) \

#`define uvm_do_seq(UVM_SEQ, SEQR_CONS_IF) \
#  `uvm_do_on(UVM_SEQ, SEQR_CONS_IF.consumer_seqr) \

#`define uvm_do_seq_with(UVM_SEQ, SEQR_CONS_IF, CONSTRAINTS) \
#  `uvm_do_on_with(UVM_SEQ, SEQR_CONS_IF.consumer_seqr, CONSTRAINTS) \


#//-----------------------------------------------------------------------------
#//
#// Group- Sequence Library
#//
#//-----------------------------------------------------------------------------


#// MACRO: `uvm_add_to_sequence_library
#//
#// Adds the given sequence ~TYPE~ to the given sequence library ~LIBTYPE~
#//
#//| `uvm_add_to_seq_lib(TYPE,LIBTYPE)
#//
#// Invoke any number of times within a sequence declaration to statically add
#// that sequence to one or more sequence library types. The sequence will then
#// be available for selection and execution in all instances of the given
#// sequencer types.
#//
#//| class seqA extends uvm_sequence_base #(simple_item);
#//|
#//|    function new(string name=`"TYPE`");
#//|      super.new(name);
#//|    endfunction
#//|
#//|    `uvm_object_utils(seqA)
#//|
#//|    `uvm_add_to_seq_lib(seqA, simple_seq_lib_RST)
#//|    `uvm_add_to_seq_lib(seqA, simple_seq_lib_CFG)
#//|
#//|    virtual task body(); \
#//|      `uvm_info("SEQ_START", {"Executing sequence '", get_full_name(),
#//|                             "' (",get_type_name(),")"},UVM_HIGH)
#//|      #10;
#//|    endtask
#//|
#//|  endclass
#
#
#`define uvm_add_to_seq_lib(TYPE,LIBTYPE) \
#   static bit add_``TYPE``_to_seq_lib_``LIBTYPE =\
#      LIBTYPE::m_add_typewide_sequence(TYPE::get_type());



#// MACRO: `uvm_sequence_library_utils
#//
#//| `uvm_sequence_library_utils(TYPE)
#//
#// Declares the infrastructure needed to define extensions to the
#// <uvm_sequence_library> class. You define new sequence library subtypes
#// to statically specify sequence membership from within sequence
#// definitions. See also <`uvm_add_to_sequence_library> for more information.
#//
#//
#//| typedef simple_seq_lib uvm_sequence_library #(simple_item);
#//|
#//| class simple_seq_lib_RST extends simple_seq_lib;
#//|
#//|   `uvm_object_utils(simple_seq_lib_RST)
#//|
#//|   `uvm_sequence_library_utils(simple_seq_lib_RST)
#//|
#//|   function new(string name="");
#//|     super.new(name);
#//|   endfunction
#//|
#//| endclass
#//
#// Each library, itself a sequence, can then be started independently
#// on different sequencers or in different phases of the same sequencer.
#// See <uvm_sequencer_base::start_phase_sequence> for information on
#// starting default sequences.
#
#`define uvm_sequence_library_utils(TYPE) \
#\
#   static protected uvm_object_wrapper m_typewide_sequences[$]; \
#   \
#   function void init_sequence_library(); \
#     foreach (TYPE::m_typewide_sequences[i]) \
#       sequences.push_back(TYPE::m_typewide_sequences[i]); \
#   endfunction \
#   \
#   static function void add_typewide_sequence(uvm_object_wrapper seq_type); \
#     if (m_static_check(seq_type)) \
#       TYPE::m_typewide_sequences.push_back(seq_type); \
#   endfunction \
#   \
#   static function void add_typewide_sequences(uvm_object_wrapper seq_types[$]); \
#     foreach (seq_types[i]) \
#       TYPE::add_typewide_sequence(seq_types[i]); \
#   endfunction \
#   \
#   static function bit m_add_typewide_sequence(uvm_object_wrapper seq_type); \
#     TYPE::add_typewide_sequence(seq_type); \
#     return 1; \
#   endfunction



#//-----------------------------------------------------------------------------
#//
#// Group: Sequencer Subtypes
#//
#//-----------------------------------------------------------------------------
#
#
#// MACRO: `uvm_declare_p_sequencer
#//
#// This macro is used to declare a variable ~p_sequencer~ whose type is
#// specified by ~SEQUENCER~.
#//
#//| `uvm_declare_p_sequencer(SEQUENCER)
#//
#// The example below shows using the `uvm_declare_p_sequencer macro
#// along with the uvm_object_utils macros to set up the sequence but
#// not register the sequence in the sequencer's library.
#//
#//| class mysequence extends uvm_sequence#(mydata);
#//|   `uvm_object_utils(mysequence)
#//|   `uvm_declare_p_sequencer(some_seqr_type)
#//|   task body;
#//|     //Access some variable in the user's custom sequencer
#//|     if(p_sequencer.some_variable) begin
#//|       ...
#//|     end
#//|   endtask
#//| endclass
#//

#`define uvm_declare_p_sequencer(SEQUENCER) \
#  SEQUENCER p_sequencer;\
#  virtual function void m_set_p_sequencer();\
#    super.m_set_p_sequencer(); \
#    if( !$cast(p_sequencer, m_sequencer)) \
#        `uvm_fatal("DCLPSQ", \
#        $sformatf("%m %s Error casting p_sequencer, please verify that this sequence/sequence item is intended to execute on this type of sequencer", get_full_name())) \
#  endfunction
