#ifndef EVENTS_H
#define EVENTS_H

#define N_PROCC 4
#define N_CORES 2

typedef struct {
    int id;
    double time;
    int node;
    int core;
    int prev_state;
    int curr_state;
    int l_status;
} event_t;

/* Global state variables */
extern int kdebug;
extern int event_idx;
extern event_t d_events[10000];
extern int d_status[N_PROCC];
extern int d_l_status[N_PROCC][N_CORES];
extern int d_count[N_PROCC];

/* Function declarations */
int generate_events(int num_events_limit);
void enqueue(event_t *e);

#endif /* EVENTS_H */
