from peewee import PostgresqlDatabase, Model
from playhouse.shortcuts import ReconnectMixin

import config as cfg


class Database(ReconnectMixin, PostgresqlDatabase):
    ...


db = Database(cfg.DB.db_name, user=cfg.DB.user, password=cfg.DB.password,
              host=cfg.DB.host, port=cfg.DB.port, autoconnect=False)


class BaseModel(Model):
    class Meta:
        database = db
