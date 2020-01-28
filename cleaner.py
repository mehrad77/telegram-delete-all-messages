from time import sleep
from os import getenv

from pyrogram import Client
from pyrogram.api.functions.messages import Search
from pyrogram.api.types import InputPeerSelf, InputMessagesFilterEmpty
from pyrogram.api.types.messages import ChannelMessages
from pyrogram.errors import FloodWait, UnknownError


API_ID = 22543
API_HASH ='6501cd6ce521e6f2d6cb6c1d542d417c'

app = Client("client", api_id=API_ID, api_hash=API_HASH)
app.start()


class Cleaner:
    def __init__(self, peer=None, chat_id=None):
        self.peer = peer
        self.chat_id = chat_id
        self.message_ids = []
        self.add_offset = 0

    def select_supergroup(self):
        dialogs = app.get_dialogs()

        chats = [x for x in dialogs if x.chat.type == 'private']

        for i, chat in enumerate(chats):
            print(f'{i+1}. {chat.chat.first_name}')

        print('')

        chat_n = int(input('Insert chat number: '))
        selected_chat = chats[chat_n - 1]

        selected_chat_peer = app.resolve_peer(selected_chat.chat.id)
        self.peer = selected_chat_peer
        self.chat_id = selected_chat.chat.id

        print(f'Selected {selected_chat.chat.first_name}\n')

        return selected_chat, selected_chat_peer

    def run(self):
        q = self.search_messages()
        self.update_ids(q)
        messages_count = len(q.messages)
        print(f'Found {messages_count} your messages in selected chat')

        if messages_count < 100:
            pass
        else:
            self.add_offset = 100

            for i in range(0, messages_count, 100):
                q = self.search_messages()
                self.update_ids(q)
                self.add_offset += 100

        self.delete_messages()

    @staticmethod
    def chunks(l, n):
        """Yield successive n-sized chunks from l.
        https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks#answer-312464"""
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def update_ids(self, query: ChannelMessages):
        for msg in query.messages:
            self.message_ids.append(msg.id)

        return len(query.messages)

    def delete_messages(self):
        print(
            f'Deleting {len(self.message_ids)} messages with next message IDs:')
        print(self.message_ids)
        for message_ids_chunk in self.chunks(self.message_ids, 100):
            try:
                app.delete_messages(chat_id=self.chat_id,
                                    message_ids=message_ids_chunk)
            except FloodWait as flood_exception:
                sleep(flood_exception.x)

    def search_messages(self):
        print(f'Searching messages. OFFSET: {self.add_offset}')
        return app.send(
            Search(
                peer=self.peer,
                q='',
                filter=InputMessagesFilterEmpty(),
                min_date=0,
                max_date=0,
                offset_id=0,
                add_offset=self.add_offset,
                limit=100,
                max_id=0,
                min_id=0,
                hash=0,
                from_id=InputPeerSelf()
            )
        )


if __name__ == '__main__':
    try:
        deleter = Cleaner()
        deleter.select_supergroup()
        deleter.run()
    except UnknownError as e:
        print(f'UnknownError occured: {e}')
        print('Probably API has changed, ask developers to update this utility')
    finally:
        app.stop()
