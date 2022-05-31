import json
import os
import pandas as pd

data_path = 'fb_messages/inbox'
person_name = 'Jade Chongsathapornpong'
chat_name = person_name.lower().replace(" ", "")
print(chat_name)

def extract_messages(chatname, datapath):
    chatname.strip().lower()
    messages_json = os.path.join(datapath, [i for i in os.listdir(datapath) if chatname in i][0], "message_1.json")
    f = open(messages_json)
    chat = json.load(f)["messages"]

    extracted = []
    for m in chat:
        if m['sender_name'] == person_name and m['type'] == 'Generic' and not m['is_unsent'] \
                and 'photos' not in m.keys() and 'audio_files' not in m.keys() and 'videos' not in m.keys():
            if "Reacted" != m['content'][:7]:
                print(m["content"])
                message = m["content"].encode('latin1').decode('utf8')
                print(message)
                extracted.append(message)

    df = pd.DataFrame()
    df["content"] = extracted

    df.to_csv(f"{person_name}_messages.csv", index=None)


if __name__ == "__main__":
    extract_messages(chat_name, data_path)