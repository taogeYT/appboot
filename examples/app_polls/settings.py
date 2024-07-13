from appboot.conf.default import DataBases, EngineConfig

APP_NAME: str = "app_polls"
DATABASES: DataBases = DataBases(
    default=EngineConfig(url="sqlite+aiosqlite:///./../db.sqlite3")
)
