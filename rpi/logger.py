import json


class Logger(object):
    log_buffer = []

    def info(self, origin, msg):
        self.log_buffer.append([0, origin, self.to_string(msg)])

    def warning(self, origin, msg):
        self.log_buffer.append([1, origin, self.to_string(msg)])

    def error(self, origin, msg):
        self.log_buffer.append([2, origin, self.to_string(msg)])

    def verbose(self, origin, msg):
        self.log_buffer.append([3, origin, self.to_string(msg)])

    def to_string(self, msg):
        try: s = str(msg)
        except:
            try: s = json.dumps(msg)
            except:
                try: s = repr(msg)
                except: s = ''
        return s

    def get_log(self):
        l = list(self.log_buffer)
        self.log_buffer = []
        return l