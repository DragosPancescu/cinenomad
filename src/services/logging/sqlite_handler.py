import logging
import traceback
from datetime import datetime, timezone

from services.database.models import LogEntry
from services.database import queries


class SQLiteHandler(logging.Handler):
    """Custom logging handler that writes log records to the SQLite database."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            tb = None
            if record.exc_info and record.exc_info[2] is not None:
                tb = "".join(traceback.format_exception(*record.exc_info))

            log_entry = LogEntry(
                timestamp=datetime.fromtimestamp(
                    record.created, tz=timezone.utc
                ).isoformat(),
                level=record.levelname,
                logger_name=record.name,
                message=record.getMessage(),
                module=record.module,
                func_name=record.funcName,
                line_no=record.lineno,
                traceback=tb,
            )

            queries.insert_log(log_entry)
        except Exception:
            self.handleError(record)
