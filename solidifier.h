#pragma once

#define assert sassert
#define solidifier_main main
#include "types.h"

uint nondet();
uint nondet_uint() { return nondet(); }
uint nondet_address() { return nondet(); }

void
bytes_copy(char *from, char *to, int bytes)
{
    while(bytes-- >= 0) to[bytes] = from[bytes];
}

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

struct _message
{
    bytes32 data;
    uint gas;
    address sender;
    bytes32 sig;
    uint value;
};

typedef struct _message message;

message msg;

void
set_msg_sender(uint x)
{
    msg.sender.x = x;
}

