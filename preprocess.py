import json
import os
import pandas as pd
from sklearn.model_selection import train_test_split
import codecs
import argparse


def extract_messages(chatname, datapath, person_name):
    chatname.strip().lower()
    messages_json = os.path.join(datapath, [i for i in os.listdir(datapath) if chatname in i][0], "message_1.json")
    f = codecs.open(messages_json)
    chat = json.load(f)["messages"]

    extracted = []
    for m in chat:
        if (person_name is not None and m['sender_name'] == person_name or person_name is None) and \
                m['type'] == 'Generic' and not m['is_unsent'] \
                and 'photos' not in m.keys() and 'audio_files' not in m.keys() and 'videos' not in m.keys():
            if "Reacted" != m['content'][:7]:
                message = m["content"].encode('latin1').decode('utf-8')
                extracted.append(message)

    df = pd.DataFrame()
    df["content"] = extracted

    csv_path = f"{chatname}_messages.csv"
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
        data = []
        posts = splits[split_file]['content'].tolist()
        for post in posts:
            post = str(post).strip()
            bos_token = '<BOS>'
            eos_token = '<EOS>'
            data.append(bos_token + ' ' + post + ' ' + eos_token)
        for line in data:
            try:
                f.write(line)
                f.write("\n")
            except UnicodeEncodeError:
                continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--chat_name",
                        default="jadechongsathapornpong",
                        help="all lowercase, no spaces version of messenger chat name")
    parser.add_argument("--name",
                        default=None,
                        help="Set --name to a person's name (first last, capitalized correctly) if you want to "
                             "impersonate that person. Otherwise, set it to None (default) if you want to \"average\" "
                             "all the people in the chat into one bot.")
    parser.add_argument("--messages_path",
                        default="fb_messages/inbox",
                        help="path to the inbox directory of your downloaded FB Messenger chats")
    args = parser.parse_args()
    extract_messages(args.chat_name, args.messages_path, args.name)
