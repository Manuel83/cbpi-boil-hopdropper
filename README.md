# CraftBeerPi Boil Step with Hop Dropper Actor


## Setup Hop Dropper Actor
First you need to setup a hop dropper actor. Select a GPIO and set a time out. 
If you switch the actor on it will be switched of after the timeout.
Future improvement would be to control a servo motor 

![alt text](https://github.com/Manuel83/cbpi-boil-hopdropper/raw/master/HopDropperActor.png)

## Setup Boil Step
Select the hop dropper actor for the boil step. For each hop alert the actor will be switched on and after the timeout (see actor config) switched off

![alt text](https://github.com/Manuel83/cbpi-boil-hopdropper/raw/master/BoilStepWithHopDropper-2.png)
