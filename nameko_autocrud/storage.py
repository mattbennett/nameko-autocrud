from sqlalchemy_filters import apply_loads, apply_filters, apply_sort


class NotFound(LookupError):
    pass


class DBStorage(object):

    def __init__(self, model_cls, session=None):
        self.model_cls = model_cls
        self.session = session

    def _get(self, pk):
        obj = self.query.get(pk)
        if not obj:
            raise NotFound(
                '{} with ID {} does not exist'
                .format(self.model_cls.__name__, pk))
        return obj

    @property
    def query(self):
        return self.session.query(self.model_cls)

    def get(self, pk):
        return self._get(pk)

    def list(
        self, filters=None, loads=None, order_by=None, offset=None, limit=None
    ):
        query = self.query
        if filters:
            query = apply_filters(query, filters)
        if loads:
            query = apply_loads(query, loads)
        if order_by:
            query = apply_sort(query, order_by)
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        return query.all()

    def count(self, filters=None):
        query = self.query
        if filters:
            query = apply_filters(query, filters)

        return query.count()

    def update(self, pk, data, flush=True, commit=True):
        obj = self._get(pk)
        for key, value in data.items():
            setattr(obj, key, value)
        if commit:
            self.session.commit()
            self.session.refresh(obj)
        elif flush:
            self.session.flush()
            self.session.refresh(obj)
        return obj

    def create(self, data, flush=True, commit=True):
        obj = self.model_cls(**data)
        self.session.add(obj)
        if commit:
            self.session.commit()
            self.session.refresh(obj)
        elif flush:
            self.session.flush()
            self.session.refresh(obj)

        return obj

    def delete(self, pk, flush=True, commit=True):
        obj = self._get(pk)
        self.session.delete(obj)
        if commit:
            self.session.commit()
        elif flush:
            self.session.flush()
