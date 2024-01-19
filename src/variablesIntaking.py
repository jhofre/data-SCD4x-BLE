import asyncio
from bleak import BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic

mac_address_third = "F1:05:96:09:C9:5C"
co2_list = []

service_uuid_loggin_interval = "00008001-B38D-4985-720E-0F993A68EE41"
service_uuid_available_samples = "00008002-B38D-4985-720E-0F993A68EE41"
service_uuid_requested_samples = "00008003-B38D-4985-720E-0F993A68EE41"
service_uuid_data_transfer = "00008004-B38D-4985-720E-0F993A68EE41"


def notification_handler(characteristic: BleakGATTCharacteristic, data: bytearray):
    global co2_list
    co2_list = []
    co2_list.append(list(data))


def printCO2():
    print("CO2 List:", co2_list)
    co2_msb = co2_list[0][7]
    co2_lsb = co2_list[0][6]
    co2_hex = f"{co2_msb:02x}{co2_lsb:02x}"
    co2_dec = int(co2_hex, 16)
    print(f"- Co2 concentration: {co2_dec} ppm\n")
    

def printTemperature():
    co2_msb = co2_list[0][3]
    co2_lsb = co2_list[0][2]
    #print(co2_msb, co2_lsb)
    co2_hex = f"{co2_msb:02x}{co2_lsb:02x}"
    co2_dec_ticks = int(co2_hex, 16)
    temperature = -45 + ((175.0 * co2_dec_ticks ) / ((2 **16) - 1))
    print(f"- Temperature: {temperature} °C\n")
    
def printHumidity():
    co2_msb = co2_list[0][5]
    co2_lsb = co2_list[0][4]
    #print(co2_msb, co2_lsb)
    co2_hex = f"{co2_msb:02x}{co2_lsb:02x}"
    humidity_dec_ticks = int(co2_hex, 16)
    humidity = ((100.0 * humidity_dec_ticks) / ((2 **16) - 1))
    print(f"- Humidity: {humidity} %\n")

async def main():
    async with BleakClient(mac_address_third) as client:
        print("Connecting...")
        print("Gadget connected!")
        print(" ")

        # Read characteristics, etc.
        logging_interval = await client.read_gatt_char(service_uuid_loggin_interval)
        print("Logging Interval:", logging_interval)
        print("")
        available_samples = await client.read_gatt_char(service_uuid_available_samples)
        print("Available samples:", available_samples)
        print("")
        requested_samples = await client.read_gatt_char(service_uuid_requested_samples)
        print("Requested samples:", requested_samples)
        print("")

        # Request to omit the oldest samples of the sensor
        await client.write_gatt_char("00008003-B38D-4985-720E-0F993A68EE41", b'\x01\x00', response=False)

        # Check the requested samples.
        logging_interval = await client.read_gatt_char("00008003-B38D-4985-720E-0F993A68EE41")
        print("Checking requested samples:", logging_interval)
        print("")

        # Periodically activate notifications and print CO2 data
        for rep in range(5):  # Change the range to control the number of times
            await client.start_notify(service_uuid_data_transfer, notification_handler)
            await asyncio.sleep(5.0)  # Wait for 10 seconds
            print("******DATA INTAKING SENSIRION SCD41 CO₂ Sensor Demonstrator******\n", "------Notification ",rep,"-------", "\n" )
            printCO2()
            printTemperature()
            printHumidity()
            

    # Device will disconnect when the block exits.


# Using asyncio.run() is important to ensure that the device disconnects on
# KeyboardInterrupt or other unhandled exception.
asyncio.run(main())


