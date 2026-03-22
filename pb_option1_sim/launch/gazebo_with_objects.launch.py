import importlib.util
from pathlib import Path


def generate_launch_description():
    gz_launch = Path(__file__).with_name('gz_sim_with_objects.launch.py')
    spec = importlib.util.spec_from_file_location(
        'pb_option1_sim_gz_launch',
        gz_launch,
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.generate_launch_description()
