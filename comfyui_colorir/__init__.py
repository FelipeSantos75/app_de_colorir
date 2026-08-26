# -*- coding: utf-8 -*-
"""Nos do ComfyUI para o gerador de paginas de colorir.

Instale ligando esta pasta em custom_nodes do ComfyUI (junction no Windows):

    mklink /J "<ComfyUI>\\custom_nodes\\comfyui_colorir" "C:\\projetos\\app_de_colorir\\comfyui_colorir"

Assim o pacote continua versionado junto com o projeto.
"""

from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
