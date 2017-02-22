# -*- coding: utf-8 -*-
u"""Requestsライブラリによるスクレイパー
"""
import unittest

import requests

# My library
# import logmessage

class RequestsScraper():
    u"""Requestを使用するスクレイパー
    """
    def __init__(self, user_agent=None):
        self.requests = requests.Session()
        if user_agent is not None:
            self.requests.headers.update(user_agent)

    def set_user_agent(self, user_agent):
        """リクエストヘッダーのUser-Agentを更新する
        """
        self.requests.headers.update(user_agent)

    def set_referer(self, referer):
        """リクエストヘッダーのUser-Agentを更新する
        """
        self.requests.headers.update(referer)

    def fetch(self, url):
        """ページを取得する
        """
        return self.requests.get(url)

    def fetch_image(self, url, path, referer=None):
        """保存する
        """
        if referer is not None:
            self.set_referer(referer)

        response = self.fetch(url)

        if response.status_code == 200:
            with open(path, 'wb') as image_file:
                for chunk in response.iter_content(1024):
                    image_file.write(chunk)

        return response


class FatorialTest(unittest.TestCase):
    u"""テスト用のクラス
    """

    def setUp(self):
        u"""セットアップ
        """
        user_agent = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/55.0.2883.87 Safari/537.36"}
        self.requests = RequestsScraper(user_agent=user_agent)

    def test_fetch(self):
        """トップページを取得する
        介援隊のページ
        """
        url = 'https://www.kaientai.cc/'
        response = self.requests.fetch(url)

        self.assertIsInstance(response, requests.models.Response)
        self.assertEqual(response.status_code, 200)

        response.close()
        response.connection.close()

    def test_fetch_list_page(self):
        """一覧ページを取得する
        """
        url = 'https://www.kaientai.cc/listword.aspx?ccd=0101'
        response = self.requests.fetch(url)

        self.assertEqual(response.status_code, 200)

        response.close()
        response.connection.close()

    def test_fetch_detail_page(self):
        """一覧ページを取得する
        """
        url = 'https://www.kaientai.cc/goods.aspx?webcd=298761'
        response = self.requests.fetch(url)

        self.assertEqual(response.status_code, 200)

        response.close()
        response.connection.close()

    def test_fetch_image_not_found(self):
        """一覧ページを取得する
        """
        url = 'https://www.kaientai.cc/images/products/298761.jpg'
        response = self.requests.fetch(url)

        self.assertEqual(response.status_code, 404)

        response.close()
        response.connection.close()

    def test_set_user_agent(self):
        """一覧ページを取得する
        """
        url = 'https://www.kaientai.cc/images/products/298761.jpg'
        self.requests.set_user_agent({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/55.0.2883.87 Safari/537.36"})
        response = self.requests.fetch(url)

        self.assertEqual(response.status_code, 404)

        response.close()
        response.connection.close()

    def test_set_useragent_referer(self):
        """一覧ページを取得する
        """
        url = 'https://www.kaientai.cc/images/products/298761.jpg'
        self.requests.set_user_agent({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/55.0.2883.87 Safari/537.36"})
        self.requests.set_referer({
            'referer': 'https://www.kaientai.cc/goods.aspx?webcd=298761'})
        response = self.requests.fetch(url)

        self.assertEqual(response.status_code, 200)

        response.close()
        response.connection.close()

    def test_save_image(self):
        """画像を取得する
        """
        url = 'https://www.kaientai.cc/images/products/298761.jpg'
        self.requests.set_referer({
            'referer': 'https://www.kaientai.cc/goods.aspx?webcd=298761'})
        response = self.requests.fetch(url)

        if response.status_code == 200:
            with open('test.jpg', 'wb') as image_file:
                for chunk in response.iter_content(1024):
                    image_file.write(chunk)

        self.assertEqual(response.status_code, 200)

        response.close()
        response.connection.close()

    def test_fetch_image_fail(self):
        """画像を取得する
        """
        url = 'https://www.kaientai.cc/images/products/298761.jpg'
        path = 'tmp/fail.jpg'
        response = self.requests.fetch_image(url, path)

        self.assertEqual(response.status_code, 404)

        response.close()
        response.connection.close()

    def test_fetch_image(self):
        """画像を取得する
        """
        url = 'https://www.kaientai.cc/images/products/298761.jpg'
        path = 'tmp/test.jpg'
        referer = {'referer': 'https://www.kaientai.cc/goods.aspx?webcd=298761'}
        response = self.requests.fetch_image(url, path, referer)

        print(response.request.headers)

        self.assertEqual(response.status_code, 200)

        response.close()
        response.connection.close()

    def tearDown(self):
        u"""ファイルをクローズする。
        """
        pass

if __name__ == '__main__':
    unittest.main()
