import plistlib
from zipfile import ZipFile


def get_info(path: str) -> dict[str, str]:
    with ZipFile(path) as zf:
        for name in zf.namelist():
            if name.endswith(".app/Info.plist"):
                pl_name: str = name
                break
        
        with zf.open(pl_name) as pl:
            plist = plistlib.load(pl)

    return {
        "n": try_plist(plist, "CFBundleDisplayName", "CFBundleName"),
        "v": try_plist(
            plist, "CFBundleShortVersionString", "CFBundleVersion"),
        "b": plist["CFBundleIdentifier"]
    }


def try_plist(plist: dict[str, str], n1: str, n2: str) -> str:
    try:
        return plist[n1]
    except KeyError:
        return plist[n2]
