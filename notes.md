something to compare it to: sampling from what information might be, what would be the right thing to do if you know your opponent has X resource cards?
easiest thing to do is to randomize? do the imperfect info versions of MCTS work better than the determinized version?
come up with implementation of game and then baseline agent - come up with basic idea for the agent and put in references to the more advanced agents later
send copy of proposal draft a couple days before due (monday, tuesday)
code and report should be one of the deliverables

----------------------------------------------

baseline agent: anything that plays semi-reasonably
heuristic agent vs rule-based agent
can even just implement previous work's baseline agent to compare

would need to start with the IS-version
look at algorithms again - how to deal with not knowing specific state?
what does the algorithm do for the opponent

can do determinized version of MCTS first if i want
states based on what the other player has done recently
if they chose to do something that seems suboptimal, can infer that they didn't have the ability to do an optimal things
can sample possibilities of cards? and do actions
cut it off and apply heuristic/threshold? (VPs)
look at previous catan MCTS?
look into meta-actions

3:15 next friday

----------------------------------------------
