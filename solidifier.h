#pragma once

#define assert sassert
#define solidifier_main main
#define nondet_uint nondet

typedef int bool;
typedef int uint;

int nondet();

#define MAX_MAPPING_SIZE

struct _mapping_uint_uint
{
    uint id;
    uint data[MAX_MAPPING_SIZE];
};

typedef struct _mapping_uint_uint mapping_uint_uint;

#define false 0
#define true 1
