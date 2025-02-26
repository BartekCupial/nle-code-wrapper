# ROADMAP

### done:
- building strategies
- injecting strategies
- panic mode, exit running strategy when condition
- when we raise BotPanic we destroy state of the strategy, how to keep it?
    - we don't
- how to build strategies out of different strategies now?
    - just call inner strategy

### todo:
- decide what llm should see 
    - everything should be in 'Bot' class
- use api to query llms to create strategies
    - design prompts
        - information about task
        - decide which functions llms will know about
        - build documentation 
    - play selected minihack envs
    - llm builds strategy
    - llm gets feedback
        - exception messages
        - information about success
  


### Current approach
- Strategy decorator`Strategy.wrap`. Its features: 
    - keeps track of number of strategy steps
    - timeouts when we exceed max strategy steps
    - executes strategy 
- Strategies have access to Bot class and its contents
    - current and last state, glyphs, message, tty_chars
    - pathfinder (for movemement)
    - pvp (for keeping track of enemies and fighting)
    - inventory (can be easily indexed as a dictionary, example inventory["tools])
- 

### AutoAscend approach
- strategies are executed with few specific functions
    - until -> runs specific strategy until specific condition is met
    - before -> it combines two strategies, second one is executed after the first one yields True
    - preempt -> creates strategy that can be interrupted by other strategies
    - repeat -> repeats current strategy indefinitely
    - every -> runs the current strategy periodically

example for how gather items strategy is constructed
```python
    def gather_items(self):
        return (
            self.pickup_and_drop_items()
            .before(self.check_containers())
            .before(self.wear_best_stuff())
            .before(self.wand_engrave_identify())
            .before(self.go_to_unchecked_containers())
            .before(
                self.check_items()
                .before(self.go_to_item_to_pickup())
                .repeat()
                .every(5)
                .preempt(
                    self.agent,
                    [
                        self.pickup_and_drop_items(),
                        self.check_containers(),
                    ],
                )
            )
            .repeat()
        )

```

- how exploration works;
    - `explore1` explores new parts of the dungeon while searching and opening doors
        - gather items if there are some 
        - untrap and search for traps 
        - every now and then if identifies items on altar and dips for excalibur
    - there is also exploration for different levels since there is no limit for searching :>

```
            def exploration_strategy(level, **kwargs):
                return Strategy(
                    lambda: self.agent.exploration.explore1(
                        level,
                        trap_search_offset=1,
                        kick_doors=self.agent.current_level.dungeon_number != Level.GNOMISH_MINES,
                        **kwargs,
                    ).strategy()
                ).preempt(
                    self.agent,
                    [
                        self.identify_items_on_altar().every(100),
                        self.identify_items_on_altar().condition(
                            lambda: self.agent.current_level.objects[self.agent.blstats.y, self.agent.blstats.x]
                            in G.ALTAR
                        ),
                        self.dip_for_excalibur().condition(lambda: self.agent.blstats.experience_level >= 7).every(10),
                    ],
                )
```


```python
        return (
            open_visit_search(search_prio_limit)
            .preempt(
                self.agent,
                [
                    self.agent.inventory.gather_items(),
                    self.untrap_traps().every(10),
                ],
            )
            .preempt(
                self.agent,
                [
                    self.search_neighbors_for_traps(trap_search_offset),
                ],
            )
        )
```

### Notes:
- interesting: "MiniHack-HideNSeek-v0" might be salvaged, it's possible to solve it with correct combination of explore_room and run_away, this could be an example where NNs are better then LLMs. Especially possible when we will additionally use exploration with direction (west, east etc)


### what next?:
- what skills we are missing?
    - inventory management
        - (done) item usage (zap wand, read scroll/book, quaff potion, wear armor, wield weapon)
        - item identification
        - weight management
        - resource prioritization
        - armor class maximization
    - combat
        - (done) fighting (target selection, melee, kiting, engulfed)
        - spellcasting (heal, protection)
        - passive defence (passive attacks from monsters)
        - (done) use the optimal weapon or spell given situation
    - matter manipulation
        - (done) boulder pushing
        - corridor digging
        - phasing or other forms of manipulating the environment
    - survival
        - (done) food strategy
        - praying strategy
        - resource prioritization
        - escape strategy (eg. scroll of teleportation)
    - interactions with neutral monsters (shopkeeper, guards, quest giver)
    - (done) engraving
    - skill enhancement: improve weapon and spell proficiencies

