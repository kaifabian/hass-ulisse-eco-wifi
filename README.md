# hass-ulisse-eco-wifi
[Home Assistant](https://www.home-assistant.io/) integration for *Ulisse 13 DCI Eco WiFi*.

The Ulisse 13 DCI Eco WiFi is a type of mobile split air conditioning system (separate inside and outside units) that is sold by multiple brands.


## Supported devices and firmware versions

// TODO


## Installation

### HACS
*This is not (yet) officially supported, sorry!*

### Manual installation
Merge the `custom_integrations` directory in this repository with the one in your Home Assistant configuration directory. The folder structure should look as follows:
```
[+] (config folder)
 |- ...
 |-[+] custom_integrations
 |  |- ...
 |  |-[+] ulisse_eco_wifi
 |  |  |- ...
 |  |  |- manifest.json
 |  |  |- climate.py
 |  |  \- ...
 |  \- ...
 \- ...
```


## Configuration

To fulfill minimal requirements to control one single A/C unit, add the following to your `configuration.yaml`:

```
climate:
  - platform: ulisse_eco_wifi
    devices:
      - host: "<ip address of your AC>"
```

A `device` configuration consists of the following options:
| option      | required/optional | type                                 | default value            | description |
| ----------- | ----------------- | ------------------------------------ | ------------------------ | --- |
| `host`      | required          | string                               | -                        | IP address or hostname of the A/C unit |
| `port`      | optional          | integer                              | 1001                     | TCP port of the A/C's web server |
| `ssl`       | optional          | boolean                              | false                    | Enables accessing the device's webserver via SSL<sup>[1](#unique_id)</sup> |
| `name`      | optional          | string                               | "Ulisse 13 DCI Eco WiFi" | Display name of the device |
| `unique_id` | optional          | string<sup>[3](#unique_id_fmt)</sup> | -                        | Unique ID identifying the device<sup>[2](#unique_id)</sup>. Required if the device should be referenced in automations/scripts/etc. |

<a name="ssl"><sup>1</sup></a>: SSL is **not** supported by the current A/C firmware. Use this only if you access the A/C through an SSL-enabled reverse proxy. \
<a name="unique_id"><sup>2</sup></a>: This field should uniquely identify the A/C unit. We recommend using the device's serial number or MAC address here. Please do *not* use any information unrelated to the actual unit. Bad examples are: location (e. g. "Bedroom"), because it could change over time; color (e. g. "white"), because it could apply to multiple units; IP address (e. g. "192.168.123.21"), because it could change over time; ... \
<a name="unique_id_fmt"><sup>3</sup></a>: Valid characters are lower-case letters (`[a-z]`) and numbers (`[0-9]`) and underscores (`_`). The `unique_id` must not start or end with an underscore and also must not contain multiple consecutive underscores.


## Legal

This integration is provided as-is, free of charge, under the terms of the [license](LICENSE.md).

Although this integration was tested by the author(s) before publication, we do not have any official relationship with any manufacturer or vendor of those A/C units. Everything related to the control of the A/C unit and the connected protocol(s) has been reverse engineered. We do not give any guarantee with regards to this integration whatsoever, but especially:

- We will not guarantee that this integration works with your A/C unit.
- We will not guarantee that we will keep this integration up to date with any changes made to the A/C unit by the manufacturer(s) or vendor(s), e. g. firmware updates.
- We take no liability for any damages and/or injuries caused by using this integration, i. e. damage to the A/C unit or to your home.


## General and security considerations

- This integration is provided as-is. There are no guarantees that it will keep functioning. We recommend **not** updating your device's firmware beyond the version supported by this integration.
- The A/C unit's web interface is **unencrypted** and **unauthenticated**. Make sure that only users and devices that are supposed to control the A/C have access to the unit's IP address.
- Communication with the vendor's cloud is also **unencrypted**. Although it is **authenticated** (random-ish username/password combination), credentials can easily be *sniffed* because they are sent as plain text. Also, the cloud doesn't offer any way to verify its authenticity, so it can easily be impersonated by any third party. We recommend **blocking** access to the cloud by either null-routing or firewalling the IP address `31.14.128.210`.


## Acknowledgements

// TODO
