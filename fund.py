import datetime
import numpy as np  #数値計算用
import pandas as pd  #データ処理用

from fund_data import *
from fund_process import *
from fund_show import *



if (__name__ == "__main__"):
    #^N225:日経平均、TPY=F:TOPIX先物
    #^GSPC:S&P500、^DJI:Dow30、MSFT:マイクロソフト
    #1321:225投信、1570:日経レバETF、1571:日経インバETF、1330:上場インデックス225
    #2413:エムスリー、2678:アスクル、
    #3407:旭化成、3769:GMOPG、3923:ラクス、3990:UUUM
    #4385:メルカリ、4436:ミンカブ、4478:フリー、4479:マクアケ、4776:サイボウズ、
    #6096:レアジョブ、6448:ブラザー工業、
    #6628:オンキヨー、6718:アイホン、6752:パナソニック、6861:キーエンス、6954:ファナック
    #7068:フィードフォース、7079:WDBココ、7201:日産、7203:トヨタ、
    #8306:三菱UFJ、8411:みずほ
    #9020:JR東、9022:JR東海、9962:ミスミ、
    stock_code = "7564.T"  #証券コード

    #
    try:
        #財務データを取得
        df_fin = get_stock_financials("minkabu", stock_code, True)
        #df_fin = get_stock_financials("kabutan", stock_code, True)
        print("df_fin =\n", df_fin)
        print()  #'''

    except Exception as e:
        import traceback
        print("エラー情報\n" + traceback.format_exc())
        #print("例外:", e.args)


    #
    try:
        #財務データ追加
        df_fin = add_annual_data(df_fin)
        print(df_fin)
        print(df_fin['フリーCF'])

        #財務三表のグラフ
        show_financial_statements(stock_code, df_fin)

    except Exception as e:
        import traceback
        print("エラー情報\n" + traceback.format_exc())
        #print("例外:", e.args)

