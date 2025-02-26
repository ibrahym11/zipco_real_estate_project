import requests
import os
import json
import pandas as pd

# Step 1: Fetch Data from API
url = "https://realty-mole-property-api.p.rapidapi.com/properties"

querystring = {"Limit": "100000"}

headers = {
    "x-rapidapi-key": "dbb3bcf097mshfb01a9ac784d64fp122d84jsnc850a4b9192e",
    "x-rapidapi-host": "realty-mole-property-api.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)
print(response.json())

data = response.json()

# Save the data to a file
filename = 'PropertyRecords.json'
with open(filename, 'w') as file:
    json.dump(response.json(), file, indent=4)

# Step 2: Load JSON Data into Pandas DataFrame
propertyrecords_df = pd.read_json('PropertyRecords.json')

# Convert dictionary columns to strings
propertyrecords_df['features'] = propertyrecords_df['features'].apply(json.dumps)

# Fill missing data with default values
propertyrecords_df.fillna({
    'assessorID': 'Unknown',
    'legalDescription': 'Not available',
    'squareFootage': 0,
    'subdivision': 'Not available',
    'yearBuilt': 0,
    'bathrooms': 0,
    'lotSize': 0,
    'propertyType': 'Unknown',
    'lastSalePrice': 0,
    'lastSaleDate': 'Not available',
    'features': 'None',
    'taxAssessment': 'Not available',
    'owner': 'Unknown',
    'propertyTaxes': 'Not available',
    'bedrooms': 0,
    'ownerOccupied': 0,
    'zoning': 'Unknown',
    'addressLine2': 'Not available',
    'formattedAddress': 'Not available',
    'county': 'Not available'
}, inplace=True)

# Step 3: Create Dimension Tables

# Location Dimension Table
location_dim = propertyrecords_df[['addressLine1', 'city', 'state', 'zipCode', 'formattedAddress',
                                   'county', 'longitude', 'latitude', 'addressLine2']].drop_duplicates().reset_index(drop=True)
location_dim.index.name = 'location_id'

# Sales Dimension Table
sales_dim = propertyrecords_df[['lastSaleDate', 'lastSalePrice']].drop_duplicates().reset_index(drop=True)
sales_dim.index.name = 'sales_id'

# Features Dimension Table
features_dim = propertyrecords_df[['features', 'yearBuilt', 'propertyType', 'bedrooms',
                                   'bathrooms']].drop_duplicates().reset_index(drop=True)
features_dim.index.name = 'features_id'

# Fact Table (Merged data)
fact_dim = propertyrecords_df.merge(location_dim, on=['addressLine1', 'city', 'state', 'zipCode', 'formattedAddress', 'county', 'longitude', 'latitude', 'addressLine2'], how='left') \
                             .merge(sales_dim, on=['lastSaleDate', 'lastSalePrice'], how='left') \
                             .merge(features_dim, on=['features', 'yearBuilt', 'propertyType', 'bedrooms', 'bathrooms'], how='left') \
                             [['location_id', 'sales_id', 'features_id', 'formattedAddress', 'taxAssessment', 'id', 'assessorID', 'squareFootage', 'legalDescription', 'ownerOccupied', 'subdivision',
                               'propertyTaxes', 'owner', 'lotSize']]

# Step 4: Save Fact Table
fact_columns = ['addressLine1', 'city', 'state', 'zipCode', 'formattedAddress',
       'county', 'features', 'taxAssessment', 'id', 'longitude', 'latitude',
       'assessorID', 'squareFootage', 'yearBuilt', 'propertyType', 'bedrooms',
       'bathrooms', 'legalDescription', 'ownerOccupied', 'subdivision',
       'propertyTaxes', 'owner', 'lotSize', 'lastSaleDate', 'addressLine2',
       'lastSalePrice']
fact_table = propertyrecords_df[fact_columns]

# Save the fact table to CSV (optional)
fact_table.to_csv('property_fact.csv', index=False)

# Save dimensions to CSV (optional)
location_dim.to_csv('location_dimension.csv', index=False)
sales_dim.to_csv('sales_dimension.csv', index=False)
features_dim.to_csv('features_dimension.csv', index=False)

print("Data loaded and saved successfully.")
