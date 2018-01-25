from modules import ActorBase, cbpi
from modules.core.props import Property, StepProperty
from modules.core.step import StepBase
import time
try:
    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)
except Exception as e:
    print e
    pass


@cbpi.step
class BoilStepWithHopDropper(StepBase):
    '''
    Just put the decorator @cbpi.step on top of a method
    '''
    # Properties
    temp = Property.Number("Temperature", configurable=True, default_value=100, description="Target temperature for boiling")
    kettle = StepProperty.Kettle("Kettle", description="Kettle in which the boiling step takes place")
    timer = Property.Number("Timer in Minutes", configurable=True, default_value=90, description="Timer is started when target temperature is reached")
    hop_dropper = StepProperty.Actor("Hop Dropper", description="Please select the hop dropper actor")
    hop_1 = Property.Number("Hop 1 Addition", configurable=True, description="First Hop alert")
    hop_1_added = Property.Number("", default_value=None)
    hop_2 = Property.Number("Hop 2 Addition", configurable=True, description="Second Hop alert")
    hop_2_added = Property.Number("", default_value=None)
    hop_3 = Property.Number("Hop 3 Addition", configurable=True)
    hop_3_added = Property.Number("", default_value=None, description="Third Hop alert")
    hop_4 = Property.Number("Hop 4 Addition", configurable=True)
    hop_4_added = Property.Number("", default_value=None, description="Fourth Hop alert")
    hop_5 = Property.Number("Hop 5 Addition", configurable=True)
    hop_5_added = Property.Number("", default_value=None, description="Fives Hop alert")

    def init(self):
        '''
        Initialize Step. This method is called once at the beginning of the step
        :return:
        '''
        # set target tep
        self.set_target_temp(self.temp, self.kettle)

    @cbpi.action("Start Timer Now")
    def start(self):
        '''
        Custom Action which can be execute form the brewing dashboard.
        All method with decorator @cbpi.action("YOUR CUSTOM NAME") will be available in the user interface
        :return:
        '''
        if self.is_timer_finished() is None:
            self.start_timer(int(self.timer) * 60)

    def reset(self):
        self.stop_timer()
        self.set_target_temp(self.temp, self.kettle)

    def finish(self):
        self.set_target_temp(0, self.kettle)

    def check_hop_timer(self, number, value):

        if self.__getattribute__("hop_%s_added" % number) is not True and time.time() > (
                    self.timer_end - (int(self.timer) * 60 - int(value) * 60)):
            self.__setattr__("hop_%s_added" % number, True)
            if self.hop_dropper is not None:
                self.actor_on(int(self.hop_dropper))
            self.notify("Hop Alert", "Please add Hop %s" % number, timeout=None)

    def execute(self):
        '''
        This method is execute in an interval
        :return:
        '''
        # Check if Target Temp is reached
        if self.get_kettle_temp(self.kettle) >= float(self.temp):
            # Check if Timer is Running
            if self.is_timer_finished() is None:
                self.start_timer(int(self.timer) * 60)
            else:
                self.check_hop_timer(1, self.hop_1)
                self.check_hop_timer(2, self.hop_2)
                self.check_hop_timer(3, self.hop_3)
                self.check_hop_timer(4, self.hop_4)
                self.check_hop_timer(5, self.hop_5)
        # Check if timer finished and go to next step
        if self.is_timer_finished() == True:
            self.notify("Boil Step Completed!", "Starting the next step", timeout=None)
            self.next()


@cbpi.actor
class HopDropperActor(ActorBase):
    gpio = Property.Select("GPIO", options=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27], description="GPIO to which the actor is connected")
    timeout = Property.Number("Timeout", configurable=True,default_value=2, description="After how many seconds the actor should switch off again")

    def init(self):
        GPIO.setup(int(self.gpio), GPIO.OUT)
        GPIO.output(int(self.gpio), 1)


    def on(self, power=0):
        def toggleTimeJob(id, t):
            self.api.socketio.sleep(t)
            self.api.switch_actor_off(int(id))
        
        t = self.api.socketio.start_background_task(target=toggleTimeJob, id=self.id, t=self.timeout)
        GPIO.output(int(self.gpio), 1)

    def off(self):

        GPIO.output(int(self.gpio), 0)
