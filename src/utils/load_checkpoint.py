# PyTorch StudioGAN: https://github.com/POSTECH-CVLab/PyTorch-StudioGAN
# The MIT License (MIT)
# See license file or visit https://github.com/POSTECH-CVLab/PyTorch-StudioGAN for details

# utils/load_checkpoint.py


import os

import torch
import torch.nn as nn
import torch.nn.utils.prune as prune

def pruning_generate(model, state_dict):

    parameters_to_prune =[]
    for (name, m) in model.named_modules():
        if isinstance(m, nn.Conv2d) or isinstance(m, nn.ConvTranspose2d):
            m = prune.custom_from_mask(m, name = 'weight', mask = state_dict[name + ".weight_mask"])


def load_checkpoint(model, optimizer, filename, metric=False, ema=False):
    # Note: Input model & optimizer should be pre-defined.  This routine only updates their states.
    start_step = 0
    if ema:
        checkpoint = torch.load(filename)
        pruning_generate(model, checkpoint['state_dict'])
        model.load_state_dict(checkpoint['state_dict'])
        return model
    else:
        checkpoint = torch.load(filename)
        seed = checkpoint['seed']
        run_name = checkpoint['run_name']
        start_step = checkpoint['step']
        pruning_generate(model, checkpoint['state_dict'])
        model.load_state_dict(checkpoint['state_dict'])
        optimizer.load_state_dict(checkpoint['optimizer'])
        ada_p = checkpoint['ada_p']
        for state in optimizer.state.values():
            for k, v in state.items():
                if isinstance(v, torch.Tensor):
                    state[k] = v.cuda()

        if metric:
            best_step = checkpoint['best_step']
            best_fid = checkpoint['best_fid']
            best_fid_checkpoint_path = checkpoint['best_fid_checkpoint_path']
            return model, optimizer, seed, run_name, start_step, ada_p, best_step, best_fid, best_fid_checkpoint_path
    return model, optimizer, seed, run_name, start_step, ada_p
