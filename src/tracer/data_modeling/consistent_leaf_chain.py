
import pandas as pd
import numpy as np

def p_min_vector(delta, c):
    """
    Compute p_min(n) for every n = 0, 1, ..., m, given:
        delta : sequence of delta_0, ..., delta_m  (length m+1)
        c     : sequence of c_1, ..., c_m           (length m)

    Returns:
        list of p_min values, where result[n] = p_min for that n
        (so result[0] = p_min(0), result[1] = p_min(1), ..., result[m] = p_min(m))
    """
    m = len(delta) - 1
    if len(c) != m:
        raise ValueError(f"c must have length m = {m} (delta has length m+1={m+1}), got {len(c)}")

    S = delta[0]   # numerator at n=0
    D = 1          # denominator at n=0
    results = [-S / D]  # p_min(0)

    for n in range(1, m + 1):
        S = delta[n] + c[n - 1] * S   # c[n-1] is c_n
        D = c[n - 1] * D
        results.append(- S / D)

    return results


def consumption_vector(delta, c, P):
    """
    Compute consumption(n) for every n = 0, 1, ..., m, given:
        delta : sequence of delta_0, ..., delta_m  (length m+1)
        c     : sequence of c_1, ..., c_m           (length m)
        P     : free parameter (scalar)

    consumption(n) = delta_n + sum_{i=0}^{n-1} delta_i * prod_{j=i+1}^{n} c_j
                      + P * prod_{j=1}^{n} c_j

    Returns:
        list of consumption values, where result[n] = consumption at level n
    """
    m = len(delta) - 1
    if len(c) != m:
        raise ValueError(f"c must have length m = {m} (delta has length m+1={m+1}), got {len(c)}")

    S = delta[0]   # numerator at n=0
    D = 1          # denominator/product at n=0
    results = [S + P * D]  # consumption(0)

    for n in range(1, m + 1):
        S = delta[n] + c[n - 1] * S   # c[n-1] is c_n
        D = c[n - 1] * D
        results.append(S + P * D)

    return results

def c_from_imports(imports):
    """
    Compute c_1, ..., c_m from a sequence of total imports across tiers,
    ordered from the most upstream (n=0) to most downstream (n=m):

        c_j = imports_j / imports_{j-1},   for j = 1, ..., m

    Parameters:
        imports : sequence of import totals, length m+1,
                  imports[0] = imports at tier 0 (most upstream),
                  imports[m] = imports at tier m (most downstream)

    Returns:
        list of c_1, ..., c_m  (length m)
    """
    m = len(imports) - 1
    c = []
    for j in range(1, m + 1):
        c.append(imports[j] / imports[j - 1])
    return c

def calculate_min_domestic_shares(domestic_share_data, hs_codes):
    """Generate a dataframe of minimum domestic share for each country and hs code combination."""

    hs_codes = hs_codes.copy()
    df = domestic_share_data.copy()
    df = df[df['hs_code'].isin(hs_codes)]
    # Load data
    df = df.drop(['a','b','mu','nu','r'], axis = 1)
    reversed_codes = list(hs_codes)
    df['hs_code'] = pd.Categorical(df['hs_code'], categories=reversed_codes, ordered=True)
    df = df.sort_values('hs_code')

    # Prepare inputs
    country_codes = df.country_code.unique()
    min_domestic_shares=pd.DataFrame()
    imports = df.groupby('hs_code')['imports'].sum().to_frame()
    imports=list(imports['imports'])
    cs = c_from_imports(imports)


    # iterate through each country
    for country_code in country_codes:
        sub_df = df[df['country_code']==country_code].copy()
        if len(sub_df)!= len(hs_codes):
            continue
        deltas = list(sub_df['imports']-sub_df['exports'])
        sub_df['p_min'] = p_min_vector(deltas, cs)
        P_min = max(0,sub_df['p_min'].max())
        sub_df['consumption']=np.maximum(0,consumption_vector(deltas, cs, P_min)) # Fixing P to P_min
        sub_df['production'] = np.maximum(0,sub_df['exports']-sub_df['imports']+sub_df['consumption'])
        sub_df['export ratio'] = sub_df['exports']/(sub_df['exports']+sub_df['imports'])
        sub_df['min_domestic_share'] = sub_df['production']/(sub_df['production']+sub_df['imports'])
        sub_df.reset_index(drop =True, inplace=True)

        # extract sub df where an intervention was required
        if P_min > 0:
            sub_df = sub_df.loc[:sub_df.index[sub_df['p_min'] == P_min][0]]
            sub_df = sub_df[['hs_code', 'country_code', 'min_domestic_share']]
            min_domestic_shares = pd.concat([min_domestic_shares, sub_df])

    return min_domestic_shares