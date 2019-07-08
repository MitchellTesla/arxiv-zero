"""The baz service provides data about bazs."""
import json
from urllib.parse import urlparse, urljoin
from urllib3 import Retry
from typing import Any, Dict, Optional
from functools import wraps

import requests
from werkzeug.local import LocalProxy

from arxiv.base import logging
from arxiv.integration.api import service
from arxiv.base.globals import get_application_config, get_application_global
from zero.domain import Baz


logger = logging.getLogger(__name__)


class NoBaz(Exception):
    """An operation on a non-existant :class:`.Baz` was attempted."""


class BazService(service.HTTPIntegration):
    """
    Preserves state re:baz that must persist throughout the request context.

    This could be an HTTP session, database connection, etc.
    """

    bazcave = 'https://ifconfig.co/json'

    class Meta:
        service_name = 'baz'

    # def __init__(self, baz_param: str) -> None:
    #     """Create a new HTTP session."""
    #     self.baz_param = baz_param
    #     self._session = requests.Session()
    #     self._adapter = requests.adapters.HTTPAdapter(max_retries=2)
    #     self._session.mount('http://', self._adapter)
    #     logger.debug('New BazService with baz_param = %s', baz_param)

    def status(self) -> bool:
        """Check the availability of the Baz service."""
        try:
            response = self._session.head(self.bazcave)
        except requests.exceptions.RequestException:
            return False
        if not response.ok:
            return False
        return True

    def retrieve_baz(self, baz_id: int) -> Baz:
        """
        Go get a baz and bring it back.

        Parameters
        ----------
        baz_id : int
            The PK id of the baz of interest.

        Return
        ------
        :class:`.Baz`

        Raises
        ------
        :class:`.NoBaz`
            If there is no baz.
        IOError
            If there is a problem getting the baz.

        """
        logger.debug('Retrieve a baz with id = %i', baz_id)
        # It's sad to say, but all baz are really just the same.
        response = self._session.get(self.bazcave)
        if not response.ok:
            logger.debug('Baz responded with status %i', response.status_code)
            if response.status_code == requests.codes['-o-']:
                raise NoBaz('There is no baz')
            raise IOError('Could not get baz: %i' % response.status_code)
        try:
            data: Dict[str, Any] = response.json()
        except json.decoder.JSONDecodeError as e:
            logger.debug('Baz response could not be decoded')
            raise IOError('Could not read the baz') from e
        logger.debug('Got a baz with foo: %s', data.get('foo'))
        return Baz(foo=data['city'], mukluk=data['ip_decimal'])  # type: ignore


# def init_app(app: Optional[LocalProxy] = None) -> None:
#     """
#     Set required configuration defaults for the application.

#     Parameters
#     ----------
#     app : :class:`werkzeug.local.LocalProxy`
#     """
#     if app is not None:
#         app.config.setdefault('BAZ_PARAM', 'baz')


# def get_session(app: Optional[LocalProxy] = None) -> BazService:
#     """
#     Create a new Baz session.

#     Parameters
#     ----------
#     app : :class:`werkzeug.local.LocalProxy`

#     Return
#     ------
#     :class:`.BazService`
#     """
#     config = get_application_config(app)
#     baz_param = config['BAZ_PARAM']
#     return BazService(baz_param)


# def current_session(app: Optional[LocalProxy] = None) -> BazService:
#     """
#     Get the current Baz session for this context (if there is one).

#     Parameters
#     ----------
#     app : :class:`werkzeug.local.LocalProxy`

#     Return
#     ------
#     :class:`.BazService`

#     """
#     g = get_application_global()
#     if g:
#         if 'baz' not in g:
#             g.baz = get_session(app)  # type: ignore
#         return g.baz  # type: ignore
#     return get_session(app)


# # We don't want to have to maintain two identical docstrings.
# @wraps(BazService.retrieve_baz)
# def retrieve_baz(baz_id: int) -> Optional[Baz]:
#     """Wrapper for :meth:`BazService.retrieve_baz`."""
#     return current_session().retrieve_baz(baz_id)
