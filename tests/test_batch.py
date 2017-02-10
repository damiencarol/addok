from addok.batch import process_documents, flush
from addok.core import search
from addok.db import DB


def test_process_should_index_by_default(factory):
    doc = factory(skip_index=True, name="Melicocq")
    assert not search("Mélicocq")
    process_documents(doc.copy())
    assert search("Melicocq")


def test_process_should_deindex_if_action_is_given(factory):
    doc = factory(name="Mélicocq")
    assert search("Mélicoq")
    process_documents({"_action": "delete", "id": doc["id"]})
    assert not search("Mélicoq")


def test_process_should_update_if_action_is_given(factory):
    doc = factory(name="rue de l'avoine")
    assert search("rue")
    doc["_action"] = "update"
    doc["name"] = "avenue de l'avoine"
    process_documents(doc.copy())
    assert search("avenue")
    assert not search("rue")


def test_flush(factory, monkeypatch):

    class Args:
        force = False

    factory(name="rue de l'avoine")
    assert DB.keys()
    monkeypatch.setitem(__builtins__, 'input', lambda *args, **kwargs: 'no')
    flush(Args())
    assert DB.keys()
    monkeypatch.setitem(__builtins__, 'input', lambda *args, **kwargs: 'yes')
    flush(Args())
    assert not DB.keys()


def test_force_flush(factory):

    class Args:
        force = True

    factory(name="rue de l'avoine")
    assert DB.keys()
    flush(Args())
    assert not DB.keys()
