import discord
import asyncio
import sys
import pathlib

async def connect_stdin_stdout():
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    dummy = asyncio.Protocol()
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)
    w_transport, _ = await loop.connect_write_pipe(lambda: dummy, sys.stdout)
    writer = asyncio.StreamWriter(w_transport, protocol, reader, loop)
    return reader, writer

async def start_discord():
    tokenfile = open(pathlib.Path(__file__).parent.parent.absolute() / "token.txt", "r")
    token = tokenfile.readline()
    tokenfile.close()
    await client.start(token)

async def main_called_loop(client):
    print("Accepting Input")
    reader, writer = await connect_stdin_stdout()
    while True:
        line = await reader.readline()
        command = line.decode("utf-8").split("\t")[0]
        if command == "create":
            for guild in client.guilds:
                for c in guild.categories:
                    if c.name == "Among Us":
                        await c.create_voice_channel(line.decode("utf-8").split("create\t")[1])
        elif command == "delete":
            for guild in client.guilds:
                for c in guild.categories:
                    if c.name == "Among Us":
                        for channel in c.voice_channels:
                            if channel.name.strip() == line.decode("utf-8").split("delete\t")[1].strip():
                                await channel.delete(reason="Game End")
        print(line.decode("utf-8"))

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

client = MyClient()

try:
    client.loop.create_task(start_discord())
    client.loop.run_until_complete(main_called_loop(client))
except KeyboardInterrupt:
    client.loop.run_until_complete(client.logout())
# cancel all tasks lingering
finally:
    client.loop.close()