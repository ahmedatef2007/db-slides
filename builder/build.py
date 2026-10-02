import importlib, sys, datetime
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
for n in sys.argv[1:]:
    d = importlib.import_module(f"lesson{n}").build()
    total = d.write(f"../decks/lesson{n}", NOW)
    print(f"lesson{n}: {total} slides")
