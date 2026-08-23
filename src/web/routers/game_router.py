from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from web.schemas.game import (
    CreateGameRequest, GameResponse, JoinGameResponse,
    MoveRequest, HistoryGameResponse, LeaderboardPlayer
)
from web.security.auth import get_db
from web.security.jwt import get_current_user_from_cookie
from datasource.model.user_model import UserModel
from di.database import SessionLocal
from datasource.repository.game_repository import SQLAlchemyGameRepository
from domain.service.game_service import GameServiceImpl
from domain.model.game_status import GameStatus
from typing import List
import jwt

router = APIRouter(tags=["Игры"])
templates = Jinja2Templates(directory="templates")


def get_game_service(db: SessionLocal = Depends(get_db)):
    repo = SQLAlchemyGameRepository(db)
    return GameServiceImpl(repo)


def check_auth_and_redirect(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/auth/login", status_code=303)
    try:
        from web.security.jwt import SECRET_KEY, ALGORITHM
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("uuid")
    except jwt.PyJWTError:
        return RedirectResponse(url="/auth/login", status_code=303)


@router.post("/games", response_model=GameResponse, status_code=201)
def create_game_api(
        request: CreateGameRequest,
        current_user: UserModel = Depends(get_current_user_from_cookie),
        service: GameServiceImpl = Depends(get_game_service)
):
    game = service.create_game(str(current_user.uuid), request.mode)
    return GameResponse(uuid=str(game.uuid), mode=game.mode, status=game.status.value, message="Игра создана")


@router.get("/games", response_model=List[GameResponse])
def get_available_games_api(
    service: GameServiceImpl = Depends(get_game_service)
):
    games = service.get_available_games()
    return [GameResponse(uuid=str(g.uuid), mode=g.mode, status=g.status.value) for g in games]

@router.post("/games/{game_uuid}/join", response_model=JoinGameResponse)
def join_game_api(
        game_uuid: str,
        current_user: UserModel = Depends(get_current_user_from_cookie),
        service: GameServiceImpl = Depends(get_game_service)
):
    try:
        game = service.join_game(game_uuid, str(current_user.uuid))
        return JoinGameResponse(uuid=str(game.uuid), status=game.status.value, message="Вы присоединились")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/game/{game_uuid}")
def make_move_api(
        game_uuid: str,
        move: MoveRequest,
        current_user: UserModel = Depends(get_current_user_from_cookie),
        service: GameServiceImpl = Depends(get_game_service)
):
    try:
        game = service.make_move(game_uuid, str(current_user.uuid), move.field)
        return {"message": "Ход принят", "status": game.status.value}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/games/history", response_model=List[HistoryGameResponse])
def get_history_api(
        current_user: UserModel = Depends(get_current_user_from_cookie),
        service: GameServiceImpl = Depends(get_game_service)
):
    games = service.get_finished_games_by_user(str(current_user.uuid))
    return [
        HistoryGameResponse(
            uuid=str(g.uuid), mode=g.mode, status=g.status.value,
            created_at=g.created_at.isoformat() if g.created_at else None,
            player1_uuid=g.player1_uuid, player2_uuid=g.player2_uuid
        ) for g in games
    ]


@router.get("/leaderboard", response_model=List[LeaderboardPlayer])
def get_leaderboard_api(
        n: int = 10,
        current_user: UserModel = Depends(get_current_user_from_cookie),
        service: GameServiceImpl = Depends(get_game_service),
        db: SessionLocal = Depends(get_db)
):
    stats = service.get_top_players(n)
    players = []
    for stat in stats:
        user = db.query(UserModel).filter(UserModel.uuid == stat['user_uuid']).first()
        players.append(LeaderboardPlayer(
            login=user.login if user else "Unknown",
            wins=stat['total_wins'],
            losses_draws=stat['total_losses_draws'],
            win_ratio=round(stat['win_ratio'], 2)
        ))
    return players



@router.get("/games/new", response_class=HTMLResponse)
def create_game_page(request: Request):
    return templates.TemplateResponse(request, name="create_game.html", context={})


@router.post("/games/new", response_class=RedirectResponse)
def create_game_from_form(
        request: Request,
        mode: str = Form(...),
        service: GameServiceImpl = Depends(get_game_service)
):
    user_uuid = check_auth_and_redirect(request)
    if isinstance(user_uuid, RedirectResponse):
        return user_uuid

    game = service.create_game(user_uuid, mode)
    return RedirectResponse(url=f"/game/{game.uuid}", status_code=303)


@router.get("/games/lobby", response_class=HTMLResponse)
def lobby_page(
        request: Request,
        service: GameServiceImpl = Depends(get_game_service)
):
    all_games = service.get_available_games()

    token = request.cookies.get("access_token")
    user_uuid = None

    if token:
        try:
            import jwt
            from web.security.jwt import SECRET_KEY, ALGORITHM
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_uuid = payload.get("uuid")
        except jwt.PyJWTError:
            pass

    if user_uuid:
        games = [game for game in all_games if str(game.player1_uuid) != user_uuid]
    else:
        games = all_games

    return templates.TemplateResponse(
        request,
        name="lobby.html",
        context={"games": games}
    )


@router.get("/game/{game_uuid}", response_class=HTMLResponse)
def game_page(
        request: Request,
        game_uuid: str,
        service: GameServiceImpl = Depends(get_game_service)
):
    user_uuid = check_auth_and_redirect(request)
    if isinstance(user_uuid, RedirectResponse):
        return user_uuid

    game = service.get_game(game_uuid)
    if not game:
        raise HTTPException(status_code=404, detail="Игра не найдена")

    winner = None
    if game.status == GameStatus.WIN:
        if game.get_winner_uuid() == game.player1_uuid:
            winner = 1
        elif game.get_winner_uuid() == game.player2_uuid:
            winner = 2
    elif game.status == GameStatus.DRAW:
        winner = 0

    is_player1 = (user_uuid == str(game.player1_uuid))
    is_player2 = (user_uuid == str(game.player2_uuid))

    if game.status.value == 'waiting':
        is_my_turn = False
    elif game.mode == 'pve':
        is_my_turn = (game.status.value == 'in_progress')
    else:
        is_my_turn = (user_uuid == str(game.current_player_uuid))

    my_symbol = 1 if is_player1 else 2

    return templates.TemplateResponse(request, name="game.html", context={
        "game_uuid": game.uuid,
        "board": game.board.field,
        "winner": winner,
        "game_status": game.status.value,
        "is_my_turn": is_my_turn,
        "game_mode": game.mode,
        "is_player1": is_player1,
        "is_player2": is_player2,
        "my_symbol": my_symbol
    })


@router.get("/history", response_class=HTMLResponse)
def history_page(
        request: Request,
        service: GameServiceImpl = Depends(get_game_service)
):
    user_uuid = check_auth_and_redirect(request)
    if isinstance(user_uuid, RedirectResponse):
        return user_uuid

    games = service.get_finished_games_by_user(user_uuid)
    return templates.TemplateResponse(
        request,
        name="history.html",
        context={
            "games": games,
            "user_uuid": user_uuid
        }
    )


@router.get("/leaderboard_page", response_class=HTMLResponse)
def leaderboard_page_html(
        request: Request,
        n: int = 10,
        service: GameServiceImpl = Depends(get_game_service),
        db: SessionLocal = Depends(get_db)
):
    stats = service.get_top_players(n)
    players = []
    for stat in stats:
        user = db.query(UserModel).filter(UserModel.uuid == stat['user_uuid']).first()
        players.append({
            "login": user.login if user else "Unknown",
            "wins": stat['total_wins'],
            "losses_draws": stat['total_losses_draws'],
            "win_ratio": round(stat['win_ratio'], 2)
        })
    return templates.TemplateResponse(request, name="leaderboard.html", context={"players": players})