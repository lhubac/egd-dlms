## Proč tento projekt vznikl?

Chytré elektroměry distribuované společností EG.D poskytují rozhraní HAN
(Home Area Network), které pravidelně vysílá DLMS/COSEM Push zprávy.

Přestože obsahují cenné informace o okamžité spotřebě, energiích,
tarifu nebo stavech relé, neexistovalo jednoduché open-source řešení,
které by tato data automaticky zpřístupnilo v Home Assistantu.

Projekt EGD-DLMS vznikl s cílem nabídnout:

- spolehlivý pasivní příjem dat z elektroměru,
- jednoduché nasazení pomocí Dockeru,
- automatickou integraci do Home Assistantu,
- možnost vývoje a testování bez připojeného elektroměru.

## Why this project?

Smart meters distributed by EG.D provide a HAN (Home Area Network) interface
that periodically transmits DLMS/COSEM Push messages.

Although the transmitted data contain valuable information about power,
energy, tariff and relay status, there is currently no simple open-source
bridge that automatically integrates these values into Home Assistant.

EGD-DLMS fills this gap by providing a lightweight passive bridge focused on:

- reliability,
- easy deployment using Docker,
- automatic Home Assistant integration,
- reproducible offline testing.

![License](https://img.shields.io/badge/license-MIT-green.svg)
