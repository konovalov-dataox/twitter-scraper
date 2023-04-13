from core.module import AcceleratorModule

module = AcceleratorModule.declare_module(
    name='fetcher',
    requirements=['httpx']
)

if module:
    from .fetcher import AsyncFetcher

    module.module_class = AsyncFetcher
