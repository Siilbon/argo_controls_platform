# Truthtable Parser | Parker Jordan
"""
This Truthtable Parser is intented to translate the operation on a given unit 
from its truthtable. It translates a given unit's steps into a readible format
and provides the conditions of advancing to the next step.

Required Parameters:
    Truthtable's Name
    Desired Sequence
"""

import numpy as np
import pandas as pd
from collections import namedtuple
from acp_app.services.eos_to_english import eos_resolve
from pathlib import Path


class TruthtableDB():

    def __init__(self, path):
        self.path = path
        self._tt_name = Path(self.path).stem
        self._df = self.read_tt_file()

        self._tt_name_lst, self._seq_num_lst, self._seq = self.get_desired_seq(
        )

        self._next_steps = self.get_next_steps()
        self._step_name = self.get_step_name()
        self._eos_english = self.get_eos_english()
        self._true_devices = self.get_true_devices()
        self._false_devices = self.get_false_devices()

        self.tt = self.parse_truthtable()

    # Reads in the truthtable excel file into a DataFrame
    def read_tt_file(self):
        df = pd.read_excel(self.path, sheet_name=1, header=None)
        header = ['Info', 'Tag', 'Address', 'Description']
        header.extend(list(str(step) for step in range(1, 102)))
        df.columns = header
        return df

    # Assigns row numbers to key information stored in the truthtables
    @staticmethod
    def get_tt_rows():
        seqnum = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
        seqrow = (12, 13, 14, 15, 16, 17, 18, 19, 20, 21)

        seqrn = namedtuple('all_seq', ['seqrow', 'seqnum'])
        # Row numbers for the EOS type through EOS Mod 8
        mod = (3, 4, 5, 6, 7, 8, 9, 10, 11)
        step_name_r = 0
        first_device_r = 35
        return mod, seqrn(seqrow, seqnum), step_name_r, first_device_r

    # Parses the given truthtable for the order of steps for the given sequence
    def get_desired_seq(self):
        mod, seqrn, step_name_r, first_device_r = self.get_tt_rows()

        tt_name_lst = []
        seq_num_lst = []
        seq_lst = []

        for seq_r in seqrn.seqrow:
            print(
                f'Extracing sequence {seqrn.seqnum[seqrn.seqrow.index(seq_r)]} from truthtable {self._tt_name}...'
            )
            seq = [1]
            next_sn = -1
            tick = 1
            try:
                while (seq[0] != next_sn):
                    lookup_val = seq[len(seq) - tick]
                    eos_info = list(self._df.loc[self._df.index[list(mod)],
                                                 str(lookup_val)])
                    eos_step_desc_english, step_not_found, branch_steps = eos_resolve(
                        *eos_info)

                    if bool(branch_steps.branch_to
                            ) is True and not branch_steps.keepxfr:
                        tick = len(branch_steps.branch_to)
                        seq.extend(branch_steps.branch_to)
                    elif bool(branch_steps.branch_to
                              ) is True and branch_steps.keepxfr:
                        tick = len(branch_steps.branch_to)
                        seq.extend(branch_steps.branch_to)
                        next_sn = self._df.loc[self._df.index[seq_r],
                                               str(lookup_val)]
                        seq.append(next_sn)
                    else:
                        next_sn = self._df.loc[self._df.index[seq_r],
                                               str(lookup_val)]
                        seq.append(next_sn)

                    if seq[-1] == seq[-2]:
                        tick = 1

                    if len(seq) > 100:
                        break

                seq = list(dict.fromkeys(seq))
                seq.append(1)

                seq_num_lst += [seqrn.seqnum[seqrn.seqrow.index(seq_r)]
                                ] * len(seq)
                seq_lst.extend(seq)

            except KeyError:
                pass

        tt_name_lst += [self._tt_name] * len(seq_lst)
        return tt_name_lst, seq_num_lst, seq_lst

    # Parses the given truthtable to return the subsuquent steps for the given sequence
    def get_next_steps(self):
        mod, seqrn, step_name_r, first_device_r = self.get_tt_rows()
        next_steps = []

        for idx, lookup_val in enumerate(self._seq):

            eos_info = list(self._df.loc[self._df.index[list(mod)],
                                         str(lookup_val)])
            eos_step_desc_english, step_not_found, branch_steps = eos_resolve(
                *eos_info)

            if bool(branch_steps.branch_to) is True:
                branch_text = ' or '.join(
                    str(i) for i in branch_steps.branch_to)
                if branch_steps.keepxfr:
                    xfrstep = self._df.loc[self._df.index[seqrn.seqrow[
                        seqrn.seqnum.index(self._seq_num_lst[idx])]],
                                           str(lookup_val)]
                    branch_text = f'{branch_text} or {xfrstep}'
                next_steps.append(branch_text)
            else:
                next_sn = self._df.loc[self._df.index[seqrn.seqrow[
                    seqrn.seqnum.index(self._seq_num_lst[idx])]],
                                       str(lookup_val)]
                next_steps.append(str(next_sn))
        return next_steps

    # Translates the End of Step condtions for each step in the given sequence
    def get_eos_english(self):
        mod, seqrn, step_name_r, first_device_r = self.get_tt_rows()
        eos_english = []
        for lookup_val in self._seq:
            eos_info = list(self._df.loc[self._df.index[list(mod)],
                                         str(lookup_val)])
            step_english, step_not_found, branch_steps = eos_resolve(*eos_info)
            eos_english.append(step_english)
        return eos_english

    # Parses the given truthtable to return the name of each step in the given sequence
    def get_step_name(self):
        mod, seqrn, step_name_r, first_device_r = self.get_tt_rows()
        step_name = []
        for i in self._seq:
            sn_names = self._df.loc[self._df.index[step_name_r], str(i)]
            step_name.append(sn_names)
        return step_name

    # Parses the given truthtable to return all devices the are in the On/True state
    # for each step in the given sequence
    def get_true_devices(self):
        mod, seqrn, step_name_r, first_device_r = self.get_tt_rows()
        true_devices = []
        dvdf = self._df.drop(range(0, first_device_r), axis=0)
        for i in self._seq:
            rawdev = list(dvdf.loc[dvdf[str(i)] == 1].Tag)
            devtags = [str(i) for i in rawdev]
            devtags = [item.strip() for item in devtags]
            devtags = list(filter(None, devtags))

            # need a list of strings
            true_devices.append(str(devtags))

        return true_devices

    # Parses the given truthtable to return all devices the are in the Off/False state
    # for each step in the given sequence
    def get_false_devices(self):
        mod, seqrn, step_name_r, first_device_r = self.get_tt_rows()
        false_devices = []
        dvdf = self._df.drop(range(0, first_device_r), axis=0)
        for i in self._seq:
            rawdev = list(dvdf.loc[dvdf[str(i)] == 0].Tag)
            devtags = [str(i) for i in rawdev]
            devtags = [item.strip() for item in devtags]
            devtags = list(filter(None, devtags))
            false_devices.append(devtags)
        return false_devices

    #
    def parse_truthtable(self):
        parsed_tt = pd.DataFrame(list(
            zip(self._tt_name_lst, self._seq_num_lst, self._seq,
                self._step_name, self._eos_english, self._next_steps,
                self._true_devices)),
                                 columns=[
                                     'name', 'seq', 'step_num', 'step_name',
                                     'eos_cond', 'next_step', 'true_dev'
                                 ])
        return parsed_tt
