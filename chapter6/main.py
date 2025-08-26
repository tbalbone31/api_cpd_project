"""FastAPI program - Chapter 4"""
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date

import crud
import schemas
from database import SessionLocal

api_description = """
This API provides read-only access to info from the SportsWorldCentral
(SWC) Fantasy Football API.
The endpoints are grouped into the following categories:

## Analytics
Get information about the health of the API and counts of leagues, teams,
and players.

## Player
You can get a list of NFL players, or search for an individual player by
player_id.

## Scoring
You can get a list of NFL player performances, including the fantasy points
they scored using SWC league scoring.

## Membership
Get information about all the SWC fantasy football leagues and the teams in them.
"""

# FastAPI constructor with additional details added for OpenAPI Specification
app = FastAPI(
    description=api_description,
    title="Sports World Central (SWC) Fantasy Football API",
    version="0.1"
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", tags=["analytics"])
async def root():
    return {"message": "API health check successful"}


@app.get(
    "/v0/players/",
    response_model=list[schemas.Player],
    tags=["player"],
    summary="Get a list of NFL players",
    description="Retrieve a list of NFL players with optional filtering by various parameters.",
    operation_id="v0_get_players"
)
def read_players(
    skip: int = Query(0, description="The number of items to skip at the beginning of API call."),
    limit: int = Query(100, description="The number of records to return after the skipped records."),
    minimum_last_changed_date: date = Query(None, description="The minimum date of change that you want to return records. Exclude any records changed before this."),
    first_name: str = Query(None, description="The first name of the players to return"),
    last_name: str = Query(None, description="The last name of the players to return"),
    db: Session = Depends(get_db)
):
    players = crud.get_players(
        db,
        skip=skip,
        limit=limit,
        min_last_changed_date=minimum_last_changed_date,
        first_name=first_name,
        last_name=last_name
    )
    return players


@app.get(
    "/v0/players/{player_id}",
    response_model=schemas.Player,
    tags=["player"],
    summary="Get one player using the Player ID, which is internal to SWC",
    description="If you have an SWC Player ID of a player from another API call such as v0_get_players, you can call this API using the player ID",
    response_description="One NFL player",
    operation_id="v0_get_players_by_player_id"
)
def read_player(
    player_id: int,
    db: Session = Depends(get_db)
):
    player = crud.get_player(db, player_id=player_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@app.get(
    "/v0/performances/",
    response_model=list[schemas.Performance],
    tags=["scoring"],
    summary="Get a list of NFL player performances",
    description="Retrieve a list of NFL player performances with optional filtering by various parameters.",
    response_description="A list of NFL player performances",
    operation_id="v0_get_performances"
)
def read_performances(
    skip: int = Query(
        0, description="The number of items to skip at the beginning of API call."
    ),
    limit: int = Query(
        100, description="The number of records to return after the skipped records."
    ),
    minimum_last_changed_date: date = Query(
        None,
        description="The minimum data of change that you want to return records. Exclude any records changed before this.",
    ),
    db: Session = Depends(get_db),
):
    performances = crud.get_performances(
        db, skip=skip, limit=limit, min_last_changed_date=minimum_last_changed_date
    )
    return performances


@app.get(
    "/v0/leagues/{league_id}",
    response_model=schemas.League,
    tags=["membership"],
    summary="Get one league using the League ID, which is internal to SWC",
    description="If you have an SWC League ID of a league from another API call such as v0_get_leagues, you can call this API using the league ID",
    response_description="One SWC league",
    operation_id="v0_get_leagues_by_league_id"
)
def read_league(
    league_id: int,
    db: Session = Depends(get_db)
):
    league = crud.get_league(db, league_id=league_id)
    if league is None:
        raise HTTPException(status_code=404, detail="League not found")
    return league


@app.get(
    "/v0/leagues/",
    response_model=list[schemas.League],
    tags=["membership"],
    summary="Get a list of SWC leagues",
    description="Retrieve a list of SWC leagues with optional filtering by various parameters.",
    response_description="A list of SWC leagues",
    operation_id="v0_get_leagues"
)
def read_leagues(
    skip: int = Query(
        0, description="The number of items to skip at the beginning of API call."
    ),
    limit: int = Query(
        100, description="The number of records to return after the skipped records."
    ),
    minimum_last_changed_date: date = Query(
        None,
        description="The minimum data of change that you want to return records. Exclude any records changed before this.",
    ),
    league_name: str = Query(
        None, description="Name of the leagues to return. Not unique in the SWC."
    ),
    db: Session = Depends(get_db),
):
    leagues = crud.get_leagues(
        db,
        skip=skip,
        limit=limit,
        min_last_changed_date=minimum_last_changed_date,
        league_name=league_name,
    )
    return leagues


@app.get(
    "/v0/teams/",
    response_model=list[schemas.Team],
    tags=["membership"],
    summary="Get a list of SWC teams",
    description="Retrieve a list of SWC teams with optional filtering by various parameters.",
    response_description="A list of SWC teams",
    operation_id="v0_get_teams"
)
def read_teams(
    skip: int = Query(
        0, description="The number of items to skip at the beginning of API call."
    ),
    limit: int = Query(
        100, description="The number of records to return after the skipped records."
    ),
    minimum_last_changed_date: date = Query(
        None,
        description="The minimum data of change that you want to return records. Exclude any records changed before this.",
    ),
    team_name: str = Query(
        None,
        description="Name of the teams to return. Not unique across SWC, but is unique inside a league.",
    ),
    league_id: int = Query(
        None, description="League ID of the teams to return. Unique in SWC."
    ),
    db: Session = Depends(get_db),
):
    teams = crud.get_teams(
        db,
        skip=skip,
        limit=limit,
        min_last_changed_date=minimum_last_changed_date,
        team_name=team_name,
        league_id=league_id,
    )
    return teams


@app.get(
    "/v0/counts/",
    response_model=schemas.Counts,
    tags=["analytics"],
    summary="Get counts of various SWC entities",
    description="Retrieve counts of leagues, teams, and players in the SWC.",
    response_description="Counts of SWC entities",
    operation_id="v0_get_counts"
)
def get_count(db: Session = Depends(get_db)):
    counts = schemas.Counts(
        league_count=crud.get_league_count(db),
        team_count=crud.get_team_count(db),
        player_count=crud.get_player_count(db)
    )
    return counts