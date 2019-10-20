import datetime
import time
from typing import Optional


class Timer(object):
    r"""
    A simple timer to record time per iteration and ETA of training. Using this
    is slightly faster than using ``tqdm`` during distributed training. Time
    taken and ETA are estimated in a moving average with a fixed window size.

    Parameters
    ----------
    window_size: int, optional (default = 1)
        Window size for calculating moving average time of past few iterations.
    total_iterations: int, optional (default = None)
        Total number of iterations. ETA will not be tracked (will remain "N?A")
        if this is not provided.
    resume_from: int, optional (default = 0)
        Iteration from which the training was started/resumed.
    """

    def __init__(
        self,
        window_size: int = 1,
        total_iterations: Optional[int] = None,
        resume_from: int = 0,
    ):
        self.total_iters = total_iterations
        self.current_iter = resume_from

        self._start_time = time.time()
        self._window_times = [0.0] * window_size

    def tic(self) -> None:
        r"""Start recording time: call at the beginning of iteration."""
        self._start_time = time.time()

    def toc(self) -> None:
        r"""Stop recording time: call at the end of iteration."""
        self._window_times.append(time.time() - self._start_time)
        self._window_times = self._window_times[1:]
        self.current_iter += 1

    @property
    def stats(self) -> str:
        r"""Return a single string with current iteration, avg time and ETA."""
        return f"Iter {self.current_iter} | Avg: {self.avg:.3f} sec | ETA: {self.eta_hhmmss}"

    @property
    def avg(self) -> float:
        r"""Return average time per iteration in seconds."""
        return sum(self._window_times) / len(self._window_times)

    @property
    def eta_hhmmss(self) -> str:
        r"""Return ETA in the form of HH:MM:SS string."""
        if self.total_iters:
            avg_time = sum(self._window_times) / len(self._window_times)
            _eta = avg_time * (self.total_iters - self.current_iter)
            # Convert seconds to HH:MM:SS
            return str(datetime.timedelta(seconds=_eta))
        else:
            return "N/A"

    @property
    def eta_sec(self) -> float:
        r"""Return ETA in the form of seconds."""
        if self.total_iters:
            avg_time = sum(self._window_times) / len(self._window_times)
            return avg_time * (self.total_iters - self.current_iter)
        else:
            return 0.0