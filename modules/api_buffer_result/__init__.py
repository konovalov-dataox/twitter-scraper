from core.module import AcceleratorModule

module = AcceleratorModule.declare_module(
    name='api_buffer_result',
    requirements=['redis', ]
)

if module:
    from .api_buffer_result import AsyncApiBufferResult

    module.module_class = AsyncApiBufferResult
