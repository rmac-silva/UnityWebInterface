# Communication Protocol
[8][...] - First 8 bits are reserved for message type

## Message Types

### Messages
'M' - Message
'L' - Message Log
'MSG_SYNC' - Message Log Sync

### Levels & Patterns
'LVL_SYNC' - Unity sends over all the levels at the start of the session, so python has the updated list | Or the webapp requests all the levels from unity
'LVL_UPD' - An update of a given level, sent over to unity

### Game Sync
'LVL_STRT' - Unity sends over this message when the user starts a level, contains information about what level the user is on
'C_LVL' - Unity sends the current level the user is on, and wether if he's playing or not
'LVL_FIN' - Unity sends over this message when the user ends a level
'GS_SYNC' - Python requests a game status sync

### DDA
'OBS_CHNG' - Obstacle Constant / Setting change 
'SPW_CHNG' - Spawner Constant / Setting change 
'P_CHNG' - Player Constant / Setting change 
'HIT_REPO' - Hit Report, for when the player gets hit by a given pattern
'FASTER_S' - Faster Spawner
'SLOWER_S' - Slower Spawner

### Agent
'A_BUSY' - Tells unity the agent is busy processing a request
'A_RDY' - Tells unity the agent has finished executing

# Important!
After making changes to the patterns, don't forget to export them under Tools > Export Patterns

Delete the old ones from appdata if you changed the names of patterns, otherwise you can leave them be and they will be overwritten