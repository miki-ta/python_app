import unittest, turukame

class TestTurukame(unittest.TestCase):

    def test_turukame(self):
        # 鶴亀算を計算
        turu, kame = turukame.calc_turukame(
            turukame.Turu(),
            turukame.Kame(), 
            heads=10, legs=28)

        # 結果を検証する
        self.assertEqual(turu, 6, "基本的な計算で鶴の数")
        self.assertEqual(kame, 4, "基本的な計算で亀の数")

