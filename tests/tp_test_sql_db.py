# Truthtable Parser Test File | Karl Siil
# Troubleshooting the sql database for the parser

#%%
import os
import pandas as pd
from sqlalchemy import select

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')




#%%
df = pd.read_sql('''SELECT * FROM tt_master where name == "41IX1X" and seq == 4''', SQLALCHEMY_DATABASE_URI)

df.head()

#%%

# tt_query = (select([Truthtables
#                     ]).where(
#                         Truthtables.seq == 2))

# tt_table = pd.read_sql(tt_query, db.engine)
# %%


# %%
print(df.head())