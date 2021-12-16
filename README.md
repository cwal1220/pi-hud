# pi-hud
HUD(Head-Up Display) for Raspberry Pi4

# Supported feature
1. Speed
2. RPM
3. Engine Load
4. Engine Coolant
5. DPF(Diesel Particulate Filter) Distance
6. DPF(Diesel Particulate Filter) Temperature

## Install
  ```
  cd ~
  git clone https://github.com/cwal1220/pi-hud
  sudo apt-get install python3-pyqt5
  ```


## Connect Bluetooth
  ```
  pi@raspberrypi:~ $ bluetoothctl
  Agent registered
  [bluetooth]# power on
  Changing power on succeeded
  [bluetooth]# pairable on
  Changing pairable on succeeded
  [bluetooth]# agent on
  Agent is already registered
  [bluetooth]# default-agent
  Default agent request successful
  [bluetooth]# scan on
  ```


## Testing
  ```
  Hyundai Accent(Solaris) 2014 1.6 CRDI 
  ```
