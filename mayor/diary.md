# Fableton — mayor's diary

Notes for future me (read first):
- Map: owned 9 tiles, x/z from -935 to +935. Highway enters from the west; stub ends at (-622, 6). River flows from the south-east (upstream) round the east and north side to the north-west (downstream). North = +z, east = +x.
- Technical: the MCP tools `cs2_zone_area`, `cs2_build_road`, `cs2_find_prefabs` (queries with spaces) break on names with spaces. Workaround: `bridge.py` / `mayor.py` in this folder call the same bridge with correct encoding (`PYTHONPATH=. python3 turns/<script>.py`). `cs2_connect_road` works fine. Save names: no spaces.
- Grid: arterial (Medium Road) along z=0; small streets every 116 m (z=-232,-116,116) and avenues every 220 m (x=-400,-180,40,260). Industry on a spur west: x -860..-620, z -232..-116.
- Wind turbines need ~120 m between each other.
- Milestone popup: it holds the game paused and no cs2 tool can close it. With the human's OK (2026-11-11) there is a helper: `rog/close_popup.sh` (scheduled task `cs2-mayor-click` on ROG clicks CLOSE in the game window). After it, start the run again. Delete the task at the very end of the project.
- 2026-11-11 18:08 the human updated MAYOR.md: runs at speed 8; a helper `popup_closer.py` must be running (max speed + video camera; it may move the camera between my screenshots); the watcher no longer treats traffic accidents as incidents. Popups are still mine to close with `rog/close_popup.sh` (signature-building OK button: `rog/close_popup.sh 0.5 0.688`). The Monitor tool expires every 30 min — re-arm the watcher.
- 2026-11-11 18:52 I patched `watcher.py` (function `in_city`): fires outside the owned tiles (+150 m) no longer pause the game — a wildfire 3 km away was pausing every few game-minutes. Backup of the old file is not kept in the folder; the change is ~12 lines.
- 2026-11-11 19:15 second watcher patch: burning trees/bushes (VEGETATION regex) no longer pause the game — only buildings on fire do.
- Shoreline water pump sits at water level; a road on a steep bank above it does not connect. Use groundwater pumps (aquifer under x -30..250, z -200..-30 and south-west x -640..-300, z -930..-700).
- 2026-11-12: **one in-game day = one budget "month"** (income ~+1.4M per day). Development points: `cs2_devtree` / `cs2_devtree_buy` work. Tiles: `cs2_buy_map_tiles` works (33 permits left).
- Popups pause the game and end the run early with a plain TURN_DONE: milestone → `rog/close_popup.sh`; "new signature building" → `rog/close_popup.sh 0.5 0.71` (0.688 missed the OK button on 2026-11-12 s5), then `ssh rog "echo 0.5656 0.7475> C:\cs2-mayor\click.txt"` to restore the default. If a run stops early with no INCIDENT, take one screenshot.
- Big lots (incinerator 200×216, gas plant 216×304, hospital on a slope) are refused on sloping ground even at ~4%; `turns/flat.py` ranks flat owned blocks. `/build/place/roadside` really builds — never "test" with an expensive prefab.
- The river runs between the town (z<130) and the flat north bank (z>380) at x 200..800: water up to 28 m deep. `/build/road` e1/e2 are metres above the terrain (river bed), not above water. For bridges try `cs2_connect_road` with one snapped end and one free end with e1/e2.
- Landfills show "Facility Full" almost at once (no landfill area can be drawn through the bridge) — an incinerator is the real fix.
- The Monitor watcher expires after 30 min; re-arming it does not reset the session clock.
- 2026-11-12 s4: `/build/road/connect` has NO dry run — a `dryRun` parameter is ignored and the road is built. `/build/zone` repaints OCCUPIED cells too (the houses under it get replaced) — keep circles small and on empty lots. Shoreline dry run works (`/build/place/shoreline dryRun=true`). If OBS is not running: `ssh rog "schtasks /run /tn CS2MayorOBS"`, wait 12 s, then `obs.py start`.
- The office block at x -1260..-1000, z -720..-490 (SW of the centre, next to turbines and the landfill) never grew a single office at demand 100; cause unknown.
- 2026-11-12 s5: **bridges work**: `bridge.call("/build/road", dict(prefab=..., x1,z1,x2,z2, bridge="true"))` between two EXISTING nodes on dry land spans the river in one go (x=340 bridge, 440 m). Make the far node first with a stub going away from the water. A road at ground level passes under a highway bridge without touching it (loop at z=-1314).
- Zones on NEW roads stay dead for ~4 in-game days, then fill within a day (north bank: roads 01-06, full on 01-10). Zones on old roads fill in hours. Build roads 4 days ahead of need. Office High is unlocked (zone name "Office High").
- s5: `turns/rg.py x z radius` = compact road graph; `turns/t20p.py` = scan for fully unzoned pockets (safe r=22 painting). `cs2_devtree` output is huge - call the bridge and filter instead. `resume.py <targetFrame>` needs the target frame from the run call.
- s5: 2-car deadlocks at signalled Medium Road junctions: lights off usually clears them; (-180,-696) needed an all-way stop. Watcher now ignores burning vehicles (regex widened).
- s5: highway is N-S at x~-1350 (northbound = east carriageway). Full interchange at z~0..60. My exits: z=-1128 (right turns only + loop under the bridge for southbound) and z=-490 (northbound side only).
- s7: **new roads are NOT dead for 4 days** - East Bank and South Works built hundreds of cells within a day. The old "dead" blocks had another cause (the East Bank at first had no road link at all). A bridge made with `/build/road bridge=true` can start at a NEW node floating above the existing street end (same x/z, other height) -> no cars, power, water. Fix that worked: demolish the low stub, then `road()` (connect) from the street junction to the bridge end.
- s7: upzoning works: painting Residential Medium/High over low housing on old roads rebuilds it within hours (+13k people in two days). Roadside placement never bulldozes buildings - a refusal means the spot is taken. `put()`/`near()`/`try_around()` helpers live in turns/t22e.py, t22f.py, t24a.py. Bus lines: `cs2_create_transit_line` with {x,z} stops. The calendar: day 12 of a year is followed by 01-01 of the next year.
- s8: `turns/civic.py` has `put(prefab,x,z,horiz,want)` (exact t, sides verified: no FLIP needed). `/city/devtree/buy` works through bridge.py now. Bridge `/build/road bridge=true` from an existing dead-end node (150,-1504) to an existing corner node joined correctly. Tiles are cheap (~40k each), 82 permits left. Flat plateau = Campus (x 210..742, z -2280..-1800); parkway x=742 links it to the East Bank.
- s7: when a run crawls at speed 1 although popup_closer runs, `/sim/control speed=8` does not stick; I cancelled the last 4 h instead.
- build-out: the LHC went down on a 2% slope (9 m over 512 m) and the Space Center on ~4%; the airport did not. `cs2_buy_map_tiles` (MCP tool) works, `/city/tiles/buy` through bridge.py does not take a JSON list. Storms leave 'Weather Destroyed' ruins (service buildings too) without an INCIDENT - check notifications, bulldoze, re-place. During a fire popup_closer holds speed 1 on purpose.

**Current plan** (rewritten 2028-01-08 03:21 game time, end of the build-out session - FINISHED)
1. Mission and build-out are both complete: pop 90,761, happiness 80, unemployment 9.5, balance +5.19M/mo, no loans. Save `Fableton_BUILDOUT` (goal save: `Fableton_FINAL_78730`).
2. West of the highway now: Large Hadron Collider (-1918,16), Space Center (-2510,-74), housing north along x=-2240/-2560, industry south at x=-1818 (z -300..-900).
3. Not built: Airport01 (1136x376, refused everywhere on the ~3.5% slope; AirportNode is bought). 0 development points left.
4. Clean-up still open: delete the ROG task `cs2-mayor-click`, stop `popup_closer.py`.

## Turn 1 · 2026-01-06 · pop 0 · balance 0/mo · happiness 50%
Saw: empty map, 1,000,000 in the treasury, a highway stub and a river bending around a flat meadow.
Did: built the first grid (arterial + 4 avenues + 3 streets) and an industrial spur by the highway; water pump upstream (south-east), sewage outlet downstream (north-west), two wind turbines by the highway stub; zoned ~3,900 cells low residential, ~320 commercial, ~720 industrial. Spent ~125k.
Why: houses in the east near the river and away from factories; factories next to the highway so trucks never cross the town; clean water taken above the town, sewage released below it.
Caption: day one. an empty meadow, a river, one million.

## Turn 2 · 2026-01-06 14:59 · pop 116 · balance -45,208/mo · happiness 53%
Saw: milestone 1 "Tiny Village" (+25k, +3 tile permits) paused the game ~5 h in; first houses, shops and factories are up; 383 free jobs; garbage, healthcare and deathcare just unlocked. The river pump never got road access (lot sits 7 m below the bank road), so mid-turn I swapped it for a groundwater pump at (107,-148) on the aquifer under the town.
Did: landfill south of the industrial street (-794,-300); small clinic on the arterial (-344,32). Cemetery postponed until there are more people.
Why: garbage starts piling from day one, the landfill belongs with the factories; clinic in the middle so ambulances reach every street. Upkeep is now ~73k/mo against tiny taxes, so nothing else until the town fills in.
Caption: first hundred residents. first milestone. first landfill.
Note: milestone popups pause the game and stay on screen; a timed run ends early when that happens (check frameIndex vs target).

## Turn 3 · 2026-01-07 03:39 · pop 460 · balance -8,155/mo · happiness 71%
Saw: every residential lot taken, 282 free jobs and 11 businesses short of workers; demand for houses at max, none for shops or factories. Row housing just unlocked. Groundwater pump capacity sagged from 75k to 40k (use 4.7k) — watch it.
Did: two new rows of streets south (z=-348, z=-464) with the avenues extended and the old pump cul-de-sac closed into a loop; low residential on z=-348, row houses on z=-464 and on the west side of the x=-400 avenue.
Why: the town is short of people, not of jobs; row houses pack more households per metre for the long road to 75k.
Caption: jobs outnumber people. build homes, nothing else.

## Turn 4 · 2026-01-07 05:32 · pop 610 · balance +4,295/mo · happiness 67%
Saw: milestone 2 "Small Village" (+50k, +4 tile permits; schools and medium density unlocked). Unemployment jumped to 18%: the free jobs are for the uneducated, educated residents have none. Air pollution from the factories drifts north-north-east, away from the houses.
Did: second industrial block north of the highway stub (x -860..-622, z 122..238), downwind; elementary school (-466,-432) and cemetery (-460,-496) on a new stub of the z=-464 street. Tried to sell surplus power: transformer + line to the outside grid would not connect through the bridge, so I demolished the transformer again (lost ~10k).
Why: more factories = more jobs of every level; the school both hires educated people and makes the next generation employable. Balance is finally positive.
Caption: second milestone. first school. the budget turns green.
Lesson: zone_line repaints occupied lots too — only paint empty land.

## Turn 5 · 2026-01-07 13:32 · pop 1,526 · balance +26,277/mo · happiness 65%
Saw: milestone 3 "Large Village" (+75k, +5 permits; fire and police unlocked). Population more than doubled in 8 hours and jobs did not keep up: unemployment 27.6%, the only free jobs are for the uneducated; no demand for shops, offices still locked. Power use is at 60% of what two turbines give.
Did: new street z=-580 with medium-density housing; fire house (-344,-552) and police station (-234,-552) on it; wind-farm road north of the factories with turbines 3 and 4. Spent ~275k, treasury 481k.
Why: fires are the incident I can least afford; police and fire also hire educated people. Medium density is the fastest way to the next milestone, which should bring offices — the real cure for educated unemployment.
Caption: third milestone. firemen, police, and too few jobs.
Note: roads x=-520 and x=-400 south of z=-464 are blocked by the cemetery lot; z=-580 connects via x=-180 and x=40 only.

## Turn 6 · 2026-01-08 03:54 · pop 2,580 · balance +16,865/mo · happiness 62%
Saw: unemployment stuck at 27.5%: 2,151 adults, only 974 jobs, 33 free. Industry and shops finally show demand (54 and 15). Two free signature buildings unlocked.
Did: third industrial block (x -860..-622, z 354..470) plus industrial strips along the medium spur roads — about 980 empty industrial cells; a little commercial on the arterial. New street z=-696 with the two signature buildings (Polaris Suites at (-344,-668), Rock Musician Mansion at (-124,-736)) and low residential on its north side only.
Why: jobs first — the town needs roughly a thousand more; housing is held back to one side of one street until the factories hire.
Caption: 2,500 people, 974 jobs. zoning factories as fast as i can.
Addendum (same turn): placing the signature buildings tipped XP over milestone 4 "Grand Village" (+100k, +6 permits = 18 unused; parks, bus, taxi and **Office Low** unlocked). Zoned ~400 cells of low offices on the south side of z=-696 and west of x=-520 — the educated jobs the town was missing.

## Turn 7 · 2026-01-08 14:26 · pop 3,546 · balance +161,559/mo · happiness 66%
Saw: offices filled at once and pay 51k tax; unemployment down to 18.6% and falling; demand 100 for every housing density. Two small fires (put out, no losses) and two traffic accidents paused the run. The single highway junction at (-622,6) is choking: flow 6–16% on the stub and the arterial west end.
Did: (during the run) two bypass streets between town and industry (z=-232 and z=119); now a second junction on the highway stub at x=-700 with medium roads straight into both industrial blocks; new street z=-812 with medium housing; offices on the z=-232 link, shops on the z=119 link; turbine 5 on a wind road at (-610,-716).
Why: trucks and factory commuters should leave the stub before they reach the town junction; housing demand is at max and money is no longer the limit (+161k/mo).
Caption: offices arrive, unemployment falls, the highway exit jams.

## Turn 8 · 2026-01-08 19:48 · pop 4,249 · balance +258,351/mo · happiness 64%
Saw: money is flowing (+258k/mo) but traffic flow is 65% and the highway off-ramp is at 7% — the queue reaches back onto the highway. Unemployment 20.9%, demand for industry 55, offices 58, low housing 100. A far-away highway pile-up paused the run three times (not ours; just resume with `python3 resume.py <targetFrame>`).
Did: removed the N and S legs from the old junction at (-622,6) — the stub now runs straight into the arterial, industry uses the x=-700 junction, the cut legs stay as dead ends. Bus depot (-628,-652) and 24 bus stops for two lines (North Works, South Works; ids in turns/bus_stops.json) — but **bus lines are still milestone-locked**, retry `turns/t08d.py` later, never with force. Bought 4 tiles for ~132k (NW, W with the interchange, two south; 14 permits left). NW industrial extension (x -1100..-860, z 354..586, ~1,250 cells) and a south street z=-924 with low housing.
Why: two signalled junctions 78 m apart were strangling the only entrance; factories go north-west where the wind carries smoke over the river; buses should take commuters off the arterial as soon as the game allows lines.
Caption: one road in, one road out. rebuilding the front door.

## Turn 9 · 2026-01-08 23:20 · pop 4,749 · balance +194,107/mo · happiness 62%
Saw: milestone 5 "Tiny Town" (+125k, +7 permits = 21 unused; post, radio, bus stations, mixed housing). Bus lines still report "locked" although the depot is unlocked — left alone, flagged for the human. Map tiles cost upkeep (64k/mo for 13 tiles) — buy only what gets built on. Traffic flow 67%; the jam is ~1,000 commuter cars, not trucks; off-ramp still 7%. Health down to 55, unemployment 17.7%, office demand 64, all housing demand 100.
Did: traffic lights off at the x=-700 industrial junction and at arterial/x=-400 (side streets now yield); West Parkway (medium road x=-590, z -232..-464) with offices on both sides, linked to the z=-464 street so the south district can reach the highway without the arterial; south street z=-1040 with medium housing, a second clinic (-435,-1008), a park, a small park and a playground; turbines 6 and 7 on the NW edge (x=-1120).
Why: every car from the south had to climb to the arterial and queue at two lights; the parkway gives a second way west and puts educated jobs between homes and factories.
Caption: five thousand people and one thousand of them stuck in traffic.

## Turn 10 · 2026-01-09 08:49 · pop 6,234 · balance +299,919/mo · happiness 66%
Saw: traffic flow down to 58%; the queue is ~150 cars of outside commuters turning north into the factories through one T-junction at (-700,122), backing up over the off-ramp onto the highway. Unemployment 19.6% (locals are too educated for the 155 free uneducated jobs); shops in demand (29), industry 53. Two house fires on z=-924, 700 m from the only fire house.
Did: fourth leg on the ramp node (-802,17) north to z=122 as a second factory entrance; parkway x=-590 extended north to the arterial (T at (-590,4)) and south by a diagonal to x=-520; lights off at seven junctions on these routes. New street z=-1156 zoned mixed (housing over shops) with fire house 2 (-124,-1128); industrial street z=702; shops along the parkway. Saved as Fableton_T10.
Why: split the highway flow at the first node instead of the second; give the south a west-side route that never touches the avenues; shops and mixed blocks hire exactly the poorly/medium-educated locals who are unemployed.
Caption: the factories hire commuters from outside. the town pays in traffic.
Addendum (turn 10, during the run): the fire on z=-924 kept spreading because the fire engine sat in a 230-car queue on the x=-180 avenue. Root cause = one way in and out. Built two at-grade highway links with plain Medium Road: **north link** (-1100,586) → highway nodes (-1256,609)/(-1276,611), and **south link** from the parkway (-590,-464) west along z≈-470..-490 → highway nodes (-1324,-490)/(-1344,-489). Bought tile (-1247,-623) for 34k (20 permits left). Highway ramp prefabs are still locked; at-grade junctions are what the game allows now.

## Turn 11 · 2026-01-09 20:49 · pop 8,139 · balance +475,401/mo · happiness 65%
Saw: the long turn 10 ended well: the two highway links, lights off on the highway junctions and widening x=-520, x=-180 and the industrial links from Small to Medium **in place** (`/build/road/replace`, 3.9k for 25 segments, buildings survive) cut queues from 230 cars to under 50. Two houses burned down on z=-924 before the roads cleared; ruins bulldozed. A gridlock loop at arterial/x=-400 went away when I put its lights back. Unemployment 16.1% and falling, offices and all housing at demand 100, 184 buildings levelling up. Bus lines still locked.
Did: fire budget 150% (during the fire). New grid: z=-1272 and z=-1388 across the south, a west district (x -860..-520, z -1040..-1388); offices on the north side of z=-1272, medium housing elsewhere, mixed on z=-1156 west, low on z=-1388 west. Elementary school 2 (-605,-1116), cemetery 2 (-775,-1188), three parks, the free Ironpress signature building, turbines 8–10 along the south highway link.
Why: the road skeleton finally has spare capacity, so housing and offices can grow again; services follow the people south-west.
Caption: three ways onto the highway now. the town breathes again.
Rules learned: uncontrolled 4-way of equal roads can deadlock — keep lights where two busy roads cross, remove them only where a side road meets a main road. Widening in place is cheap: do it before a street jams, not after.

## Turn 12 · 2026-01-10 03:43 · pop 10,191 · balance +618,257/mo · happiness 67%
Saw: ten thousand residents. Unemployment 14.8%, queues almost gone at night (318 cars on the road). The landfill is **full** (garbage 367k/mo); children jumped to 779 and teens to 176; demand: low housing 100, high 100 (still locked), industry 54, medium 0 (1,000 cells still empty).
Did: landfill 2 on the south highway link (-844,-546); south row z=-1504 with high school (-265,-1464), clinic 3 (-639,-1476), post office (-571,-1480), the free Rubique signature block, low housing on the rest; industrial street z=818 in the north. Spent ~335k, treasury 115k.
Why: garbage is a hard quality-of-life rule; landfills are the only tool until incineration unlocks, so I will keep adding one whenever "Facility Full" shows. Schools before the teenagers need them.
Caption: ten thousand people. the first landfill is already full.

## Session end · 2026-01-10 13:52 (real time 2026-11-11 19:21)
Stopped mid-turn 12 on the human's order ("стой, выключи"; the helper's camera fly-overs were going wild). Game paused and saved as `Fableton_T12_session1_end`; recording stopped; watcher and `popup_closer.py` stopped.
State: pop 12,941 · happiness 69% · money 456,884 · balance about +600k/mo · unemployment was 14.8% at the start of the turn. Demand: low housing 100, high 100 (locked), industry 54, offices 86.
Open items for next session:
- Finish widening the x=40 avenue to Medium (8 of 13 segments failed as one batch with OverlapExisting — retry one by one).
- A car wreck on the diagonal (-555,-522) had a 127-car queue behind it on x=-520; check it cleared.
- Zone offices (demand 86) and industry (54); landfill 2 is new, watch for "Facility Full".
- Bus lines still "locked" (depot + 24 stops are built; `turns/t08d.py` creates the two lines) — ask the human whether this is a mod lock-check bug.
- Water at ~50% of one groundwater pump; add a second pump before 70%.
- Unspent: 20 tile permits. Milestone 6 (XP 31.6k) should bring high density.

## Session resumed · 2026-01-10 13:52 (real 19:24)
The stop order was meant for the other session; the human said "продолжай". Recording and watcher restarted; `popup_closer.py` left OFF (its camera fly-overs were the problem) — do not restart it unless the human says so. Finished widening x=40 to Medium (all 13 segments), no deadlocks. New office park south of the south highway link (x -1260..-1000, z -596..-712, ~600 cells) for office demand 86. Turn 12 continues to frame 9715094.

## Session end (technical, by the operator) · 2026-01-10 15:06 (real time 2026-11-11 19:25)
Stopped mid-turn 12 because the human ran out of usage limits — not a game decision. Game paused and saved; the newest save is the auto-named `11-ноября-19-25-49` (game time 2026-01-10 15:24), right after `Fableton_T12_session1_end2`. Recording stopped; helper stopped. Pop 13,247 · happiness 69% · money 677,641. Next session: load the newest save, then continue the open items from the previous session-end note.

## Session end · 2026-01-10 15:24 (real time 2026-11-11 19:26)
Stopped on the human's order ("все стоп, продолжим потом"). Game paused, saved as `Fableton_T12_session1_end2`; recording, watcher and `popup_closer.py` are all stopped.
State: pop 13,247 · happiness 69% · health 59 · money ~678k · balance +1.0M/mo · unemployment 14.1% · milestone 7 "Busy Town" reached (27 tile permits unused).
Turn 12 was not finished (target frame 9715135; now 9668071) — start the next session with a fresh turn 13 observation instead of resuming.
Open items:
- **Development tree**: milestones 6 and 7 unlocked nothing new through the bridge. High-density zones, highways, large roads, hospital, college, incineration, recycling are all still locked; many of these need development points spent in the Progression panel, and no cs2 tool does that. Ask the human how to spend them (my ROG clicker could do it, but it was approved only for closing popups).
- Bus lines still "locked" (depot + 24 stops built; `turns/t08d.py` creates the two lines). Probably the same dev-tree question.
- Garbage 485k/mo on two landfills — watch "Facility Full"; incineration is locked.
- Water 51k of ~85k from one groundwater pump: build a second pump first thing (aquifer under x -640..-300, z -930..-700 or the central one).
- Children 1,728 / teens 390: check school capacity (2 elementary, 1 high school).
- Office park by the south link (695 empty cells) is filling; industry demand 54 with only 71 empty cells — zone more in the north (z=818 row was the last).
- A forest fire is burning east/south-east of the river (141 trees, x 889..5774) — not in the built area, watcher ignores trees.
- `popup_closer.py`: the human's other session keeps restarting it and killing the watcher when it does; if the watcher Monitor dies with exit 143/144, just re-arm it.

## Session start · 2026-01-10 15:31 (real time 2026-11-12)
New chat. Recording, watcher and `popup_closer.py` started as MAYOR.md (edited after the last session) asks.

## Turn 13 · 2026-01-10 15:31 · pop 13,370 · balance +997,736/mo · happiness 69%
Saw: money is fine (694k, +1.0M/mo) but traffic flow is 56% and the main highway off-ramp is at 6%: the z=0 arterial is the only Medium east-west road and it is saturated from the ramp to x=-180; x=-520 carries the whole south (flow 17%). Unemployment 14.3% with 52 free jobs; industry demand 54 with 71 empty cells; water at 60% of one pump.
Did: bought the SW tile (51k, 36 permits left). **Third highway link**: Medium road from the west end of z=-1156 (-860) to highway nodes (-1349,-1128)/(-1369,-1128), lights off there. Widened Small→Medium in place: z=116 and z=-232 (x -400..260), z=-464 (x -400..40), x=-400 (z -348..116), z=-1156 (x -520..-180 and -68..40; three segments refused with OverlapExisting). Groundwater pump 2 at (-435,-780) on the SW aquifer. Industry zoned along the new link (469 cells, x -1290..-1010).
Why: the south district now reaches the highway without x=-520 or the arterial; two parallel Medium streets take through traffic off z=0; factories by the new link give southern residents jobs that need no trip through town.
Caption: one arterial was carrying the whole town. now it has help.
Note: right after widening, `/city/zoning` shows ~1,700 low-housing cells as "empty" although the houses still stand (spot checks) — looks like a flag reset on rebuilt zone blocks; re-check after the run before zoning more housing.
Incident: car on fire at (-186,-610), 160 m from fire house 1 → nothing to fix; watcher patched so burning vehicles no longer pause the game; run resumed.
Incident: factory on fire at (-908,670), NW industry, 1.3 km from the nearest fire house → built fire house 3 at (-888,528); run resumed. (Zoning check mid-run: houses on widened streets are intact, pop 14,776, money 996k.)
Incident: house fire at (-320,-268), 285 m from fire house 1 → covered, no change; run resumed.
Incident: gridlock flag (cleared by itself); cause = 109 cars queued at the lights where the new SW link meets the Small street z=-1156 at x=-860 → lights off at (-860,-1156); widened x=-860 (z -1272..-1040), z=-1040 (x -690..-520) and z=-1272 (x -860..-690) to Medium so the link has three ways into town. z=-1156 between -860 and -520 still refuses (OverlapExisting, likely school/cemetery lots). Run resumed.

## Turn 14 · 2026-01-11 15:31 · pop 15,450 · balance +1,126,426/mo · happiness 68%
Saw: +2,080 residents in a day; **unemployment 9.9%** (first time under the 10% target), 389 free jobs; treasury 1.49M. The 469 industrial cells on the SW link filled within the day. Demand: all housing 100, offices 100, shops 56, industry 4. Landfill "Facility Full" again (garbage 556k/mo). Queues are short now (max 17 cars) but the day-average flow is 44%: the highway mainline slows to 7–10% at my at-grade links — ramps are still locked.
Did: bought the south tile (39k, 35 permits left) and built **Southfield**: x=-520 avenue (Medium) and x=-860 / x=-340 streets extended to z=-1968; cross streets z=-1620, -1736 (Medium), -1852, -1968. Elementary school 3, clinic 4, fire house 4, two parks, a playground. Zoned medium housing on z=-1620 (~850 cells), offices (466) and shops (119) on z=-1736, low housing on the two southern streets and the side streets (~1,860). Landfill 3 at (-1272,-1205) by the SW link. Spent 401k, saved as Fableton_T14_start.
Why: demand for every kind of housing is at 100 and money is piling up; the south is flat, dry and next to the new highway link, so new residents do not load the old arterial. Offices and shops inside the district keep some trips local.
Caption: unemployment under ten percent. time to build a whole new district.

## Session end (technical, by the operator) · 2026-01-11 23:31
Session stopped by the human to add a missing tool. Game paused and saved as `Fableton_before_devtree`; recording, watcher and `popup_closer.py` were stopped.
Answer to your open item about development points: the bridge now has `cs2_devtree` (points, nodes, cost, requirements, what each node unlocks) and `cs2_devtree_buy` (same as clicking Unlock in the Progression panel). See MAYOR.md.
Bus lines: the bus line needs "Bus Stop Built Req" (at least one counted bus stop) or a built bus station. Its progress was 0 because the bridge placed every stop as `BusStop02 Placeholder`, a prefab the game does not count as a built stop. Fixed: stop placement now picks a real stop in the city's theme (e.g. `NA_BusStop01`). The 28 existing placeholder stops still exist.
New tool `cs2_unlock_requirements` (see MAYOR.md).

## Session start · 2026-01-11 23:32 (real time 2026-11-12 03:23)
New chat. Recording, watcher and `popup_closer.py` started.

## Turn 15 · 2026-01-11 23:44 · pop 18,091 · balance +1,252,087/mo · happiness 68%
Saw: 198 "no electricity" icons, almost all in Southfield: ten turbines give 47.7 MW against 48.4 MW of demand. Unemployment back to 11.6% (142 free jobs) after 2,600 people moved in; industry demand 55 with 71 empty cells; landfill "Facility Full"; 28 development points unspent.
Did: spent 17 points — gas power plant, advanced road services, incineration, hospital, college, highways, large roads, roundabouts, recycling, trains, advanced electricity (11 left). Bought two tiles (108k): west of Southfield and south of it. Two new streets west from x=-860 (z=-1620 Medium, z=-1852 Small, to x=-1300) with six wind turbines on their south sides (+~29 MW), 596 industrial cells on their north sides, landfill 4 at (-1226,-1548). Incineration plant (1M) and gas plant were refused by the game on the north side of z=-1620 (a landfill fits there, the 200×216 m lot does not — slope 4%?); not built yet.
Why: turbines cost 25k each and need no fuel trucks, so they end the shortage today; factories west of Southfield are downwind and give the south jobs without a trip through town.
Caption: southfield went dark. six new turbines switch it back on.
Incident: milestone 8 popup paused the run at 08:14 (high-density housing unlocked, +8 points) → closed it, run resumed. Power now 71 MW vs 41 MW used. Seen: 3 houses destroyed by water at (275,-300) on the east bank; both new landfills report "Facility Full".

## Turn 16 · 2027-01-01 00:16 · pop 21,755 · balance +1,604,938/mo · happiness 64%
Saw: power fixed (71 MW made, 50 used). Unemployment 6.9%; treasury 2.74M. Happiness fell 68→64 and health is 58. All housing demand at 100, high density now unlocked (milestone 8). River water destroyed 8 houses on the east bank around (275,-310). Water capacity fell 161k→125k (use 67k). Offices: 699 zoned cells still empty although demand is 100.
Did: saved Fableton_T16_start. **South district** on the new tile: x=-520 avenue (Medium) and x=-860 / x=-340 streets extended to z=-2664; cross streets z=-2200, -2316, -2432 (Medium), -2548, -2664. **Hospital** at (-774,-2712) (1.88M; it was refused on the avenue, fits on the last street). Elementary school 4, fire house 5, park, playground. Zoned high-density housing along the avenue and z=-2432 (~520 cells), medium on the other cross streets (~2,400), low on the side streets (~1,000), shops at the two main crossings. Dezoned 118 cells on the flooded east bank. Treasury 605k.
Why: health was the weakest number and the clinic network had no hospital; every housing type is wanted and unemployment is low enough to let people in; nobody should rebuild where the river comes over the bank.
Caption: first hospital, first towers. the city grows south.
Incident: "new signature building" popup (Gatehouse Residences, free) paused the run at 09:04 → clicked OK, run resumed. Pop 24,455, happiness back to 70%.
Incident: 5-car deadlock loop at the signalled junction (-180,-1156) with the Small part of z=-1156 → traffic lights off there; run resumed. Other long queues: (-590,-464) 40 cars, SW link (-942,-1151) 25 cars.
Incident: 3-car deadlock on the SW link at (-942,-1151) → widened the link to Large Road from x=-860 to -1187 (the last segment to the highway refused: OverlapExisting); run resumed.

## Turn 17 · 2027-01-02 00:26 · pop 27,981 · balance +1,493,594/mo · happiness 66%
Saw: +6,200 residents in a day (the south district filled at once), milestone 9 "Great Town". Unemployment jumped to 16.9% with 16 free jobs; power is at the limit again (71.1 MW made, 71.0 used); health up to 65 with the hospital; garbage 927k/mo; river water has destroyed 19 houses on the east bank. Medium and high housing demand is now ~0, low still 100.
Did: no new housing. Tried to open the flat land north of the river (x 400..700, z 450..760): road z=440 (x 260..790) and a **gas power plant at (480,604)** are built there, but the bridge from (260,116) is NOT: only a loose middle span (260,190)-(260,310) stands, both bank spans were refused (InWater / SteepSlope). The plant is not connected to anything yet. Instead: three more turbines on a new street z=-2084 (x -860..-1300), a link x=-1300 between z=-1620 and z=-1852, and 665 industrial cells around those streets. Spent ~505k, treasury 1.53M.
Why: jobs first — the town let in more people than it had work for; turbines are the only power I can add in minutes while the bridge problem is unsolved.
Caption: built a power plant across the river. forgot the river.
Incident: building fire at (-316,-84), centre → nearest fire house is within reach (distance printed in the log); nothing to change; run resumed.

## Session end · 2027-01-03 00:29 (real time 2026-11-12 04:18)
Session 3: turns 15–17. Game paused and saved as `Fableton_T18_session3_end`; recording, watcher, `popup_closer.py` stopped.
State: pop 29,804 · happiness 63% · health 64 · money 2.87M · balance +1.37M/mo · unemployment 16.3% (101 free jobs) · power 86.9 MW made / 64.3 used · **water 129.6k used / 101k capacity, sewage 129.6k / 100k** · garbage 970k/mo · traffic 45% · 28 dev points · milestone 9.
Start the next session with turn 18 and item 1 of the Current plan (water) before running any time.

## Session start · 2027-01-03 00:38 (real time 2026-11-12 12:57)
New chat (session 4). Recording, watcher and `popup_closer.py` started.

## Turn 18 · 2027-01-03 00:38 · pop 29,814 · balance +1,369,839/mo · happiness 63%
Saw: water use 129.7k against 102.8k capacity (two groundwater pumps, yield falling), sewage 129.7k against 100k. Unemployment 16.3% with 105 free jobs. The 699 empty office cells are all in one block south-west of the centre (x -1260..-1000, z -720..-490) where nothing has ever grown. Treasury 2.88M.
Did: three groundwater pumps on new stub streets west of the x=-520 avenue (z=-740, -860, -980) over the south-west aquifer; a second sewage outlet at (-400,313) next to the first. West half of the dead office block rezoned to industry (356 cells); 269 office cells painted on the x=-520 avenue around z=-2000 in the south district. Development points: university, water treatment, welfare office, park maintenance, fire station, crematorium (19 left).
Mistakes: a "dry run" of four road variants built all of them (three are now the pump streets, one spare stub at z=-850). The office circles in the south also covered ~120 cells of occupied houses; those homes will be replaced by offices.
Why: people without water leave before people without jobs do; the aquifer is the only water I can reach in minutes. Jobs must come to where the unemployed live, and the old office block is dead for a reason I do not know yet — industry there is the test.
Caption: three new wells. and four roads i only meant to preview.
Incident: row-house fire at (-292,-496) → a fire house stands 76 m away, nothing to change; bulldozed 15 flood ruins (most now on the north edge of the centre, x 80..230, z 84..152 — the river is reaching z=116); run resumed.
Incident: office fire at (-610,-398) → fire house 307 m away, nothing to change; run resumed. Water now 318k capacity / 131k used, sewage 200k / 131k — shortage over.
Incident: 3-car deadlock at the unsignalled Large Road junction (-860,-1156) → traffic lights on; run resumed. For the next turn: 128 cars queue on the Small Road x=-340 at z=-1678, 46 at the SW link junction (-1187,-1137).
Incident: 2-car deadlock at the signalled junction (-520,-1852) → lights off there. My three pump stubs had put traffic lights on the x=-520 avenue every 60 m (74 cars queued at z=-1010) → lights off at all three; run resumed.

## Turn 19 · 2027-01-05 00:36 · pop 32,920 · balance +1,943,316/mo · happiness 58%
Saw: water fixed (287k capacity / 129k used). +3,100 residents, treasury 5.98M. Happiness fell 63→58 and health 64→59: 58 garbage icons (1.08M/mo, three landfills full) and the new sewage outlet reports "pipeline not connected". Unemployment 14.0% (101 free jobs). Nothing grew on the rezoned half of the dead south-west block either — not offices, not industry. Commercial demand 96.
Did: **incineration plant** (1M) at (-1085,-828), south side of the z=-712 street in the dead block — the game accepted the big lot there. **Wastewater treatment plant** (400k) at (-402,230) on the outlet road, because a road to the second outlet is refused (InWater). Treasury 4.58M.
Why: happiness is under the 60% target and garbage is the loudest complaint; the landfills fill in hours, a furnace does not. The land nobody wants to build on is the right place for it.
Caption: nothing grows on that block. so it gets the furnace.
Incident: house fire at (-451,-952) → fire house 371 m away, nothing to change; cleared one collapsed shop at (-535,-26); run resumed.
Incident: warehouse fire at (-888,-130) in the west industrial district → nearest fire house was 658 m away; built a **fire station** at (-940,-203) on the industrial spur (treasury 3.26M after it); run resumed.
Incident: milestone 10 "Small City" popup stopped the run at 01-06 01:29 → closed it. The hour was over, so the run was cancelled at 01:54 (about 23 h short).

## Session end · 2027-01-06 01:54 (real time 2026-11-12 14:03)
Session 4: turns 18–19. Game paused and saved as `Fableton_T20_session4_end`; recording, watcher, `popup_closer.py` stopped.
State: pop 35,606 · happiness 64% · health 64 · money 4.57M · balance +1.79M/mo · unemployment 15.5% (104 free jobs) · power 113.7 MW made / 47.4 used · water 455k capacity / 161k used, sewage 632k / 161k · garbage 1.18M/mo · traffic 39% · 29 dev points · milestone 10.
Start the next session with turn 20 and item 1 of the Current plan (jobs).

## Turn 20 · 2027-01-06 01:54 · pop 35,606 · balance +1,788,639/mo · happiness 64%
Saw: unemployment 15.5% with 100 free jobs; only 40 office, 41 shop and 98 industrial cells empty, so demand (office 90, shops 73, industry 56) has nowhere to land. The "dead" south-west block finally filled (282 office + 303 industrial cells occupied). Garbage icons gone since the furnace started. 22 flood ruins: the river surface (~461 m) stands level with the low bank on both sides of the z=116 street (x 48..290) and the east edge at (140..206, -380..-492).
Did: zoned empty roadside only — shops 282 cells (z=-470 road at x -800..-600, z=-696 street), offices 344 cells (z=-480 road x -1200..-800), industry 344 cells ((-1300,-1700) and (-1100,-2100)). Bulldozed the 22 ruins and dezoned their lots (165 cells). Removed the never-connected second sewage outlet. No new housing.
Why: the jobless are the one target I miss; every job zone was full, so the fix is land, not taxes. Homes on a bank level with the river will drown again — give that strip back to the water.
Caption: 2,400 people out of work. so: shops, offices, factories. no houses.
Also (while the clock ran): development points → large parks, sports parks, city hall (21 left). **South-west highway exit rebuilt**: my two shortcut roads crossed both highway carriageways at grade (z=-1128 and z=-490) and the highway crawled at 6–20% flow. Built a 710 m Small Road loop from the Large Road junction (-1187,-1137) south, west under the highway bridge in the valley at z=-1314 (deck 16 m above), and back north to the southbound carriageway at (-1369,-1128); then removed both 20 m crossing links. Every turn onto or off the highway there is now a right turn. One factory at (-1174,-1174) bulldozed for the road. Southbound access at z=-490 is gone on purpose (the full interchange at z≈0 is 500 m north).
Also: **the north bank is open.** Extended the z=0 arterial 80 m east (two houses bulldozed) and built a 440 m Medium Road bridge at x=340 in one span — `/build/road` with `bridge=true` between two existing nodes, (340,0) and (340,440), worked first time; the old loose span at x=260 is gone. Street grid on the flat north bank: x=340/476/612/790/900 × z=440/556/672/788/880. Zoned shops along z=440 and offices on the east edge only; housing there waits for the jobless rate. Unused gas plant on the north bank demolished (upkeep 3.11M → 2.81M/mo; power is still 108 MW made / 51 used).
Mid-run check (01-06 15:48): jobs 13,749 → 14,556 in 14 h, the new industrial cells filled first; city traffic flow 39 → 47% a few hours after the exit rebuild. Added 230 more industrial cells (z=-1700 street, along the new loop road).
Incident: gridlock alarm at 01-06 16:33 → the loop had already cleared (0 deadlocks on inspection; longest queue is 85 cars at the map-edge highway exit, outside my reach); run resumed.
Incident: truck on fire on the highway at (-1307,-218) → fire station 370 m away, nothing to change; watcher filter widened so burning vehicles with an NA_ prefix no longer pause the game; one more flood ruin at (22,152) cleared and dezoned; run resumed.
Mid-run (01-07 00:31): pop 37,945, unemployment 14.1%, happiness 62. Industry is the only job zone that fills within hours (offices 560 and shops 533 cells still empty), so: **West Works** — a 700 m Medium Road along x=-1470 from the loop junction (-1470,-1150) north to z=-450, west of the highway, 992 industrial cells on both sides. Trucks reach the highway by right turns only.
Incident: 2-car deadlock at the signalled junction (-520,-1272) on the x=-520 avenue → traffic lights off there; run resumed.
Mid-run (01-08 21:01): pop 40,559, unemployment back up to 16.9%, happiness 60. The last high-density lots filled (+2,600 people) while nothing at all has grown on the roads I built this turn (West Works 1,092 cells, north bank 969 cells) — same as the old "dead block", which needed ~2–3 days after its roads were built. Zones on OLD roads fill within hours. So: scanned the old town on a 40 m grid for pockets with zonable but completely unzoned cells and painted them (r=22, no occupied cell touched): 589 office + 119 industrial cells.
Incident: 2-car deadlock at the signalled junction (-180,-696) → traffic lights off there; run resumed.
Incident: the same junction (-180,-696) locked again 8 game-minutes later with 3 cars and no lights → all-way stop there; run resumed.
Incident: "new signature building" popup (Principlis office) stopped the run at 01-09 00:11 → closed it; run resumed.
Incident: gridlock alarm at 01-09 10:23 → already cleared on inspection (0 deadlocks); run resumed.
Incident: house fire at (-120,-952) at 01-09 17:55 -> fire house 176 m away, nothing to change. The hour was over, so the run was cancelled here (about 8 h short).
Result of turn 20 (01-09 17:56): pop 42,048 · balance +2,859,946/mo · happiness 62% · unemployment 17.7% · treasury 13.5M · traffic 44%. Jobs grew 13,749 -> 15,824 but 6,400 people moved in. Last act: taxes - industry, offices, shops 10 -> 8%, residential 10 -> 11%.

## Session end · 2027-01-09 17:56 (real time 2026-11-12 15:05)
Session 5: turn 20 only (one long run, 88 of 96 h). Game paused and saved as `Fableton_T21_session5_end`; recording, watcher, `popup_closer.py` stopped.
State: pop 42,048 · happiness 62% · health 64 · money 13.53M · balance +2.86M/mo · unemployment 17.7% (18 free jobs) · power 96.4 MW made / 49.9 used · water 455k capacity / 117k used, sewage 492k / 117k · garbage 1.33M/mo · traffic 44% · 21 dev points.
Start the next session with turn 21 and item 1 of the Current plan (do the new job zones grow?).

## Session start · 2027-01-09 17:56 (real time 2026-11-12 15:08)
Session 6. Recording, watcher and helper started.

## Turn 21 · 2027-01-09 17:56 · pop 42,048 · balance +2,255,905/mo · happiness 62%
Saw: unemployment 17.7%, 18 free jobs. No game time has passed since the last check, so West Works (986 empty industrial cells) and the north bank (961 empty) are still bare; both are on owned tiles and the roads are connected, so I keep waiting (the old "dead block" needed 2-3 days). Tax cut cost ~0.6M/mo of balance. Air-pollution icons sit over the old centre (x -480..-120, z -480..120), downwind of the first industrial spur; noise icons line the x=-840 road at z -2160..-1440.
Did: **University** (1.5M) on the north bank, west side of the x=340 road, lot x 104..328, z 454..774. **College** (0.75M) in the north-bank grid: removed the inner street (612..790, 672) and put it at (684,672). Bulldozed and dezoned 3 drowned offices at (262..275, -335..-287). 24 h run.
Why: every job zone on an old road is full and new land takes days to wake up; campuses hire staff at once and take adults out of the job queue as students - and the town had no schooling above high school.
Caption: no jobs? then school. a university and a college on the north bank.
Incident: house fire at (-597,-1068) at 01-09 19:29 -> fire house 477 m away, nothing to change; run resumed.
Incident: house fire at (-50,-316) at 01-09 21:44 -> fire house 377 m away, nothing to change; run resumed.
Incident: 2-car deadlock at the signalled junction (-180,-1272) at 01-09 21:48 -> traffic lights off there; run resumed.
Incident: 3-car deadlock at the signalled junction (-520,-2200) at 01-10 01:43 -> traffic lights off there; run resumed.
Result of turn 21 (01-10 17:55): pop 42,804 · balance +2,434,230/mo · happiness 58% · unemployment 17.5% (3,586 people) · treasury 13.57M. Jobs 15,824 -> 16,836. **The north bank woke up**: all 543 office cells and 389 of 410 shop cells built in one day, 4-5 days after its roads. West Works (roads 3.7 days old) still bare - same clock, expect it next turn.

## Turn 22 · 2027-01-10 17:55 · pop 42,804 · balance +2,434,230/mo · happiness 58%
Saw: happiness slipped under the 60 target; the jobless number is flat because 1,700 people moved in while 1,000 jobs appeared. Office demand 100 (16,653 companies waiting) with 291 empty cells; industry demand 79 with West Works still asleep. Office High is unlocked and I had never used it. 14 fire icons are one burning grove at (750..840, -770..-700), no buildings.
Did: zoned **Office High, 843 cells** on every empty lot of the north bank's west half (x 340..612, z 440..880) - roads there are now "awake". One more drowned office cleared at (-376,296). 48 h run.
Why: towers hold several times the jobs of low offices per cell, on land that just proved it grows in a day. The east half of the north bank stays free for housing once the jobless rate falls.
Caption: 16,653 companies waiting for a desk. fine. towers.
Also (while the clock ran, 01-10 20:53): land ahead of need - a Small Road loop in the empty field between the old town and the highway interchange, (-1140,354) -> (-1140,170) -> (-980,170) -> (-980,354), zoned Office High. It should wake around 01-14. Housing plan: the north bank's east half (~2,100 free cells) as Residential High can hold most of the 32k people still missing, so no new tiles are needed yet - jobs first.
Incident: house fire at (218,-256) at 01-10 22:34 -> fire house 635 m away, nothing to change; run resumed.

## Note from the client (by the operator) · real time 2026-11-12
The Goal section of MAYOR.md was updated: pace (+10,000 residents per session), a 2–3 month reserve with the rest invested, quality targets checked at the finish, several projects per turn. Re-read it before planning turn 21.
Result so far (run cancelled at 01-11 05:35 after 11.7 of 48 h - the human ended the session): pop 42,930 · balance +2,351,672/mo · happiness 58% · unemployment 17.0% · treasury 14.74M · jobs 17,088.

## Session end · 2027-01-11 05:35 (real time 2026-11-12 15:40)
Session 6: turn 21 and the first 12 h of turn 22. Game paused and saved as `Fableton_T22_session6_end`; recording, watcher, `popup_closer.py` stopped.
State: pop 42,930 · happiness 58% · health 62 · money 14.74M · balance +2.35M/mo · unemployment 17.0% (103 free jobs) · power 96.0 MW made / 53.7 used · water 442k capacity / 122k used, sewage 484k / 122k · garbage 1.38M/mo · traffic 41%.
Start the next session by finishing turn 22 (run 36 h), then item 1-2 of the Current plan.

### Session 7 · turn 22 continued (run resumed 01-11 05:35, 36 h)
Saw: free "awake" land is almost gone — the north bank's 2,100 unzoned cells are block interiors behind offices, only 242 were real lots. Office High occupied=137 on the west field = my 01-10 paint went over 137 cells of working industry there (lesson: check `occupied` before painting). West Works still bare at 4.2 days.
Did (while the clock ran): 1) Residential High on the 242 free north-bank lots. 2) **Upzoned 894 cells of old-centre low housing** (x 0..320, z -320..20) to Residential High — old roads, so towers replace houses within hours. 3) **East Bank**: Small Road bridge (90,-580)->(400,-580) (Medium was refused; replace to Medium refused too: InWater), Medium arterial z=-580 to x=860, street grid x 470/606/742/860 × z -464/-696/-812/-900, 1,315 Residential High cells + corner shops; service block x 606..860, z -900..-812 left free. 4) **West Field** (north bank west of the university): Medium Road z=440 -> x=60 -> north to z=880, streets z 556/672/788/880 and x -76/-212/-330, 1,246 Residential High cells; service block x -76..60, z 672..788 left free. 5) Bought the tile x -1558..-935, z -2805..-2182 (55k) and built **South Works**: Medium spine x=-1152, streets x -1440/-1300/-1008 × z -2200..-2664, links to the housing at (-860,-2200) and (-860,-2432), 1,520 industrial cells.
Why: the client wants +10,000 residents per session and quality is judged at the finish, so housing can no longer wait for jobs: towers on old roads for people now, three new districts on a 4-day clock for the next turns. Roads cost almost nothing against a 15.8M treasury.
Caption: three new districts in one morning. the bulldozers are tired.
Also (01-11 evening): services for the new districts before anyone moves in — West Field: elementary school, clinic, fire house, park (block x -212..60, z 672..788, the x=-76 segment removed to fit the school); East Bank: elementary school north of z=-464, clinic, fire house, police, park in the south block. Happiness money: 8 dev points on sports parks + telecom; welfare office in South Works (-1078,-2272), telecom tower (-460,-660), community pools at (-364,-406), (-726,-1098), (-435,-888), (-124,-1192), (-376,-1562), (-774,-1656), (540,-428), (-10,520), basketball (800,-432). ~0.9M in total.
Also (01-12 ~01:00): **bus lines unlocked at last** — the lock was "Bus Stop/Station Built Req": stops placed through the bridge do not count, a real BusStation01 does. Built one on the south edge of South Works (-1080,-2724) and created lines 1 "North Works" (12 stops) and 2 "South Works" (14 stops) with `cs2_create_transit_line` and {x,z} stops (snapRadius 12; the ids in turns/bus_stops.json are stale).
Incident: house fire at (-488,-884) at 01-12 04:30 -> fire house 362 m away, nothing to change; run resumed. (Milestone 11 "Big City" popup at 01-12 03:44 closed with rog/close_popup.sh: +275k, +11 dev points, +18 permits.)
Incident: office fire at (-610,-258) at 01-12 07:53 -> fire house 335 m away, nothing to change; run resumed.
Incident: 2-car deadlock at the signalled junction (-180,-1040) at 01-12 08:42 -> traffic lights removed; run resumed.

## Turn 23 · 2027-01-12 17:35 · pop 48,246 · balance +4,123,869/mo · happiness 65%
Saw: turn 22 result — pop +5,316 in 36 h, **unemployment 17.0% -> 9.1%**, jobs 17,088 -> 21,050 (office towers on the north bank: 865 of 1,176 cells built), happiness 58 -> 65, treasury 17.9M. Shops and services now report missing workers. The East Bank started growing after ONE day (not four) — but with no power, water, sewage or workers: my bridge's west end was a separate node 11 m above the street end, not connected. Water use doubled (122k -> 233k of 441k). Deadlocks at signalled junctions again.
Did: reconnected the bridge (demolished the old stub, `road()` connect (40,-580)->(90,-580) snapped to the bridge node). Lights off at (340,672) and (340,556) on the north spine (69 cars queued). Tried a second north bridge (40,116)->(60,440): the span was built but its south end again hung 9 m above the low junction; removed the south half, **the north half (51,300)->(60,440) is still standing as a dead-end pier** — finish it from a town node at ~470 m height or demolish it. Utilities for +20k people: 5 wind turbines on the edge of South Works (+25 MW), 4 groundwater pumps on the east aquifer (96,-84), (228,-58), (-14,-84), (228,-174), second wastewater plant (-574,295). Upzoned the west half of the old centre (x -340..-20, z -320..20) from low to Residential Medium.
Why: labour is now the scarce thing, so housing is the lever again; medium demand is 100 while high-rise demand rests at 0 until the new towers fill.
Caption: built a bridge to nowhere. fixed it. nobody saw that.
Also (01-12 evening, clock running): utilities confirmed — East Bank outage icons gone, power 111 MW made / 86 used, water 762k, sewage 916k. Eight more wind turbines on the outer edges of the East Bank and north of z=880 in the West Field were ALL refused by the game (cause not checked) — power margin is only ~25 MW, find turbine sites first thing next turn.
Also: 3 turbines accepted inside South Works blocks at (-1226,-2296), (-1226,-2528), (-1080,-2528) (roadside, t=0.5) -> power 119 MW made / 90 used.
Incident: shop fire at (-202,-20) at 2028-01-01 13:51 (the calendar rolled from 2027-01-12 to 2028-01-01) -> fire house 551 m away, nothing to change; run resumed.

## Turn 24 · 2028-01-01 17:35 · pop 56,210 · balance +4,332,381/mo · happiness 67%
Saw: +7,964 people in 24 h (towers in the old centre, East Bank 744 cells built in a day once the bridge was really connected). Unemployment back to 12.5% (63 free jobs), office demand 100, industry 82. **South Works grew 647 cells in ONE day** — so new roads are not "dead for 4 days"; the earlier dead blocks were something else. West Works (986 cells) is still bare after 6 days although its road is connected and carries traffic. 60 hearse icons. Power 119 MW made / 97 used.
Did: West Works dezoned and zoned again in one pass (test). Office row z=-1260 (x -440..100) upzoned Office Low -> Office High, 196 cells. Crematorium in South Works (-1080,-2384). 2 more turbines in South Works (-1335,-2180), (-1263,-2412); six other spots refused. 24 h run.
Why: jobs must chase the 13k new residents — towers on old roads are the fastest job land; deathcare was the one service visibly short.
Caption: 56,000 people. the hearses are behind schedule.
Incident: 2-car deadlock at the signalled junction (-520,-2432) at 2028-01-02 00:20 -> lights removed; run resumed.
Incident: 2-car deadlock at the signalled junction (-1100,586) at 2028-01-02 01:23 -> lights removed; run resumed.
Incident: deadlock on the East Bank bridge at (375,-580), 15 cars queued, 2028-01-02 03:14 -> lights removed at the bridgehead junction (470,-580) (helper: turns/deadlock.py fix); the Small Road bridge is the district's only link - a second bridge is urgent; run resumed.
Incident: fire at (-535,-264) at 2028-01-02 12:45 -> station within reach, nothing to change; run resumed.
Result of turn 24 (2028-01-02 13:30, run cancelled 4 h early at the 60-minute mark - the game had dropped to speed 1): pop 61,673 · balance +4,370,847/mo · happiness 63% · unemployment 14.6% · treasury 24.46M. Office High 865 -> 1,057 cells built; industry did not move (7,258 occupied, 1,884 empty).

## Session end · 2028-01-02 13:30 (real time 2026-11-12 16:45)
Session 7: rest of turn 22, turns 23-24. Game paused and saved as `Fableton_T24_session7_end`; recording, watcher, `popup_closer.py` stopped.
State: pop 61,673 (session start 42,930, +18,743) · happiness 63% · health 64 · money 24.46M · balance +4.37M/mo · unemployment 14.6% · power 127.8 MW made / 80.9 used · water 779k / 250k, sewage 956k / 250k · traffic 42%.
Start the next session with items 2-4 of the Current plan (jobs, why industry is stuck, second East Bank bridge).
Incident: house fire at (-317,-1012) at 2028-01-02 16:33 (before the turn 25 run) -> fire house 225 m away, nothing to change.

## Turn 25 · 2028-01-02 16:33 · pop 61,722 · balance +4,322,296/mo · happiness 63%
Saw: final session. 13,300 people short of 75,000; unemployment 15.2% with 76 free jobs; office demand 100; 24.5M idle in the treasury. West Works still bare after the rezone test (988 empty industrial cells), South Works stuck at 755 empty. Built towers still have vacant flats (high-rise building demand 0), low/medium demand 100.
Did: (1) every fully empty industrial block in West Works and South Works repainted Office High (1,403 cells). (2) All 24 development points spent: tourist attractions, technical + medical university, radio telescope, geological research, police HQ, geothermal plant. (3) Bought 5 tiles south-east (204k) and built **Campus** on the flat plateau across the river (x 210..742, z -2280..-1800): ring of Medium Road, Medical University, Technical University, Geological Research Center, Radio Telescope, Observation Tower, Water Park, second hospital. (4) **Parkway** x=742 from the East Bank (742,-900) south to the campus with City Hall, Police HQ, a big high school and a second college on its east side - this is also the East Bank's second way out. (5) Bridge (150,-1504)->(210,-1800) from the town to the campus (checked with rg: joined to the old node). (6) Zoned Residential Medium along the parkway and the campus ring (1,650 cells), shops by the universities (650); upzoned 826 cells of old low housing in the centre to medium. (7) 8 wind turbines around the new district. Spent ~20M; treasury 4.5M.
Why: jobs for the educated were the bottleneck - universities, research and offices hire exactly them, and the idle money becomes science, tourism and services as the brief asks. Medium housing is where demand is.
Caption: twenty million in one afternoon. the city gets a campus.
Incident: deadlock alarm at 2028-01-02 17:28 -> the loop had cleared by itself; removed lights at the junctions holding 87-111 queued cars (north spine, highway exit); run resumed.
Incident: 2-car deadlock at the unsignalled junction (-180,-1040) at 2028-01-02 17:57 -> all-way stop there, lights off at (-180,-924); run resumed.
Incident: deadlock at the signalled junction (-520,-1156) at 2028-01-03 01:55, 4 cars queued -> lights removed; run resumed.
Incident: deadlock again at (-180,-1040) at 2028-01-03 04:49, 7 cars queued (stop signs did not help) -> traffic lights there; run resumed.
Incident: fire at the new campus hospital (158,-2150) at 2028-01-03 06:22, nearest station 639 m away across the river -> fire houses on the campus (178,-1860) and on the parkway (710,-1426); run resumed.
Incident: tower fire at (-654,-2404) at 2028-01-03 17:19 -> station 224 m away, nothing to change; run resumed.
Incident: deadlock alarm at 2028-01-03 22:55 -> the loop had cleared by itself, nothing changed; run resumed.
Incident: deadlock alarm at 2028-01-04 02:36 -> cleared by itself again, nothing changed; run resumed.
Incident: deadlock again at (-520,-1156) at 2028-01-04 07:31 with the lights off, 3 cars queued -> all-way stop there; run resumed.
Result of turn 25 (2028-01-04 16:33): pop 70,744 (+9,022 in 48 h) · balance +5,321,094/mo · happiness 74% · unemployment 16.8% (7 free jobs) · treasury 12.98M. Parkway and Campus zones filled completely within two days (839 housing cells, 572 shop cells). Office High: South Works took 512 cells, **West Works took 0 of 667** - that land is dead for offices as well as industry. Power 166 MW made / 90 used.

## Turn 26 · 2028-01-04 16:33 · pop 70,744 · balance +5,321,094/mo · happiness 74%
Saw: people arrive faster than jobs: 41,668 adults, 25,481 jobs, 7 free. All three housing demands at 100, 1,350 empty high-rise cells waiting, so 75,000 is close; unemployment is the one target still far off. Fresh flat roads fill in a day or two, West Works never does.
Did: upzoned every pure Office Low circle on old roads (west and centre, not the new north bank) to Office High - 1,690 cells. Bronze Statue at the campus (790,-1980), second crematorium (628,-2332) for the 5 hearse icons, parks in the West Field, East Bank, Parkway, north bank and the West Field loop. Treasury 9.6M.
Why: towers on old roads are the only job land that has reliably grown within hours; each rebuilt block holds several times the workers.
Caption: 70,000 people, seven vacancies. swapping office blocks for towers.
Also (clock running): bought 2 more tiles east (123k) and built **Office Row**: Medium Road x=990 from z=-960 to z=-1690 with a link z=-1690 back to the parkway (742,-1690); Office High on both sides (~1,000 cells) - fresh flat-ish roads are what filled fastest this session. The north end (990,-960) is a dead end: the tile north of z=-935 is not owned (ExceedsCityLimits).
Incident: deadlock at the signalled junction (-340,-2432) at 2028-01-04 21:17, 3 cars queued -> lights removed; run resumed.
Result of turn 26 so far (2028-01-04 22:04, run stopped by the human after 5.5 h to end the session): pop 70,927 · balance +5,641,369/mo · happiness 75% · unemployment 11.1% (jobs 25,481 -> 27,756) · treasury 10.69M. Office High occupied 1,569 -> 4,030 cells.

## Session end · 2028-01-04 22:04 (real time 2026-11-12 17:48)
Session 8: turn 25 and the start of turn 26. Game paused and saved as `Fableton_T26_session8_end`; recording, watcher, `popup_closer.py` stopped.
State: pop 70,927 (session start 61,722, +9,205) · happiness 75% · health 68 · money 10.69M (start 24.49M) · balance +5.64M/mo (start +4.32M) · unemployment 11.1% (start 15.2%) · power 163 MW made / 106 used · water 842k / 328k, sewage 968k / 328k · traffic 40%.
Not reached: 75,000 (4,073 short) and unemployment < 10%. Start the next session with item 1 of the Current plan (run the remaining 48 h and watch Office Row).

## Turn 27 · 2028-01-04 22:04 · pop 70,927 · balance +5,641,369/mo · happiness 75%
Saw: session 9 (final). 4,073 people short of 75,000; all housing demand at 100 with 1,333 empty high-rise cells. Unemployment 11.1% with only 90 free jobs; shops demand 73, industry 86, offices 0 (1,545 office cells still empty). 10.7M in the treasury, 8.7M of it idle.
Did: scanned the whole city for fully unzoned pockets on existing roads and zoned them: 289 cells Commercial High + 507 Commercial Low next to homes and offices, 331 industrial next to factories (West Works and the flood strips skipped). Education: 3 elementary schools (-900,-1533), (-774,-2356), (698,-1163) and 3 high schools (-430,-1780), (-934,-2392), (268,828) - 12,500 children had 6 schools. Leisure: skate park, 2 basketball courts, 3 tennis courts, 2 big city parks, a long park, 2 dog parks across the west, East Bank and north bank.
Why: jobs are the last missing target and shops/industry are what the demand bars ask for; the idle money goes to schools and sport, which the city has least of per head.
Caption: 4,000 to go. shops in every gap, six new schools.
Incident: deadlock alarm at 2028-01-04 23:05 -> loop had cleared by itself, nothing changed; run resumed.
Note: IceflakeArena01 (free signature building, 192x136) and RecyclingCenter01 (176x144) fit nowhere on existing roads - they need a new road on flat land.
Also (clock running): the empty high-rise land in the West Field N was not being built (towers 2,292 -> 2,266 cells in 12 h at demand 100), so 695 empty Residential High cells there became Residential Medium (pockets touching existing towers left alone); 88 circles of old low housing (1,669 cells, every third entry of t25_low2.json) upzoned to medium.
Incident: office fire at (876,614) at 2028-01-05 10:35, nearest station 852 m away -> fire house on the north-east bank; run resumed.
Also (clock running): spent 24 of 25 development points on Health Research Institute, Disease Control Center and Large Hadron Collider. Built the Health Research Institute on Office Row (1038,-1060) (1M) and a Recycling Center in South Works (-1226,-2004) (880k). Disease Control Center (200x160, 2M), Iceflake Arena (192x136, free) and the collider (432x512, 4M) found no lot on existing roads - they need a new flat site. Treasury 10.7M.
Note: speed 1 during a run is not a bug - popup_closer.py drops to normal speed while a fire burns and returns to 8 afterwards.
Also (clock running): **Science Park** east of Office Row - Medium Road loop (990,-1420)-(1240,-1420)-(1240,-1160)-(990,-1160); Disease Control Center at (1177,-1512) (2M) and Iceflake Arena at (1177,-1080) (free) on its outer sides. The inside of the loop (250x260) is still empty. Big lots do place on ~125 m segments (sweep with minlen 90 in turns/t27e.py). Treasury 8.8M.
Incident: tower fire at (534,-672) at 2028-01-05 14:36 -> station 294 m away, nothing to change; run resumed.
Result of turn 27 (2028-01-05 22:04): pop 75,840 (+4,913 in 24 h) · balance +5,517,422/mo · happiness 75% · unemployment 9.4% (jobs 27,756 -> 30,848) · treasury 11.1M. **75,000 passed.** Medium housing took 1,000 more cells; shops demand fell to 0 after the new commercial pockets filled.

## Turn 28 · 2028-01-05 22:04 · pop 75,840 · balance +5,517,422/mo · happiness 75%
Saw: every finish target is met for the first time: 75,840 people, happiness 75, unemployment 9.4, no utility warnings (power 159/109 MW, water 753k/389k, sewage 968k/389k). 6 hearse icons, health 68. Office demand back at 45, industry 81. 11.1M in the treasury. Now it has to hold for one in-game month.
Did: saved as Fableton_T28_75k. Third hospital at the Science Park (938,-1488) (1.88M), third crematorium in South Works (-1080,-2036), Office High inside the Science Park loop (461 cells). Collider still has no site: a city-wide placement sweep runs with the clock.
Why: unemployment is only 0.6 points under the limit, so more office land keeps the margin; health and deathcare are the weakest services; the rest of the idle money is meant for the collider.
Caption: 75,840. now hold it for a month.
Also (clock running): the collider sweep over eight edge areas found no 432x512 lot (it needs a new flat site; the flattest empty one is around (-1960,28), west of the highway, unowned, 14 m of relief). Five more parks in the old west side: (-344,-500), plaza (-908,-2258), (-435,-956), (-605,-1544), playground (-775,-1132). Treasury 9.7M.
Incident: park fire at (-430,-2292) at 2028-01-06 08:37 -> station 108 m away, nothing to change; run resumed.
Incident: factory fire at (-640,-264) at 2028-01-06 09:45 -> station 306 m away, nothing to change; run resumed.
Result of turn 28 (2028-01-06 22:04): pop 78,730 (+2,890 in 24 h) · balance +5,186,549/mo · happiness 75% · health 69 · unemployment 8.6% (jobs 31,616) · treasury 13.86M. Population stayed above 75,000 from 2028-01-05 19:00 to 2028-01-06 22:04 (lowest sample 75,186) - a full in-game month.

## Turn 29 · FINAL · 2028-01-06 22:04 · pop 78,730 · balance +5,186,549/mo · happiness 75%
Saw: the goal held for a whole in-game month: 78,730 residents, happiness 75%, unemployment 8.6%, no loans, monthly balance +5.2M; power 159 MW made / 106 used, water 753k / 394k, sewage 932k / 394k, the incinerator and the new recycling center take the garbage, no utility warning anywhere on the map.
Did: saved as Fableton_FINAL_78730 and stopped.
Why: every finish condition in MAYOR.md is met.
Caption: 78,730 residents. the meadow is a city.
Summary: Fableton started as a grid on an empty meadow with one million, factories by the highway and homes by the river. It grew by filling whatever the demand bars asked for, then by jumping the river with bridges to the north bank, the East Bank, the campus plateau and South Works when the first tiles ran out. The two moves that mattered most late were upzoning old low housing to medium density (tens of thousands of residents on roads that already existed) and swapping low office blocks for towers plus Office Row, which pulled unemployment from 17% to under 9%. The surplus went into three universities, nine schools, three hospitals, a science park and parks. Not done: the Large Hadron Collider is unlocked but has no flat 432x512 site, so 13.9M sits in the treasury instead of the ~2M reserve the rules asked for.

## Session end · 2028-01-06 22:04 (session 9, final)
Session 9: turns 27-28 and the finish. Game paused and saved as `Fableton_FINAL_78730` (also `Fableton_T28_75k`); recording, watcher stopped.
State: pop 78,730 (session start 70,927, +7,803) · happiness 75% (start 75%) · money 13.86M (start 10.69M) · balance +5.19M/mo (start +5.64M) · unemployment 8.6% (start 11.1%).
Left over: ROG scheduled task `cs2-mayor-click` is NOT deleted yet; `popup_closer.py` still runs on the Mac; 1 development point unspent; the collider needs a site.

## Turn 30 · BUILD-OUT · 2028-01-07 · pop 85,136 · balance +3,405,658/mo · happiness 77%
Saw: 13.86M idle, one development point, the collider still without a site; residential demand 100 everywhere, industrial 82, office 0. Mid-session Milestone 14 "Grand City" arrived (+14 points) and a storm wrecked 16 buildings on the highway side.
Did: bought 5 tiles west of the highway. Road in from the z=-490 exit, avenue z=-270 and loops x=-1650/-1470/-2240. **Large Hadron Collider** placed first try at (-1918,16); **Space Center** at (-2510,-74) after buying Airport+SpaceCenter+Heliport nodes (the first point went to the Firewatch Tower). Three signature buildings (office, medium residential, manufacturing), bus station + line 4 "Collider Express" to the old bus station, hospital, college, 2 elementary schools, high school, clinic, 2 fire houses, police, post office, firefighting heliport, battery station, taxi/road/park depots, ~20 parks and sports fields. Zoned ~3,900 cells (medium/high/low housing north and west, industry south at x=-1818, a little commerce). Airport: refused at every spot (1136x376 on a 3.5% slope). Cleared the storm ruins; rebuilt the hospital on a 2.5M loan.
Incident: gridlock at (-520,-1620) → traffic lights off. Incident: building fire (103,-492) → three fire houses within 760 m, resumed.
Why: the session's brief is to turn the whole treasury into the buildings the city never got; the flattest free land was west of the highway, and with demand at 100 the new streets fill on their own.
Caption: a collider and a spaceport on the meadow's west side.
Incident: building fire (-372,-1894) → fire houses in range, resumed.

## Session end · 2028-01-08 03:21 (build-out session, real time 2026-11-12 19:12)
Build-out: turn 30. Game paused and saved as `Fableton_BUILDOUT`; recording and watcher stopped. The last 96 h run was cut at SESSION_END_NOW (about 29 of the hours ran).
State: pop 90,761 (start 78,730, +12,031) · happiness 80% (start 75%) · money 1.98M (start 13.86M) · balance +5.19M/mo (start +5.19M) · unemployment 9.5% (start 8.6%) · loan 2.5M taken and repaid.
Left over: airport not placeable; ROG task `cs2-mayor-click` NOT deleted; `popup_closer.py` still runs on the Mac.
