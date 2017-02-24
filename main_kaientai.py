# -*- coding: utf-8 -*-
u"""Webスクレイピング用のコード
対象サイト: 介援隊
"""
import os
import re
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
# My library
from logmessage import logprint
import scraping
import textfile
import csvfile
import requests_scraper

URL = 'https://www.kaientai.cc/Default.aspx'

LOGIN_DICT = {
    'login_id': 'general-h',
    'login_id_name': 'ctl00$MainContent$txtID',
    'password': '101968',
    'password_name': 'ctl00$MainContent$txtPSW',
    'submit_path': '//input[@id="MainContent_btnLogin"]'
}

# csvファイルを格納するディレクトリ
CSV_DIR = './kaientai/'

# 結果を格納するディレクトリ
RESULT_DIR = 'kaientai-result'

# イメージを格納するディレクトリ
IMAGE_DIR = 'kaientai-image'

# アイコンを格納するディレクトリ
ICON_DIR = 'kaientai-icon'

# カテゴリ名保存用ファイル名
CATEGORY_FILE_NAME = 'category.txt'

# プロダクトURL保存用ファイル名
PRODUCT_URL_FILE_NAME = 'product_url.txt'
# 処理済みプロダクト格納用ファイル
COMPLETE_PRODUCT_FILE_NAME = 'complete_product.txt'

def make_header_list():
    u"""csvファイル用のヘッダーを作成する。
    """
    header_list = [
        'ID', '卸CD', 'サブCD', 'カテゴリ1', 'カテゴリ2',
        'カテゴリ3', '品名1', '品名2', '品名3', '型番',
        'メーカー名', '税抜価格', '仕切価', '掛率', '販売価',
        '項目選択肢1', '項目1', '項目選択肢2', '項目2', '項目選択肢3',
        '項目3', '項目選択肢4', '項目4', '項目選択肢5', '項目5',
        '販売単位', 'JAN', 'キャッチ1', 'キャッチ2', 'キャッチ3',
        '商品説明', '販売説明', '商品補足', '商品仕様1', '商品仕様2',
        '商品仕様3', '商品仕様4', '商品仕様5', '商品画像1', '商品画像2',
        '商品画像3', '商品画像4', '商品画像5', '商品画像6', '販売説明画像1',
        '販売説明画像2', '販売説明画像3', '送料', '別途送料', '価格制限定価',
        '価格制限下限', '廃盤・中止', '組立用品', '取寄商品', '受注生産',
        '設置費別途', '一般', '管理', '高度', '特管',
        '医薬部外品', '医療用医薬品', '第１類医薬品', '第２類医薬品', '第３類医薬品',
        '在庫商品', '返品不可', '送料無料', 'その他1', 'その他2',
        'その他3', 'その他4', 'その他5', 'その他6', 'その他7',
        'その他8', 'その他9', '備考1', '備考2', '備考3',
        '備考4', '備考5', '出力フラグ', '保護フラグ1', '登録日',
        '最終更新日'
    ]

    return header_list


if __name__ == '__main__':
    # CSVファイルのヘッダー作成
    HEADER_LIST = make_header_list()
    CSVFILE = csvfile.Csvfile(CSV_DIR, HEADER_LIST)

    # カテゴリ名保存用ファイル
    CATEGORY_LIST = []
    CATEGORY_OBJ = textfile.TextFile(RESULT_DIR, CATEGORY_FILE_NAME)
    CATEGORY_GET_RESULT = {}
    # プロダクトURL保存用ファイル
    PRODUCT_URL = []
    PRODUCT_URL_OBJ = textfile.TextFile(RESULT_DIR, PRODUCT_URL_FILE_NAME)
    # 処理済みプロダクト格納用ファイル
    COMPLETE_PRODUCT = []
    COMPLETE_OBJ = textfile.TextFile(RESULT_DIR, COMPLETE_PRODUCT_FILE_NAME)

    # RequestsScraperクラスの初期化
    USER_AGENT = (
        "Mozilla/5.0 (X11; Linux x86_64)"
        "AppleWebKit/537.36 (KHTML, like Gecko)"
        "Chrome/55.0.2883.87 Safari/537.36")
    REQUESTS = requests_scraper.RequestsScraper(user_agent=USER_AGENT)

    # Sanwachannelクラスの初期化
    SCRAPING = scraping.Scraping(URL)

    # ログイン処理
    CURRENT_PAGE = SCRAPING.get_page()
    SCRAPING.execute_login(LOGIN_DICT)

    # カテゴリファイルがあるかを判定する。
    if os.path.isfile(RESULT_DIR + '/' + CATEGORY_FILE_NAME):
        # カテゴリファイルがあれば

        # * カテゴリファイルを読み込みカテゴリリストに格納する。
        logprint('カテゴリをファイルから読み込みます。')
        CATEGORY_FILE = CATEGORY_OBJ.open_read_mode()

        for line in CATEGORY_FILE:
            if not line.startswith("#"):
                if line != "\n":
                    line_strip = line.strip()
                    line_list = line_strip.split(",")
                    CATEGORY_LIST.append(line_list)

        logprint("CATEGORYの長さ:" + str(len(CATEGORY_LIST)))
        CATEGORY_FILE.close()

    # カテゴリリストの長さが0だったら
    if len(CATEGORY_LIST) == 0:
        # * サイトからカテゴリを取得して

        # カテゴリ名格納ファイルを書き込み用にオープンする。
        CATEGORY_FILE = CATEGORY_OBJ.open_append_mode()
        logprint('カテゴリをサイトから読み込みます。')

        # カテゴリ毎のリンクを取得する。
        XPATH = "//a[@href]"
        ATTRIBUTE = "href"
        PATTERN = "https://www.kaientai.cc/listword.aspx?ccd="
        CATEGORY_LINKS = SCRAPING.get_link_and_text_list(XPATH, ATTRIBUTE, PATTERN)

        for link in CATEGORY_LINKS:
            # * カテゴリリストに格納する。
            CATEGORY_LIST.append([link[0], link[1]])

            # * カテゴリファイルに格納する。
            CATEGORY_FILE.write(link[0] + "," + link[1] + '\n')

        # プログラムの初回はcategory.txtを作成して終了する。
        exit()

    # * カテゴリ取得結果ディクショナリを作成する。
    for link in CATEGORY_LIST:
        CATEGORY_GET_RESULT[link[1]] = False

    # URLファイルがあるか判定する。
    if os.path.isfile(RESULT_DIR + '/' + PRODUCT_URL_FILE_NAME):
        # URLファイルがあればURLファイルからURLを読み込む
        logprint('商品のURLをファイルから読み込みます。')
        PRODUCT_URL_FILE = PRODUCT_URL_OBJ.open_read_mode()

        for line in PRODUCT_URL_FILE:
            if line.startswith("#"):
                pass
            elif line == '\n':
                pass
            else:
                line_list = line.split(',')

                # * URLリストに格納する。
                PRODUCT_URL.append(line_list[0] + ',' + line_list[1].strip())

                # * カテゴリ取得結果ディクショナリを更新する。
                CATEGORY_GET_RESULT[line_list[1].strip()] = True

        PRODUCT_URL_FILE.close()

    # カテゴリ取得結果ディクショナリとカテゴリリストをもとにURLを取得する。
    # カテゴリ名格納ファイルを書き込み用にオープンする。
    PRODUCT_URL_FILE = PRODUCT_URL_OBJ.open_append_mode()
    logprint('商品のURLをページから読み込みます。')

    # カテゴリリンクでループ
    for category_link in CATEGORY_LIST:
        if CATEGORY_GET_RESULT[category_link[1]] is True:
            continue

        logprint(category_link[0] + ":" + category_link[1])
        category_page = SCRAPING.get_page(category_link[0])
        CURRENT_PAGE = category_page
        lbl_count = SCRAPING.get_text_by_xpath(category_page, '//span[@id="MainContent_lblCount"]')
        logprint(lbl_count + "件の商品が見つかりました。")

        # アクティブな要素がなくなるまでループする
        active_element_xpath = "//span[@class='m_pager_active']"

        # 取得したURLをURLファイルに格納する。
        url_count = 0
        while True:
            # 商品のwebcdを取得する。1ページにつき10個の商品
            webcd_list = SCRAPING.get_attribute_list_by_xpath('//div[@id="title"]/h2/a', 'href')
            for webcd in webcd_list:
                product_record = webcd + ',' + category_link[1]

                PRODUCT_URL_FILE.write(product_record + '\n')
                PRODUCT_URL.append(product_record)

                url_count += 1

            # アクティブな要素の次の要素をクリック
            next_link = SCRAPING.get_next_link(active_element_xpath)

            # whileループの終了条件
            # シューズカテゴリの590ページの次へをクリックすると
            # 「'/'アプリケーションでサーバー　エラーが発生しました。」
            # エラーが発生するので next_linkがNoneだったらwhileループを
            # 抜ける
            # 歩行関連 -> シューズ 9,631件中5,900件
            # 住宅改修 -> 上がりかまち手すりまで確認
            if (next_link is None) or (next_link.text == '>>'):
                break

            # クリック前のページ
            old_page = None
            try:
                old_page = category_page.find_element_by_tag_name('html')
            except NoSuchElementException:
                pass
            except WebDriverException:
                pass

            SCRAPING.execute_link_click_by_element(next_link)

            if old_page is not None:
                # クリック前のページが古くなるまで待つ
                WebDriverWait(category_page, 30).until(staleness_of(old_page))

        logprint(str(url_count) + '件の商品のURLを保存しました。')

    # 処理済みのファイルを読み込む
    COMPLETE_FILE = COMPLETE_OBJ.open_read_mode()
    if COMPLETE_FILE is not None:
        for line in COMPLETE_FILE:
            if line != "\n":
                COMPLETE_PRODUCT.append(line.strip())

        COMPLETE_FILE.close()

    # 商品情報を取得してCSVファイルに書き込む。
    COMPLETE_FILE = COMPLETE_OBJ.open_append_mode()
    for product_row in PRODUCT_URL:

        product_line = product_row.split(',')

        product_url = product_line[0]

        product_category = product_line[1]

        # 処理済であれば何もしない
        if product_row in COMPLETE_PRODUCT:
            continue

        product_list = []

        webcd = ''

        # クリック前のページ
        old_detail_page = None
        try:
            old_detail_page = CURRENT_PAGE.find_element_by_tag_name('html')
        except NoSuchElementException:
            pass
        except WebDriverException:
            pass

        # 商品毎のページを取得する。
        product_page = SCRAPING.get_page(product_url)
        logprint(product_page.current_url)
        CURRENT_PAGE = product_page

        if old_detail_page is not None:
            # 前のページが古くなるまで待つ
            WebDriverWait(product_page, 30).until(staleness_of(old_detail_page))

        # ご指定の商品がデータベースにありません。の場合の処理
        try:
            pnl_no_item = product_page.find_element_by_xpath(
                "//div[@id='MainContent_pnlNoItem']"
            )
        except NoSuchElementException:
            pass
        except WebDriverException:
            pass
        else:
            logprint(product_url + 'がデータベースにないためスキップします。')
            continue

        # ログインされているかのチェック。仕切価があるかを確認する。
        try:
            cost_text = product_page.find_element_by_xpath(
                "//span[@id='MainContent_lblCost']"
            ).text
        except NoSuchElementException:
            # ログイン処理
            CURRENT_PAGE = SCRAPING.get_page()
            SCRAPING.execute_login(LOGIN_DICT)
            # クリック前のページ
            old_detail_page = CURRENT_PAGE.find_element_by_tag_name('html')

            # 商品毎のページを取得する。
            product_page = SCRAPING.get_page(product_url)
            logprint(product_page.current_url)
            CURRENT_PAGE = product_page

            # 前のページが古くなるまで待つ
            WebDriverWait(product_page, 30).until(staleness_of(old_detail_page))
        except WebDriverException:
            pass
        else:
            logprint(cost_text)
            if cost_text == '':
                # ログイン処理
                CURRENT_PAGE = SCRAPING.get_page()
                SCRAPING.execute_login(LOGIN_DICT)
                # クリック前のページ
                old_detail_page = CURRENT_PAGE.find_element_by_tag_name('html')

                # 商品毎のページを取得する。
                product_page = SCRAPING.get_page(product_url)
                logprint(product_page.current_url)
                CURRENT_PAGE = product_page

                # 前のページが古くなるまで待つ
                WebDriverWait(product_page, 30).until(staleness_of(old_detail_page))


        # 01 ID: URLに表示されるwebcdを取得
        webcd_search = re.search(r"\d+", product_url)
        webcd = webcd_search.group()
        product_list.extend([webcd])

        # 02 卸CD: デフォルトで、以下テキストを挿入 『ket』
        product_list.extend(['ket'])

        # 03 サブCD: 空欄
        product_list.extend([''])

        # 04 カテゴリ1: パンクズリストのトップページ > の次のカテゴリ
        try:
            lbl_category = product_page.find_elements_by_xpath(
                "//span[@id='MainContent_lblCategory']/a"
            )
        except WebDriverException:
            pass

        if len(lbl_category) > 1:
            product_list.extend([lbl_category[1].get_attribute('innerHTML')])
        else:
            product_list.extend([''])

        # 05 カテゴリ2:
        # パンクズリストのトップページ > 入浴関連 > の次のカテゴリ
        if len(lbl_category) > 2:
            product_list.extend([lbl_category[2].get_attribute('innerHTML')])
        else:
            product_list.extend([''])

        # 06 カテゴリ3: 空欄
        product_list.extend([''])

        # 07 品名1: 商品名に該当するもの全て
        try:
            lbl_goods_name = product_page.find_element_by_xpath(
                "//span[@id='MainContent_lblGoodsName']"
            ).get_attribute('innerHTML')
            lbl_goods_name = lbl_goods_name.replace('&amp;', '&')
        except NoSuchElementException:
            lbl_goods_name = ''
        except WebDriverException:
            lbl_goods_name = ''
        else:
            pass

        product_list.extend([lbl_goods_name])

        # 08 品名2: 空欄
        product_list.extend([''])

        # 09 品名3: 空欄
        product_list.extend([''])

        # 10 型番: 商品名の/ 以降次のスペースで区切られたもの
        # 移乗サポート台 https://www.kaientai.cc/goods.aspx?webcd=257442 の
        # 型番は0002である。excelで開くと2になっているがcsv上は0002になっている。
        model_number_split = lbl_goods_name.split('/')
        if len(model_number_split) > 1:
            model_number = model_number_split[1].split('　')[0].strip()
            product_list.extend([model_number])
        else:
            product_list.extend([''])

        # 11 メーカー名: メーカー名で表示されたもの
        try:
            maker_name = product_page.find_element_by_xpath(
                "//span[@id='MainContent_lblMakerName']/a"
            ).text

        except NoSuchElementException:
            maker_name = ''
        except WebDriverException:
            maker_name = ''
        else:
            pass

        product_list.extend([maker_name])

        # 12 税抜価格: 小売価格で表示されたもの数字のみ
        try:
            price_text = product_page.find_element_by_xpath(
                "//span[@id='MainContent_lblPrice']"
            ).text

        except NoSuchElementException:
            price_text = ''
        except WebDriverException:
            price_text = ''
        else:
            pass

        decimal_search = re.findall(r"\d+", price_text)

        if len(decimal_search) == 0:
            decimal_search = [price_text]

        price = ''
        for decimal in decimal_search:
            price += decimal

        product_list.extend([price])

        # 13 仕切価: 卸売価格で表示されたもの 数字のみ
        try:
            cost_text = product_page.find_element_by_xpath(
                "//span[@id='MainContent_lblCost']"
            ).text

        except NoSuchElementException:
            cost_text = ''
        except WebDriverException:
            cost_text = ''
        else:
            pass

        # この商品はお見積り商品になりますの場合の処理
        if cost_text.startswith('この商品は'):
            cost_text = cost_text.split('（')[0]
            product_list.extend([cost_text])
        # お問い合わせくださいの場合の処理
        elif cost_text.startswith('お問い合わせ'):
            cost_text = cost_text.split('（')[0]
            product_list.extend([cost_text])
        # 卸売価格が表示されている場合の処理
        elif '円' in cost_text:
            cost_text = cost_text.split('円')[0]
            decimal_search = re.findall(r"\d+", cost_text)
            cost = ''
            for decimal in decimal_search:
                cost += decimal
            product_list.extend([cost])

        # 卸売価格がない場合の処理
        else:
            product_list.extend([''])

        # 14 掛率: 空欄
        product_list.extend([''])

        # 15 販売価: 空欄
        product_list.extend([''])

        # 16 項目選択肢1: カラーやサイズなど選択項目がある場合の項目名
        # ラベルを取得する。
        label = ''
        try:
            label = product_page.find_element_by_xpath(
                "//span[@id='MainContent_lbl属性1']"
            ).text
        except NoSuchElementException:
            pass
        except WebDriverException:
            pass

        product_list.extend([label.replace('：', '')])

        # 17 項目1: 選択項目のリスト表示されたもの半角スペースで区切って表示
        # オプションを取得する。
        option_list = []
        try:
            option_list = product_page.find_elements_by_xpath(
                "//select[@name='ctl00$MainContent$ddl属性1']/option"
            )
        except WebDriverException:
            pass

        option_text = ''
        for option in option_list:
            if len(option_text) == 0:
                option_text = option.text
            else:
                option_text += ' ' + option.text

        product_list.extend([option_text])

        # 18 項目選択肢2: 選択項目が複数ある場合（2個め）
        # ラベルを取得する。
        label = ''
        try:
            label = product_page.find_element_by_xpath(
                "//span[@id='MainContent_lbl属性2']"
            ).text
        except NoSuchElementException:
            pass
        except WebDriverException:
            pass

        product_list.extend([label.replace('：', '')])

        # 19 項目2: 選択項目のリスト表示されたもの半角スペースで区切って表示
        # オプションを取得する。
        option_list = []
        try:
            option_list = product_page.find_elements_by_xpath(
                "//select[@name='ctl00$MainContent$ddl属性2']/option"
            )
        except WebDriverException:
            pass

        option_text = ''
        for option in option_list:
            if len(option_text) == 0:
                option_text = option.text
            else:
                option_text += ' ' + option.text

        product_list.extend([option_text])

        # 20 項目選択肢3: 選択項目が複数ある場合（3個め）
        # ラベルを取得する。
        label = ''
        try:
            label = product_page.find_element_by_xpath(
                "//span[@id='MainContent_lbl属性3']"
            ).text
        except NoSuchElementException:
            pass
        except WebDriverException:
            pass

        product_list.extend([label.replace('：', '')])

        # 21 項目3: 選択項目のリスト表示されたもの半角スペースで区切って表示
        # オプションを取得する。
        option_list = []
        try:
            option_list = product_page.find_elements_by_xpath(
                "//select[@name='ctl00$MainContent$ddl属性3']/option"
            )
        except WebDriverException:
            pass

        option_text = ''
        for option in option_list:
            if len(option_text) == 0:
                option_text = option.text
            else:
                option_text += ' ' + option.text

        product_list.extend([option_text])

        # 22 項目選択肢4: 空欄
        product_list.extend([''])

        # 23 項目4: 空欄
        product_list.extend([''])

        # 24 項目選択肢5: 空欄
        product_list.extend([''])

        # 25 項目5: 空欄
        product_list.extend([''])

        # 26 販売単位: 数量の入力ボックス右に表示される単位
        try:
            lbl_unit = product_page.find_element_by_xpath("//span[@id='MainContent_lblUnit']").text
        except NoSuchElementException:
            lbl_unit = ''
        except WebDriverException:
            lbl_unit = ''
        else:
            pass

        product_list.extend([lbl_unit])

        # 27 JAN: JANコード
        try:
            jancd = product_page.find_element_by_xpath("//span[@id='MainContent_lblJANCD']").text
        except NoSuchElementException:
            jancd = ''
        except WebDriverException:
            jancd = ''
        else:
            pass

        product_list.extend([jancd])

        # 28 キャッチ1: 空欄
        product_list.extend([''])

        # 29 キャッチ2: 空欄
        product_list.extend([''])

        # 30 キャッチ3: 空欄
        product_list.extend([''])

        # 31 商品説明: 商品の説明欄に記載の内容
        #              タグは含むが、<span>タグは削除
        # 注意: r-commmentのmは3つ
        try:
            r_comment = product_page.find_element_by_xpath(
                "//div[@id='r-commment']/p"
            ).get_attribute('outerHTML')

            comment = product_page.find_element_by_xpath(
                "//span[@id='MainContent_lblComment']"
            ).get_attribute('innerHTML')

        except NoSuchElementException:
            r_comment = ''
            comment = ''
        except WebDriverException:
            r_comment = ''
            comment = ''
        else:
            pass

        if len(comment) != 0:
            product_list.extend([r_comment + '\n' + comment])
        else:
            product_list.extend([''])

        # 32 販売説明: デフォルトで、以下テキストを挿入
        # 『※商品の中には一部倉庫からの取り寄せ商品もございます。
        # 取り寄せの場合、お届けまで通常1週間～10日ほどかかります。
        # また、ご注文のタイミングによって売切れとなる場合もございますので、
        # ご注文前にお問い合わせください。』
        product_list.extend([
            '※商品の中には一部倉庫からの取り寄せ商品もございます。' +
            '取り寄せの場合、お届けまで通常1週間～10日ほどかかります。' +
            'また、ご注文のタイミングによって売切れとなる場合もござい' +
            'ますので、' + 'ご注文前にお問い合わせください。'])

        # 33 商品補足: 空欄
        product_list.extend([''])

        # 34 商品仕様1: 商品の仕様欄に記載の内容
        #               タグは含むが、<span>タグは削除
        try:
            r_spec = product_page.find_element_by_xpath(
                "//div[@id='r-spec']/p"
            ).get_attribute('outerHTML')

            spec = product_page.find_element_by_xpath(
                "//span[@id='MainContent_lblSpec']"
            ).get_attribute('innerHTML')

        except NoSuchElementException:
            r_spec = ''
            spec = ''
        except WebDriverException:
            r_spec = ''
            spec = ''
        else:
            pass

        if len(spec) != 0:
            product_list.extend([r_spec + '\n' + spec])
        else:
            product_list.extend([''])

        # 35 商品仕様2: 空欄
        product_list.extend([''])

        # 36 商品仕様3: 空欄
        product_list.extend([''])

        # 37 商品仕様4: 空欄
        product_list.extend([''])

        # 38 商品仕様5: 空欄
        product_list.extend([''])

        # 商品画像
        up_image_list = SCRAPING.get_attribute_list_by_xpath(
            "//div[@id='up']/img", 'src'
        )
        image_name_list = []
        for up_image in up_image_list:
            image_name_search = re.search(r"[\da-zA-Z_-]+.jpg", up_image)
            if image_name_search is not None:
                image_name = image_name_search.group()
                image_name_list.append([up_image, image_name])

        # 39 商品画像1: 卸CD＋『-』＋ID＋『.jpg』 画像がない場合はブランク
        if len(image_name_list) > 0:
            image_name0 = 'ket-' + webcd + '.jpg'
            product_list.extend([image_name0])

            # 画像を保存する。
            url = image_name_list[0][0]
            referer = product_page.current_url
            path = IMAGE_DIR + '/' + image_name0
            response = REQUESTS.fetch_image(url, path, referer)

        else:
            product_list.extend([''])

        # 40 商品画像2: 卸CD＋『-』＋ID＋『_1.jpg』 画像がない場合はブランク
        if len(image_name_list) > 1:
            image_name1 = 'ket-' + webcd + '_1.jpg'
            product_list.extend([image_name1])

            # 画像を保存する。
            url = image_name_list[1][0]
            referer = product_page.current_url
            path = IMAGE_DIR + '/' + image_name1
            response = REQUESTS.fetch_image(url, path, referer)

        else:
            product_list.extend([''])

        # 41 商品画像3: 卸CD＋『-』＋ID＋『_2.jpg』 画像がない場合はブランク
        if len(image_name_list) > 2:
            image_name2 = 'ket-' + webcd + '_2.jpg'
            product_list.extend([image_name2])

            # 画像を保存する。
            url = image_name_list[2][0]
            referer = product_page.current_url
            path = IMAGE_DIR + '/' + image_name2
            response = REQUESTS.fetch_image(url, path, referer)

        else:
            product_list.extend([''])

        # 42 商品画像4: 卸CD＋『-』＋ID＋『_3.jpg』 画像がない場合はブランク
        if len(image_name_list) > 3:
            image_name3 = 'ket-' + webcd + '_3.jpg'
            product_list.extend([image_name3])

            # 画像を保存する。
            url = image_name_list[3][0]
            referer = product_page.current_url
            path = IMAGE_DIR + '/' + image_name3
            response = REQUESTS.fetch_image(url, path, referer)

        else:
            product_list.extend([''])

        # 43 商品画像5: 卸CD＋『-』＋ID＋『_4.jpg』 画像がない場合はブランク
        if len(image_name_list) > 4:
            image_name4 = 'ket-' + webcd + '_4.jpg'
            product_list.extend([image_name4])

            # 画像を保存する。
            url = image_name_list[4][0]
            referer = product_page.current_url
            path = IMAGE_DIR + '/' + image_name4
            response = REQUESTS.fetch_image(url, path, referer)

        else:
            product_list.extend([''])

        # 44 商品画像6: 卸CD＋『-』＋ID＋『_5.jpg』 画像がない場合はブランク
        if len(image_name_list) > 5:
            image_name5 = 'ket-' + webcd + '_5.jpg'
            product_list.extend([image_name5])

            # 画像を保存する。
            url = image_name_list[5][0]
            referer = product_page.current_url
            path = IMAGE_DIR + '/' + image_name5
            response = REQUESTS.fetch_image(url, path, referer)

        else:
            product_list.extend([''])

        # 45 販売説明画像1: 空欄
        product_list.extend([''])

        # 46 販売説明画像2: 空欄
        product_list.extend([''])

        # 47 販売説明画像3: 空欄
        product_list.extend([''])

        # 48 送料: 空欄
        product_list.extend([''])

        # アイコン画像
        icon_image_list = SCRAPING.get_attribute_list_by_xpath(
            "//div[@id='r-icon']/img", 'src'
        )
        icon_image_name_list = []
        icon_name_list = []
        icon_url_list = []
        for icon_image in icon_image_list:
            icon_name_search = re.search(r"[\da-zA-Z_-]+.png", icon_image)
            if icon_name_search is not None:
                icon_name = icon_name_search.group()
                icon_image_name_list.append([icon_image, icon_name])
                icon_name_list.append(icon_name)
                icon_url_list.append(icon_image)

        # 49 別途送料: アイコン欄に、icon_03.pngがある場合に『1』をセット
        if 'icon_03.png' in icon_name_list:
            product_list.extend(['1'])
        else:
            product_list.extend([''])

        # 50 価格制限定価: 空欄
        product_list.extend([''])

        # 51 価格制限下限: 空欄
        product_list.extend([''])

        # 52 廃盤・中止: 空欄
        product_list.extend([''])

        # 53 組立用品: 空欄
        product_list.extend([''])

        # 54 取寄商品: アイコン欄に、icon_06.pngがある場合に『1』をセット
        if 'icon_06.png' in icon_name_list:
            product_list.extend(['1'])
        else:
            product_list.extend([''])


        # 55 受注生産: 空欄
        product_list.extend([''])

        # 56 設置費別途: 空欄
        product_list.extend([''])

        # 57 一般: 空欄
        product_list.extend([''])

        # 58 管理: 空欄
        product_list.extend([''])

        # 59 高度: 空欄
        product_list.extend([''])

        # 60 特管: 空欄
        product_list.extend([''])

        # 61 医薬部外品: 空欄
        product_list.extend([''])

        # 62 医療用医薬品: 空欄
        product_list.extend([''])

        # 63 第１類医薬品: 空欄
        product_list.extend([''])

        # 64 第２類医薬品: 空欄
        product_list.extend([''])

        # 65 第３類医薬品: 空欄
        product_list.extend([''])

        # 66 在庫商品: 空欄
        product_list.extend([''])

        # 67 返品不可: 空欄
        product_list.extend([''])

        # 68 送料無料: 空欄
        product_list.extend([''])

        # 69 その他1: アイコン欄のアイコン名称
        if len(icon_image_name_list) > 0:
            icon_name0 = icon_image_name_list[0][1]
            product_list.extend([icon_name0])

            # アイコンを保存する。
            url = icon_image_name_list[0][0]
            referer = product_page.current_url
            path = ICON_DIR + '/' + icon_name0
            response = REQUESTS.fetch_image(url, path, referer)

        else:
            product_list.extend([''])

        # 70 その他2: アイコン欄のアイコン名称
        if len(icon_image_name_list) > 1:
            icon_name1 = icon_image_name_list[1][1]
            product_list.extend([icon_name1])

            # アイコンを保存する。
            url = icon_image_name_list[1][0]
            referer = product_page.current_url
            path = ICON_DIR + '/' + icon_name1
            response = REQUESTS.fetch_image(url, path, referer)

        else:
            product_list.extend([''])

        # 71 その他3: アイコン欄のアイコン名称
        if len(icon_image_name_list) > 2:
            icon_name2 = icon_image_name_list[2][1]
            product_list.extend([icon_name2])

            # アイコンを保存する。
            url = icon_image_name_list[2][0]
            referer = product_page.current_url
            path = ICON_DIR + '/' + icon_name2
            response = REQUESTS.fetch_image(url, path, referer)

        else:
            product_list.extend([''])

        # 72 その他4: アイコン欄のアイコン名称
        if len(icon_image_name_list) > 3:
            icon_name3 = icon_image_name_list[3][1]
            product_list.extend([icon_name3])

            # アイコンを保存する。
            url = icon_image_name_list[3][0]
            referer = product_page.current_url
            path = ICON_DIR + '/' + icon_name3
            response = REQUESTS.fetch_image(url, path, referer)

        else:
            product_list.extend([''])

        # 73 その他5: アイコン欄のアイコン名称
        if len(icon_image_name_list) > 4:
            icon_name4 = icon_image_name_list[4][1]
            product_list.extend([icon_name4])

            # アイコンを保存する。
            url = icon_image_name_list[4][0]
            referer = product_page.current_url
            path = ICON_DIR + '/' + icon_name4
            response = REQUESTS.fetch_image(url, path, referer)

        else:
            product_list.extend([''])

        # 74 その他6: アイコン欄のアイコン名称
        if len(icon_image_name_list) > 5:
            icon_name5 = icon_image_name_list[5][1]
            product_list.extend([icon_name5])

            # アイコンを保存する。
            url = icon_image_name_list[5][0]
            referer = product_page.current_url
            path = ICON_DIR + '/' + icon_name4
            response = REQUESTS.fetch_image(url, path, referer)

        else:
            product_list.extend([''])

        # 75 その他7: アイコン欄のアイコン名称
        if len(icon_image_name_list) > 6:
            icon_name6 = icon_image_name_list[6][1]
            product_list.extend([icon_name6])

            # アイコンを保存する。
            url = icon_image_name_list[6][0]
            referer = product_page.current_url
            path = ICON_DIR + '/' + icon_name6
            response = REQUESTS.fetch_image(url, path, referer)

        else:
            product_list.extend([''])

        # 76 その他8: アイコン欄のアイコン名称
        if len(icon_image_name_list) > 7:
            icon_name7 = icon_image_name_list[7][1]
            product_list.extend([icon_name7])

            # アイコンを保存する。
            url = icon_image_name_list[7][0]
            referer = product_page.current_url
            path = ICON_DIR + '/' + icon_name7
            response = REQUESTS.fetch_image(url, path, referer)

        else:
            product_list.extend([''])

        # 77 その他9: アイコン欄のアイコン名称
        if len(icon_image_name_list) > 8:
            icon_name8 = icon_image_name_list[8][1]
            product_list.extend([icon_name8])

            # アイコンを保存する。
            url = icon_image_name_list[8][0]
            referer = product_page.current_url
            path = ICON_DIR + '/' + icon_name8
            response = REQUESTS.fetch_image(url, path, referer)

        else:
            product_list.extend([''])

        # 78 備考1: 同一カテゴリー商品のWEBCD
        # 複数ある場合は半角スペースで区切る
        category_list = []
        try:
            r_category_list = product_page.find_elements_by_xpath(
                "//div[@id='r-category']/table/tbody/tr/td[@class='Name']/a"
            )
        except WebDriverException:
            pass

        for r_category in r_category_list:
            category_list.append(r_category.get_attribute('href'))

        category_webcd = ''
        for category in category_list:
            category_search = re.search(r"\d+", category)
            category_cd = category_search.group()
            if len(category_webcd) == 0:
                category_webcd = category_cd
            else:
                category_webcd += ' ' + category_cd

        product_list.extend([category_webcd])

        # 79 備考2: 空欄
        product_list.extend([''])

        # 80 備考3: 空欄
        product_list.extend([''])

        # 81 備考4: 空欄
        product_list.extend([''])

        # 82 備考5: 空欄
        product_list.extend([''])

        # 83 出力フラグ: 空欄
        product_list.extend([''])

        # 84 保護フラグ1: 空欄
        product_list.extend([''])

        # 85 登録日: 空欄
        product_list.extend([''])

        # 86 最終更新日: YYYYMMDD クローリング実行日
        today = datetime.now()
        product_list.extend([str(today.year) + '/' + str(today.month) + '/' + str(today.day)])

        CSVFILE.writerow(product_list)

        COMPLETE_FILE.write(product_url + ',' + product_category + '\n')

    COMPLETE_FILE.close()

    logprint('全部で' + str(str(len(PRODUCT_URL))) + '件の商品のURLを保存しました。')

    logprint('商品情報の取得を終了します。')
