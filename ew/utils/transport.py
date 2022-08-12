import asyncio

from . import core as ewutils
from .district import EwDistrict
from .frontend import EwResponseContainer
from ..backend.transport import EwTransportBase
from ..static import cfg as ewcfg
from ..static import poi as poi_static

"""
	Database Object for public transportation vehicles, such as ferries or subway trains
"""


class EwTransport(EwTransportBase):
    """ Makes the object move across the world map. Called once at client startup for every object """

    async def move_loop(self):
        response = ""
        poi_data = poi_static.id_to_poi.get(self.poi)
        last_messages = []
        # Loop till bot stops
        while not ewutils.TERMINATE:

            # Grab EwTransportLine object for current line
            transport_line = poi_static.id_to_transport_line.get(self.current_line)
            client = ewutils.get_client()
            resp_cont = EwResponseContainer(client=client, id_server=self.id_server)

            if not transport_line:
                return

            # If the train is at its last stop, switch to the opposite direction
            if self.current_stop == transport_line.last_stop:
                # wait for other train to clear the line
                if self.transport_type == ewcfg.transport_type_subway:
                    # find the other train
                    twin_poi = self.poi
                    if self.poi[-1] == '1':
                        twin_poi = twin_poi[:-1] + '2'
                    else:
                        twin_poi = twin_poi[:-1] + '1'
                    twin_train = EwTransport(id_server=self.id_server, poi=twin_poi)

                    delay_track = 0
                    # check every second
                    while (twin_train.current_line == transport_line.next_line):
                        twin_train = EwTransport(id_server=self.id_server, poi=twin_poi)
                        if twin_train.current_stop == poi_static.id_to_transport_line[twin_train.current_line].last_stop:
                            break
                        delay_track += 1
                        await asyncio.sleep(1)
                    if delay_track != 0 and ewutils.DEBUG:
                        ewutils.logMsg(self.poi + " waited " + str(delay_track) + " seconds for " + twin_poi)

                self.current_line = transport_line.next_line
                self.persist()
            # If the train is mid-route
            else:
                schedule = transport_line.schedule[self.current_stop]
                # Wait for scheduled time
                await asyncio.sleep(schedule[0])
                # Delete last arrival message
                for message in last_messages:
                    try:
                        await message.delete()
                        pass
                    except Exception as e:
                        ewutils.logMsg("Failed to delete message while moving transport {}: {}".format(transport_line.str_name, e))
                # Switch to the next stop
                self.current_stop = schedule[1]
                self.persist()

                # Grab EwPoi of station
                stop_data = poi_static.id_to_poi.get(self.current_stop)

                # announce new stop inside the transport
                response = "We have reached {}.".format(stop_data.str_name)

                # Initialize next_line in this scope
                next_line = transport_line

                # Allow for some stops to be blocked
                if stop_data.is_transport_stop:
                    response += " You may exit now."

                # If it's at the end, announce new route
                if stop_data.id_poi == transport_line.last_stop:
                    next_line = poi_static.id_to_transport_line[transport_line.next_line]
                    response += " This {} will proceed on {}.".format(self.transport_type, next_line.str_name.replace("The", "the"))
                else:
                    # Otherwise announce next stop, if usable
                    next_stop = poi_static.id_to_poi.get(transport_line.schedule.get(stop_data.id_poi)[1])
                    if next_stop.is_transport_stop:
                        response += " The next stop is {}.".format(next_stop.str_name)
                resp_cont.add_channel_response(poi_data.channel, response)


                # announce transport has arrived at the stop
                if stop_data.is_transport_stop:
                    response = "{} has arrived. You may board now.".format(next_line.str_name)
                    resp_cont.add_channel_response(stop_data.channel, response)
                elif self.transport_type == ewcfg.transport_type_ferry:
                    response = "{} sails by.".format(next_line.str_name)
                    resp_cont.add_channel_response(stop_data.channel, response)
                elif self.transport_type == ewcfg.transport_type_blimp:
                    response = "{} flies overhead.".format(next_line.str_name)
                    resp_cont.add_channel_response(stop_data.channel, response)

                last_messages = await resp_cont.post()


""" Starts movement of all transports. Called once at client startup """


async def init_transports(id_server = None):
    if id_server is not None:
        for poi in poi_static.transports:
            transport_data = EwTransport(id_server=id_server, poi=poi)
            asyncio.ensure_future(transport_data.move_loop())
