import importlib.util
from pathlib import Path


def generate_launch_description():
    sim_gz_launch = Path(__file__).with_name('sim_gz.launch.py')
    spec = importlib.util.spec_from_file_location(
        'pb_option1_bringup_sim_gz_launch',
        sim_gz_launch,
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.generate_launch_description()
