import unittest
from core import buscar, comparar, extraer_local, fps_por_100


class TestCore(unittest.TestCase):
    def test_busqueda_exacta_y_sin_marca(self):
        self.assertEqual(buscar("RTX 5070")[0]["nombre"], "RTX 5070")
        self.assertEqual(buscar("Radeon RX 9070 XT")[0]["nombre"], "RX 9070 XT")

    def test_gpu_inexistente_da_sugerencias(self):
        gpu, sug = buscar("RTX Spark")
        self.assertIsNone(gpu)
        self.assertTrue(sug)

    def test_extraer_prefiere_nombre_largo(self):
        self.assertEqual(extraer_local("RTX 5070 Ti vs RTX 5070"), ["RTX 5070 Ti", "RTX 5070"])

    def test_fps_por_100(self):
        self.assertAlmostEqual(fps_por_100({"fps_promedio": 100, "precio_usd": 500}), 20.0)

    def test_comparar_ganadores(self):
        c = comparar(buscar("RTX 5070")[0], buscar("RX 9070 XT")[0])
        self.assertEqual(c["ganadores"]["mas_rapida"], "RX 9070 XT")
        self.assertEqual(c["ganadores"]["mas_eficiente"], "RTX 5070")
        self.assertEqual((c["marca_1"], c["marca_2"]), ("NVIDIA", "AMD"))


if __name__ == "__main__":
    unittest.main()
