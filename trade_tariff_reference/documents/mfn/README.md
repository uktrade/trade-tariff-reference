# Creates a printed classification and schedule from the UK tariff database for 2019

## Building the tariff schedule

Run the Python script as follows:

`py create_tariff_schedule_xml.py s 01 99`

in order to create a full set of schedule documents from the current database, where the following arguments apply.

* create_tariff_schedule_xml.py is the script name
* s is the switch which indicates that this is a schedule that is being built (not a classification table, which is represented by "c")
* 01 is the 1st chapter to build
* 99 is the last chapter to build

## Building the tariff classification

Run the Python script as follows:

`py create_tariff_schedule_xml.py c 01 99`

in order to create a full set of schedule documents from the current database, where the following arguments apply.

- create_tariff_schedule_xml.py is the script name
- "c" is the switch which indicates that this is a classification table that is being built
- 01 is the 1st chapter to build
- 99 is the last chapter to build

## 