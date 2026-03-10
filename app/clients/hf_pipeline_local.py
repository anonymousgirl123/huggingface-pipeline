"""Legacy module kept for compatibility with earlier imports.

Originally the project used a different client name, HFPipelineLocalClient.
The implementation was later consolidated into ``hf_local.py`` and renamed to
``HFLocalClient``.  This stub re-exports the class so downstream code can
continue to import ``HFPipelineLocalClient``.
"""

from .hf_local import HFLocalClient as HFPipelineLocalClient

__all__ = ["HFPipelineLocalClient"]
