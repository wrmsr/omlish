import argparse
import os
from pathlib import Path

import yaml
from pytorch_lightning import Trainer
from pytorch_lightning.callbacks import LearningRateMonitor, ModelCheckpoint
from pytorch_lightning.loggers import TensorBoardLogger

from dataset import VAEDataset
# from models import *


if __name__ == '__main__':
    os.chdir(os.path.dirname(__file__))

    parser = argparse.ArgumentParser(description='Generic runner for VAE models')
    parser.add_argument(
        '--config',
        '-c',
        dest="filename",
        metavar='FILE',
        help='path to the config file',
        default='configs/vae.yaml',
    )

    args = parser.parse_args()
    with open(args.filename, 'r') as file:
        try:
            config = yaml.safe_load(file)
        except yaml.YAMLError as exc:
            print(exc)

    data = VAEDataset(
        **config["data_params"],
        pin_memory=len(config['trainer_params']['gpus']) != 0,
    )
    data.setup()

    tb_logger = TensorBoardLogger(
        save_dir=config['logging_params']['save_dir'],
        name=config['model_params']['name'],
    )

    # For reproducibility
    # from pytorch_lightning.utilities.seed import seed_everything
    # seed_everything(config['exp_params']['manual_seed'], True)

    from experiment import VAEXperiment
    from models import vae_models
    model = vae_models[config['model_params']['name']](**config['model_params'])
    experiment = VAEXperiment(model, config['exp_params'])

    from pytorch_lightning.strategies import DDPStrategy  # noqa
    runner = Trainer(
        logger=tb_logger,
        callbacks=[
            LearningRateMonitor(),
            ModelCheckpoint(
                save_top_k=2,
                dirpath=os.path.join(tb_logger.log_dir, "checkpoints"),
                monitor="val_loss",
                save_last=True,
            ),
        ],
        # strategy=DDPStrategy(
        #     accelerator='cpu',
        #     find_unused_parameters=False,
        # ),
        **{k: v for k, v in config['trainer_params'].items() if k not in {'gpus'}},
    )

    Path(f"{tb_logger.log_dir}/Samples").mkdir(exist_ok=True, parents=True)
    Path(f"{tb_logger.log_dir}/Reconstructions").mkdir(exist_ok=True, parents=True)

    print(f"======= Training {config['model_params']['name']} =======")
    runner.fit(experiment, datamodule=data)
