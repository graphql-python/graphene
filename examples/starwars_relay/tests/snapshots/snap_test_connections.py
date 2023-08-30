# snapshottest: v1 - https://goo.gl/zC4yUc

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_correct_fetch_first_ship_rebels 1"] = {
    "data": {
        "rebels": {
            "name": "Alliance to Restore the Republic",
            "ships": {
                "pageInfo": {
                    "startCursor": "YXJyYXljb25uZWN0aW9uOjA=",
                    "endCursor": "YXJyYXljb25uZWN0aW9uOjA=",
                    "hasNextPage": True,
                    "hasPreviousPage": False,
                },
                "edges": [
                    {"cursor": "YXJyYXljb25uZWN0aW9uOjA=", "node": {"name": "X-Wing"}}
                ],
            },
        }
    }
}
