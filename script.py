#!/usr/bin/env python

'''
The imported Excel file lists all PLZ from the Postlexikon of the
österreichische Post AG, available at https://www.post.at/g/c/postlexikon
2020-07-15
'''

# Reading the PLZ list of the Österreichische Post AG:
POST = pd.read_excel("PLZ-BESTIMMUNGSORT-06072020.xls")

df = POST[['PLZ', 'Bestimmungsort']] # only PLZ and name are of interest
# Dropping duplicate entries:
df = df.loc[df.duplicated() == False].reset_index(drop=True)
# Creating location name:
df['Location'] = df.Bestimmungsort.str.replace("ß", "ss")
                 + " "
                 + df.PLZ.apply(str)
                 + ", Austria"
# Note: Special German character ß needs to be replaced with ss, otherwise
# Nominatim cannot process the location name)

# Setting up user for Nominatim:
locator = Nominatim(user_agent="my-user")
# # Limiting the rate of request to 1/s:
geocode = RateLimiter(locator.geocode, min_delay_seconds=1)
# Testing the setup with a random location name
# location = locator.geocode("3100 St. Pölten, Austria")

for i in df.index: # for every location in the dataset
    # Getting the geodata from Nominatim:
    gc = locator.geocode(df.loc[i].Location)
    if gc: # if the geodata was succesfully acquired
        # Storing latitudes and longitudes in the respective columns:
        df.loc[i, 'Latitude'] = gc.latitude
        df.loc[i, 'Longitude'] = gc.longitude
    else: # If no geodata was acquired printing the location name:
        df.loc[i].Location

# Saving the geodata to a csv file:
df.to_csv("geocodes-austria.csv", sep="\t", index=False)
# Note: Some locations cannot be located and need to be filled in manually