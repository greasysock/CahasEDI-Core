# CahasEDI-Core

Server/Client to AS2 messaging server for managing EDI partnerships and interpreting messages

## Frontend

[CahasEDI-Dashboard](https://github.com/greasysock/CahasEDI-Dashboard) is being developed alongside CahasEDI-Core to be the official frontend for the project.

#### Disclaimer

CahasEDI-Core is in very early stages of development and is not ready/intended for use at the moment.

#### Framework

#### Todo

* Implement EDI Documents for reading and writing (to vendor specification):
    * ~~810~~
    * ~~850~~
    * ~~855~~
    * 856
    * ~~860~~
    * ~~997~~
* Check documents for syntax
* Migrate syntax backend from EdiEngine to native library
#### Requirements
* Temporarily
    * EdiEngine https://github.com/olmelabs/EdiEngine (Used for syntax checking, and 856 document type)
* Python 3
    * SQLAlchemy
    * Psycopg2
    * Falcon
    * gunicorn
    * redis
    * huey
* Postgresql
* OpenAS2 Configured for each partnership
