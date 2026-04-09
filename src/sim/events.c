#include "events.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

/* Global variables definition */
int kdebug = 1;
int event_idx = 0;
event_t d_events[10000];
int d_status[N_PROCC];
int d_l_status[N_PROCC][N_CORES];
int d_count[N_PROCC] = {N_CORES, N_CORES, N_CORES, N_CORES};
int d_state = 0;

static int d_node = 0;
static int d_core = 0;
static double d_time = 0.0;

int generate_events(int num_events_limit) {
    int count = 0;
    event_t *e;

    while (count < num_events_limit && d_state < 4) { // 4 is STATE_END
        bool should_gen = false;
        int status = 0;

        /* Logic for d_status calculation */
        if (d_state == 0) { // STATE_IDLE
            status = 1;
            should_gen = true;
        } else if (d_state == 1) { // STATE_D_C
            status = (d_node % 2 == 0) ? 1 : 0;
            should_gen = (status == 1);
        } else if (d_state == 2) { // STATE_D_D
            status = 1;
            should_gen = true;
        } else if (d_state == 3) { // STATE_D_E
            status = (d_node % 2 == 1) ? 1 : 0;
            should_gen = (status == 1);
        }

        if (should_gen) {
            if (kdebug == 0) {
                e = (event_t *) malloc(sizeof(event_t));
            } else {
                if (event_idx >= 10000) return count;
                e = &d_events[event_idx++];
            }
            
            e->id = event_idx;
            e->time = d_time;
            e->node = d_node;
            e->core = d_core;
            e->prev_state = d_state;
            e->curr_state = d_state;
            e->l_status = status;
            
            // update global status tracking
            d_status[d_node] = status;
            d_l_status[d_node][d_core] = status;
            
            enqueue(e);
            count++;
        }

        /* Advance to next simulation step */
        d_core++;
        if (d_core >= d_count[d_node]) {
            d_core = 0;
            d_node++;
            if (d_node >= N_PROCC) {
                d_node = 0;
                d_state++;
                d_time += 1.0;
            }
        }
    }
    return count;
}
