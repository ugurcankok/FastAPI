from typing import Optional

from sqlmodel import Field, SQLModel, create_engine

DB_FILE = 'db.sqlite3'
engine = create_engine(f"sqlite:///{DB_FILE}", echo=True)

class TrackModel(SQLModel, table=True):
    # Note: Optional fields are marked as Nullable in the database
    __tablename__ = 'track'
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    artist: str
    duration: float

def create_tables():
    SQLModel.metadata.create_all(engine)

if __name__ == '__main__':
    create_tables()