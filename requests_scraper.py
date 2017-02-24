# -*- coding: utf-8 -*-
u"""Requestsライブラリによるスクレイパー
"""
import os
import unittest

import requests

# My library
# import logmessage

class RequestsScraper():
    u"""Requestを使用するスクレイパー
    """
    def __init__(self, user_agent=None):
        user_agent_dict = {'User-Agent': user_agent}

        self.requests = requests.Session()

        if user_agent is not None:
            self.requests.headers.update(user_agent_dict)

    def set_user_agent(self, user_agent):
        """リクエストヘッダーのUser-Agentを更新する
        """
        user_agent_dict = {'User-Agent': user_agent}
        self.requests.headers.update(user_agent_dict)

    def set_referer(self, referer):
        """リクエストヘッダーのRefererを更新する
        """
        referer_dict = {'referer': referer}
        self.requests.headers.update(referer_dict)

    def fetch(self, url):
        """ページを取得する
        """
        return self.requests.get(url)

    def fetch_image(self, url, path, referer=None):
        """保存する
        """
        path_list = path.split('/')[0:-1]
        image_dir = ''
        for dir_path in path_list:
            if len(image_dir) == 0:
                image_dir = dir_path
            else:
                image_dir += '/' + dir_path

        # ./imageディレクトリを作成する。
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)

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
        user_agent = (
            "Mozilla/5.0 (X11; Linux x86_64)"
            "AppleWebKit/537.36 (KHTML, like Gecko)"
            "Chrome/55.0.2883.87 Safari/537.36")
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
        self.requests.set_user_agent(
            "Mozilla/5.0 (X11; Linux x86_64)"
            "AppleWebKit/537.36 (KHTML, like Gecko)"
            "Chrome/55.0.2883.87 Safari/537.36")
        response = self.requests.fetch(url)

        self.assertEqual(response.status_code, 404)

        response.close()
        response.connection.close()

    def test_set_useragent_referer(self):
        """一覧ページを取得する
        """
        url = 'https://www.kaientai.cc/images/products/298761.jpg'
        self.requests.set_user_agent(
            "Mozilla/5.0 (X11; Linux x86_64)"
            "AppleWebKit/537.36 (KHTML, like Gecko)"
            "Chrome/55.0.2883.87 Safari/537.36")
        self.requests.set_referer('https://www.kaientai.cc/goods.aspx?webcd=298761')
        response = self.requests.fetch(url)

        self.assertEqual(response.status_code, 200)

        response.close()
        response.connection.close()

    def test_save_image(self):
        """画像を取得する
        """
        url = 'https://www.kaientai.cc/images/products/298761.jpg'
        self.requests.set_referer('https://www.kaientai.cc/goods.aspx?webcd=298761')
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
        refererを設定しないので失敗する
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
        referer = 'https://www.kaientai.cc/goods.aspx?webcd=298761'
        response = self.requests.fetch_image(url, path, referer)

        print(response.request.headers)

        self.assertEqual(response.status_code, 200)

        response.close()
        response.connection.close()

    def test_fetch_image_tmp_tmp(self):
        """画像を取得する
        """
        url = 'https://www.kaientai.cc/images/products/298761.jpg'
        path = 'tmp/tmp/test.jpg'
        referer = 'https://www.kaientai.cc/goods.aspx?webcd=298761'
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
