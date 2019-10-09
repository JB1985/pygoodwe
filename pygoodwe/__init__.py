import json
import logging
from datetime import datetime
import argparse
import sys
import time
import requests

def run_once(args):
    #global last_eday_kwh

    # Check if we only want to run during daylight
    #if args.city:
    #    a = Astral()
    #    sun = a[args.city].sun(local=True)
    #    now = datetime.time(datetime.now())
    #    if now < sun['dawn'].time() or now > sun['dusk'].time():
    #        logging.debug("Skipped upload as it's night")
    #        return

    # Fetch the last reading from GoodWe
    gw = API(
        system_id=args.get('gw_station_id'), 
        account=args.get('gw_account'), 
        password=args.get('gw_password'),
        lang='en',
        )
    data = gw.getCurrentReadings()

    # Check if we want to abort when offline
    #if args.get('skip_offline'):
    #    if data['status'] == 'Offline':
    #        logging.debug("Skipped upload as the inverter is offline")
    #        return

    # Append reading to CSV file
    if args.get('csv'):
        raise NotImplementedError("Haven't done the CSV thing yet.")
    #    if data['status'] == 'Offline':
    #        logging.debug("Don't append offline data to CSV file")
    #    else:
    #        locale.setlocale(locale.LC_ALL, locale.getlocale())
    #        csv = gw_csv.GoodWeCSV(args.csv)
    #        csv.append(data)

    # Submit reading to PVOutput, if they differ from the previous set
    #eday_kwh = data['eday_kwh']
    #if data['pgrid_w'] == 0 and abs(eday_kwh - last_eday_kwh) < 0.001:
    #    logging.debug("Ignore unchanged reading")
    #else:
    #    last_eday_kwh = eday_kwh

    #if args.darksky_api_key:
    #    ds = ds_api.DarkSkyApi(args.darksky_api_key)
    #    data['temperature'] = ds.get_temperature(data['latitude'], data['longitude'])
        
    #voltage = data['grid_voltage']
    if args.get("pv_voltage"):
        #voltage=data['pv_voltage']
        pass
    return data
    #pvo = pvo_api.PVOutputApi(args.pvo_system_id, args.pvo_api_key)
    #pvo.add_status(data['pgrid_w'], last_eday_kwh, data.get('temperature'), voltage)


#def copy(args):
    # Fetch readings from GoodWe
    #date = datetime.strptime(args.date, "%Y-%m-%d")

    #gw = API(args.gw_station_id, args.gw_account, args.gw_password)
    #data = gw.getDayReadings(date)

    #if args.darksky_api_key:
    #    ds = ds_api.DarkSkyApi(args.darksky_api_key)
    #    temperatures = ds.get_temperature_for_day(data['latitude'], data['longitude'], date)
    #else:
    #    temperatures = None
    #temperatures = None
    # Submit readings to PVOutput
    #pvo = pvo_api.PVOutputApi(args.pvo_system_id, args.pvo_api_key)
    #pvo.add_day(data['entries'], temperatures)


POWERFLOW_STATUS_TEXT = { 
    -1 : "Outward",
}

class API(object):

    def __init__(self, system_id : str, account : str, password : str, skipload : bool=False):
        """
        lang: Real Soon Now it'll filter out any responses without that language
        skipload: don't run self.getCurrentReadings() on init
        """
        self.system_id = system_id
        self.account = account
        self.password = password
        self.token = '{"version":"v2.0.4","client":"ios","language":"en"}'
        self.global_url = 'https://globalapi.sems.com.cn/api/'
        self.base_url = self.global_url
        self.status = { -1 : 'Offline', 0 : 'Waiting', 1 : 'Normal' }
        if skipload:
            self.data = 0
        else:
            self.getCurrentReadings(raw=True)

    def _loaddata(self, filename):
        """ loads a json file of existing data """
        with open(filename, 'r') as fh:
            self.data = json.loads(fh.read())
        return True



        
    def loaddata(self, filename):
        """ loads a json object from a file with a string. write this out with json.dumps(self.data) """
        self._loaddata(filename)
            
    def _getCurrentReadings(self, raw=True):
        ''' Download the most recent readings from the GOODWE API. '''

        payload = {
            'powerStationId' : self.system_id
        }

        # GOODWE server
        self.data = self.call("v1/PowerStation/GetMonitorDetailByPowerstationId", payload)

        if raw:
            return self.data

    def getCurrentReadings(self, raw=True):
        return self._getCurrentReadings(raw)
        


    #def getDayReadings(self, date):
    #    date_s = date.strftime('%Y-%m-%d')

    #    payload = {
    #        'powerStationId' : self.system_id
    #    }
    #    data = self.call("v1/PowerStation/GetMonitorDetailByPowerstationId", payload)
    #   if 'info' not in data:
        #     logging.warning(date_s + " - Received bad data " + str(data))
        #     return result

        # result = {
        #     'latitude' : data['info'].get('latitude'),
        #     'longitude' : data['info'].get('longitude'),
        #     'entries' : []
        # }

        # payload = {
        #     'powerstation_id' : self.system_id,
        #     'count' : 1,
        #     'date' : date_s
        # }
        # data = self.call("PowerStationMonitor/GetPowerStationPowerAndIncomeByDay", payload)
        # if len(data) == 0:
        #     logging.warning(date_s + " - Received bad data " + str(data))
        #     return result

        # eday_kwh = data[0]['p']

        # payload = {
        #     'id' : self.system_id,
        #     'date' : date_s
        # }
        # data = self.call("PowerStationMonitor/GetPowerStationPacByDayForApp", payload)
        # if 'pacs' not in data:
        #     logging.warning(date_s + " - Received bad data " + str(data))
        #     return result

        # minutes = 0
        # eday_from_power = 0
        # for sample in data['pacs']:
        #     parsed_date = datetime.strptime(sample['date'], "%m/%d/%Y %H:%M:%S")
        #     next_minutes = parsed_date.hour * 60 + parsed_date.minute
        #     sample['minutes'] = next_minutes - minutes
        #     minutes = next_minutes
        #     eday_from_power += sample['pac'] * sample['minutes']
        # factor = eday_kwh / eday_from_power if eday_from_power > 0 else 1

        # eday_kwh = 0
        # for sample in data['pacs']:
        #     date += timedelta(minutes=sample['minutes'])
        #     pgrid_w = sample['pac']
        #     increase = pgrid_w * sample['minutes'] * factor
        #     if increase > 0:
        #         eday_kwh += increase
        #         result['entries'].append({
        #             'dt' : date,
        #             'pgrid_w': pgrid_w,
        #             'eday_kwh': round(eday_kwh, 3)
        #         })

        # return result


    def call(self, url : str, payload : str, max_tries : int=10):
        for i in range(1, 4):
            try:
                headers = { 
                    'User-Agent': 'PVMaster/2.0.4 (iPhone; iOS 11.4.1; Scale/2.00)', 
                    'Token': self.token,
                    }

                r = requests.post(self.base_url + url, headers=headers, data=payload, timeout=10)
                r.raise_for_status()
                data = r.json()
                logging.debug(data)

                if data['msg'] == 'success' and data['data'] is not None:
                    return data['data']
                else:
                    loginPayload = { 'account': self.account, 'pwd': self.password }
                    r = requests.post(self.global_url + 'v1/Common/CrossLogin', headers=headers, data=loginPayload, timeout=10)
                    r.raise_for_status()
                    data = r.json()
                    self.base_url = data['api']
                    self.token = json.dumps(data['data'])
            except requests.exceptions.RequestException as exp:
                logging.warning(exp)
            time.sleep(i ** 3)
        else:
            logging.error("Failed to call GoodWe API")

        return {}

    def parseValue(self, value, unit):
        try:
            return float(value.rstrip(unit))
        except ValueError as exp:
            logging.warning(exp)
            return 0
    
    def are_batteries_full(self, fullstate : float=100.0):
        """ boolean result for if the batteries are full. you can set your given 'full' percentage in float if you want to lower this a little
        are_batteries_full(fullstate=90.0): returns bool
        """
        if self.get_battery_soc() > fullstate:
            return True
        return False


    def get_battery_soc(self):
        """ returns the single value state of charge for the batteries in the plant 
        returns : float
        """
        if not self.data:
            self.getCurrentReadings(True)
        return float(self.data['soc']['power'])

    def _get_batteries_soc(self):
        """ returns a list of the state of charge for the batteries
        returns: list[float,]
        """
        if not self.data:
            self.getCurrentReadings(True)
        return [ float(inverter['invert_full']['soc']) for inverter in self.data['inverter'] ]
    
    def get_batteries_soc(self):
        if not self.data:
            self.getCurrentReadings(True)
        return self._get_batteries_soc()

    def _get_station_location(self):
        retval = [{
            'latitude' : info['data']['latitude'],
            'longitude' : info['data']['longitude'],
        } for info in self.data['info'] ]
        return retval
    
    def get_station_location(self):
        return self._get_station_location()

    def getPVFlow(self):
        raise NotImplementedError("SingleInverter has this, multi does not")

    def getVoltage(self):
        if not self.data:
            self.getCurrentReadings(True)
        return [ float(inverter['invert_full']['vac1']) for inverter in gw.data['inverter']]

    def getLoadFlow(self):
        raise NotImplementedError("multi-unit load watts isn't implemented yet")

    def getDataPvoutput(self):
        """ updates and returns the data necessary for a one-shot pvoutput upload 
            'd' : testdate.strftime("%Y%m%d"),
            't' : testtime.strftime("%H:%M"),
            'v2' : 500, # power generation
            'v4' : 450, 
            'v5' : 23.5, # temperature
            'v6' : 234.0, # voltage
        """
        if not self.data:
            self.getCurrentReadings()
        #"time": "10/04/2019 14:37:29"
        timestamp = datetime.strptime(self.data['info']['time'], '%m/%d/%Y %H:%M:%S')
        data = {}
        data['d'] = timestamp.strftime("%Y%m%d") # date
        data['t'] = timestamp.strftime("%H:%M") # time
        data['v2'] = self.getPVFlow() # PV Generation
        data['v4'] = self.getLoadFlow() # power consumption
        #data['v5'] = 23.5 # temperature
        data['v6'] = self.getVoltage() # voltage
        return data

class MovingAverage:

    def __init__(self, n):
        self.n = round(n) if n > 0 else 1
        self.denominator = self.n * (self.n + 1) / 2
        self.queue = []

    def add(self, x):

        if len(self.queue) == 0:
            self.queue = [x] * self.n
            self.total = sum(self.queue)
            self.numerator = x * self.denominator

        self.numerator += self.n * x - self.total

        self.total += x - self.queue[0]

        self.queue.append(x)
        self.queue = self.queue[-self.n:]

        return self.numerator / self.denominator
        
class SingleInverter(API):
    def __init__(self, system_id : str, account : str, password : str, skipload : bool=False):
        # instantiate the base class
        super().__init__(system_id, account, password, skipload)
        
    def loaddata(self, filename):
        self._loaddata(filename)
        if len(self.data['inverter']):
            self.data['inverter'] = self.data['inverter'][0]

    def getCurrentReadings(self, raw=True):
        """ grabs the data and makes sure self.data only has a single inverter """
        
        # update the data
        self._getCurrentReadings(raw)
        # reduce self.data['inverter'] to a single dict from a list
        if len(self.data['inverter']):
            self.data['inverter'] = self.data['inverter'][0]


        
        #if self.data[]
        
    def get_station_location(self):
        if not self.data:
            self.getCurrentReadings(True)
        return { 
            'latitude' : self.data['info']['latitude'],
            'longitude' : self.data['info']['longitude']
        }

    def getPVFlow(self):
        """ returns the current flow amount of the PV panels """
        if not self.data:
            self.getCurrentReadings(True)
        if self.data['powerflow']['pv'].endswith('(W)'):
            pvflow = self.data['powerflow']['pv'][:-3]
        else:
            pvflow = self.data['powerflow']['pv']
        return float(pvflow)
    
    def getVoltage(self):
        """ gets the current line voltage """
        if not self.data:
            self.getCurrentReadings(True)
        return float(self.data['inverter']['invert_full']['vac1'])

    def getLoadFlow(self):
        if not self.data:
            self.getCurrentReadings(True)
        if self.data['powerflow']['bettery'].endswith('(W)'):
            loadflow = float(self.data['powerflow']['load'][:-3])
        else:
            loadflow = float(self.data['powerflow']['load'])
        # I'd love to see the *house* generate power
        if self.data['powerflow']['loadStatus'] == -1:
            loadflow_direction = "Using"
        else:
            raise ValueError("Your 'load' is generating power.")
        self.loadflow = loadflow
        self.loadflow_direction = loadflow_direction
        return loadflow