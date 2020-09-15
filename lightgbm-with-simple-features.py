# HOME CREDIT DEFAULT RISK COMPETITION

# TODO feature importance bölümünü düzenle

import gc
import time
from contextlib import contextmanager
import warnings
from scripts.helper_functions import get_namespace, i_love_ds
from scripts.pre_processing import application_train_test, bureau_and_balance, previous_applications, pos_cash, \
    installments_payments, credit_card_balance
from scripts.train import kfold_lightgbm

warnings.simplefilter(action='ignore', category=FutureWarning)


@contextmanager
def timer(title):
    t0 = time.time()
    yield
    print("{} - done in {:.0f}s".format(title, time.time() - t0))


def main(debug=False):
    num_rows = 10000 if debug else None

    with timer("Process application train"):
        df = application_train_test(num_rows)
        print("application train & test shape:", df.shape)

    with timer("Process bureau and bureau_balance"):
        bureau = bureau_and_balance(num_rows)
        print("Bureau df shape:", bureau.shape)
        df = df.join(bureau, how='left', on='SK_ID_CURR')
        del bureau
        gc.collect()

    with timer("Process previous_applications"):
        prev = previous_applications(num_rows)
        print("Previous applications df shape:", prev.shape)
        df = df.join(prev, how='left', on='SK_ID_CURR')
        del prev
        gc.collect()

    with timer("Process POS-CASH balance"):
        pos = pos_cash(num_rows)
        print("Pos-cash balance df shape:", pos.shape)
        df = df.join(pos, how='left', on='SK_ID_CURR')
        del pos
        gc.collect()

    with timer("Process installments payments"):
        ins = installments_payments(num_rows)
        print("Installments payments df shape:", ins.shape)
        df = df.join(ins, how='left', on='SK_ID_CURR')
        del ins
        gc.collect()

    with timer("Process credit card balance"):
        cc = credit_card_balance(num_rows)
        print("Credit card balance df shape:", cc.shape)
        df = df.join(cc, how='left', on='SK_ID_CURR')

        # saving final dataframes
        train_df = df[df['TARGET'].notnull()]
        test_df = df[df['TARGET'].isnull()]
        train_df.to_pickle("data/final_train_df.pkl")
        test_df.to_pickle("data/final_test_df.pkl")

        del cc, train_df, test_df
        gc.collect()

    with timer("Run LightGBM with kfold"):
        feat_importance = kfold_lightgbm(df, debug=debug)


if __name__ == "__main__":
    namespace = get_namespace()
    i_love_ds()
    with timer("Full model run"):
        main(debug=namespace.debug)



# kaggle model run: 7879s
# server: 8290s
# mac: 5073s
# google 8: 3189s
# workstation: 1987s
# submission public score: 0.79186
