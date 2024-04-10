from .base import *
from .beta_vae import *
from .betatc_vae import *
from .cat_vae import *
from .cvae import *
from .dfcvae import *
from .dip_vae import *
from .fvae import *
from .gamma_vae import *
from .hvae import *
from .info_vae import *
from .iwae import *
from .joint_vae import *
from .logcosh_vae import *
# from .twostage_vae import *
from .lvae import LVAE
from .miwae import *
from .mssim_vae import MSSIMVAE
from .swae import *
from .vampvae import *
from .vanilla_vae import *
from .vq_vae import *
from .wae_mmd import *


# Aliases
VAE = VanillaVAE
GaussianVAE = VanillaVAE
CVAE = ConditionalVAE
GumbelVAE = CategoricalVAE

vae_models = {'HVAE': HVAE,
              'LVAE': LVAE,
              'IWAE': IWAE,
              'SWAE': SWAE,
              'MIWAE': MIWAE,
              'VQVAE': VQVAE,
              'DFCVAE': DFCVAE,
              'DIPVAE': DIPVAE,
              'BetaVAE': BetaVAE,
              'InfoVAE': InfoVAE,
              'WAE_MMD': WAE_MMD,
              'VampVAE': VampVAE,
              'GammaVAE': GammaVAE,
              'MSSIMVAE': MSSIMVAE,
              'JointVAE': JointVAE,
              'BetaTCVAE': BetaTCVAE,
              'FactorVAE': FactorVAE,
              'LogCoshVAE': LogCoshVAE,
              'VanillaVAE': VanillaVAE,
              'ConditionalVAE': ConditionalVAE,
              'CategoricalVAE': CategoricalVAE}
