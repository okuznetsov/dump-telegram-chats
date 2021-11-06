import asyncio
import json
import os
import sqlite3
import traceback
from datetime import datetime

import aiosqlite
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl import types
from telethon.tl.functions.users import GetFullUserRequest


def default(o):
    if isinstance(o, datetime):
        return o.isoformat()
    elif isinstance(o, bytes):
        return "<<BYTES>>"
    return o


class TelegramFactory:
    def __init__(self, api_id, api_hash, phone, password=None):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.password = password
        self._client = None

    async def __call__(self, session_name="session_name"):
        if self._client is None:
            client = TelegramClient(StringSession(), self.api_id, self.api_hash)
            await client.start(phone=self.phone, password=self.password)
            self._client = client

        return self._client


class TelegramMessageUseCase:
    def __init__(self, factory: TelegramFactory, db):
        self.factory = factory
        self.db = db
        self.fmt = "%Y-%m-%d %H:%M:%S"
        self._users = set()

    async def __call__(self, *args, **kwargs):
        tasks = []
        async for dialog in (await self.factory()).iter_dialogs():
            if isinstance(dialog.entity, types.Chat):
                tasks.append(self.worker(dialog))
        return await asyncio.gather(*tasks)

    async def worker(self, entity):
        while True:
            try:
                await self._worker(entity)
                return
            except (asyncio.CancelledError, KeyboardInterrupt):
                break
            except:
                print(traceback.format_exc())
                await asyncio.sleep(5)

    async def _worker(self, entity):
        iter_kwargs = {
            "entity": entity,
            "wait_time": 1,
            "reverse": True,
        }
        entity_id = str(abs(entity.id))
        cursor = await self.db.execute(
            "SELECT * FROM web_chat WHERE chat_type = 'chat' AND id = ?",
            [entity_id]
        )
        web_chat = await cursor.fetchone()
        await cursor.close()

        if not web_chat:
            # return
            print("New chat", entity.title)
            #     return
            await self.db.execute(
                """
                INSERT INTO web_chat (id, title, date, udate, disabled, chat_type)
                VALUES (?, ?, ?, ?, 0, "chat")
                """,
                [entity_id, entity.title, entity.date.strftime(self.fmt), datetime.now().strftime(self.fmt)]
            )
            web_chat = {
                "disabled": 0,
                "last_message_date": "",
                "migrated_id": None,
            }
        # else:
        #     print("Work with", entity.title)

        # if str(web_chat["id"]) != "518954405":
        # if str(web_chat["id"]) != "222084062":
        #     return

        if web_chat["disabled"] == 1:
            return

        if web_chat['last_message_date']:
            iter_kwargs["offset_date"] = datetime.strptime(web_chat['last_message_date'], self.fmt)

        telegram_client = await self.factory()

        if web_chat["migrated_id"]:
            try:
                iter_kwargs["entity"] = await telegram_client.get_entity(int(web_chat["migrated_id"]))
            except:
                print(entity.title, traceback.format_exc())

        counter = 0

        async for container in telegram_client.iter_messages(**iter_kwargs):
            if isinstance(container, types.MessageService):
                if isinstance(container.action, types.MessageActionChatMigrateTo):
                    query = "UPDATE web_chat SET migrated_id = ? WHERE id = ?"
                    params = [container.action.channel_id, entity_id]
                    await self.db.execute(query, params)
                    try:
                        iter_kwargs["entity"] = await telegram_client.get_entity(container.action.channel_id)
                    except:
                        print(entity.title, traceback.format_exc())
                    else:
                        async for message in telegram_client.iter_messages(**iter_kwargs):
                            if isinstance(message, types.MessageService):
                                continue
                            await self._handle_message(entity_id, message)
                            counter += 1
                    break
            else:
                await self._handle_message(entity_id, container)
            counter += 1

        print(entity.title, counter, entity_id)

    async def _handle_message(self, entity_id, message):
        if not message.from_id:
            return

        if isinstance(message.from_id, types.PeerChannel):
            return

        print(message.from_id)
        if message.from_id.user_id not in self._users:
            query = "INSERT OR IGNORE INTO web_user (id, name, username) VALUES (?, ?, ?)"
            params = [message.from_id.user_id, "?", "?"]
            await self.db.execute(query, params)
            self._users.add(message.from_id.user_id)

        query = """
                INSERT OR IGNORE INTO web_message (id, chat_id, text, user_id, date, original_response)
                VALUES (?, ?, ?, ?, ?, ?)
            """
        params = [
            str(entity_id) + "_" + str(message.id),
            entity_id,
            message.message,
            message.from_id.user_id,
            message.date.strftime(self.fmt),
            json.dumps(
                message.to_dict(),
                ensure_ascii=False,
                indent=4,
                default=default,
            ),
        ]
        await self.db.execute(query, params)
        query = "UPDATE web_chat SET last_message_date = ? WHERE id = ?"
        params = [message.date.strftime(self.fmt), entity_id]
        await self.db.execute(query, params)


class TelegramUserUseCase:
    def __init__(self, factory, db):
        self.factory = factory
        self.db = db

    async def __call__(self, *args, **kwargs):
        telegram_client = await self.factory()
        cursor = await self.db.execute("SELECT * FROM web_user")
        for user in await cursor.fetchall():
            if user['username'] != '?' or user['name'] != '?':
                continue

            try:
                full_user_info = await telegram_client(GetFullUserRequest(types.User(id=user['id'])))
            except:
                continue

            user_data = full_user_info.user
            name = " ".join(list(filter(None, [user_data.first_name, user_data.last_name])))
            await self.db.execute(
                "UPDATE web_user SET name = ?, username = ? WHERE id = ?",
                [name, user_data.username, user["id"]]
            )


async def main():
    path = "./db.sqlite3"

    async with aiosqlite.connect(path, isolation_level=None) as connection:
        connection.row_factory = sqlite3.Row

        factory = TelegramFactory(
            api_id=os.environ.get("API_ID"),
            api_hash=os.environ.get("API_HASH"),
            phone=os.environ.get("CLIENT_PHONE"),
            password=os.environ.get("CLIENT_PASSWORD"),
        )
        await factory()

        await TelegramMessageUseCase(
            factory,
            db=connection
        )()


asyncio.run(main())
