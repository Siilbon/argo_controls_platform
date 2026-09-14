"""App-specific helpers on top of mfgkit.intellution.

Tag database parsing lives in mfgkit; this module only shapes its output for
the intellution_tags table and the search views.
"""
import pandas as pd

DEFAULT_COLS = [
    'database', 'name', 'tag', 'desc', 'ft_topic', 'ioad', 'source', 'opc_topic',
    'ienab', 'opendesc', 'closedesc', 'elo', 'ehi', 'egudesc', 'pri',
    'sa1', 'sa2', 'sa3', 'all_areas', 'almext1', 'almext2', 'prefix',
    'loop', 'suffix', 'alias_root', 'alias_field', 'alias_rest', 'uploaded'
]


def search_all_intellution_df(term, df_iter, col):
    print(f"Term: {term}, Column: {col}")
    results = pd.DataFrame()
    for df in df_iter:
        result = df.df[df.df[col].str.contains(term, na=False, case=False)]
        results = pd.concat([results, result])

    return results


def clean_intellution_df(df):
    return df[DEFAULT_COLS]
