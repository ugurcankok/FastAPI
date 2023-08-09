import json
import pathlib
from typing import List, Union

from fastapi import FastAPI, Response

from models import Track

# instantiate the FastAPI app
app = FastAPI()

data = [] # to load data

# to signify that this function should be triggered when the application is first started with uvicorn,
# to run application, we use uvicorn main:app but when you changed something and automatically run uvicorn main:app --reload
@app.on_event("startup")
async def startup_event():
    data_path = pathlib.Path() / 'data' / 'tracks.json'
    with open(data_path, 'r') as f:
        tracks = json.load(f)
        for track in tracks:
            data.append(Track(**track).dict())

@app.get('/tracks/', response_model=List[Track])
def tracks():
    return data


@app.get('/tracks/{track_id}/', response_model=Union[Track, str])
def track(track_id: int, response: Response):
    track = None

    for t in data:
        if t['id'] == track_id:
            track = t
            break

    if track is None:
        response.status_code = 404
        return "Track Not Found"

    return track

@app.post("/tracks/", response_model=Track, status_code=201)
def create_track(track: Track):
    track_dict = track.dict()

    # assign track next sequential ID
    track_dict['id'] = max(data, key=lambda x: x['id']).get('id') + 1

    # append the track to our data and return 201 response with created resource
    data.append(track_dict)

    return track_dict

@app.put('/tracks/{track_id}/', response_model=Union[Track, str])
def update_track(track_id: int, updated_track: Track, response: Response):
    track = None

    for t in data:
        if t['id'] == track_id:
            track = t
            break

    if track is None:
        response.status_code = 404
        return "Track Not Found"

    # update the track data
    for key, val in updated_track.dict().items():
        if key != 'id':  # don't reset the ID
            track[key] = val

    return track

@app.delete('/tracks/{track_id}/')
def delete_track(track_id: int, response: Response):
    track_index = None

    for idx, t in enumerate(data):
        if t['id'] == track_id:
            track_index = idx
            break

    if track_index is None:
        response.status_code = 404
        return "Track Not Found"

    # delete the track from the data, and return empty 200 response
    del data[track_index]
    return Response(status_code=200)