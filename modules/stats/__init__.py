from modules import cbpi


def getserial():
  cpuserial = "0000000000000000"
  try:
    f = open('/proc/cpuinfo','r')
    for line in f:
      if line[0:6]=='Serial':
        cpuserial = line[10:26]
    f.close()
  except:
    cpuserial = "0000000000000000"
  return cpuserial


@cbpi.initalizer(order=9999)
def sendStats(cbpi):

    try:
        serial = getserial()

        info = {
        "id": serial,
        "version": "3.0",
        "kettle": len(cbpi.cache.get("kettle")),
        "hardware": len(cbpi.cache.get("actors")),
        "thermometer": "CBP3.0",
        "hardware_control": "CBP3.0"
        }

        import requests
        r = requests.post('http://statistics.craftbeerpi.com', json=info)

    except Exception as e:
        pass