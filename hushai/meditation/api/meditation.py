"""冥想会话与进度追踪 API。"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from hushai.meditation.api.auth import get_current_user_id
from hushai.meditation.db.models import DailyProgress, MeditationSession, User
from hushai.meditation.db.session import get_session

router = APIRouter(prefix="/api/meditation", tags=["meditation"])


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _date_only(dt: datetime) -> datetime:
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


class SessionStartRequest(BaseModel):
    conversation_id: str | None = None
    scene_id: str | None = None
    mood_before: int | None = Field(default=None, ge=1, le=10)


class SessionStartResponse(BaseModel):
    session_id: str
    started_at: datetime


class SessionEndRequest(BaseModel):
    session_id: str
    mood_after: int | None = Field(default=None, ge=1, le=10)
    note: str | None = None


class SessionEndResponse(BaseModel):
    session_id: str
    duration_seconds: int
    mood_before: int | None
    mood_after: int | None


class MoodCheckInRequest(BaseModel):
    mood: int = Field(..., ge=1, le=10)


class MoodCheckInResponse(BaseModel):
    mood: int
    recorded_at: datetime


class RecentSessionItem(BaseModel):
    id: str
    started_at: str | None
    duration_seconds: int
    mood_before: int | None
    mood_after: int | None


class ProgressStatsResponse(BaseModel):
    total_sessions: int
    total_duration_seconds: int
    current_streak: int
    longest_streak: int
    today_sessions: int
    today_duration_seconds: int
    avg_mood: float | None
    recent_sessions: list[RecentSessionItem]


class DayProgress(BaseModel):
    date: str
    day_name: str
    sessions: int
    duration_seconds: int
    mood: float | None
    streak: int


class WeeklyProgressResponse(BaseModel):
    days: list[DayProgress]


_active_sessions: dict[str, datetime] = {}


@router.post("/session/start", response_model=SessionStartResponse)
async def start_session(
    req: SessionStartRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    session_id = str(uuid.uuid4())
    started_at = _utcnow()
    _active_sessions[session_id] = started_at

    session = MeditationSession(
        id=session_id,
        user_id=user_id,
        conversation_id=req.conversation_id,
        scene_id=req.scene_id,
        started_at=started_at,
        mood_before=req.mood_before,
    )
    db.add(session)
    await db.commit()

    return SessionStartResponse(session_id=session_id, started_at=started_at)


@router.post("/session/end", response_model=SessionEndResponse)
async def end_session(
    req: SessionEndRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    if req.session_id not in _active_sessions:
        raise HTTPException(status_code=404, detail="Session not found or already ended")

    started_at = _active_sessions.pop(req.session_id)
    ended_at = _utcnow()
    duration_seconds = int((ended_at - started_at).total_seconds())

    result = await db.execute(
        select(MeditationSession).where(
            MeditationSession.id == req.session_id,
            MeditationSession.user_id == user_id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.ended_at = ended_at
    session.duration_seconds = duration_seconds
    session.mood_after = req.mood_after
    session.note = req.note

    await db.commit()
    await _update_daily_progress(
        db, user_id, ended_at, session.mood_before, session.mood_after, duration_seconds
    )

    return SessionEndResponse(
        session_id=req.session_id,
        duration_seconds=duration_seconds,
        mood_before=session.mood_before,
        mood_after=session.mood_after,
    )


@router.post("/mood-checkin", response_model=MoodCheckInResponse)
async def mood_checkin(
    req: MoodCheckInRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    recorded_at = _utcnow()
    await _update_daily_progress(db, user_id, recorded_at, mood_after=req.mood)

    return MoodCheckInResponse(mood=req.mood, recorded_at=recorded_at)


async def _update_daily_progress(
    db: AsyncSession,
    user_id: str,
    dt: datetime,
    mood_before: int | None = None,
    mood_after: int | None = None,
    duration: int = 0,
):
    date_key = _date_only(dt)

    result = await db.execute(
        select(DailyProgress).where(
            DailyProgress.user_id == user_id,
            func.date(DailyProgress.date) == date_key.date(),
        )
    )
    dp = result.scalar_one_or_none()

    if not dp:
        dp = DailyProgress(
            id=str(uuid.uuid4()),
            user_id=user_id,
            date=date_key,
            meditation_count=0,
            total_duration_seconds=0,
        )
        db.add(dp)

    dp.meditation_count += 1
    dp.total_duration_seconds += duration

    mood_val = mood_after if mood_after is not None else mood_before
    if mood_val is not None:
        old_count = dp.meditation_count - 1
        if old_count > 0 and dp.mood_avg is not None:
            dp.mood_avg = (dp.mood_avg * old_count + mood_val) / dp.meditation_count
        else:
            dp.mood_avg = float(mood_val)

    yesterday = date_key - timedelta(days=1)
    y_result = await db.execute(
        select(DailyProgress).where(
            DailyProgress.user_id == user_id,
            func.date(DailyProgress.date) == yesterday.date(),
        )
    )
    y_dp = y_result.scalar_one_or_none()
    dp.streak_day = (y_dp.streak_day + 1) if y_dp and y_dp.meditation_count > 0 else 1

    await db.commit()


@router.get("/stats", response_model=ProgressStatsResponse)
async def get_stats(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    today = _date_only(_utcnow())

    total_result = await db.execute(
        select(
            func.count(MeditationSession.id),
            func.coalesce(func.sum(MeditationSession.duration_seconds), 0),
            func.coalesce(func.avg(MeditationSession.mood_after), 0),
        ).where(MeditationSession.user_id == user_id)
    )
    total_row = total_result.one()
    total_sessions = total_row[0] or 0
    total_duration = int(total_row[1] or 0)
    avg_mood = float(total_row[2]) if total_row[2] and total_row[2] > 0 else None

    today_result = await db.execute(
        select(
            func.count(MeditationSession.id),
            func.coalesce(func.sum(MeditationSession.duration_seconds), 0),
        ).where(
            MeditationSession.user_id == user_id,
            func.date(MeditationSession.started_at) == today.date(),
        )
    )
    today_row = today_result.one()
    today_sessions = today_row[0] or 0
    today_duration = int(today_row[1] or 0)

    streak_result = await db.execute(
        select(DailyProgress)
        .where(DailyProgress.user_id == user_id)
        .order_by(DailyProgress.date.desc())
        .limit(365)
    )
    dps = streak_result.scalars().all()

    current_streak = 0
    longest_streak = 0
    running_streak = 0
    prev_date: datetime | None = None

    for dp in dps:
        if prev_date is None:
            if (
                dp.date.date() == today.date()
                or dp.date.date() == (today - timedelta(days=1)).date()
            ):
                if dp.meditation_count > 0:
                    running_streak = dp.streak_day
                    current_streak = dp.streak_day
        else:
            expected = prev_date - timedelta(days=1)
            if dp.date.date() == expected.date() and dp.meditation_count > 0:
                running_streak = dp.streak_day
                longest_streak = max(longest_streak, running_streak)
            else:
                longest_streak = max(longest_streak, running_streak)
                running_streak = 0
        prev_date = dp.date

    longest_streak = max(longest_streak, running_streak)

    recent_result = await db.execute(
        select(MeditationSession)
        .where(MeditationSession.user_id == user_id)
        .order_by(MeditationSession.started_at.desc())
        .limit(5)
    )
    recent_sessions = [
        RecentSessionItem(
            id=s.id,
            started_at=s.started_at.isoformat() if s.started_at else None,
            duration_seconds=s.duration_seconds,
            mood_before=s.mood_before,
            mood_after=s.mood_after,
        )
        for s in recent_result.scalars().all()
    ]

    return ProgressStatsResponse(
        total_sessions=total_sessions,
        total_duration_seconds=total_duration,
        current_streak=current_streak,
        longest_streak=longest_streak,
        today_sessions=today_sessions,
        today_duration_seconds=today_duration,
        avg_mood=avg_mood,
        recent_sessions=recent_sessions,
    )


@router.get("/weekly", response_model=WeeklyProgressResponse)
async def get_weekly(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    today = _date_only(_utcnow())
    days = []

    day_names = ["日", "一", "二", "三", "四", "五", "六"]

    for i in range(6, -1, -1):
        target_date = today - timedelta(days=i)
        result = await db.execute(
            select(DailyProgress).where(
                DailyProgress.user_id == user_id,
                func.date(DailyProgress.date) == target_date.date(),
            )
        )
        dp = result.scalar_one_or_none()

        days.append(
            DayProgress(
                date=target_date.strftime("%m-%d"),
                day_name=day_names[target_date.weekday()],
                sessions=dp.meditation_count if dp else 0,
                duration_seconds=dp.total_duration_seconds if dp else 0,
                mood=dp.mood_avg if dp else None,
                streak=dp.streak_day if dp else 0,
            )
        )

    return WeeklyProgressResponse(days=days)
