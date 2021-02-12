import re  #正規表現用
import datetime, os

import numpy as np  #数値計算用
import pandas as pd  #データ処理用
import requests  #クローリング用
import bs4  #スクレイピング用



#財務諸表のデータを取得
#損益計算書（PL）。売上高、営業利益、経常利益、純利益。
#貸借対照表（BS）。流動資産、固定資産。流動負債、固定負債、自己資本。
#キャッシュフロー計算書（CF）。営業CF、投資CF、財務CF。
def get_stock_financials(database, stock_code, show=False):
    print("database =", database, "/ code =", str(stock_code))

    #SettingWithCopyWarningの警告文を消す
    #import warnings
    #warnings.filterwarnings('ignore')

    pd.set_option('display.unicode.east_asian_width', True)  #全角文字幅を考慮して表示



    #みんなの株式から
    if(database=="minkabu"):
        url = "https://minkabu.jp/stock/" +stock_code[:4] +"/settlement"
        print("url =", url)
        df_list = pd.read_html(url, match="決算期")  #html内の全tableをデータフレームとして取得
        #print(df_list)

        #損益計算書（PL）。決算期(決算発表日)、売上高、営業利益、経常利益、純利益、1株益
        df_PL = df_list[0].copy().dropna()  #通期、full year
        if (show==True):
            print(df_PL)
        df_PL = df_PL.rename(columns={"決算期(決算発表日)":"決算期", "1株益":"EPS"})  #列名変更
        df_PL["発表日"] = df_PL["決算期"].str[-12:]  #年月日だけ抽出
        df_PL["決算期"] = df_PL["決算期"].str.extract(r"([0-9年月]+)")  #年月だけ抽出
        df_PL["発表日"] = pd.to_datetime(df_PL["発表日"], format='(%Y/%m/%d)', errors='coerce')  #型変換
        df_PL["決算期"] = pd.to_datetime(df_PL["決算期"], format='%Y年%m月')  #型変換
        df_PL = df_PL.replace(r'(---)', np.nan, regex=True)  #無効な値を置換
        df_PL[["売上高", "営業利益"]] = df_PL[["売上高", "営業利益"]].astype(float)
        df_PL[["経常利益", "純利益", "EPS"]] = df_PL[["経常利益", "純利益", "EPS"]].astype(float)
        df_PL = df_PL[["決算期", "発表日", "売上高", "営業利益", "経常利益", "純利益", "EPS"]]
        df_PL = df_PL.sort_values("決算期", ascending=True)

        #貸借対照表（BS）。決算期、1株純資産、総資産、純資産、自己資本率
        df_BS = df_list[1].copy().dropna()
        if (show==True):
            print(df_BS)
        df_BS = df_BS.rename(columns={"1株純資産":"BPS", "純資産":"自己資本"})  #列名変更
        df_BS = df_BS.rename(columns={"自己資本率":"自己資本比率"})  #列名変更
        #df_BS["1株純資産"] = pd.to_numeric(df_BS["1株純資産"], errors='coerce')  #数値以外をNaNに変換
        #df_BS = df_BS.fillna(0)  #NaNを含む要素を置換
        df_BS["決算期"] = df_BS["決算期"].str.extract(r"([0-9年月]+)")  #年月だけ抽出
        df_BS["決算期"] = pd.to_datetime(df_BS["決算期"], format='%Y年%m月')  #型変換
        df_BS = df_BS.replace(r'(---)', np.nan, regex=True)  #無効な値を置換
        df_BS[["総資産", "自己資本", "BPS"]] = df_BS[["総資産", "自己資本", "BPS"]].astype(float)
        df_BS["総負債"] = df_BS["総資産"] -df_BS["自己資本"]
        df_BS = df_BS[["決算期", "総資産", "総負債", "自己資本", "BPS"]]
        df_BS = df_BS.sort_values("決算期", ascending=True)

        #キャッシュフロー計算書（CF）。決算期、営業CF、投資CF、財務CF、現金期末残高、フリーCF
        df_CF = df_list[3].copy().dropna()
        if (show==True):
            print(df_CF)
        df_CF["決算期"] = df_CF["決算期"].str.extract(r"([0-9年月]+)")  #年月だけ抽出
        df_CF["決算期"] = pd.to_datetime(df_CF["決算期"], format='%Y年%m月')  #型変換
        df_CF = df_CF.replace(r'(---)', np.nan, regex=True)  #無効な値を置換
        df_CF[["営業CF", "投資CF", "財務CF"]] = df_CF[["営業CF", "投資CF", "財務CF"]].astype(float)
        df_CF = df_CF[["決算期", "営業CF", "投資CF", "財務CF"]]
        df_CF = df_CF.sort_values("決算期", ascending=True)

        #収益性。決算期、ROA、ROE
        df_profit = df_list[2].copy().dropna()
        if (show==True):
            print(df_profit)
        df_profit["決算期"] = df_profit["決算期"].str.extract(r"([0-9年月]+)")  #年月だけ抽出
        df_profit["決算期"] = pd.to_datetime(df_profit["決算期"], format='%Y年%m月')  #型変換
        df_profit["ROA"] = df_profit["ROA"].str[:-1]
        df_profit["ROE"] = df_profit["ROE"].str[:-1]
        df_profit["ROA"] = pd.to_numeric(df_profit["ROA"], errors='coerce')  #数値以外をNaNに変換
        df_profit["ROE"] = pd.to_numeric(df_profit["ROE"], errors='coerce')  #数値以外をNaNに変換
        #df_profit = df_profit.fillna(0)  #NaNを含む要素を置換
        #df_profit = df_profit.replace(r'(---)', 0.0, regex=True)  #無効な値を置換
        #df_profit["ROA"] = df_profit["ROA"].str.replace(',', '')
        #df_profit["ROE"] = df_profit["ROE"].str.replace(',', '')
        df_profit[["ROA", "ROE"]] = df_profit[["ROA", "ROE"]].astype(np.float64)  #型変換
        df_profit = df_profit.sort_values("決算期", ascending=True)

        #外部結合した財務データを作る
        df_fin = pd.merge(df_PL, df_BS, on="決算期", how='outer')
        df_fin = pd.merge(df_fin, df_CF, on="決算期", how='outer')
        df_fin = pd.merge(df_fin, df_profit, on="決算期", how='outer')


    #株探から
    if(database=="kabutan"):
        url = "https://kabutan.jp/stock/finance?code=" +stock_code[:4]
        print("url =", url)

        #損益計算書（PL、通期）。決算期、売上高、営業益、経常益、最終益、修正1株益、１株配、発表日
        df_list = pd.read_html(url, match="最終益")  #html内の全tableをデータフレームとして取得
        #print(df_list)
        df_PL = df_list[0].copy().dropna()  #通期、full year
        if (show==True):
            print(df_PL)
        df_PL["発表日"] = pd.to_datetime(df_PL["発表日"], format='%y/%m/%d', errors='coerce')  #型変換
        df_PL = df_PL.rename(columns={"営業益":"営業利益", "経常益":"経常利益"})  #列名変更
        df_PL = df_PL.rename(columns={"最終益":"純利益", "修正1株益":"EPS"})  #列名変更
        df_PL["決算期"] = df_PL["決算期"].replace(r'(.*(-|予).*)', np.nan, regex=True)  #無効な値を置換
        df_PL = df_PL.dropna()  #NaNを含む行を捨てる
        df_PL["決算期"] = df_PL["決算期"].astype(str).str.extract(r"([0-9.]+)")  #年月だけ抽出
        df_PL["決算期"] = pd.to_datetime(df_PL["決算期"], format='%Y.%m')  #型変換
        df_PL = df_PL.replace(r'(－)', np.nan, regex=True)  #無効な値を置換
        df_PL[["売上高", "営業利益"]] = df_PL[["売上高", "営業利益"]].astype(float)
        df_PL[["経常利益", "純利益", "EPS"]] = df_PL[["経常利益", "純利益", "EPS"]].astype(float)
        df_PL = df_PL[["決算期", "発表日", "売上高", "営業利益", "経常利益", "純利益", "EPS"]]

        #貸借対照表（BS）。決算期、１株純資産、自己資本比率、総資産、自己資本、剰余金、有利子負債倍率、発表日
        df_list = pd.read_html(url, match="自己資本")  #html内の全tableをデータフレームとして取得
        #print(df_list)
        df_BS = df_list[0].copy().dropna()
        if (show==True):
            print(df_BS)
        #df_BS["発表日"] = pd.to_datetime(df_BS["発表日"], format='%y/%m/%d')  #型変換
        df_BS = df_BS.rename(columns={"１株純資産":"BPS"})  #列名変更
        df_BS["決算期"] = df_BS["決算期"].replace(r'(.*(-|予).*)', np.nan, regex=True)  #無効な値を置換
        df_BS = df_BS.dropna()  #NaNを含む行を捨てる
        df_BS["決算期"] = df_BS["決算期"].astype(str).str.extract(r"([0-9.]+)")  #年月だけ抽出
        df_BS["決算期"] = pd.to_datetime(df_BS["決算期"], format='%Y.%m')  #型変換
        df_BS = df_BS.replace(r'(－)', np.nan, regex=True)  #無効な値を置換
        df_BS[["総資産", "自己資本", "BPS"]] = df_BS[["総資産", "自己資本", "BPS"]].astype(float)
        df_BS["総負債"] = df_BS["総資産"] -df_BS["自己資本"]
        df_BS = df_BS[["決算期", "総資産", "総負債", "自己資本", "BPS"]]

        #キャッシュフロー計算書（CF）。決算期、営業益、フリーCF、営業CF、投資CF、財務CF、現金等残高、現金比率
        df_list = pd.read_html(url, match="営業CF")  #html内の全tableをデータフレームとして取得
        #print(df_list)
        df_CF = df_list[0].copy().dropna()
        if (show==True):
            print(df_CF)
        df_CF["決算期"] = df_CF["決算期"].replace(r'(.*(-|予).*)', np.nan, regex=True)  #無効な値を置換
        df_CF = df_CF.dropna()  #NaNを含む行を捨てる
        df_CF["決算期"] = df_CF["決算期"].astype(str).str.extract(r"([0-9.]+)")  #年月だけ抽出
        df_CF["決算期"] = pd.to_datetime(df_CF["決算期"], format='%Y.%m')  #型変換
        df_CF = df_CF.replace(r'(－)', np.nan, regex=True)  #無効な値を置換
        df_CF[["営業CF", "投資CF", "財務CF"]] = df_CF[["営業CF", "投資CF", "財務CF"]].astype(float)
        df_CF = df_CF[["決算期", "営業CF", "投資CF", "財務CF"]]

        #収益性。決算期、売上高、営業益、売上営業利益率、ＲＯＥ、ＲＯＡ、総資産回転率、修正1株益
        df_list = pd.read_html(url, match="ＲＯＥ")  #html内の全tableをデータフレームとして取得
        #print(df_list)
        df_profit = df_list[0].copy().dropna()
        if (show==True):
            print(df_profit)
        df_profit = df_profit.rename(columns={"ＲＯＥ":"ROE", "ＲＯＡ":"ROA"})  #列名変更
        df_profit["決算期"] = df_profit["決算期"].replace(r'(.*(-|予).*)', np.nan, regex=True)  #無効な値を置換
        df_profit = df_profit.dropna()  #NaNを含む行を捨てる
        df_profit["決算期"] = df_profit["決算期"].astype(str).str.extract(r"([0-9.]+)")  #年月だけ抽出
        df_profit["決算期"] = pd.to_datetime(df_profit["決算期"], format='%Y.%m')  #型変換
        df_profit = df_profit.replace(r'(－)', np.nan, regex=True)  #無効な値を置換
        df_profit[["ROA", "ROE"]] = df_profit[["ROA", "ROE"]].astype(float)
        df_profit = df_profit[["決算期", "ROA", "ROE"]]

        #外部結合した財務データを作る
        df_fin = pd.merge(df_PL, df_BS, on="決算期", how='outer')
        df_fin = pd.merge(df_fin, df_CF, on="決算期", how='outer')
        df_fin = pd.merge(df_fin, df_profit, on="決算期", how='outer')


    #株探から
    if(database=="kabutan_qtr"):
        url = "https://kabutan.jp/stock/finance?code=" +stock_code[:4]
        print("url =", url)

        #損益計算書（PL、通期）。決算期、売上高、営業益、経常益、最終益、修正1株益、１株配、発表日
        df_list = pd.read_html(url, match="最終益")  #html内の全tableをデータフレームとして取得
        df_PL = df_list[6].copy().dropna()  #3か月、quarter
        if (show==True):
            print(df_PL)
        df_PL["発表日"] = pd.to_datetime(df_PL["発表日"], format='%y/%m/%d', errors='coerce')  #型変換
        df_PL = df_PL.rename(columns={"営業益":"営業利益", "経常益":"経常利益"})  #列名変更
        df_PL = df_PL.rename(columns={"最終益":"純利益", "修正1株益":"EPS"})  #列名変更
        df_PL["決算期"] = df_PL["決算期"].replace(r'(.*予.*)', np.nan, regex=True)  #無効な値を置換
        df_PL = df_PL.dropna()  #NaNを含む行を捨てる
        df_PL["決算期"] = df_PL["決算期"].astype(str).str.extract(r"([0-9.]+)")  #年月だけ抽出
        df_PL["決算期"] = pd.to_datetime(df_PL["決算期"], format='%y.%m')  #型変換
        df_PL = df_PL.replace(r'(－)', np.nan, regex=True)  #無効な値を置換
        df_PL[["売上高", "営業利益"]] = df_PL[["売上高", "営業利益"]].astype(float)
        df_PL[["経常利益", "純利益", "EPS"]] = df_PL[["経常利益", "純利益", "EPS"]].astype(float)
        df_PL = df_PL[["決算期", "発表日", "売上高", "営業利益", "経常利益", "純利益", "EPS"]]
        df_fin = df_PL


    #銘柄名と業種を取得
    url = "https://minkabu.jp/stock/" +stock_code[:4]
    #print("url =", url)
    html = requests.get(url)
    soup = bs4.BeautifulSoup(html.text, "html.parser")
    stock_name = soup.find("h1").text
    sector_name = soup.find_all("div", class_="ly_content_wrapper size_ss")
    sector_name = sector_name[0].contents[3].text

    df_fin.insert(0, "業種", sector_name)
    df_fin.insert(0, "銘柄名", stock_name)
    df_fin.insert(0, "コード", stock_code)


    #株価データを追加
    date_min = min(df_fin["決算期"]) -datetime.timedelta(days=1*30) #1か月前まで取得
    date_max = max(df_fin["決算期"]) +datetime.timedelta(days=4*30) #4か月後まで取得
    #print(date_min, date_max)

    stock_data = get_stock_data(stock_code, 'yahoo', date_min, date_max)
    stock_data = stock_data.set_index("Date")  #indexに指定
    stock_data = stock_data.asfreq('d', method='ffill')  #直前の値で穴埋め
    stock_data = stock_data.reset_index()

    stock_data["Date"] = stock_data["Date"] +datetime.timedelta(days=-3*30)  #3か月前にずらす
    stock_data = stock_data.rename(columns={"Date":"決算期"})  #列名変更


    #df_fin = pd.merge(df_fin, stock_data, left_on="決算期", right_on="Date", how='left')
    df_fin = pd.merge(df_fin, stock_data, on="決算期", how='left')


    return df_fin



#株価データを取得
def get_stock_data(stock_code, database, date_min, date_max, show=False):
    #csvファイルから
    if(database=='csv'):
        file_relative_path = os.path.dirname(__file__)
        csv_relative_path = r'../../inout_data/price_data/' +str(stock_code) +r".T.csv"
        stock_data = pd.read_csv(os.path.join(file_relative_path, csv_relative_path))
        #stock_data = pd.read_csv(os.path.join(file_relative_path, csv_relative_path), index_col=0)
        stock_data['Date'] = pd.to_datetime(stock_data['Date'])

    #pandas_datareaderで、Yahoo!FinanceやFREDから
    else:
        import pandas_datareader
        stock_data = pandas_datareader.data.DataReader(str(stock_code), database, date_min, date_max)
        stock_data = stock_data.reset_index()  #

    if(show==True):
        print(stock_code, "=\n", stock_data.head(5).append(stock_data.tail(5)))  #先頭と末尾を表示
        print(stock_data.describe())
        print()

    return stock_data



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
    stock_code = "3984.T"  #証券コード

    #
    #財務データを取得
    df_fin = get_stock_financials("minkabu", stock_code, True)
    #df_fin = get_stock_financials("kabutan", stock_code, True)
    df_fin = get_stock_financials("kabutan_qtr", stock_code, True)
    print("df_fin =\n", df_fin)
    print()  #'''
