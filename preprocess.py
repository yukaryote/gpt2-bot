import json
import os
import pandas as pd
from sklearn.model_selection import train_test_split


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
                message = m["content"].encode('latin1').decode('utf8')
                extracted.append(message)

    df = pd.DataFrame()
    df["content"] = extracted

    csv_path = f"{person_name}_messages.csv"
    df.to_csv(csv_path, index=False)

    train_test_ratio = 0.9
    train_valid_ratio = 7 / 9
    df_full_train, df_test = train_test_split(df, train_size=train_test_ratio, random_state=1)
    df_train, df_val = train_test_split(df_full_train, train_size=train_valid_ratio, random_state=1)

    if "train_test_splits" not in os.listdir(os.curdir):
        os.makedirs("train_test_splits")
    train_test_folder = "train_test_splits"
    splits = {"train": df_train, "val": df_val, "test": df_test}
    for split_file in splits:
        train_test_path = os.path.join(train_test_folder, split_file + ".txt")
        f = open(train_test_path, 'w')
        data = ''
        posts = splits[split_file]['content'].tolist()
        for post in posts:
            post = str(post).strip()
            bos_token = '<BOS>'
            eos_token = '<EOS>'
            data += bos_token + ' ' + post + ' ' + eos_token + '\n'
            print(data)

        try:
            f.write(data)
        except UnicodeEncodeError:
            continue


if __name__ == "__main__":
    extract_messages(chat_name, data_path)
