## Nerve savers:

Datasheed: ADC2 pins are NOT usable when Wifi is enabled

My Experience: ADC1 pins are also not stable for data when Wifi is enabled. 
Workaround: write Wifi code in a separate function with turn Wifi off at the end and only run the function when no data is transmiited.
<br>
Wake up pins must be RTC pins