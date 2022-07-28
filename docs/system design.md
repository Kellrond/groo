# System design
The goal of this document is to outline and record the decisions which have been made while building this. Things will evolve and change as the project progresses and new decisions need to be made. 

## Overview
The goal is to have a system which can be controlled remotely via a web interface or from command line either locally or remotely via ssh. The system should also be able to operate as a master or a slave node. To do this it will be important to build each module so that it's provides data and functions that work by all methods of control. 

## Modules 
### Sensors
Sensor modules will likely have to be written per vendor or a wrapper written for existing Python sensor modules. Readings must be made available for display and written to the DB at different poling rates. 
### Controls 
Control modules like sensors will likely have to be written per vendor or vendor code wrapped with a module. Controls must be available to report status and change status from any interface. Safeties must be in place to prevent a system failure from damaging plants.
### Alerts
Email, and SMS messages should be sent to a grower if there is an issue which requires human intervention or a critical decision needs to be made and the system does not have enough data or history to know how to respond.
### Logging
Logging via flat file will be used for software debugging, but separately to help unify message between systems. While apache will log an API call, it may not be clear how that interacted with other routines. Logging will act to log module activity and may use other services logs to paint a more complete picture on the history of the system. 
### Database
The database access will only take place through this module. The persistence layer should be able to be swapped out and changes only happen in one place. The database will start out as MySQL, but I want to make sure it works well with SQLite too.
