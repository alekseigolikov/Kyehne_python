# Shipping API


## Shipping list
```
GET /shippings/
```
### status codes:
200 - OK


## New shipment creation:
```
POST /shippings/
```

### data format: form-data/x-www-form-urlencoded/raw post json

### status codes:
201 - New shipment created
400 - Incorrect data provided


## Shipment detail:
```
GET /shippings/<id>/
```
### <id> is the shipment id 

### status codes:
404 - Shipping not found
200 - OK


## Shipment update:
```
PUT /shipping/<id>/
```
### data format: form-data/x-www-form-urlencoded/raw post json
### <id> is the shipment id

### status codes:
404 - Shipping not found
400 - Incorrect data provided
200 - OK


## Shipment delete:
```
DELETE /shipping/<id>/
```
### <id> is the shipment id

### status codes:
404 - Shipping not found
204 - Shipping deleted

# Data fields for update/creation:
id - ID of shipiing
creation_date - Date of record creation
name - Name of Shipment
origin - City of Origin
destination - City of Destination
current_location - Current location
state - State