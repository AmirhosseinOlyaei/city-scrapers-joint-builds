from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.daltx_bot import DaltxBotSpider


events_response = file_response(
    join(dirname(__file__), "files", "daltx_bot_events.html"),
    url="https://www.dallascollege.edu/events/?categories%5B%5D=Category%3EBoard%20of%20Trustees&search=all",
)

event_details_response = file_response(
    join(dirname(__file__), "files", "daltx_bot_event_details.html"),
    url="https://www.dallascollege.edu/events/trustees/2026/jun-2-board-meeting---regular/",
)


@pytest.fixture
def spider():
    return DaltxBotSpider()


@pytest.fixture
def parsed_events(spider):
    with freeze_time("2026-05-14"):
        return [request for request in spider.parse(events_response)]


@pytest.fixture
def parsed_items(spider):
    item = events_response.css(".row.calendar-search-results")[0]
    event_details_response.meta["item"] = item
    with freeze_time("2026-05-14"):
        return [item for item in spider._construct_meeting(event_details_response)]


def test_count(parsed_events):
    assert len(parsed_events) == 2


def test_title(parsed_items):
    assert parsed_items[0]["title"] == "June Board Meeting - Regular"


def test_description(parsed_items):
    assert parsed_items[0]["description"] == "The Board of Trustees will hold a regular meeting on June 2, 2026."


def test_start(parsed_items):
    assert parsed_items[0]["start"] == datetime(2026, 6, 2, 16, 0)


def test_end(parsed_items):
    assert parsed_items[0]["end"] == datetime(2026, 6, 2, 17, 0)


def test_time_notes(parsed_items):
    assert parsed_items[0]["time_notes"] == ""


def test_id(parsed_items):
    assert parsed_items[0]["id"] == "daltx_bot/202606021600/x/june_board_meeting_regular"


def test_status(parsed_items):
    assert parsed_items[0]["status"] == TENTATIVE


def test_location(parsed_items):
    assert parsed_items[0]["location"] == {
        "name": "Administrative Office",
        "address": "1601 Botham Jean Blvd., Dallas TX 75215"
    }


def test_source(parsed_items):
    assert parsed_items[0]["source"] == "https://www.dallascollege.edu/events/trustees/2026/jun-2-board-meeting---regular/"


def test_links(parsed_items):
    assert parsed_items[0]["links"] == []


def test_classification(parsed_items):
    assert parsed_items[0]["classification"] == BOARD


def test_all_day(parsed_items):
    assert parsed_items[0]["all_day"] is False
