from acp_app.services.eos_to_english import *

# Tests for common utilities


def test_is_set():
    assert is_set(1, 0) == True
    assert is_set(2, 0) == False
    assert is_set(3, 0) == True
    assert is_set(3, 1) == True
    assert is_set(3, 2) == False
    assert is_set(64, 6) == True
    assert is_set(64, 6) == True


def test_parse_discrete_io():
    io = parse_discrete_io(word_num=145,
                           bit_num=1,
                           state_num=0)
    assert io.address == 'rack 14 mod 5 bit 1 (Real_Inputs[145].1)'
    assert io.state == False

    io = parse_discrete_io(word_num=135,
                           bit_num=3,
                           state_num=1)
    assert io.address == 'rack 13 mod 5 bit 3 (Real_Inputs[135].3)'
    assert io.state == True

    io = parse_discrete_io(word_num=10,
                           bit_num=3,
                           state_num=2)
    assert io.address == 'Binary_EOS[10].3'
    assert io.state == False

    io = parse_discrete_io(word_num=110,
                           bit_num=3,
                           state_num=3)
    assert io.address == 'Binary_EOS[110].3'
    assert io.state == True


def test_parse_analog():
    assert parse_analog(analog_num=678,
                        greater_than=1,
                        analog_preset=34) == 'Analog_Variables[678] is greater than or equal to 34'

    assert parse_analog(analog_num=92,
                        greater_than=0,
                        analog_preset=1000) == 'Analog_Variables[92] is less than or equal to 1000'


def test_parse_time():
    assert parse_time(
        time_preset=135) == 'the time in step exceeds 2.25 minutes (135 seconds)'

    assert parse_time(
        time_preset=60) == 'the time in step exceeds 1.00 minutes (60 seconds)'

    assert parse_time(
        time_preset=3600) == 'the time in step exceeds 1.00 hours (60.00 minutes)'


def test_parse_process_step_range():
    process = 30
    step1 = 21
    step2 = 29

    assert parse_process_step_range(process_num=process,
                                    low_step=step1,
                                    high_step=step2,
                                    in_range=True) == 'any unit of process 30 is between steps 21 and 29'
    assert parse_process_step_range(process_num=process,
                                    low_step=step1,
                                    high_step=step2,
                                    in_range=False) == 'any unit of process 30 is not between steps 21 and 29'


def test_parse_process_either_step():
    process = 30
    step1 = 21
    step2 = 29
    assert parse_process_either_step(process_num=process,
                                     step_num1=step1,
                                     step_num2=step2,
                                     in_step=True) == 'any unit of process 30 is in steps 21 or 29'
    assert parse_process_either_step(process_num=process,
                                     step_num1=step1,
                                     step_num2=step2,
                                     in_step=False) == 'any unit of process 30 is not in steps 21 or 29'

    process = 30
    step1 = 21
    step2 = 21
    assert parse_process_either_step(process_num=process,
                                     step_num1=step1,
                                     step_num2=step2,
                                     in_step=True) == 'any unit of process 30 is in step 21'
    assert parse_process_either_step(process_num=process,
                                     step_num1=step1,
                                     step_num2=step2,
                                     in_step=False) == 'any unit of process 30 is not in step 21'

    process = 30
    step1 = 29
    assert parse_process_either_step(process_num=process,
                                     step_num1=step1,
                                     in_step=True) == 'any unit of process 30 is in step 29'
    assert parse_process_either_step(process_num=process,
                                     step_num1=step1,
                                     in_step=False) == 'any unit of process 30 is not in step 29'


def test_parse_process_both_steps():
    process = 30
    step1 = 21
    step2 = 29

    assert parse_process_both_steps(process_num=process,
                                    step_num1=step1,
                                    step_num2=step2,
                                    in_step=True) == 'any two units of process 30 are in steps 21 and 29'
    assert parse_process_both_steps(process_num=process,
                                    step_num1=step1,
                                    step_num2=step2,
                                    in_step=False) == 'any two units of process 30 are not in steps 21 and 29'


def test_parse_unit_step_range():
    unit = 30
    step1 = 21
    step2 = 29

    assert parse_unit_step_range(unit_num=unit,
                                 low_step=step1,
                                 high_step=step2,
                                 in_range=True) == 'unit 30 is between steps 21 and 29'
    assert parse_unit_step_range(unit_num=unit,
                                 low_step=step1,
                                 high_step=step2,
                                 in_range=False) == 'unit 30 is not between steps 21 and 29'


def test_parse_unit_either_step():
    unit = 30
    step1 = 21
    step2 = 29
    assert parse_unit_either_step(unit_num=unit,
                                  step_num1=step1,
                                  step_num2=step2,
                                  in_step=True) == 'unit 30 is in steps 21 or 29'
    assert parse_unit_either_step(unit_num=unit,
                                  step_num1=step1,
                                  step_num2=step2,
                                  in_step=False) == 'unit 30 is not in steps 21 or 29'

    unit = 30
    step1 = 21
    step2 = 21
    assert parse_unit_either_step(unit_num=unit,
                                  step_num1=step1,
                                  step_num2=step2,
                                  in_step=True) == 'unit 30 is in step 21'
    assert parse_unit_either_step(unit_num=unit,
                                  step_num1=step1,
                                  step_num2=step2,
                                  in_step=False) == 'unit 30 is not in step 21'

    unit = 30
    step1 = 29
    assert parse_unit_either_step(unit_num=unit,
                                  step_num1=step1,
                                  in_step=True) == 'unit 30 is in step 29'
    assert parse_unit_either_step(unit_num=unit,
                                  step_num1=step1,
                                  in_step=False) == 'unit 30 is not in step 29'


def test_parse_unit_seq_range():
    unit = 30
    seq1 = 21
    seq2 = 29

    assert parse_unit_seq_range(unit_num=unit,
                                 low_seq=seq1,
                                 high_seq=seq2,
                                 in_range=True) == 'unit 30 is between sequence 21 and 29'
    assert parse_unit_seq_range(unit_num=unit,
                                 low_seq=seq1,
                                 high_seq=seq2,
                                 in_range=False) == 'unit 30 is not between sequence 21 and 29'


def test_parse_unit_either_step():
    unit = 30
    step1 = 21
    step2 = 29
    assert parse_unit_either_step(unit_num=unit,
                                  step_num1=step1,
                                  step_num2=step2,
                                  in_step=True) == 'unit 30 is in steps 21 or 29'
    assert parse_unit_either_step(unit_num=unit,
                                  step_num1=step1,
                                  step_num2=step2,
                                  in_step=False) == 'unit 30 is not in steps 21 or 29'

    unit = 30
    step1 = 21
    step2 = 21
    assert parse_unit_either_step(unit_num=unit,
                                  step_num1=step1,
                                  step_num2=step2,
                                  in_step=True) == 'unit 30 is in step 21'
    assert parse_unit_either_step(unit_num=unit,
                                  step_num1=step1,
                                  step_num2=step2,
                                  in_step=False) == 'unit 30 is not in step 21'

    unit = 30
    step1 = 29
    assert parse_unit_either_step(unit_num=unit,
                                  step_num1=step1,
                                  in_step=True) == 'unit 30 is in step 29'
    assert parse_unit_either_step(unit_num=unit,
                                  step_num1=step1,
                                  in_step=False) == 'unit 30 is not in step 29'


def test_parse_step_transition():
    assert parse_step_transition(55) == 'transfer to step 55'


def test_extract_steps():
    steps = extract_steps(1055)
    assert (steps.first == 10) & (steps.second == 55)

    steps = extract_steps(1750)
    assert (steps.first == 17) & (steps.second == 50)

    steps = extract_steps(50)
    assert (steps.first == 0) & (steps.second == 50)

    steps = extract_steps(610)
    assert (steps.first == 6) & (steps.second == 10)

    steps = extract_steps(1)
    assert (steps.first == 0) & (steps.second == 1)


# All end of steps (eos) will be prefixed by 'Step # ends when '


def test_eos_0():
    assert eos_0() == 'an operator advances out of the step manually.'


def test_eos_1():
    assert eos_1(eos_mod_1=145,
                 eos_mod_2=1,
                 eos_mod_3=0) == 'rack 14 mod 5 bit 1 (Real_Inputs[145].1) is False.'

    assert eos_1(eos_mod_1=135,
                 eos_mod_2=3,
                 eos_mod_3=1) == 'rack 13 mod 5 bit 3 (Real_Inputs[135].3) is True.'

    assert eos_1(eos_mod_1=10,
                 eos_mod_2=3,
                 eos_mod_3=2) == 'Binary_EOS[10].3 is False.'

    assert eos_1(eos_mod_1=110,
                 eos_mod_2=3,
                 eos_mod_3=3) == 'Binary_EOS[110].3 is True.'


def test_eos_2():
    assert eos_2(eos_mod_1=123,
                 eos_mod_8=553) == 'Analog_Variables[123] is greater than 553.'


def test_eos_3():
    assert eos_3(eos_mod_1=123,
                 eos_mod_8=553) == 'Analog_Variables[123] is less than 553.'


def test_eos_4():
    assert eos_4(
        eos_mod_7=135) == 'the time in step exceeds 2.25 minutes (135 seconds).'


def test_eos_5():
    assert eos_5(eos_mod_1=12,
                 eos_mod_2=35,
                 eos_mod_3=50) == 'unit 12 is between steps 35 and 50.'


def test_eos_6():
    assert eos_6(eos_mod_1=14,
                 eos_mod_2=36,
                 eos_mod_3=51) == 'unit 14 is not between steps 36 and 51.'


def test_eos_11():
    assert eos_11() == 'the first scan is over, it\'s always true.'


def test_eos_20():
    assert eos_20(eos_mod_1=14,
                  eos_mod_2=36,
                  eos_mod_3=51) == 'any unit of process 14 is in steps 36 or 51.'


def test_eos_21():
    assert eos_21(eos_mod_1=234,
                  eos_mod_2=2,
                  eos_mod_3=0,
                  eos_mod_4=23,
                  eos_mod_5=2524,
                  eos_mod_6=2726,
                  eos_mod_7=135) == 'the time in step exceeds 2.25 minutes (135 seconds). If rack 23 mod 4 bit 2 (Real_Inputs[234].2) is False then the GCC continues. If True then in sequence 1 transfer to step 23, in sequence 2 transfer to step 24, in sequence 3 transfer to step 25, in sequence 4 transfer to step 26, in sequence 5 transfer to step 27.'


def test_eos_22():
    assert eos_22(eos_mod_1=123,
                  eos_mod_2=11,
                  eos_mod_3=13,
                  eos_mod_4=234,
                  eos_mod_5=2,
                  eos_mod_6=0,
                  eos_mod_7=135
                  ) == 'rack 23 mod 4 bit 2 (Real_Inputs[234].2) is False after the time in step exceeds 2.25 minutes (135 seconds) or when any unit of process 123 is in steps 11 or 13.'

    assert eos_22(eos_mod_1=123,
                  eos_mod_2=11,
                  eos_mod_3=13,
                  eos_mod_4=234,
                  eos_mod_5=2,
                  eos_mod_6=1,
                  eos_mod_7=135
                  ) == 'rack 23 mod 4 bit 2 (Real_Inputs[234].2) is True after the time in step exceeds 2.25 minutes (135 seconds) or when any unit of process 123 is in steps 11 or 13.'

    assert eos_22(eos_mod_1=123,
                  eos_mod_2=11,
                  eos_mod_3=13,
                  eos_mod_4=234,
                  eos_mod_5=2,
                  eos_mod_6=2,
                  eos_mod_7=135
                  ) == 'Binary_EOS[234].2 is False after the time in step exceeds 2.25 minutes (135 seconds) or when any unit of process 123 is in steps 11 or 13.'

    assert eos_22(eos_mod_1=123,
                  eos_mod_2=11,
                  eos_mod_3=13,
                  eos_mod_4=234,
                  eos_mod_5=2,
                  eos_mod_6=3,
                  eos_mod_7=135
                  ) == 'Binary_EOS[234].2 is True after the time in step exceeds 2.25 minutes (135 seconds) or when any unit of process 123 is in steps 11 or 13.'


def test_eos_23():
    assert eos_23(eos_mod_1=30,
                  eos_mod_2=21,
                  eos_mod_3=29
                  ) == 'any two units of process 30 are in steps 21 and 29.'


def test_eos_25():
    assert eos_25(eos_mod_1=234,
                  eos_mod_2=2,
                  eos_mod_3=3,
                  eos_mod_4=123,
                  eos_mod_5=11,
                  eos_mod_6=13,
                  eos_mod_7=135,
                  eos_mod_8=145
                  ) == 'Binary_EOS[234].2 is True transfer to step 11, or if the time in step exceeds 2.25 minutes (135 seconds) and Analog_Variables[123] is less than or equal to 145 transfer to step 13.'

    assert eos_25(eos_mod_1=234,
                  eos_mod_2=2,
                  eos_mod_3=7,
                  eos_mod_4=123,
                  eos_mod_5=11,
                  eos_mod_6=13,
                  eos_mod_7=135,
                  eos_mod_8=145
                  ) == 'Binary_EOS[234].2 is True transfer to step 11, or if the time in step exceeds 2.25 minutes (135 seconds) and Analog_Variables[123] is greater than or equal to 145 transfer to step 13.'


def test_eos_26():
    assert eos_26(eos_mod_1=234,
                  eos_mod_2=2,
                  eos_mod_3=3,
                  eos_mod_4=123,
                  eos_mod_5=11,
                  eos_mod_6=13,
                  eos_mod_7=135,
                  eos_mod_8=145
                  ) == 'Binary_EOS[234].2 is True transfer to step 11, or if the time in step exceeds 2.25 minutes (135 seconds) and Analog_Variables[123] is less than or equal to 145 the GCC continues.'

    assert eos_26(eos_mod_1=234,
                  eos_mod_2=2,
                  eos_mod_3=7,
                  eos_mod_4=123,
                  eos_mod_5=11,
                  eos_mod_7=135,
                  eos_mod_8=145
                  ) == 'Binary_EOS[234].2 is True transfer to step 11, or if the time in step exceeds 2.25 minutes (135 seconds) and Analog_Variables[123] is greater than or equal to 145 the GCC continues.'


def test_eos_27():
    assert eos_27(eos_mod_1=174,
                  eos_mod_2=0,
                  eos_mod_4=234,
                  eos_mod_5=2,
                  eos_mod_6=0,
                  eos_mod_8=135
                  ) == 'Analog_Variables[174] is less than or equal to 135 or rack 23 mod 4 bit 2 (Real_Inputs[234].2) is False.'

    assert eos_27(eos_mod_1=174,
                  eos_mod_2=1,
                  eos_mod_4=234,
                  eos_mod_5=2,
                  eos_mod_6=0,
                  eos_mod_8=135
                  ) == 'Analog_Variables[174] is greater than or equal to 135 or rack 23 mod 4 bit 2 (Real_Inputs[234].2) is False.'

    assert eos_27(eos_mod_1=174,
                  eos_mod_2=1,
                  eos_mod_4=234,
                  eos_mod_5=2,
                  eos_mod_6=2,
                  eos_mod_8=135
                  ) == 'Analog_Variables[174] is greater than or equal to 135 or Binary_EOS[234].2 is False.'


def test_eos_28():
    assert eos_28(eos_mod_1=174,
                  eos_mod_2=1,
                  eos_mod_4=234,
                  eos_mod_5=2,
                  eos_mod_6=2,
                  eos_mod_8=135
                  ) == 'Analog_Variables[174] is greater than or equal to 135 and Binary_EOS[234].2 is False.'


def test_eos_29():
    assert eos_29(eos_mod_1=174,
                  eos_mod_2=1,
                  eos_mod_3=1,
                  eos_mod_4=34,
                  eos_mod_5=10,
                  eos_mod_6=20,
                  eos_mod_7=135,
                  eos_mod_8=145
                  ) == 'Analog_Variables[174] is greater than or equal to 145 and the time in step exceeds 2.25 minutes (135 seconds), or any unit of process 34 is in steps 10 or 20.'

    assert eos_29(eos_mod_1=174,
                  eos_mod_2=1,
                  eos_mod_3=0,
                  eos_mod_4=34,
                  eos_mod_5=10,
                  eos_mod_6=20,
                  eos_mod_7=135,
                  eos_mod_8=145
                  ) == 'Analog_Variables[174] is greater than or equal to 145 and the time in step exceeds 2.25 minutes (135 seconds), or any unit of process 34 is not in steps 10 or 20.'


def test_eos_30():
    assert eos_30(eos_mod_1=174,
                  eos_mod_2=0,
                  eos_mod_7=135,
                  eos_mod_8=1110
                  ) == 'Analog_Variables[174] is less than or equal to 1110 and the time in step exceeds 2.25 minutes (135 seconds).'


def test_eos_31():
    assert eos_31(eos_mod_1=174,
                  eos_mod_2=0,
                  eos_mod_7=135,
                  eos_mod_8=1110
                  ) == 'Analog_Variables[174] is less than or equal to 1110 or the time in step exceeds 2.25 minutes (135 seconds).'


def test_eos_32():
    assert eos_32(eos_mod_1=14,
                  eos_mod_7=195
                  ) == 'the time in step exceeds 3.25 minutes (195 seconds) transfer to step 14.'


def test_eos_33():
    assert eos_33(eos_mod_1=14,
                  eos_mod_2=21,
                  eos_mod_3=22,
                  eos_mod_4=123,
                  eos_mod_5=0,
                  eos_mod_8=195
                  ) == 'any unit of process 14 is not in steps 21 or 22 and Analog_Variables[123] is greater than 195.'

    assert eos_33(eos_mod_1=14,
                  eos_mod_2=21,
                  eos_mod_3=22,
                  eos_mod_4=123,
                  eos_mod_5=1,
                  eos_mod_8=195
                  ) == 'any unit of process 14 is in steps 21 or 22 and Analog_Variables[123] is greater than 195.'


def test_eos_34():
    assert eos_34(eos_mod_1=14,
                  eos_mod_2=21,
                  eos_mod_3=22,
                  eos_mod_4=123,
                  eos_mod_5=0,
                  eos_mod_8=195
                  ) == 'any unit of process 14 is not in steps 21 or 22 or Analog_Variables[123] is greater than 195.'

    assert eos_34(eos_mod_1=14,
                  eos_mod_2=21,
                  eos_mod_3=22,
                  eos_mod_4=123,
                  eos_mod_5=1,
                  eos_mod_8=195
                  ) == 'any unit of process 14 is in steps 21 or 22 or Analog_Variables[123] is greater than 195.'


def test_eos_35():
    assert eos_35(eos_mod_1=174,
                  eos_mod_2=1,
                  eos_mod_3=0,
                  eos_mod_4=34,
                  eos_mod_5=10,
                  eos_mod_6=20,
                  eos_mod_7=135,
                  eos_mod_8=145
                  ) == 'unit 174 is in step 1 then transfer to step 10, if the time in step exceeds 2.25 minutes (135 seconds) then transfer to step 20.'

    assert eos_35(eos_mod_1=174,
                  eos_mod_2=1,
                  eos_mod_3=1,
                  eos_mod_4=34,
                  eos_mod_5=10,
                  eos_mod_6=20,
                  eos_mod_7=135,
                  eos_mod_8=145
                  ) == 'unit 174 is in step 1 then transfer to step 10, if Analog_Variables[34] is less than or equal to 145 then transfer to step 20.'

    assert eos_35(eos_mod_1=174,
                  eos_mod_2=1,
                  eos_mod_3=2,
                  eos_mod_4=34,
                  eos_mod_5=10,
                  eos_mod_6=20,
                  eos_mod_7=135,
                  eos_mod_8=145
                  ) == 'unit 174 is in step 1 then transfer to step 10, if the time in step exceeds 2.25 minutes (135 seconds) then transfer to step 20.'

    assert eos_35(eos_mod_1=174,
                  eos_mod_2=1,
                  eos_mod_3=3,
                  eos_mod_4=34,
                  eos_mod_5=10,
                  eos_mod_6=20,
                  eos_mod_7=135,
                  eos_mod_8=145
                  ) == 'unit 174 is in step 1 then transfer to step 10, if Analog_Variables[34] is greater than or equal to 145 then transfer to step 20.'


def test_eos_36():
    assert eos_36(eos_mod_1=174,
                  eos_mod_2=7,
                  eos_mod_3=0,
                  eos_mod_5=31,
                  eos_mod_6=32,
                  eos_mod_7=135
                  ) == 'rack 17 mod 4 bit 7 (Real_Inputs[174].7) is False then transfer to step 31, if the time in step exceeds 2.25 minutes (135 seconds) then transfer to step 32.'


def test_eos_37():
    assert eos_37(eos_mod_1=266,
                  eos_mod_2=16,
                  eos_mod_3=0,
                  eos_mod_4=322,
                  eos_mod_5=13,
                  eos_mod_6=2,
                  eos_mod_7=3660
                  ) == 'rack 26 mod 6 bit 16 (Real_Inputs[266].16) is False or the time in step exceeds 1.02 hours (61.00 minutes), and Binary_EOS[322].13 is False.'


def test_eos_38():
    assert eos_38(eos_mod_1=10,
                  eos_mod_2=21,
                  eos_mod_3=0,
                  eos_mod_4=11,
                  eos_mod_5=31,
                  eos_mod_6=1,
                  eos_mod_7=22,
                  eos_mod_8=32
                  ) == 'unit 10 is in step 21 then transfer to step 22, if unit 11 is not in step 31 then transfer to step 32.'


def test_eos_39():
    assert eos_39(eos_mod_1=174,
                  eos_mod_2=7,
                  eos_mod_3=0,
                  eos_mod_7=135,
                  eos_mod_8=4000
                  ) == 'rack 17 mod 4 bit 7 (Real_Inputs[174].7) is False and the time in step exceeds 2.25 minutes (135 seconds), or when the time in step exceeds 1.11 hours (66.67 minutes).'


def test_eos_41():
    assert eos_41(eos_mod_1=10,
                  eos_mod_2=21,
                  eos_mod_3=23,
                  eos_mod_4=11,
                  eos_mod_5=31,
                  eos_mod_6=40,
                  eos_mod_7=1
                  ) == 'any unit of process 10 is in steps 21 or 23 and any unit of process 11 is between steps 31 and 40.'


def test_eos_42():
    assert eos_42(eos_mod_1=10,
                  eos_mod_2=21,
                  eos_mod_3=23,
                  eos_mod_4=11,
                  eos_mod_5=31,
                  eos_mod_6=40,
                  eos_mod_7=0
                  ) == 'any unit of process 10 is in steps 21 or 23 or any unit of process 11 is not between steps 31 and 40.'


def test_eos_43():
    assert eos_43(eos_mod_1=10,
                  eos_mod_2=21,
                  eos_mod_3=23,
                  eos_mod_4=1,
                  eos_mod_7=135
                  ) == 'any unit of process 10 is in steps 21 or 23 and the time in step exceeds 2.25 minutes (135 seconds).'


def test_eos_44():
    assert eos_44(eos_mod_1=123,
                  eos_mod_2=10,
                  eos_mod_3=3,
                  eos_mod_4=132,
                  eos_mod_5=7,
                  eos_mod_6=2,
                  eos_mod_7=135,
                  eos_mod_8=12
                  ) == 'Binary_EOS[123].10 is True and Binary_EOS[132].7 is False then the GCC continues, or if the time in step exceeds 2.25 minutes (135 seconds) then transfer to step 12.'


def test_eos_45():
    assert eos_45(eos_mod_1=174,
                  eos_mod_2=7,
                  eos_mod_3=0,
                  eos_mod_4=12,
                  eos_mod_7=135
                  ) == 'the time in step exceeds 2.25 minutes (135 seconds) then the GCC continues, or if rack 17 mod 4 bit 7 (Real_Inputs[174].7) is False then transfer to step 12.'


def test_eos_46():
    assert eos_46(eos_mod_1=123,
                  eos_mod_2=0,
                  eos_mod_3=3,
                  eos_mod_4=132,
                  eos_mod_5=7,
                  eos_mod_6=2,
                  eos_mod_7=135,
                  eos_mod_8=12
                  ) == 'Analog_Variables[123] is less than or equal to 135 then the GCC continues, or if Analog_Variables[3] is less than or equal to 12 or rack 13 mod 2 bit 7 (Real_Inputs[132].7) is False then transfer to step 2.'

    assert eos_46(eos_mod_1=123,
                  eos_mod_2=1,
                  eos_mod_3=3,
                  eos_mod_4=132,
                  eos_mod_5=7,
                  eos_mod_6=2,
                  eos_mod_7=135,
                  eos_mod_8=12
                  ) == 'Analog_Variables[123] is greater than or equal to 135 then the GCC continues, or if Analog_Variables[3] is less than or equal to 12 or rack 13 mod 2 bit 7 (Real_Inputs[132].7) is False then transfer to step 2.'

    assert eos_46(eos_mod_1=123,
                  eos_mod_2=2,
                  eos_mod_3=3,
                  eos_mod_4=132,
                  eos_mod_5=7,
                  eos_mod_6=2,
                  eos_mod_7=135,
                  eos_mod_8=12
                  ) == 'Analog_Variables[123] is less than or equal to 135 then the GCC continues, or if Analog_Variables[3] is greater than or equal to 12 or rack 13 mod 2 bit 7 (Real_Inputs[132].7) is False then transfer to step 2.'

    assert eos_46(eos_mod_1=123,
                  eos_mod_2=15,
                  eos_mod_3=3,
                  eos_mod_4=132,
                  eos_mod_5=7,
                  eos_mod_6=2,
                  eos_mod_7=135,
                  eos_mod_8=12
                  ) == 'Analog_Variables[123] is greater than or equal to 135 then the GCC continues, or if Analog_Variables[3] is greater than or equal to 12 or Binary_EOS[132].7 is True then transfer to step 2.'


def test_eos_47():
    assert eos_47(eos_mod_1=123,
                  eos_mod_2=15,
                  eos_mod_3=20,
                  eos_mod_4=132,
                  eos_mod_5=7,
                  eos_mod_6=20,
                  eos_mod_7=0,
                  eos_mod_8=12
                  ) == 'unit 123 is not between steps 15 and 20 then the GCC continues, or if unit 132 is not between steps 7 and 20 then transfer to step 12.'

    assert eos_47(eos_mod_1=123,
                  eos_mod_2=15,
                  eos_mod_3=20,
                  eos_mod_4=132,
                  eos_mod_5=7,
                  eos_mod_6=20,
                  eos_mod_7=1,
                  eos_mod_8=12
                  ) == 'unit 123 is between steps 15 and 20 then the GCC continues, or if unit 132 is not between steps 7 and 20 then transfer to step 12.'

    assert eos_47(eos_mod_1=123,
                  eos_mod_2=15,
                  eos_mod_3=20,
                  eos_mod_4=132,
                  eos_mod_5=7,
                  eos_mod_6=20,
                  eos_mod_7=2,
                  eos_mod_8=12
                  ) == 'unit 123 is not between steps 15 and 20 then the GCC continues, or if unit 132 is between steps 7 and 20 then transfer to step 12.'

    assert eos_47(eos_mod_1=123,
                  eos_mod_2=15,
                  eos_mod_3=20,
                  eos_mod_4=132,
                  eos_mod_5=7,
                  eos_mod_6=20,
                  eos_mod_7=3,
                  eos_mod_8=12
                  ) == 'unit 123 is between steps 15 and 20 then the GCC continues, or if unit 132 is between steps 7 and 20 then transfer to step 12.'


def test_eos_48():
    assert eos_48(eos_mod_1=123,
                  eos_mod_2=15,
                  eos_mod_3=1,
                  eos_mod_4=2,
                  eos_mod_5=6,
                  eos_mod_6=3,
                  eos_mod_7=20
                  ) == 'current unit is between sequence 2 and 6 and rack 12 mod 3 bit 15 (Real_Inputs[123].15) is True and the time in step exceeds 0.33 minutes (20 seconds) then transfer to step 3, or if the time in step exceeds 0.33 minutes (20 seconds) then the GCC continues.'


def test_eos_73():
    assert eos_73(eos_mod_1=342,
                  eos_mod_2=5,
                  eos_mod_3=0,
                  eos_mod_7=135
                  ) == 'the time in step exceeds 2.25 minutes (135 seconds) and rack 34 mod 2 bit 5 (Real_Inputs[342].5) is False.'


def test_eos_74():
    assert eos_74(eos_mod_1=342,
                  eos_mod_2=5,
                  eos_mod_3=0,
                  eos_mod_7=135
                  ) == 'the time in step exceeds 2.25 minutes (135 seconds) or rack 34 mod 2 bit 5 (Real_Inputs[342].5) is False.'


def test_eos_75():
    assert eos_75(eos_mod_1=134,
                  eos_mod_2=0,
                  eos_mod_3=49,
                  eos_mod_4=167,
                  eos_mod_5=1,
                  eos_mod_6=30,
                  eos_mod_7=100,
                  eos_mod_8=189
                  ) == 'Analog_Variables[134] is less than or equal to 100 then transfer to step 49 or if Analog_Variables[167] is greater than or equal to 189 then transfer to step 30.'


def test_eos_77():
    assert eos_77(eos_mod_1=34,
                  eos_mod_2=10,
                  eos_mod_3=20
                  ) == 'any unit of process 34 is between steps 10 and 20.'


def test_eos_80():
    assert eos_80(eos_mod_1=266,
                  eos_mod_2=16,
                  eos_mod_3=0,
                  eos_mod_4=322,
                  eos_mod_5=13,
                  eos_mod_6=2
                  ) == 'rack 26 mod 6 bit 16 (Real_Inputs[266].16) is False and Binary_EOS[322].13 is False.'


def test_eos_83():
    assert eos_83(eos_mod_1=266,
                  eos_mod_2=16,
                  eos_mod_3=0,
                  eos_mod_4=322,
                  eos_mod_5=13,
                  eos_mod_6=2,
                  eos_mod_7=3660
                  ) == 'rack 26 mod 6 bit 16 (Real_Inputs[266].16) is False or Binary_EOS[322].13 is False or the time in step exceeds 1.02 hours (61.00 minutes).'


def test_eos_85():
    assert eos_85(eos_mod_1=266,
                  eos_mod_2=16,
                  eos_mod_3=0,
                  eos_mod_4=322,
                  eos_mod_5=13,
                  eos_mod_6=2,
                  eos_mod_7=37,
                  eos_mod_8=56
                  ) == 'rack 26 mod 6 bit 16 (Real_Inputs[266].16) is False then transfer to step 37 or if Binary_EOS[322].13 is False then transfer to step 56.'
