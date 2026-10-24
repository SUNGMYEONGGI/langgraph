"""Content-Location metadata comes from the URI path only."""

import httpx
import pytest

from langgraph_sdk._shared.utilities import _get_run_metadata_from_response


@pytest.mark.parametrize(
    "prefix", ["", "https://example.com", "https://example.com/api"]
)
@pytest.mark.parametrize("suffix", ["", "?view=full", "#details", "?view=full#details"])
@pytest.mark.parametrize("thread_id", [None, "thread-1"])
def test_run_metadata_ignores_query_and_fragment(
    prefix: str, suffix: str, thread_id: str | None
) -> None:
    path = f"/threads/{thread_id}/runs/run-1" if thread_id else "/runs/run-1"
    response = httpx.Response(200, headers={"Content-Location": prefix + path + suffix})
    assert _get_run_metadata_from_response(response) == {
        "run_id": "run-1",
        "thread_id": thread_id,
    }


@pytest.mark.parametrize(
    "location",
    [
        None,
        "/other",
        "/other?next=/runs/fake",
        "/other#/runs/fake",
        "https://[invalid/runs/fake",
    ],
)
def test_non_run_location_has_no_metadata(location: str | None) -> None:
    headers = {"Content-Location": location} if location is not None else {}
    assert _get_run_metadata_from_response(httpx.Response(200, headers=headers)) is None
