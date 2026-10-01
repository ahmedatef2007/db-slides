import json,sys
d=json.load(open(f"../decks/lesson{sys.argv[1]}/project/deck.json"))
f={f'project/slides/{s}.html':f'project/slides/{s}.html' for s in d['order']}
f['project/ds/databasecourse/tokens.json']={'artifact':'https://claude.ai/artifact/WdbVXkRa43NmX6n2AKuXTF','path':'project/tokens.json'}
print(json.dumps(f))
