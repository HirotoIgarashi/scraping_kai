# -*- coding: utf-8 -*-
u"""ユーティリティ用のライブラリ
"""
import re
import unittest

def make_header_name(name, number):
    """
    リストnameを受け取り要素数numberのリストを返す
    iが10の場合はlist1からlist10までを返す
    """
    name_list = []
    for i in range(0, number):
        name_list.append(name + 'list' + str(i + 1))

    return name_list


def remove_comma(data):
    u"""
    * データから数値のみを抜き出す。(1,280件) -> ['1','280']
    * 結果のリストをつなげる。['1','280'] -> 1280
    * intに変換する。
    戻り値 : int
    """
    # 数字のみを抜き出す。(1,280件) -> ['1','280']
    match_list = re.findall(r"\d+", data)
    str_data = ''
    int_data = 0
    for count in match_list:
        str_data += str(count)
    int_data = int(str_data)

    return int_data


class FactorialTest(unittest.TestCase):
    u"""テスト用のクラス
    """

    def setUp(self):
        u"""セットアップ
        """
        pass

    def test_make_header_name(self):
        u"""テスト
        """
        test_list = 'test_'
        test_result = make_header_name(test_list, 3)

        self.assertEqual(test_result, ['test_list1', 'test_list2', 'test_list3'])

    def test_remove_comma(self):
        u"""カンマを削除するテスト
        """
        self.assertEqual(remove_comma('1,240'), 1240)

    def tearDown(self):
        u"""クローズ処理など
        """
        pass

if __name__ == '__main__':
    unittest.main()


