import json
import pathlib
from typing import List, Union

from fastapi import FastAPI, Response, Depends
from sqlmodel import Session, select

from models import Track
from database import TrackModel, engine

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    DATAFILE = pathlib.Path() / 'data' / 'tracks.json'

    # create a Session scoped to the startup event
    # Note: we can also use a context manager
    session = Session(engine)

    # check if the database is already populated
    stmt = select(TrackModel)
    result = session.exec(stmt).first()

    # Load data if there's no results
    if result is None:
        with open(DATAFILE, 'r') as f:
            tracks = json.load(f)
            for track in tracks:
                session.add(TrackModel(**track))

        session.commit()
    session.close()

def get_session():
    with Session(engine) as session:
        yield session
@app.get('/tracks/', response_model = List[Track])
def tracks(session: Session = Depends(get_session)):
    stmt = select(TrackModel)
    result = session.exec(stmt).all()
    return result

@app.get('/tracks/{track_id}/', response_model = Union[Track, str])
def track(track_id: int, response: Response, session: Session = Depends(get_session)):
    track = session.get(TrackModel, track_id)

    if track is None:
        response.status_code = 404
        return "Track Not Found"

    return track

@app.post("/tracks/", response_model=Track, status_code=201)
def create_track(track: TrackModel, session: Session = Depends(get_session)):
    session.add(track)
    session.commit()
    session.refresh(track)
    return track

@app.put('/tracks/{track_id}/', response_model=Union[Track, str])
def update_track(track_id: int, updated_track: Track, response: Response, session: Session = Depends(get_session)):
    track = session.get(TrackModel, track_id)
    if track is None:
        response.status_code = 404
        return "Track Not Found"

    # update the track data
    track_dict = updated_track.dict(exclude_unset=True)
    for key, val in track_dict.items():
        setattr(track, key, val)

    session.add(track)
    session.commit()
    session.refresh(track)
    return track

@app.delete('/tracks/{track_id}/')
def delete_track(track_id: int, response: Response, session: Session = Depends(get_session)):

    track = session.get(TrackModel, track_id)

    if track is None:
        response.status_code = 404
        return "Track Not Found"

    session.delete(track)
    session.commit()
    return Response(status_code=200)