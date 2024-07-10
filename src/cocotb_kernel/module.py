# TODO: Remove 'type: ignore' once cocotb v1.9 releases, which contains type stubs
# TODO: Create type stubs for CocotbKernelApp
import os
import signal
from types import FrameType
from typing import Any, Coroutine

import cocotb  # type: ignore
from cocotb.handle import SimHandleBase  # type: ignore
from ipykernel.kernelapp import IPKernelApp
from IPython.core.interactiveshell import ExecutionResult


class CocotbKernelApp(IPKernelApp):
    # Patch init_signal because the kernel is ran in a separate thread
    def init_signal(self) -> None:
        pass


# Add ipykernel's coroutines to cocotb's event loop
def cocotb_loop_runner(coro: Coroutine[Any, Any, ExecutionResult]) -> ExecutionResult:
    @cocotb.function  # type: ignore
    async def coro_wrapper() -> ExecutionResult:
        return await coro

    return coro_wrapper()  # type: ignore


@cocotb.test()  # type: ignore
async def kernel_entry(dut: SimHandleBase) -> None:
    connection_file = os.environ["COCOTB_CONNECTION_FILE"]

    app = CocotbKernelApp.instance(user_ns=dict(dut=dut))

    def interrupt_kernel(_signal: int, _frame: FrameType | None) -> None:
        # ipykernel<=6 uses a dedicated interrupt handler, however in this context the
        # kernel is ran within a thread, preventing signals from being passed to the kernel.
        #
        # TODO: ipykernel interrupts have been changed to use a queue in a recent pull request
        # https://github.com/ipython/ipykernel/pull/1079
        # Update this to call sigint_handler() on the next major update to ipykernel
        raise NotImplementedError("cocotb_kernel doesn't support interrupting execution")

    signal.signal(signal.SIGINT, interrupt_kernel)

    # Run ipykernel in a separate thread
    @cocotb.external  # type: ignore
    def start_kernel() -> None:
        app.initialize(["-f", connection_file])  # type: ignore
        app.shell.loop_runner = cocotb_loop_runner  # type: ignore
        app.start()  # type: ignore

    cocotb.log.info("starting ipykernel")
    await start_kernel()
