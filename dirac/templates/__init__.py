import os

base_dir = os.path.dirname(__file__)

with open(os.path.join(base_dir, 'run_gaudi_app.sh')) as f:
    run_gaudi_app = f.read()

with open(os.path.join(base_dir, 'add_gaudi_input_data.py')) as f:
    add_gaudi_input_data = f.read()

__all__ = [
    run_gaudi_app,
    add_gaudi_input_data
]
