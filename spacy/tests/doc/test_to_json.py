import pytest
from spacy.tokens import Doc, Span


@pytest.fixture()
def doc(en_vocab):
    words = ["c", "d", "e"]
    pos = ["VERB", "NOUN", "NOUN"]
    tags = ["VBP", "NN", "NN"]
    heads = [0, 0, 0]
    deps = ["ROOT", "dobj", "dobj"]
    ents = ["O", "B-ORG", "O"]
    morphs = ["Feat1=A", "Feat1=B", "Feat1=A|Feat2=D"]
    return Doc(
        en_vocab,
        words=words,
        pos=pos,
        tags=tags,
        heads=heads,
        deps=deps,
        ents=ents,
        morphs=morphs,
    )


def test_doc_to_json(doc):
    json_doc = doc.to_json()
    assert json_doc["text"] == "c d e "
    assert len(json_doc["tokens"]) == 3
    assert json_doc["tokens"][0]["pos"] == "VERB"
    assert json_doc["tokens"][0]["tag"] == "VBP"
    assert json_doc["tokens"][0]["dep"] == "ROOT"
    assert len(json_doc["ents"]) == 1
    assert json_doc["ents"][0]["start"] == 2  # character offset!
    assert json_doc["ents"][0]["end"] == 3  # character offset!
    assert json_doc["ents"][0]["label"] == "ORG"


def test_doc_to_json_underscore(doc):
    Doc.set_extension("json_test1", default=False)
    Doc.set_extension("json_test2", default=False)
    doc._.json_test1 = "hello world"
    doc._.json_test2 = [1, 2, 3]
    json_doc = doc.to_json(underscore=["json_test1", "json_test2"])
    assert "_" in json_doc
    assert json_doc["_"]["json_test1"] == "hello world"
    assert json_doc["_"]["json_test2"] == [1, 2, 3]


def test_doc_to_json_underscore_error_attr(doc):
    """Test that Doc.to_json() raises an error if a custom attribute doesn't
    exist in the ._ space."""
    with pytest.raises(ValueError):
        doc.to_json(underscore=["json_test3"])


def test_doc_to_json_underscore_error_serialize(doc):
    """Test that Doc.to_json() raises an error if a custom attribute value
    isn't JSON-serializable."""
    Doc.set_extension("json_test4", method=lambda doc: doc.text)
    with pytest.raises(ValueError):
        doc.to_json(underscore=["json_test4"])


def test_doc_to_json_span(doc):
    """Test that Doc.to_json() includes spans"""
    doc.spans["test"] = [Span(doc, 0, 2, "test"), Span(doc, 0, 1, "test")]
    json_doc = doc.to_json()
    assert "spans" in json_doc
    assert len(json_doc["spans"]) == 1
    assert len(json_doc["spans"]["test"]) == 2
    assert json_doc["spans"]["test"][0]["start"] == 0
