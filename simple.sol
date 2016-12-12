pragma solidity ^0.4.0;

contract Ballot {

    function assert(bool) {}
    function assume(bool) {}
    function nondet_uint() returns (uint) {}
    function nondet_address() returns (address) {}
    function set_msg_sender(address) {}

    function solidifier_main() returns (uint)
    {
        for (var i = 0; i < 2000; i++) {
            i+=1;
        }
        return 0;
    }
}

