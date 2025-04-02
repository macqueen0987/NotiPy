from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from var import dbhost, dbport, dbuser, dbpassword, dbname

engine = create_async_engine(f"mysql+aiomysql://{dbuser}:{dbpassword}@{dbhost}:{dbport}/{dbname}", echo=False, future=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)
async def get_db():
    async with async_session() as session:
        yield session