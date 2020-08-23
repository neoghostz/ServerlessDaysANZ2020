import pytest
import hashlib
import json

from GeneratePDF import GeneratePDF


payload = "{\"table_data\": [[\"First Name\", \"Last Name\", \"email\", \"zip\"],[\"Mike\", \"Driscoll\", \"mike@somewhere.com\", \"55555\"],[\"John\", \"Doe\", \"jdoe@doe.com\", \"12345\"],[\"Nina\", \"Ma\", \"inane@where.com\", \"54321\"]]}"

expected = {}

@pytest.fixture()
def payload_dict():
    return json.loads(payload)

@pytest.fixture()
def expected_data():
    return expected

@pytest.fixture()
def bootstrap_generate_pdf(payload_dict):
    the_object = GeneratePDF(payload_dict)

    return the_object


def test_pdf_generation(bootstrap_generate_pdf, expected_data):
    pdf = bootstrap_generate_pdf.build_pdf()
    #print(hashlib.md5(bootstrap_generate_pdf.pdf).digest)
    assert type(pdf) == bytes
