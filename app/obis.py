SENSORS = {
    "power_import_w": ("EGD aktuální odběr", "W", "power", "measurement"),
    "power_export_w": ("EGD aktuální dodávka", "W", "power", "measurement"),
    "power_l1_w": ("EGD výkon L1", "W", "power", "measurement"),
    "power_l2_w": ("EGD výkon L2", "W", "power", "measurement"),
    "power_l3_w": ("EGD výkon L3", "W", "power", "measurement"),

    "energy_import_kwh": ("EGD energie odběr celkem", "kWh", "energy", "total_increasing"),
    "energy_export_kwh": ("EGD energie dodávka celkem", "kWh", "energy", "total_increasing"),
    "energy_import_t1_kwh": ("EGD energie odběr T1", "kWh", "energy", "total_increasing"),
    "energy_import_t2_kwh": ("EGD energie odběr T2", "kWh", "energy", "total_increasing"),
    "energy_import_t3_kwh": ("EGD energie odběr T3", "kWh", "energy", "total_increasing"),
    "energy_import_t4_kwh": ("EGD energie odběr T4", "kWh", "energy", "total_increasing"),

    "tariff": ("EGD aktuální tarif", None, None, None),
    "meter_serial": ("EGD výrobní číslo", None, None, None),

    "last_message": ("EGD poslední zpráva", None, "timestamp", None),
    "message_count": ("EGD počet zpráv", None, None, "total_increasing"),
    "reconnect_count": ("EGD počet reconnectů", None, None, "total_increasing"),
    "last_frame_length": ("EGD délka posledního rámce", "B", "data_size", "measurement"),
}


OBIS_MAP = {
    "1.7.0": ("power_import_w", 1),
    "2.7.0": ("power_export_w", 1),

    "21.7.0": ("power_l1_w", 1),
    "41.7.0": ("power_l2_w", 1),
    "61.7.0": ("power_l3_w", 1),

    "1.8.0": ("energy_import_kwh", 0.001),
    "1.8.1": ("energy_import_t1_kwh", 0.001),
    "1.8.2": ("energy_import_t2_kwh", 0.001),
    "1.8.3": ("energy_import_t3_kwh", 0.001),
    "1.8.4": ("energy_import_t4_kwh", 0.001),

    "2.8.0": ("energy_export_kwh", 0.001),
}
