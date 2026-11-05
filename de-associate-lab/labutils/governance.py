"""Simulate Unity Catalog identity functions locally, to practise column masks and row filters.

    from labutils.governance import login
    login("ana@corp.com", groups=["finance_team"])   # pretend to be this user
Then SQL can use current_user() and is_account_group_member('finance_team').
"""
from pyspark.sql.types import BooleanType, StringType

_STATE = {"user": "you@corp.com", "groups": set()}


def login(user, groups=()):
    from labutils import get_spark
    _STATE["user"], _STATE["groups"] = user, set(groups)
    spark = get_spark()
    spark.udf.register("is_account_group_member", lambda g: g in _STATE["groups"], BooleanType())
    spark.udf.register("lab_current_user", lambda: _STATE["user"], StringType())
    print(f"Logged in as {user}  groups={sorted(_STATE['groups']) or '[]'}")
