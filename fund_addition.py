import time, datetime, os
import numpy as np  #数値計算用
import pandas as pd  #データ処理用
import requests  #クローリング用
import bs4  #スクレイピング用
from sklearn import linear_model  #回帰分析用
from sklearn.metrics import r2_score  #決定係数用



def add_annual_data(df_fin):
    #損益計算書（PL、通期）
    df_fin["売上高"] = 10**6*df_fin["売上高"]
    df_fin["営業利益"] = 10**6*df_fin["営業利益"]
    df_fin["経常利益"] = 10**6*df_fin["経常利益"]
    df_fin["純利益"] = 10**6*df_fin["純利益"]
    df_fin["営業利益率"] = 100*df_fin["営業利益"]/df_fin["売上高"]
    df_fin["経常利益率"] = 100*df_fin["経常利益"]/df_fin["売上高"]
    df_fin["純利益率"] = 100*df_fin["純利益"]/df_fin["売上高"]
    df_fin["営業利益前年比"] = 100*df_fin["営業利益"].pct_change()  #前年比 (A-B)/B
    df_fin["経常利益前年比"] = 100*df_fin["経常利益"].pct_change()  #前年比 (A-B)/B
    df_fin["純利益前年比"] = 100*df_fin["純利益"].pct_change()  #前年比 (A-B)/B
    df_fin['EPS前年比'] = 100*df_fin['EPS'].pct_change()  #前年比 (A-B)/B

    #貸借対照表（BS）
    df_fin["総資産"] = 10**6*df_fin["総資産"]
    df_fin["総負債"] = 10**6*df_fin["総負債"]
    df_fin["自己資本"] = 10**6*df_fin["自己資本"]
    df_fin["自己資本比率"] = 100*df_fin["自己資本"]/df_fin["総資産"]
    df_fin['BPS前年比'] = 100*df_fin['BPS'].pct_change()  #前年比 (A-B)/B

    #キャッシュフロー計算書（CF）
    df_fin["営業CF"] = 10**6*df_fin["営業CF"]
    df_fin["投資CF"] = 10**6*df_fin["投資CF"]
    df_fin["財務CF"] = 10**6*df_fin["財務CF"]
    df_fin["フリーCF"] = df_fin["営業CF"] +df_fin["投資CF"]

    #収益性
    df_fin["ROA前年比"] = 100*df_fin["ROA"].pct_change()  #前年比 (A-B)/B
    df_fin["ROE前年比"] = 100*df_fin["ROE"].pct_change()  #前年比 (A-B)/B
    #'''

    #その他の指標
    df_fin["発行株数"] = df_fin["純利益"]/df_fin["EPS"]
    df_fin["時価総額"] = df_fin["発行株数"]*df_fin["Adj Close"]
    df_fin["PBR"] = df_fin["Adj Close"]/df_fin["BPS"]  #四半期データでは計算できない
    #df_fin["BPR"] = df_fin["BPS"]/df_fin["Adj Close"]  #四半期データでは計算できない
    df_fin["PER"] = df_fin["Adj Close"]/df_fin["EPS"]
    #df_fin["EPR"] = df_fin["EPS"]/df_fin["Adj Close"]
    df_fin["PER前年比"] = 100*df_fin["PER"].pct_change()  #前年比 (A-B)/B
    df_fin["Adj Close前年比"] = 100*df_fin["Adj Close"].pct_change()  #前年比 (A-B)/B


    return df_fin



#回帰モデル作成
def make_ml_model(code, text, stock_x, stock_y, x_delay=False, show=False):
    #列名を保存
    label_x = stock_x.name  #説明変数
    label_y = stock_y.name  #目的変数

    #1日後ろにずらす
    if (x_delay==True):
        stock_x = stock_x.shift(freq='1D')  #indexの場合
        #stock_x['Date'] = stock_x['Date'] +datetime.timedelta(days=1)  #列の場合

    #変数を内部結合
    df_merge = pd.merge(stock_x, stock_y, left_index=True, right_index=True, how='inner')
    #print("df_merge =\n", df_merge)

    #欠損値を削除し、ndarray化し、転置したデータを変数に使う
    df_merge = df_merge.dropna()
    data_x = df_merge[label_x].values.reshape((-1, 1))
    data_y = df_merge[label_y].values.reshape((-1, 1))

    model = linear_model.LinearRegression()  #重回帰分析用
    
    try:
        model.fit(data_x, data_y)  #予測モデルを作成
        y_pred = model.predict(data_x)  #予測値を計算
    
        a = model.coef_[0,0]  #傾き
        b = model.intercept_[0]  #切片
        r2 = r2_score(data_x, y_pred)  #決定係数r^2

    except Exception as e:
        #import traceback
        #print("エラー情報\n" + traceback.format_exc())
        
        b = np.nan
        r2 = np.nan

    df_fin_stat = pd.DataFrame()  #1銘柄の指標
    df_fin_stat["コード"] = [code]
    df_fin_stat[text +"に対する切片"] = [b]
    df_fin_stat[text +"との決定係数"] = [r2]

    return df_fin_stat



def get_stock_forecast(database, stock_code, show=False):
    
    if(database=="nikkei"):
        url = "https://www.nikkei.com/nkd/company/?scode=" +stock_code[:4]
        html = requests.get(url)
        soup = bs4.BeautifulSoup(html.text, "html.parser")

        forward_per = soup.find_all("div", class_="m-stockInfo_detail_right")
        forward_per = forward_per[0].find_all("span", class_="m-stockInfo_detail_value")
        forward_per = forward_per[1].text[:-1]
        print(forward_per)


    if(database=="kabuyoho"):
        url = "https://kabuyoho.jp/reportTarget?bcode=" +stock_code[:4]
        df_list = pd.read_html(url, match="株価")  #html内の全tableをデータフレームとして取得
        print(df_list)
        df_PL = df_list[0].copy().dropna()

        forward_per = soup.find_all("section", class_="m-stockInfo_detail_right")
        #forward_per = forward_per[0].find_all("span", class_="m-stockInfo_detail_value")
        print(forward_per)



if (__name__ == "__main__"):
    stock_code = '7203.T'
    get_stock_forecast('nikkei', stock_code, show=False)
    get_stock_forecast('kabuyoho', stock_code, show=False)

