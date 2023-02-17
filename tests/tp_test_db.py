# Truthtable Parser Test File | Parker Jordan
# Tests all truthtables and sequences for excution and correntness

from acp_app.services.truthtable_parser import TruthtableDB
import numpy as np
import pandas as pd
from pathlib import Path
from colorama import Fore, Back, Style
from colorama import init

def gettruthtabledata():
    all_tts = []
    path = 'C:/Users/pjordan/TruthtablesTest/ref2'

    files = Path(path).glob('**/*.xls')
    for file in files:
        truthtable = TruthtableDB(file)
        all_tts.append(truthtable.tt)
    tt_master = pd.concat(all_tts)
    return tt_master

def getanswerkey():
    dirc = 'C:/Users/pjordan/Truthtables/tp_parser_answers.xlsx'
    seq1 = pd.read_excel(dirc, sheet_name=0)
    seq2 = pd.read_excel(dirc, sheet_name=1)
    seq3 = pd.read_excel(dirc, sheet_name=2)
    seq4 = pd.read_excel(dirc, sheet_name=3)
    seq5 = pd.read_excel(dirc, sheet_name=4)
    key = {
        1 : seq1,
        2 : seq2,
        3 : seq3,
        4 : seq4,
        5 : seq5}
    return key

def compare():

    df = gettruthtabledata()
    answerkey = getanswerkey()
    #truthtables = list(answerkey[1])
    truthtables = ['41IXA', '41IXB', '41IXC', '41IXD', '41IXE', '41IXF']
    #truthtables = ['41IXA']
    seqs = [2, 3, 4, 5]
    right = []
    wrong = []

    for tt in truthtables:
            for i in seqs:
                parsedtt = df.query(f'Truthtable==@tt and `Sequence Number`==@i')
                answer = answerkey[i]

                if np.array_equal(parsedtt['Step Number'], answer[tt].dropna().astype(int)):
                    print(Fore.BLUE + Style.BRIGHT + f'{tt} Sequence {i} is vaild and correct!')
                    right.append(f'{tt} Seq{i}')
                else:
                    print(Fore.RED + Style.BRIGHT + f'{tt} Sequence {i} does not return the correct step numbers')
                    print(answer[tt].dropna().astype(int))
                    print(parsedtt['Step Number'])
                    wrong.append(f'{tt} Seq{i}')
    return right, wrong, parsedtt, answer


#right, wrong, parsedtt, answer = compare()
#print(Style.RESET_ALL)
#print(parsedtt['Step Number'])
#print(answer['41IXA'].dropna().astype(int))

tt_data = gettruthtabledata()

print(tt_data)