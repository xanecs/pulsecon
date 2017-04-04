from pulsectl import Pulse, PulseLoopStop
import redis
import toml
import json

class Pulsecon(object):
    def update_list(self):
        inputs = self.pulse.sink_input_list()
        newstate = {}
        for input in inputs:
            newstate[input.proplist['application.name']] = input.__dict__['buffer_usec'] > 0
        if newstate != self.playstate:
            self.r.publish(self.redis_channel + ':playing', json.dumps(newstate))
            for k in newstate:
                self.r.set(self.redis_channel + ':' + k, 'true' if newstate[k] else 'false')
            for k in self.playstate:
                if not (k in newstate):
                    self.r.set(self.redis_channel + ':playing:' + k, 'false')
            self.playstate = newstate

    def update_volume(self):
        sinks = self.pulse.sink_list()
        volume = self.pulse.volume_get_all_chans(sinks[0])
        if self.volume != volume:
            self.r.publish(self.redis_channel + ':volume', json.dumps({'volume': volume}))
            self.r.set(self.redis_channel + ':volume', str(volume))
            self.volume = volume

    def set_volume(self, volume):
        sinks = self.pulse.sink_list()
        self.pulse.volume_set_all_chans(sinks[0], volume)

    def handle_command(self, message):
        data = json.loads(message['data'].decode('utf-8'))
        if 'action' in data and data['action'] == 'volume':
            self.set_volume(data['params']['volume'])

    def __init__(self):
        self.playstate = {}
        self.volume = None

        with open('config.toml') as conffile:
            config = toml.loads(conffile.read())

        redis_host = config['redis']['host']
        redis_port = config['redis']['port']
        self.redis_channel = config['redis']['channel']

        self.r = redis.StrictRedis(host=redis_host, port=redis_port, db=0)
        self.p = self.r.pubsub()
        self.p.subscribe(**{self.redis_channel + ':command': self.handle_command}, ignore_subscribe_messages=True)

        with Pulse('pulsecon') as pulse:
            self.pulse = pulse
            def callback(ev):
                raise PulseLoopStop

            pulse.event_mask_set('all')
            pulse.event_callback_set(callback)
            while(True):
                try:
                    pulse.event_listen(timeout=0.2)
                    self.update_list()
                    self.update_volume()
                    self.p.get_message()

                except KeyboardInterrupt:
                    break

        vol = float(self.r.get(self.redis_channel + ':volume'))
        self.set_volume(vol)

def init():
    Pulsecon()

if __name__ == '__main__':
    init()
