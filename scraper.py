# -*- coding: utf-8 -*-
u"""スクレイピング用のライブラリ
"""
import os
import time
from urllib.error import HTTPError
from urllib.error import URLError
from http.client import RemoteDisconnected
import unittest
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# My library
from logmessage import logprint


class Scraper():
    """
    Scrapingクラス
    メソッド:
        * __init__(self, base_url):
        * get_page(self, url=None):
        * execute_login(self, login_dict, driver=None):
        * get_elements_by_xpath(self, xpath, driver=None):
        * get_text_by_xpath(xpath, driver=None):
        * get_attribute_list_by_xpath(self, xpath, attribute, driver=None):
        * get_link_and_text_list(self, xpath, attribute, pattern, driver=None):
        * get_next_link(self, xpath):
        * execute_link_click_by_element(self, element):
        * execute_link_click_by_xpath(self, xpath):
        * execute_search(self, input_list, submit_path):
        * is_link_enable(self, link_text):
        * get_table_row(self, xpath):
        * get_next_page(self, link_text):
        * get_product_link(self, product_pattern):
        * get_absolute_url(self, source):
        @staticmethod
        * get_select_list_by_xpath(driver, xpath):
        * get_links(self, url, link_pattern, xpath):
        @staticmethod
        * get_product_url(row, link_text):
    """
    def __init__(self, base_url):
        """
        目的: phantomJSのドライバーを取得する。
        引数:
            * base_url: トップページのURL
        動作:
            * OSを判定してLinux版のバイナリとWindows版のバイナリを選択する
            * バイナリの置き場所はlibの下
            * リクエストヘッダのAcceptとUser-Agentを設定する
        設定:
            * self.page_list:
            * self.product_page_list:
            * self.base_url: トップページ
            * self.driver:
        戻り値:
            * driver: phantomJSのドライバー
            * None: ドライバーの取得に失敗した場合
        """

        self.page_list = []
        self.product_page_list = []

        self.base_url = base_url

        dcap = DesiredCapabilities.PHANTOMJS
        dcap['phantomjs.page.settings.accept'] = (
            'text/html,application/xhtml+xml,application/xml;'
            'q=0.9,image/webp,*/*;q=0.8'
        )
        dcap['phantomjs.page.customHeaders.2'] = (
            'text/html,application/xhtml+xml,application/xml;'
            'q=0.9,image/webp,*/*;q=0.8'
        )

        ua_value = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)'
                    'AppleWebKit 537.36 (KHTML, like Gecko) Chrome')
        dcap['phantomjs.page.settings.userAgent'] = ua_value
        dcap['phantomjs.page.customHeaders.User-Agent'] = ua_value

        try:
            if os.name == 'posix':
                self.driver = webdriver.PhantomJS(
                    executable_path='lib/phantomjs',
                    desired_capabilities=dcap)
            elif os.name == 'nt':
                self.driver = webdriver.PhantomJS(
                    executable_path='lib/phantomjs.exe',
                    desired_capabilities=dcap)
            else:
                logprint('Unsupported OS')

        except URLError as error_code:
            logprint('ドライバーの取得に失敗しました。')
            logprint(error_code)
        except WebDriverException as error_code:
            logprint('PhantomJSのサービスとの接続に失敗しました。')
            logprint('libディレクトリにPhantomJSの実行ファイルが必要です。')


    def get_page(self, url=None):
        """
        目的: urlを受け取りページを取得する。
        引数:
            * url: 取得するページのURL
            * None: 引数にurlがなかったらbase_urlを設定する
        戻り値:
            * self.driver: ベージのドライバー
            * None: 例外が発生した場合はNoneを返す
        """
        if url is None:
            url = self.base_url

        try:
            old_page = self.driver.find_element_by_tag_name('html')
            self.driver.get(url)
        except HTTPError as error_code:
            logprint(url)
            logprint(error_code)
            return None
        except URLError as error_code:
            logprint("The server could not be found!")
            logprint(error_code)
            return None
        except RemoteDisconnected as error_code:
            logprint("Error! RemoteDisconnected")
            logprint(error_code)
            return None
        except WebDriverException as error_code:
            logprint("Error! WebDriverException")
            logprint(error_code)
            return None

        # リクエストヘッダを確認するときのコード
        # cap_dict = self.driver.desired_capabilities
        # key = 'phantomjs.page.settings.userAgent'
        # print('%s: %s' % (key, cap_dict[key]))
        # key = 'phantomjs.page.settings.accept'
        # print('%s: %s' % (key, cap_dict[key]))
        # print(self.driver.current_url)

        try:
            WebDriverWait(self.driver, 30).until(
                EC.staleness_of(old_page)
                )
        except TimeoutException as error_code:
            logprint("Error! TimeoutException")
            logprint(error_code)
            return None

        return self.driver

    def execute_login(self, login_dict, driver=None):
        """
        目的: ログインを実行する。
        引数:
            * driver: Seleniumのドライバー
            * login_dict
                login_dict = {
                    'login_id': "general-h",
                    'login_id_name': "ctl00$MainContent$txtID",
                        : IDを入力する<input>タグのname属性の値
                    'password': "101968",
                    'password_name': "ctl00$MainContent$txtPSW",
                        : パスワードを入力する<input>タグのname属性の値
                    'submit_path': "//input[@id='MainContent_btnLogin']"
                        : クリックするHTML要素のXPATH
                }
        戻り値:
            * driver: Seleniumのドライバー
        """
        if driver is None:
            driver = self.driver

        try:
            driver.find_element_by_name(
                login_dict['login_id_name']).send_keys(login_dict['login_id'])
            driver.find_element_by_name(
                login_dict['password_name']).send_keys(login_dict['password'])
            driver.find_element_by_xpath(
                login_dict['submit_path']).click()
        except NoSuchElementException as error_code:
            logprint(error_code)
            logprint('ログインが失敗しました。')
            return None
        else:
            logprint('ログインしています。')

        return driver

    def get_elements_by_xpath(self, xpath, driver=None):
        """
        目的: driverとxpathを受け取りWeb要素をリストで返す。
        引数:
            * xpath: 取得したいWeb要素のxpath
        戻り値:
            * 見つかった時: Web要素のリスト
            * 見つからなかった時: [] 空のリスト
        """
        if driver is None:
            driver = self.driver

        try:
            elements = driver.find_elements_by_xpath(xpath)
        except WebDriverException:
            logprint('Error! WebDriverException')
            return []
        except RemoteDisconnected:
            logprint("Error! RemoteDisconnected")
            return []

        return elements

    def get_text_by_xpath(self, xpath, driver=None):
        """
        目的:
            * XPATHのWeb要素のテキストを返す
            * 要素がしなかったら空文字列を返す。
        引数:
            * xpath: 検索するxpath
        戻り値 :
            * data : xpathに一致したテキスト
            * '' : データが一致しなかった時
        """
        if driver is None:
            driver = self.driver

        try:
            element_text = driver.find_element_by_xpath(xpath).text
        except NoSuchElementException:
            return ''
        except WebDriverException:
            logprint('Error! WebDriverException')
            return ''
        except RemoteDisconnected:
            logprint("Error! RemoteDisconnected")
            return ''

        element_text = bytes(element_text, 'utf-8').decode('utf-8')

        return element_text

    def get_attribute_list_by_xpath(self, xpath, attribute, driver=None):
        """
        目的: XPATHと属性名を受け取り属性の値のリストを返す。
        用例:
            * xpath = "//a[@href]"
            * attribute = "href"
            * self.scraper.get_attribute_list_by_xpath(xpath, attribute)
        引数:
            * xpath: XPATH
            * attribute: 属性名
        戻り値:
            * 結果のリスト
            * 見つからない場合は空のリスト
        """
        if driver is None:
            driver = self.driver

        return_list = []

        # xpathに合致する要素をdata_listに格納する
        try:
            data_list = (driver
                         .find_elements_by_xpath(xpath))
        except NoSuchElementException:
            logprint("NoSuchElementException!")
            return return_list
        except WebDriverException:
            logprint("WebDriverException!")
            return return_list
        except RemoteDisconnected:
            logprint("Error! RemoteDisconnected")
            return return_list

        for data in data_list:
            if data.get_attribute(attribute) is not None:
                return_list.append(data.get_attribute(attribute))

        return return_list

    def get_link_and_text_list(self, xpath, attribute, pattern, driver=None):
        """
        目的: XPATHと属性名を受け取り属性の値のリストを返す。
        用例:
            * xpath = "//a[@href]"
            * attribute = "href"
            * pattern = "http://xxxxx"
            * self.scraper.get_attribute_list_by_xpath(xpath, attribute, pattern)
        引数:
            * xpath: XPATH
            * attribute: 属性名
            * pattern: リンク先アドレスのパターン
        戻り値:
            * 結果のリスト
            * 見つからない場合は空のリスト
        """
        if driver is None:
            driver = self.driver

        return_list = []

        # xpathに合致する要素をdata_listに格納する
        try:
            data_list = driver.find_elements_by_xpath(xpath)
        except NoSuchElementException:
            logprint("NoSuchElementException!")
            return return_list
        except WebDriverException:
            logprint("WebDriverException!")
            return return_list

        for data in data_list:
            if data.get_attribute(attribute).startswith(pattern):
                link_text = data.get_attribute('innerHTML')
                link_text = bytes(link_text, 'utf-8').decode('utf-8')
                return_list.append(
                    [
                        data.get_attribute(attribute),
                        link_text
                    ])

        return return_list

    def get_next_link(self, xpath):
        u"""
        目的: 引数で与えられたxpathの次の要素が存在するかを調べる
        引数:
            * xpath: 調べたい要素のxpath
        戻り値:
            * 存在する場合の次の要素を返す。
            * None - 存在しない場合Noneを返す。
        """
        try:
            next_link = self.driver.find_element_by_xpath(xpath + '/following-sibling::*')
        except NoSuchElementException:
            return None

        return next_link

    def execute_link_click_by_element(self, element):
        u"""リンクをクリックする。
        """
        click_text = element.text
        try:
            element.click()
        except NoSuchElementException as error_code:
            logprint(error_code)
            logprint(click_text + 'のクリックが失敗しました。')
            return None
        else:
            logprint(click_text + 'をクリックしました。')

        return self.driver

    def execute_link_click_by_xpath(self, xpath):
        u"""リンクをクリックする。
        """
        driver = self.driver
        try:
            driver.find_element_by_xpath(xpath).click()
        except NoSuchElementException as error_code:
            logprint(error_code)
            logprint(
                driver.find_element_by_xpath(
                    '//body').get_attribute('outerHTML'))
            logprint(xpath + 'のクリックが失敗しました。')
            return None
        else:
            logprint(xpath + 'をクリックしました。')

        return self.driver

    def execute_search(self, input_list, submit_path):
        u"""リンクをクリックする。
        引数:
            * input_list: [xpath, 値]となっている。
        """
        for value in input_list:
            try:
                element = self.driver.find_element_by_name(value[0])
            except NoSuchElementException:
                logprint(value[0] + 'の指定が間違っています。')
                return None

            if element.get_attribute('type') == 'checkbox':
                if element.is_selected():
                    element.click()
            else:
                element.send_keys(value[1])

        try:
            self.driver.find_element_by_xpath(submit_path).click()
            time.sleep(20)
        except NoSuchElementException:
            logprint('xpathの指定が間違っています。')
            logprint(submit_path)
            return None

        return self.driver

    def is_link_enable(self, link_text):
        u"""
        目的: 引数で与えられたリンクが存在するか
        戻り値:
            * True - 存在する。
            * False - 存在しない。
        """
        try:
            link_exists = self.driver.find_element_by_link_text(
                link_text).is_enabled()
        except NoSuchElementException:
            logprint(link_text + 'は見つかりません。')
            return False
        else:
            return link_exists

    def get_table_row(self, xpath):
        u"""
        目的: 引数で与えられたテーブルの行をリストで返す
        引数:
            * xpath - テーブルのxpath
        戻り値:
            * テーブルの行
        """
        try:
            return_list = self.driver.find_elements_by_xpath(xpath)
        except NoSuchElementException:
            return None
        except WebDriverException:
            return None

        return return_list

    def get_next_page(self, link_text):
        u"""
        目的: 引数で与えられたリンクをクリックする
        引数:
            * link_text - リンクのテキスト
        戻り値:
            * TrueかFalseを返す
        """
        try:
            # next button '次のページ'をクリックする
            old_page = (self.driver.find_element_by_tag_name('html'))
            self.driver.find_element_by_link_text(link_text).click()
            WebDriverWait(self.driver, 30).until(
                EC.staleness_of(old_page))
        except NoSuchElementException as error_code:
            logprint('NoSuchElementException')
            logprint(error_code)
            return False
        except StaleElementReferenceException as error_code:
            logprint('StaleElementReferenceException')
            logprint(error_code)
            return False
        except TimeoutException as error_code:
            logprint('TimeoutException')
            logprint(error_code)
            return False
        except WebDriverException as error_code:
            logprint('WebDriverException')
            logprint(error_code)
            return False
        else:
            return True

    def get_product_link(self, product_pattern):
        u"""
        目的 : 商品個別のページを返す。
        引数 :
                * product_pattern -- 正規表現
        設定 :
                *
        戻り値 : link_list -- リンクのリスト
        例外発行 : なし
        処理方式:
            * <div class="mdItemList">以下のaタグでループする。
            * aタグのhref属性の値をlink_listに格納する。
        """

        link_list = []

        try:
            links = (self.driver.find_elements_by_xpath
                     ("//div[@class='mdItemList']/div/div/ul/li/dl/dd/a"))
        except StaleElementReferenceException as error_code:
            logprint('StaleElementReferenceException')
            logprint(error_code)
        except WebDriverException as error_code:
            logprint('WebDriverException')
            logprint(error_code)
        else:
            for link in links:
                try:
                    new_page = link.get_attribute('href')
                except StaleElementReferenceException as error_code:
                    logprint('StaleElementReferenceException')
                    logprint(error_code)
                else:
                    # 商品パターンの処理
                    if product_pattern.search(new_page):
                        link_list.append(new_page)

        return link_list

    def get_absolute_url(self, source):
        u"""起点になるurlとhrefの値を受け取り
        相対パスだったら絶対パスに変換して返す
        """

        absolute_url = ''
        # 相対パスを絶対パスに加工
        if source.startswith('/'):
            source = source[1:]
            absolute_url = self.base_url + source

        # 相対パスを絶対パスに加工
        # ページのリンクが'./page=2&cfrom=A00000'という形式になっている
        if source.startswith('./'):
            source = source[2:]
            absolute_url = self.base_url + source

        return absolute_url


    @staticmethod
    def get_select_list_by_xpath(driver, xpath):
        u"""driverとxpathを受け取り結果をリストで返す。
        """

        return_list = []
        try:
            selections = driver.find_elements_by_xpath(xpath)
        except NoSuchElementException:
            return None
        except WebDriverException:
            return None

        i = 0
        # select -> <p><span><select><option>
        for select in selections:
            try:
                select_name = select.find_element_by_xpath(
                    xpath +
                    "[" +
                    str(i + 1) +
                    "]/select").get_attribute("name")
                return_list.append([select_name])

                option_list = select.find_elements_by_xpath(
                    xpath +
                    "[" +
                    str(i + 1) +
                    "]/select/option")

                for option in option_list:
                    if option.text == '選択してください':
                        pass
                    else:
                        return_list[i].append(option.text)
            except NoSuchElementException:
                pass
            except WebDriverException:
                pass

            i += 1

        return return_list

    def get_links(self, url, link_pattern, xpath):
        u"""
        目的 : トップページを引数として受け取りページ内の商品カテゴリの
               リストを返す。
        引数 :
            * url -- URL
            * link_pattern -- リンクの正規表現
            * xpath -- linkへのxpath
        設定 :
                * self.page_list -- ページのURLのリスト
        戻り値 : self.page_list -- ページのURLのリスト
        例外発行 : なし
        処理方式:
            * 20回ごとにメッセージを出力する。
            * ページをgetする。
            * <div id="NaviStrCategory1">を探す。
            * <a ...>タグを探してループする。
            * href属性の値を取得する。
        """

        logprint(url)

        link_serial_number = 0

        if link_serial_number % 20 == 0:
            if link_serial_number != 0:
                logprint(
                    str(link_serial_number) + '個目のカテゴリを処理しています。')

        self.get_page(url)

        links = self.get_elements_by_xpath(xpath)

        if links is []:
            self.page_list = None
        else:
            for link in links:
                new_page = link.get_attribute('href')

                # リンク追跡パターン
                if link_pattern.search(new_page):
                    if new_page not in self.page_list:
                        self.page_list.append(new_page)

        link_serial_number += 1

        return self.page_list

    @staticmethod
    def get_product_url(row, link_text):
        u"""
        目的 :
            * 商品が表示されるリンクを受け取りクリックする。
        引数 :
            * row - 商品リストの行データ
            * link_text - リンクテキスト
        設定 :
                *
        戻り値 : なし
        例外発行 : なし
        """
        try:
            a_tag = row.find_element_by_link_text(link_text)
        except NoSuchElementException:
            return None
        else:
            url = a_tag.get_attribute('href')

        return url

class FactorialTest(unittest.TestCase):
    u"""テスト用のクラス
    """

    def setUp(self):
        u"""セットアップ
        """
        self.scraper = Scraper('https://www.kaientai.cc/')

    def test_get_page(self):
        u"""pageを取得するテスト
        """
        page = self.scraper.get_page()
        data = page.find_element_by_xpath('//body').get_attribute('outerHTML')
        self.assertTrue(data.startswith('<body'))

    def test_execute_login(self):
        u"""loginするテスト
        """
        page = self.scraper.get_page()

        login_dict = {
            'login_id': "general-h",
            'login_id_name': "ctl00$MainContent$txtID",
            'password': "101968",
            'password_name': "ctl00$MainContent$txtPSW",
            'submit_path': "//input[@id='MainContent_btnLogin']"
        }

        page = self.scraper.execute_login(login_dict)
        data = page.find_element_by_xpath('//body').get_attribute('outerHTML')
        login_msg = page.find_element_by_xpath(
            "//p[@class='loginmsg']").text
        self.assertTrue(data.startswith('<body'))
        self.assertEqual(login_msg, 'ご利用ありがとうございます。')

    def test_get_elements_by_xpath(self):
        """
        Web要素を取得するテスト。
        <div id="dd01">は食事関連
        """
        xpath = '//div[@id="dd01"]'
        self.scraper.get_page()
        elements = self.scraper.get_elements_by_xpath(xpath)

        self.assertEqual(len(elements), 1)

    def test_get_elements_not_find(self):
        """
        Web要素を取得するテスト。
        <div id="abcd">はないはず
        """
        xpath = '//div[@id="abcd"]'
        self.scraper.get_page()
        elements = self.scraper.get_elements_by_xpath(xpath)

        self.assertEqual(elements, [])

    def test_get_text_by_xpath(self):
        """
        Web要素のテキストを取得するテスト。
        """
        xpath = '//*[@id="left-menu-maker"]/h3'
        self.scraper.get_page()
        element_text = self.scraper.get_text_by_xpath(xpath)

        self.assertEqual(element_text, 'メーカーから探す')

    def test_get_text_not_find(self):
        """
        Web要素のテキストを取得するテスト。
        失敗して空文字がかえってくる。
        """
        xpath = '//*[@id="left-menu-maker"]/h4'
        self.scraper.get_page()
        element_text = self.scraper.get_text_by_xpath(xpath)

        self.assertEqual(element_text, '')

    def test_get_attributes_not_find(self):
        u"""linkを取得するテスト。見つからないケース
        <div href="xxxx">はありえないケース
        """
        xpath = "//div"
        attribute = "href"
        self.scraper.get_page()
        links = self.scraper.get_attribute_list_by_xpath(xpath, attribute)

        self.assertEqual(links, [])

    def test_get_attributes(self):
        u"""linkを取得するテスト
        """
        xpath = "//a[@href]"
        attribute = "href"
        self.scraper.get_page()
        links = self.scraper.get_attribute_list_by_xpath(xpath, attribute)

        for link in links:
            if link.startswith("https://www.kaientai.cc/listword.aspx?ccd="):
                pass

        self.assertEqual(len(links), 237)

    def test_get_link_and_text(self):
        u"""link先URLとテキストを取得するテスト
        """
        xpath = "//a[@href]"
        attribute = "href"
        pattern = "https://www.kaientai.cc/listword.aspx?ccd="
        self.scraper.get_page()
        links = self.scraper.get_link_and_text_list(xpath, attribute, pattern)

        self.assertEqual(len(links), 141)

    def test_get_next_link_false(self):
        u"""アクティブページの次のlinkを取得するテスト
        """
        active_element_xpath = "//span[@class='m_pager_active']"
        self.scraper.get_page()
        next_link = self.scraper.get_next_link(active_element_xpath)

        self.assertEqual(next_link, None)

    def test_get_next_link_end(self):
        u"""アクティブページの次のlinkを取得するテスト
        """
        active_element_xpath = "//span[@class='m_pager_active']"
        # 10件だけデータがあるページ
        self.scraper.get_page("https://www.kaientai.cc/listword.aspx?ccd=0209")
        next_link = self.scraper.get_next_link(active_element_xpath)

        self.assertTrue(next_link)
        self.assertEqual(next_link.text, '>>')

    def test_get_next_link(self):
        u"""アクティブページの次のlinkを取得するテスト
        """
        active_element_xpath = "//span[@class='m_pager_active']"
        # 21件あるページ
        self.scraper.get_page("https://www.kaientai.cc/listword.aspx?ccd=0202")
        next_link = self.scraper.get_next_link(active_element_xpath)

        self.assertTrue(next_link)
        self.assertEqual(next_link.text, '2')

    def test_get_next_link_loop(self):
        u"""アクティブページの次のlinkを取得するテスト
        """
        active_element_xpath = "//span[@class='m_pager_active']"
        # 21件あるページ
        self.scraper.get_page("https://www.kaientai.cc/listword.aspx?ccd=0202")
        next_link = self.scraper.get_next_link(active_element_xpath)
        while next_link.text != '>>':
            self.scraper.execute_link_click_by_element(next_link)
            next_link = self.scraper.get_next_link(active_element_xpath)

        self.assertEqual(next_link.text, '>>')

    def test_get_product_list(self):
        u"""商品のwebcdを取得するテスト
        """
        active_element_xpath = "//span[@class='m_pager_active']"
        # 21件あるページ
        self.scraper.get_page("https://www.kaientai.cc/listword.aspx?ccd=0202")
        product_list = []
        while True:
            product_list.extend(
                self.scraper.get_attribute_list_by_xpath('//div[@id="title"]/h2/a', 'href')
            )
            next_link = self.scraper.get_next_link(active_element_xpath)
            if next_link.text == '>>':
                break
            self.scraper.execute_link_click_by_element(next_link)

        self.assertEqual(len(product_list), 21)

    def tearDown(self):
        u"""クローズ処理など
        """
        self.scraper.driver.quit()

if __name__ == '__main__':
    unittest.main()


