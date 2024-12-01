# Tibber GraphAPI [access your EV data]

__Please note__, _that this integration is not official and not supported by the tibber development team. I am not affiliated with tibber in any way._

[![hacs_badge][hacsbadge]][hacs] [![github][ghsbadge]][ghs] [![BuyMeCoffee][buymecoffeebadge]][buymecoffee] [![PayPal][paypalbadge]][paypal] [![hainstall][hainstallbadge]][hainstall]

---

## Tibber Invitation link

###### Advertisement / Werbung

If you want to join Tibber (become a customer), you might want to use my personal invitation link. When you use this link, Tibber will we grant you and me a bonus of 50,-€ for each of us. This bonus then can be used in the Tibber store (not for your power bill) - e.g. to buy a Tibber Bridge. I am fully aware, that when you are here in this repository the chances are very high, that you are already a Tibber customer and have already a Tibber Pulse. If you are already a Tibber customer and have not used an invitation link yet, you can also enter one afterward in the Tibber App (up to 14 days). [[see official Tibber support article](https://support.tibber.com/en/articles/4601431-tibber-referral-bonus#h_ae8df266c0)]

Please consider [using my personal Tibber invitation link to join Tibber today](https://invite.tibber.com/6o0kqvzf) or Enter the following code: 6o0kqvzf (six, oscar, zero, kilo, quebec, victor, zulu, foxtrot) afterward in the Tibber App - TIA!

---

## Know Issues

- probably very unstable - initial version

## Want to report an issue?

Please use the [GitHub Issues](https://github.com/marq24/ha-tibber-graphapi/issues) for reporting any issues you encounter with this integration. Please be so kind before creating a new issues, check the closed ones, if your problem have been already reported (& solved). 

In order to speed up the support process you might like already prepare and provide DEBUG log output. In the case of a technical issue - like not-supported--yet-communication-mode - I would need this DEBUG log output to be able to help/fix the issue. There is a short [tutorial/guide 'How to provide DEBUG log' here](https://github.com/marq24/ha-senec-v3/blob/master/docs/HA_DEBUG.md) - please take the time to quickly go through it.

## Kudos

- all handcrafted 

## Setup / Installation

### Step I: Install the integration

#### Option 1: via HACS

- Install [Home Assistant Community Store (HACS)](https://hacs.xyz/)
- Add the custom integration repository to HACS: `https://github.com/marq24/ha-tibber-graphapi`
- Add integration repository (search for "Tibber GraphAPI" in "Explore & Download Repositories")
- Use the 3-dots at the right of the list entry (not at the top bar!) to download/install the custom integration - the latest release version is automatically selected. Only select a different version if you have specific reasons.
- After you presses download and the process has completed, you must __Restart Home Assistant__ to install all dependencies
- Setup the custom integration as described below (see _Step II: Adding or enabling the integration_)

#### Option 2: manual steps

- Copy all files from `custom_components/tibber_graphapi/` to `custom_components/tibber_graphapi/` inside your config Home Assistant directory.
- Restart Home Assistant to install all dependencies

### Step II: Adding or enabling the integration

__You must have installed the integration (manually or via HACS before)!__

#### Option 1: My Home Assistant (2021.3+)

Just click the following Button to start the configuration automatically (for the rest see _Option 2: Manually steps by step_):

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=tibber_graphapi)

#### Option 2: Manually steps by step

Add custom integration using the web interface and follow instruction on screen.

- Go to `Configuration -> Integrations` and add "Tibber GraphAPI" integration
- Specify:
    - Provide display name for the device
    - Provide the username of your Tibber account
    - Provide the password of your Tibber account
    - OPTIONAL: Provide the vehicle index [if you have multiple vehicles in your tibber account]
    - Provide the update interval (can be 60 Seconds)
    - Provide area where the Tibber Pule Bridge is located

__IMPORTANT to know__: It can happen all types of errors - this is a quick hack build

[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-custom-orange.svg?style=for-the-badge&logo=homeassistantcommunitystore&logoColor=ccc

[ghs]: https://github.com/sponsors/marq24
[ghsbadge]: https://img.shields.io/github/sponsors/marq24?style=for-the-badge&logo=github&logoColor=ccc&link=https%3A%2F%2Fgithub.com%2Fsponsors%2Fmarq24&label=Sponsors

[buymecoffee]: https://www.buymeacoffee.com/marquardt24
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a-coffee-blue.svg?style=for-the-badge&logo=buymeacoffee&logoColor=ccc

[paypal]: https://paypal.me/marq24
[paypalbadge]: https://img.shields.io/badge/paypal-me-blue.svg?style=for-the-badge&logo=paypal&logoColor=ccc

[hainstall]: https://my.home-assistant.io/redirect/config_flow_start/?domain=tibber_graphapi
[hainstallbadge]: https://img.shields.io/badge/dynamic/json?style=for-the-badge&logo=home-assistant&logoColor=ccc&label=usage&suffix=%20installs&cacheSeconds=15600&url=https://analytics.home-assistant.io/custom_integrations.json&query=$.tibber_graphapi.total
