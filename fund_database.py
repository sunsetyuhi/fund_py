import time, datetime, os, collections
import numpy as np  #数値計算用
import pandas as pd  #データ処理用

from fund_data import *
from fund_addition import *
from fund_process import *



#TOPIX構成銘柄情報を取得
def get_jp_code(database, show=False):
    #
    if (database=="jpx"):
        pd.set_option('display.unicode.east_asian_width', True)  #全角文字幅を考慮して表示

        excel_name = "https://www.jpx.co.jp/markets/indices/topix/tvdivq00000030ne-att/TOPIX_weight_jp.xlsx"
        df_code = pd.read_excel(excel_name)

        df_code["日付"] = df_code["日付"].replace(r'(.*/D.*)', np.nan, regex=True)  #無効な値を置換
        df_code = df_code.drop(["調整係数対象銘柄"], axis=1).dropna()  #NaNを含む行を捨てる
        df_code["日付"] = pd.to_datetime(df_code["日付"], format='%Y%m%d')  #型変換
        df_code["コード"] = df_code["コード"].astype(str).str[:4] +".T"

        if (show==True):
            counter = collections.Counter(df_code["業種"].values.tolist())  #単語の出現回数を取得
            print(counter)

    if (database=="xlsx"):
        pass

    return df_code



def get_database(code_list, database, filename, loop=1, show=False):
    file_relative_path = os.path.dirname(__file__)
    csv_relative_path01 = r'../../inout_data/fund_data/' +filename +r'.csv'
    csv_relative_path02 = r'../../inout_data/fund_data/' +filename +r'_error.csv'
    
    #保存済みのファイルがあれば開く
    try:
        df_fin_all = pd.read_csv(os.path.join(file_relative_path, csv_relative_path01), index_col=0)
        df_fin_all = df_fin_all.sort_values(["コード", "決算期"])
        df_fin_all = df_fin_all.drop_duplicates()  #重複行を削除
        df_fin_all["決算期"] = pd.to_datetime(df_fin_all["決算期"])
        df_fin_all["発表日"] = pd.to_datetime(df_fin_all["発表日"])

        df_fin_error_all = pd.read_csv(os.path.join(file_relative_path, csv_relative_path02), index_col=0)
        df_fin_error_all = df_fin_error_all.sort_values(["コード"])
        df_fin_error_all = df_fin_error_all.drop_duplicates()  #重複行を削除
        
        if(database=="minkabu"):
            df_fin_error_all = df_fin_error_all[df_fin_error_all["エラー文"] != "HTTP Error 404: Not Found"]
        elif(database=="kabutan_qtr"):
            df_fin_error_all = df_fin_error_all[df_fin_error_all["エラー文"] != "No tables found matching pattern '最終益'"]
            df_fin_error_all = df_fin_error_all[df_fin_error_all["エラー文"] != "list index out of range"]

        #code_list_all = list(set(df_fin_all["コード"].values.tolist()))  #データベースにあるコードリスト
        #code_residue = list(set(code_list) -set(code_list_all))  #探索リスト（HTTP Error 404含む）
        code_residue = list(set(df_fin_error_all["コード"].values.tolist()))  #探索リスト（HTTP Error 404除く）
        code_residue = sorted(code_residue, reverse=False)

    except Exception as e:
        df_fin_all = pd.DataFrame()
        df_fin_error_all = pd.DataFrame()  #取得に失敗した銘柄

        code_residue = list(set(code_list))  #探索が必要なコードリスト
        code_residue = sorted(code_residue, reverse=False)

    print("df_fin_all =\n", df_fin_all)
    print("code_residue =\n", code_residue)


    for loop_count in range(loop):
        for code_count in range(len(code_residue)):
            try:
                #財務データ取得
                df_fin = get_stock_financials(database, code_residue[code_count])

                #財務データにデータ追加
                df_fin = add_annual_data(df_fin)
                
                #取得した銘柄情報を記録
                if (len(df_fin_all.index) != 0):  #銘柄情報まとめデータに値がある時
                    df_fin_all = df_fin_all.append(df_fin, ignore_index=True)
                else:  #
                    df_fin_all = df_fin

            except Exception as e:
                import traceback
                print("エラー情報\n" +traceback.format_exc())

                #取得に失敗した銘柄情報を記録
                df_fin_error = pd.DataFrame({ "コード":[code_residue[code_count]] })
                df_fin_error["エラー文"] = e
                if (len(df_fin_error_all.index) != 0):  #銘柄情報まとめデータに値がある時
                    df_fin_error_all = df_fin_error_all.append(df_fin_error, ignore_index=True)
                else:  #
                    df_fin_error_all = df_fin_error
                #print("df_fin_error_all = ", df_fin_error_all)

            #進捗状況
            print("progress (loop) = ", loop_count+1, "/", loop)
            print("progress (code) = ", code_count+1, "/", len(code_residue))
            print("------------------------------")
            print()

            #定期処理
            if ((code_count+1)%50 == 0):
                #ファイル保存
                df_fin_all = df_fin_all.astype(str)
                df_fin_all = df_fin_all.sort_values(["コード", "決算期"])
                df_fin_all = df_fin_all.drop_duplicates()  #重複行を削除
                df_fin_all.to_csv(os.path.join(file_relative_path, csv_relative_path01))  #データ出力

                df_fin_error_all = df_fin_error_all.astype(str)
                df_fin_error_all = df_fin_error_all.sort_values(["コード"])
                df_fin_error_all = df_fin_error_all.drop_duplicates()  #重複行を削除
                df_fin_error_all.to_csv(os.path.join(file_relative_path, csv_relative_path02))  #データ出力

                #処理を一時停止する（データの取得エラー対策）
                print("Sleep now (30 seconds).")
                print()
                time.sleep(30)

        #ファイル保存
        df_fin_all = df_fin_all.astype(str)
        df_fin_all = df_fin_all.sort_values(["コード", "決算期"])
        df_fin_all = df_fin_all.drop_duplicates()  #重複行を削除
        df_fin_all.to_csv(os.path.join(file_relative_path, csv_relative_path01))  #データ出力

        df_fin_error_all = df_fin_error_all.astype(str)
        df_fin_error_all = df_fin_error_all.sort_values(["コード"])
        df_fin_error_all = df_fin_error_all.drop_duplicates()  #重複行を削除
        df_fin_error_all.to_csv(os.path.join(file_relative_path, csv_relative_path02))  #データ出力

        print("df_fin_error_all = ", df_fin_error_all)


    return df_fin_all



if (__name__ == "__main__"):
    #計算の開始時刻を記録
    print ("Calculation start: ", time.ctime())  #計算開始時刻を表示
    compute_time = time.time()  #計算の開始時刻

    pd.set_option('display.unicode.east_asian_width', True)  #全角文字幅を考慮して表示


    #TOPIX構成銘柄情報を取得
    df_code = get_jp_code("jpx", show=True)
    #print(df_code)

    #指定した業種の銘柄を抽出。[]なら全銘柄。
    industry = []  #全銘柄
    #industry = ["情報・通信業"]
    #industry = ["卸売業", "小売業"]
    #industry = ["精密機器"]
    if (industry!=[]):
        df_code = df_code[df_code["業種"].isin(industry)]
    #print(df_code)

    #code_list = df_code["コード"].values.tolist()
    code_list = [str(i) +".T" for i in range(1300, 10000)]  #総当たり
    #print(code_list)


    #
    #date = datetime.date.today().strftime('%Y%m%d')
    date = datetime.date(2021, 1, 1).strftime('%Y%m%d')
    filename = 'fund_data_' +date
    df_fin_all = get_database(code_list, "minkabu", filename, loop=2)
    #df_fin_all = get_database(code_list, "kabutan_qtr", filename, loop=2)
    print(df_fin_all)


    #計算時間の表示
    compute_time = time.time() -compute_time
    print ("Calculation time: {:0.5f}[sec]".format(compute_time))

