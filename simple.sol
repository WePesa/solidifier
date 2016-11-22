pragma solidity ^0.4.0;

contract Arithmetic {
    function assume(bool) {}
    function assert(bool) {}
    function nondet_uint() returns (uint) {}

    function inc(uint x) returns (uint)
    {
        return x + 1;
    }

    function solidifier_main() returns (uint)
    {
        uint x = nondet_uint();
        assume(x > 2);
        uint y = inc(x);
        assert(y >= 3);
        return 0;
    }
}
