import unittest
from core import analizar, buscar, comparar, extraer_local, fps_por_100


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


class TestFormasDeEscribir(unittest.TestCase):
    PARES = {
        "RTX5070Ti vs rx9070xt": ["RTX 5070 Ti", "RX 9070 XT"],
        "compara la geforce RTX 5070 con la radeon rx 9070 xt": ["RTX 5070", "RX 9070 XT"],
        "5070 y 9070xt": ["RTX 5070", "RX 9070 XT"],
        "4070s o 4060": ["RTX 4070 Super", "RTX 4060"],
        "ARC b580 contra a770": ["Arc B580", "Arc A770"],
        "Quiero comparar una RTX 5090 y una RX 7800-XT por favor!!": ["RTX 5090", "RX 7800 XT"],
        "5070 ti 5070": ["RTX 5070 Ti", "RTX 5070"],
        "RTX 4070 SUPER / RX 7600": ["RTX 4070 Super", "RX 7600"],
        "rtx 4070 suprer vs rx 7600": ["RTX 4070 Super", "RX 7600"],
        "¿Cuál es mejor, la nvidia 4090 o la amd 9070?": ["RTX 4090", "RX 9070"],
        "rtx_5080,rx-9070-xt": ["RTX 5080", "RX 9070 XT"],
        "  RX   9070   XT    vs    RTX   5070  ": ["RX 9070 XT", "RTX 5070"],
    }

    def test_variantes(self):
        for texto, esperado in self.PARES.items():
            with self.subTest(texto):
                self.assertEqual(extraer_local(texto), esperado)

    def test_no_adivina_modelos_fuera_de_la_base(self):
        self.assertEqual(analizar("rtx 5070 super vs rx 9070")["desconocidas"], ["rtx 5070 super"])
        self.assertEqual(analizar("rtx 3060 vs rtx 4060")["desconocidas"], ["rtx 3060"])

    def test_numeros_sueltos_no_confunden(self):
        self.assertEqual(extraer_local("rtx 5070 y rx 9070 xt a 1080p con 600 dolares"), ["RTX 5070", "RX 9070 XT"])
