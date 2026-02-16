# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import types

from superset.constants import TimeGrain
from superset.db_engine_specs.base import BaseEngineSpec, DatabaseCategory


class OracleEngineSpec(BaseEngineSpec):
    engine = "oracle"
    engine_name = "Oracle"

    metadata = {
        "description": "Oracle Database is a multi-model database management system.",
        "logo": "oraclelogo.png",
        "homepage_url": "https://www.oracle.com/database/",
        "categories": [
            DatabaseCategory.TRADITIONAL_RDBMS,
            DatabaseCategory.PROPRIETARY,
        ],
        "pypi_packages": ["oracledb"],
        "connection_string": "oracle://{username}:{password}@{hostname}:{port}",
        "default_port": 1521,
        "notes": "Previously used cx_Oracle, now uses oracledb.",
        "docs_url": "https://cx-oracle.readthedocs.io/en/latest/user_guide/installation.html",
    }
    force_column_alias_quotes = True
    max_column_name_length = 128
    supports_multivalues_insert = True

    _time_grain_expressions = {
        None: "{col}",
        TimeGrain.SECOND: "CAST({col} as TIMESTAMP)",
        TimeGrain.MINUTE: "CAST(TRUNC(CAST({col} as DATE), 'MI') AS TIMESTAMP)",
        TimeGrain.HOUR: "CAST(TRUNC(CAST({col} as DATE), 'HH') AS TIMESTAMP)",
        TimeGrain.DAY: "CAST(TRUNC(CAST({col} as DATE), 'DDD') AS TIMESTAMP)",
        TimeGrain.WEEK: "CAST(TRUNC(CAST({col} as DATE), 'WW') AS TIMESTAMP)",
        TimeGrain.MONTH: "CAST(TRUNC(CAST({col} as DATE), 'MONTH') AS TIMESTAMP)",
        TimeGrain.QUARTER: "CAST(TRUNC(CAST({col} as DATE), 'Q') AS TIMESTAMP)",
        TimeGrain.YEAR: "CAST(TRUNC(CAST({col} as DATE), 'YEAR') AS TIMESTAMP)",
    }

    @classmethod
    def convert_dttm(
        cls, target_type: str, dttm: datetime, db_extra: Optional[dict[str, Any]] = None
    ) -> Optional[str]:
        sqla_type = cls.get_sqla_column_type(target_type)

        if isinstance(sqla_type, types.Date):
            return f"TO_DATE('{dttm.date().isoformat()}', 'YYYY-MM-DD')"
        if isinstance(sqla_type, types.TIMESTAMP):
            return f"""TO_TIMESTAMP('{
                dttm.isoformat(timespec="microseconds")
            }', 'YYYY-MM-DD"T"HH24:MI:SS.ff6')"""
        if isinstance(sqla_type, types.DateTime):
            datetime_formatted = dttm.isoformat(timespec="seconds")
            return f"""TO_DATE('{datetime_formatted}', 'YYYY-MM-DD"T"HH24:MI:SS')"""
        return None

    @classmethod
    def epoch_to_dttm(cls) -> str:
        return "TO_DATE('1970-01-01','YYYY-MM-DD')+(1/24/60/60)*{col}"

    @classmethod
    def epoch_ms_to_dttm(cls) -> str:
        return "TO_DATE('1970-01-01','YYYY-MM-DD')+(1/24/60/60/1000)*{col}"

    @classmethod
    def fetch_data(
        cls, cursor: Any, limit: Optional[int] = None
    ) -> list[tuple[Any, ...]]:
        """
        :param cursor: Cursor instance
        :param limit: Maximum number of rows to be returned by the cursor
        :return: Result of query
        """
        if not cursor.description:
            return []
        return super().fetch_data(cursor, limit)
