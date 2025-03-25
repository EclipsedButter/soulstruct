from __future__ import annotations

__all__ = ["TexconvError", "TexconvConfig", "texconv", "texconv_to_dds", "batch_texconv_to_dds"]

import multiprocessing
import subprocess
import typing as tp
from pathlib import Path

from soulstruct.exceptions import SoulstructError
from soulstruct.utilities.files import PACKAGE_PATH


class TexconvError(SoulstructError):
    """Error raised by `texconv` subprocess."""
    pass


def texconv(*args):
    texconv_path = PACKAGE_PATH("base/textures/texconv")
    if not texconv_path.is_file():
        raise FileNotFoundError("Cannot find `texconv` executable that should be bundled with Soulstruct in 'base/textures'.")
    if str(args[-1])[0] in ('/','-'):
        args = args[:-1] + ('--',) + args[-1:]
    return subprocess.run(
        [texconv_path, *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return subprocess.run(
        ["wine", "cmd", "/C" f"\"{texconv_path} {' '.join(args)}\""],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

def texconv_path():
    return PACKAGE_PATH("base/textures/texconv")


class TexconvConfig(tp.NamedTuple):
    output_dir: str
    dds_format: str
    is_dx10: bool
    mipmap_count: int
    input_path: Path | str


def texconv_to_dds(config: TexconvConfig) -> bytes | None:
    """Run `texconv` on a single file, returning the output DDS data."""
    if "TYPELESS" in config.dds_format:
        # `texconv` does not support TYPELESS. Caller must resolve it first (probably to 'UNORM').
        raise TexconvError(
            f"DDS format '{config.dds_format}' is not supported by `texconv`. (Try UNORM instead of TYPELESS.)"
        )
    args = [
        "-o", config.output_dir, "-ft", "dds", "-f", config.dds_format,
        "-m", str(config.mipmap_count), "-nologo", str(config.input_path)
    ]
    if config.is_dx10:
        args.insert(4, "-dx10")  # use extended DX10 header
    texconv_result = texconv(*args)
    output_name = Path(config.input_path).with_suffix(".dds").name
    try:
        return Path(config.output_dir, output_name).read_bytes()
    except FileNotFoundError:
        print(f"Could not find converted DDS file. Stdout: {texconv_result.stdout.decode()}")
        return None


def batch_texconv_to_dds(configs: list[TexconvConfig]) -> list[bytes]:
    """Run `texconv` in parallel on multiple files, returning a dictionary of output DDS data.

    `output_dir` should be a temporary location that can be used to write the DDS files (which are immediately read).

    `dds_format`, `is_dx10`, `mipmap_count`, and `input_path` are all required in `dds_kwargs` for each key.
    """
    for config in configs:
        if "TYPELESS" in config.dds_format:
            # `texconv` does not support TYPELESS. Caller must resolve it first (probably to 'UNORM').
            raise TexconvError(
                f"DDS format '{config.dds_format}' is not supported by `texconv`. (Try UNORM instead of TYPELESS.)"
            )
    # out = []
    # configsLen = len(configs)
    # for i in range(configsLen):
    #     config = configs[i]
    #     print(f"Converting textures...    ({i+1}/{configsLen})           ",end='\r')
    #     out.append(texconv_to_dds(config))
    # print("\ndone")
    # return out

    # full_args = []
    # texconv_path = str(PACKAGE_PATH("base/textures/texconv.exe"))
    # print("converting textures...")
    # if not texconv_path.is_file():
    #     raise FileNotFoundError("Cannot find `texconv.exe` that should be bundled with Soulstruct in 'base/textures'.")
    # for config in configs:
    #     if "TYPELESS" in config.dds_format:
    #         # `texconv` does not support TYPELESS. Caller must resolve it first (probably to 'UNORM').
    #         raise TexconvError(
    #             f"DDS format '{config.dds_format}' is not supported by `texconv`. (Try UNORM instead of TYPELESS.)"
    #         )
        
    #     #! BUTTER use wine cmd to do convert sequentially
    #     args = [
    #         texconv_path, "-o", config.output_dir, "-ft", "dds", "-f", config.dds_format,
    #         "-m", str(config.mipmap_count), "-nologo", str(config.input_path)
    #     ]
    #     if config.is_dx10:
    #         args.insert(5, "-dx10")  # use extended DX10 header
    #     full_args += args + ["&&"]
    
    # full_args += ["rem"]
    # print(["wine", "cmd", "/C" f"\"{' '.join(full_args)}\""])
    # texconv_result = subprocess.run(
    #     ["wine", "cmd", "/C", f"\"{' '.join(args)}\""],
    #     stdout=subprocess.PIPE,
    #     stderr=subprocess.PIPE,
    # )

    # out = []
    # for config in configs:
    #     output_name = Path(config.input_path).with_suffix(".dds").name
    #     try:
    #         out.append(Path(config.output_dir, output_name).read_bytes())
    #     except FileNotFoundError:
    #         print(f"Could not find converted DDS file. Stdout: {texconv_result.stdout.decode()}")
    #         continue
    # return out

    # with multiprocessing.Pool() as pool:
    #     return list(pool.starmap(texconv_to_dds, configs))
    
    # use wine cmd to do convert sequentially
    
    
    out = []
    configsLen = len(configs)
    for i in range(configsLen):
        config = configs[i]
        print(f"Converting textures...    ({i+1}/{configsLen})           ",end='\r')
        out.append(texconv_to_dds(config))
    print("\ndone")
    return out
