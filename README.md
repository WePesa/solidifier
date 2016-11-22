The Solidifier project aims at providing a set of tools for formal verification
of smart contracts written in Solidity or in the EVM bytecode form.

## Requirements
You need to have Solidity compiled to use Solidifier.
Please check the instructions here:
https://github.com/ethereum/solidity

## Usage
Your Solidity code should contain _assertions_, safety
properties you want to verify. Since Solidity does not have
a built-in _assert_ function, we have the following workaround:

1. In the beginning of your contract, add the code _function assert (bool) {}_
2. Use _assert(property)_ to tell Solidifier the conditions you want to verify
3. Now run _solidifier.py code.sol_

## Example
