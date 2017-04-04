from pulsectl import Pulse, PulseLoopStop
import redis
import toml
import json

def update_list(pulse):
    inputs = pulse.sink_input_list()
    dict = {}
    for input in inputs:
        dict[input.proplist['application.name']] = input.__dict__['buffer_usec'] > 0
    return dict

def init():
    playstate = None
    with open('config.toml') as conffile:
        config = toml.loads(conffile.read())

    redis_host = config['redis']['host']
    redis_port = config['redis']['port']
    redis_channel = config['redis']['channel']

    r = redis.StrictRedis(host=redis_host, port=redis_port, db=0)

    with Pulse('pulsecon') as pulse:
        def callback(ev):
            print(ev)
            print('---')
            print(ev.__dict__)
            raise PulseLoopStop

        pulse.event_mask_set('all')
        pulse.event_callback_set(callback)
        while(True):
            try:
                pulse.event_listen(timeout=1)
                newstate = update_list(pulse)
                if newstate != playstate:
                    playstate = newstate
                    r.publish(redis_channel, json.dumps(playstate))
                    for k in playstate:
                        r.set(redis_channel + ':' + k, 'true' if playstate[k] else 'false')
            except KeyboardInterrupt:
                break

if __name__ == '__main__':
    init()
