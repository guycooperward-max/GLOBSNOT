import pandas as pd
from pathlib import Path

from tracer.data_loading.load import load_domestic_share_data, load_global_net_exports
from tracer.data_modeling.consistent_leaf_chain import calculate_min_domestic_shares

HERE = Path(__file__).parent


if __name__ == "__main__":
    share = load_domestic_share_data(["2601", "7403"])
    share.to_csv(HERE/'output_test_file.csv', index = False)
    hs_codes = ['2601','7403']
    min_shares = calculate_min_domestic_shares(share, hs_codes)
    print(share)
    print(min_shares)
    print("passed")