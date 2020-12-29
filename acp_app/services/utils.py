import re
import pandas as pd


def read_stacked_csv(path, sep, offset, table_name_col, table_name_default,
                     column_parser, encoding, **kwargs):
    """A wrapper for pd.read_csv to read in multiple stacked tables.

    Args:
        path (str): path to .csv file
        sep (str): a string that separates the tables
        offset (int): the number of lines between the table headers
        table_name_col (str): the column to get the table name from
        table_name_default (str): a default name for a table table_name_col
                                  value is NaN
        column_parser (function): a function which cleans the table names
        kwargs: any key word args to send to pd.read_csv

    Returns:
        dict: A dictionary with keys that are the title of the table and
              values that are pd.DataFrame
    """
    tables = {}
    start = None
    with open(path, encoding=encoding) as file:
        for line_number, line in enumerate(file.readlines()):
            if re.search(sep, line) and start is None:
                # find the first table
                start = line_number

            elif re.search(sep, line):
                # calculate the size of the table
                end = line_number
                length = end - start - offset

                # Read in table
                table = pd.read_csv(path,
                                    skiprows=start,
                                    nrows=length,
                                    encoding=encoding,
                                    **kwargs)

                # apply the column_parser
                if column_parser is not None:
                    table.columns = column_parser(table.columns)

                # name the column and store it in the 'tables' dict
                if pd.notna(table[table_name_col][0]):
                    table_name = table[table_name_col][0]
                else:
                    table_name = table_name_default

                tables[table_name] = table
                start = end
    return tables
