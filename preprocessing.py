# Step 2 - preprocess
import json
import nltk
import re
from nltk.tokenize import word_tokenize
import os

def read_file(path):
    f = open(path, "r")
    prod = json.load(f)
    return prod

f = read_file("Corpus/Headphones/0feecb11-2ff1-49c0-9e89-ff661109b710.json")
print(str(f))

def tokenize(f):
    fstr = str(f)
    final = re.sub(r'[\[\]\{\}\(\)]', '\n', fstr)
    final = re.sub(r'[\'\"]', '', final)
    final = re.sub(r"\\u[a-fA-F0-9]{4}", " ", final)
    final = re.sub(r":", " ", final)
    final = re.sub(r",", " ", final)
    
    words = word_tokenize(final)
    print(words)
    rm_stop = []
    for w in words:
        if w not in nltk.corpus.stopwords.words('english'):
            rm_stop.append(w)

    return rm_stop

total = 0
for fold in ["Headphones", "Soundbars", "Speakers"]:
    fold_count = 0
    for fn in os.listdir(os.path.join("./Corpus/", fold))[:20]:
        file_path = os.path.join("./Corpus/", fold, fn)
        d =  read_file(file_path)
        # del d[fn.strip(".json")]["features"]
        del d[fn.strip(".json")]["about_us"]
        del d[fn.strip(".json")]["emi"]

        features = []
        for feat,v in d[fn.strip(".json")]["features"].items():
            if feat == "All features":
                continue
            features.append(feat)
        d[fn.strip(".json")]["features"] = features[:2]
        spec = []
        try:
            for sp,v in d[fn.strip(".json")]["specification"].items():
                spec.extend(v)
            d[fn.strip(".json")]["specification"] = spec
        except:
            continue
        write_path = os.path.join("./Final_Corpus/", fold, fn)
        with open(write_path, 'w') as f:
            json.dump(d, f, ensure_ascii=False, indent=4)
        tokens = tokenize(d)
        tokens = [t for t in tokens]
        fold_count += len(tokens)
        print()
    
    total+= fold_count
    print(fold, ": ", fold_count)
print(total)
