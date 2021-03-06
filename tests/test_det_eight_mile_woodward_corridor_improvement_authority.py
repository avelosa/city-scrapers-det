from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, PASSED, TENTATIVE
from city_scrapers_core.items import Meeting
from city_scrapers_core.utils import file_response
from freezegun import freeze_time
from scrapy.settings import Settings

from city_scrapers.spiders.det_eight_mile_woodward_corridor_improvement_authority import (  # noqa
    DetEightMileWoodwardCorridorImprovementAuthoritySpider,
)

# Shared properties between two different page / meeting types
SOURCE = "http://www.degc.org/public-authorities/emwcia/"

LOCATION = {
    "name": "DEGC, Guardian Building",
    "address": "500 Griswold St, Suite 2200, Detroit, MI 48226",
}

test_response = file_response(
    join(
        dirname(__file__),
        "files",
        "det_eight_mile_woodward_corridor_improvement_authority.html",
    ),
    url="http://www.degc.org/public-authorities/emwcia/",
)

spider = DetEightMileWoodwardCorridorImprovementAuthoritySpider()
spider.settings = Settings(values={"CITY_SCRAPERS_ARCHIVE": False})

freezer = freeze_time("2018-01-21")
freezer.start()
parsed_items = [
    item for item in spider._next_meetings(test_response) if isinstance(item, Meeting)
]
freezer.stop()


# current meeting (e.g. http://www.degc.org/public-authorities/emwcia/)
def test_title():
    assert parsed_items[0]["title"] == "Board of Directors"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2018, 8, 14, 14)


def test_end():
    assert parsed_items[0]["end"] is None


def test_id():
    assert (
        parsed_items[0]["id"]
        == "det_eight_mile_woodward_corridor_improvement_authority/201808141400/x/board_of_directors"  # noqa
    )


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == LOCATION


def test_source():
    assert parsed_items[0]["source"] == SOURCE


def test_links():
    assert parsed_items[0]["links"] == []


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False


@pytest.mark.parametrize("item", parsed_items)
def test_classification(item):
    assert item["classification"] == BOARD


# previous meetings e.g.
# http://www.degc.org/public-authorities/emwcia/emwcia-fy-2016-2017-meetings/
test_prev_response = file_response(
    join(
        dirname(__file__),
        "files",
        "det_eight_mile_woodward_corridor_improvement_authority_prev.html",
    ),
    url="http://www.degc.org/public-authorities/emwcia/",
)
freezer.start()
parsed_prev_items = [
    item
    for item in spider._parse_prev_meetings(test_prev_response)
    if isinstance(item, Meeting)
]
parsed_prev_items = sorted(parsed_prev_items, key=lambda x: x["start"], reverse=True)
freezer.stop()


def test_requests():
    freezer.start()
    requests = list(spider._prev_meetings(test_response))
    freezer.stop()
    urls = {r.url for r in requests}
    assert len(requests) == 2
    assert urls == {
        "http://www.degc.org/public-authorities/emwcia/fy-2017-2018-meetings/",
        "http://www.degc.org/public-authorities/emwcia/emwcia-fy-2016-2017-meetings/",
    }


def test_prev_meeting_count():
    assert len(parsed_prev_items) == 2


def test_prev_title():
    assert parsed_prev_items[0]["title"] == "Board of Directors"


def test_prev_description():
    assert parsed_prev_items[0]["description"] == ""


def test_prev_start():
    assert parsed_prev_items[0]["start"] == datetime(2017, 6, 13, 14)


def test_prev_end():
    assert parsed_prev_items[0]["end"] is None


def test_prev_id():
    assert (
        parsed_prev_items[0]["id"]
        == "det_eight_mile_woodward_corridor_improvement_authority/201706131400/x/board_of_directors"  # noqa
    )


def test_prev_status():
    assert parsed_prev_items[0]["status"] == PASSED


def test_prev_location():
    assert parsed_prev_items[0]["location"] == LOCATION


def test_prev_source():
    assert parsed_prev_items[0]["source"] == SOURCE


def test_prev_links():
    assert parsed_prev_items[0]["links"] == [
        {
            "href": "http://www.degc.org/wp-content/uploads/2017-06-13-EMWCIA-Board-Meeting-Agenda.pdf",  # noqa
            "title": "EMWCIA Agenda",
        },
        {
            "href": "http://www.degc.org/wp-content/uploads/2017-06-13-EMWCIA-Board-Meeting-Minutes.pdf",  # noqa
            "title": "EMWCIA Minutes",
        },
    ]


@pytest.mark.parametrize("item", parsed_prev_items)
def test_prev_all_day(item):
    assert item["all_day"] is False


@pytest.mark.parametrize("item", parsed_prev_items)
def test_prev_classification(item):
    assert item["classification"] == BOARD
