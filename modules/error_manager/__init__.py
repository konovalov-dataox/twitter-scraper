from core.module import AcceleratorModule

module = AcceleratorModule.declare_module(
    name='error_manager',
    requirements=['sqlalchemy', 'pymysql', 'redis']
)

if module:
    from .error_manager import AsyncErrorManager

    module.module_class = AsyncErrorManager
