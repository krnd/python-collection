import appdata


appdata.init(
    __file__,
    "___folder___",
    container="___container___",
    package="___package___",
    application="___application___",
    server="/___server___",
)


for location in (
    "package",
    "application",
    "user",
    "local",
    "temp",
    "server",
):
    try:
        path = appdata.get(location)
        print(location, "=", path)
    except Exception as exc:
        print(location, "!!")
        print(f"  {type(exc).__name__}: {exc}")
