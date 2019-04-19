class InterfaceStats(object):
  """
  Used to save Interface statistics
  """

  def __init__(self, interface, snmp_if_index, timestamp, input_bytes, input_packets,
               output_bytes, output_packets, input_drops, input_errors, output_drops,
               output_errors, input_bps, output_bps):
    self._interface = interface
    self._snmp_if_index = snmp_if_index
    self._timestamp = timestamp
    self._input_bytes = input_bytes
    self._input_packets = input_packets
    self._output_bytes = output_bytes
    self._output_packets = output_packets
    self._input_drops = input_drops
    self._input_errors = input_errors
    self._output_drops = output_drops
    self._output_errors = output_errors
    self._input_bps = input_bps
    self._output_bps = output_bps

  @property
  def interface(self):
    return self._interface

  @interface.setter
  def interface(self, interface):
    self._interface = interface

  @property
  def snmp_if_index(self):
    return self._snmp_if_index

  @snmp_if_index.setter
  def snmp_if_index(self, snmp_if_index):
    self._snmp_if_index = snmp_if_index

  @property
  def timestamp(self):
    return self._timestamp

  @timestamp.setter
  def timestamp(self, timestamp):
    self._timestamp = timestamp

  @property
  def input_bytes(self):
    return self._input_bytes

  @input_bytes.setter
  def input_bytes(self, input_bytes):
    self._input_bytes = input_bytes

  @property
  def input_packets(self):
    return self._input_packets

  @input_packets.setter
  def input_packets(self, input_packets):
    self._input_packets = input_packets

  @property
  def output_bytes(self):
    return self._output_bytes

  @output_bytes.setter
  def output_bytes(self, output_bytes):
    self._output_bytes = output_bytes

  @property
  def output_packets(self):
    return self._output_packets

  @output_packets.setter
  def output_packets(self, output_packets):
    self._output_packets = output_packets

  @property
  def input_drops(self):
    return self._input_drops

  @input_drops.setter
  def input_drops(self, input_drops):
    self._input_drops = input_drops

  @property
  def input_errors(self):
    return self._input_errors

  @input_errors.setter
  def input_errors(self, input_errors):
    self._input_errors = input_errors

  @property
  def output_drops(self):
    return self._output_drops

  @output_drops.setter
  def output_drops(self, output_drops):
    self._output_drops = output_drops

  @property
  def output_errors(self):
    return self._output_errors

  @output_errors.setter
  def output_errors(self, output_errors):
    self._output_errors = output_errors

  @property
  def input_bps(self):
    return self._input_bps

  @input_bps.setter
  def input_bps(self, input_bps):
    self._input_bps = input_bps

  @property
  def output_bps(self):
    return self._output_bps

  @output_bps.setter
  def output_bps(self, output_bps):
    self._output_bps = output_bps
