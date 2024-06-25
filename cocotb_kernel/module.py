# type: ignore
import signal
import cocotb
from cocotb.handle import SimHandleBase
from typing import Any, Coroutine
from ipykernel.kernelapp import IPKernelApp
from IPython.core.interactiveshell import ExecutionResult

class CocotbKernelApp(IPKernelApp):
    # Patch init_signal because the kernel is ran in a separate thread
    def init_signal(self) -> None:
        pass

# Add ipykernel's coroutines to cocotb's event loop
def cocotb_loop_runner(coro: Coroutine[Any, Any, ExecutionResult]) -> ExecutionResult:
    @cocotb.function
    async def coro_wrapper() -> ExecutionResult:
        return await coro

    return coro_wrapper()

@cocotb.test()
async def kernel_entry(dut: SimHandleBase) -> None:
    app = CocotbKernelApp.instance(user_ns=dict(dut=dut))

    def interrupt_kernel(_signal: signal.Signals, _frame: Any) -> None:
        # ipykernel<=6 uses a dedicated interrupt handler, however in this context the 
        # kernel is ran within a thread, preventing signals from being passed to the kernel.
        #
        # TODO: This feature has been changed to a queue in a recent pull request
        # https://github.com/ipython/ipykernel/pull/1079
        # Update this to call sigint_handler() on the next major update to ipykernel
        raise NotImplementedError('cocotb_kernel doesn\'t support interrupting execution')
    signal.signal(signal.SIGINT, interrupt_kernel)

    # Run ipykernel in a separate thread
    @cocotb.external
    def start_kernel() -> None:
        app.initialize(cocotb.argv)
        app.shell.loop_runner = cocotb_loop_runner
        app.start()

    cocotb.log.info('starting ipykernel')
    await start_kernel()