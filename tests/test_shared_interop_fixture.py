import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/"tests/fixtures/core-interoperability-v1.1.0.json"
def test_m1296_fixture_requires_both_m36_version_domains():
 fixture=json.loads(FIXTURE.read_text(encoding="utf-8"))
 root=fixture["root_response"]["genome"]; envelope=fixture["m1296_response"]
 assert envelope["root_schema_version"]==root["standard_version"]=="1.0.0"
 assert envelope["root_genome_version"]==root["genome_version"]=="1.0.0"
 assert envelope["node_count"]==36 and envelope["capacity"]==1296
def test_m1296_fixture_does_not_infer_schema_or_content_version():
 fixture=json.loads(FIXTURE.read_text(encoding="utf-8")); envelope=fixture["m1296_response"]
 assert "root_schema_version" in envelope and "root_genome_version" in envelope
 assert envelope["root_schema_version"] != fixture["contract_version"] or envelope["root_genome_version"] != fixture["contract_version"]
