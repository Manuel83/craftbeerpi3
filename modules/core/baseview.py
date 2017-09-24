from flask import request, json
from flask_classy import route, FlaskView
from flask_login import login_required

from modules.core.core import cbpi


class BaseView(FlaskView):

    as_array = False
    cache_key = None
    api = cbpi

    @login_required
    @route('/<int:id>', methods=["GET"])
    def getOne(self, id):
        if self.api.cache.get(self.cache_key) is not None:
            return json.dumps(self.api.cache.get(self.cache_key).get(id))
        else:
            return json.dumps(self.model.get_one(id))

    @login_required
    @route('/', methods=["GET"])
    def getAll(self):
        if self.api.cache.get(self.cache_key) is not None:
            return json.dumps(self.api.cache.get(self.cache_key))
        else:
            return json.dumps(self.model.get_all())

    def _pre_post_callback(self, data):
        pass


    def _post_post_callback(self, m):
        pass

    @login_required
    @route('/', methods=["POST"])
    def post(self):

        data = request.json
        self.api._app.logger.info("INSERT Model %s", self.model.__name__)
        self._pre_post_callback(data)
        m = self.model.insert(**data)
        if self.api.cache.get(self.cache_key) is not None:
            self.api.cache.get(self.cache_key)[m.id] = m

        self._post_post_callback(m)

        return json.dumps(m)

    def _pre_put_callback(self, m):
        pass

    def _post_put_callback(self, m):
        pass

    @login_required
    @route('/<int:id>', methods=["PUT"])
    def put(self, id):
        data = request.json
        data["id"] = id
        try:
            del data["instance"]
        except:
            pass
        if self.api.cache.get(self.cache_key) is not None:
            self._pre_put_callback(self.api.cache.get(self.cache_key)[id])
            self.api.cache.get(self.cache_key)[id].__dict__.update(**data)
            m = self.model.update(**self.api.cache.get(self.cache_key)[id].__dict__)
            self._post_put_callback(self.api.cache.get(self.cache_key)[id])
            return json.dumps(self.api.cache.get(self.cache_key)[id])
        else:
            m = self.model.update(**data)

            self._post_put_callback(m)
            return json.dumps(m)


    def _pre_delete_callback(self, m):
        pass

    def _post_delete_callback(self, id):
        pass

    @login_required
    @route('/<int:id>', methods=["DELETE"])
    def delete(self, id):
        if self.api.cache.get(self.cache_key) is not None:
            self._pre_delete_callback(self.api.cache.get(self.cache_key)[id])
            del self.api.cache.get(self.cache_key)[id]
        m = self.model.delete(id)

        def _post_delete_callback(self, id):
            pass
        return ('',204)

    @classmethod
    def post_init_callback(cls, obj):
        pass

    @classmethod
    def init_cache(cls):
        with cls.api._app.app_context():

            if cls.model.__as_array__ is True:
                cls.api.cache[cls.cache_key] = []

                for value in cls.model.get_all():
                    cls.post_init_callback(value)
                    cls.api.cache[cls.cache_key].append(value)
            else:
                cls.api.cache[cls.cache_key] = {}
                for key, value  in cls.model.get_all().iteritems():
                    cls.post_init_callback(value)
                    cls.api.cache[cls.cache_key][key] = value
