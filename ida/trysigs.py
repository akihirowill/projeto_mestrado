from idautils import *
from idaapi import *
from idc import *
import traceback
import time
import os


log_dir = '/home/william/ida_logs'


class State:
    snapshot = None
    initial_funcs = None
    sigs = None
    curr_sig = 0
    start_ts = 0


def log_file():
    return os.path.join(log_dir, get_root_filename() + '.log')


def initial_state():
    state = State()

    state.start_ts = time.time()

    state.snapshot = ida_loader.snapshot_t()
    state.snapshot.desc = "Initial SnapShot Without Signatures"
    ida_kernwin.take_database_snapshot(state.snapshot)

    state.initial_funcs = set()
    for segea in Segments():
        for funcea in Functions(segea, SegEnd(segea)):
            state.initial_funcs.add(GetFunctionName(funcea))

    return state


def apply_next_sig(err, state):
    if state.curr_sig >= len(state.sigs):
        return finished(state)

    curr_sig_name = state.sigs[state.curr_sig]
    print '\n\n==>', curr_sig_name

    res = plan_to_apply_idasgn(curr_sig_name)
    assert res != 0

    auto_wait()

    with open(log_file(), 'a') as f:
        # please remove {autoload.cfg, armsigl.sig}, otherwise the assertion can fail
        assert ida_funcs.get_idasgn_qty() == 1
        sig_name, unused, hits = ida_funcs.get_idasgn_desc_with_matches(0)
        assert sig_name == curr_sig_name
        assert ida_funcs.calc_idasgn_state(0) == ida_funcs.IDASGN_APPLIED
        f.write('\n\n==> %s\t%d\n' % (sig_name, hits))

        for segea in Segments():
            for funcea in Functions(segea, SegEnd(segea)):
                function_name = GetFunctionName(funcea)
                is_new = int(function_name not in state.initial_funcs)
                is_lib = int((get_func(funcea).flags & 4) != 0)
                f.write('0x%x\t%s\t%d\t%d\n' % (funcea, function_name, is_new, is_lib))

    state.curr_sig += 1
    ida_kernwin.restore_database_snapshot(state.snapshot, apply_next_sig, state)


def finished(state):
    with open(log_file(), 'a') as f:
        f.write('\n\n*** time spent applying sigs: %.3f seconds\n' % (time.time() - state.start_ts))
    print "all done"
    Exit(0)


def main():
    # avoid script from running twice when restoring initial snapshot
    if hasattr(ida_kernwin, '_trysigs_running'):
        return
    ida_kernwin._trysigs_running = True

    ti = time.time()
    auto_wait()
    tf = time.time()

    with open(log_file(), 'a') as f:
        f.write('\n\n*** time spent with the initial analysis: %.3f seconds\n' % (tf - ti))


    state = initial_state()

    # never let the GC collect our state
    ida_kernwin._trysigs_anchor = state

    with open(ARGV[1]) as f:
        state.sigs = [line.strip() for line in f]

    apply_next_sig(None, state)


if __name__ == '__main__':
    try:
        main()
    except:
        traceback.print_exc()
        Exit(0)   # comment this line for debugging
