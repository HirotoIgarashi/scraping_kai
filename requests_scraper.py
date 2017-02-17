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
    def __init__(self):
        self.requests = requests.Session()

    def set_user_agent(self, user_agent):
        """リクエストヘッダーのUser-Agentを更新する
        """
        self.requests.headers.update(user_agent)

    def fetch(self, url):
        """ページを取得する
        """
        return self.requests.get(url)

    def save(self):
        """保存する
        """
        pass


class FatorialTest(unittest.TestCase):
    u"""テスト用のクラス
    """

    def setUp(self):
        u"""セットアップ
        """
        self.requests = RequestsScraper()

    def test_fetch(self):
        """トップページを取得する
        介援隊のページ
        """
        url = 'https://www.kaientai.cc/'
        self.response = self.requests.fetch(url)

        self.assertIsInstance(self.response, requests.models.Response)
        self.assertEqual(self.response.status_code, 200)

    def test_fetch_list_page(self):
        """一覧ページを取得する
        """
        url = 'https://www.kaientai.cc/listword.aspx?ccd=0101'
        self.response = self.requests.fetch(url)

        self.assertEqual(self.response.status_code, 200)

    def test_fetch_detail_page(self):
        """一覧ページを取得する
        """
        url = 'https://www.kaientai.cc/goods.aspx?webcd=298761'
        self.response = self.requests.fetch(url)

        self.assertEqual(self.response.status_code, 200)

    def test_fetch_image_not_found(self):
        """一覧ページを取得する
        """
        url = 'https://www.kaientai.cc/images/products/298761.jpg'
        self.response = self.requests.fetch(url)

        print(self.response.request.headers)

        self.assertEqual(self.response.status_code, 404)

    def test_set_user_agent(self):
        """一覧ページを取得する
        """
        url = 'https://www.kaientai.cc/images/products/298761.jpg'
        self.requests.set_user_agent({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'})
        self.response = self.requests.fetch(url)

        print(self.response.request.headers)

        self.assertEqual(self.response.status_code, 404)

    def tearDown(self):
        u"""ファイルをクローズする。
        """
        self.response.connection.close()
        self.response.close()
        self.response.raw.close()
        # self.response.close()
        # pass

if __name__ == '__main__':
    unittest.main()
