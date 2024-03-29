"""Provides database storage for the Dozer Discord bot"""
import logging

import asyncpg

CHATBOT_LOGGER = logging.getLogger(__name__)

Pool = None


async def db_init(db_url):
    """Initializes the database connection"""
    global Pool
    Pool = await asyncpg.create_pool(dsn=db_url, command_timeout=15)


async def db_migrate():
    """Gets all subclasses and checks their migrations."""
    async with Pool.acquire() as conn:
        await conn.execute("""CREATE TABLE IF NOT EXISTS versions (
        table_name text PRIMARY KEY,
        version_num int NOT NULL
        )""")
    CHATBOT_LOGGER.info("Checking for db migrations")
    for cls in DatabaseTable.__subclasses__():
        exists = await Pool.fetchrow("""SELECT EXISTS(
        SELECT 1
        FROM information_schema.tables
        WHERE
        table_name = $1)""", cls.__tablename__)
        if exists['exists']:
            version = await Pool.fetchrow("""SELECT version_num FROM versions WHERE table_name = $1""",
                                          cls.__tablename__)
            if version is None:
                # Migration/creation required, go to the function in the subclass for it
                await cls.initial_migrate()
                version = {"version_num": 0}
            if int(version["version_num"]) < len(cls.__versions__):
                # the version in the DB is less than the version in the bot, run all the migrate scripts necessary
                CHATBOT_LOGGER.info(
                    f"Table {cls.__tablename__} is out of date attempting to migrate")
                for i in range(int(version["version_num"]), len(cls.__versions__)):
                    # Run the update script for this version!
                    await cls.__versions__[i](cls)
                    CHATBOT_LOGGER.info(
                        f"Successfully updated table {cls.__tablename__} from version {i} to {i + 1}")
                async with Pool.acquire() as conn:
                    await conn.execute("""UPDATE versions SET version_num = $1 WHERE table_name = $2""",
                                       len(cls.__versions__), cls.__tablename__)
        else:
            await cls.initial_create()
            await cls.initial_migrate()


class DatabaseTable:
    """Defines a database table"""
    __tablename__ = None
    __versions__ = []
    __uniques__ = []

    # Declare the migrate/create functions
    @classmethod
    async def initial_create(cls):
        """Create the table in the database"""
        raise NotImplementedError("Database schema not implemented!")

    @classmethod
    async def initial_migrate(cls):
        """Create a version entry in the versions table"""
        async with Pool.acquire() as conn:
            await conn.execute("""INSERT INTO versions VALUES ($1, 0)""", cls.__tablename__)

    @staticmethod
    def nullify():
        """Function to be referenced when a table entry value needs to be set to null"""

    async def update_or_add(self):
        """Assign the attribute to this object, then call this method to either insert the object if it doesn't exist in
        the DB or update it if it does exist. It will update every column not specified in __uniques__."""
        keys = []
        values = []
        for var, value in self.__dict__.items():
            # Done so that the two are guaranteed to be in the same order, which isn't true of keys() and values()
            if value is self.nullify:
                keys.append(var)
                values.append(None)
            elif value is not None:
                keys.append(var)
                values.append(value)

        updates = ""
        for key in keys:
            if key in self.__uniques__:
                # Skip updating anything that has a unique constraint on it
                continue
            updates += f"{key} = EXCLUDED.{key}"
            if keys.index(key) == len(keys) - 1:
                updates += " ;"
            else:
                updates += ", \n"
        async with Pool.acquire() as conn:
            if updates:
                statement = f"""
                INSERT INTO {self.__tablename__} ({", ".join(keys)})
                VALUES({','.join(f'${i + 1}' for i in range(len(values)))})
                ON CONFLICT ({self.__uniques__}) DO UPDATE
                SET {updates}
                """
            else:
                statement = f"""
                INSERT INTO {self.__tablename__} ({", ".join(keys)})
                VALUES({','.join(f'${i + 1}' for i in range(len(values)))})
                ON CONFLICT ({self.__uniques__}) DO NOTHING;
                """
            await conn.execute(statement, *values)

    def __repr__(self):
        values = ""
        first = True
        for key, value in self.__dict__.items():
            if not first:
                values += ", "
                first = False
            values += f"{key}: {value}"
        return f"{self.__tablename__}: <{values}>"

    # Class Methods

    @classmethod
    async def get_by(cls, **filters):
        """Get a list of all records matching the given column=value criteria. This will grab all attributes, it's more
        efficent to write your own SQL queries than use this one, but for a simple query this is fine."""
        async with Pool.acquire() as conn:
            statement = f"SELECT * FROM {cls.__tablename__}"
            if filters:
                # note: this code relies on subsequent iterations of the same dict having the same iteration order.
                # This is an implementation detail of CPython 3.6 and a language guarantee in Python 3.7+.
                conditions = " AND ".join(
                    f"{column_name} = ${i + 1}" for (i, column_name) in enumerate(filters))
                statement = f"{statement} WHERE {conditions};"
            else:
                statement += ";"
            return await conn.fetch(statement, *filters.values())

    @classmethod
    async def delete(cls, **filters):
        """Deletes by any number of criteria specified as column=value keyword arguments. Returns the number of entries deleted"""
        async with Pool.acquire() as conn:
            if filters:
                # This code relies on properties of dicts - see get_by
                conditions = " AND ".join(
                    f"{column_name} = ${i + 1}" for (i, column_name) in enumerate(filters))
                statement = f"DELETE FROM {cls.__tablename__} WHERE {conditions};"
            else:
                # Should this be a warning/error? It's almost certainly not intentional
                statement = f"TRUNCATE {cls.__tablename__};"
            return await conn.execute(statement, *filters.values())

    @classmethod
    async def set_initial_version(cls):
        """Sets initial version"""
        await Pool.execute("""INSERT INTO versions (table_name, version_num) VALUES ($1,$2)""", cls.__tablename__, 0)
