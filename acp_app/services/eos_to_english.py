import os
from collections import namedtuple
import re


def is_set(decimal_word, bit_number):
    decimal_word, bit_number = int(decimal_word), int(bit_number)
    return (decimal_word & 1 << bit_number) != 0


def parse_discrete_io(word_num, bit_num, state_num):
    """Parses 3 variables into either a discrete IO address or
    into a Binary EOS and the prefered state"""

    # state = 0 or 1
    state = is_set(state_num, 0)
    # input_type 0 = I/O, 1 = Binary
    is_binary = is_set(state_num, 1)

    if is_binary:
        input_text = f'Binary_EOS[{word_num}].{bit_num}'
    else:
        rack_num = word_num // 10
        mod_num = word_num % 10
        if bit_num > 7:
            bit_num -= 2
        input_text = f'rack {rack_num} mod {mod_num} bit {bit_num} (Real_Inputs[{word_num}].{bit_num})'

    parsed_discrete_io = namedtuple('io', ['address', 'state'])

    return parsed_discrete_io(input_text, state)


def parse_analog(analog_num, greater_than, analog_preset, equal_to=True):
    if greater_than:
        compare = 'greater than'
    else:
        compare = 'less than'

    if equal_to:
        compare += ' or equal to'

    return f'Analog_Variables[{analog_num}] is {compare} {analog_preset}'


def parse_time(time_preset):
    hours = time_preset / 3600
    mins = time_preset / 60
    secs = time_preset

    if time_preset >= 3600:
        return f'the time in step exceeds {hours:.2f} hours ({mins:.2f} minutes)'
    else:
        return f'the time in step exceeds {mins:.2f} minutes ({secs} seconds)'


def parse_xfer_on(state_num):

    if state_num:
        return f'transfer on DI'
    else:
        return f'transfer on process'


def parse_process_step_range(process_num, low_step, high_step, in_range=True, unit_count=0, is_greater=True):
    # Process number and steps
    comp_state = {True : 'or more', False: 'or less'}
    if unit_count == 0:
        if in_range:
            return f'any unit of process {process_num} is between steps {low_step} and {high_step}'
        else:
            return f'any unit of process {process_num} is not between steps {low_step} and {high_step}'
    else:
        return f'{unit_count} {comp_state[is_greater]} units of process {process_num} is between steps {low_step} and {high_step}'
    


def parse_process_either_step(process_num,
                              step_num1,
                              step_num2=None,
                              in_step=True):
    # Process number and steps
    if (step_num1 != step_num2) & (step_num2 is not None):
        # 2 unique steps
        if in_step:
            return f'any unit of process {process_num} is in steps {step_num1} or {step_num2}'
        else:
            return f'any unit of process {process_num} is not in steps {step_num1} or {step_num2}'
    else:
        # Same step in both or only 1 step
        if in_step:
            return f'any unit of process {process_num} is in step {step_num1}'
        else:
            return f'any unit of process {process_num} is not in step {step_num1}'


def parse_process_both_steps(process_num, step_num1, step_num2, in_step=True):
    # Process number and steps
    if in_step:
        return f'any two units of process {process_num} are in steps {step_num1} and {step_num2}'
    else:
        return f'any two units of process {process_num} are not in steps {step_num1} and {step_num2}'


def parse_unit_step_range(unit_num, low_step, high_step, in_range=True):
    # Unit number and steps
    if in_range:
        return f'unit {unit_num} is between steps {low_step} and {high_step}'
    else:
        return f'unit {unit_num} is not between steps {low_step} and {high_step}'


def parse_unit_either_step(unit_num, step_num1, step_num2=None, in_step=True):
    # Unit number and steps
    if (step_num1 != step_num2) & (step_num2 is not None):
        # 2 unique steps
        if in_step:
            return f'unit {unit_num} is in steps {step_num1} or {step_num2}'
        else:
            return f'unit {unit_num} is not in steps {step_num1} or {step_num2}'
    else:
        # Same step in both or only 1 step
        if in_step:
            return f'unit {unit_num} is in step {step_num1}'
        else:
            return f'unit {unit_num} is not in step {step_num1}'


def parse_unit_seq_range(unit_num, low_seq, high_seq, in_range=True):
    '''Units in a sequence within a range'''

    if unit_num is None:
        unit_num = 'current unit'
    else:
        unit_num = f'unit {unit_num}'

    if in_range:
        return f'{unit_num} is between sequence {low_seq} and {high_seq}'
    else:
        return f'{unit_num} is not between sequence {low_seq} and {high_seq}'


def parse_step_transition(step_num, keepxfr=False):
    step_branch.branch_to.append(step_num)
    step_branch.keepxfr = keepxfr
    return f'transfer to step {step_num}', step_branch


def extract_steps(step_nums):
    first = step_nums // 100
    second = step_nums % 100
    extracted_steps = namedtuple('steps', ['first', 'second'])

    return extracted_steps(first=first, second=second)


# The end of step conditions


def eos_0(eos_mod_1=None,
          eos_mod_2=None,
          eos_mod_3=None,
          eos_mod_4=None,
          eos_mod_5=None,
          eos_mod_6=None,
          eos_mod_7=None,
          eos_mod_8=None):
    """End of Step 0: Requires an operator to advance the sequence
    Inputs:
        None
    Outputs:
        A formatted string"""

    return 'an operator advances out of the step manually.'


def eos_1(eos_mod_1=None,
          eos_mod_2=None,
          eos_mod_3=None,
          eos_mod_4=None,
          eos_mod_5=None,
          eos_mod_6=None,
          eos_mod_7=None,
          eos_mod_8=None):
    """End of Step 1: A bit (binary or real I/O) needs to be in the specified state
    Inputs:
        eos_mod_1,
        eos_mod_2,
        eos_mod_3
    Outputs:
        A formatted string"""
    io = parse_discrete_io(word_num=eos_mod_1,
                           bit_num=eos_mod_2,
                           state_num=eos_mod_3)

    return f'''{io.address} is {io.state}.'''


def eos_2(eos_mod_1=None,
          eos_mod_2=None,
          eos_mod_3=None,
          eos_mod_4=None,
          eos_mod_5=None,
          eos_mod_6=None,
          eos_mod_7=None,
          eos_mod_8=None):
    """End of Step 2: An Analog_Variables word is greater than a preset value
    Inputs:
        eos_mod_1,
        eos_mod_8
    Outputs:
        A formatted string"""

    analog_text = parse_analog(analog_num=eos_mod_1,
                               greater_than=True,
                               analog_preset=eos_mod_8,
                               equal_to=False)

    return f'{analog_text}.'


def eos_3(eos_mod_1=None,
          eos_mod_2=None,
          eos_mod_3=None,
          eos_mod_4=None,
          eos_mod_5=None,
          eos_mod_6=None,
          eos_mod_7=None,
          eos_mod_8=None):
    """End of Step 3: An Analog_Variables word is less than a preset value
    Inputs:
        eos_mod_1,
        eos_mod_8
    Outputs:
        A formatted string"""

    analog_text = parse_analog(analog_num=eos_mod_1,
                               greater_than=False,
                               analog_preset=eos_mod_8,
                               equal_to=False)

    return f'{analog_text}.'


def eos_4(eos_mod_1=None,
          eos_mod_2=None,
          eos_mod_3=None,
          eos_mod_4=None,
          eos_mod_5=None,
          eos_mod_6=None,
          eos_mod_7=None,
          eos_mod_8=None):
    '''End of Step 4: The time in step is greater than the preset value
    Inputs:
        eos_mod_7
    Outputs:
        A formatted string'''

    time_text = parse_time(eos_mod_7)

    return f'''{time_text}.'''


def eos_5(eos_mod_1=None,
          eos_mod_2=None,
          eos_mod_3=None,
          eos_mod_4=None,
          eos_mod_5=None,
          eos_mod_6=None,
          eos_mod_7=None,
          eos_mod_8=None):
    '''End of Step 5: A unit is between 2 steps in a range
    Inputs:
        eos_mod_1
        eos_mod_2
        eos_mod_3
    Outputs:
        A formatted string'''

    unit_text = parse_unit_step_range(unit_num=eos_mod_1,
                                      low_step=eos_mod_2,
                                      high_step=eos_mod_3)

    return f'''{unit_text}.'''


def eos_6(eos_mod_1=None,
          eos_mod_2=None,
          eos_mod_3=None,
          eos_mod_4=None,
          eos_mod_5=None,
          eos_mod_6=None,
          eos_mod_7=None,
          eos_mod_8=None):
    '''End of Step 6: A unit is not between 2 steps in a range
    Inputs:
        eos_mod_1
        eos_mod_2
        eos_mod_3
    Outputs:
        A formatted string'''

    unit_text = parse_unit_step_range(unit_num=eos_mod_1,
                                      low_step=eos_mod_2,
                                      high_step=eos_mod_3,
                                      in_range=False)

    return f'''{unit_text}.'''


def eos_11(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    return '''the first scan is over, it's always true.'''


def eos_17(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    io = parse_discrete_io(word_num=eos_mod_5,
                           bit_num=eos_mod_2,
                           state_num=eos_mod_6)

    input_text = f'''{io.address} is {io.state}'''

    analog_text = parse_analog(analog_num=eos_mod_1, greater_than=True, analog_preset=eos_mod_8)

    unit_text = parse_unit_either_step(unit_num='in current process', step_num1=eos_mod_3, step_num2=eos_mod_4)

    time_text = parse_time(time_preset=eos_mod_7)
    
    return f'{analog_text} or {unit_text} or {input_text} and {time_text}.'


def eos_20(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    process_text = parse_process_either_step(process_num=eos_mod_1,
                                             step_num1=eos_mod_2,
                                             step_num2=eos_mod_3)
    return f'{process_text}.'


def eos_21(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    # Discrete address
    io = parse_discrete_io(word_num=eos_mod_1,
                           bit_num=eos_mod_2,
                           state_num=eos_mod_3)

    input_text = f'''{io.address} is {io.state}'''

    # Time in step
    time_text = parse_time(eos_mod_7)

    # Sequence transitions
    step_list = [
        eos_mod_4,
        extract_steps(eos_mod_5).second,
        extract_steps(eos_mod_5).first,
        extract_steps(eos_mod_6).second,
        extract_steps(eos_mod_6).first
    ]

    seq_text = ''
    for seq, step in enumerate(step_list, 1):
        seq_text += f'in sequence {seq} {parse_step_transition(step)[0]}, '

    # Drop the last ', ' from the list
    seq_text = seq_text[:-2]

    return f'''{time_text}. If {input_text} then the GCC continues. If {not(io.state)} then {seq_text}.'''


def eos_22(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    '''End of Step 22: (A bit (binary or real I/O) needs to be in the specified state and the time in step is greater
    than a preset value) or (Any unit of a specified process is in a step)
    Inputs:
        eos_mod_1
        eos_mod_2
        eos_mod_3
        eos_mod_4
        eos_mod_5
        eos_mod_6
        eos_mod_7
    Outputs:
        A formatted string'''

    # Discrete address
    io = parse_discrete_io(word_num=eos_mod_4,
                           bit_num=eos_mod_5,
                           state_num=eos_mod_6)
    input_text = f'''{io.address} is {io.state}'''

    # Time in step
    time_text = parse_time(eos_mod_7)

    # Process number and steps
    process_text = parse_process_either_step(process_num=eos_mod_1,
                                             step_num1=eos_mod_2,
                                             step_num2=eos_mod_3)

    return f'''{input_text} after {time_text} or when {process_text}.'''


def eos_23(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    process_text = parse_process_both_steps(process_num=eos_mod_1,
                                            step_num1=eos_mod_2,
                                            step_num2=eos_mod_3)
    return f'{process_text}.'


def eos_25(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    # Discrete address
    io = parse_discrete_io(word_num=eos_mod_1,
                           bit_num=eos_mod_2,
                           state_num=eos_mod_3)
    input_text = f'''{io.address} is {io.state}'''

    # Analog Address
    greater = is_set(eos_mod_3, 2)
    analog_text = parse_analog(analog_num=eos_mod_4,
                               greater_than=greater,
                               analog_preset=eos_mod_8)

    # Time in step
    time_text = parse_time(eos_mod_7)

    # Step transfers
    step_text1, step_num1 = parse_step_transition(eos_mod_5)
    step_text2, step_num2 = parse_step_transition(eos_mod_6)

    return f'{input_text} {step_text1}, or if {time_text} and {analog_text} {step_text2}.'


def eos_26(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    # Discrete address
    io = parse_discrete_io(word_num=eos_mod_1,
                           bit_num=eos_mod_2,
                           state_num=eos_mod_3)
    input_text = f'''{io.address} is {io.state}'''

    # Analog Address
    greater = is_set(eos_mod_3, 2)
    analog_text = parse_analog(analog_num=eos_mod_4,
                               greater_than=greater,
                               analog_preset=eos_mod_8)

    # Time in step
    time_text = parse_time(eos_mod_7)

    # Step transfers
    step_text, step_num = parse_step_transition(eos_mod_5)

    return f'{input_text} {step_text}, or if {time_text} and {analog_text} the GCC continues.'


def eos_27(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    # Analog Address
    analog_text = parse_analog(analog_num=eos_mod_1,
                               greater_than=eos_mod_2,
                               analog_preset=eos_mod_8)
    # Discrete address
    io = parse_discrete_io(word_num=eos_mod_4,
                           bit_num=eos_mod_5,
                           state_num=eos_mod_6)
    input_text = f'''{io.address} is {io.state}'''

    return f'{analog_text} or {input_text}.'


def eos_28(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    # Analog Address
    analog_text = parse_analog(analog_num=eos_mod_1,
                               greater_than=eos_mod_2,
                               analog_preset=eos_mod_8)
    # Discrete address
    io = parse_discrete_io(word_num=eos_mod_4,
                           bit_num=eos_mod_5,
                           state_num=eos_mod_6)
    input_text = f'''{io.address} is {io.state}'''

    return f'{analog_text} and {input_text}.'


def eos_29(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    # Analog Address
    analog_text = parse_analog(analog_num=eos_mod_1,
                               greater_than=eos_mod_2,
                               analog_preset=eos_mod_8)
    # Time in step
    time_text = parse_time(eos_mod_7)

    # Process number and steps
    process_text = parse_process_either_step(process_num=eos_mod_4,
                                             step_num1=eos_mod_5,
                                             step_num2=eos_mod_6,
                                             in_step=eos_mod_3)

    return f'{analog_text} and {time_text}, or {process_text}.'


def eos_30(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    # Analog Address
    analog_text = parse_analog(analog_num=eos_mod_1,
                               greater_than=eos_mod_2,
                               analog_preset=eos_mod_8)
    # Time in step
    time_text = parse_time(eos_mod_7)

    return f'{analog_text} and {time_text}.'


def eos_31(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    # Analog Address
    analog_text = parse_analog(analog_num=eos_mod_1,
                               greater_than=eos_mod_2,
                               analog_preset=eos_mod_8)
    # Time in step
    time_text = parse_time(eos_mod_7)

    return f'{analog_text} or {time_text}.'


def eos_32(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    # Time in step
    time_text = parse_time(eos_mod_7)

    # Step transition
    step_text, step_num = parse_step_transition(step_num=eos_mod_1)

    return f'{time_text} {step_text}.'


def eos_33(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    # Process number and steps
    process_text = parse_process_either_step(process_num=eos_mod_1,
                                             step_num1=eos_mod_2,
                                             step_num2=eos_mod_3,
                                             in_step=eos_mod_5)

    # Analog Address
    analog_text = parse_analog(analog_num=eos_mod_4,
                               greater_than=True,
                               analog_preset=eos_mod_8,
                               equal_to=False)

    return f'{process_text} and {analog_text}.'


def eos_34(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    # Process number and steps
    process_text = parse_process_either_step(process_num=eos_mod_1,
                                             step_num1=eos_mod_2,
                                             step_num2=eos_mod_3,
                                             in_step=eos_mod_5)

    # Analog Address
    analog_text = parse_analog(analog_num=eos_mod_4,
                               greater_than=True,
                               analog_preset=eos_mod_8,
                               equal_to=False)

    return f'{process_text} or {analog_text}.'


def eos_35(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    analog_select = is_set(eos_mod_3, 0)
    greater = is_set(eos_mod_3, 1)

    # Unit number and steps
    unit_text = parse_unit_either_step(unit_num=eos_mod_1, step_num1=eos_mod_2)
    # Time in step
    time_text = parse_time(eos_mod_7)

    # Analog Address
    analog_text = parse_analog(analog_num=eos_mod_4,
                               greater_than=greater,
                               analog_preset=eos_mod_8)

    # Step transition
    step_text1, step_num = parse_step_transition(step_num=eos_mod_5)
    step_text2, step_num = parse_step_transition(step_num=eos_mod_6)

    if analog_select:
        return f'{unit_text} then {step_text1}, if {analog_text} then {step_text2}.'
    else:
        return f'{unit_text} then {step_text1}, if {time_text} then {step_text2}.'


def eos_36(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    # Discrete address
    io = parse_discrete_io(word_num=eos_mod_1,
                           bit_num=eos_mod_2,
                           state_num=eos_mod_3)
    input_text = f'''{io.address} is {io.state}'''

    # Time in step
    time_text = parse_time(eos_mod_7)

    # Step transition
    step_text1, step_num1 = parse_step_transition(step_num=eos_mod_5)
    step_text2, step_num2 = parse_step_transition(step_num=eos_mod_6)

    return f'{input_text} then {step_text1}, if {time_text} then {step_text2}.'


def eos_37(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    # Discrete address
    io1 = parse_discrete_io(word_num=eos_mod_1,
                            bit_num=eos_mod_2,
                            state_num=eos_mod_3)
    input_text1 = f'''{io1.address} is {io1.state}'''

    io2 = parse_discrete_io(word_num=eos_mod_4,
                            bit_num=eos_mod_5,
                            state_num=eos_mod_6)
    input_text2 = f'''{io2.address} is {io2.state}'''

    # Time in step
    time_text = parse_time(eos_mod_7)

    return f'{input_text1} or {time_text}, and {input_text2}.'


def eos_38(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    # Unit number and steps
    in_step1 = not (eos_mod_3)
    unit_text1 = parse_unit_either_step(unit_num=eos_mod_1,
                                        step_num1=eos_mod_2,
                                        in_step=in_step1)
    in_step2 = not (eos_mod_6)
    unit_text2 = parse_unit_either_step(unit_num=eos_mod_4,
                                        step_num1=eos_mod_5,
                                        in_step=in_step2)

    # Step transition
    step_text1, step_num1 = parse_step_transition(step_num=eos_mod_7)
    step_text2, step_num2 = parse_step_transition(step_num=eos_mod_8)

    return f'{unit_text1} then {step_text1}, if {unit_text2} then {step_text2}.'


def eos_39(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    # Discrete address
    io = parse_discrete_io(word_num=eos_mod_1,
                           bit_num=eos_mod_2,
                           state_num=eos_mod_3)
    input_text = f'''{io.address} is {io.state}'''

    # Time in step
    time_text1 = parse_time(eos_mod_7)
    time_text2 = parse_time(eos_mod_8)

    return f'{input_text} and {time_text1}, or when {time_text2}.'


def eos_41(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    # Process number and steps
    process_text1 = parse_process_either_step(process_num=eos_mod_1,
                                              step_num1=eos_mod_2,
                                              step_num2=eos_mod_3,
                                              in_step=eos_mod_5)
    process_text2 = parse_process_step_range(process_num=eos_mod_4,
                                             low_step=eos_mod_5,
                                             high_step=eos_mod_6,
                                             in_range=eos_mod_7)
    return f'{process_text1} and {process_text2}.'


def eos_42(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    # Process number and steps
    process_text1 = parse_process_either_step(process_num=eos_mod_1,
                                              step_num1=eos_mod_2,
                                              step_num2=eos_mod_3,
                                              in_step=eos_mod_5)
    process_text2 = parse_process_step_range(process_num=eos_mod_4,
                                             low_step=eos_mod_5,
                                             high_step=eos_mod_6,
                                             in_range=eos_mod_7)
    return f'{process_text1} or {process_text2}.'


def eos_43(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    # Process number and steps
    process_text = parse_process_either_step(process_num=eos_mod_1,
                                             step_num1=eos_mod_2,
                                             step_num2=eos_mod_3,
                                             in_step=eos_mod_4)
    # Time in step
    time_text = parse_time(eos_mod_7)

    return f'{process_text} and {time_text}.'


def eos_44(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    # Discrete address
    io1 = parse_discrete_io(word_num=eos_mod_1,
                            bit_num=eos_mod_2,
                            state_num=eos_mod_3)
    input_text1 = f'''{io1.address} is {io1.state}'''

    io2 = parse_discrete_io(word_num=eos_mod_4,
                            bit_num=eos_mod_5,
                            state_num=eos_mod_6)
    input_text2 = f'''{io2.address} is {io2.state}'''

    # Time in step
    time_text = parse_time(eos_mod_7)

    # Step transition
    step_text, step_num = parse_step_transition(step_num=eos_mod_8)

    return f'{input_text1} and {input_text2} then the GCC continues, or if {time_text} then {step_text}.'


def eos_45(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    # Discrete address
    io = parse_discrete_io(word_num=eos_mod_1,
                           bit_num=eos_mod_2,
                           state_num=eos_mod_3)
    input_text = f'''{io.address} is {io.state}'''

    # Time in step
    time_text = parse_time(eos_mod_7)

    # Step transition
    step_text, step_num = parse_step_transition(step_num=eos_mod_4)

    return f'{time_text} then the GCC continues, or if {input_text} then {step_text}.'


def eos_46(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    # Analog values
    greater1 = is_set(eos_mod_2, 0)
    analog_text1 = parse_analog(analog_num=eos_mod_1,
                                greater_than=greater1,
                                analog_preset=eos_mod_7)

    greater2 = is_set(eos_mod_2, 1)
    analog_text2 = parse_analog(analog_num=eos_mod_3,
                                greater_than=greater2,
                                analog_preset=eos_mod_8)

    # Discrete address
    state_num = eos_mod_2 >> 2
    io = parse_discrete_io(word_num=eos_mod_4,
                           bit_num=eos_mod_5,
                           state_num=state_num)
    input_text = f'''{io.address} is {io.state}'''

    # Step transition
    step_text, step_num = parse_step_transition(step_num=eos_mod_6)

    return f'{analog_text1} then the GCC continues, or if {analog_text2} or {input_text} then {step_text}.'


def eos_47(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    '''End of Step 47: If a unit is within or not within a step range go to the next step, or if another unit is within or not within a step range go to another step
    Inputs:
        eos_mod_1
        eos_mod_2
        eos_mod_3
        eos_mod_4
        eos_mod_5
        eos_mod_6
        eos_mod_7
        eos_mod_8
    Outputs:
        A formatted string
    '''

    # Unit number and steps
    in_range1 = is_set(eos_mod_7, 0)
    unit_text1 = parse_unit_step_range(unit_num=eos_mod_1,
                                       low_step=eos_mod_2,
                                       high_step=eos_mod_3,
                                       in_range=in_range1)

    in_range2 = is_set(eos_mod_7, 1)
    unit_text2 = parse_unit_step_range(unit_num=eos_mod_4,
                                       low_step=eos_mod_5,
                                       high_step=eos_mod_6,
                                       in_range=in_range2)

    # Step transition
    step_text, step_num = parse_step_transition(step_num=eos_mod_8)

    return f'{unit_text1} then the GCC continues, or if {unit_text2} then {step_text}.'


def eos_48(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    '''End of Step 48: If the time in step is greater than the preset value and a unit is within a sequence range go to a specified step, otherwise go to the next step
    Inputs:
        eos_mod_1
        eos_mod_2
        eos_mod_3
        eos_mod_4
        eos_mod_5
        eos_mod_6
        eos_mod_7
    Outputs:
        A formatted string
    '''
    # Time Values
    time_text = parse_time(eos_mod_7)

    # Unit number and sequences
    in_range = True

    unit_text = parse_unit_seq_range(unit_num=None,
                                     low_seq=eos_mod_4,
                                     high_seq=eos_mod_5,
                                     in_range=in_range)

    io = parse_discrete_io(word_num=eos_mod_1,
                           bit_num=eos_mod_2,
                           state_num=eos_mod_3)

    input_text = f'''{io.address} is {io.state}'''

    # Step transition
    step_text, step_num = parse_step_transition(step_num=eos_mod_6)

    return f'{unit_text} and {input_text} and {time_text} then {step_text}, or if {time_text} then the GCC continues.'


def eos_49(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    '''End of Step 48: If the time in step is greater than the preset value and a unit is within a sequence range go to a specified step, otherwise go to the next step
    Inputs:
        eos_mod_1
        eos_mod_2
        eos_mod_3
        eos_mod_4
        eos_mod_5
        eos_mod_6
        eos_mod_7
    Outputs:
        A formatted string
    '''
    pass


def eos_70(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    '''End of Step 70: The analog varible is greater than the analog preset
    or a bit (binary or real I/O) is in a specified state and time in step is great than the preset value
    Inputs:
        eos_mod_1
        eos_mod_4
        eos_mod_5
        eos_mod_6
        eos_mod_7
        eos_mod_8
    Outputs:
        A formatted string'''

    # Discrete address
    io = parse_discrete_io(word_num=eos_mod_4,
                           bit_num=eos_mod_5,
                           state_num=eos_mod_6)
    input_text = f'''{io.address} is {io.state}'''

    # Time Values
    time_text = parse_time(eos_mod_7)

    analog_text = parse_analog(analog_num=eos_mod_1, greater_than=True, analog_preset=eos_mod_8)

    return f'''{time_text} and {input_text} or {analog_text}.'''


def eos_73(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    '''End of Step 73: The time in step is greater than the preset value 
    and a bit (binary or real I/O) needs to be in the specified state
    Inputs:
        eos_mod_1
        eos_mod_2
        eos_mod_3
        eos_mod_7
    Outputs:
        A formatted string'''

    # Discrete address
    io = parse_discrete_io(word_num=eos_mod_1,
                           bit_num=eos_mod_2,
                           state_num=eos_mod_3)
    input_text = f'''{io.address} is {io.state}'''

    # Time Values
    time_text = parse_time(eos_mod_7)

    return f'''{time_text} and {input_text}.'''


def eos_74(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    '''End of Step 74: The time in step is greater than the preset value or a bit (binary or real I/O) needs to be in the specified state
    Inputs:
        eos_mod_1
        eos_mod_2
        eos_mod_3
        eos_mod_7
    Outputs:
        A formatted string'''

    # Time Values
    time_text = parse_time(eos_mod_7)

    # Discrete address
    io = parse_discrete_io(word_num=eos_mod_1,
                           bit_num=eos_mod_2,
                           state_num=eos_mod_3)
    input_text = f'''{io.address} is {io.state}'''

    return f'''{time_text} or {input_text}.'''


def eos_75(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    analog_text1 = parse_analog(analog_num=eos_mod_1,
                                greater_than=eos_mod_2,
                                analog_preset=eos_mod_7)
    step_text1, step_num1 = parse_step_transition(step_num=eos_mod_3)

    analog_text2 = parse_analog(analog_num=eos_mod_4,
                                greater_than=eos_mod_5,
                                analog_preset=eos_mod_8)
    step_text2, step_num2 = parse_step_transition(step_num=eos_mod_6)

    return f'{analog_text1} then {step_text1} or if {analog_text2} then {step_text2}.'


def eos_76(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    analog_text1 = parse_analog(analog_num=eos_mod_1, greater_than=eos_mod_2, analog_preset=eos_mod_7)
    analog_text2 = parse_analog(analog_num=eos_mod_3, greater_than=eos_mod_4, analog_preset=eos_mod_8)

    return f'{analog_text1} and {analog_text2}.'


def eos_77(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    process_text = parse_process_step_range(process_num=eos_mod_1,
                                            low_step=eos_mod_2,
                                            high_step=eos_mod_3)
    return f'{process_text}.'


def eos_80(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    '''End of Step 80: 2 bits (binary or real I/O) need to be in the specified state
    Inputs:
        eos_mod_1
        eos_mod_2
        eos_mod_3
        eos_mod_4
        eos_mod_5
        eos_mod_6
    Outputs:
        A formatted string'''

    # Discrete address
    io1 = parse_discrete_io(word_num=eos_mod_1,
                            bit_num=eos_mod_2,
                            state_num=eos_mod_3)
    input_text1 = f'''{io1.address} is {io1.state}'''

    io2 = parse_discrete_io(word_num=eos_mod_4,
                            bit_num=eos_mod_5,
                            state_num=eos_mod_6)
    input_text2 = f'''{io2.address} is {io2.state}'''

    return f'''{input_text1} and {input_text2}.'''


def eos_81(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    # Discrete address
    io1 = parse_discrete_io(word_num=eos_mod_1,
                            bit_num=eos_mod_2,
                            state_num=eos_mod_3)
    input_text1 = f'''{io1.address} is {io1.state}'''

    io2 = parse_discrete_io(word_num=eos_mod_4,
                            bit_num=eos_mod_5,
                            state_num=eos_mod_6)
    input_text2 = f'''{io2.address} is {io2.state}'''

    return f'''{input_text1} or {input_text2}.'''


def eos_82(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    # Discrete address
    io1 = parse_discrete_io(word_num=eos_mod_1,
                            bit_num=eos_mod_2,
                            state_num=eos_mod_3)
    input_text1 = f'''{io1.address} is {io1.state}'''

    io2 = parse_discrete_io(word_num=eos_mod_4,
                            bit_num=eos_mod_5,
                            state_num=eos_mod_6)
    input_text2 = f'''{io2.address} is {io2.state}'''

    time_text = parse_time(eos_mod_7)

    return f'''{input_text1} and {input_text2} or {time_text}.'''


def eos_83(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    # Discrete address
    io1 = parse_discrete_io(word_num=eos_mod_1,
                            bit_num=eos_mod_2,
                            state_num=eos_mod_3)
    input_text1 = f'''{io1.address} is {io1.state}'''

    io2 = parse_discrete_io(word_num=eos_mod_4,
                            bit_num=eos_mod_5,
                            state_num=eos_mod_6)
    input_text2 = f'''{io2.address} is {io2.state}'''

    # Time in step
    time_text = parse_time(eos_mod_7)

    return f'{input_text1} or {input_text2} or {time_text}.'


def eos_85(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    io1 = parse_discrete_io(word_num=eos_mod_1,
                            bit_num=eos_mod_2,
                            state_num=eos_mod_3)
    input_text1 = f'''{io1.address} is {io1.state}'''
    step_text1, step_num1 = parse_step_transition(step_num=eos_mod_7)

    io2 = parse_discrete_io(word_num=eos_mod_4,
                            bit_num=eos_mod_5,
                            state_num=eos_mod_6)
    input_text2 = f'''{io2.address} is {io2.state}'''
    step_text2, step_num2 = parse_step_transition(step_num=eos_mod_8)

    return f'{input_text1} then {step_text1} or if {input_text2} then {step_text2}.'


def eos_86(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    io = parse_discrete_io(word_num=eos_mod_1,
                            bit_num=eos_mod_2,
                            state_num=eos_mod_3)
    input_text = f'''{io.address} is {io.state}'''
    analog_text = parse_analog(analog_num=eos_mod_4,
                                greater_than=eos_mod_5,
                                analog_preset=eos_mod_8)
    step_text, step_num = parse_step_transition(step_num=eos_mod_6, keepxfr=True)

    return f'{input_text} then {step_text} or if {analog_text}.'


def eos_87(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    analog_text = parse_analog(analog_num=eos_mod_1,
                                greater_than=eos_mod_2,
                                analog_preset=eos_mod_8)
    step_text, step_num = parse_step_transition(step_num=eos_mod_7, keepxfr=True)
    unit_text = parse_process_step_range(process_num=eos_mod_3, low_step=eos_mod_4, high_step=eos_mod_5, in_range=eos_mod_6)

    return f'{analog_text} then {step_text} or if {unit_text}.'


def eos_93(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    analog_text1 = parse_analog(analog_num=eos_mod_1,
                                greater_than=eos_mod_2,
                                analog_preset=eos_mod_7)
    analog_text2 = parse_analog(analog_num=eos_mod_1,
                                greater_than=eos_mod_2,
                                analog_preset=eos_mod_8)                            

    return f'{analog_text1} or {analog_text2}.'


def eos_96(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    io = parse_discrete_io(word_num=eos_mod_1,
                            bit_num=eos_mod_2,
                            state_num=eos_mod_3)
    input_text = f'''{io.address} is {io.state}'''
    process_text = parse_process_step_range(process_num=eos_mod_5, low_step=eos_mod_6, high_step=eos_mod_7,in_range=(~eos_mod_4 & 1))
    xfer_to = parse_xfer_on(state_num=(eos_mod_4 << 1))
    step_text, step_num = parse_step_transition(step_num=eos_mod_8, keepxfr=True)

    return f'{input_text} then {step_text} or if {process_text}. Step will {xfer_to}.'

def eos_97(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    unit_text = parse_process_step_range(process_num=eos_mod_1, low_step=eos_mod_2, high_step=eos_mod_3, unit_count=eos_mod_4, is_greater=eos_mod_5)
    step_text = parse_step_transition(step_num=eos_mod_6)    
    time_text = parse_time(eos_mod_7)                        

    return f'{time_text} then {step_text} or {unit_text}.'

def eos_98(eos_mod_1=None,
           eos_mod_2=None,
           eos_mod_3=None,
           eos_mod_4=None,
           eos_mod_5=None,
           eos_mod_6=None,
           eos_mod_7=None,
           eos_mod_8=None):
    process_text1 = parse_process_step_range(process_num=eos_mod_1, low_step=eos_mod_2, high_step=eos_mod_3, unit_count=eos_mod_8, is_greater=eos_mod_4)
    process_text2 = parse_process_step_range(process_num=eos_mod_5, low_step=eos_mod_6, high_step=eos_mod_7, unit_count=eos_mod_8, is_greater=eos_mod_4)

    return f'{process_text1} or {process_text2}.'


def eos_resolve(eos_type, eos_mod_1, eos_mod_2, eos_mod_3, eos_mod_4,
                eos_mod_5, eos_mod_6, eos_mod_7, eos_mod_8):
    global step_branch
    step_branch = namedtuple('branching', ['branch_to', 'keepxfr'])
    step_branch.branch_to = []
    step_branch.keepxfr = False
    
    eos_type = int(eos_type)

    header_text = f'End of step Type {eos_type}: The step ends when'
    # header_text = 'The step ends when'

    eos_function = f'eos_{eos_type}'

    try:
        eos_text = eval(
            f'''{eos_function}({eos_mod_1}, {eos_mod_2}, {eos_mod_3}, {eos_mod_4},
                                            {eos_mod_5}, {eos_mod_6}, {eos_mod_7}, {eos_mod_8})'''
        )

        eos_step_desc_english = ' '.join([header_text, eos_text])
        step_not_found = False
    except NameError:
        eos_step_desc_english = f'End of step type {eos_type}'
        step_not_found = True

    return eos_step_desc_english, step_not_found, step_branch