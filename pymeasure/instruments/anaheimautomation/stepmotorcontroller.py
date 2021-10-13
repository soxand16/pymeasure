#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2021 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import asyncio
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import truncated_range, strict_discrete_set


class MotorController(Instrument):
    """Driver to interface with Anaheim Automation stepper motor controllers. This driver has been tested with the DPY50601 and DPE25601 motor controllers. 
    """

    basespeed = Instrument.control(
        "VB", "B%i", 
        """Integer property that represents the motor controller's starting/homing speed. This property can be set.""",
        validator=truncated_range,
        values=[1, 5000],
    )
    
    maxspeed = Instrument.control(
        "VM", "M%i", 
        """Integer property that represents the motor controller's maximum (running) speed. This property can be set.""",
        validator=truncated_range,
        values=[1, 50000],
    )

    direction = Instrument.control(
        "V+", "%s",
        """A string property that represents the direction in which the stepper motor will rotate upon subsequent step commands. This property can be set. 'CW' corresponds to clockwise rotation and 'CCW' corresponds to counter-clockwise rotation.""",
        map_values=True, 
        validator=strict_discrete_set,
        values={"CW" : "+", "CCW" : "-"},
        get_process=lambda d: "+" if d == 1.0 else "-",
    )    

    steps = Instrument.control(
        "VN", "N%i",
        """An integer property that represents the number of steps the motor controller will run upon the next 'G' (go) command that is sent to the controller. This property can be set.""",
        validator=truncated_range,
        values=[0, 8388607]
    )

    position = Instrument.control(
       "VZ", "Z%i",
       """An integer property that represents the step position reference as seen by the motor controller. This property can be set.""",
       validator=truncated_range,
       values=[-8388607, 8388607]
    ) 

    error_reg = Instrument.measurement(
        "!",
        "Reads the current value of the error codes register."
    )

    def __init__(self, adapter, idn, write_termination="\r", **kwargs):
        self.idn = idn
        self.write_termination = write_termination
        
        super().__init__(
            adapter,
            "Anaheim Automation Stepper Motor Controller",
            **kwargs
        )

    def stop(self):
        """Method that stops all motion on the motor controller."""
        self.write(".")

    def go(self):
        """Method that sends the G command to the controller to tell the controller to turn the 
           motor the number of steps previously set with the steps property."""

        self.write("G")

    def step(self, steps, direction):
        """Similar to the go() method, but also sets the number of steps and the direction in the same method.
        
        :param steps: Number of steps to clock
        :param direction: Value to set on the direction property before sending the go command to the controller.
        """
        self.steps = steps 
        self.direction = direction
        self.write("G")

    def slew(self, direction):
        """Sends the slew command to the motor controller. This tells the controller to clock the stepper motor until a stop command is sent or a limit switch is reached.
        
        :param direction: value to set on the direction property before sending the slew command to the controller.
        """
        self.direction = direction
        self.write("S") 

    def write(self, command):
        """Override the instrument base write method to add the motor controller's id to the command string.
        
        :param command: command string to be sent to the motor controller.
        """
        self.adapter.write("@{}".format(self.idn) + command + self.write_termination)

    def values(self, command, **kwargs):
        """ Override the instrument base values method to add the motor controller's id to the command string.
        
        :param command: command string to be sent to the motor controller.
        """
        return self.adapter.values("@{}".format(self.idn) + command + self.write_termination, **kwargs)
        
    def ask(self, command):
            """ Override the instrument base ask method to add the motor controller's id to the command string.
            
            :param command: command string to be sent to the instrument
            """
            return self.adapter.ask("@{}".format(self.idn) + command + self.write_termination)
    
