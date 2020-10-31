from lsp_utils import NpmClientHandler


@classmethod
def install_in_cache(cls) -> bool:
    return False


# make LSP servers installed to "Package Storage" by default
NpmClientHandler.install_in_cache = install_in_cache
