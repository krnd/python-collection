import dataclasses
import functools
from dataclasses import dataclass
from types import EllipsisType
from typing import (
    Any,
    ClassVar,
    Final,
    Self,
    Type,
    TypeGuard,
    TypeVar,
    overload,
)

import requests
from bs4 import BeautifulSoup, ResultSet, Tag
from bs4.element import PageElement


# ################################ PACKAGE #####################################


__sname__ = "github"
__version__ = "1.0"
__description__ = ...

__requires__ = (
    "requests",
    "beautifulsoup4",
    "lxml",
)


__all__ = (
    # fmt: off
    "Repository",
    # fmt: on
)


# ################################ TYPING ######################################


TELEMENT = TypeVar("TELEMENT", bound=PageElement)


# ################################ TYPES #######################################


@dataclass(eq=False, kw_only=True, slots=True)
class Repository:
    _cache: ClassVar[Final] = dict[str, Self]()

    owner: str = dataclasses.field(init=True, repr=True, kw_only=False)
    name: str = dataclasses.field(init=True, repr=True, kw_only=False)

    desc: str = dataclasses.field(init=False, repr=False)

    license: str | EllipsisType | None = dataclasses.field(
        init=False, repr=False
    )

    stars: int = dataclasses.field(init=False, repr=False)
    watchers: int = dataclasses.field(init=False, repr=False)
    forks: int = dataclasses.field(init=False, repr=False)


# ################################ FUNCTIONS ###################################


def repository(
    owner: str,
    name: str,
    *,
    refresh: bool = False,
) -> Repository:
    key = f"{owner}/{name}"

    if refresh:
        pass
    elif key in Repository._cache:
        return Repository._cache[key]

    repo = _scrap.repository(owner, name)

    Repository._cache[key] = repo
    return repo


def clear_caches() -> None:
    _scrap.invoke.cache_clear()
    Repository._cache.clear()


# ################################ INTERNALS ###################################


class _scrap:

    @staticmethod
    @functools.lru_cache(maxsize=1)
    def invoke(owner: str, name: str) -> BeautifulSoup:
        _request = requests.request(
            "GET",
            f"https://github.com/{owner}/{name}",
        )
        if _request.status_code == 404:
            raise LookupError(...)

        return BeautifulSoup(_request.content, "lxml")

    css_repository_about: Final = (
        "#repo-content-pjax-container > div > div > div"
        " > div.Layout-sidebar > div > div:nth-child(1) > div"
        " > div"
    )

    @classmethod
    def repository(
        cls,
        owner: str,
        name: str,
        *,
        soup: BeautifulSoup | None = None,
    ) -> Repository:
        repo = Repository(owner, name)

        soup = soup or cls.invoke(owner, name)

        _about = soup.select_one(cls.css_repository_about)
        if _about is None:
            raise ValueError(...)

        repo.desc = cls.about_description(_about) or ""

        _abouties = _about.find_all("h3", recursive=False)
        assert is_result_set(_abouties, Tag), (
            "ResultSet[Tag](<h3>)"
            # <format-break>
        )

        for _header in _abouties:
            header = _header.get_text(strip=True)

            if header == "Stars":
                repo.stars = cls.about_numeric_value(_header)
            elif header == "Watchers":
                repo.watchers = cls.about_numeric_value(_header)
            elif header == "Forks":
                repo.forks = cls.about_numeric_value(_header)
            elif header == "License":
                repo.license = cls.about_license(_header)

        return repo

    @staticmethod
    def about_description(_about: Tag, /) -> str | None:
        _heading = _about.find(None, recursive=False)
        assert (
            _heading is not None
            and isinstance(_heading, Tag)
            and _heading.name == "h2"
            and _heading.get_text(strip=True) == "About"
        ), "Tag(<h2>About)"

        _desc = _heading.find_next_sibling(None)
        assert (
            _desc is not None
            and isinstance(_desc, Tag)
            and (_desc.name == "div" or _desc.name == "p")
        ), "Tag(<div> or <p>)"

        if _desc.name == "div":
            return None
        return _desc.get_text(strip=True)

    @staticmethod
    def about_license(_header: Tag, /) -> str | EllipsisType | None:
        _license = _header.find_next_sibling("div")
        assert (
            _license is not None
            and isinstance(_license, Tag)
            # <format-break>
        ), "Tag(<div>)"

        _license = _license.find("a", recursive=False)
        assert (
            _license is not None
            and isinstance(_license, Tag)
            # <format-break>
        ), "Tag(<strong>)"

        license = _license.get_text(strip=True)
        license = license.removesuffix("license")
        license = str.strip(license)

        if license == "Unlicense":
            return None
        if license == "View":
            return Ellipsis
        return license

    @staticmethod
    def about_numeric_value(_header: Tag, /) -> int:
        _element = _header.find_next_sibling("div")
        assert (
            _element is not None
            and isinstance(_element, Tag)
            # <format-break>
        ), "Tag(<div>)"

        _element = _element.find("strong", recursive=True)
        assert (
            _element is not None
            and isinstance(_element, Tag)
            # <format-break>
        ), "Tag(<strong>)"

        text = _element.get_text(strip=True)
        if text.endswith("k"):
            scaler, text = 1e3, text.removesuffix("k")
        else:
            scaler = 1e0

        return int(float(text) * scaler)


# ################################ HELPERS #####################################


@overload
def is_result_set(
    obj: Any,
    /,
) -> TypeGuard[ResultSet[Any]]: ...


@overload
def is_result_set(
    obj: Any,
    inner: Type[TELEMENT],
    /,
) -> TypeGuard[ResultSet[TELEMENT]]: ...


def is_result_set(
    obj: Any,
    inner: Type[TELEMENT] | None = None,
    /,
) -> TypeGuard[ResultSet[TELEMENT]]:
    return (
        obj is not None
        and isinstance(obj, ResultSet)
        and (
            inner is None  # <format-break>
            or all(isinstance(node, inner) for node in obj)
        )
    )
