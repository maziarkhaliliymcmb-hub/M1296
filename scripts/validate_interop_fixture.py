"""Validate the pinned cross-repository 36OS interoperability fixture."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/"tests"/"fixtures"/"core-interoperability-v1.1.0.json"
EXPECTED_ROOT_BLOB="a4f7f63a48d31c1c3ee6636c515645ab72ba302b"
def validate():
 data=json.loads(FIXTURE.read_text(encoding="utf-8"))
 assert data["fixture_id"]=="36OS-CORE-INTEROPERABILITY-CONFORMANCE"
 assert data["fixture_version"]==data["contract_version"]=="1.1.0"
 assert data["contract_id"]=="36OS-CORE-INTEROPERABILITY"
 p=data["provenance"]; assert p["root_blob_sha"]==EXPECTED_ROOT_BLOB and p["mutable"] is False
 root=data["root_response"]; genome=root["genome"]
 assert root["standard"]==genome["standard"]=="M36" and genome["genome_id"]=="M36-ROOT"
 assert genome["standard_version"]==p["root_schema_version"]=="1.0.0"
 assert genome["genome_version"]==p["root_genome_version"]=="1.0.0"
 assert root["gene_count"]==36 and root["root_protected"] is True
 genes=[g["id"] for c in sorted(genome["chromosomes"],key=lambda x:x["index"]) for g in c["genes"]]
 assert len(genes)==len(set(genes))==36 and genes[0]=="M36-CHR01-G01" and genes[-1]=="M36-CHR06-G06"
 for key,standard,capacity in (("m666_response","M666",666),("m1296_response","M1296",1296)):
  response=data[key]; assert response["standard"]==standard
  assert response["root_schema_version"]==genome["standard_version"]
  assert response["root_genome_version"]==genome["genome_version"]
  assert response["capacity"]==capacity
  records=response["relations"] if standard=="M666" else response["edges"]
  assert response["active_count"]==len(records)
 assert data["m1296_response"]["node_count"]==36
 for r in data["m666_response"]["relations"]:
  assert type(r["gene_a"]) is int and type(r["gene_b"]) is int and 0<=r["gene_a"]<=r["gene_b"]<36
 for e in data["m1296_response"]["edges"]:
  assert type(e["source"]) is int and type(e["target"]) is int and 0<=e["source"]<36 and 0<=e["target"]<36
if __name__=="__main__":
 validate(); print("Pinned 36OS interoperability fixture is valid.")
