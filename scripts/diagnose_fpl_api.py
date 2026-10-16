#!/usr/bin/env python3
"""Read-only public FPL endpoint diagnostic. Never prints response bodies or credentials."""
import json, time, urllib.request, urllib.error, datetime
BASE="https://fantasy.premierleague.com/api/"
PATHS=[
"bootstrap-static/","leagues-classic/98695/standings/",
"entry/506228/","entry/506228/history/","entry/506228/transfers/",
"entry/506228/event/6/picks/","event/6/live/","fixtures/?event=6",
"event-status/",
]
results=[]
for path in PATHS:
    url=BASE+path
    status=None; error=None; size=None; valid=False
    for attempt in range(1,4):
        start=time.monotonic()
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; FPLMoneyballDiagnostics/1.0)","Accept":"application/json"})
            with urllib.request.urlopen(req,timeout=20) as res:
                status=res.status; data=res.read(4_000_000); size=len(data)
                valid=isinstance(json.loads(data), (dict,list))
            error=None
            break
        except urllib.error.HTTPError as exc:
            status=exc.code;error=f"HTTP {exc.code}"
            if status not in (429,500,502,503,504):break
        except Exception as exc:
            error=type(exc).__name__
        time.sleep(attempt*2)
    results.append({"path":path,"status":status,"json_valid":valid,"bytes":size,"error":error})
    print(f"{path}: status={status} valid_json={valid} bytes={size} error={error}")
with open("fpl-api-diagnostic.json","w") as f:
    json.dump({"checked_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"results":results},f,indent=2)
if any(not r["json_valid"] for r in results):raise SystemExit(1)
