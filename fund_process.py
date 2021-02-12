import time, datetime, os
import numpy as np  #数値計算用
import pandas as pd  #データ処理用
import pandas_datareader
import numba  #最適化ライブラリ

from fund_addition import *



def make_fin_index(df_fin, code):
    #全角の英数字記号を半角に変換するためのテーブル
    trans_table = str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)})

    stock_name = df_fin[df_fin["コード"]==code]["銘柄名"].values[0]
    stock_name = stock_name.translate(trans_table)  #全角の英数字記号を半角に変換
    sector_name = df_fin[df_fin["コード"]==code]["業種"].values[0]
    eps_min = df_fin["EPS"].min()
    delta_eps_min = df_fin["EPS前年比"].min()
    delta_eps_mean = df_fin["EPS前年比"].mean()
    delta_eps_std = df_fin["EPS前年比"].std()
    delta_eps_sharpe = delta_eps_mean/delta_eps_std
    #delta_eps_cv = delta_eps_std/delta_eps_mean  #変動係数
    price_newest = df_fin["Adj Close"].values.tolist()[-1]  #最新のAdj Close
    delta_close_min = df_fin["Adj Close前年比"].min()
    delta_close_mean = df_fin["Adj Close前年比"].mean()
    delta_close_std = df_fin["Adj Close前年比"].std()
    delta_close_sharpe = delta_close_mean/delta_close_std
    #delta_close_cv = delta_close_std/delta_close_mean  #変動係数
    volume_mean = df_fin["Volume"].mean()
    per_newest = df_fin["PER"].values.tolist()[-1]  #最新のPER
    per_min = df_fin["PER"].min()
    delta_per_min = df_fin["PER前年比"].min()
    delta_per_mean = df_fin["PER前年比"].mean()
    delta_per_std = df_fin["PER前年比"].std()
    delta_per_sharpe = delta_per_mean/delta_per_std
    
    #
    payout_time_nume = np.log10(delta_per_mean*(1 +0.01*delta_eps_mean -1) +1)
    #payout_time_nume = np.log10(per_newest*(1 +0.01*delta_eps_mean -1) +1)
    payout_time_deno = np.log10(1 +0.01*delta_eps_mean)
    payout_time = payout_time_nume/payout_time_deno

    df_fin_index = pd.DataFrame()  #1銘柄の指標
    df_fin_index["コード"] = [code]
    df_fin_index["銘柄名"] = [stock_name]
    df_fin_index["業種"] = [sector_name]
    df_fin_index["EPSの最小値"] = [eps_min]
    df_fin_index["⊿EPSの最小値"] = [delta_eps_min]
    df_fin_index["⊿EPSの平均"] = [delta_eps_mean]
    df_fin_index["⊿EPSの標準偏差"] = [delta_eps_std]
    df_fin_index["⊿EPSのシャープレシオ"] = [delta_eps_sharpe]
    #df_fin_index["⊿EPSの変動係数"] = [delta_eps_cv]
    df_fin_index["Close"] = [price_newest]
    df_fin_index["⊿Closeの最小値"] = [delta_close_min]
    df_fin_index["⊿Closeの平均"] = [delta_close_mean]
    df_fin_index["⊿Closeの標準偏差"] = [delta_close_std]
    df_fin_index["⊿Closeのシャープレシオ"] = [delta_close_sharpe]
    #df_fin_index["⊿Closeの変動係数"] = [delta_close_cv]
    df_fin_index["Volumeの平均"] = [volume_mean]
    df_fin_index["PER（直近のIR発表後）"] = [per_newest]
    df_fin_index["PERの最小値"] = [per_min]
    df_fin_index["⊿PERの最小値"] = [delta_per_min]
    df_fin_index["⊿PERの平均"] = [delta_per_mean]
    df_fin_index["⊿PERの標準偏差"] = [delta_per_std]
    df_fin_index["⊿PERのシャープレシオ"] = [delta_per_sharpe]
    df_fin_index["投資回収期間"] = [payout_time]

    return df_fin_index



#@numba.jit  #JITで最適化
def make_fin_index_all(df_fin_all):
    code_list_all = df_fin_all["コード"].values.tolist()  #データベースにあるコードリスト
    code_list_all = list(set(code_list_all))
    code_list_all = sorted(code_list_all, reverse=False)
    #print(code_list_all)

    date_min = min(df_fin_all["決算期"]) -datetime.timedelta(days=1*30)
    date_max = max(df_fin_all["決算期"]) +datetime.timedelta(days=4*30) #4か月後まで取得
    price_n225 = pandas_datareader.data.DataReader("1321.T", "yahoo", date_min, date_max)
    price_mothers = pandas_datareader.data.DataReader("2516.T", "yahoo", date_min, date_max)

    df_fin_index_all = pd.DataFrame()  #全銘柄の指標
    for code_count in range(len(code_list_all)):
        code = code_list_all[code_count]
        #print(code)
        df_fin = df_fin_all[df_fin_all["コード"]==code]  #1銘柄の財務データ
        df_fin_index = make_fin_index(df_fin, code)  #指標を計算

        data_x = df_fin[["決算期", "Close"]].set_index("決算期")  #Date列をindexにする
        data_x = data_x["Close"]

        data_y = price_n225["Adj Close"].copy()
        df_fin_stat = make_ml_model(code, "日経平均ETF", data_x, data_y, x_delay=False)  #統計データ
        df_fin_index = pd.merge(df_fin_index, df_fin_stat, on="コード", how='outer')

        data_y = price_mothers["Adj Close"].copy()
        df_fin_stat = make_ml_model(code, "マザーズETF", data_x, data_y, x_delay=False)  #統計データ
        df_fin_index = pd.merge(df_fin_index, df_fin_stat, on="コード", how='outer')

        #取得した銘柄情報を記録
        if (len(df_fin_index_all.index) != 0):  #銘柄情報まとめデータに値がある時
            df_fin_index_all = df_fin_index_all.append(df_fin_index, ignore_index=True)
        else:  #
            df_fin_index_all = df_fin_index

    #スクリーニング
    '''df_fin_index_all = df_fin_index_all.sort_values("投資回収期間", ascending=False).dropna()
    df_fin_index_all = df_fin_index_all[0.0<df_fin_index_all["⊿EPSの最小値"]]
    df_fin_index_all = df_fin_index_all[1.0<df_fin_index_all["⊿EPSのシャープレシオ"]]
    df_fin_index_all = df_fin_index_all[df_fin_index_all["Close"]<10000.0]
    #df_fin_index_all = df_fin_index_all[-30.0<df_fin_index_all["⊿Closeの最小値"]]
    #df_fin_index_all = df_fin_index_all[10.0<df_fin_index_all["⊿Closeの平均"]]
    #df_fin_index_all = df_fin_index_all[1.0<df_fin_index_all["⊿Closeのシャープレシオ"]]
    #df_fin_index_all = df_fin_index_all[10000.0<df_fin_index_all["Volumeの平均"]]
    df_fin_index_all = df_fin_index_all[0.5<df_fin_index_all["⊿PERのシャープレシオ"]]  #'''

    return df_fin_index_all



if (__name__ == "__main__"):
    #計算の開始時刻を記録
    print ("Calculation start: ", time.ctime())  #計算開始時刻を表示
    compute_time = time.time()  #計算の開始時刻

    pd.set_option('display.unicode.east_asian_width', True)  #全角文字幅を考慮して表示


    #date = datetime.date.today().strftime('%Y%m%d')
    date = datetime.date(2021, 1, 1).strftime('%Y%m%d')

    filename = 'fund_data_' +date
    file_relative_path = os.path.dirname(__file__)
    csv_relative_path01 = r'../../inout_data/fund_data/' +filename +r'.csv'

    df_fin_all = pd.read_csv(os.path.join(file_relative_path, csv_relative_path01), index_col=0)
    df_fin_all = df_fin_all.sort_values(["コード", "決算期"])
    df_fin_all["決算期"] = pd.to_datetime(df_fin_all["決算期"])
    df_fin_all["発表日"] = pd.to_datetime(df_fin_all["発表日"])
    print(df_fin_all)


    industry = []  #TOPIX全銘柄
    #industry = ["情報・通信業", "サービス業"]
    #industry = ["サービス業"]
    #industry = ["卸売業", "小売業"]
    #industry = ["精密機器"]

    #指定した業種の銘柄を抽出。[]なら全銘柄。
    if (industry!=[]):
        df_fin_all = df_fin_all[df_fin_all["業種"].isin(industry)]
    #print(df_code)

    df_fin_index_all = make_fin_index_all(df_fin_all)
    print(df_fin_index_all.head(20))
    print(df_fin_index_all.tail(20))

    filename = 'fund_data_' +date +'_index'
    csv_relative_path01 = r'../../inout_data/fund_data/' +filename +r'.csv'
    df_fin_index_all.to_csv(os.path.join(file_relative_path, csv_relative_path01))  #データ出力


    #計算時間の表示
    compute_time = time.time() -compute_time
    print ("Calculation time: {:0.5f}[sec]".format(compute_time))

