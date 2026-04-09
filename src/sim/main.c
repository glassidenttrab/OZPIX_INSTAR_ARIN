#include <stdio.h>
#include <stdlib.h>
#include "events.h"

/* Simplified event queue management */
#define MAX_QUEUE 1024
event_t* event_queue[MAX_QUEUE];
int queue_head = 0;
int queue_tail = 0;

void enqueue(event_t *e) {
    if ((queue_tail + 1) % MAX_QUEUE == queue_head) {
        printf("Queue overflow!\n");
        return;
    }
    event_queue[queue_tail] = e;
    queue_tail = (queue_tail + 1) % MAX_QUEUE;
}

event_t* dequeue() {
    if (queue_head == queue_tail) {
        return NULL;
    }
    event_t* e = event_queue[queue_head];
    queue_head = (queue_head + 1) % MAX_QUEUE;
    return e;
}

int main(int argc, char* argv[]) {
    printf("Starting Simulation (N_PROCC=%d, N_CORES=%d)...\n", N_PROCC, N_CORES);
    
    // Generate up to 100 events
    int events_to_generate = 100;
    int generated = generate_events(events_to_generate);
    
    printf("Generated %d events.\n", generated);
    
    event_t* e;
    printf("\nID\tTime\tState\tNode\tCore\tStatus\n");
    printf("--------------------------------------------------\n");
    while ((e = dequeue()) != NULL) {
        const char* state_name = "UNKNOWN";
        switch(e->curr_state) {
            case 0: state_name = "IDLE"; break;
            case 1: state_name = "D_C"; break;
            case 2: state_name = "D_D"; break;
            case 3: state_name = "D_E"; break;
        }
        printf("%d\t%.1f\t%s\t%d\t%d\t%d\n", 
               e->id, e->time, state_name, e->node, e->core, e->l_status);
        
        // Memory cleanup if using dynamic allocation
        // if (kdebug == 0) free(e);
    }
    
    printf("\nSimulation Complete.\n");
    return 0;
}
