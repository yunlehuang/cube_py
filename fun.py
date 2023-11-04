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
        df = raw[['card_title','card_url','back_url','script_cascade_helper']].copy()
        df['tts_name'] = df.apply(lambda r: r['card_title'] + '\n' + r['script_cascade_helper'], axis=1)
        df = df.reset_index(drop=True)
        return df
    if type == 'lands':
        sheet_id = '1e126rklurwrdjOKVxNV6DjIMTTkfNJ94niuSxmcYObM'
        gid = '2139880948'

        raw = get_master(sheet_id, gid)
        df = raw[['card_title','card_url','back_url','script_cascade_helper']].copy()
        df['tts_name'] = df.apply(lambda r: r['card_title'] + '\n' + r['script_cascade_helper'], axis=1)
        df = df.reset_index(drop=True)
        return df
    if type == 'packs':
        sheet_id = '1e126rklurwrdjOKVxNV6DjIMTTkfNJ94niuSxmcYObM'
        gid = '388804950'

        raw = get_master(sheet_id, gid)        
        df = raw[['card_title','ready_to_publish','card_url','back_url','script_cascade_helper','pack_category']].copy()
        df = df.loc[df['ready_to_publish'] == True]
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

def calculate_std_of_counts(pack, column_name, df):
    # find all poss values
    all_possible_values = df[column_name].unique().tolist()
    
    # Count the occurrences of each unique value in the column
    counts = pack[column_name].value_counts()

    # Reindex the counts to include all possible suits with a default count of 0 for those not present
    counts = counts.reindex(all_possible_values, fill_value=0)

    # Calculate the standard deviation of these counts
    std_dev = counts.std()

    return std_dev

def split_deck(df, chunk_size):
    """
    Splits a DataFrame into a list of DataFrames with given chunk size.

    :param df: pandas.DataFrame
    :param chunk_size: int
    :return: list of pandas.DataFrame
    """
    # Calculate the number of chunks
    num_chunks = len(df) // chunk_size + int(len(df) % chunk_size != 0)
    
    # Split the DataFrame into chunks
    return [df[i*chunk_size:(i+1)*chunk_size] for i in range(num_chunks)]



def make_packs(pack_size, num_packs, threshold, df):
    packs_ready = []
    holding_area = []

    # initialize cards that haven't been put into packs
    remaining_cards = df.sample(frac=1).reset_index(drop=True)

    # iterate until N packs are makde
    while len(packs_ready) < num_packs:
        # split cards into packs
        split_df = split_deck(remaining_cards, pack_size)

        # check that each pack matches the stddev criteria
        for p in split_df:
            stddev = calculate_std_of_counts(p, 'pack_category', df)
            if stddev <= threshold and len(p)>=pack_size:
                packs_ready.append(p)
            else:
                holding_area.append(p)

        remaining_cards = pd.concat(holding_area, ignore_index=True).sample(frac=1).reset_index(drop=True)

        # Then repeat the above until N packs are made i.e. len(packs_ready) >= N

    packs_to_use = packs_ready[0:num_packs]
    output_deck = pd.concat(packs_to_use, ignore_index=True)

    return output_deck