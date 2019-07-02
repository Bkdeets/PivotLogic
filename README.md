#Trading Application

This is the base structure for our automated day trading application. 

<br>

### Contexts
This will hold the classes that represent execution contexts for strategies.
The Context class will be an abstract class which the Backtest, PaperTrade, and LiveTrade classes will implement.
Each strategy should be programmed with the same methods defined in Context, then, at runtime, 
the execution context (LiveTrade, PaperTrade, Backtest) will be specified.
This will allow us to create one file for each strategy and use an argument to 
execute the strategy in a different environment

<br>

### Strategies
This file will hold our strategies. Each strategy should have one file
here that uses the methods defined in Context to implement
the trading logic.

<br>

### Indicators
This file will hold calculations for indicators that some 
strategies will be built on.