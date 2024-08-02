#include "mbed.h"

DigitalOut led(PA_4);
AnalogIn RV(A1); // Connect RV pin of the sensor to A1 of Nucleo board
AnalogIn TMP(A0); // Connect TMP pin of the sensor to A0 of Nucleo board

Serial pc(USBTX, USBRX, 115200); // tx, rx for serial communication
Serial device(D1, D0, 115200); 

const float ZeroWind_RV = 0.576801; // The RV reading at zero wind speed
const float WindGain = 0.1; // The gain of the sensor in mV per mph
const float TempGain = 0.476191 / 24; // The gain of the sensor in mV per degree Celsius

int main() {
    while(1) {
        float RV_Wind = RV.read(); // Read the value from the RV pin
        float TMP_Therm = TMP.read(); // Read the value from the TMP pin

        // Calculate wind speed and temperature
        float WindSpeed = (RV_Wind - ZeroWind_RV) / WindGain;
        float Temperature = TMP_Therm / TempGain;

        ((Stream&)pc).printf("W: %f \n", WindSpeed); // Print the wind speed
        ((Stream&)pc).printf("T: %f \n", Temperature); // Print the temperature
                
        led = !led; 
        wait(1); 
    }
}
