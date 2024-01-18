import asyncio

""" Bleak Pyhton library """
from bleak import BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic

""" MAC Address Sensirion SCD41 Gadget Sensor """
mac_sensor_three = "F1:05:96:09:C9:5C"

""" Service Characteristics UUID """
# Data Transfer UUID notification
#Contains two frames: 1) The header  2)Sampling data
service_uuid_data_transfer = "00008004-B38D-4985-720E-0F993A68EE41"

""" Global variable to store the raw data frame from the sensor  """
raw_sensor_frame = [] 
        

async def get_co2():
    co2_msb = raw_sensor_frame[0][7]
    co2_lsb = raw_sensor_frame[0][6]
    #print(raw_sensor_frame)
    #print(co2_msb, co2_lsb)
    co2_hex = f"{co2_msb:02x}{co2_lsb:02x}"
    co2_dec = int(co2_hex, 16)
    return co2_dec
    

async def get_temperature():
    temperature_msb = raw_sensor_frame[0][3]
    temperature_lsb = raw_sensor_frame[0][2]
    """ print(raw_sensor_frame)
    print(temperature_msb, temperature_lsb) """
    temperature_hex = f"{temperature_msb:02x}{temperature_lsb:02x}"
    temperature_dec_ticks = int(temperature_hex, 16)
    temperature = -45 + ((175.0 * temperature_dec_ticks ) / ((2 **16) - 1))
    return temperature
    
    
async def get_humidity():
    humidity_msb = raw_sensor_frame[0][5]
    humidity_lsb = raw_sensor_frame[0][4]
    """ print(raw_sensor_frame)
    print(humidity_msb, humidity_lsb) """
    humidity_hex = f"{humidity_msb:02x}{humidity_lsb:02x}"
    humidity_dec_ticks = int(humidity_hex, 16)
    humidity = ((100.0 * humidity_dec_ticks) / ((2 **16) - 1))
    return humidity
   

#Contains two frames: 1) The header  2)Sampling data
# keep only the sampling data in the variable
async def notification_handler(characteristic: BleakGATTCharacteristic, data: bytearray):
    global raw_sensor_frame
    raw_sensor_frame = []
    raw_sensor_frame.append(list(data))
    await asyncio.sleep(20)

""" Connecting to the Sensor """
async def interface_sensor():
    async with BleakClient(mac_sensor_three) as scd41_three:
        print('\nEstablishing connection')
        print("Sensor connected!\n")
        """ Sensor Notification contaning the data frame """
        for rep in range(40):
            await scd41_three.start_notify(service_uuid_data_transfer, notification_handler)
            await asyncio.sleep(3.0)
            print("******DATA INTAKING SENSIRION SCD41 CO₂ Sensor Demonstrator******\n", "------Notification ",rep,"-------", "\n" )
            co2_concentration= await get_co2()
            print(f"- Co2 concentration: {co2_concentration} ppm\n")
            temperature = await get_temperature()
            print(f"- Temperature: {temperature} °C\n")
            humidity_percentage = await get_humidity()
            print(f"- Humidity: {humidity_percentage} %\n")
    print(raw_sensor_frame)       



"Main Co-routine"
async def main():
    print("\nStarting Data Collection\n")
    interface_task = asyncio.create_task(interface_sensor())
    await interface_task
    



# Using asyncio.run() is important to ensure that the device disconnects on
# KeyboardInterrupt or other unhandled exception.
asyncio.run(main())   