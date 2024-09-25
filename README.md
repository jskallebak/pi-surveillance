# Instuktioner til lukas

Prøv med gpiod

Først.  
sudo apt-get install libgpiod-dev  
pip3 install gpiod

lav en fil kaldt test.py og copy-paste min test.py

chip = gpiod.Chip('gpiochip0') <--- hvis dette ikke er den rigtige chip på dit board

prøv   
ls /dev/gpiochip*

og skriv hvad du får  
chip = gpiod.Chip('skriv her')


inPin1 = chip.get_line(21) <----- Skriv de porte du bruger  
inPin2 = chip.get_line(20)  
inPin3 = chip.get_line(16)  
inPin4 = chip.get_line(12)  

kør scriptet ved komandoen:  
python3 test.py

Hvis den printer  
0 = ikke noget strøm  
1 = der er strøm  