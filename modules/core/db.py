import sqlite3

from flask import json, g


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d
        db = g._database = sqlite3.connect('craftbeerpi.db')
        db.row_factory = dict_factory
    return db

class DBModel(object):

    __priamry_key__ = "id"
    __as_array__ = False
    __order_by__ = None
    __json_fields__ = []

    def __init__(self, args):

       self.__setattr__(self.__priamry_key__, args.get(self.__priamry_key__))
       for f in self.__fields__:
           if f in self.__json_fields__:
               if  args.get(f) is not None:

                   if isinstance(args.get(f) , dict) or isinstance(args.get(f) , list) :
                       self.__setattr__(f, args.get(f))
                   else:
                       self.__setattr__(f, json.loads(args.get(f)))
               else:
                   self.__setattr__(f, None)
           else:
               self.__setattr__(f, args.get(f))

    @classmethod
    def get_all(cls):
        cur = get_db().cursor()
        if cls.__order_by__ is not None:

            cur.execute("SELECT * FROM %s ORDER BY %s.'%s'" % (cls.__table_name__,cls.__table_name__,cls.__order_by__))
        else:
            cur.execute("SELECT * FROM %s" % cls.__table_name__)

        if cls.__as_array__ is True:
            result = []
            for r in cur.fetchall():

                result.append( cls(r))
        else:
            result = {}
            for r in cur.fetchall():
                result[r.get(cls.__priamry_key__)] = cls(r)
        return result

    @classmethod
    def get_one(cls, id):
        cur = get_db().cursor()
        cur.execute("SELECT * FROM %s WHERE %s = ?" % (cls.__table_name__, cls.__priamry_key__), (id,))
        r = cur.fetchone()
        if r is not None:
            return cls(r)
        else:
            return None

    @classmethod
    def delete(cls, id):
        cur = get_db().cursor()
        cur.execute("DELETE FROM %s WHERE %s = ? " % (cls.__table_name__, cls.__priamry_key__), (id,))
        get_db().commit()

    @classmethod
    def insert(cls, **kwargs):
        cur = get_db().cursor()


        if cls.__priamry_key__ is not None and kwargs.has_key(cls.__priamry_key__):
            query = "INSERT INTO %s (%s, %s) VALUES (?, %s)" % (
                cls.__table_name__,
                cls.__priamry_key__,
                ', '.join("'%s'" % str(x) for x in cls.__fields__),
                ', '.join(['?'] * len(cls.__fields__)))
            data = ()
            data = data + (kwargs.get(cls.__priamry_key__),)
            for f in cls.__fields__:
                if f in cls.__json_fields__:
                    data = data + (json.dumps(kwargs.get(f)),)
                else:
                    data = data + (kwargs.get(f),)
        else:

            query = 'INSERT INTO %s (%s) VALUES (%s)' % (
                cls.__table_name__,
                ', '.join("'%s'" % str(x) for x in cls.__fields__),
                ', '.join(['?'] * len(cls.__fields__)))

            data = ()
            for f in cls.__fields__:
                if f in cls.__json_fields__:
                    data = data + (json.dumps(kwargs.get(f)),)
                else:
                    data = data + (kwargs.get(f),)


        cur.execute(query, data)
        get_db().commit()
        i = cur.lastrowid
        kwargs["id"] = i

        return cls(kwargs)

    @classmethod
    def update(cls, **kwargs):
        cur = get_db().cursor()
        query = 'UPDATE %s SET %s WHERE %s = ?' % (
            cls.__table_name__,
            ', '.join("'%s' = ?" % str(x) for x in cls.__fields__),cls.__priamry_key__)

        data = ()
        for f in cls.__fields__:
            if f in cls.__json_fields__:
                data = data + (json.dumps(kwargs.get(f)),)
            else:
                data = data + (kwargs.get(f),)

        data = data + (kwargs.get(cls.__priamry_key__),)
        cur.execute(query, data)
        get_db().commit()
        return cls(kwargs)