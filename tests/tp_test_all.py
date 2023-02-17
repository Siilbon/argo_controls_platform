# Truthtable Parser Test File | Parker Jordan
# Tests every truthtable and sequence for excution and correntness

from acp_app.services.truthtable_parser import parse_truthtable
import pandas as pd
from colorama import Fore, Back, Style
from colorama import init

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

def evaltts():
    key = getanswerkey()
    #truthtables = list(key[1])
    truthtables = ['41IXA']
    seqs = [2,3,4,5]
    right = []
    wrong = []
    for tt in truthtables:
        for i in seqs:
            parseddf = parse_truthtable(tt=tt, seq_val=i)
            answer = key[i]
            
            if parseddf['Step Number'].equals(answer[tt]) is True:
                print(Fore.BLUE + Style.BRIGHT + f'{tt} Sequence {i} is vaild and correct!')
                right.append(f'{tt} Seq{i}')
            else:
                print(Fore.RED + Style.BRIGHT + f'{tt} Sequence {i} does return the correct step numbers')
                wrong.append(f'{tt} Seq{i}')
    return right, wrong

to_fix = evaltts()[1]