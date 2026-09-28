import unittest

from app import app


class TestAppApi(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_calculo_devuelve_derivada_y_muestras(self):
        response = self.client.post("/api/calculo", json={"expr": "x**2", "a": 0, "b": 2})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["derivada"], "2*x")
        self.assertEqual(len(data["x"]), 160)

    def test_ejercicio_se_corrige(self):
        response = self.client.post("/api/ejercicios/1", json={"answer": 14})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["correct"])

    def test_simulador_y_laboratorio(self):
        simulation = self.client.post("/api/simulador", json={"t": 2})
        laboratory = self.client.get("/api/laboratorio3d")
        self.assertEqual(simulation.status_code, 200)
        self.assertEqual(laboratory.status_code, 200)
        self.assertEqual(len(laboratory.get_json()["orbit"]["x"]), 160)


if __name__ == "__main__":
    unittest.main()