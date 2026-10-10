# python imports
from tracer.spark import spark
from tracer.config import HYPERPARAMS_TABLE
import pandas as pd

def load_domestic_share_data(hs_codes):
    hs_codes_str = ", ".join(f"'{code}'" for code in hs_codes)
    query = f"""
        SELECT *
        FROM {HYPERPARAMS_TABLE}
        WHERE hs_code IN ({hs_codes_str})
        AND a IS NOT NULL
    """
    return spark.sql(query).toPandas()

def load_global_net_exports(hs_codes):
    hs_codes_str = ", ".join(f"'{code}'" for code in hs_codes)
    query = f"""
        SELECT * 
        FROM silver_country_hs_code_hyperparamers_2
        WHERE hs_code IN ({hs_codes_str})
        AND a IS NOT NULL
    """
    share = spark.sql(query).toPandas()
    share['net_exports'] = share['exports']-share['imports']
    share = share[share['net_exports']>0]
    share = share[['hs_code', 'country_code', 'country_name', 'exports', 'imports', 'net_exports']]

    global_share = share.groupby(['hs_code']).net_exports.sum().reset_index()
    share = pd.merge(share, global_share, on = 'hs_code', suffixes=('', '_global'))
    share['global_share'] = share['net_exports']/share['net_exports_global']
    return share

def load_import_shares(hs_codes):
    hs_codes_str = ", ".join(f"'{code}'" for code in hs_codes)
    # Pull only the records you need directly from the cluster database
    query = f"""
        SELECT * 
        FROM silver_country_imports 
        WHERE hs_code IN ({hs_codes_str})
    """
    imports = spark.sql(query).toPandas()
    imports = imports[['hs_code', 'country_code', 'source_country_code', 'import_share']]
    return imports