# CahasEDI-Core

Server/Client to AS2 messaging server for managing EDI partnerships and interpreting messages

#### Disclaimer

CahasEDI-Core is in very early stages of development and is not ready/intended for use in system critical environments at the moment.

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
* Postgresql
* OpenAS2 Configured for each partnership
