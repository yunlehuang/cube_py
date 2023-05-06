#%%
import pandas as pd
import json
import datetime

#%%
def hello():
    print('hello world')

def get_master(sheet_id, gid):
    '''
    sheet id is the id after d/ and before /edit
    returns a df
    '''
    import pandas as pd

    url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}'
    df = pd.read_csv(url)
    return df

def url_encode_spaces(url):
    from urllib.parse import quote
    return quote(url, safe=":/?#[]@!$&'()*+,;=%")

def check_null(df, col):
    new_df = df.copy()
    new_df['is_null'] = new_df[col].isnull()
    return_df = new_df.loc[new_df['is_null'] == True]
    return return_df

def check_image(df, col):
    new_df = df.copy()
    def is_image(link):
        return link.endswith('.jpg') or link.endswith('.png') or link.endswith('.jpeg')
    new_df['is_image'] = new_df[col].apply(is_image)
    return_df = new_df.loc[new_df['is_image'] == False]
    return return_df

def parse_sheet(type):
    if type == 'cube':
        sheet_id = '1e126rklurwrdjOKVxNV6DjIMTTkfNJ94niuSxmcYObM'
        gid = '388804950'

        raw = get_master(sheet_id, gid)        
        df = raw[['card_title','ready_to_publish','card_url','back_url','script_cascade_helper']].copy()
        df = df.loc[df['ready_to_publish'] == True]
        df['tts_name'] = df.apply(lambda r: r['card_title'] + '\n' + r['script_cascade_helper'], axis=1)
        df = df.reset_index(drop=True)
        return df
    if type == 'tokens':
        sheet_id = '1e126rklurwrdjOKVxNV6DjIMTTkfNJ94niuSxmcYObM'
        gid = '990091517'

        raw = get_master(sheet_id, gid)
        df = raw[['card_title','card_url','script_cascade_helper']].copy()
        df['tts_name'] = df.apply(lambda r: r['card_title'] + '\n' + r['script_cascade_helper'], axis=1)
        df = df.reset_index(drop=True)
        return df
    if type == 'lands':
        sheet_id = '1e126rklurwrdjOKVxNV6DjIMTTkfNJ94niuSxmcYObM'
        gid = '2139880948'

        raw = get_master(sheet_id, gid)
        df = raw[['card_title','card_url','script_cascade_helper']].copy()
        df['tts_name'] = df.apply(lambda r: r['card_title'] + '\n' + r['script_cascade_helper'], axis=1)
        df = df.reset_index(drop=True)
        return df

def add_card_columns(df):
    new_df = df.copy()
    new_df['CardID'] = (new_df.index + 1) * 100
    new_df['card_number'] = new_df.index + 1
    new_df['card_number'] = new_df['card_number'].astype(str)
    return new_df

def std_transform():
    return {
        "posX": 0,
        "posY": 0,
        "posZ": 0,
        "rotX": 0,
        "rotY": 180,
        "rotZ": 180,
        "scaleX": 1,
        "scaleY": 1,
        "scaleZ": 1
    }

def contained_object(df, type, back_url):
    ContainedObjects = []
    if type == 'cube':
        for i, row in df.iterrows():
            if pd.isna(row['back_url']):
                card = {
                    'CardID': row['CardID'],
                    'Name': 'Card',
                    "Nickname": row['tts_name'],
                    "Transform": std_transform()
                }
                ContainedObjects.append(card)
            else:
                CustomDeck_front = {}
                CustomDeck_front[row['card_number']] = {
                    'FaceURL': row['card_url'],
                    'BackURL': back_url,
                    'NumHeight': 1,
                    'NumWidth': 1,
                    "BackIsHidden": True,
                    "UniqueBack": False,
                    "Type": 0
                }
                CustomDeck_back = {}
                CustomDeck_back[row['card_number']] = {
                    'FaceURL': row['back_url'],
                    'BackURL': back_url,
                    'NumHeight': 1,
                    'NumWidth': 1,
                    "BackIsHidden": True,
                    "UniqueBack": False,
                    "Type": 0
                }
                card = {
                    'CardID': row['CardID'],
                    'Name': 'Card',
                    "Nickname": row['tts_name'],
                    "Transform": std_transform(),
                    "CustomDeck": CustomDeck_front,
                    "States": {
                        "2": {
                            "Name": "Card",
                            "Transform": std_transform(),
                            "Nickname": row['tts_name'],
                            "CardID": row['CardID'],
                            "CustomDeck": CustomDeck_back
                        }
                    }
                }
                ContainedObjects.append(card)
    return ContainedObjects

def custom_deck(df, back_url):
    CustomDeck = {}
    for i, row in df.iterrows():
        CustomDeck[row['card_number']] = {
            'FaceURL': row['card_url'],
            'BackURL': back_url,
            'NumHeight': 1,
            'NumWidth': 1,
            'BackIsHidden': True
        }
    return CustomDeck