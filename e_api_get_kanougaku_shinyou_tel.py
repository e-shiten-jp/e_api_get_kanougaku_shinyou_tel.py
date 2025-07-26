# -*- coding: utf-8 -*-
# Copyright (c) 2021 Tachibana Securities Co., Ltd. All rights reserved.

# 2021.07.08,   yo.
# 2022.10.20 reviced,   yo.
# 2025.07.25 reviced,   yo.
# Python 3.11.2 / debian12
# API v4r7 で動作確認
# 立花証券ｅ支店ＡＰＩ利用のサンプルコード
# 機能: 信用新規建可能額の取得
#
# 利用方法: 
# 事前に「e_api_login_tel.py」を実行して、仮想URL等を取得しておいてください。
#
# == ご注意: ========================================
#   本番環境にに接続した場合、実際に市場に注文を出せます。
#   市場で約定した場合取り消せません。
# ==================================================
#

import urllib3
import datetime
import json
import time


#--- 共通コード ------------------------------------------------------

# request項目を保存するクラス。配列として使う。
# 'p_no'、'p_sd_date'は格納せず、func_make_url_requestで生成する。
class class_req :
    def __init__(self) :
        self.str_key = ''
        self.str_value = ''
        
    def add_data(self, work_key, work_value) :
        self.str_key = func_check_json_dquat(work_key)
        self.str_value = func_check_json_dquat(work_value)


# 口座属性クラス
class class_def_account_property:
    def __init__(self):
        self.sUserId = ''           # userid
        self.sPassword = ''         # password
        self.sSecondPassword = ''   # 第２パスワード
        self.sUrl = ''              # 接続先URL
        self.sJsonOfmt = 5          # 返り値の表示形式指定
        
# ログイン属性クラス
class class_def_login_property:
    def __init__(self):
        self.p_no = 0               # 累積p_no
        self.sUrlRequest = ''       # request用仮想URL
        self.sUrlMaster = ''        # master用仮想URL
        self.sUrlPrice = ''         # price用仮想URL
        self.sUrlEvent = ''         # event用仮想URL
        self.sZyoutoekiKazeiC = ''  # 8.譲渡益課税区分    1：特定  3：一般  5：NISA     ログインの返信データで設定済み。 
        self.sSecondPassword = ''   # 22.第二パスワード  APIでは第２暗証番号を省略できない。 関連資料:「立花証券・e支店・API、インターフェース概要」の「3-2.ログイン、ログアウト」参照
        self.sJsonOfmt = ''         # 返り値の表示形式指定
        
        

# 機能: システム時刻を"p_sd_date"の書式の文字列で返す。
# 返値: "p_sd_date"の書式の文字列
# 引数1: システム時刻
# 備考:  "p_sd_date"の書式：YYYY.MM.DD-hh:mm:ss.sss
def func_p_sd_date(int_systime):
    str_psddate = ''
    str_psddate = str_psddate + str(int_systime.year) 
    str_psddate = str_psddate + '.' + ('00' + str(int_systime.month))[-2:]
    str_psddate = str_psddate + '.' + ('00' + str(int_systime.day))[-2:]
    str_psddate = str_psddate + '-' + ('00' + str(int_systime.hour))[-2:]
    str_psddate = str_psddate + ':' + ('00' + str(int_systime.minute))[-2:]
    str_psddate = str_psddate + ':' + ('00' + str(int_systime.second))[-2:]
    str_psddate = str_psddate + '.' + (('000000' + str(int_systime.microsecond))[-6:])[:3]
    return str_psddate


# JSONの値の前後にダブルクオーテーションが無い場合付ける。
def func_check_json_dquat(str_value) :
    if len(str_value) == 0 :
        str_value = '""'
        
    if not str_value[:1] == '"' :
        str_value = '"' + str_value
        
    if not str_value[-1:] == '"' :
        str_value = str_value + '"'
        
    return str_value
    
    
# 受けたテキストの１文字目と最終文字の「"」を削除
# 引数：string
# 返り値：string
def func_strip_dquot(text):
    if len(text) > 0:
        if text[0:1] == '"' :
            text = text[1:]
            
    if len(text) > 0:
        if text[-1] == '\n':
            text = text[0:-1]
        
    if len(text) > 0:
        if text[-1:] == '"':
            text = text[0:-1]
        
    return text
    


# 機能: URLエンコード文字の変換
# 引数1: 文字列
# 返値: URLエンコード文字に変換した文字列
# 
# URLに「#」「+」「/」「:」「=」などの記号を利用した場合エラーとなる場合がある。
# APIへの入力文字列（特にパスワードで記号を利用している場合）で注意が必要。
#   '#' →   '%23'
#   '+' →   '%2B'
#   '/' →   '%2F'
#   ':' →   '%3A'
#   '=' →   '%3D'
def func_replace_urlecnode( str_input ):
    str_encode = ''
    str_replace = ''
    
    for i in range(len(str_input)):
        str_char = str_input[i:i+1]

        if str_char == ' ' :
            str_replace = '%20'       #「 」 → 「%20」 半角空白
        elif str_char == '!' :
            str_replace = '%21'       #「!」 → 「%21」
        elif str_char == '"' :
            str_replace = '%22'       #「"」 → 「%22」
        elif str_char == '#' :
            str_replace = '%23'       #「#」 → 「%23」
        elif str_char == '$' :
            str_replace = '%24'       #「$」 → 「%24」
        elif str_char == '%' :
            str_replace = '%25'       #「%」 → 「%25」
        elif str_char == '&' :
            str_replace = '%26'       #「&」 → 「%26」
        elif str_char == "'" :
            str_replace = '%27'       #「'」 → 「%27」
        elif str_char == '(' :
            str_replace = '%28'       #「(」 → 「%28」
        elif str_char == ')' :
            str_replace = '%29'       #「)」 → 「%29」
        elif str_char == '*' :
            str_replace = '%2A'       #「*」 → 「%2A」
        elif str_char == '+' :
            str_replace = '%2B'       #「+」 → 「%2B」
        elif str_char == ',' :
            str_replace = '%2C'       #「,」 → 「%2C」
        elif str_char == '/' :
            str_replace = '%2F'       #「/」 → 「%2F」
        elif str_char == ':' :
            str_replace = '%3A'       #「:」 → 「%3A」
        elif str_char == ';' :
            str_replace = '%3B'       #「;」 → 「%3B」
        elif str_char == '<' :
            str_replace = '%3C'       #「<」 → 「%3C」
        elif str_char == '=' :
            str_replace = '%3D'       #「=」 → 「%3D」
        elif str_char == '>' :
            str_replace = '%3E'       #「>」 → 「%3E」
        elif str_char == '?' :
            str_replace = '%3F'       #「?」 → 「%3F」
        elif str_char == '@' :
            str_replace = '%40'       #「@」 → 「%40」
        elif str_char == '[' :
            str_replace = '%5B'       #「[」 → 「%5B」
        elif str_char == ']' :
            str_replace = '%5D'       #「]」 → 「%5D」
        elif str_char == '^' :
            str_replace = '%5E'       #「^」 → 「%5E」
        elif str_char == '`' :
            str_replace = '%60'       #「`」 → 「%60」
        elif str_char == '{' :
            str_replace = '%7B'       #「{」 → 「%7B」
        elif str_char == '|' :
            str_replace = '%7C'       #「|」 → 「%7C」
        elif str_char == '}' :
            str_replace = '%7D'       #「}」 → 「%7D」
        elif str_char == '~' :
            str_replace = '%7E'       #「~」 → 「%7E」
        else :
            str_replace = str_char
        str_encode = str_encode + str_replace        
    return str_encode


# 機能： ファイルから文字情報を読み込み、その文字列を返す。
# 戻り値： 文字列
# 第１引数： ファイル名
# 備考：　json形式のファイルを想定。
def func_read_from_file(str_fname):
    str_read = ''
    try:
        with open(str_fname, 'r', encoding = 'utf_8') as fin:
            while True:
                line = fin.readline()
                if not len(line):
                    break
                str_read = str_read + line
        return str_read
    except IOError as e:
        print('Can not Write!!!')
        print(type(e))



# 機能： API問合せ文字列を作成し返す。
# 戻り値： api問合せのurl文字列
# 第１引数： ログインは、Trueをセット。それ以外はFalseをセット。
# 第２引数： ログインは、APIのurlをセット。それ以外はログインで返された仮想url（'sUrlRequest'等）の値をセット。
# 第３引数： 要求項目のデータセット。クラスの配列として受取る。
def func_make_url_request(auth_flg, \
                          url_target, \
                          work_class_req) :
    str_url = url_target
    if auth_flg == True :   # ログインの場合
        str_url = str_url + 'auth/'
    str_url = str_url + '?'
    str_url = str_url + func_make_json_format(work_class_req)
    return str_url


# 機能: API問合せ。通常のrequest,price用。
# 返値: API応答（辞書型）
# 第１引数： URL文字列。
# 備考: APIに接続し、requestの文字列を送信し、応答データを辞書型で返す。
#       master取得は専用の func_api_req_muster を利用する。
def func_api_req(str_url): 
    print('送信文字列＝')
    print(str_url)  # 送信する文字列

    # APIに接続
    http = urllib3.PoolManager()
    req = http.request('GET', str_url)
    print("req.status= ", req.status )

    # 取得したデータを、json.loadsを利用できるようにstr型に変換する。日本語はshift-jis。
    bytes_reqdata = req.data
    str_shiftjis = bytes_reqdata.decode("shift-jis", errors="ignore")

    print('返信文字列＝')
    print(str_shiftjis)

    # JSON形式の文字列を辞書型で取り出す
    json_req = json.loads(str_shiftjis)

    return json_req


# 機能: class_req型データをjson形式の文字列に変換する。
# 返値: json形式の文字
# 第１引数： class_req型データ
def func_make_json_format(work_class_req):
    str_json_data =  '{\n\t'
    for i in range(len(work_class_req)) :
        if len(work_class_req[i].str_key) > 0:
            str_json_data = str_json_data + work_class_req[i].str_key + ':' + work_class_req[i].str_value + ',\n\t'
    str_json_data = str_json_data[:-3] + '\n}'
    return str_json_data


# 機能： アカウント情報をファイルから取得する
# 引数1: 口座情報を保存したファイル名
# 引数2: 口座情報（class_def_account_property型）データ
def func_get_acconut_info(fname, class_account_property):
    str_account_info = func_read_from_file(fname)
    # JSON形式の文字列を辞書型で取り出す
    json_account_info = json.loads(str_account_info)

    class_account_property.sUserId = json_account_info.get('sUserId')
    class_account_property.sPassword = json_account_info.get('sPassword')
    class_account_property.sSecondPassword = json_account_info.get('sSecondPassword')
    class_account_property.sUrl = json_account_info.get('sUrl')

    # 返り値の表示形式指定
    class_account_property.sJsonOfmt = json_account_info.get('sJsonOfmt')
    # "5"は "1"（1ビット目ＯＮ）と”4”（3ビット目ＯＮ）の指定となり
    # ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定


# 機能： ログイン情報をファイルから取得する
# 引数1: ログイン情報を保存したファイル名（fname_login_response = "e_api_login_response.txt"）
# 引数2: ログインデータ型（class_def_login_property型）
def func_get_login_info(str_fname, class_login_property):
    str_login_respons = func_read_from_file(str_fname)
    dic_login_respons = json.loads(str_login_respons)
    class_login_property.sUrlRequest = dic_login_respons.get('sUrlRequest')                # request用仮想URL
    class_login_property.sUrlMaster = dic_login_respons.get('sUrlMaster')                  # master用仮想URL
    class_login_property.sUrlPrice = dic_login_respons.get('sUrlPrice')                    # price用仮想URL
    class_login_property.sUrlEvent = dic_login_respons.get('sUrlEvent')                    # event用仮想URL
    class_login_property.sUrlEventWebSocket = dic_login_respons.get('sUrlEventWebSocket')  # webxocket用仮想URL
    class_login_property.sZyoutoekiKazeiC = dic_login_respons.get('sZyoutoekiKazeiC')      # 8.譲渡益課税区分    1：特定  3：一般  5：NISA     ログインの返信データで設定済み。 
    

# 機能： p_noをファイルから取得する
# 引数1: p_noを保存したファイル名（fname_info_p_no = "e_api_info_p_no.txt"）
# 引数2: login情報（class_def_login_property型）データ
def func_get_p_no(fname, class_login_property):
    str_p_no_info = func_read_from_file(fname)
    # JSON形式の文字列を辞書型で取り出す
    json_p_no_info = json.loads(str_p_no_info)
    class_login_property.p_no = int(json_p_no_info.get('p_no'))
        
    
# 機能: ファイルに書き込む
# 引数1: 出力ファイル名
# 引数2: 出力するデータ
# 備考:
def func_write_to_file(str_fname_output, str_data):
    try:
        with open(str_fname_output, 'w', encoding = 'utf-8') as fout:
            fout.write(str_data)
    except IOError as e:
        print('Can not Write!!!')
        print(type(e))


# 機能: p_noを保存するためのjson形式のテキストデータを作成します。
# 引数1: p_noを保存するファイル名（fname_info_p_no = "e_api_info_p_no.txt"）
# 引数2: 保存するp_no
# 備考:
def func_save_p_no(str_fname_output, int_p_no):
    # "p_no"を保存する。
    str_info_p_no = '{\n'
    str_info_p_no = str_info_p_no + '\t' + '"p_no":"' + str(int_p_no) + '"\n'
    str_info_p_no = str_info_p_no + '}\n'
    func_write_to_file(str_fname_output, str_info_p_no)
    print('現在の"p_no"を保存しました。 p_no =', int_p_no)            
    print('ファイル名:', str_fname_output)

#--- 以上 共通コード -------------------------------------------------




# 参考資料（必ず最新の資料を参照してください。）
#マニュアル
#「立花証券・ｅ支店・ＡＰＩ（v4r2）、REQUEST I/F、機能毎引数項目仕様」
# (api_request_if_clumn_v4r2.pdf)
# p13/46 No.10 CLMZanShinkiKanoIjiritu を参照してください。
#
# 11 CLMZanShinkiKanoIjiritu
#  1 sCLMID	メッセージＩＤ	char*	I/O	"CLMZanShinkiKanoIjiritu"
#  2 sIssueCode	銘柄コード	char[12]	I/O	銘柄コード（6501 等）
#  3 sSizyouC	市場	char[2]	I/O	00：東証"
#  4 sResultCode	結果コード	char[9]	O	０：ＯＫ、０以外：CLMMsgTable.sMsgIdで検索しテキストを表示。 0～999999999、左詰め、マイナスの場合なし
#  5 sResultText	結果テキスト	char[512]	O	ShiftJis
#  6 sWarningCode	警告コード	char[9]	O	０：ＯＫ、０以外：CLMMsgTable.sMsgIdで検索しテキストを表示。 0～999999999、左詰め、マイナスの場合なし
#  7 sWarningText	警告テキスト	char[512]	O	ShiftJis
#  8 sSummaryUpdate	更新日時	char[12]	O	YYYYMMDDHHMM  照会機能仕様書 ２－５．（３）、(以下は標準WebになくRich-I/Fにある項目) No.1
#  9 sSummarySinyouSinkidate	信用新規建可能額	char[16]	O	照会機能仕様書 ２－５．（３）、（A）現物取引 - 買付注文 - 通常 No.4。 0～9999999999999999、左詰め、マイナスの場合なし
# 10 sItakuhosyoukin	委託保証金率	char[13]	O	照会機能仕様書 ２－５．（３）、（E1）可能額・数量等 No.5。 0.00～999999999999.99、左詰め、マイナスの場合なし、小数点以下桁数切詰め
# 11 sOisyouKakuteiFlg	追証フラグ	char[1]	O	0：未確定, 1：確定  照会機能仕様書 ２－５．（３）、（以下は標準WebになくRich-I/Fにある項目） No.2




# --------------------------
# 機能: 信用新規建可能額取得
# 返値: API応答（辞書型）
# 引数1： p_no
# 引数2： class_cust_property（request通番）, 口座属性クラス
# 備考:
#
def func_kanougaku_shinyou(int_p_no, class_login_property):

    req_item = [class_req()]
    str_p_sd_date = func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得

    str_key = '"p_no"'
    str_value = func_check_json_dquat(str(int_p_no))
    #req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"p_sd_date"'
    str_value = str_p_sd_date
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sCLMID"'
    str_value = 'CLMZanShinkiKanoIjiritu'  # 信用新規建可能額を指示。
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = class_login_property.sJsonOfmt    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    # URL文字列の作成
    str_url = func_make_url_request(False, \
                                     class_login_property.sUrlRequest, \
                                     req_item)

    json_return = func_api_req(str_url)

    return json_return











    
# ======================================================================================================
# ==== プログラム始点 =================================================================================
# ======================================================================================================

if __name__ == "__main__":
    # --- ファイル名等を設定 ------------------------------------------------------------------
    fname_account_info = "e_api_account_info.txt"
    fname_login_response = "e_api_login_response.txt"
    fname_info_p_no = "e_api_info_p_no.txt"
    # --- 以上ファイル名設定 -------------------------------------------------------------------------

    my_account_property = class_def_account_property()
    my_login_property = class_def_login_property()
    
    # 口座情報をファイルから読み込む。
    func_get_acconut_info(fname_account_info, my_account_property)
    
    # ログイン応答を保存した「e_api_login_response.txt」から、仮想URLと課税flgを取得
    func_get_login_info(fname_login_response, my_login_property)

    
    my_login_property.sJsonOfmt = my_account_property.sJsonOfmt                   # 返り値の表示形式指定
    my_login_property.sSecondPassword = func_replace_urlecnode(my_account_property.sSecondPassword)        # 22.第二パスワード  APIでは第２暗証番号を省略できない。 関連資料:「立花証券・e支店・API、インターフェース概要」の「3-2.ログイン、ログアウト」参照
    
    # 現在（前回利用した）のp_noをファイルから取得する
    func_get_p_no(fname_info_p_no, my_login_property)
    my_login_property.p_no = my_login_property.p_no + 1
    
    print()
    print('-- 信用 新規建 可能額 の照会 -------------------------------------------------------------')
    json_return = func_kanougaku_shinyou(my_login_property.p_no, my_login_property)
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p13/46 No.10 CLMZanShinkiKanoIjiritu を参照してください。
        
    print("更新日時= ", json_return.get("sSummaryUpdate"))           # 更新日時
    print("信用新規建可能額= ", json_return.get("sSummarySinyouSinkidate"))  # 信用新規建可能額
    print("委託保証金率= ", json_return.get("sItakuhosyoukin"))            # 委託保証金率

    print()    
    print('p_errno', json_return.get('p_errno'))
    print('p_err', json_return.get('p_err'))
    # 仮想URLが無効になっている場合
    if json_return.get('p_errno') == '2':
        print()    
        print("仮想URLが有効ではありません。")
        print("電話認証＋e_api_login_tel.py実行")
        print("を再度実行してください。")
        
    print()    
    print()    
    # "p_no"を保存する。
    func_save_p_no(fname_info_p_no, my_login_property.p_no)
       


