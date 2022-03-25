# Dieses Script überprüft welche Zelle die meiste Spannung besitzt und welche Spannung diese hat
# Danach wird der maximale Ladestrom des Victron Systems eingestellt.
# Dies hilft mit einer höhreren Strom zu laden und dann wenn der Akku nahezuvoll ist diesen zu verringern.
# Auch die Spannung wird herrabgesetzt.


import time
import paho.mqtt.client as mqtt
import logging
import json

cerboserial = "123456789"    # Ist auch gleich VRM Portal ID
broker_address = "192.168.1.xxx"

#  Einstellen der Limits (Über Maxvoltcell1 wird Stufe 2 eingesetzt, über 2 dann 3 usw.)

MaxAmpStufe1 = 400
MaxAmpStufe2 = 100
MaxAmpStufe3 = 20
MaxAmpStufe4 = 6
MaxAmpStufe5 = 0

VoltSpgvoll = 55
VoltSpgred = 54.4

MaxVoltCell1 = 3.40
MaxVoltCell2 = 3.42
MaxVoltCell3 = 3.45
MaxVoltCell4 = 3.5

# Pfade

MaxCellVoltagePath = "/battery/512/System/MaxCellVoltage"
MaxChargeCurrentPath = "/settings/0/Settings/SystemSetup/MaxChargeCurrent"
MaxChargeVoltagePath = "/settings/0/Settings/SystemSetup/MaxChargeVoltage"

# Variblen setzen
verbunden = 0
durchlauf = 0
maxcellvoltage = 3.0

logging.basicConfig(filename='Error.log', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %H:%M:%S')

def on_disconnect(client, userdata, rc):
    global verbunden
    print("Client Got Disconnected")
    if rc != 0:
        print('Unexpected MQTT disconnection. Will auto-reconnect')

    else:
        print('rc value:' + str(rc))

    try:
        print("Trying to Reconnect")
        client.connect(broker_address)
        verbunden = 1
    except Exception as e:
        logging.exception("Fehler beim reconnecten mit Broker")
        print("Error in Retrying to Connect with Broker")
        verbunden = 0
        print(e)

def on_connect(client, userdata, flags, rc):
        global verbunden
        if rc == 0:
            print("Connected to MQTT Broker!")
            verbunden = 1
            client.subscribe("N/" + cerboserial + MaxCellVoltagePath)
        else:
            print("Failed to connect, return code %d\n", rc)


def on_message(client, userdata, msg):
    try:

        global maxcellvoltage
        if msg.topic == "N/" + cerboserial + MaxCellVoltagePath:   # MaxCellVoltage auslesen
            if msg.payload != '{"value": null}' and msg.payload != b'{"value": null}':
                maxcellvoltage = json.loads(msg.payload)
                maxcellvoltage = round(float(maxcellvoltage['value']), 2)
            else:
                print("MaxCellVoltage war Null und wurde ignoriert")

    except Exception as e:
        logging.exception("Programm MAMC ist abgestürzt. (on message Funkion)")
        print(e)
        print("Im MAMC Programm ist etwas beim auslesen der Nachrichten schief gegangen")

# Konfiguration MQTT
client = mqtt.Client("MAMC")  # create new instance
client.on_disconnect = on_disconnect
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_address)  # connect to broker

logging.debug("Programm MAMC wurde gestartet")

client.loop_start()
time.sleep(5)
print(maxcellvoltage)
while(1):
    try:
        durchlauf = durchlauf + 1
        print(durchlauf)
        time.sleep(60)
        if maxcellvoltage <= MaxVoltCell1:
            print("Höchste Zelle(" + str(maxcellvoltage) + "V) liegt unter dem Wert vom Stufe 1 (" + str(MaxVoltCell1) + "V), ")
            print("daher wird maximaler Strom von " + str(MaxAmpStufe1) + "A eingestellt")
            print("Außerdem wird Ladespannung nicht reduziert und auf " + str(VoltSpgvoll) + "V eingestellt")
            client.publish("W/" + cerboserial + MaxChargeVoltagePath, '{"value": ' + str(VoltSpgvoll) + ' }')
            client.publish("W/" + cerboserial + MaxChargeCurrentPath, '{"value": ' + str(MaxAmpStufe1) + ' }')
            time.sleep(120)
        elif maxcellvoltage <= MaxVoltCell2:
            print("Höchste Zelle(" + str(maxcellvoltage) + "V)  liegt über dem Wert vom Stufe 1 (" +str(MaxVoltCell1) + "V), ")
            print("daher wird der Ladestrom von " + str(MaxAmpStufe2) + "A eingestellt")
            print("Außerdem wird Ladespannung reduziert und auf " + str(VoltSpgred) + "V eingestellt")
            client.publish("W/" + cerboserial + MaxChargeVoltagePath, '{"value": ' + str(VoltSpgred) + ' }')
            client.publish("W/" + cerboserial + MaxChargeCurrentPath, '{"value": ' + str(MaxAmpStufe2) + ' }')
        elif maxcellvoltage <= MaxVoltCell3:
            print("Höchste Zelle(" + str(maxcellvoltage) + "V)  liegt über dem Wert vom Stufe 2 (" +str(MaxVoltCell2) + "V), ")
            print("daher wird der Ladestrom von " + str(MaxAmpStufe3) + "A eingestellt")
            print("Außerdem wird Ladespannung reduziert und auf " + str(VoltSpgred) + "V eingestellt")
            client.publish("W/" + cerboserial + MaxChargeVoltagePath, '{"value": ' + str(VoltSpgred) + ' }')
            client.publish("W/" + cerboserial + MaxChargeCurrentPath, '{"value": ' + str(MaxAmpStufe3) + ' }')
        elif maxcellvoltage <= MaxVoltCell4:
            print("Höchste Zelle(" + str(maxcellvoltage) + "V)  liegt über dem Wert vom Stufe 3 (" +str(MaxVoltCell3) + "V), ")
            print("daher wird der Ladestrom von " + str(MaxAmpStufe4) + "A eingestellt")
            print("Außerdem wird Ladespannung reduziert und auf " + str(VoltSpgred) + "V eingestellt")
            client.publish("W/" + cerboserial + MaxChargeVoltagePath, '{"value": ' + str(VoltSpgred) + ' }')
            client.publish("W/" + cerboserial + MaxChargeCurrentPath, '{"value": ' + str(MaxAmpStufe4) + ' }')
        elif maxcellvoltage >= MaxVoltCell4:
            print("Höchste Zelle(" + str(maxcellvoltage) + "V)  liegt über dem Wert vom Stufe 4 (" +str(MaxVoltCell4) + "V), ")
            print("daher wird der Ladestrom von " + str(MaxAmpStufe5) + "A eingestellt")
            print("Außerdem wird Ladespannung reduziert und auf " + str(VoltSpgred) + "V eingestellt")
            client.publish("W/" + cerboserial + MaxChargeVoltagePath, '{"value": ' + str(VoltSpgred) + ' }')
            client.publish("W/" + cerboserial + MaxChargeCurrentPath, '{"value": ' + str(MaxAmpStufe5) + ' }')

    except Exception as e:
        logging.exception("Programm MAMC ist abgestürzt. (while Schleife)")
        print(e)
        print("Im MAMC Programm ist etwas beim auslesen der Nachrichten schief gegangen")