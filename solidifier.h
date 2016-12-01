#pragma once

#define assert sassert
#define solidifier_main main
#define nondet_uint nondet

typedef int bool;
typedef int uint;
typedef int bytes32;
typedef int uint256;

#define NONDET_SIZE

int nondet();

#define false 0
#define true 1

struct _address
{
    uint x;
    uint balance;
};

typedef struct _address address;

uint
address_send(address *from, address *to, uint val)
{
    from->balance -= val;
    to->balance += val;
    return 1;
}

address this;

void
throw()
{
}
