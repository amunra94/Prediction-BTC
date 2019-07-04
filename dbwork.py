import sqlalchemy


class DataBase:
    def __init__(self, name_db):
        self.engine = sqlalchemy.create_engine('sqlite:///' + name_db, echo=False)
        self.metadata = sqlalchemy.MetaData()

    def init_user_table(self, name_tab):
        self.users_table = sqlalchemy.Table(name_tab, self.metadata,
                                            sqlalchemy.Column('user_id', sqlalchemy.Integer, primary_key=True),
                                            sqlalchemy.Column('chat_id', sqlalchemy.Integer),
                                            sqlalchemy.Column('first_name', sqlalchemy.String),
                                            sqlalchemy.Column('last_name', sqlalchemy.String),
                                            sqlalchemy.Column('username', sqlalchemy.String),
                                            )

        self.metadata.create_all(bind=self.engine)

    def init_email_table(self, name_tab):
        self.emails_table = sqlalchemy.Table(name_tab, self.metadata,
                                            sqlalchemy.Column('email', sqlalchemy.String))

        self.metadata.create_all(bind=self.engine)

    def push_email(self, name_tab, email):
        with self.engine.connect() as conn:
            meta = sqlalchemy.MetaData(self.engine)
            emails_table = sqlalchemy.Table(name_tab, meta, autoload=True)

            conn.execute(emails_table.insert(), email=email)

    def push_user(self, name_tab, user_id, chat_id, first_name, last_name, username):
        with self.engine.connect() as conn:
            meta = sqlalchemy.MetaData(self.engine)
            users_table = sqlalchemy.Table(name_tab, meta, autoload=True)

            conn.execute(users_table.insert(),
                         user_id=user_id,
                         chat_id=chat_id,
                         first_name=first_name,
                         last_name=last_name,
                         username=username,
                         )

    def get_users_id(self, name_tab):
        with self.engine.connect() as conn:
            meta = sqlalchemy.MetaData(self.engine)
            users_table = sqlalchemy.Table(name_tab, meta, autoload=True)
            records = conn.execute(sqlalchemy.select([users_table.c.user_id]))
            rows = list(records)
        return rows

    def get_emails(self, name_tab):
        with self.engine.connect() as conn:
            meta = sqlalchemy.MetaData(self.engine)
            emails_table = sqlalchemy.Table(name_tab, meta, autoload=True)
            records = conn.execute(sqlalchemy.select([emails_table.c.email]))
            rows = list(records)
        return rows

    def get_users(self, name_tab):
        with self.engine.connect() as conn:
            meta = sqlalchemy.MetaData(self.engine)
            users_table = sqlalchemy.Table(name_tab, meta, autoload=True)
            records = conn.execute(sqlalchemy.select([users_table]))
            rows = list(records)[:10]
        return rows

    def check_user(self, name_tab, user_id):
        with self.engine.connect() as conn:
            meta = sqlalchemy.MetaData(self.engine)
            users_table = sqlalchemy.Table(name_tab, meta, autoload=True)
            t_uid = (user_id,)
            records = conn.execute(sqlalchemy.select([users_table.c.user_id]).where(users_table.c.user_id == user_id))

            if t_uid in records:
                return True
            else:
                return False

    def get_last_sent(self, name_tab):
        with self.engine.connect() as conn:
            meta = sqlalchemy.MetaData(self.engine)
            sent_table = sqlalchemy.Table(name_tab, meta, autoload=True)
            records = conn.execute(sqlalchemy.select([sqlalchemy.func.max(sent_table.c.date)]))
            rows = list(records)
            return rows
