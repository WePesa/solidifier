The Solidifier project aims at providing a set of tools for formal verification
of smart contracts written in Solidity or in the EVM bytecode form.

## Requirements

1. Solidity - https://github.com/ethereum/solidity
2. SeaHorn - https://github.com/seahorn/seahorn

## Usage
Your Solidity code should contain _assertions_, safety
properties you want to verify. Since Solidity does not have
a built-in _assert_ function, we have the following workaround:

1. In the beginning of your contract, add the code _function assert (bool) {}_
2. Use _assert(property)_ to tell Solidifier the conditions you want to verify
3. Now run _solidifier.py code.sol_

The assertion you are verifying might be inside functions that are called by external entities.
To ensure that these assertions are also verifiable, you can create a function
_function solidifier_main() returns (uint) {}_ and put code that uses the other functions inside
_solidifier_main_. The file _simple.sol_ contains an example of such usage.
Notice that variables should be set to nondeterministic values when the program is being verified
(as shown in _simple.sol_).

Another important tool is the function _assume_ which can be used to bound behaviors (as shown in _simple.sol_).
