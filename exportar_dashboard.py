"""Exporta somente as tabelas tratadas do SQLite, sem modificar o banco.

Uso: python exportar_dashboard.py --banco banco_zoonoses.db
"""

import argparse
from collections import Counter
from contextlib import closing
from datetime import date, datetime, timezone
import json
from pathlib import Path
import sqlite3
import tempfile


NA = "Não informado"
TABLES = ("animais", "vacinacoes", "diagnosticos", "maus_tratos", "obitos_eutanasias")


def texto(value):
    return str(value).strip() if value is not None and str(value).strip() else NA


def data_iso(value):
    """Datas ausentes ficam vazias; não inventamos uma data para o evento."""
    try:
        return date.fromisoformat(str(value)[:10]).isoformat()
    except (ValueError, TypeError):
        return ""


def exportar(banco):
    # mode=ro também impede que um caminho errado crie um banco vazio.
    with closing(sqlite3.connect(banco.resolve().as_uri() + "?mode=ro", uri=True)) as connection:
        connection.row_factory = sqlite3.Row
        connection.execute("BEGIN")  # Uma fotografia consistente das cinco tabelas.
        tabelas = {
            tabela: [dict(row) for row in connection.execute(f'SELECT * FROM "{tabela}"')]
            for tabela in TABLES
        }

    animais = {r["id_animal"]: r for r in tabelas["animais"]}
    especie = lambda r: {"Cachorro": "Cão", "Cão": "Cão", "Gato": "Gato"}.get(r.get("especie"), texto(r.get("especie")))
    situacao = {"Em dia": "Completa", "Parcial": "Parcial", "Pendente": "Incompleta"}
    data = {k: [] for k in ("cad", "vac", "canil", "notif", "diag", "maus", "obit")}

    for r in tabelas["animais"]:
        data["cad"].append({
            "ia": r["id_animal"], "m": texto(r.get("municipio")), "e": especie(r),
            "r": texto(r.get("raca")), "x": texto(r.get("sexo")), "i": None,
            "d": data_iso(r.get("data_cadastro")), "st": texto(r.get("status")),
            "vf": texto(r.get("vacinas_faltantes")),
            "sv": situacao.get(r.get("situacao_vacinacao"), texto(r.get("situacao_vacinacao"))),
        })

    aplicadas = [r for r in tabelas["vacinacoes"] if r.get("situacao") == "Aplicada"]
    for r in aplicadas:
        a = animais.get(r["id_animal"], {})
        data["vac"].append({
            "id": r["id_vacinacao"], "ia": r["id_animal"], "m": texto(a.get("municipio")),
            "e": especie(a), "d": data_iso(r.get("data_aplicacao")), "n": 1,
        })

    for r in tabelas["diagnosticos"]:
        a = animais.get(r["id_animal"], {})
        data["diag"].append({
            "id": r["id_diagnostico"], "ia": r["id_animal"], "m": texto(a.get("municipio")),
            "do": texto(r.get("diagnostico")), "d": data_iso(r.get("data_diagnostico")),
            "tr": texto(r.get("situacao")), "ev": NA,
        })

    for r in tabelas["maus_tratos"]:
        data["maus"].append({
            "id": r["id_ocorrencia"], "ia": r.get("id_animal"), "m": texto(r.get("municipio")),
            "tm": texto(r.get("tipo_ocorrencia")), "d": data_iso(r.get("data_ocorrencia")),
            "gr": NA, "pv": texto(r.get("situacao")),
        })

    for r in tabelas["obitos_eutanasias"]:
        data["obit"].append({
            "id": r["id_evento"], "ia": r.get("id_animal"), "m": texto(r.get("municipio")),
            "ot": texto(r.get("tipo_evento")), "mo": texto(r.get("motivo")),
            "d": data_iso(r.get("data_evento")),
        })

    return {
        "schema_version": 1,
        "meta": {
            "gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "fonte": banco.name,
            "contagens_banco": {t: len(rows) for t, rows in tabelas.items()},
            "situacoes_vacinacao": dict(Counter(texto(r.get("situacao")) for r in tabelas["vacinacoes"])),
            "sem_data": {k: sum(not r["d"] for r in rows) for k, rows in data.items()},
            "secoes_indisponiveis": ["canil", "notif"],
            "campos_indisponiveis": ["idade", "gravidade", "evolucao"],
        },
        "data": data,
    }


def main():
    base = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--banco", type=Path, default=base / "banco_zoonoses.db")
    parser.add_argument("--saida", type=Path, default=base / "dados" / "dashboard.json")
    args = parser.parse_args()
    try:
        payload = exportar(args.banco)
    except (sqlite3.Error, OSError) as error:
        parser.exit(1, f"Não foi possível ler o banco tratado: {error}\n")
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    # Substituição atômica: uma leitura da página nunca recebe JSON pela metade.
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=args.saida.parent, delete=False) as temp:
        json.dump(payload, temp, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
        temp.write("\n")
        temporary = Path(temp.name)
    temporary.replace(args.saida)
    print(f"Exportado: {args.saida}")
    print(" | ".join(f"{k}: {len(rows)}" for k, rows in payload["data"].items()))


if __name__ == "__main__":
    main()
