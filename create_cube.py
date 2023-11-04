# %% libraries
import pandas as pd
import json
import datetime
import sys
import fun

back_url = 'https://customcards.s3.us-east-2.amazonaws.com/card_back.jpg'

#%% parse arguments
options = ['cube','tokens','lands','packs']
type = None
if len(sys.argv) <= 1:
    print('No args provided. Options are: {}'.format(', '.join(options)))
else:
    for e in sys.argv[1:]:
        if e in options:
            type = e
            print('Making {}'.format(type))
            break
    if not type:
        print('No valid arguments. Options are: {}'.format(', '.join(options)))


#%% Get data from the proper sheet. 
# Remove excess columns, filter unused rows, create proper card title
df = fun.parse_sheet(type)


#%% Make packs if the option for it was selected
if type == 'packs':
    df = fun.make_packs(pack_size = 12, num_packs=16, threshold=1.1, df=df)


#%%
# Add additional columns that the json deck will need
df_cardid = fun.add_card_columns(df)
 
#%% Make the dict values for the components of ObjectStates
ContainedObjects = fun.contained_object(df_cardid, type, back_url)
DeckIDs = list(df_cardid['CardID'])
CustomDeck = fun.custom_deck(df_cardid, back_url)

#%% Combine all values to the final deck
final_object = {
    'ObjectStates': [
        {
            'Name': 'DeckCustom',
            'ContainedObjects': ContainedObjects,
            'DeckIDs': DeckIDs,
            'CustomDeck': CustomDeck,
            "Transform": fun.std_transform()
        }
    ]
}

#%% Writing to json file
json_object = json.dumps(final_object, indent=4)
file_name = datetime.datetime.now().strftime("{}_%Y-%m-%d-%H%M%S.json".format(type))

with open(file_name, "w") as outfile:
    outfile.write(json_object)