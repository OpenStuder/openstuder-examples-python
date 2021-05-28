from enum import Flag, auto


class PropertyCategory(Flag):
    INVERTER_STATE = auto()
    PV_POWER = auto()
    PV_ENERGY_STATS = auto()
    GRID_POWER = auto()
    GRID_ENERGY_STATS = auto()
    OUTPUT_POWER = auto()
    OUTPUT_ENERGY_STATS = auto()
    BATTERY_POWER = auto()
    BATTERY_VOLTAGE = auto()
    BATTERY_CURRENT = auto()
    BATTERY_CHARGE = auto()
    BATTERY_TEMPERATURE = auto()
    BATTERY_ENERGY_STATS = auto()


class Installation:
    def __init__(self, device_access_id, inverter_count, solar_charger_count, battery_count):
        self.device_access_id = device_access_id
        self.inverter_count = inverter_count
        self.solar_charger_count = solar_charger_count
        self.battery_count = battery_count
        self.property_values = {}

    def get_property_ids(self, categories):
        return []

    def set_property_value(self, property_id, value):
        self.property_values[property_id] = value

    def inverter_get_state(self):
        return False

    def inverter_turn_on(self, client):
        pass

    def inverter_turn_off(self, client):
        pass

    def pv_get_power(self):
        return None

    def pv_get_energy_today(self):
        return None

    def pv_get_energy_yesterday(self):
        return None

    def grid_get_power(self):
        return None

    def grid_get_energy_today(self):
        return None

    def grid_get_energy_yesterday(self):
        return None

    def output_get_power(self):
        return None

    def output_get_energy_today(self):
        return None

    def output_get_energy_yesterday(self):
        return None

    def battery_get_power(self):
        return None

    def battery_get_voltage(self):
        return None

    def battery_get_current(self):
        return None

    def battery_get_charge(self):
        return None

    def battery_get_temperature(self):
        return None

    def battery_get_charge_today(self):
        return None

    def battery_get_charge_yesterday(self):
        return None

    def battery_get_discharge_today(self):
        return None

    def battery_get_discharge_yesterday(self):
        return None


class Xcom485IInstallation(Installation):
    def __init__(self, device_access_id, devices):
        self.__xtender_ids = []
        self.__variotrack_ids = []
        self.__variostring_ids = []
        self.__battery_id = None

        for device in devices:
            id_ = device['id']
            if id_.startswith('xt') and id_ != 'xts':
                self.__xtender_ids.append(id_)
            if id_.startswith('vt') and id_ != 'vts':
                self.__variotrack_ids.append(id_)
            if id_.startswith('vs') and id_ != 'vss':
                self.__variostring_ids.append(id_)
            if id_ == 'bat':
                self.__battery_id = id_
            super(Xcom485IInstallation, self).__init__(device_access_id, len(self.__xtender_ids), len(self.__variotrack_ids) + len(self.__variostring_ids),
                                                       1 if self.__battery_id is not None else 0)

    def get_property_ids(self, categories):
        ids = []
        if categories & PropertyCategory.INVERTER_STATE:
            ids += [f'{self.device_access_id}.xts.3049']

        if categories & PropertyCategory.PV_POWER:
            for vt_id in self.__variotrack_ids:
                ids.append(f'{self.device_access_id}.{vt_id}.11004')
            for vs_id in self.__variostring_ids:
                ids.append(f'{self.device_access_id}.{vs_id}.15010')

        if categories & PropertyCategory.PV_ENERGY_STATS:
            for vt_id in self.__variotrack_ids:
                ids.append(f'{self.device_access_id}.{vt_id}.11007')
                ids.append(f'{self.device_access_id}.{vt_id}.11011')
            for vs_id in self.__variostring_ids:
                ids.append(f'{self.device_access_id}.{vs_id}.15017')
                ids.append(f'{self.device_access_id}.{vs_id}.15027')

        if categories & PropertyCategory.GRID_POWER:
            for xt_id in self.__xtender_ids:
                ids.append(f'{self.device_access_id}.{xt_id}.3137')

        if categories & PropertyCategory.GRID_ENERGY_STATS:
            for xt_id in self.__xtender_ids:
                ids.append(f'{self.device_access_id}.{xt_id}.3081')
                ids.append(f'{self.device_access_id}.{xt_id}.3080')

        if categories & PropertyCategory.OUTPUT_POWER:
            for xt_id in self.__xtender_ids:
                ids.append(f'{self.device_access_id}.{xt_id}.3136')

        if categories & PropertyCategory.OUTPUT_ENERGY_STATS:
            for xt_id in self.__xtender_ids:
                ids.append(f'{self.device_access_id}.{xt_id}.3083')
                ids.append(f'{self.device_access_id}.{xt_id}.3082')

        if categories & PropertyCategory.BATTERY_POWER:
            ids += [f'{self.device_access_id}.bat.7003']

        if categories & PropertyCategory.BATTERY_VOLTAGE:
            ids += [f'{self.device_access_id}.bat.7000']

        if categories & PropertyCategory.BATTERY_CURRENT:
            ids += [f'{self.device_access_id}.bat.7001']

        if categories & PropertyCategory.BATTERY_CHARGE:
            ids += [f'{self.device_access_id}.bat.7002']

        if categories & PropertyCategory.BATTERY_TEMPERATURE:
            ids += [f'{self.device_access_id}.bat.7033']

        if categories & PropertyCategory.BATTERY_ENERGY_STATS:
            ids += [f'{self.device_access_id}.bat.7007', f'{self.device_access_id}.bat.7008', f'{self.device_access_id}.bat.7009', f'{self.device_access_id}.bat.7010']
        return ids

    def inverter_get_state(self):
        return self.property_values[f'{self.device_access_id}.xts.3049'] == 1.0

    def inverter_turn_on(self, client):
        client.write_property(f'{self.device_access_id}.xts.1415')

    def inverter_turn_off(self, client):
        client.write_property(f'{self.device_access_id}.xts.1399')

    def pv_get_power(self):
        power = 0
        for key, value in self.property_values.items():
            if key.endswith('.11004') or key.endswith('.15010'):
                power += value
        return power

    def pv_get_energy_today(self):
        energy = 0
        for key, value in self.property_values.items():
            if key.endswith('.11007') or key.endswith('.15017'):
                energy += value
        return energy

    def pv_get_energy_yesterday(self):
        energy = 0
        for key, value in self.property_values.items():
            if key.endswith('.11011') or key.endswith('.15027'):
                energy += value
        return energy

    def grid_get_power(self):
        power = 0
        for key, value in self.property_values.items():
            if key.endswith('.3137'):
                power += value
        return power

    def grid_get_energy_today(self):
        energy = 0
        for key, value in self.property_values.items():
            if key.endswith('.3081'):
                energy += value
        return energy

    def grid_get_energy_yesterday(self):
        energy = 0
        for key, value in self.property_values.items():
            if key.endswith('.3080'):
                energy += value
        return energy

    def output_get_power(self):
        power = 0
        for key, value in self.property_values.items():
            if key.endswith('.3136'):
                power += value
        return power

    def output_get_energy_today(self):
        energy = 0
        for key, value in self.property_values.items():
            if key.endswith('.3083'):
                energy += value
        return energy

    def output_get_energy_yesterday(self):
        energy = 0
        for key, value in self.property_values.items():
            if key.endswith('.3082'):
                energy += value
        return energy

    def battery_get_power(self):
        return self.property_values[f'{self.device_access_id}.bat.7003']

    def battery_get_voltage(self):
        return self.property_values[f'{self.device_access_id}.bat.7000']

    def battery_get_current(self):
        return self.property_values[f'{self.device_access_id}.bat.7001']

    def battery_get_charge(self):
        return self.property_values[f'{self.device_access_id}.bat.7002']

    def battery_get_temperature(self):
        return self.property_values[f'{self.device_access_id}.bat.7033']

    def battery_get_charge_today(self):
        return self.property_values[f'{self.device_access_id}.bat.7007']

    def battery_get_charge_yesterday(self):
        return self.property_values[f'{self.device_access_id}.bat.7009']

    def battery_get_discharge_today(self):
        return self.property_values[f'{self.device_access_id}.bat.7008']

    def battery_get_discharge_yesterday(self):
        return self.property_values[f'{self.device_access_id}.bat.7010']


class DemoInstallation(Installation):
    def __init__(self, device_access_id):
        super(DemoInstallation, self).__init__(device_access_id, 1, 1, 1)

    def get_property_ids(self, categories):
        ids = []
        if categories & PropertyCategory.INVERTER_STATE:
            ids += [f'{self.device_access_id}.inv.3049']
        if categories & PropertyCategory.PV_POWER:
            ids += [f'{self.device_access_id}.sol.11004']
        if categories & PropertyCategory.PV_ENERGY_STATS:
            ids += [f'{self.device_access_id}.sol.11007', f'{self.device_access_id}.sol.11011']
        if categories & PropertyCategory.GRID_POWER:
            ids += [f'{self.device_access_id}.inv.3137']
        if categories & PropertyCategory.GRID_ENERGY_STATS:
            ids += [f'{self.device_access_id}.inv.3081', f'{self.device_access_id}.inv.3080']
        if categories & PropertyCategory.OUTPUT_POWER:
            ids += [f'{self.device_access_id}.inv.3136']
        if categories & PropertyCategory.OUTPUT_ENERGY_STATS:
            ids += [f'{self.device_access_id}.inv.3083', f'{self.device_access_id}.inv.3082']
        if categories & PropertyCategory.BATTERY_POWER:
            ids += [f'{self.device_access_id}.bat.7003']
        if categories & PropertyCategory.BATTERY_VOLTAGE:
            ids += [f'{self.device_access_id}.bat.7000']
        if categories & PropertyCategory.BATTERY_CURRENT:
            ids += [f'{self.device_access_id}.bat.7001']
        if categories & PropertyCategory.BATTERY_CHARGE:
            ids += [f'{self.device_access_id}.bat.7002']
        if categories & PropertyCategory.BATTERY_TEMPERATURE:
            ids += [f'{self.device_access_id}.bat.7033']
        if categories & PropertyCategory.BATTERY_ENERGY_STATS:
            ids += [f'{self.device_access_id}.bat.7007', f'{self.device_access_id}.bat.7008', f'{self.device_access_id}.bat.7009', f'{self.device_access_id}.bat.7010']
        return ids

    def inverter_get_state(self):
        return self.property_values[f'{self.device_access_id}.inv.3049'] == 1.0

    def inverter_turn_on(self, client):
        client.write_property(f'{self.device_access_id}.inv.1415')

    def inverter_turn_off(self, client):
        client.write_property(f'{self.device_access_id}.inv.1399')

    def pv_get_power(self):
        return self.property_values[f'{self.device_access_id}.sol.11004']

    def pv_get_energy_today(self):
        return self.property_values[f'{self.device_access_id}.sol.11007']

    def pv_get_energy_yesterday(self):
        return self.property_values[f'{self.device_access_id}.sol.11011']

    def grid_get_power(self):
        return self.property_values[f'{self.device_access_id}.inv.3137']

    def grid_get_energy_today(self):
        return self.property_values[f'{self.device_access_id}.inv.3081']

    def grid_get_energy_yesterday(self):
        return self.property_values[f'{self.device_access_id}.inv.3080']

    def output_get_power(self):
        return self.property_values[f'{self.device_access_id}.inv.3136']

    def output_get_energy_today(self):
        return self.property_values[f'{self.device_access_id}.inv.3083']

    def output_get_energy_yesterday(self):
        return self.property_values[f'{self.device_access_id}.inv.3082']

    def battery_get_power(self):
        return self.property_values[f'{self.device_access_id}.bat.7003']

    def battery_get_voltage(self):
        return self.property_values[f'{self.device_access_id}.bat.7000']

    def battery_get_current(self):
        return self.property_values[f'{self.device_access_id}.bat.7001']

    def battery_get_charge(self):
        return self.property_values[f'{self.device_access_id}.bat.7002']

    def battery_get_temperature(self):
        return self.property_values[f'{self.device_access_id}.bat.7033']

    def battery_get_charge_today(self):
        return self.property_values[f'{self.device_access_id}.bat.7007']

    def battery_get_charge_yesterday(self):
        return self.property_values[f'{self.device_access_id}.bat.7009']

    def battery_get_discharge_today(self):
        return self.property_values[f'{self.device_access_id}.bat.7008']

    def battery_get_discharge_yesterday(self):
        return self.property_values[f'{self.device_access_id}.bat.7010']
