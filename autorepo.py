import os
import asyncio
from io import BytesIO
from random import choice
from hashlib import sha256
from datetime import datetime

import orjson
import uvloop
import aiohttp
import aiofiles
import pyrogram.types as ptypes
from pyrogram import Client, filters

import env
import tbhutils
from filelock import FileLock

API: str = "https://upload.starfiles.co/chunk"
CSIZE: int = 2097152
CHARS: str = "qwertyuiopasdfghjklzxcvbnm1234567890"
upload_lock: asyncio.Lock = asyncio.Lock()

uvloop.install()
app: Client = Client(
    "autorepo", env.TELE_API_ID, env.TELE_API_HASH,
    bot_token=env.TELE_BOT_TOKEN)


@app.on_message(  # type: ignore
        filters.document & (filters.channel | filters.private))
async def new_doc(client: Client, msg: ptypes.Message) -> None:
    if msg.chat.username not in env.CHANNEL_USERNAMES:
        return
    elif not msg.document.file_name.endswith(".ipa"):
        return

    async with upload_lock:
        async with aiofiles.tempfile.TemporaryDirectory() as tmpdir:
            print("downloading")
            path: str = await msg.download(f"{tmpdir}/")
            app_info: dict[str, str] = tbhutils.get_info(path)

            # icon shit
            thumbs = msg.document.thumbs
            ipath = await client.download_media(
                thumbs[0].file_id, f"{tmpdir}/")

            print("uploading")
            file_id: str = await starfiles_upload(
                path, (size := msg.document.file_size))
            icon_id: str = await starfiles_upload(
                ipath, thumbs[0].file_size)  # type: ignore

        # get existing repo data
        with FileLock("serve/repo.json") as f:
            data = orjson.loads(f.read())

        # get caption, read ipa info, add to apps
        data["apps"].insert(0, {
            "name": msg.document.file_name.split("-")[0],
            "bundleIdentifier": app_info["b"],
            "version": app_info["v"],
            "versionDate": datetime.now().strftime("%Y-%m-%d"),
            "size": size,
            "downloadURL": f"https://download.starfiles.co/{file_id}",
            "localizedDescription": msg.caption,
            "iconURL": f"https://download.starfiles.co/{icon_id}",
            "developerName": "hi"
        })
        print(f"added data -- file {file_id}, icon {icon_id}")

        with FileLock("serve/repo.json") as f:
            f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2).decode())
            print("wrote data")


async def starfiles_upload(path: str, size: int) -> str:
    TOTAL_CHUNKS: int = (size + 2097151) // 2097152
    results: list = [None] * TOTAL_CHUNKS

    for cnum in range(TOTAL_CHUNKS):
        await upload_chunk(cnum, TOTAL_CHUNKS, results, path)

    files: str = ",".join(results)
    file_id: str = "".join(choice(CHARS) for _ in range(12))

    async with aiohttp.ClientSession() as sess:
        async with sess.post(API,
                data={"compile_file": files, "file_id": file_id,
                "name": os.path.basename(path)}) as req:
            await req.read()

    return file_id


async def upload_chunk(
    cnum: int, total: int, results: list, file: str
) -> None:
    async with aiofiles.open(file, "rb") as opened:
        await opened.seek(cnum * CSIZE)
        chunk = await opened.read(CSIZE)
    
    h1 = sha256()
    h1.update(chunk)
    aux: str = h1.hexdigest()

    async with aiohttp.ClientSession() as session:
        data: aiohttp.FormData = aiohttp.FormData()
        data.add_field("upload", BytesIO(chunk))
        data.add_field("chunk_hash", aux)

        async with session.post(API, data=data) as actual:
            await actual.read()
            results[cnum] = aux


if __name__ == "__main__":
    app.run()
