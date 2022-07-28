# Garden data

## Glossary

- grower:
  - End user of the system, may be a horticulturalist, hobbiest, or data user
- system:
  - this software package together with a Raspberry Pi 

## Overview 

To provide open source software to aid gardeners, farmers, homesteaders and plant lovers alike grow more productive and beautiful plants. 

Writing for the Raspberry pi environment (possible expansion to other ARM machines) allows these low power machines to be deployed onsite easily and inexpensively. 

The system will rely on sensor data, both real-time and historic, to control systems like irrigation, lighting, and temperature. Rain sensors / soil moisture to ensure that plants are not over watered or water wasted. Graduated lighting as the sun sets to minimize power usage and provide more even lighting to the plants. 

There are numerous proven methods of greenhouse control at an industrial scale, but those are designed for pure yield and not efficiency. Nor are they affordable for non-commercial growers. I hope to provide an affordable way for people to take a data driven approach to gardening. 

## Sensors 
There are a variety of low cost sensor options available. These can be polled and stored at a configurable rate. Video and image sensors are also included in this category. 

Various conditions which can be monitored:
- light
- temperature
- humidity
- air speed
- rain fall
- soil temperature
- soil moisture
- soil ph 
- soil nutrient
- irrigation water flow 

## Controls 
As with sensors there are many different conditions you can control. If you can control power then really anything is possible. 

Possible conditions to control:
- soil moisture (irrigation)
- lighting 
  - color
  - brightness
- temperature
- humidity
- soil nutrients
- wind
- vents (open/close)

## Software 
Python will be the primary language for a number of reasons, largest of all, many of the utilities for the Raspberry Pi and the GPIO pins are written in Python. But also the end user of the system may have limited programming experience and Python has a low barrier to entry. Overall, languages, dependencies, and other vendor software should be chosen based on ease of use, community support and other relevant.  


## Data
Data will be gathered by sensors to be used to future control calculations. Previous days temperature and rainfall can be used to determine how much water is used. As the system matures various sensors data can be analyzed in conjunction to help increase efficiency and yield. Soil moisture, temperature, rainfall, wink speed and water flow rates can be processed to determine the most efficient water usage helping to budget water use or even calculate the best size of rainwater collection needed to irrigate. 

As the project grow there is hope to setup an option to submit you data to a cloud server, both for storage and backup. There would be an opt in component to share data. With enough successes and failures best conditions can be inferred and offered as suggestions to other growers. 

## User interface
Since the raspberry pi is small and low powered it may end up being placed away from network connectivity. Therefore there needs to be access via a phone or laptop computer in proximity to the device. This could be done via a bluetooth, wifi device, or usb connection (usb gadget mode) and accessible from a utility on the growers device. 

A network connection will be preferred since alerts can play a large role in an automated system. With a network connection a local (or WAN) site can be used to access the system, view reports and logs, and view the garden through live and time lapse video. Grower logging will also be done through the web interface, with anecdotal reports which can be referenced in the future.

## Websites that I have referenced