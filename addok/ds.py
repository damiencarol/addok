from addok.config import config
from addok.db import DB
from addok.helpers import keys, scripts


class RedisStore:

    def fetch(self, *keys):
        pipe = DB.pipeline(transaction=False)
        for key in keys:
            pipe.get(key)
        for key, doc in zip(keys, pipe.execute()):
            if doc is not None:
                yield key, doc

    def add(self, *docs):
        pipe = DB.pipeline(transaction=False)
        for key, blob in docs:
            pipe.set(key, blob)
        pipe.execute()

    def remove(self, *keys):
        pipe = DB.pipeline(transaction=False)
        for key in keys:
            pipe.delete(key)
        pipe.execute()

    def flush(self):
        scripts.delete(args=['d|*'])


class DSProxy:
    instance = None

    def __getattr__(self, name):
        return getattr(self.instance, name)


DS = DSProxy()


@config.on_load
def on_load():
    DS.instance = config.DOCUMENT_STORE()


def store_documents(docs):
    to_add = []
    to_remove = []
    for doc in docs:
        if not doc:
            continue
        key = keys.document_key(doc['id'])
        if doc.get('_action') in ['delete', 'update']:
            to_remove.append(key)
        if doc.get('_action') in ['index', 'update', None]:
            to_add.append((key, config.DOCUMENT_SERIALIZER.dumps(doc)))
        yield doc
    if to_remove:
        DS.remove(*to_remove)
    if to_add:
        DS.add(*to_add)


def get_document(key):
    results = DS.fetch(key)
    try:
        _, doc = next(results)
    except StopIteration:
        return None
    return config.DOCUMENT_SERIALIZER.loads(doc)


def get_documents(*keys):
    for id_, blob in DS.fetch(*keys):
        yield id_, config.DOCUMENT_SERIALIZER.loads(blob)
