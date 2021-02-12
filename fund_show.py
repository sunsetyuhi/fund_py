import numpy as np  #数値計算用
import pandas as pd  #データ処理用
import matplotlib.pyplot as plt  #データ可視化用
import matplotlib.dates as mdates  #日付処理用
import seaborn as sns  #matplotlib拡張用



def show_financial_statements(stock_code, df_fin):
    #BSの面積図、去年と今年のレーダーチャート
    
    fig = plt.figure(figsize=(8, 6), dpi=100, facecolor='#ffffff')
    plt.rcParams["font.family"] = "IPAexGothic" #全体のフォントを設定
    plt.suptitle('Financial statements : code ' +str(stock_code))  #グラフタイトル


    ###グラフ左上
    ax = fig.add_subplot(3, 2, 1)
    #ax = fig.add_subplot(2, 3, 1)
    plt.plot(df_fin['決算期'], df_fin['売上高'], lw=1.0, label='売上高')  #
    #plt.plot(df_fin['決算期'], df_fin['粗利益'], lw=1.0, label='粗利益')  #
    plt.plot(df_fin['決算期'], df_fin['営業利益'], lw=1.0, label='営業利益')  #
    plt.plot(df_fin['決算期'], df_fin['経常利益'], lw=1.0, label='経常利益')  #
    plt.plot(df_fin['決算期'], df_fin['純利益'], lw=1.0, label='純利益')  #

    ax.set_title("損益計算書（PL）")
    plt.xlabel('Date')
    plt.ylabel('Amount')
    plt.grid(which='major',color='gray',linestyle='-')  #主目盛
    plt.axhline(0, color='#000000')  #f(x)=0の線
    plt.legend(loc='best') #凡例(グラフラベル)を表示


    ###グラフ左中
    ax = fig.add_subplot(3, 2, 3)
    #ax = fig.add_subplot(2, 3, 2)
    plt.plot(df_fin['決算期'], df_fin['総資産'], lw=1.0, label='総資産')  #
    plt.plot(df_fin['決算期'], df_fin['総負債'], lw=1.0, label='総負債')  #
    plt.plot(df_fin['決算期'], df_fin['自己資本'], lw=1.0, label='自己資本')  #

    ax.set_title("貸借対照表（BS）")
    plt.xlabel('Date')
    plt.ylabel('Amount')
    plt.grid(which='major',color='gray',linestyle='-')  #主目盛
    plt.axhline(0, color='#000000')  #f(x)=0の線
    plt.legend(loc='best') #凡例(グラフラベル)を表示


    ###グラフ左下
    ax = fig.add_subplot(3, 2, 5)
    #ax = fig.add_subplot(2, 3, 3)
    plt.plot(df_fin['決算期'], df_fin['営業CF'], lw=1.0, label='営業CF')  #
    plt.plot(df_fin['決算期'], df_fin['投資CF'], lw=1.0, label='投資CF')  #
    plt.plot(df_fin['決算期'], df_fin['財務CF'], lw=1.0, label='財務CF')  #
    plt.plot(df_fin['決算期'], df_fin['フリーCF'], lw=1.0, label='フリーCF')  #

    ax.set_title("キャッシュフロー計算書（CL）")
    plt.xlabel('Date')
    plt.ylabel('Amount')
    plt.grid(which='major',color='gray',linestyle='-')  #主目盛
    plt.axhline(0, color='#000000')  #f(x)=0の線
    plt.legend(loc='best') #凡例(グラフラベル)を表示


    ###グラフ右上
    ax = fig.add_subplot(3, 2, 2)
    #ax = fig.add_subplot(2, 3, 4)
    #plt.plot(df_fin['決算期'], df_fin["営業利益率"], lw=1.0, label='営業利益率')  #
    plt.plot(df_fin['決算期'], df_fin["経常利益率"], lw=1.0, label='経常利益率')  #
    plt.plot(df_fin['決算期'], df_fin["純利益率"], lw=1.0, label='純利益率')  #
    plt.plot(df_fin['決算期'], df_fin["自己資本比率"], lw=1.0, label='自己資本比率')  #
    plt.plot(df_fin['決算期'], df_fin['ROA'], lw=1.0, label='総資産利益率(ROA)')  #
    plt.plot(df_fin['決算期'], df_fin['ROE'], lw=1.0, label='自己資本利益率(ROE)')  #

    ax.set_title("収益性")
    plt.xlabel('Date')
    plt.ylabel('Ratio')
    plt.grid(which='major',color='gray',linestyle='-')  #主目盛
    plt.axhline(0, color='#000000')  #f(x)=0の線
    plt.legend(loc='best') #凡例(グラフラベル)を表示
    #plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left', borderaxespad=0)


    ###グラフ右中
    ax = fig.add_subplot(3, 2, 4)
    #ax = fig.add_subplot(2, 3, 5)
    plt.plot(df_fin['決算期'], df_fin['BPS'], lw=1.0, label='1株当たり純資産(BPS)')  #
    plt.plot(df_fin['決算期'], df_fin['EPS'], lw=1.0, label='1株当たり純利益(EPS)')  #

    ax.set_title("1株当たりの指標")
    plt.xlabel('Date')
    plt.ylabel('Amount')
    plt.grid(which='major',color='gray',linestyle='-')  #主目盛
    plt.axhline(0, color='#000000')  #f(x)=0の線
    plt.legend(loc='best') #凡例(グラフラベル)を表示


    ###グラフ右下
    ax = fig.add_subplot(3, 2, 6)
    #ax = fig.add_subplot(2, 3, 6)
    #plt.plot(df_fin['決算期'], df_fin['営業利益前年比'], lw=1.0, label='営業利益')  #
    plt.plot(df_fin['決算期'], df_fin['経常利益前年比'], lw=1.0, label='経常利益')  #
    plt.plot(df_fin['決算期'], df_fin['純利益前年比'], lw=1.0, label='純利益')  #
    plt.plot(df_fin['決算期'], df_fin['BPS前年比'], lw=1.0, label='BPS')  #
    plt.plot(df_fin['決算期'], df_fin['EPS前年比'], lw=1.0, label='EPS')  #
    plt.plot(df_fin['決算期'], df_fin['ROA前年比'], lw=1.0, label='ROA')  #
    plt.plot(df_fin['決算期'], df_fin['ROE前年比'], lw=1.0, label='ROE')  #

    ax.set_title("前年比")
    plt.xlabel('Date')
    plt.ylabel('Ratio')
    plt.grid(which='major',color='gray',linestyle='-')  #主目盛
    plt.axhline(0, color='#000000')  #f(x)=0の線
    plt.legend(loc='best') #凡例(グラフラベル)を表示


    #余白を調整
    fig.tight_layout()
    plt.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9, wspace=0.2, hspace=0.4)
    #plt.subplots_adjust(bottom=0.1, top=0.9, wspace=0.2, hspace=0.3)
    plt.show()



if (__name__ == "__main__"):
    from fund_data import *
    from fund_process import *
    
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
    stock_code = "8411.T"  #証券コード

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

        #財務三表のグラフ
        show_financial_statements(stock_code, df_fin)

    except Exception as e:
        import traceback
        print("エラー情報\n" + traceback.format_exc())
        #print("例外:", e.args)

