"""Provides access to the Things data store."""

from typing import Any, Dict, Optional

from werkzeug.local import LocalProxy
from sqlalchemy.exc import OperationalError

from zero.domain import Thing
from .models import db, DBThing


def init_app(app: Optional[LocalProxy]) -> None:
    """Set configuration defaults and attach session to the application."""
    db.init_app(app)


def get_a_thing(id: int) -> Optional[Thing]:
    """
    Get data about a thing.

    Parameters
    ----------
    id : int
        Unique identifier for the thing.

    Returns
    -------
    :class:`.Thing`
        Data about the thing.

    Raises
    ------
    IOError
        When there is a problem querying the database.

    """
    try:
        thing_data = db.session.query(DBThing).get(id)
    except OperationalError as e:
        raise IOError('Could not query database: %s' % e.detail) from e
    if thing_data is None:
        return None
    return Thing(id=thing_data.id, name=thing_data.name,    # type: ignore
                 created=thing_data.created)


def store_a_thing(the_thing: Thing) -> Thing:
    """
    Create a new record for a :class:`.Thing` in the database.

    Parameters
    ----------
    the_thing : :class:`.Thing`

    Raises
    ------
    IOError
        When there is a problem querying the database.
    RuntimeError
        When there is some other problem.
    """
    thing_data = DBThing(name=the_thing.name, created=the_thing.created)    # type: ignore
    try:
        db.session.add(thing_data)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise RuntimeError('Ack! %s' % e) from e
    the_thing.id = thing_data.id
    return the_thing


def update_a_thing(the_thing: Thing) -> None:
    """
    Update the database with the latest :class:`.Thing`.

    Parameters
    ----------
    the_thing : :class:`.Thing`

    Raises
    ------
    IOError
        When there is a problem querying the database.
    RuntimeError
        When there is some other problem.
    """
    if not the_thing.id:
        raise RuntimeError('The thing has no id!')
    try:
        thing_data = db.session.query(DBThing).get(the_thing.id)
    except OperationalError as e:
        raise IOError('Could not query database: %s' % e.detail) from e
    if thing_data is None:
        raise RuntimeError('Cannot find the thing!')
    thing_data.name = the_thing.name
    db.session.add(thing_data)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise RuntimeError('Ack! %s' % e) from e
