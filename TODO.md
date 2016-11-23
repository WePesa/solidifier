### TODO

1. Calculate the estimated gas of each function - This is a problem if the 
function interact with the state of the blockchain, using BLOCKHASH, TIMESTAMP with some weird logic. I think
we can get trough some cases even in that case.
In the other cases, an accurate estimate can be given: To calculate we need to look at: https://github.com/ethereum/cpp-ethereum/blob/a6543809275b4f4c3bb86f4e2748182aaa61a711/libevmcore/EVMSchedule.h and run accordingly with a gasPrice.
We can let the user input the gas price and output Sum(operations)*gasprice
