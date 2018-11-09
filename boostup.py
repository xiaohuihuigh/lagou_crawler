# coding=utf8
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count


def boost_up(func, tasks, core=None, method='Process'):
    if method == 'Process':
        from multiprocessing import Pool
    else:
        from multiprocessing.dummy import Pool
    pool = Pool(core)

    # executor = ProcessPoolExecutor(core)
    # result = executor.map(func, tasks)
    #
    #
    # jobs = [Process(target=func, args=task) for task in tasks]
    # map(lambda j: j.start(), jobs)
    # map(lambda j: j.join(), jobs)

    holder = pool.map(func, tasks)
    pool.close()
    pool.join()

    return holder


class SpeedUp(object):
    def __init__(self, core=None):
        self.execute = ProcessPoolExecutor(core)

    def __del__(self):
        self.execute.shutdown()

    def __call__(self, func):
        def args_wrapper(tasks):
            return self.execute.map(func, tasks)

        return args_wrapper


def run_in_process(core=None):
    core = cpu_count if core is None else core

    def _run_in_process(f):
        def __run_in_process(*args, **kwargs):
            _processes = []
            for i in range(core):
                p = multiprocessing.Process(target=f, args=args, kwargs=kwargs)
                p.start()
                _processes.append(p)

            for p in _processes:
                p.join()

        return __run_in_process

    return _run_in_process


if __name__ == '__main__':
    # print(linux.__code__.co_code
    # print(list(linux(range(4))))
    import pandas  as pd

    d = pd.DataFrame([[1,3], [21,4], [3,6]], columns=['1','2'])
    print(d.nlargest(axis=1))
    pass
