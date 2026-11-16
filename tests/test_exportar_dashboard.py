import hashlib
from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import unittest

from exportar_dashboard import exportar


class ExportacaoTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name) / "teste.db"
        with closing(sqlite3.connect(self.db)) as c:
            c.executescript("""
                CREATE TABLE animais (id_animal TEXT, municipio TEXT, especie TEXT,
                    situacao_vacinacao TEXT, data_cadastro TEXT);
                INSERT INTO animais VALUES ('ANM001','Rio Branco','Cachorro','Em dia','2026-11-15T02:42:59');
                CREATE TABLE vacinacoes (id_vacinacao INTEGER, id_animal TEXT, situacao TEXT, data_aplicacao TEXT);
                INSERT INTO vacinacoes VALUES (1,'ANM001','Aplicada','2026-10-01');
                INSERT INTO vacinacoes VALUES (2,'ANM001','Pendente','2026-10-02');
                INSERT INTO vacinacoes VALUES (3,'ANM001','Aguardando reforço','2026-10-03');
                INSERT INTO vacinacoes VALUES (4,'ANM001','Aplicada',NULL);
                CREATE TABLE diagnosticos (id_diagnostico INTEGER, id_animal TEXT, diagnostico TEXT,
                    situacao TEXT, data_diagnostico TEXT);
                INSERT INTO diagnosticos VALUES (1,'ANM001','Raiva','Em tratamento','2026-02-30');
                CREATE TABLE maus_tratos (id_ocorrencia INTEGER, id_animal TEXT, municipio TEXT);
                INSERT INTO maus_tratos VALUES (1,NULL,'Rio Branco');
                CREATE TABLE obitos_eutanasias (id_evento INTEGER, id_animal TEXT);
            """)
            c.commit()

    def test_exportacao_preserva_banco_e_nao_conta_pendencias_como_doses(self):
        antes = hashlib.sha256(self.db.read_bytes()).digest()
        payload = exportar(self.db)
        self.assertEqual(antes, hashlib.sha256(self.db.read_bytes()).digest())
        self.assertEqual(len(payload["data"]["vac"]), 2)
        self.assertEqual(payload["meta"]["contagens_banco"]["vacinacoes"], 4)
        self.assertEqual(payload["data"]["cad"][0]["ia"], "ANM001")
        self.assertEqual(payload["data"]["cad"][0]["e"], "Cão")
        self.assertEqual(payload["data"]["cad"][0]["sv"], "Completa")
        self.assertEqual(payload["data"]["cad"][0]["d"], "2026-11-15")
        self.assertEqual(payload["data"]["vac"][0]["m"], "Rio Branco")

    def test_ausencias_nao_sao_inventadas(self):
        payload = exportar(self.db)
        self.assertEqual(payload["meta"]["sem_data"]["vac"], 1)
        self.assertEqual(payload["data"]["diag"][0]["d"], "")
        self.assertIsNone(payload["data"]["cad"][0]["i"])
        self.assertEqual(payload["data"]["maus"][0]["gr"], "Não informado")
        self.assertIsNone(payload["data"]["maus"][0]["ia"])
        self.assertEqual(payload["data"]["canil"], [])
        self.assertEqual(payload["data"]["notif"], [])

    def test_banco_inexistente_nao_e_criado(self):
        missing = self.db.parent / "inexistente.db"
        with self.assertRaises(sqlite3.OperationalError):
            exportar(missing)
        self.assertFalse(missing.exists())


if __name__ == "__main__":
    unittest.main()
