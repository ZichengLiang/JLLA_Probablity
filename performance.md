### Obeservations


### Log
##### Change in simulation ticks does not affect runtime
The performance bottleneck: predict_starting_lineup
- Finding a player in the big big json file is expensive
- 10000 times monte-carlo simulation for team lineup is expensive and not necessary

Solution:
- Separate the players.json by team, now it's in ./team_files
- Reduce the iteration to 100 times, the result is the same, even better (ManCity vs Chelsea)

Increased performance by 100 times

##### Multicore processing
Increased performance by ~5 times (this may vary due to the nature of multiprocessing)