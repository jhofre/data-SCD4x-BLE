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
        

#Contains two frames: 1) The header  2)Sampling data
# keep only the sampling data in the variable
def notification_handler(characteristic: BleakGATTCharacteristic, data: bytearray):
    global raw_sensor_frame
    raw_sensor_frame = []
    raw_sensor_frame.append(list(data))

def get_co2():
    print("CO2 List:", raw_sensor_frame)
    co2_msb = raw_sensor_frame[0][7]
    co2_lsb = raw_sensor_frame[0][6]
    co2_hex = f"{co2_msb:02x}{co2_lsb:02x}"
    co2_dec = int(co2_hex, 16)
    print(f"- Co2 concentration: {co2_dec} ppm\n")

def get_temperature():
    co2_msb = raw_sensor_frame[0][3]
    co2_lsb = raw_sensor_frame[0][2]
    #print(co2_msb, co2_lsb)
    co2_hex = f"{co2_msb:02x}{co2_lsb:02x}"
    co2_dec_ticks = int(co2_hex, 16)
    temperature = -45 + ((175.0 * co2_dec_ticks ) / ((2 **16) - 1))
    print(f"- Temperature: {temperature} °C\n")
    
def get_humidity():
    co2_msb = raw_sensor_frame[0][5]
    co2_lsb = raw_sensor_frame[0][4]
    #print(co2_msb, co2_lsb)
    co2_hex = f"{co2_msb:02x}{co2_lsb:02x}"
    humidity_dec_ticks = int(co2_hex, 16)
    humidity = ((100.0 * humidity_dec_ticks) / ((2 **16) - 1))
    print(f"- Humidity: {humidity} %\n")

""" Connecting to the Sensor """
async def interface_sensor():
    async with BleakClient(mac_sensor_three) as scd41_three:
        print('\nEstablishing connection')
        print("Sensor connected!\n")
        """ Sensor Notification contaning the data frame """
        for rep in range(5):
            await scd41_three.start_notify(service_uuid_data_transfer, notification_handler)
            await asyncio.sleep(3.0)
            print("******DATA INTAKING SENSIRION SCD41 CO₂ Sensor Demonstrator******\n", "------Notification ",rep,"-------", "\n" )
            get_co2()
            get_temperature()
            get_humidity()



        


"Main Co-routine"
async def main():
    print("\nStarting Data Collection\n")
    interface_task = asyncio.create_task(interface_sensor())
    await interface_task
    



# Using asyncio.run() is important to ensure that the device disconnects on
# KeyboardInterrupt or other unhandled exception.
asyncio.run(main())   