from addok.db import DB

from addok.helpers import scripts


def test_manual_scan(factory):
    factory(name="rue de la monnaie", city="Vitry")
    factory(name="La monnaye", city="Saint-Loup-Cammas")
    street1 = factory(name="rue de la monnaie", city="Paris", importance=1)
    street2 = factory(name="rue de la monnaie", city="Condom", importance=0.9)
    results = scripts.manual_scan(keys=['w|monnaie', 'w|rue', 'w|de'],
                                  args=[2])
    assert results == ['d|{}'.format(street1['id']).encode(),
                       'd|{}'.format(street2['id']).encode()]


def test_zinter(factory):
    docs = (
        factory(name="rue de la monnaie", city="Vitry"),
        factory(name="La monnaye", city="Saint-Loup-Cammas"),
        factory(name="rue de la monnaie", city="Paris", importance=1),
        factory(name="rue de la monnaie", city="Condom", importance=0.9),
    )
    results = scripts.zinter(keys=['w|monnaie', 'w|rue', 'w|de'],
                             args=['tmp', 2])
    assert results == ['d|{}'.format(docs[2]['id']).encode(),
                       'd|{}'.format(docs[3]['id']).encode()]
    results = scripts.zinter(keys=['w|monnaie', 'w|rue', 'w|de'],
                             args=['tmp', 3])
    assert results == ['d|{}'.format(docs[2]['id']).encode(),
                       'd|{}'.format(docs[3]['id']).encode(),
                       'd|{}'.format(docs[0]['id']).encode()]


def test_delete(factory):
    factory(name="rue de la monnaie", city="Vitry", id='1234')
    assert DB.exists('d|1234')
    assert DB.exists('w|rue')
    scripts.delete(args=['d|*'])
    assert DB.exists('w|rue')
    assert not DB.exists('d|1234')
